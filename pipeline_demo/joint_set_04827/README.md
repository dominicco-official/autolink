# Pipeline walk-through for joint_set_04827
Each `stepN_*` folder has `input/`, `output/`, `README.md`.

| Step | What | Tool | AI? |
|---|---|---|---|
| 1 | which faces mate | JoinABLe GNN | yes |
| 2 | rebuild as parametric CAD | LLM writes CadQuery | yes |
| 3 | verify rebuild | CadQuery + trimesh | no |
| 4 | classify joint | rule table | no |
| 5 | place parts | CadQuery solver + sampling | no |
| 6 | infer relations | sensitivity + scan | no |
| 7 | propagate edit | CadQuery | no |
