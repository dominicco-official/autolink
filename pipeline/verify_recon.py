"""Step-3 verifier: python pipeline\verify_recon.py joint_set_XXXXX  -> per-part checks and face mismatches."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import autolink_pipe as ap
for js in sys.argv[1:]:
    parts = ap.load_parts(js); d = ap.joint_set_doc(js)
    for k, b in ((1, d["body_one"]), (2, d["body_two"])):
        try: s = parts[k].build(**parts[k].PARAMS).val()
        except Exception as e: print(f"{js} part {k}: BUILD ERROR {e}"); continue
        rep, table, dsr, adj = ap.verify(s, b)
        print(f"{js} part {k}: {'PASS' if rep['PASS'] else 'FAIL'}  " + "; ".join(f"{c['check'].split(' ')[0]}={'ok' if c['pass'] else 'X'}" for c in rep["checks"]))
        if not rep["PASS"]:
            for c in rep["checks"]:
                if not c["pass"]: print("    ", {k2: v for k2, v in c.items() if k2 != "check"}, c["check"])
            for f in rep["face_matching"]:
                if not f["MATCH"]: print(f"     unmatched dataset face {f['dataset_face']} {f['type']} r={f['radius']} ; cq faces:", [(r['cq_face'], r['type'], round(r.get('radius', 0), 4), [round(x, 3) for x in r['centroid']]) for r in ap.cq_rows(s) if r['type'] == f['type']][:6])
