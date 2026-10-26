"""56166_003bf479_0011_2 (joint_set_01324, body one): a flat washer / ring.
Graph: cylinder r=0.15 (hole, reversed), cylinder r=0.25 (outer), planes at y=-1.404060 (+Y) and y=-1.704060 (-Y). Axis Y."""
import cadquery as cq
ORIGIN = (-10.170551, -1.704060, 5.042088)          # bottom-center of the ring (dataset coordinates)
PARAMS = {"inner_radius": 0.15, "outer_radius": 0.25, "thickness": 0.30}
def build(inner_radius, outer_radius, thickness):
    pts = [(inner_radius, 0), (outer_radius, 0), (outer_radius, thickness), (inner_radius, thickness)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).translate(ORIGIN)
