"""51791_b6580a7f_0007_2 (joint_set_03894, body two): a smaller tube that fits inside part one.
Graph: inner cylinder r=0.75 (reversed), outer cylinder r=1.5, end planes at x=-1 and x=+1. Axis X."""
import cadquery as cq
PARAMS = {"inner_radius": 0.75, "outer_radius": 1.5, "length": 2.0}
def build(inner_radius, outer_radius, length):
    h = length / 2
    pts = [(-h, inner_radius), (-h, outer_radius), (h, outer_radius), (h, inner_radius)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (1, 0, 0))
