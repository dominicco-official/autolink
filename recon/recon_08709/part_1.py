"""29947_0f21f39e_0019_1 (joint_set_08709, body one): a tapered pin with a near-spherical nose and a bore in the flat end. Axis Z through (0, 27.5).
Top plane z=60 (annulus r 0.513675..1.1); bore r=0.513675 from z=60 down to z=54.9; shallow cone from r=1.1 at z=60 to r=1.828831 at z=49.423748;
nose arc of radius 1.8 (centre on axis-ish at z=49.3, offset 0.033089) down to a tiny flat r=0.033089 at z=47.5."""
import math, cadquery as cq
ORIGIN = (0.0, 27.5, 0.0)
PARAMS = {"top_z": 60.0, "top_radius": 1.1, "bore_radius": 0.513675, "bore_floor_z": 54.9, "cone_end_radius": 1.828831, "cone_end_z": 49.423748,
          "nose_radius": 1.8, "nose_center_z": 49.3, "nose_center_r": 0.033089, "tip_z": 47.5}
def build(top_z, top_radius, bore_radius, bore_floor_z, cone_end_radius, cone_end_z, nose_radius, nose_center_z, nose_center_r, tip_z):
    C = (nose_center_r, nose_center_z); A = (cone_end_radius, cone_end_z); B = (nose_center_r, tip_z)
    a1 = math.atan2(A[1] - C[1], A[0] - C[0]); a2 = math.atan2(B[1] - C[1], B[0] - C[0]); am = (a1 + a2) / 2
    M = (C[0] + nose_radius * math.cos(am), C[1] + nose_radius * math.sin(am))
    wp = (cq.Workplane("XY").moveTo(0, tip_z).lineTo(nose_center_r, tip_z).threePointArc(M, A).lineTo(top_radius, top_z)
          .lineTo(bore_radius, top_z).lineTo(bore_radius, bore_floor_z).lineTo(0, bore_floor_z).close())
    # profile is (r, z) in the XY plane; revolve about Y then rotate Y->Z so the part axis is Z, as in the dataset
    return wp.revolve(360, (0, 0, 0), (0, 1, 0)).rotate((0, 0, 0), (1, 0, 0), 90).translate(ORIGIN)

