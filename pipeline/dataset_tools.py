"""Index the test split for the web UI and extract joint sets on demand.
  python pipeline\dataset_tools.py index            -> data/test_split_index.json (needs data/scan/*.json: joint-set + body graph files of the test split)
  python pipeline\dataset_tools.py extract <joint_set> ...  -> copies/extracts joint JSON, body JSONs and OBJs into data/j1.0.0 and writes the step-2 face summaries
  python pipeline\dataset_tools.py fetch            -> prints download instructions / runs the scan extraction from the 7z archives
7-Zip path: AUTOLINK_7Z env var or C:\Program Files\7-Zip\7z.exe."""
import os, sys, json, shutil, subprocess, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import autolink_pipe as ap
SCAN = ap.ROOT / "data" / "scan"; ARCHIVE = ap.ROOT / "data" / "j1.0.0.7z"; PRE = ap.ROOT / "data" / "j1.0.0_preprocessed.7z"
SEVENZ = os.environ.get("AUTOLINK_7Z", r"C:\Program Files\7-Zip\7z.exe")
URLS = {"j1.0.0.7z": ("https://fusion-360-gallery-dataset.s3.us-west-2.amazonaws.com/assembly/j1.0.0/j1.0.0.7z", 2975602672),
        "j1.0.0_preprocessed.7z": ("https://fusion-360-gallery-dataset.s3.us-west-2.amazonaws.com/assembly/j1.0.0/j1.0.0_preprocessed.7z", 538969936)}

def sevenz(args):
    if not Path(SEVENZ).exists(): raise SystemExit(f"7-Zip not found at {SEVENZ}; install it or set AUTOLINK_7Z")
    r = subprocess.run([SEVENZ] + args, capture_output=True, text=True); 
    if r.returncode != 0: raise RuntimeError(r.stdout[-800:] + r.stderr[-800:])
    return r.stdout

def body_stats(b):
    p = SCAN / f"{b}.json"
    if not p.exists(): p = ap.DATA / f"{b}.json"
    if not p.exists(): return None
    g = json.loads(p.read_text(encoding="utf-8")); pr = g["properties"]; faces = [n for n in g["nodes"] if "surface_type" in n]
    axes, normals = set(), set()
    for n in faces:
        if "axis_x" in n and n["surface_type"] in ("CylinderSurfaceType", "ConeSurfaceType", "TorusSurfaceType"):
            d = np.array([n["axis_x"], n["axis_y"], n["axis_z"]]); o = np.array([n["origin_x"], n["origin_y"], n["origin_z"]])
            if np.linalg.norm(d) < 1e-9: continue
            d = d / np.linalg.norm(d); d = d * (1 if d[np.argmax(np.abs(d))] > 0 else -1); o = o - np.dot(o, d) * d; axes.add(tuple(np.round(np.concatenate([d, o]), 3)))
        if n["surface_type"] == "PlaneSurfaceType":
            nn = np.array([n["normal_x"], n["normal_y"], n["normal_z"]]); nn = nn * (1 if nn[np.argmax(np.abs(nn))] > 0 else -1); normals.add(tuple(np.round(nn, 3)))
    types = sorted({n["surface_type"].replace("SurfaceType", "") for n in faces})
    return {"faces": pr["face_count"], "types": types, "axisymmetric": len(axes) <= 1 and len(normals) <= 1, "n_axes": len(axes)}

def index():
    tt = json.loads((ap.DATA / "train_test.json").read_text(encoding="utf-8"))["test"]; rows = []
    for js in tt:
        p = SCAN / f"{js}.json"
        if not p.exists(): p = ap.DATA / f"{js}.json"
        if not p.exists(): rows.append({"joint_set": js, "available": False}); continue
        d = json.loads(p.read_text(encoding="utf-8")); s1, s2 = body_stats(d["body_one"]), body_stats(d["body_two"])
        rows.append({"joint_set": js, "available": True, "body_one": d["body_one"], "body_two": d["body_two"], "n_joints": len(d["joints"]), "joint_type": d["joints"][0]["joint_motion"]["joint_type"].replace("JointType", ""),
                     "faces": [s1["faces"] if s1 else None, s2["faces"] if s2 else None], "types": sorted(set((s1 or {}).get("types", [])) | set((s2 or {}).get("types", []))),
                     "axisymmetric_both": bool(s1 and s2 and s1["axisymmetric"] and s2["axisymmetric"]), "reconstructable_types": bool(s1 and s2 and set(s1["types"]) | set(s2["types"]) <= {"Plane", "Cylinder", "Cone", "Torus", "Sphere"})})
    (ap.ROOT / "data" / "test_split_index.json").write_text(json.dumps(rows), encoding="utf-8"); print("indexed", len(rows), "test joint sets;", sum(r["available"] for r in rows), "with graph files")

