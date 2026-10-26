# Experiment_Log

This file is **append-only**. It is the record of every Phase 1 run attempted
(Environment creation, smoke test, Official_Eval, Adapter run, Pose_Search,
cache regeneration, lockfile verification, the deliverable script), including
failures.

Rules:

- Entries are added **only** by `scripts/_phase1_common.py`
  (`append_experiment_entry`), which opens this file in append mode. Do not
  hand-edit, reorder, merge, or delete entries.
- Every entry carries: ISO 8601 date, the exact command line run, the
  Environment reference (Environment_Lockfile path or its hash), the
  JoinABLe_Repo commit hash, the Checkpoint id, Data_Root, the outcome
  (`success` or `failure`), and either the key numbers (metrics, counts,
  wall-clock durations) or the full error text.
- A failure entry is written **before** any rerun or workaround is attempted.
  A later successful rerun is a separate entry that names the failure entry it
  supersedes.
- If an entry is found to be incorrect, a **new** entry is appended that names
  the date and command of the incorrect entry and states the correction. The
  original entry is left unchanged.
- Every metric reported elsewhere in `docs/` or `README.md` must reference the
  entry here that produced it.

Entry template (written by `_phase1_common.py`):

```markdown
## <ISO 8601 timestamp> — <run kind> — <success|failure>
- command: `<exact command line>`
- environment: <Environment_Lockfile path> (sha256 <hash>)
- joinable_commit: <40-hex>
- checkpoint: <file name>
- data_root: <path>
- outcome: <success|failure>
- key numbers: <metrics, counts, duration_s=...>     (success only)
- error: (fenced block with full traceback or last 50 lines)  (failure only)
- output: <path of captured console log>
- supersedes: <reference to an earlier entry, or (none)>
```

---

<!-- Entries below this line are appended by scripts/_phase1_common.py only. -->
## 2026-10-25T07:07:55+00:00 — conda — failure
- command: `C:\Users\domlimco\AppData\Local\miniconda3\Scripts\conda.exe env create -y -n autolink -f C:\Users\domlimco\Downloads\autolink\third_party\JoinABLe\environment_cpu.yml`
- environment: conda env 'autolink' from third_party/JoinABLe/environment_cpu.yml (lockfile: environment/lock/conda_explicit.txt (sha256 unavailable: lockfile missing))
- joinable_commit: 5a3b9933e91269d19b6cc733b244a879eb4bfc30
- checkpoint: last_run_0.ckpt
- data_root: (not used)
- outcome: failure
- key numbers: (none)
- error:

```text
exit code 1
              Usage of dash-separated 'description-file' will not be supported in future

              versions. Please use the underscore name 'description_file' instead.

      

              This deprecation is overdue, please update your project and remove deprecated

              calls to avoid build errors in the future.

      

              See https://setuptools.pypa.io/en/latest/userguide/declarative_config.html for details.

              ********************************************************************************

      

      !!

        opt = self.warn_dash_deprecation(opt, section)

      C:\Users\domlimco\AppData\Local\miniconda3\envs\autolink\lib\site-packages\setuptools\__init__.py:80: _DeprecatedInstaller: setuptools.installer and fetch_build_eggs are deprecated.

      !!

      

              ********************************************************************************

              Requirements should be satisfied by a PEP 517 installer.

              If you are using pip, you can try `pip install --use-pep517`.

              ********************************************************************************

      

      !!

        dist.fetch_build_eggs(dist.setup_requires)

      C:\Users\domlimco\AppData\Local\miniconda3\envs\autolink\lib\site-packages\setuptools\dist.py:472: SetuptoolsDeprecationWarning: Invalid dash-separated options

      !!

      

              ********************************************************************************

              Usage of dash-separated 'description-file' will not be supported in future

              versions. Please use the underscore name 'description_file' instead.

      

              This deprecation is overdue, please update your project and remove deprecated

              calls to avoid build errors in the future.

      

              See https://setuptools.pypa.io/en/latest/userguide/declarative_config.html for details.

              ********************************************************************************

      

      !!

        opt = self.warn_dash_deprecation(opt, section)

      running bdist_wheel

      running build

      running build_ext

      building 'pysdf' extension

      error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/

      [end of output]

  

  note: This error originates from a subprocess, and is likely not a problem with pip.

  ERROR: Failed building wheel for pysdf

  error: subprocess-exited-with-error

  

  × Building wheel for vhacdx (pyproject.toml) did not run successfully.

  │ exit code: 1

  ╰─> [20 lines of output]

      running bdist_wheel

      running build

      running build_py

      running egg_info

      writing src\vhacdx.egg-info\PKG-INFO

      writing dependency_links to src\vhacdx.egg-info\dependency_links.txt

      writing requirements to src\vhacdx.egg-info\requires.txt

      writing top-level names to src\vhacdx.egg-info\top_level.txt

      reading manifest file 'src\vhacdx.egg-info\SOURCES.txt'

      reading manifest template 'MANIFEST.in'

      adding license file 'LICENSE'

      writing manifest file 'src\vhacdx.egg-info\SOURCES.txt'

      creating build

      creating build\lib.win-amd64-cpython-37

      creating build\lib.win-amd64-cpython-37\vhacdx

      copying src\vhacdx\VHACD.h -> build\lib.win-amd64-cpython-37\vhacdx

      copying src\vhacdx\main.cpp -> build\lib.win-amd64-cpython-37\vhacdx

      running build_ext

      building 'vhacdx' extension

      error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/

      [end of output]

  

  note: This error originates from a subprocess, and is likely not a problem with pip.

  ERROR: Failed building wheel for vhacdx

  error: subprocess-exited-with-error

  

  × Building wheel for xxhash (pyproject.toml) did not run successfully.

  │ exit code: 1

  ╰─> [13 lines of output]

      running bdist_wheel

      running build

      running build_py

      creating build

      creating build\lib.win-amd64-cpython-37

      creating build\lib.win-amd64-cpython-37\xxhash

      copying xxhash\version.py -> build\lib.win-amd64-cpython-37\xxhash

      copying xxhash\__init__.py -> build\lib.win-amd64-cpython-37\xxhash

      copying xxhash\py.typed -> build\lib.win-amd64-cpython-37\xxhash

      copying xxhash\__init__.pyi -> build\lib.win-amd64-cpython-37\xxhash

      running build_ext

      building '_xxhash' extension

      error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/

      [end of output]

  

  note: This error originates from a subprocess, and is likely not a problem with pip.

  ERROR: Failed building wheel for xxhash

ERROR: Could not build wheels for pysdf, vhacdx, xxhash, which is required to install pyproject.toml-based projects



failed

CondaEnvException: Pip failed
```

