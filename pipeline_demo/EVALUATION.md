# AutoLink pipeline evaluation (Fusion 360 Gallery test split)

Step-2 model: Claude (Fable 5.1) in the Kiro chat session, acting as the step-2 LLM; verifier = pipeline/verify_recon.py

## Easy set: the first 10 test joint sets that fit on disk (all axisymmetric parts)

- JoinABLe top-1 hit 10/10, but on these parts 100% of all face pairs count as correct (every face shares the axis), so this says little.
- Reconstruction: 20/20 parts pass step 3, 20 on the first script.
- Placement: axis correct 10/10; axial position equals the designer's in 4/10 (the rest admit several stop positions).
- 9 parametric relations; 10/10 example edits rebuild without interference.

| joint set | faces | types | JoinABLe hit rank | GT-ok pairs | step2 attempts | step3 | rule | cands | contact | axis err | axial vs designer | relations | +30% edit overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| joint_set_01324 | 4+7 | cylinder, plane | 1 | 100% | 1 / 1 | PASS | concentric | 8 | 6% | 0.0 deg | 0.3 cm | part1.inner_radius = part2.shaft_radius + 0.003650 | 0% |
| joint_set_03894 | 4+4 | cylinder, plane | 1 | 100% | 1 / 1 | PASS | concentric | 8 | 34% | 0.0 deg | 2.0 cm | part1.inner_radius = part2.outer_radius + 0.000000 | 0% |
| joint_set_04039 | 6+7 | cylinder, plane, torus | 1 | 100% | 1 / 1 | PASS | concentric | 4 | 42% | 0.0 deg | 0.004 cm | part1.bore_radius = part2.neck_radius + 0.000635<br>part1.hole_radius = part2.bore_radius | 0% |
| joint_set_07243 | 4+3 | cylinder, plane | 1 | 100% | 1 / 1 | PASS | concentric (edge->face) | 8 | 2% | 0.0 deg | 0.15 cm | part1.inner_radius = part2.radius + -0.015525 | 0% |
| joint_set_08045 | 2+7 | cylinder, plane, sphere | 1 | 100% | 1 / 1 | PASS | flush_mate | 1 | 21% | 0.0 deg | 13.97 cm | (pose only) | 0% |
| joint_set_10371 | 8+3 | cylinder, plane | 1 | 100% | 1 / 1 | PASS | concentric | 8 | 2% | 0.0 deg | 21.5 cm | part1.hole_radius = part2.radius + 0.000000 | 0% |
| joint_set_10420 | 4+4 | cylinder, plane | 1 | 100% | 1 / 1 | PASS | concentric | 8 | 4% | 0.0 deg | 0.1 cm | part1.hole_radius = part2.hole_radius + 0.000000 | 0% |
| joint_set_11051 | 3+3 | cylinder, plane | 1 | 100% | 1 / 1 | PASS | flush_mate | 1 | 29% | 0.0 deg | 0.0 cm | (pose only) | 0% |
| joint_set_13082 | 14+9 | cone, cylinder, plane, torus | 1 | 100% | 1 / 1 | PASS | concentric | 4 | 5% | 0.0 deg | 0.0 cm | part1.bore_radius = part2.shaft_radius + 0.000000 | 0% |
| joint_set_16475 | 6+5 | cone, cylinder, plane, torus | 1 | 100% | 1 / 1 | PASS | flush_mate | 1 | 42% | 0.0 deg | 0.0 cm | part1.disc_radius = part2.radius | 0% |

## Hard set: 10 joint sets chosen for non-axisymmetric geometry (hole patterns, brackets, levers, 4-26 faces per part)

- JoinABLe top-1 hit 8/10 (top-10: 10/10); here only 7% of face pairs are acceptable, so the hits are meaningful.
- Reconstruction: 18/20 parts attempted, 17 pass step 3, 12 on the first script; 2 not attempted (effort budget); 1 failed after 3 attempts (08709 part 2).
- Placement: axis correct 8/8 placed; axial position equals the designer's in 0/8.
- 9 parametric relations; 5/8 blind +30% example edits rebuild without interference (an automatic +30% on a radius can legitimately create interference; the pipeline reports it rather than hiding it).

| joint set | faces | types | JoinABLe hit rank | GT-ok pairs | step2 attempts | step3 | rule | cands | contact | axis err | axial vs designer | relations | +30% edit overlap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| joint_set_03531 | 6+15 | cylinder, plane | 1 | 0% | 1 / 1 | PASS | flush_mate | 1 | 88% | 0.0 deg | 0.2 cm | (pose only) | 0% |
| joint_set_04827 | 15+19 | cone, cylinder, plane | 1 | 2% | 2 / 1 | PASS | concentric | 8 | 29% | 0.0 deg | 0.3 cm | part1.bore_radius = part2.shaft_radius + -0.000825 | 25% |
| joint_set_08709 | 6+20 | cone, cylinder, plane, torus | 1 | 9% | 2 / FAIL after 3 | FAIL | - | - | - | - | - | - | - |
| joint_set_09176 | 13+6 | cylinder, plane, torus | 1 | 9% | 1 / 1 | PASS | concentric | 16 | 64% | 0.0 deg | 2.995 cm | part1.rod_radius = part2.inner_radius + 0.000000 | 0% |
| joint_set_11584 | 12+9 | cone, cylinder, plane | 1 | 12% | 2 / 2 | PASS | concentric | 8 | 0% | 0.0 deg | 2.05 cm | part1.hole_radius = part2.radius + 0.000000 | 2% |
| joint_set_12396 | 7+15 | cone, cylinder, plane, torus | 1 | 6% | 1 / 1 | PASS | concentric (edge->face) | 8 | 8% | 0.0 deg | 1.5 cm | part1.bore_radius = part2.tab_hole_r + 0.000000 | 0% |
| joint_set_13342 | 8+14 | cone, cylinder, plane | 8 | 8% | 1 / 1 | PASS | concentric | 8 | 21% | 0.0 deg | 0.145 cm | part1.tip_radius = part2.h8_r + -0.000000 | 0% |
| joint_set_14090 | 16+19 | cone, cylinder, plane, torus | 3 | 8% | not attempted / not attempted | - | - | - | - | - | - | - | - |
| joint_set_14572 | 11+14 | cylinder, plane | 1 | 3% | 3 / 1 | PASS | concentric | 8 | 6% | 0.0 deg | 0.476 cm | part1.bottom_pin_radius = part2.end_hole_radius + 0.000000<br>part1.end_radius = part2.end_radius | 0% |
| joint_set_17464 | 6+16 | cylinder, plane, torus | 1 | 9% | 1 / 1 | PASS | concentric | 4 | 17% | 0.0 deg | 0.925 cm | part1.head_radius = part2.cbore_radius + -0.000000<br>part1.bore_radius = part2.cross_radius | 52% |

## Verifier changes made while running the hard set
- centroid tolerance now 0.1% of bbox diagonal (min 0.002 cm)
- trimmed cylinder faces via BRepAdaptor_Surface
- surface-distance sampling chunked (memory)
- tessellation deflection scales with part size
- CONE<->CYLINDER compatible when taper ~0

Dataset: Fusion 360 Gallery Assembly dataset (non-commercial research licence). Per-step files: `pipeline_demo/<joint_set>/stepN_*/`. Attempt log: `recon/ATTEMPTS.json`.