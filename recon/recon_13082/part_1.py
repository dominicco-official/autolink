"""137295_a2385b57_0000_1 (joint_set_13082, body one): a hollow, tapered bottle-shaped cap, revolved about Z.
Read from the 14-face graph: base cylinder r=7 (z 0-2) with a shoulder at z=2, fillet r=0.8 into an outer cone
(r 4.906 at z=2.692 -> r 3.315 at z=14.387), fillet r=0.1 under a lip at z=14.5, neck cylinder r=3.5 (z 14.5-18.5),
top bore r=2.5 down to z=12.962, inner cone parallel to the outer one down to r=4.222 at z=0.3, fillet r=0.1,
bottom recess cylinder r=5 (z 0-0.2), bottom annulus r 5..7 at z=0."""
import math, cadquery as cq

PARAMS = {"base_radius": 7.0, "base_height": 2.0, "shoulder_fillet": 0.8,
          "cone_r_bottom": 4.905862, "cone_z_bottom": 2.692192, "cone_r_top": 3.315433, "cone_z_top": 14.386524,
          "lip_fillet": 0.1, "lip_z": 14.5, "neck_radius": 3.5, "top_z": 18.5,
          "bore_radius": 2.5, "bore_bottom_z": 12.961723, "inner_cone_r_bottom": 4.221994, "inner_floor_z": 0.3,
          "recess_fillet": 0.1, "recess_radius": 5.0}

def _mid(A, B, C, r):
    """midpoint of the shorter circular arc of radius r about centre C from A to B (profile plane)."""
    a1 = math.atan2(A[1] - C[1], A[0] - C[0]); a2 = math.atan2(B[1] - C[1], B[0] - C[0])
    d = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi; m = a1 + d / 2
    return (C[0] + r * math.cos(m), C[1] + r * math.sin(m))

def build(base_radius, base_height, shoulder_fillet, cone_r_bottom, cone_z_bottom, cone_r_top, cone_z_top,
          lip_fillet, lip_z, neck_radius, top_z, bore_radius, bore_bottom_z, inner_cone_r_bottom, inner_floor_z,
          recess_fillet, recess_radius):
    # shoulder fillet: tangent to plane z=base_height, centre (rs, base_height + f)
    f = shoulder_fillet; cz = base_height + f
    # radial position of the fillet centre: distance to the cone-start point must equal f
    rs = cone_r_bottom + math.sqrt(max(f * f - (cone_z_bottom - cz) ** 2, 0.0))
    A1, B1, C1 = (rs, base_height), (cone_r_bottom, cone_z_bottom), (rs, cz)
    # lip fillet: tangent to plane z=lip_z (centre lip_fillet below it); tangent point on plane at radius rl
    rl = cone_r_top + math.sqrt(max(lip_fillet ** 2 - (cone_z_top - (lip_z - lip_fillet)) ** 2, 0.0))
    A2, B2, C2 = (cone_r_top, cone_z_top), (rl, lip_z), (rl, lip_z - lip_fillet)
    # recess fillet: between underside plane z=inner_floor_z and recess cylinder r=recess_radius
    rr = recess_radius - recess_fillet; zr = inner_floor_z - recess_fillet
    A3, B3, C3 = (rr, inner_floor_z), (recess_radius, zr), (rr, zr)
    wp = (cq.Workplane("XZ").moveTo(base_radius, 0).lineTo(base_radius, base_height).lineTo(*A1)
          .threePointArc(_mid(A1, B1, C1, f), B1).lineTo(*A2).threePointArc(_mid(A2, B2, C2, lip_fillet), B2)
          .lineTo(neck_radius, lip_z).lineTo(neck_radius, top_z).lineTo(bore_radius, top_z).lineTo(bore_radius, bore_bottom_z)
          .lineTo(inner_cone_r_bottom, inner_floor_z).lineTo(*A3).threePointArc(_mid(A3, B3, C3, recess_fillet), B3)
          .lineTo(recess_radius, 0).close())
    return wp.revolve(360, (0, 0, 0), (0, 1, 0))
