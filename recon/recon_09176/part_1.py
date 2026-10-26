"""63166_658ce590_0004_1 (joint_set_09176, body one): a clevis pin along +Y at (x=-0.78, z=-4.5): rod r=0.104403 from y=1.35 to 7.3
with a 0.1 fillet rounding the bottom end (tiny flat left), and an eye at the top: a 0.06 x 0.2 tab (x -0.81..-0.75, z -4.6..-4.4)
from y=7.3 to 7.5 with a semicircular top r=0.1 about the X axis through (y=7.5, z=-4.5) and a through hole r=0.05 along X."""
import cadquery as cq
AXIS = (-0.78, -4.5)   # (x, z) of the rod axis
PARAMS = {"rod_radius": 0.104403, "rod_bottom_y": 1.35, "rod_top_y": 7.3, "tip_fillet": 0.1, "tab_thickness": 0.06, "tab_width": 0.2, "eye_center_y": 7.5, "eye_outer_radius": 0.1, "eye_hole_radius": 0.05}
def build(rod_radius, rod_bottom_y, rod_top_y, tip_fillet, tab_thickness, tab_width, eye_center_y, eye_outer_radius, eye_hole_radius):
    x0, z0 = AXIS
    rod = cq.Workplane("XZ", origin=(x0, rod_bottom_y, z0)).circle(rod_radius).extrude(-(rod_top_y - rod_bottom_y)).faces("<Y").edges().fillet(tip_fillet)
    # eye: profile in the YZ plane (rectangle + semicircle), extruded along X across the tab thickness
    prof = (cq.Workplane("YZ", origin=(x0 - tab_thickness / 2, 0, 0)).moveTo(rod_top_y, z0 - tab_width / 2).lineTo(eye_center_y, z0 - tab_width / 2)
            .threePointArc((eye_center_y + eye_outer_radius, z0), (eye_center_y, z0 + tab_width / 2)).lineTo(rod_top_y, z0 + tab_width / 2).close().extrude(tab_thickness))
    hole = cq.Workplane("YZ", origin=(x0 - 1, eye_center_y, z0)).circle(eye_hole_radius).extrude(2)
    return rod.union(prof).cut(hole)
