"""
Headless run of JoinABLe's notebooks/joint_prediction_viewer.ipynb and
notebooks/joint_set_viewer.ipynb.

Same calls as the notebook cells. Only difference: meshplot is put in "website"
mode so each plot is saved as a self-contained HTML file instead of shown as a
Jupyter widget.

Usage (from Project_Root with the autolink env):
    conda run -n autolink python scratch\prediction_viewer_offline.py
Outputs: results\viewer\<joint_set_id>_*.html + summary.json
"""
import sys
import json
import argparse
from pathlib import Path

import torch
import meshplot as mp

ROOT = Path(__file__).resolve().parents[1]
JOINABLE = ROOT / "third_party" / "JoinABLe"
DATA_DIR = ROOT / "data" / "j1.0.0"
OUT_DIR = ROOT / "results" / "viewer"

sys.path.insert(0, str(JOINABLE))
from joint.joint_prediction_set import JointPredictionSet  # noqa: E402
from joint.joint_environment import JointEnvironment  # noqa: E402
from joint.joint_set import JointSet  # noqa: E402
from datasets.joint_graph_dataset import JointGraphDataset  # noqa: E402
from train import JointPrediction  # noqa: E402

mp.website()  # plot() returns a Viewer and does not auto-save/display


def save(p, name):
    p.save(str(OUT_DIR / name))


def render_prediction(jps, stem):
    # notebook cell: assembled pair under top-1 prediction with default params
    transform = JointEnvironment.get_transform_from_parameters(
        jps, prediction_index=0, offset=0, rotation_in_degrees=0, flip=False
    )
    v, f, c, e, n, ni = jps.get_meshes(
        apply_transform=True,
        body_one_transform=transform,
        show_joint_entity_colors=False,
        show_joint_equivalent_colors=False,
        return_vertex_normals=True,
    )
    save(mp.plot(v, f, c=c), f"{stem}_pred_assembled_top1")

    # notebook cells: per-body top-1 predicted entity (colored) + predicted axis (green)
    for body in (1, 2):
        vb, fb, _, _ = jps.get_mesh(
            body=body,
            apply_transform=False,
            show_joint_entity_colors=False,
            show_joint_equivalent_colors=False,
        )
        cb, eb = jps.get_joint_predictions(body=body, limit=1)
        p = mp.plot(vb, fb, c=cb, shading={"colormap": "cool", "normalize": [0, 1]})
        if eb is not None:
            p.add_edges(vb, eb, shading={"line_color": "red"})
        start_pts, end_pts = jps.get_joint_prediction_axis_lines(body=body, limit=1)
        p.add_lines(start_pts, end_pts, shading={"line_color": "green"})
        p.add_points(start_pts, shading={"point_color": "green", "point_size": 1})
        save(p, f"{stem}_pred_body{body}_top1_axis")


def render_ground_truth(joint_file, stem):
    # joint_set_viewer.ipynb cells: designer's joint (red = entity, yellow = equivalents)
    js = JointSet(joint_file)
    v, f, c, e = js.get_meshes(
        joint_index=0, show_joint_entity_colors=False, show_joint_equivalent_colors=False
    )
    p = mp.plot(v, f, c=c)
    if e is not None:
        if e[0] is not None:
            p.add_edges(v, e[0], shading={"line_color": "red"})
        if e[1] is not None:
            p.add_edges(v, e[1], shading={"line_color": "yellow"})
    save(p, f"{stem}_gt_assembled")

    for body in (1, 2):
        vb, fb, cb, eb = js.get_mesh(body=body, show_joint_equivalent_colors=False)
        p = mp.plot(vb, fb, c=cb)
        if eb is not None:
            if eb[0] is not None:
                p.add_edges(vb, eb[0], shading={"line_color": "red"})
            if eb[1] is not None:
                p.add_edges(vb, eb[1], shading={"line_color": "yellow"})
        start_pt, end_pt = js.get_joint_axis_line(body=body)
        p.add_lines(start_pt, end_pt, shading={"line_color": "green"})
        p.add_points(start_pt, shading={"point_color": "green", "point_size": 1})
        save(p, f"{stem}_gt_body{body}_axis")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--checkpoint", default="pretrained/paper/last_run_0.ckpt")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    extracted = sorted(p.name for p in DATA_DIR.glob("joint_set_*.json"))[: args.limit]
    print(f"{len(extracted)} joint sets with geometry on disk")

    # notebook cell: load network on CPU
    model = JointPrediction.load_from_checkpoint(
        str(JOINABLE / args.checkpoint), map_location=torch.device("cpu")
    )
    model.eval()

    # notebook cell: dataset (loads test.pickle)
    dataset = JointGraphDataset(root_dir=DATA_DIR, split="test", label_scheme="Joint,JointEquivalent")
    index_of = {name: i for i, name in enumerate(dataset.files)}

    summary = []
    for name in extracted:
        stem = Path(name).stem
        if name not in index_of:
            print(f"{stem}: not in test split cache, skipping")
            continue
        index = index_of[name]
        g1, g2, joint_graph = dataset[index]
        joint_file = DATA_DIR / name

        # notebook cell: run inference, build the prediction set
        jps = JointPredictionSet(joint_file, g1, g2, joint_graph, model)
        top1 = jps.prediction_data["predictions"][0]

        # ground-truth entity indices (joint + equivalents) as flat graph node indices
        label_matrix = joint_graph.edge_attr.view(g1.num_nodes, g2.num_nodes)
        gt_pairs = {(int(a), int(b)) for a, b in torch.nonzero(label_matrix).tolist()}
        pred_pair = (top1["body_one"]["index"], top1["body_two"]["index"])
        hit = pred_pair in gt_pairs

        render_prediction(jps, stem)
        render_ground_truth(joint_file, stem)

        row = {
            "joint_set": stem,
            "dataset_index": index,
            "body_one": jps.joint_data["body_one"],
            "body_two": jps.joint_data["body_two"],
            "n1": int(g1.num_nodes),
            "n2": int(g2.num_nodes),
            "top1_prob": top1["value"],
            "top1_body_one": f'{top1["body_one"]["type"]}[{top1["body_one"]["index"]}]',
            "top1_body_two": f'{top1["body_two"]["type"]}[{top1["body_two"]["index"]}]',
            "top1_hits_ground_truth": hit,
            "num_gt_pairs": len(gt_pairs),
        }
        summary.append(row)
        print(f"{stem}: n1={row['n1']} n2={row['n2']} top1={row['top1_body_one']} x {row['top1_body_two']} "
              f"p={row['top1_prob']:.3f} hit={hit}")

    with open(OUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"top-1 hits: {sum(r['top1_hits_ground_truth'] for r in summary)}/{len(summary)}")
    print(f"wrote {OUT_DIR}")


if __name__ == "__main__":
    main()
