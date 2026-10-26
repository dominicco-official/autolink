"""
Step 2 - LLM reconstruction of a dataset part as a parametric CadQuery script, verified by step 3.

    conda run -n autolink-cad python pipeline\llm_reconstruct.py joint_set_04039 [more ids] [--max-attempts 3] [--provider anthropic|openai|bedrock|mock|agent]

Provider is chosen with AUTOLINK_LLM_PROVIDER (or --provider). Credentials come ONLY from environment variables:
  anthropic : ANTHROPIC_API_KEY            model: AUTOLINK_LLM_MODEL (default claude-sonnet-4-5)
  openai    : OPENAI_API_KEY               model: AUTOLINK_LLM_MODEL (default gpt-4o)
  bedrock   : AWS credentials via boto3    model: AUTOLINK_LLM_MODEL (default anthropic.claude-3-5-sonnet-20241022-v2:0), AWS_REGION
  mock      : no network; returns the script already in recon/ (for testing the loop) or a deliberately wrong one with --mock-fail-first
  agent     : no network; writes recon/recon_<id>/REQUEST_part_N.md and waits for a human/agent to write part_N.py

Loop per part:  prompt(face summary [+ previous script + verifier report]) -> script -> build -> step-3 checks
                -> PASS: save part_N.py ; FAIL: retry with the report, up to --max-attempts.
Every attempt (prompt, raw reply, extracted script, verifier report) is saved to recon/recon_<id>/attempts/.
"""
import os, re, sys, json, time, argparse, importlib.util, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import autolink_pipe as ap

SYSTEM = """You are a mechanical CAD engineer who writes CadQuery 2.x (Python) scripts.
You will receive a complete description of ONE solid part from a B-Rep: every face (type, area, centroid, normal/axis/radius),
every edge (type, length, radius, center) and which faces each edge borders. Units are centimetres. The part may sit anywhere in space;
reproduce it in the SAME position (same bounding box).
Write a Python module that defines:
  PARAMS = {...}            # dict of named design parameters (floats) that reproduce the part exactly; use meaningful names
  def build(**params):      # returns a cq.Workplane with exactly one solid, built ONLY from the parameters (no magic numbers except derived geometry)
Rules: import only math and cadquery as cq. Derive dependent sizes (e.g. outer = bore + wall) inside build(). Prefer revolve for axisymmetric parts,
box/extrude/cut for prismatic parts, .fillet()/.chamfer() for torus/cone transitions. Return ONLY one ```python code block, no prose."""

def _summary(js, k):
    p = ap.DEMO / js / "step2_reconstruct_cadquery" / "input" / f"part_{k}_face_summary.txt"
    if not p.exists():
        d = ap.joint_set_doc(js); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(ap.face_summary_text(d["body_one" if k == 1 else "body_two"]), encoding="utf-8")
    return p.read_text(encoding="utf-8")

def _extract_code(reply):
    m = re.findall(r"```(?:python)?\s*(.*?)```", reply, re.S); return (m[-1] if m else reply).strip() + "\n"

def _verify_script(code, body, workdir, tag):
    """Exec the candidate script in isolation, build, run step-3 checks. Returns (ok, report_text, report_dict)."""
    p = workdir / f"{tag}.py"; p.write_text(code, encoding="utf-8")
    try:
        spec = importlib.util.spec_from_file_location(tag, p); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        solid = mod.build(**mod.PARAMS).val()
    except Exception as e:
        return False, f"BUILD ERROR: {type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}", {"build_error": str(e)}
    try:
        rep, table, dsr, adj = ap.verify(solid, body)
    except Exception as e:
        return False, f"VERIFY ERROR: {type(e).__name__}: {e}", {"verify_error": str(e)}
    lines = [f"{'PASS' if c['pass'] else 'FAIL'}: {c['check']} -> " + ", ".join(f"{k}={v:.6g}" if isinstance(v, float) else f"{k}={v}" for k, v in c.items() if k not in ('check', 'pass')) for c in rep["checks"]]
    if not rep["PASS"]:
        cqr = ap.cq_rows(solid)
        lines.append("Unmatched dataset faces (type, radius, centroid):")
        for f in rep["face_matching"]:
            if not f["MATCH"]: lines.append(f"  dataset face {f['dataset_face']} {f['type']} r={f['radius']} centroid={[round(x,4) for x in dsr[f['dataset_face']]['centroid']]}")
        lines.append("Faces your script produced (type, radius, centroid, area):")
        for r in cqr: lines.append(f"  cq face {r['cq_face']} {r['type']} r={round(r.get('radius', 0), 5)} centroid={[round(x,4) for x in r['centroid']]} area={r['area']:.5g}")
    return rep["PASS"], "\n".join(lines), rep

# ---------------- providers ----------------
def _call_anthropic(messages):
    import anthropic; client = anthropic.Anthropic()
    r = client.messages.create(model=os.environ.get("AUTOLINK_LLM_MODEL", "claude-sonnet-4-5"), max_tokens=4000, system=SYSTEM, messages=messages)
    return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
def _call_openai(messages):
    from openai import OpenAI; client = OpenAI()
    r = client.chat.completions.create(model=os.environ.get("AUTOLINK_LLM_MODEL", "gpt-4o"), messages=[{"role": "system", "content": SYSTEM}] + messages, temperature=0.2)
    return r.choices[0].message.content
