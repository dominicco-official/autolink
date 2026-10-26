"""21237_7887a24b_0048_2 (joint_set_13342, body two): a round plate r=3.19, thickness 0.125 (z 0..0.125) with 11 through holes
of assorted radii at the positions read from the graph (PCB-like layout). Parameters: plate radius/thickness and each hole's (x, y, r)."""
import cadquery as cq
PARAMS = {"plate_radius": 3.19, "thickness": 0.125,
          "h0_x": -0.018394, "h0_y": 0.3, "h0_r": 0.5, "h1_x": 2.4, "h1_y": -1.39, "h1_r": 0.15, "h2_x": 2.53, "h2_y": 1.27, "h2_r": 0.16, "h3_x": 1.7924, "h3_y": -0.1647, "h3_r": 0.14,
          "h4_x": 0.0, "h4_y": -1.5, "h4_r": 0.215, "h5_x": -1.9, "h5_y": -1.8, "h5_r": 0.09, "h6_x": -2.4, "h6_y": -1.39, "h6_r": 0.15, "h7_x": -1.7924, "h7_y": 0.1647, "h7_r": 0.14,
          "h8_x": -1.79, "h8_y": 2.06, "h8_r": 0.1, "h9_x": 0.4, "h9_y": 2.75, "h9_r": 0.15, "h10_x": 0.0, "h10_y": 2.64, "h10_r": 0.1}
def build(plate_radius, thickness, **holes):
    plate = cq.Workplane("XY").circle(plate_radius).extrude(thickness)
    n = len(holes) // 3
    for i in range(n):
        plate = plate.cut(cq.Workplane("XY", origin=(holes[f"h{i}_x"], holes[f"h{i}_y"], -1)).circle(holes[f"h{i}_r"]).extrude(thickness + 2))
    return plate
