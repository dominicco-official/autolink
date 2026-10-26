"""40513_89770261_0009_1 (joint_set_16475, body one): a chamfered disc with a pin on top.
Graph: disc cylinder r=3.15 (y -0.25..0), 45-degree cone chamfer 0.05 at the bottom edge (r 3.10 at y=-0.30),
bottom plane y=-0.3, top plane y=0 (annulus), pin cylinder r=0.25 (y 0..1.9), pin top plane y=1.9. Axis Y."""
import cadquery as cq
PARAMS = {"disc_radius": 3.15, "disc_thickness": 0.30, "chamfer": 0.05, "pin_radius": 0.25, "pin_length": 1.90}
def build(disc_radius, disc_thickness, chamfer, pin_radius, pin_length):
    R, T, c, r, L = disc_radius, disc_thickness, chamfer, pin_radius, pin_length
    pts = [(0, -T), (R - c, -T), (R, -T + c), (R, 0), (r, 0), (r, L), (0, L)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
