"""
autolink_pipe: shared implementation of pipeline steps 2-7 (CadQuery side, Python 3.11 env).
Used by pipeline/pipeline_steps.py (writes the step folders), pipeline/llm_reconstruct.py (step 2) and webapp/server.py (live rebuilds).
"""
import json, re, sys, itertools, importlib
from pathlib import Path
import numpy as np, trimesh, cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "j1.0.0"
DEMO = ROOT / "pipeline_demo"
TYPE_NORM = {"TORUS": "TORUS", "REVOLUTION": "TORUS", "PLANE": "PLANE", "CYLINDER": "CYLINDER", "CONE": "CONE", "SPHERE": "SPHERE"}

RULES = {
    ("CYLINDER", "CYLINDER"): {"name": "concentric", "constraints": ["coaxial"], "free_dof": ["slide along axis", "spin about axis"], "resolve_slide": "shoulder search (step 5)", "radius_relation": "r1 = r2 + clearance"},
    ("PLANE", "PLANE"): {"name": "flush_mate", "constraints": ["coplanar, normals opposed", "face centers coincide"], "free_dof": ["spin about normal"], "resolve_slide": "align face centers", "radius_relation": None},
    ("CYLINDER", "PLANE"): {"name": "axis_normal_to_plane", "constraints": ["cylinder axis parallel to plane normal"], "free_dof": ["slide in plane (2)", "slide along axis", "spin"], "resolve_slide": "shoulder search", "radius_relation": None},
    ("PLANE", "CYLINDER"): {"name": "axis_normal_to_plane", "constraints": ["cylinder axis parallel to plane normal"], "free_dof": ["slide in plane (2)", "slide along axis", "spin"], "resolve_slide": "shoulder search", "radius_relation": None},
    ("CONE", "CONE"): {"name": "concentric_taper", "constraints": ["coaxial", "equal half-angle"], "free_dof": ["spin about axis"], "resolve_slide": "cone surfaces touch", "radius_relation": "equal half-angle"},
    ("CIRCLE", "CIRCLE"): {"name": "concentric_edges", "constraints": ["coaxial", "centers coincide"], "free_dof": ["spin about axis"], "resolve_slide": "none", "radius_relation": "r1 = r2 + clearance"},
}

