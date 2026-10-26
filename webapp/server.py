"""
AutoLink demo server. Python 3.11 `autolink-cad` env, stdlib only.
  conda run -n autolink-cad python webapp\server.py   ->  http://127.0.0.1:8777
Serves webapp/index.html, the dataset meshes, the pipeline_demo step files, and does live CadQuery rebuilds.
Local-only (binds 127.0.0.1), no authentication: do not expose on a network.
"""
import os, json, sys, traceback, threading, subprocess, time, importlib
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "pipeline")); import autolink_pipe as ap; import pipeline_steps, dataset_tools, llm_reconstruct
CONDA = r"C:\Users\domlimco\AppData\Local\miniconda3\Scripts\conda.exe"

_cache = {}; _lock = threading.Lock()

def joint_sets():
    out = []
    for p in sorted(ap.DATA.glob("joint_set_*.json")):
        js = p.stem; d = ap.joint_set_doc(js); demo = ap.DEMO / js
        p1, _, _ = ap.ds_rows(d["body_one"]); p2, _, _ = ap.ds_rows(d["body_two"])
        out.append({"joint_set": js, "body_one": d["body_one"], "body_two": d["body_two"], "faces": [p1["face_count"], p2["face_count"]],
                    "surface_types": [[t["surface_type"].replace("SurfaceType", "") for t in p1["surface_types"]], [t["surface_type"].replace("SurfaceType", "") for t in p2["surface_types"]]],
                    "has_prediction": (demo / "step1_joinable_predict/output/prediction_top10.json").exists(),
                    "has_reconstruction": (demo / "step7_propagate_edit/output/propagation.json").exists(),
                    "has_part_scripts": (ROOT / "recon" / f"recon_{js.split(chr(95))[-1]}" / "part_1.py").exists(),
                    "reconstruction_requested": (demo / "step2_reconstruct_cadquery" / "REQUEST.json").exists()})
    return out

def read_step_files(js):
    D = ap.DEMO / js; res = {}
    for d in sorted(D.glob("step*")):
        s = {"readme": (d / "README.md").read_text(encoding="utf-8") if (d / "README.md").exists() else "", "input": {}, "output": {}}
        for sub in ("input", "output"):
            for f in sorted((d / sub).glob("*")):
                if f.suffix == ".json" and "mesh" not in f.name and f.stat().st_size < 400_000: s[sub][f.name] = json.loads(f.read_text(encoding="utf-8"))
                elif f.suffix in (".txt", ".py", ".md"): s[sub][f.name] = f.read_text(encoding="utf-8")
                else: s[sub][f.name] = f"<binary {f.stat().st_size} bytes>"
        res[d.name] = s
    return res

def context(js):
    """Everything needed for live rebuilds, cached per joint set."""
    with _lock:
        if js in _cache: return _cache[js]
    parts = ap.load_parts(js); d = ap.joint_set_doc(js); bodies = {1: d["body_one"], 2: d["body_two"]}
    pred = ap.jload(ap.DEMO / js / "step1_joinable_predict/output/prediction_top10.json")
    S, T, DS, ADJ, CQR = {}, {}, {}, {}, {}
    for k in (1, 2):
        s = parts[k].build(**parts[k].PARAMS).val(); S[k] = s; CQR[k] = ap.cq_rows(s); _, T[k], DS[k], ADJ[k] = ap.verify(s, bodies[k], CQR[k])
    cls = ap.classify(pred, DS[1], DS[2], bodies); po, cands, best = ap.place(S[1], S[2], T[1], T[2], cls, DS[1], DS[2], ADJ[1], ADJ[2], with_scores=False)
    rels = ap.jload(ap.DEMO / js / "step6_infer_relations/output/relations.json")["relations"]
    ctx = {"parts": parts, "bodies": bodies, "T": T, "DS": DS, "ADJ": ADJ, "cls": cls, "option": best["option"], "relations": rels}
    with _lock: _cache[js] = ctx
    return ctx

