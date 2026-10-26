"""56166_003bf479_0007_2 (joint_set_01324, body two): a pin with a collar.
Graph: shaft cylinder r=0.14635 in two pieces (y 1.7-2.2 and 2.3-3.9), collar cylinder r=0.2 (y 2.2-2.3),
end planes at y=1.7 and y=3.9, collar shoulder planes at y=2.2 and 2.3. Axis Y."""
import cadquery as cq
ORIGIN = (-0.000008, 1.700000, -10.111850)          # bottom-center of the shaft
PARAMS = {"shaft_radius": 0.14635, "collar_radius": 0.20, "length": 2.20, "collar_start": 0.50, "collar_width": 0.10}
def build(shaft_radius, collar_radius, length, collar_start, collar_width):
    r, R, L, a, w = shaft_radius, collar_radius, length, collar_start, collar_width
    pts = [(0, 0), (r, 0), (r, a), (R, a), (R, a + w), (r, a + w), (r, L), (0, L)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).translate(ORIGIN)