def extract(js):
    """Make data/j1.0.0 contain <js>.json, both body .json and .obj; write step-2 face summaries."""
    src = SCAN / f"{js}.json"
    if not (ap.DATA / f"{js}.json").exists():
        if src.exists(): shutil.copy(src, ap.DATA / f"{js}.json")
        else: sevenz(["e", str(ARCHIVE), f"-o{ap.DATA}", "-y", f"j1.0.0\\joint\\{js}.json"])
    d = ap.joint_set_doc(js); need = []
    for b in (d["body_one"], d["body_two"]):
        if not (ap.DATA / f"{b}.json").exists():
            if (SCAN / f"{b}.json").exists(): shutil.copy(SCAN / f"{b}.json", ap.DATA / f"{b}.json")
            else: need.append(f"j1.0.0\\joint\\{b}.json")
        if not (ap.DATA / f"{b}.obj").exists(): need.append(f"j1.0.0\\joint\\{b}.obj")
    if need:
        lst = ap.ROOT / "data" / "_extract_list.txt"; lst.write_text("\n".join(need)); sevenz(["e", str(ARCHIVE), f"-o{ap.DATA}", "-y", f"@{lst}"]); lst.unlink()
    out = ap.DEMO / js / "step2_reconstruct_cadquery" / "input"; out.mkdir(parents=True, exist_ok=True)
    for k, b in ((1, d["body_one"]), (2, d["body_two"])): (out / f"part_{k}_face_summary.txt").write_text(ap.face_summary_text(b), encoding="utf-8")
    return {"joint_set": js, "body_one": d["body_one"], "body_two": d["body_two"], "extracted": True}

def fetch():
    print("Download (manually or with curl) into", ap.ROOT / "data")
    for name, (url, size) in URLS.items():
        p = ap.ROOT / "data" / name; st = f"present, {p.stat().st_size:,} bytes" if p.exists() else "missing"
        print(f"  {name}: {url}  (expected {size:,} bytes) -> {st}")
        if p.exists() and abs(p.stat().st_size - size) / size > 0.05: print("   WARNING: size differs by >5%, do not extract")
    if PRE.exists() and not (ap.DATA / "train_test.json").exists():
        ap.DATA.mkdir(parents=True, exist_ok=True); sevenz(["e", str(PRE), f"-o{ap.DATA}", "-y", "train_test.json"]); print("  extracted train_test.json")
    if ARCHIVE.exists() and (ap.DATA / "train_test.json").exists() and not SCAN.exists():
        tt = json.loads((ap.DATA / "train_test.json").read_text(encoding="utf-8"))["test"]; SCAN.mkdir(parents=True)
        lst = ap.ROOT / "data" / "_scan_list.txt"; lst.write_text("\n".join(f"j1.0.0\\joint\\{js}.json" for js in tt)); sevenz(["e", str(ARCHIVE), f"-o{SCAN}", "-y", f"@{lst}"])
        bodies = sorted({b for js in tt for b in (lambda d: (d["body_one"], d["body_two"]))(json.loads((SCAN / f"{js}.json").read_text(encoding="utf-8")))})
        lst.write_text("\n".join(f"j1.0.0\\joint\\{b}.json" for b in bodies)); sevenz(["e", str(ARCHIVE), f"-o{SCAN}", "-y", f"@{lst}"]); lst.unlink(); print("  extracted test-split graph files to data/scan (", len(tt), "joint sets,", len(bodies), "bodies )")
    index()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    if cmd == "index": index()
    elif cmd == "extract":
        for js in sys.argv[2:]: print(extract(js))
    else: fetch()