def rebuild(js, p2_changes, p1_overrides=None):
    c = context(js); parts = c["parts"]
    p2 = dict(parts[2].PARAMS); p2.update(p2_changes or {})
    p1, log = ap.propagate(c["relations"], parts[1].PARAMS, p2)
    if p1_overrides: p1.update(p1_overrides)
    s1, s2 = parts[1].build(**p1).val(), parts[2].build(**p2).val()
    # re-derive side tables on the rebuilt solids by face ORDER (CadQuery keeps face order for the same script)
    asm, loc, T1, txt = ap.assemble(s1, s2, c["T"][1], c["T"][2], c["cls"], c["option"]); ov, ct = ap.score_pose(s1, s2, loc, n=3000)
    return {"part1_params": p1, "part2_params": p2, "propagated": log, "constraints": txt, "part1_transform_4x4": T1.tolist(), "overlap_fraction": ov, "contact_fraction": ct,
            "mesh1": ap.tessellate(s1, c["T"][1]), "mesh2": ap.tessellate(s2, c["T"][2])}

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(HERE), **k)
    def log_message(self, *a): pass
    def _json(self, obj, code=200):
        b = json.dumps(obj, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else str(o)).encode(); self.send_response(code)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        try:
            if u.path == "/api/joint_sets": return self._json(joint_sets())
            if u.path == "/api/test_split":   # every test-split joint set (index built by pipeline/dataset_tools.py index)
                p = ROOT / "data" / "test_split_index.json"; rows = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
                have = {d.name for d in ap.DATA.glob("joint_set_*.json")}; have = {Path(x).stem for x in have}; recon = {d.name.replace("recon_", "joint_set_") for d in (ROOT / "recon").glob("recon_*")}
                for r in rows: r["extracted"] = r["joint_set"] in have; r["has_part_scripts"] = r["joint_set"] in recon
                return self._json({"rows": rows, "llm_provider": os.environ.get("AUTOLINK_LLM_PROVIDER", ""), "llm_model": os.environ.get("AUTOLINK_LLM_MODEL", "")})
            if u.path == "/api/mesh": return self._json(ap.obj_mesh(q["body"][0]))
            if u.path == "/api/joint_set":
                js = q["id"][0]; d = ap.joint_set_doc(js); G1, G2 = ap.gt_transforms(js)
                f1 = ap.ds_rows(d["body_one"]); f2 = ap.ds_rows(d["body_two"])
                return self._json({"joint_set": js, "body_one": d["body_one"], "body_two": d["body_two"], "faces1": f1[1], "faces2": f2[1], "props1": f1[0], "props2": f2[0],
                                   "gt_transform_one": G1.tolist(), "gt_transform_two": G2.tolist(), "gt_entities": [[j["geometry_or_origin_one"]["entity_one"]["type"], j["geometry_or_origin_one"]["entity_one"]["index"], j["geometry_or_origin_two"]["entity_one"]["type"], j["geometry_or_origin_two"]["entity_one"]["index"]] for j in d["joints"]]})
            if u.path == "/api/steps": return self._json(read_step_files(q["id"][0]))
            if u.path == "/api/rebuilt_mesh":
                js, k = q["id"][0], int(q["part"][0]); p = ap.DEMO / js / f"step3_verify_rebuild/output/part_{k}_rebuilt_mesh.json"
                return self._json(json.loads(p.read_text()))
            return super().do_GET()
        except Exception as e:
            return self._json({"error": str(e), "trace": traceback.format_exc()}, 500)
    def do_POST(self):
        u = urlparse(self.path); n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n) or b"{}")
        try:
            if u.path == "/api/rebuild": return self._json(rebuild(body["joint_set"], body.get("part2_params", {}), body.get("part1_overrides")))
            if u.path == "/api/run_step1":   # live JoinABLe inference in the Python 3.7 env (subprocess)
                t0 = time.time(); js = body["joint_set"]
                r = subprocess.run([CONDA, "run", "-n", "autolink", "--cwd", str(ROOT), "python", "pipeline/joinable_predict_fast.py", js], capture_output=True, text=True, timeout=600)
                if r.returncode != 0: return self._json({"error": "JoinABLe run failed", "trace": (r.stdout + r.stderr)[-3000:]}, 500)
                with _lock: _cache.pop(js, None)
                return self._json({"seconds": round(time.time() - t0, 1), "log": r.stdout[-2000:], "prediction": ap.jload(ap.DEMO / js / "step1_joinable_predict/output/prediction_top10.json")})
            if u.path == "/api/run_steps":   # live steps 3-6 (+ example step 7) in this process
                t0 = time.time(); js = body["joint_set"]; importlib.reload(pipeline_steps)
                if not ap.load_parts(js): return self._json({"error": f"no CadQuery reconstruction (recon/recon_{js.split(chr(95))[-1]}/part_1.py) for {js}"}, 400)
                pipeline_steps.run(js)
                with _lock: _cache.pop(js, None)
                return self._json({"seconds": round(time.time() - t0, 1), "steps": read_step_files(js)})
            if u.path == "/api/extract":   # pull one test-split joint set out of the archive (joint JSON, body JSONs, OBJs) + face summaries
                t0 = time.time(); r = dataset_tools.extract(body["joint_set"]); r["seconds"] = round(time.time() - t0, 1); return self._json(r)
            if u.path == "/api/run_step2":   # LLM reconstruction with the step-3 retry loop; provider from AUTOLINK_LLM_PROVIDER (anthropic|openai|bedrock|mock)
                js = body["joint_set"]; prov = body.get("provider") or os.environ.get("AUTOLINK_LLM_PROVIDER", "")
                if not prov or prov == "agent": return self._json({"error": "No LLM provider configured. Set AUTOLINK_LLM_PROVIDER=anthropic|openai|bedrock and the matching API key env var, then restart the server. (Or use 'Request reconstruction from the agent'.)"}, 400)
                t0 = time.time(); res = {}
                for k in (1, 2):
                    ok, log = llm_reconstruct.reconstruct_part(js, k, prov, int(body.get("max_attempts", 3))); res[f"part_{k}"] = {"success": ok, "attempts": len(log), "log": [{kk: vv for kk, vv in a.items() if kk != "report"} for a in log]}
                with _lock: _cache.pop(js, None)
                return self._json({"seconds": round(time.time() - t0, 1), "provider": prov, "results": res, "steps": read_step_files(js)})
            if u.path == "/api/request_reconstruction":   # hand-off to the agent: write a request file it can pick up
                js = body["joint_set"]; p = ap.DEMO / js / "step2_reconstruct_cadquery" / "REQUEST.json"
                ap.jdump(p, {"joint_set": js, "requested_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "deliver_to": f"recon/recon_{js.split(chr(95))[-1]}/part_1.py and part_2.py", "status": "waiting_for_agent"})
                return self._json({"ok": True, "request": str(p)})
            return self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            return self._json({"error": str(e), "trace": traceback.format_exc()}, 500)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    print(f"AutoLink demo: http://127.0.0.1:{port}  (local only, no auth)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()