def _call_bedrock(messages):
    import boto3; rt = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    r = rt.converse(modelId=os.environ.get("AUTOLINK_LLM_MODEL", "anthropic.claude-3-5-sonnet-20241022-v2:0"), system=[{"text": SYSTEM}],
                    messages=[{"role": m["role"], "content": [{"text": m["content"]}]} for m in messages], inferenceConfig={"maxTokens": 4000, "temperature": 0.2})
    return "".join(c.get("text", "") for c in r["output"]["message"]["content"])
class Mock:
    """Returns the script already in recon/ (so the loop can be exercised offline). With fail_first, the first reply is a wrong box."""
    def __init__(self, js, k, fail_first=False): self.p = ap.ROOT / "recon" / f"recon_{js.split('_')[-1]}" / f"part_{k}.py"; self.n = 0; self.fail_first = fail_first
    def __call__(self, messages):
        self.n += 1
        if self.fail_first and self.n == 1: return "```python\nimport cadquery as cq\nPARAMS = {'size': 1.0}\ndef build(size):\n    return cq.Workplane('XY').box(size, size, size)\n```"
        return "```python\n" + self.p.read_text(encoding="utf-8") + "\n```"
class Agent:
    """No API: write a request file and block until the agent/human writes the script."""
    def __init__(self, js, k): self.dir = ap.ROOT / "recon" / f"recon_{js.split('_')[-1]}"; self.k = k
    def __call__(self, messages):
        self.dir.mkdir(parents=True, exist_ok=True); req = self.dir / f"REQUEST_part_{self.k}.md"; target = self.dir / f"part_{self.k}.py"
        req.write_text("# Reconstruction request (agent mode)\nWrite `" + target.name + "` (PARAMS + build) that passes pipeline/verify_recon.py.\n\n" + messages[-1]["content"], encoding="utf-8")
        print(f"   [agent] waiting for {target} ... (request in {req.name})", flush=True); t0 = os.path.getmtime(target) if target.exists() else 0
        while not target.exists() or os.path.getmtime(target) <= t0: time.sleep(2)
        req.unlink(missing_ok=True); return "```python\n" + target.read_text(encoding="utf-8") + "\n```"

def make_provider(name, js, k, mock_fail_first=False):
    return {"anthropic": _call_anthropic, "openai": _call_openai, "bedrock": _call_bedrock}.get(name) or (Mock(js, k, mock_fail_first) if name == "mock" else Agent(js, k) if name == "agent" else None)

# ---------------- loop ----------------
def reconstruct_part(js, k, provider_name, max_attempts=3, mock_fail_first=False):
    d = ap.joint_set_doc(js); body = d["body_one" if k == 1 else "body_two"]; out = ap.ROOT / "recon" / f"recon_{js.split('_')[-1]}"; att = out / "attempts"; att.mkdir(parents=True, exist_ok=True)
    call = make_provider(provider_name, js, k, mock_fail_first); assert call, f"unknown provider {provider_name}"
    messages = [{"role": "user", "content": f"Reconstruct this part.\n\n{_summary(js, k)}"}]; log = []
    for n in range(1, max_attempts + 1):
        t0 = time.time(); reply = call(messages); code = _extract_code(reply)
        ok, report, rep = _verify_script(code, body, att, f"part_{k}_attempt{n}")
        log.append({"attempt": n, "provider": provider_name, "model": os.environ.get("AUTOLINK_LLM_MODEL"), "seconds": round(time.time() - t0, 1), "pass": ok, "report": report})
        (att / f"part_{k}_attempt{n}.prompt.txt").write_text(json.dumps(messages, indent=2), encoding="utf-8"); (att / f"part_{k}_attempt{n}.reply.txt").write_text(reply, encoding="utf-8"); (att / f"part_{k}_attempt{n}.report.txt").write_text(report, encoding="utf-8")
        print(f"  {js} part {k} attempt {n}: {'PASS' if ok else 'FAIL'}", flush=True)
        if ok:
            (out / f"part_{k}.py").write_text(code, encoding="utf-8"); break
        messages += [{"role": "assistant", "content": reply}, {"role": "user", "content": "The script did not reproduce the part. Verifier report:\n\n" + report + "\n\nFix the script. Return ONLY one ```python block."}]
    (out / f"part_{k}_attempts.json").write_text(json.dumps({"joint_set": js, "part": k, "body": body, "provider": provider_name, "attempts": log, "success": any(a["pass"] for a in log)}, indent=2), encoding="utf-8")
    return any(a["pass"] for a in log), log

def main():
    a = argparse.ArgumentParser(); a.add_argument("joint_sets", nargs="+"); a.add_argument("--provider", default=os.environ.get("AUTOLINK_LLM_PROVIDER", "")); a.add_argument("--max-attempts", type=int, default=3)
    a.add_argument("--parts", default="1,2"); a.add_argument("--mock-fail-first", action="store_true"); args = a.parse_args()
    if not args.provider: sys.exit("Set AUTOLINK_LLM_PROVIDER (anthropic|openai|bedrock|mock|agent) or pass --provider. Credentials: ANTHROPIC_API_KEY / OPENAI_API_KEY / AWS credentials.")
    results = {}
    for js in args.joint_sets:
        for k in [int(x) for x in args.parts.split(",")]:
            ok, log = reconstruct_part(js, k, args.provider, args.max_attempts, args.mock_fail_first); results[f"{js}/part_{k}"] = {"success": ok, "attempts": len(log)}
    print(json.dumps(results, indent=2))

if __name__ == "__main__": main()