def jload(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def jdump(p, o): Path(p).parent.mkdir(parents=True, exist_ok=True); Path(p).write_text(json.dumps(o, indent=2, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else str(x)), encoding="utf-8")

# ---------------- dataset side ----------------
def joint_set_doc(js): return jload(DATA / f"{js}.json")

def ds_rows(body):
    """Faces of a dataset body (from its graph JSON) + adjacency (faces sharing an edge)."""
    g = jload(DATA / f"{body}.json"); faces = []
    for i, n in enumerate(g["nodes"]):
        if "surface_type" not in n: break
        r = {"ds_face": i, "type": TYPE_NORM[n["surface_type"].replace("SurfaceType", "").upper()], "centroid": [n["centroid_x"], n["centroid_y"], n["centroid_z"]], "area": n["area"], "reversed": bool(n.get("reversed"))}
        if "normal_x" in n: r["normal"] = (np.array([n["normal_x"], n["normal_y"], n["normal_z"]]) * (-1 if n.get("reversed") else 1)).tolist()
        if "radius" in n: r["radius"] = n["radius"]
        if "axis_x" in n: r["axis_dir"] = [n["axis_x"], n["axis_y"], n["axis_z"]]
        faces.append(r)
    nf = len(faces); ef = {}; adj = {i: set() for i in range(nf)}
    pos = {n["id"]: i for i, n in enumerate(g["nodes"])}   # node ids may be out of order; JoinABLe/OBJ use array position
    for l in g["links"]:
        a, b = pos[l["source"]], pos[l["target"]]
        if a < nf and b < nf: adj[a].add(b); adj[b].add(a)            # direct face-face link (seam cases)
        elif a < nf or b < nf: f, e = (a, b) if a < nf else (b, a); ef.setdefault(e, set()).add(f)
    for fs in ef.values():
        for a in fs: adj[a] |= fs - {a}
    return g["properties"], faces, {k: sorted(v) for k, v in adj.items()}

def face_summary_text(body):
    g = jload(DATA / f"{body}.json"); p = g["properties"]; L = [f"BODY {body}", f"faces={p['face_count']} edges={p['edge_count']} volume={p['volume']:.6f} area={p['area']:.6f}"]
    b = p["bounding_box"]; L.append(f"bbox min=({b['min_point']['x']:.6f}, {b['min_point']['y']:.6f}, {b['min_point']['z']:.6f}) max=({b['max_point']['x']:.6f}, {b['max_point']['y']:.6f}, {b['max_point']['z']:.6f})"); L.append("")
    for i, n in enumerate(g["nodes"]):
        if "surface_type" in n:
            s = f"face {i:2d} {n['surface_type'].replace('SurfaceType',''):9s} area={n['area']:.6f} centroid=({n['centroid_x']:.6f}, {n['centroid_y']:.6f}, {n['centroid_z']:.6f})"
            if "normal_x" in n: s += f" normal=({n['normal_x']:.3f}, {n['normal_y']:.3f}, {n['normal_z']:.3f})"
            if "radius" in n: s += f" radius={n['radius']:.6f}"
            if "axis_x" in n: s += f" axis=({n['axis_x']:.3f}, {n['axis_y']:.3f}, {n['axis_z']:.3f}) origin=({n['origin_x']:.6f}, {n['origin_y']:.6f}, {n['origin_z']:.6f})"
            if n["surface_type"] == "TorusSurfaceType": s += f" curvatures=({n['max_curvature']:.6f}, {n['min_curvature']:.6f})"
            if n.get("reversed"): s += " (reversed: material on the other side)"
        else:
            s = f"edge {i:2d} {n['curve_type'].replace('CurveType',''):9s} length={n['length']:.6f} {n.get('convexity','')}"
            if "radius" in n: s += f" radius={n['radius']:.6f} center=({n['center_x']:.6f}, {n['center_y']:.6f}, {n['center_z']:.6f})"
        L.append(s)
    nf = p["face_count"]; ef = {}; pos = {n["id"]: i for i, n in enumerate(g["nodes"])}
    for l in g["links"]:
        a, b2 = pos[l["source"]], pos[l["target"]]
        if (a < nf) == (b2 < nf): continue
        f, e = (a, b2) if a < nf else (b2, a); ef.setdefault(e, set()).add(f)
    L += ["", "edge -> faces it borders:"] + [f"  edge {e}: faces {sorted(ef[e])}" for e in sorted(ef)]
    return "\n".join(L)

def obj_mesh(body):
    """Dataset OBJ -> {vertices, triangles, tri_face} where tri_face[i] is the dataset face index of triangle i."""
    V, T, TF, cur = [], [], [], -1
    for line in (DATA / f"{body}.obj").read_text(encoding="utf-8").splitlines():
        if line.startswith("g face "): cur = int(line.split()[2])
        elif line.startswith("g "): cur = -1
        elif line.startswith("v "): V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f ") and cur >= 0:
            idx = [int(tok.split("/")[0]) - 1 for tok in line.split()[1:]]
            for k in range(1, len(idx) - 1): T.append([idx[0], idx[k], idx[k + 1]]); TF.append(cur)
    return {"vertices": V, "triangles": T, "tri_face": TF}

def gt_transforms(js):
    j = joint_set_doc(js)["joints"][0]
    def M(t):
        m = np.eye(4); m[:3, 0] = [t["x_axis"]["x"], t["x_axis"]["y"], t["x_axis"]["z"]]; m[:3, 1] = [t["y_axis"]["x"], t["y_axis"]["y"], t["y_axis"]["z"]]
        m[:3, 2] = [t["z_axis"]["x"], t["z_axis"]["y"], t["z_axis"]["z"]]; m[:3, 3] = [t["origin"]["x"], t["origin"]["y"], t["origin"]["z"]]; return m
    return M(j["geometry_or_origin_one"]["transform"]), M(j["geometry_or_origin_two"]["transform"])

# ---------------- CadQuery side ----------------
def load_parts(js):
    d = ROOT / "recon" / f"recon_{js.split('_')[-1]}"
    if not (d / "part_1.py").exists(): return None
    if str(d) not in sys.path: sys.path.insert(0, str(d))
    for m in ("part_1", "part_2"): sys.modules.pop(m, None)
    return {1: importlib.import_module("part_1"), 2: importlib.import_module("part_2"), "dir": d}

def cq_rows(solid):
    rows = []
    for i, f in enumerate(solid.Faces()):
        t = TYPE_NORM.get(f.geomType(), f.geomType()); c = f.Center()
        r = {"cq_face": i, "type": t, "centroid": [c.x, c.y, c.z], "area": f.Area()}
        if t == "PLANE": n = f.normalAt(); r["normal"] = [n.x, n.y, n.z]
        if t == "CYLINDER":
            cyl = BRepAdaptor_Surface(f.wrapped).Cylinder(); ax = cyl.Axis(); r["radius"] = cyl.Radius()   # BRepAdaptor handles trimmed surfaces too
            r["axis_dir"] = [ax.Direction().X(), ax.Direction().Y(), ax.Direction().Z()]; r["axis_pt"] = [ax.Location().X(), ax.Location().Y(), ax.Location().Z()]
        if t == "SPHERE": r["radius"] = BRepAdaptor_Surface(f.wrapped).Sphere().Radius()
        rows.append(r)
    return rows

def side_table(cqr, dsr, tol=None):
    if tol is None:   # centroid tolerance scales with part size (0.1% of bbox diagonal, min 0.002 cm)
        pts = np.array([c["centroid"] for c in cqr]); tol = max(2e-3, 1e-3 * float(np.linalg.norm(pts.max(0) - pts.min(0)))) if len(cqr) else 2e-3
    table, per_face = {}, []
    for d in dsr:
        compatible = {d["type"]} | ({"CYLINDER"} if d["type"] == "CONE" else set())   # a cone with ~zero taper is classified as a cylinder by OCC
        cands = [(float(np.linalg.norm(np.subtract(c["centroid"], d["centroid"]))), c["cq_face"]) for c in cqr
                 if c["type"] in compatible and (d["type"] not in ("CYLINDER", "SPHERE") or "radius" not in d or abs(c.get("radius", -9) - d["radius"]) < tol)]
        best = min(cands) if cands else None; ok = best is not None and best[0] < tol
        if ok: table[d["ds_face"]] = best[1]
        per_face.append({"dataset_face": d["ds_face"], "type": d["type"], "radius": d.get("radius"), "matched_cq_face": best[1] if ok else None, "centroid_distance": best[0] if best else None,
                         "area_dataset": d["area"], "area_cadquery": cqr[best[1]]["area"] if ok else None, "area_rel_err": abs(cqr[best[1]]["area"] - d["area"]) / d["area"] if ok else None, "MATCH": ok})
    return table, per_face

def tessellate(solid, table=None, tol=0.002, ang=0.1):
    """Per-face tessellation -> {vertices, triangles, tri_face (DATASET face id via table, else cq face id)}."""
    inv = {v: k for k, v in (table or {}).items()}
    V, T, TF = [], [], []
    for i, f in enumerate(solid.Faces()):
        vs, ts = f.tessellate(tol, ang); base = len(V)
        V += [[v.x, v.y, v.z] for v in vs]; T += [[base + a, base + b, base + c] for a, b, c in ts]; TF += [inv.get(i, i)] * len(ts)
    return {"vertices": V, "triangles": T, "tri_face": TF}

def to_trimesh(solid, path=None, tol=None):
    bb = solid.BoundingBox(); diag = float(np.linalg.norm([bb.xlen, bb.ylen, bb.zlen]))
    tol = tol or max(5e-4, 3e-4 * diag)          # linear deflection scales with part size (keeps triangle counts sane)
    m = tessellate(solid, tol=tol, ang=0.1); return trimesh.Trimesh(np.array(m["vertices"]), np.array(m["triangles"]), process=True)

def chamfer(a, b, n=3000):
    pa, _ = trimesh.sample.sample_surface(a, n); pb, _ = trimesh.sample.sample_surface(b, n)
    def d(mesh, pts):   # chunked point-to-surface distance (trimesh tiles points x candidate triangles; keep it bounded)
        return np.concatenate([trimesh.proximity.closest_point(mesh, pts[i:i + 500])[1] for i in range(0, len(pts), 500)])
    return float(d(b, pa).mean() + d(a, pb).mean())

def verify(solid, body, cqr=None):
    props, dsr, adj = ds_rows(body); cqr = cqr or cq_rows(solid); table, per_face = side_table(cqr, dsr)
    bb = solid.BoundingBox(); b = props["bounding_box"]
    bb_err = max(abs(bb.xmin - b["min_point"]["x"]), abs(bb.ymin - b["min_point"]["y"]), abs(bb.zmin - b["min_point"]["z"]), abs(bb.xmax - b["max_point"]["x"]), abs(bb.ymax - b["max_point"]["y"]), abs(bb.zmax - b["max_point"]["z"]))
    cd = chamfer(trimesh.load(DATA / f"{body}.obj", force="mesh"), to_trimesh(solid))
    diag = float(np.linalg.norm([bb.xlen, bb.ylen, bb.zlen])); cd_tol = max(0.01, 0.005 * diag)   # dataset meshes are coarse; scale tolerance with part size
    checks = [{"check": "face count equal", "cadquery": len(cqr), "dataset": props["face_count"], "pass": len(cqr) == props["face_count"]},
              {"check": "every dataset face matched (type, position, radius)", "matched": len(table), "of": props["face_count"], "pass": len(table) == props["face_count"]},
              {"check": "volume within 0.1%", "cadquery": solid.Volume(), "dataset": props["volume"], "pass": abs(solid.Volume() - props["volume"]) / props["volume"] < 1e-3},
              {"check": "bounding box within 1e-4 cm", "max_abs_err": bb_err, "pass": bb_err < 1e-4},
              {"check": "mean surface distance to dataset mesh < max(0.01 cm, 0.5% of bbox diagonal)", "chamfer_cm": cd, "tolerance_cm": cd_tol, "pass": cd < cd_tol}]
    return {"body": body, "PASS": all(c["pass"] for c in checks), "checks": checks, "face_matching": per_face, "side_table_dataset_face_to_cadquery_face": table, "face_adjacency_from_dataset": adj}, table, dsr, adj

def _promote_edge(side, dsr, body):
    """JoinABLe may pick a circular EDGE; use the cylinder face that edge borders (same axis, same radius)."""
    if side["entity"] == "BRepFace": return side["index"], side["geometry"].upper(), None
    g = jload(DATA / f"{body}.json"); nf = len(dsr); pos = {n["id"]: i for i, n in enumerate(g["nodes"])}
    e = side["index"]; faces = set()   # JoinABLe reports edges by flat node index (faces first, then edges)
    for l in g["links"]:
        a, b = pos[l["source"]], pos[l["target"]]
        if a == e and b < nf: faces.add(b)
        if b == e and a < nf: faces.add(a)
    cyl = [i for i in faces if dsr[i]["type"] == "CYLINDER" and abs(dsr[i].get("radius", -1) - (side.get("radius") or -2)) < 1e-4]
    if cyl: return cyl[0], "CYLINDER", f"edge {side['index']} ({side['geometry']}) -> adjacent cylinder face {cyl[0]}"
    pl = [i for i in faces if dsr[i]["type"] == "PLANE"]
    if pl: return pl[0], "PLANE", f"edge {side['index']} ({side['geometry']}) -> adjacent plane face {pl[0]}"
    return side["index"], "EDGE:" + side["geometry"].upper(), None

def classify(pred, dsr1, dsr2, bodies=None):
    top = pred["candidates"][0]
    if bodies:
        f1, t1, n1 = _promote_edge(top["body_one"], dsr1, bodies[1]); f2, t2, n2 = _promote_edge(top["body_two"], dsr2, bodies[2])
    else:
        f1, f2 = top["body_one"]["index"], top["body_two"]["index"]; t1, t2 = top["body_one"]["geometry"].upper(), top["body_two"]["geometry"].upper(); n1 = n2 = None
        if top["body_one"]["entity"] != "BRepFace" or top["body_two"]["entity"] != "BRepFace": t1, t2 = "EDGE:" + t1, "EDGE:" + t2
    rule = RULES.get((t1, t2)); r1 = dsr1[f1].get("radius") if t1 == "CYLINDER" else None; r2 = dsr2[f2].get("radius") if t2 == "CYLINDER" else None
    return {"part1_face": f1, "part1_type": t1, "part1_radius": r1, "part2_face": f2, "part2_type": t2, "part2_radius": r2, "lookup_key": f"{t1}|{t2}", "rule": rule,
            "edge_promotion": [x for x in (n1, n2) if x],
            "radius_difference": (r1 - r2) if (r1 is not None and r2 is not None) else None,
            "fit_label_geometric": (("clearance" if r1 > r2 else "interference_or_equal") if (r1 is not None and r2 is not None) else None),
            "where_an_LLM_or_VLM_could_add_value": ["name the functional intent (press fit vs clearance vs sliding)", "handle pairs not in the rule table (torus, nurbs, mixed)", "break ties when Step 5 contact scores are close"]}

# ---------------- placement ----------------
def _axis_edge(face):
    cyl = BRepAdaptor_Surface(face.wrapped).Cylinder(); ax = cyl.Axis(); p, d = ax.Location(), ax.Direction()
    p0 = cq.Vector(p.X(), p.Y(), p.Z()); dv = cq.Vector(d.X(), d.Y(), d.Z()); return cq.Edge.makeLine(p0 - dv * 10, p0 + dv * 10)

def _loc_to_T(loc): return np.array([[loc.wrapped.Transformation().Value(i, j) for j in range(1, 5)] for i in range(1, 4)] + [[0, 0, 0, 1]])

def assemble(s1, s2, t1, t2, cls, option):
    """option: for concentric -> (shoulder1, shoulder2); for flush_mate -> None. Returns (asm, loc, T, constraint text list)."""
    f1, f2 = cls["part1_face"], cls["part2_face"]; F1 = lambda d: s1.Faces()[t1[d]]; F2 = lambda d: s2.Faces()[t2[d]]
    asm = cq.Assembly().add(s2, name="part2", color=cq.Color("lightgray")).add(s1, name="part1", color=cq.Color("steelblue")); asm.constrain("part2", "Fixed"); txt = ["part2 Fixed"]
    if cls["rule"]["name"] == "concentric":
        asm.constrain("part1", F1(f1), "part2", _axis_edge(F2(f2)), "PointOnLine"); txt.append(f"part1 cylinder face {f1} PointOnLine axis of part2 cylinder face {f2}")
        if option is None:   # no shoulders anywhere: align axes and face centres
            asm.constrain("part1", F1(f1), "part2", F2(f2), "Axis", param=0); asm.constrain("part1", F1(f1), "part2", F2(f2), "Point"); txt.append("axis-only: cylinder axes parallel, face centres coincident")
        else:
            a, b, orient = (list(option) + ["opposed"])[:3]; ang = 180 if orient == "opposed" else 0
            asm.constrain("part1", F1(a), "part2", F2(b), "Axis", param=ang); txt.append(f"part1 plane {a} Axis part2 plane {b} (normals {orient})")
            asm.constrain("part1", F1(a), "part2", F2(b), "PointInPlane"); txt.append(f"part1 plane {a} PointInPlane part2 plane {b}")
    elif cls["rule"]["name"] == "flush_mate":
        asm.constrain("part1", F1(f1), "part2", F2(f2), "Plane"); txt.append(f"part1 plane {f1} Plane part2 plane {f2} (flush, centers coincide)")
    else:
        raise NotImplementedError(cls["rule"]["name"] if cls["rule"] else cls["lookup_key"])
    asm.solve(); loc = asm.children[1].loc; return asm, loc, _loc_to_T(loc), txt

def score_pose(s1, s2, loc, n=5000):
    m1 = to_trimesh(s1.moved(loc), tol=0.002); m2 = to_trimesh(s2, tol=0.002)
    pts, _ = trimesh.sample.sample_surface(m1, n); sd = trimesh.proximity.signed_distance(m2, pts)
    return float((sd > 2e-3).mean()), float((np.abs(sd) < 2e-3).mean())

def pose_options(cls, dsr1, dsr2, adj1, adj2):
    if cls["rule"] and cls["rule"]["name"] == "concentric":
        def sh(dsr, adj, f, widen=False):
            ax = np.array(dsr[f]["axis_dir"]); pool = adj[f] if not widen else range(len(dsr))
            return [j for j in pool if dsr[j]["type"] == "PLANE" and abs(abs(np.dot(dsr[j]["normal"], ax)) - 1) < 1e-6]
        a, b = sh(dsr1, adj1, cls["part1_face"]), sh(dsr2, adj2, cls["part2_face"]); how = "planar faces adjacent to each mating cylinder with normal along the axis"
        if not a or not b:   # e.g. a hole through a plate has no adjacent shoulder: use every plane perpendicular to the axis on that body
            a = a or sh(dsr1, adj1, cls["part1_face"], True); b = b or sh(dsr2, adj2, cls["part2_face"], True); how += " (widened to all perpendicular planes where the cylinder has no adjacent shoulder)"
        opts = [[x, y, o] for x, y in itertools.product(a, b) for o in ("opposed", "parallel")]
        if not opts: opts = [None]; how += "; no perpendicular planes at all: axis-only pose (origins aligned)"
        return {"how": how + "; every pairing, with normals opposed (faces touch) or parallel (faces flush, nested), is a candidate stop position", "part1_shoulders": a, "part2_shoulders": b, "options": opts}
    return {"how": "flush mate fully determines position (centers coincide); single candidate", "options": [None]}

def place(s1, s2, t1, t2, cls, dsr1, dsr2, adj1, adj2, with_scores=True):
    po = pose_options(cls, dsr1, dsr2, adj1, adj2); cands = []
    for opt in po["options"]:
        asm, loc, T, txt = assemble(s1, s2, t1, t2, cls, opt)
        ov, ct = score_pose(s1, s2, loc) if with_scores else (0.0, 0.0)
        cands.append({"option": opt, "constraints_given_to_solver": txt, "overlap_fraction": ov, "contact_fraction": ct, "part1_transform_4x4": T.tolist(), "_asm": asm})
    valid = [c for c in cands if c["overlap_fraction"] < 0.01] or cands
    best = max(valid, key=lambda c: c["contact_fraction"])
    po["underdetermined"] = bool(best["contact_fraction"] < 0.01 and len(cands) > 1)
    if cls["rule"]["name"] == "concentric" and len(cands) > 1 and sum(c["contact_fraction"] >= 0.9 * best["contact_fraction"] for c in valid) > 1 and best["contact_fraction"] > 0.01:
        po["ambiguous"] = True; po["note"] = (po.get("note", "") + " several poses have near-equal contact: tie-break needed (user offset / VLM)").strip()
    po["note"] = "no candidate makes real contact: the slide along the axis is not fixed by geometry (user offset or VLM needed)" if po["underdetermined"] else ""
    return po, cands, best

# ---------------- relations ----------------
def sensitivity(mod, base_rows, table):
    inv = {v: k for k, v in table.items()}; dep = {}
    for p in mod.PARAMS:
        prm = dict(mod.PARAMS); prm[p] += 0.01
        try: rows = cq_rows(mod.build(**prm).val())
        except Exception: continue
        for b in base_rows:
            if len(rows) == len(base_rows) and rows[b["cq_face"]]["type"] == b["type"]: r = rows[b["cq_face"]]
            else:
                same = [r for r in rows if r["type"] == b["type"]]
                if not same: continue
                r = min(same, key=lambda r: np.linalg.norm(np.subtract(r["centroid"], b["centroid"])))
            d = {}
            if "radius" in b: d["d_radius/d_param"] = round((r["radius"] - b["radius"]) / 0.01, 4)
            d["d_position/d_param"] = round(float(np.linalg.norm(np.subtract(r["centroid"], b["centroid"])) / 0.01), 4)
            d = {k: v for k, v in d.items() if abs(v) > 1e-6}
            if d and b["cq_face"] in inv: dep.setdefault(str(inv[b["cq_face"]]), {})[p] = d
    return dep

def radius_param(sens, ds_face):
    r = [(p, v["d_radius/d_param"]) for p, v in sens.get(str(ds_face), {}).items() if "d_radius/d_param" in v]
    return max(r, key=lambda x: abs(x[1]))[0] if r else None

def infer_relations(cls, dsr1, dsr2, cqr1, cqr2, t1, t2, sens1, sens2, T, best_option):
    rel = []; f1, f2 = cls["part1_face"], cls["part2_face"]
    if cls["rule"] and cls["rule"]["radius_relation"] and cls["part1_radius"] is not None:
        c = cls["part1_radius"] - cls["part2_radius"]; pa, pb = radius_param(sens1, f1), radius_param(sens2, f2)
        if pa and pb: rel.append({"kind": "concentric_clearance", "source": "step 4 joint rule", "faces": {"part1": f1, "part2": f2}, "equation": f"part1.{pa} = part2.{pb} + {c:.6f}", "dependent": {"part": 1, "param": pa}, "driver": {"part": 2, "param": pb}, "constant": c})
    R = T[:3, :3]
    for a in dsr1:
        if a["type"] != "CYLINDER" or a["ds_face"] == f1 or a["ds_face"] not in t1: continue
        ca = cqr1[t1[a["ds_face"]]]; da = R @ np.array(ca["axis_dir"]); pa_ = R @ np.array(ca["axis_pt"]) + T[:3, 3]
        for b in dsr2:
            if b["type"] != "CYLINDER" or b["ds_face"] == f2 or b["ds_face"] not in t2: continue
            cb = cqr2[t2[b["ds_face"]]]
            coax = abs(abs(np.dot(da, cb["axis_dir"])) - 1) < 1e-4 and np.linalg.norm(np.cross(pa_ - np.array(cb["axis_pt"]), cb["axis_dir"])) < 1e-3
            if coax and abs(a["radius"] - b["radius"]) < 1e-4:
                qa, qb = radius_param(sens1, a["ds_face"]), radius_param(sens2, b["ds_face"])
                if qa and qb: rel.append({"kind": "coaxial_equal_radius", "source": "scan of assembled model: coaxial cylinders with equal radius", "faces": {"part1": a["ds_face"], "part2": b["ds_face"]}, "equation": f"part1.{qa} = part2.{qb}", "dependent": {"part": 1, "param": qa}, "driver": {"part": 2, "param": qb}, "constant": 0.0})
    rel.append({"kind": "pose_constraint", "source": "step 5", "faces": {"part1": f1, "part2": f2, "option": best_option}, "equation": cls["rule"]["name"] + (" + shoulders flush" if best_option else "") + " (re-solved after every edit)"})
    return rel

def propagate(relations, p1, p2):
    p1 = dict(p1); log = []
    for r in relations:
        if "dependent" not in r: continue
        old = p1[r["dependent"]["param"]]; p1[r["dependent"]["param"]] = p2[r["driver"]["param"]] + r["constant"]
        log.append({"relation": r["equation"], "part1_param": r["dependent"]["param"], "old": old, "new": p1[r["dependent"]["param"]]})
    return p1, log



def pose_error_vs_gt(cls, dsr1, cqr1, t1, T, rel_gt):
    """Compare our part1 pose with the designer's, ignoring spin about the joint axis.
    Returns axis angle (deg, mod 180), axial and radial offset (cm) of part1's mating-axis origin."""
    f1 = cls["part1_face"]; row = cqr1[t1[f1]] if f1 in t1 else None
    if row is None: return {"note": "mating face not in side table"}
    if cls["part1_type"] == "CYLINDER": d = np.array(row["axis_dir"]); p = np.array(row["axis_pt"])
    else: d = np.array(row["normal"]); p = np.array(row["centroid"])
    d_ours = T[:3, :3] @ d; p_ours = T[:3, :3] @ p + T[:3, 3]; d_gt = rel_gt[:3, :3] @ d; p_gt = rel_gt[:3, :3] @ p + rel_gt[:3, 3]
    ang = float(np.degrees(np.arccos(np.clip(abs(np.dot(d_ours, d_gt)), -1, 1))))
    dp = p_ours - p_gt; axial = float(abs(np.dot(dp, d_gt))); radial = float(np.linalg.norm(dp - np.dot(dp, d_gt) * d_gt))
    return {"axis_angle_error_deg": ang, "axial_offset_cm": axial, "radial_offset_cm": radial,
            "note": "spin about the joint axis is a free degree of freedom and is not counted"}
