"""Fast step 1: run pretrained JoinABLe on one joint set WITHOUT loading the 1.9 GB split cache.
Python 3.7 `autolink` env. Run from Project_Root: conda run -n autolink python pipeline\joinable_predict_fast.py joint_set_XXXXX Writes pipeline_demo/<js>/step1_joinable_predict/output/prediction_top10.json"""
import sys, json, argparse, time
from pathlib import Path
t0 = time.time()
import torch
ROOT = Path(__file__).resolve().parents[1]; J = ROOT / "third_party" / "JoinABLe"; DATA = ROOT / "data" / "j1.0.0"
sys.path.insert(0, str(J))
from datasets.joint_graph_dataset import JointGraphDataset
from joint.joint_prediction_set import JointPredictionSet
from train import JointPrediction

class OneJointSet(JointGraphDataset):
    """Same loader as upstream, but never loads a split: setup_cache() says 'already loaded'."""
    def setup_cache(self): return True

ap = argparse.ArgumentParser(); ap.add_argument("joint_sets", nargs="+"); ap.add_argument("--k", type=int, default=10); a = ap.parse_args()
model = JointPrediction.load_from_checkpoint(str(J / "pretrained/paper/last_run_0.ckpt"), map_location=torch.device("cpu")); model.eval()
ds = OneJointSet(root_dir=DATA, split="test", label_scheme="Joint,JointEquivalent")
for js in a.joint_sets:
    gs = ds.load_graph(js + ".json"); g1, g2, jg = gs[0], gs[1], gs[2]
    g1 = ds.remove_unused_input_features(g1); g2 = ds.remove_unused_input_features(g2); jg = ds.remap_labels(jg, ds.labels_on, ds.labels_off)
    jps = JointPredictionSet(DATA / (js + ".json"), g1, g2, jg, model, prediction_limit=a.k); pd = jps.prediction_data
    doc = json.loads((DATA / (js + ".json")).read_text(encoding="utf-8"))
    def face_info(body, idx):
        n = json.loads((DATA / f"{body}.json").read_text(encoding="utf-8"))["nodes"][idx]; t = n.get("surface_type", n.get("curve_type", ""))
        return {"index": idx, "entity": "BRepFace" if "surface_type" in n else "BRepEdge", "geometry": t.replace("SurfaceType", "").replace("CurveType", ""), "radius": n.get("radius"), "area_or_length": n.get("area", n.get("length"))}
    out = {"joint_set": js, "checkpoint": "pretrained/paper/last_run_0.ckpt", "body_one": doc["body_one"], "body_two": doc["body_two"], "body_one_nodes": int(g1.num_nodes), "body_two_nodes": int(g2.num_nodes), "k": a.k,
           "run": {"when": time.strftime("%Y-%m-%dT%H:%M:%S"), "seconds": round(time.time() - t0, 2), "live": True},
           "note": "Probabilities are a softmax over ALL body_one x body_two node pairs, so they are small; rank is what matters. Candidates whose axis cannot be computed (NURBS) are dropped by JoinABLe.", "candidates": []}
    for r, p in enumerate(pd["predictions"], 1):
        out["candidates"].append({"rank": r, "probability": p["value"], "body_one": dict(face_info(doc["body_one"], p["body_one"]["index"]), axis_origin=p["body_one"]["origin"], axis_direction=p["body_one"]["direction"]),
                                  "body_two": dict(face_info(doc["body_two"], p["body_two"]["index"]), axis_origin=p["body_two"]["origin"], axis_direction=p["body_two"]["direction"])})
    outp = ROOT / "pipeline_demo" / js / "step1_joinable_predict" / "output" / "prediction_top10.json"; outp.parent.mkdir(parents=True, exist_ok=True); outp.write_text(json.dumps(out, indent=2))
    print("wrote", outp, f"({time.time()-t0:.1f}s) top1:", out["candidates"][0]["body_one"]["index"], out["candidates"][0]["body_two"]["index"])
