# Licenses

AutoLink Phase 1 combines two externally licensed inputs: the Fusion 360
Gallery Assembly-Joint Dataset (restrictive research license) and the JoinABLe
source code and pretrained checkpoints (MIT). This document records the terms
AutoLink is bound by, where the official texts live, and the exact notice to
attach to Dataset-derived artifacts. The short rule set Kiro applies while
editing code is in `.kiro/steering/licenses.md`; the two must agree.

## 1. Fusion 360 Gallery Assembly-Joint Dataset (the Dataset)

- Dataset: Fusion 360 Gallery Dataset, Assembly-Joint subset, version `j1.0.0`
  (`j1.0.0.7z`, `j1.0.0_preprocessed.7z`), provided by Autodesk, Inc.
- Official license text (read 2026-10-24, "Updated 11/2021"):
  https://github.com/AutodeskAILab/Fusion360GalleryDataset/blob/master/LICENSE.md
- Dataset home page: https://github.com/AutodeskAILab/Fusion360GalleryDataset
- Assembly-Joint documentation:
  https://github.com/AutodeskAILab/Fusion360GalleryDataset/blob/master/docs/assembly_joint.md

### Terms that bind this project

| Term | What it means for AutoLink |
|---|---|
| **Non-commercial research only.** The Dataset may be accessed, used, reproduced, and modified only for non-commercial research purposes (License item 1). | Everything derived from the Dataset (renders, candidate JSON, evaluation JSON, pose results, summary tables, the Curated_Set) inherits this restriction. |
| **No redistribution of the Dataset in its entirety.** The Dataset may not be redistributed or made available to others in whole (License item 2). | No Dataset file is ever committed. Others are directed to the official download URL above. |
| **Attribution required for shared portions.** Portions or modifications of the Dataset may be shared only if they are not represented as the Dataset itself, carry attribution, and are limited to non-commercial research use with the same restrictions passed downstream (License items 3 and 5). | Every Dataset-derived artifact committed under `results/` is covered by the notice in section 3 and by `results/NOTICE.md`. |

Additional items from the license text that AutoLink honours: no attempt is
made to re-associate any model with its creator (item 4); Autodesk trade
names are used only to describe the origin of the Dataset (item 6); the
Dataset is provided without warranty (item 7).

### Files that are never committed

Joint set JSON (`joint_set_XXXXX.json`), body graph JSON, OBJ meshes, SMT and
STEP B-Rep files, thumbnail PNGs, `train_test.json`, the Preprocessed_Cache
pickles (`train.pickle`, `val.pickle`, `test.pickle`), and the `.7z`
archives. `.gitignore` excludes `data/`, `*.7z`, and `*.pickle`.

## 2. JoinABLe source code and pretrained checkpoints

- Repository: https://github.com/AutodeskAILab/JoinABLe
- Vendored at commit `5a3b9933e91269d19b6cc733b244a879eb4bfc30`
  (recorded in `third_party/JOINABLE_COMMIT`); the license text below was
  read from `third_party/JoinABLe/LICENSE` at that commit.
- License: MIT. The five pretrained checkpoints
  `third_party/JoinABLe/pretrained/paper/last_run_{0..4}.ckpt` are
  distributed by the JoinABLe authors inside that repository and are kept
  where upstream keeps them; AutoLink does not re-host them.
- Paper to cite: Karl D. D. Willis, Pradeep Kumar Jayaraman, Hang Chu, Yunsheng
  Tian, Yifei Li, Daniele Grandi, Aditya Sanghi, Linh Tran, Joseph G. Lambourne,
  Armando Solar-Lezama, Wojciech Matusik. "JoinABLe: Learning Bottom-up
  Assembly of Parametric CAD Joints." CVPR 2022.

Any modification AutoLink makes to the vendored code is recorded in the
Patch_Set under `third_party/patches/` and keeps the copyright notice and
permission notice below in place.

```text
MIT License

Copyright (c) 2022 Autodesk, Inc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 3. Attribution and non-commercial notice for Dataset-derived artifacts

The text below is the exact notice to attach to every Dataset-derived
artifact (Visualization, JSON excerpt, or Markdown table containing Joint_Set
data) that is committed to this repository. It is placed either inside the
artifact (a `"notice"` field in JSON, a notice line in Markdown) or in a
`NOTICE.md` file in the same directory as the artifact. `results/NOTICE.md`
carries this text for everything under `results/`.

> **Attribution and non-commercial notice.** This artifact is a portion or
> modification of the Fusion 360 Gallery Dataset (Assembly-Joint subset,
> version j1.0.0) provided by Autodesk, Inc., and is not the Dataset itself.
> It is made available for non-commercial research purposes only, under the
> Fusion 360 Gallery Dataset License
> (https://github.com/AutodeskAILab/Fusion360GalleryDataset/blob/master/LICENSE.md).
> Recipients may access, use, reproduce, modify, or redistribute it only for
> non-commercial research purposes and must retain this notice. The Dataset
> itself is not redistributed here; obtain it from
> https://github.com/AutodeskAILab/Fusion360GalleryDataset. Predictions were
> produced with the JoinABLe pretrained model (Autodesk Research, MIT License;
> Willis et al., "JoinABLe: Learning Bottom-up Assembly of Parametric CAD
> Joints", CVPR 2022).

Short form for a single JSON `"notice"` field or a one-line Markdown footer:

```text
Derived from the Fusion 360 Gallery Dataset (Autodesk, Inc.); non-commercial research use only; not the Dataset itself; see results/NOTICE.md and docs/licenses.md.
```

## 4. AutoLink-authored code

AutoLink-authored files (`autolink/`, `scripts/`, `tests/`, `docs/`,
`environment/`, `.kiro/`, `README.md`, `autolink.config.json`,
`third_party/patches/`) are the Developer's own work. No license has been
chosen for them yet; choosing one is recorded as an open item in
[`decisions.md`](decisions.md). Whatever is chosen must stay compatible with
MIT redistribution of the vendored code and must not loosen the Dataset
restrictions on derived artifacts.

## 5. Adding dependencies

Before any new package is added to the Environment, its license is checked
for compatibility with non-commercial research use and with MIT
redistribution of AutoLink code, and the addition is recorded in
[`decisions.md`](decisions.md).