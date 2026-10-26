"""136891_4af46e9c_0028_2 (joint_set_04827, body two): a screw: shaft r=0.170825 (x -0.2..0.6), 45-degree cone from r=0.2 at x=0.6
to r=0.3 at x=0.7, head cylinder r=0.3 (x 0.7..0.8), and a plus-shaped (cross) recess in the head: two slots 0.5 long x 0.06 wide x 0.05 deep. Axis X through (y=1.0, z=4.0)."""
import cadquery as cq
ORIGIN = (0.0, 1.0, 4.0)
PARAMS = {"shaft_radius": 0.170825, "shaft_start": -0.2, "cone_start": 0.6, "cone_small_radius": 0.2, "head_radius": 0.3, "head_start": 0.7, "head_end": 0.8,
          "slot_length": 0.5, "slot_width": 0.06, "slot_depth": 0.05}
def build(shaft_radius, shaft_start, cone_start, cone_small_radius, head_radius, head_start, head_end, slot_length, slot_width, slot_depth):
    pts = [(shaft_start, 0), (shaft_start, shaft_radius), (cone_start, shaft_radius), (cone_start, cone_small_radius), (head_start, head_radius), (head_end, head_radius), (head_end, 0)]
    body = cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (1, 0, 0))
    x0 = head_end - slot_depth
    s1 = cq.Workplane("XY").box(slot_depth, slot_length, slot_width, centered=(False, True, True)).translate((x0, 0, 0))
    s2 = cq.Workplane("XY").box(slot_depth, slot_width, slot_length, centered=(False, True, True)).translate((x0, 0, 0))
    return body.cut(s1).cut(s2).translate(ORIGIN)
