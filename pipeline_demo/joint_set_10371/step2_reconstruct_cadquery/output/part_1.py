"""41729_b5092135_0012_2 (joint_set_10371, body one): a wheel / pulley blank.
Graph: outer cylinder r=15.15 (y 0-3.5); rim inner cylinders r=14.21267 as two counterbores (y 0-0.5 and 3.0-3.5);
web between y=0.5 and y=3.0 with a central hole r=2.5; planes at y=0, 0.5, 3.0, 3.5. Axis Y."""
import cadquery as cq
PARAMS = {"outer_radius": 15.15, "rim_inner_radius": 14.21267, "hole_radius": 2.5, "height": 3.5, "web_offset": 0.5, "web_thickness": 2.5}
def build(outer_radius, rim_inner_radius, hole_radius, height, web_offset, web_thickness):
    R, Ri, h, H, a, t = outer_radius, rim_inner_radius, hole_radius, height, web_offset, web_thickness
    pts = [(Ri, 0), (R, 0), (R, H), (Ri, H), (Ri, a + t), (h, a + t), (h, a), (Ri, a)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
