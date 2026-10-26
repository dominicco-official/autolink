# Windows setup notes

Two conda environments are used because JoinABLe's code is pinned to Python 3.7 / PyTorch 1.8 and CadQuery needs Python 3.11.
They talk through files (`pipeline_demo/`), and the web server calls the Python 3.7 side as a subprocess for step 1.

## 1. JoinABLe environment (`autolink`, Python 3.7)

`conda env create -n autolink -f environment\autolink_joinable_cpu.yml`

What went wrong with the upstream `environment_cpu.yml` on Windows, and the fix baked into the yml above:

1. No `cpuonly` pin -> conda picked CUDA 11.1 builds; `import torch` failed with `WinError 182 ... caffe2_detectron_ops_gpu.dll`. Fix: `pytorch=1.8.1=py3.7_cpu_0`, `cpuonly`, and the `*_cpu` PyG 1.7.2 builds from the `rusty1s` channel.
2. conda-forge resolved MKL 2025 / intel-openmp 2026; torch 1.8 then failed on `caffe2_detectron_ops.dll`. Fix: `mkl=2021.4`, `intel-openmp=2021.4` (and reinstall numpy/scipy/libblas against it).
3. `pillow` from the defaults channel lost its DLLs after the MKL swap. Fix: `pip install pillow==9.5.0`.
4. `pysdf` has no Windows wheels. Install Visual Studio 2022 Build Tools (C++ workload), download the 0.1.9 sdist, add `#include <chrono>` to `src/util.cpp`, then `pip install --no-build-isolation <dir>`. (`trimesh[easy]` extras `vhacdx`/`xxhash` also fail to build and are not needed; install plain `trimesh`.)
5. Run Python with the environment activated (`conda run -n autolink ...` or `conda activate`). Calling the interpreter by path without activation gives DLL load failures because `Library\bin` is not on PATH.

Smoke test: `conda run -n autolink --cwd third_party\JoinABLe python -c "import torch, torch_geometric, pytorch_lightning, trimesh, igl, pysdf; from train import JointPrediction; JointPrediction.load_from_checkpoint('pretrained/paper/last_run_0.ckpt', map_location='cpu'); print('ok')"`

Official evaluation (needs `data/j1.0.0/test.pickle` from the preprocessed archive): `python train.py --traintest test --dataset <abs data\j1.0.0> --exp_dir pretrained --exp_name paper --checkpoint last_run_0 --threads 1` from `third_party\JoinABLe`. 379 s on CPU; top-1 0.7954 (paper 0.7953). Log: `results/official_eval_full_20261025-010341.log`.

## 2. CAD environment (`autolink-cad`, Python 3.11)

`conda env create -n autolink-cad -f environment\autolink_cad.yml`. cadquery 2.4.0 needs `numpy<2` (`np.bool8`).

## 3. Data

Install 7-Zip. `conda run -n autolink-cad python pipeline\dataset_tools.py fetch` prints the two archive URLs (2.8 GB + 514 MB) and expected sizes.
Put them in `data/`, run `fetch` again: it extracts `train_test.json`, the test-split graph files into `data/scan/` (~5 GB), and builds `data/test_split_index.json`.
Individual joint sets are extracted into `data/j1.0.0/` on demand (`dataset_tools.py extract joint_set_XXXXX` or from the web UI). The full dataset is 35 GB unpacked; you do not need it.

## 4. Lockfiles

`environment/lock/conda_explicit.txt` and `pip_freeze.txt` are the exact `autolink` (Python 3.7) environment that produced the results in `docs/experiments.md`.
