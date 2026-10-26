"""89527_b3bf425d_0031_2 (joint_set_17464, body two): a cylindrical block (axis Y, r=1.375, h=3.8) with a 0.3 fillet on the top
edge and five holes drilled from the bottom/side:
  two r=0.12645 blind holes depth 0.8 at (x=0, z=+-1.0262)
  r=0.6 blind hole depth 2.7 at x=0.6 ; r=0.35 blind hole depth 3.2 at x=-0.7
  a counterbored cross hole at y=2.5 along X from the -X side: r=0.3 to x=-0.2, then r=0.2 on into the r=0.6 hole."""
import cadquery as cq
PARAMS = {"radius": 1.375, "height": 3.8, "top_fillet": 0.3, "pin_hole_radius": 0.12645, "pin_hole_depth": 0.8, "pin_hole_z": 1.0262,
          "big_hole_radius": 0.6, "big_hole_depth": 2.7, "big_hole_x": 0.6, "mid_hole_radius": 0.35, "mid_hole_depth": 3.2, "mid_hole_x": -0.7,
          "cross_y": 2.5, "cbore_radius": 0.3, "cbore_end_x": -0.2, "cross_radius": 0.2}
def _ycyl(r, depth, x, z):   # blind hole from the bottom plane y=0 upward
    return cq.Workplane("XZ", origin=(x, 0, z)).circle(r).extrude(-depth)
def build(radius, height, top_fillet, pin_hole_radius, pin_hole_depth, pin_hole_z, big_hole_radius, big_hole_depth, big_hole_x,
          mid_hole_radius, mid_hole_depth, mid_hole_x, cross_y, cbore_radius, cbore_end_x, cross_radius):
    body = cq.Workplane("XZ").circle(radius).extrude(-height).faces(">Y").edges().fillet(top_fillet)
    body = body.cut(_ycyl(pin_hole_radius, pin_hole_depth, 0, pin_hole_z)).cut(_ycyl(pin_hole_radius, pin_hole_depth, 0, -pin_hole_z))
    body = body.cut(_ycyl(big_hole_radius, big_hole_depth, big_hole_x, 0)).cut(_ycyl(mid_hole_radius, mid_hole_depth, mid_hole_x, 0))
    cbore = cq.Workplane("YZ", origin=(-radius - 0.2, cross_y, 0)).circle(cbore_radius).extrude(cbore_end_x - (-radius - 0.2))
    cross = cq.Workplane("YZ", origin=(cbore_end_x, cross_y, 0)).circle(cross_radius).extrude(big_hole_x - cbore_end_x)
    return body.cut(cbore).cut(cross)