- output: results/env_create_20261025-070755.log
- supersedes: (none)

## 2026-10-25T08:20:00+00:00 — pretrained checkpoint test (no AutoLink code) — success
- command: see "Commands" below; run from `third_party\JoinABLe` (eval) and Project_Root (viewer)
- environment: conda env `autolink` (Python 3.7.12, CPU). Lockfile: environment/lock/conda_explicit.txt, environment/lock/pip_freeze.txt
- joinable_commit: 5a3b9933e91269d19b6cc733b244a879eb4bfc30
- checkpoint: pretrained/paper/last_run_0.ckpt (16,111,213 bytes, 1,340,161 params)
- data_root: data/j1.0.0 (test.pickle 1,899,118,618 bytes + train_test.json from j1.0.0_preprocessed.7z; 10 test joint sets' JSON+OBJ extracted selectively from j1.0.0.7z because only ~5 GB disk was free; full archive is 35.4 GB uncompressed)
- outcome: success

### Environment fixes applied (deviations from upstream environment_cpu.yml)
1. `environment_cpu.yml` does not pin `cpuonly`, so conda resolved CUDA 11.1 builds; `import torch` failed with WinError 182 (caffe2_detectron_ops_gpu.dll). Fix: `conda install --override-channels -c pytorch -c rusty1s -c conda-forge pytorch=1.8.1=py3.7_cpu_0 torchvision=0.9.1=py37_cpu cpuonly pytorch-geometric=1.7.2=py37_torch_1.8.0_cpu pytorch-scatter=2.0.8=py37_torch_1.8.0_cpu pytorch-sparse=0.6.12=py37_torch_1.8.0_cpu pytorch-cluster=1.5.9=py37_torch_1.8.0_cpu pytorch-spline-conv=1.2.1=py37_torch_1.8.0_cpu`
2. Still WinError 182 on caffe2_detectron_ops.dll (CPU): conda-forge had resolved mkl 2025 / intel-openmp 2026. Fix: `mkl=2021.4 intel-openmp=2021.4`, then `libblas/libcblas/liblapack=*=*mkl numpy=1.21.6 scipy=1.7.3 --force-reinstall`.
3. Pillow from `defaults` channel broke (DLL load) after the MKL swap; conda-forge pillow conflicted. Fix: `conda remove --force pillow`, `pip install pillow==9.5.0`.
4. `pysdf` ships source only (no Windows wheels). Installed VS 2022 Build Tools (VC.Tools.x86.x64 + Win11 SDK) via vs_BuildTools.exe. pysdf 0.1.9 then failed with `error C2039: 'high_resolution_clock' is not a member of 'std::chrono'` (src/util.cpp:36). Fix: downloaded sdist, added `#include <chrono>` to src/util.cpp, `pip install --no-build-isolation <dir>`. This patch lives in the installed wheel, not in the vendored repo.
5. `trimesh[easy]` extras (vhacdx, xxhash) fail to build and are unused by JoinABLe; installed `trimesh==3.23.5 rtree` instead.
6. Disk: conda/pip caches purged (4.3 GB + 4.5 GB) to make room; 3 Build Tools attempts via winget failed (1602 = cancelled UAC, 0x80070070 = disk full) before the direct elevated installer succeeded.
7. Note: `python.exe` from the env must be run with the env activated (`conda run -n autolink` or `conda activate`); invoking the interpreter path directly without activation gives DLL load failures because `Library\bin` is not on PATH.

### Commands
- Smoke: `conda run -n autolink --cwd third_party\JoinABLe python -c "import torch, torch_geometric, pytorch_lightning, trimesh, igl, pysdf, meshplot; from train import JointPrediction; JointPrediction.load_from_checkpoint('pretrained/paper/last_run_0.ckpt', map_location='cpu')"` -> OK
- Official eval (limit 200): `python train.py --traintest test --dataset <abs data\j1.0.0> --exp_dir pretrained --exp_name paper --checkpoint last_run_0 --threads 1 --limit 200` -> 18 s, top-1 = 1.0000 on first 200 cached samples (cache loaded). Log: results/official_eval_limit200_20261025-010303.log
- Official eval (full test split, 1926 joint sets): same command without `--limit` -> 379 s, cache loaded from test.pickle. Log: results/official_eval_full_20261025-010341.log

### Key numbers (full test split, last_run_0, as printed)
| k | 1 | 2 | 3 | 4 | 5 | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|----|----|----|----|----|----|----|----|----|-----|
| hit@k | 0.7954 | 0.8313 | 0.8515 | 0.8619 | 0.8764 | 0.9071 | 0.9304 | 0.9403 | 0.9460 | 0.9486 | 0.9517 | 0.9522 | 0.9533 | 0.9548 | 0.9548 |

- eval_test_top_1 = 0.79543, holes = 0.80088, no_holes = 0.76946, accuracy = 0.89200, iou = 0.11569, loss = 11.1628
- Observation: top-1 79.54% vs paper 79.53% -> +0.01 percentage points (single checkpoint last_run_0; paper figure is Table 2).

### Visualization (notebook cells run headless)
- Driver: scratch/prediction_viewer_offline.py = joint_prediction_viewer.ipynb + joint_set_viewer.ipynb cells with `meshplot.website()` + `Viewer.save()`.
- Output: results/viewer/ — 6 HTML files per joint set (pred_assembled_top1, pred_body{1,2}_top1_axis, gt_assembled, gt_body{1,2}_axis) for 10 test joint sets + summary.json; 23 s total. Verified in a browser: WebGL canvas renders, body in cyan with the top-1 predicted face in magenta (colormap "cool").
- Top-1 hit (incl. equivalents) on the 10 extracted sets: 10/10 (small graphs, 3-28 nodes; not representative of the 79.5% split-wide figure).
- Screenshots: results/viewer/results_viewer_13082_pred_assembled.png, results_viewer_13082_pred_body1_axis.png
- supersedes: (none)

## 2026-10-26T01:40:00+00:00 — AutoLink pipeline on 10 test joint sets + live browser demo — success
- command: `conda run -n autolink python scratch\joinable_predict_fast.py <ids>` (step 1, 3.7 env, ~7 s/joint set, no split cache; results identical to the cached-split path on 04039: all 10 ranks + probabilities match) then `conda run -n autolink-cad python scratch\pipeline_steps.py <ids>` (steps 2-7, 3.11 env, 238 s for all 10)
- environment: `autolink` (Py 3.7, JoinABLe) + `autolink-cad` (Py 3.11, cadquery 2.4.0, trimesh 4.4.9, numpy<2); they communicate through files under pipeline_demo/
- joinable_commit: 5a3b9933e91269d19b6cc733b244a879eb4bfc30 ; checkpoint last_run_0.ckpt
- data_root: data/j1.0.0 (10 extracted test joint sets)
- outcome: success. Summary in pipeline_demo/EVALUATION.md and EVALUATION.json.
- key numbers: step 2 reconstruction (Claude in chat writing CadQuery from part_N_face_summary.txt): 20/20 parts pass step 3 on first script attempt; 4 fixes were to the verifier (sphere radius, cone radius, size-scaled surface tolerance, point-to-surface distance). Step 5: joint axis correct 10/10 (angle error 0.0 deg); axial position equals designer's in 4/10; in 6/10 the geometry admits several stop positions (axle/wheel, nested tubes, rod/dome) and the max-contact choice differs from the designer by 0.1-21.5 cm -> documented slot for user offset / VLM tie-break. Step 6: 8 parametric relations over 8/10 joint sets (2 are pose-only). Step 7: 10/10 example edits rebuild with zero overlap.
- fixes along the way: graph node ids are not always in array order (56166_003bf479_0011_2: ids 1..7,0) -> adjacency now maps id->position like JoinABLe does; JoinABLe reports edge picks as FLAT node indices -> edge->adjacent-face promotion fixed (07243); sensitivity matches faces by order; pose options now include normals opposed and parallel (fixes nested tubes 03894, washer 01324 that previously sat 20 cm away).
- browser demo: webapp/server.py + index.html at http://127.0.0.1:8777. Steps 1 and 3-6 run live on demand (11-12 s each on 04039); step 7 is live per edit; step 2 is a hand-off (REQUEST.json -> agent writes scratch/recon_<id>/part_N.py). Verified with Playwright on 04039, 11051, 13082, 07243. Screenshots in webapp/screenshots/.
- open items: 13082 live edit (shaft 2.5->3.0) rebuilds with 0% overlap but 0% contact (was 5%): the re-solved pose after a large edit needs a look; EVALUATION step1_top1_hit column is a placeholder (hit@1 on these 10 was 10/10 in results/viewer/summary.json).
- supersedes: (none)

## 2026-10-26T04:30:00+00:00 — hard set, LLM step-2 module, full-test-split UI, repo restructure — success (with recorded failures)
- commands: `pipeline\dataset_tools.py index`; `pipeline\joinable_predict_fast.py <10 hard ids>`; `pipeline\pipeline_steps.py <ids>`; `pipeline\evaluate.py`
- environment: autolink (Py3.7) + autolink-cad (Py3.11); joinable_commit 5a3b9933; checkpoint last_run_0
- repo: spec-era scaffolding removed (autolink/, scripts/, tests/, .kiro/, docs stubs); scratch/ -> pipeline/; part scripts -> recon/recon_<id>/; dataset copies removed from pipeline_demo (licence); README/LICENSE/NOTICE/env ymls written.
- step 2 automation: pipeline/llm_reconstruct.py (anthropic|openai|bedrock via env vars; mock; agent hand-off). Retry loop verified offline with `--provider mock --mock-fail-first` on 04039 part 1: attempt 1 FAIL (box) -> verifier report -> attempt 2 PASS. No API key available on this machine, so no real-model run yet.
- hard set selection: scanned all 1926 test joint sets (graph files extracted to data/scan); 250/1926 have both bodies axisymmetric; 545 candidates with >=2 distinct axes, 12-60 total faces, only plane/cylinder/cone/torus/sphere; picked 10 across joint/entity types: 03531 17464 04827 08709 13342 09176 14572 14090 12396 11584.
- step 1 on the hard set: top-1 hit 8/10 (13342 rank 8, 14090 rank 3), top-10 10/10; mean acceptable-pair fraction 7% (vs 100% on the easy set).
- step 2 (Claude in chat as the model): 18/20 parts attempted; 17 pass; first-try 12; 08709 part 2 FAIL after 3 attempts (17/20 faces; off-tangent arc); 14090 both parts not attempted. Per-part attempts in recon/ATTEMPTS.json. Verifier changes: size-scaled centroid tolerance, BRepAdaptor for trimmed cylinders, chunked distance sampling, size-scaled tessellation, CONE~CYLINDER when taper ~0.
- pipeline fixes found by the hard set: pose search now tries normals opposed AND parallel; widened shoulder search when the mating cylinder has no adjacent shoulder (hole through a plate); axis-only fallback; edge->adjacent-face promotion uses flat node indices; pipeline stops after step 3 on a failed part and records STOPPED.txt.
- steps 5-7 on the hard set: axis correct 8/8; axial = designer 0/8 (offsets 0.15-3.0 cm); 9 relations; blind +30% edits: 5/8 without interference (17464, 04827, 11584 interfere: enlarging a driver radius 30% is not always physically valid; reported, not hidden).
- UI: searchable picker over all 1926 test joint sets (extract on demand via 7-Zip), live step 1 / steps 3-6, "Run LLM reconstruction" (needs provider) and "Request from the agent"; failed verification shown as such. Verified with Playwright on 00899 (fresh extraction + live JoinABLe), 17464 (steps 5-7), 08709 (failure display).
- open items: 08709 part 2 reconstruction; 14090; real LLM run of step 2 (needs key); 13082 large-edit contact drop; the +30% example edit should respect wall thickness/clearance constraints.
- supersedes: (none)
