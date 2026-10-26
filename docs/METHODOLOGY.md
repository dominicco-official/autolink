# Methodology

## Data
The Fusion 360 Gallery Assembly dataset (j1.0.0) provides, for each *joint set*, two bodies and the designer's joint(s). Each body comes as a B-Rep **graph file** (one node per face, then one per edge, with surface type, area, centroid, normal / axis / radius, curve type, length, and face-edge adjacency) plus an OBJ mesh grouped by face. AutoLink reads the graph file; the mesh is used only for display and for the surface-distance check. The designer's joint and transform are used **only for evaluation**, never as input.

## Step 1: joint prediction (JoinABLe)
Upstream code is vendored unchanged at commit `5a3b9933`. `pipeline/joinable_predict_fast.py` loads one joint set from its JSON files (bypassing the 1.9 GB split cache by overriding `setup_cache`) and keeps JoinABLe's own `JointPredictionSet` post-processing, so predictions are identical to the upstream path (checked on `joint_set_04039`: all ten ranks and probabilities match). Output: top-K (face or edge, face or edge) pairs with probability and a derived joint axis. Edge picks are later promoted to the adjacent face with the same axis and radius.

Reproduction of the paper: `train.py --traintest test` with `last_run_0.ckpt` on the 1,926-pair test split, CPU, 379 s: top-1 0.7954 (paper 0.7953).

## Step 2: parametric reconstruction (LLM)
The graph file is rendered as a readable spec (`part_N_face_summary.txt`): every face with type and numbers, every edge with length / radius / centre, and which faces each edge borders. The prompt asks for a CadQuery module exposing `PARAMS` and `build(**params)` in the dataset's coordinate frame, deriving dependent sizes inside `build` (e.g. outer = bore + wall) so that later edits keep design intent. The reply is executed in isolation, built, and checked by step 3; on failure the verifier report (which dataset faces are unmatched, which faces the script produced, volume / bbox deltas) is appended and the model is asked again, up to three times. Every prompt, reply and report is saved under `recon/recon_<id>/attempts/`.

In the reported runs the model was Claude inside a chat session following the same procedure (`recon/ATTEMPTS.json`); the automated path (`pipeline/llm_reconstruct.py`) supports Anthropic, OpenAI and Bedrock through environment variables and was validated offline with a mock provider.

## Step 3: verification
Checks, in order: equal face count; every dataset face matched to one CadQuery face by type, radius (cylinders / spheres) and centroid within 0.1 % of the bounding-box diagonal; volume within 0.1 %; bounding box within 1e-4 cm; mean point-to-surface distance to the dataset mesh below max(0.01 cm, 0.5 % of the diagonal), the dataset meshes being coarse. The face matching doubles as the **side table** (dataset face id -> CadQuery face) used by all later steps. Verifier changes made during the project are listed in `pipeline_demo/EVALUATION.md`; they were tolerance and classification fixes (sphere / cone radii, zero-taper cones reported as cylinders by OCC, trimmed surfaces), not relaxations of what counts as a match.

## Step 4: joint classification
The two mating faces' surface types are looked up in a six-entry rule table (`step4_classify_joint/input/rule_table.json`). The table states the constraint to impose, which degrees of freedom remain, and how step 5 resolves them. No model is involved; the types are labels in the dataset. An LLM or VLM would add value above this layer (functional intent, unknown type pairs, tie-breaking), which is documented in the output.

## Step 5: placement
Constraints are expressed to CadQuery's assembly solver (`PointOnLine` for coaxiality, `Axis` + `PointInPlane` for a shoulder contact, `Plane` for flush mates). For concentric joints the slide along the axis is not fixed, so candidate stops are enumerated: every planar face adjacent to each mating cylinder whose normal is along the axis (widened to all perpendicular planes when a hole has no shoulder), paired with normals opposed (faces touch) or parallel (faces flush). Each candidate is solved, then scored by sampling the moving part's surface: fraction inside the fixed part (overlap) and fraction within 0.002 cm of it (contact). Poses with overlap are discarded; the most contact wins. The designer's transform is compared afterwards as axis angle, axial offset and radial offset (spin about the axis is free and not counted).

## Step 6: relation inference
A parameter -> face sensitivity map is built by perturbing each parameter by 0.01, rebuilding, and recording which faces change radius or position; this replaces trusting parameter names. The joint's two radii give `part1.p = part2.q + (r1 - r2)`; the assembled model is scanned for other coaxial cylinder pairs with equal radius (shared bores). The pose constraint is kept as a live relation. Output is a small constraint graph (driver, dependent, constant).

## Step 7: propagation
A driver edit is applied, dependent parameters are recomputed from the relations, both scripts rebuild, the pose is re-solved with the stored constraints, and overlap / contact are re-measured. The web UI does this per keystroke (5-10 s).

## Evaluation design
The first ten joint sets available were all axisymmetric, which makes several metrics trivially good (any face pair shares the axis; the dataset marks all such pairs as equivalent). A second set of ten was therefore selected by scanning all 1,926 test joint sets for bodies with at least two distinct axes, 12-60 total faces, and only plane / cylinder / cone / torus / sphere surfaces, spread across joint and entity types. Both sets are reported separately with the metric caveats stated.
