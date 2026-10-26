"""Write pipeline steps 2-7 into pipeline_demo/<joint_set>/stepN_*/ for any joint set that has recon/recon_<id>/part_{1,2}.py.
Usage: conda run -n autolink-cad python pipeline\pipeline_steps.py joint_set_04039 [joint_set_11051 ...]"""
import sys, shutil, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import autolink_pipe as ap

def run(js):
    D = ap.DEMO / js; parts = ap.load_parts(js)
    pred = ap.jload(D / "step1_joinable_predict/output/prediction_top10.json"); doc = ap.joint_set_doc(js); bodies = {1: doc["body_one"], 2: doc["body_two"]}
    def step(n, name):
        d = D / f"step{n}_{name}"; (d / "input").mkdir(parents=True, exist_ok=True); (d / "output").mkdir(exist_ok=True); return d
    # step 1 extras
    s1 = step(1, "joinable_predict")
    # dataset files are referenced, not copied (dataset license forbids redistribution)
    ap.jdump(s1 / "input" / f"{js}__body_ids_only.json", {"body_one": doc["body_one"], "body_two": doc["body_two"], "note": "JoinABLe inference only needs the two body ids; the designer's joints are NOT read here."})
    t = pred["candidates"][0]
    (s1 / "README.md").write_text(f"# Step 1 - JoinABLe predicts which faces mate\nTool: pretrained JoinABLe GNN (Python 3.7 env). The only neural network in the pipeline.\n\nInput: `input/<body>.json` x2 (B-Rep graph files; the network never reads the mesh) and the two body ids.\nOutput: `output/prediction_top10.json` ranked candidate pairs with probability and derived axis.\n\nTop-1: part1 {t['body_one']['entity']}[{t['body_one']['index']}] ({t['body_one']['geometry']}) <-> part2 {t['body_two']['entity']}[{t['body_two']['index']}] ({t['body_two']['geometry']}), p={t['probability']:.3f}\n", encoding="utf-8")
    s2 = step(2, "reconstruct_cadquery")
    for k, b in bodies.items(): (s2 / "input" / f"part_{k}_face_summary.txt").write_text(ap.face_summary_text(b), encoding="utf-8")
    (s2 / "README.md").write_text("# Step 2 - Rebuild each part as parametric CAD\nTool: a language model writing CadQuery. Input: `input/part_N_face_summary.txt` (readable face list from the graph file). Output: `output/part_N.py` with `PARAMS` and `build(**params)`.\n", encoding="utf-8")
    if not parts:
        (s2 / "output" / "NOT_RECONSTRUCTED.txt").write_text("No CadQuery reconstruction exists for this joint set yet (recon/recon_<id>/part_N.py). Run pipeline/llm_reconstruct.py or request one from the agent in the web UI.\n"); print(js, "step1-2 only (no reconstruction)"); return
    for k in (1, 2): shutil.copy(parts["dir"] / f"part_{k}.py", s2 / "output" / f"part_{k}.py"); ap.jdump(s2 / "output" / f"part_{k}_params.json", parts[k].PARAMS)
    # step 3
    s3 = step(3, "verify_rebuild"); S, T, DS, ADJ, CQR = {}, {}, {}, {}, {}
    for k, b in bodies.items():
        s = parts[k].build(**parts[k].PARAMS).val(); S[k] = s; CQR[k] = ap.cq_rows(s)
        rep, T[k], DS[k], ADJ[k] = ap.verify(s, b, CQR[k]); ap.jdump(s3 / "output" / f"verify_part_{k}.json", rep)
        m = ap.tessellate(s, T[k]); ap.jdump(s3 / "output" / f"part_{k}_rebuilt_mesh.json", m); print(js, f"step3 part {k}:", "PASS" if rep["PASS"] else "FAIL")
        if not rep["PASS"]:
            (s3 / "output" / "STOPPED.txt").write_text(f"part {k} failed verification; steps 4-7 not run. See verify_part_{k}.json.\n"); print(js, "stopped after step 3"); return
    (s3 / "output" / "STOPPED.txt").unlink(missing_ok=True)
    (s3 / "README.md").write_text("# Step 3 - Verify the rebuild\nTool: CadQuery + trimesh. Builds the Step 2 script, lists its faces, matches each dataset face by type/radius/centroid (-> side table), then checks face count, volume, bounding box and mean surface distance to the dataset mesh. Output: `output/verify_part_N.json`, `output/part_N_rebuilt_mesh.json` (per-triangle dataset face id).\n", encoding="utf-8")
    # step 4
    s4 = step(4, "classify_joint"); cls = ap.classify(pred, DS[1], DS[2], bodies)
    ap.jdump(s4 / "input" / "rule_table.json", {"|".join(k): v for k, v in ap.RULES.items()}); ap.jdump(s4 / "input" / "mating_pair_from_step1.json", {"part1": t["body_one"], "part2": t["body_two"], "probability": t["probability"]})
    ap.jdump(s4 / "output" / "joint_classification.json", dict(joint_set=js, **cls))
    (s4 / "README.md").write_text(f"# Step 4 - Classify the joint\nTool: dictionary lookup (`input/rule_table.json`). The face types come straight from the dataset graph labels. Lookup key here: `{cls['lookup_key']}` -> **{cls['rule']['name'] if cls['rule'] else 'no rule'}**.\n", encoding="utf-8")
    if not cls["rule"]: print(js, "no rule for", cls["lookup_key"]); return
    # step 5
    s5 = step(5, "place_parts"); po, cands, best = ap.place(S[1], S[2], T[1], T[2], cls, DS[1], DS[2], ADJ[1], ADJ[2])
    ap.jdump(s5 / "input" / "pose_options.json", po)
    for c in cands: c["_asm"].save(str(s5 / "output" / f"candidate_{'_'.join(map(str, c['option'])) if c['option'] else 'single'}.step"))
    for old in s5.glob("output/candidate_*.step"):
        if old.stem not in {f"candidate_{'_'.join(map(str, c['option'])) if c['option'] else 'single'}" for c in cands}: old.unlink()
    ap.jdump(s5 / "output" / "pose_candidates_scored.json", {"rule": "discard overlap > 1%, then pick max contact", "candidates": [{k: v for k, v in c.items() if k != "_asm"} for c in cands], "chosen_option": best["option"]})
    G1, G2 = ap.gt_transforms(js); Tb = np.array(best["part1_transform_4x4"])
    # designer frame: part2 under G2; ours: part2 identity. compare part1 pose expressed relative to part2
    rel_gt = np.linalg.inv(G2) @ G1
    err = ap.pose_error_vs_gt(cls, DS[1], CQR[1], T[1], Tb, rel_gt)
    ap.jdump(s5 / "output" / "chosen_pose.json", {"part1_transform_4x4": Tb.tolist(), "part2_transform_4x4": np.eye(4).tolist(), "option": best["option"], "underdetermined": po.get("underdetermined", False), "note": po.get("note", ""),
             "comparison_to_designer_ground_truth": dict(used_only_for_checking=True, gt_part1_relative_to_part2_4x4=rel_gt.tolist(), **err)})
    best["_asm"].save(str(s5 / "output" / "assembly_chosen.step"))
    (s5 / "README.md").write_text(f"# Step 5 - Place the parts\nTool: CadQuery assembly solver + trimesh sampling. {po['how']}. Candidates: {len(cands)}; chosen option {best['option']} with {best['contact_fraction']*100:.0f}% contact, {best['overlap_fraction']*100:.1f}% overlap. Output: `pose_candidates_scored.json`, `chosen_pose.json`, `.step` files.\n", encoding="utf-8")
    print(js, "step5 chosen", best["option"])
    # step 6
    s6 = step(6, "infer_relations"); SENS = {k: ap.sensitivity(parts[k], CQR[k], T[k]) for k in (1, 2)}
    ap.jdump(s6 / "output" / "parameter_to_face_sensitivity.json", {"how": "nudge each parameter by +0.01, rebuild, record which DATASET faces change radius/position", "part1": SENS[1], "part2": SENS[2]})
    rels = ap.infer_relations(cls, DS[1], DS[2], CQR[1], CQR[2], T[1], T[2], SENS[1], SENS[2], Tb, best["option"])
    ap.jdump(s6 / "output" / "relations.json", {"joint_set": js, "driver_part": 2, "dependent_part": 1, "relations": rels})
    (s6 / "README.md").write_text("# Step 6 - Infer parametric relations\nTool: CadQuery rebuild sensitivity + geometric scan. Output: `parameter_to_face_sensitivity.json`, `relations.json` (driver/dependent/constant per relation).\n", encoding="utf-8")
    print(js, "step6", [r["equation"] for r in rels])
    # step 7 (example edit: +30% on the driver params that appear in relations, else +30% on the first part2 param)
    s7 = step(7, "propagate_edit"); drivers = sorted({r["driver"]["param"] for r in rels if "driver" in r}) or [list(parts[2].PARAMS)[0]]
    edit = {"part": 2, "changes": {p: round(parts[2].PARAMS[p] * 1.3, 6) for p in drivers}}; ap.jdump(s7 / "input" / "user_edit.json", edit)
    p2 = dict(parts[2].PARAMS); p2.update(edit["changes"]); p1, log = ap.propagate(rels, parts[1].PARAMS, p2)
    s1b, s2b = parts[1].build(**p1).val(), parts[2].build(**p2).val()
    asm2, loc2, T2, _ = ap.assemble(s1b, s2b, T[1], T[2], cls, best["option"]); ov, ct = ap.score_pose(s1b, s2b, loc2)
    asm2.save(str(s7 / "output" / "assembly_after_edit.step"))
    ap.jdump(s7 / "output" / "propagation.json", {"edit": edit, "propagated_to_part1": log, "part1_params_after": p1, "part2_params_after": p2, "re_solved_pose": {"part1_transform_4x4": T2.tolist(), "overlap_fraction": ov, "contact_fraction": ct}})
    (s7 / "README.md").write_text(f"# Step 7 - Edit one part, the other follows\nTool: CadQuery. Edit {edit['changes']} on part 2 -> relations update part 1 -> rebuild -> re-solve pose (overlap {ov*100:.1f}%, contact {ct*100:.0f}%). Output: `propagation.json`, `assembly_after_edit.step`.\n", encoding="utf-8")
    (D / "README.md").write_text(f"# Pipeline walk-through for {js}\nEach `stepN_*` folder has `input/`, `output/`, `README.md`.\n\n| Step | What | Tool | AI? |\n|---|---|---|---|\n| 1 | which faces mate | JoinABLe GNN | yes |\n| 2 | rebuild as parametric CAD | LLM writes CadQuery | yes |\n| 3 | verify rebuild | CadQuery + trimesh | no |\n| 4 | classify joint | rule table | no |\n| 5 | place parts | CadQuery solver + sampling | no |\n| 6 | infer relations | sensitivity + scan | no |\n| 7 | propagate edit | CadQuery | no |\n", encoding="utf-8")
    print(js, "step7 overlap/contact", round(ov, 3), round(ct, 3))

if __name__ == "__main__":
    for js in sys.argv[1:]: run(js)
