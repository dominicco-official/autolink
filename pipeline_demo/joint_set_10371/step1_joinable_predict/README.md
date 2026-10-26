# Step 1 - JoinABLe predicts which faces mate
Tool: pretrained JoinABLe GNN (Python 3.7 env). The only neural network in the pipeline.

Input: `input/<body>.json` x2 (B-Rep graph files; the network never reads the mesh) and the two body ids.
Output: `output/prediction_top10.json` ranked candidate pairs with probability and derived axis.

Top-1: part1 BRepFace[4] (Cylinder) <-> part2 BRepFace[0] (Cylinder), p=0.294
