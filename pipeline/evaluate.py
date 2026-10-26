"""Build pipeline_demo/EVALUATION.{json,md} from whatever step folders exist.  conda run -n autolink-cad python pipeline\evaluate.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import autolink_pipe as ap
ATT = ap.jload(ap.ROOT / "recon" / "ATTEMPTS.json") if (ap.ROOT / "recon" / "ATTEMPTS.json").exists() else {}
def attempts(js):
    for grp in ("easy_set", "hard_set"):
        if js in ATT.get(grp, {}): return grp, ATT[grp][js]
    return "?", {}
def flat(e, nf): return e["index"] + (nf if e["type"] == "BRepEdge" else 0)
rows = []
for d in sorted(ap.DEMO.glob("joint_set_*")):
    js = d.name; doc = ap.joint_set_doc(js); pred = ap.jload(d / "step1_joinable_predict/output/prediction_top10.json")
    _, f1, _ = ap.ds_rows(doc["body_one"]); _, f2, _ = ap.ds_rows(doc["body_two"]); n1, n2 = len(f1), len(f2)
    gt = set()
    for j in doc["joints"]:
        a = [flat(j["geometry_or_origin_one"]["entity_one"], n1)] + [flat(e, n1) for e in j["geometry_or_origin_one"].get("entity_one_equivalents", [])]
        b = [flat(j["geometry_or_origin_two"]["entity_one"], n2)] + [flat(e, n2) for e in j["geometry_or_origin_two"].get("entity_one_equivalents", [])]
        gt |= {(x, y) for x, y in __import__("itertools").product(a, b)}
    ranks = [c["rank"] for c in pred["candidates"] if (c["body_one"]["index"], c["body_two"]["index"]) in gt]; total = pred["body_one_nodes"] * pred["body_two_nodes"]
    grp, att = attempts(js)
    row = {"joint_set": js, "set": grp.replace("_set", ""), "faces": [n1, n2], "surface_types": sorted({f["type"].lower() for f in f1 + f2}),
           "step1_first_hit_rank": ranks[0] if ranks else None, "step1_gt_pairs_fraction": round(len(gt) / total, 3), "step2_attempts": {k: v for k, v in att.items() if k != "notes"}, "step2_notes": att.get("notes", "")}
    v = d / "step3_verify_rebuild/output"
    if (v / "verify_part_1.json").exists():
        v1 = ap.jload(v / "verify_part_1.json"); v2 = ap.jload(v / "verify_part_2.json") if (v / "verify_part_2.json").exists() else {"PASS": False}
        row["step3_pass"] = [v1["PASS"], v2["PASS"]]
    else: row["step3_pass"] = None
    c4 = d / "step4_classify_joint/output/joint_classification.json"
    if c4.exists():
        cls = ap.jload(c4); row["step4_rule"] = cls["rule"]["name"] if cls["rule"] else None; row["step4_edge_promotion"] = bool(cls.get("edge_promotion"))
    p5 = d / "step5_place_parts/output/chosen_pose.json"
    if p5.exists():
        pose = ap.jload(p5); cands = ap.jload(d / "step5_place_parts/output/pose_candidates_scored.json"); best = next(c for c in cands["candidates"] if c["option"] == cands["chosen_option"]); e = pose["comparison_to_designer_ground_truth"]
        row.update({"step5_candidates": len(cands["candidates"]), "step5_chosen_contact": round(best["contact_fraction"], 3), "step5_axis_angle_err_deg": round(e.get("axis_angle_error_deg", -1), 2),
                    "step5_axial_offset_vs_designer_cm": round(e.get("axial_offset_cm", -1), 3), "step5_radial_err_cm": round(e.get("radial_offset_cm", -1), 4), "step5_underdetermined": pose.get("underdetermined", False)})
    r6 = d / "step6_infer_relations/output/relations.json"
    if r6.exists(): row["step6_relations"] = [r["equation"] for r in ap.jload(r6)["relations"] if "dependent" in r]
    p7 = d / "step7_propagate_edit/output/propagation.json"
    if p7.exists():
        prop = ap.jload(p7); row.update({"step7_edit": prop["edit"]["changes"], "step7_overlap_after_edit": round(prop["re_solved_pose"]["overlap_fraction"], 3), "step7_contact_after_edit": round(prop["re_solved_pose"]["contact_fraction"], 3)})
    rows.append(row)

def summarize(rs):
    n = len(rs); parts_attempted = sum(1 for r in rs for k in ("part_1", "part_2") if isinstance(r["step2_attempts"].get(k), int) or str(r["step2_attempts"].get(k, "")).startswith("FAIL"))
    parts_pass = sum(sum(r["step3_pass"]) for r in rs if r["step3_pass"]); first_try = sum(1 for r in rs for k in ("part_1", "part_2") if r["step2_attempts"].get(k) == 1)
    placed = [r for r in rs if "step5_axis_angle_err_deg" in r]
    return {"n_joint_sets": n, "step1_top1_hit": sum(1 for r in rs if r["step1_first_hit_rank"] == 1), "step1_top10_hit": sum(1 for r in rs if r["step1_first_hit_rank"]),
            "step1_mean_gt_pairs_fraction": round(sum(r["step1_gt_pairs_fraction"] for r in rs) / n, 3),
            "step2_parts_attempted": parts_attempted, "step2_parts_not_attempted": 2 * n - parts_attempted, "step3_parts_pass": parts_pass, "step2_parts_pass_first_try": first_try,
            "step5_joint_sets_placed": len(placed), "step5_axis_correct": sum(1 for r in placed if 0 <= r["step5_axis_angle_err_deg"] < 1), "step5_axial_matches_designer": sum(1 for r in placed if 0 <= r["step5_axial_offset_vs_designer_cm"] < 0.05),
            "step6_relations_total": sum(len(r.get("step6_relations", [])) for r in rs), "step7_edits_zero_overlap": sum(1 for r in rs if r.get("step7_overlap_after_edit", 1) < 0.01), "step7_edits_run": sum(1 for r in rs if "step7_overlap_after_edit" in r)}
easy = [r for r in rows if r["set"] == "easy"]; hard = [r for r in rows if r["set"] == "hard"]
out = {"model_for_step2": ATT.get("model"), "verifier_fixes": ATT.get("verifier_fixes_during_hard_set", []), "easy_set": summarize(easy), "hard_set": summarize(hard), "per_joint_set": rows}
(ap.DEMO / "EVALUATION.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
def table(rs):
    L = ["| joint set | faces | types | JoinABLe hit rank | GT-ok pairs | step2 attempts | step3 | rule | cands | contact | axis err | axial vs designer | relations | +30% edit overlap |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        a = r["step2_attempts"]; s3 = "PASS" if r["step3_pass"] and all(r["step3_pass"]) else ("FAIL" if r["step3_pass"] else "-")
        cells = [r["joint_set"], f"{r['faces'][0]}+{r['faces'][1]}", ", ".join(r["surface_types"]), str(r["step1_first_hit_rank"] or ">10"), f"{r['step1_gt_pairs_fraction']*100:.0f}%", f"{a.get('part_1','-')} / {a.get('part_2','-')}", s3,
                 f"{r.get('step4_rule') or '-'}{' (edge->face)' if r.get('step4_edge_promotion') else ''}"]
        if "step5_chosen_contact" in r:
            cells += [str(r["step5_candidates"]), f"{r['step5_chosen_contact']*100:.0f}%", f"{r['step5_axis_angle_err_deg']} deg", f"{r['step5_axial_offset_vs_designer_cm']} cm", "<br>".join(r.get("step6_relations", [])) or "(pose only)", f"{r.get('step7_overlap_after_edit', 0)*100:.0f}%"]
        else: cells += ["-", "-", "-", "-", "-", "-"]
        L.append("| " + " | ".join(cells) + " |")
    return L
E, H = out["easy_set"], out["hard_set"]
md = ["# AutoLink pipeline evaluation (Fusion 360 Gallery test split)", "", f"Step-2 model: {out['model_for_step2']}", "",
      "## Easy set: the first 10 test joint sets that fit on disk (all axisymmetric parts)", "",
      f"- JoinABLe top-1 hit {E['step1_top1_hit']}/{E['n_joint_sets']}, but on these parts {E['step1_mean_gt_pairs_fraction']*100:.0f}% of all face pairs count as correct (every face shares the axis), so this says little.",
      f"- Reconstruction: {E['step3_parts_pass']}/{2*E['n_joint_sets']} parts pass step 3, {E['step2_parts_pass_first_try']} on the first script.",
      f"- Placement: axis correct {E['step5_axis_correct']}/{E['step5_joint_sets_placed']}; axial position equals the designer's in {E['step5_axial_matches_designer']}/{E['step5_joint_sets_placed']} (the rest admit several stop positions).",
      f"- {E['step6_relations_total']} parametric relations; {E['step7_edits_zero_overlap']}/{E['step7_edits_run']} example edits rebuild without interference.", "", *table(easy), "",
      "## Hard set: 10 joint sets chosen for non-axisymmetric geometry (hole patterns, brackets, levers, 4-26 faces per part)", "",
      f"- JoinABLe top-1 hit {H['step1_top1_hit']}/{H['n_joint_sets']} (top-10: {H['step1_top10_hit']}/{H['n_joint_sets']}); here only {H['step1_mean_gt_pairs_fraction']*100:.0f}% of face pairs are acceptable, so the hits are meaningful.",
      f"- Reconstruction: {H['step2_parts_attempted']}/{2*H['n_joint_sets']} parts attempted, {H['step3_parts_pass']} pass step 3, {H['step2_parts_pass_first_try']} on the first script; {H['step2_parts_not_attempted']} not attempted (effort budget); 1 failed after 3 attempts (08709 part 2).",
      f"- Placement: axis correct {H['step5_axis_correct']}/{H['step5_joint_sets_placed']} placed; axial position equals the designer's in {H['step5_axial_matches_designer']}/{H['step5_joint_sets_placed']}.",
      f"- {H['step6_relations_total']} parametric relations; {H['step7_edits_zero_overlap']}/{H['step7_edits_run']} blind +30% example edits rebuild without interference (an automatic +30% on a radius can legitimately create interference; the pipeline reports it rather than hiding it).", "", *table(hard), "",
      "## Verifier changes made while running the hard set", *[f"- {x}" for x in out["verifier_fixes"]], "",
      "Dataset: Fusion 360 Gallery Assembly dataset (non-commercial research licence). Per-step files: `pipeline_demo/<joint_set>/stepN_*/`. Attempt log: `recon/ATTEMPTS.json`."]
(ap.DEMO / "EVALUATION.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(l for l in md if l.startswith("- ") or l.startswith("## ")))
