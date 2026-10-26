"""55817_6ac2912d_0016_2 (joint_set_14572, body two): a long crank arm. Hub r=0.7144 with bore r=0.55565 (axis Y, y 0..0.4763);
a full-height block (y 0..0.4763, z +-0.1984) from the hub to x=-1.024, 45-degree chamfers (0.1) and short vertical steps down to a thin web
(y 0.1588..0.3175) that runs to x=-8.901883 where it ends in a half-round r=0.19845 with a through hole r=0.0794."""
import cadquery as cq
PARAMS = {"hub_radius": 0.7144, "bore_radius": 0.55565, "hub_height": 0.4763, "arm_width": 0.3968, "block_end_x": -1.024, "chamfer": 0.1,
          "web_bottom_y": 0.1588, "web_top_y": 0.3175, "end_x": -8.901883, "end_radius": 0.19845, "end_hole_radius": 0.0794}
def build(hub_radius, bore_radius, hub_height, arm_width, block_end_x, chamfer, web_bottom_y, web_top_y, end_x, end_radius, end_hole_radius):
    xb, c, H = block_end_x, chamfer, hub_height
    prof = [(-0.3, 0), (xb, 0), (xb - c, c), (xb - c, web_bottom_y), (end_x, web_bottom_y), (end_x, web_top_y), (xb - c, web_top_y), (xb - c, H - c), (xb, H), (-0.3, H)]
    arm = cq.Workplane("XY", origin=(0, 0, -arm_width / 2)).polyline(prof).close().extrude(arm_width)
    end = cq.Workplane("XZ", origin=(end_x, web_bottom_y, 0)).circle(end_radius).extrude(-(web_top_y - web_bottom_y))
    hub = cq.Workplane("XZ").circle(hub_radius).extrude(-H)
    body = arm.union(end).union(hub)
    body = body.cut(cq.Workplane("XZ", origin=(0, -1, 0)).circle(bore_radius).extrude(-(H + 2)))
    body = body.cut(cq.Workplane("XZ", origin=(end_x, -1, 0)).circle(end_hole_radius).extrude(-(H + 2)))
    return body
