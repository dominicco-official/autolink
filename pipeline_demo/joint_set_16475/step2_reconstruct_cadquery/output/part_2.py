"""40513_89770261_0009_2 (joint_set_16475, body two): a disc with both circular edges filleted, tilted in space.
Graph: cylinder r=3.15 (height 0.1), two torus fillets (minor radius 0.1 from curvature -10, edge radii 3.15 -> 3.05),
two planes 0.3 apart. The axis direction is derived from the two plane centroids."""
import cadquery as cq
BASE   = (10.836926, 31.084479, -42.847722)                    # centroid of the reversed plane (face 4)
TOP    = (10.879267, 30.863136, -42.649695)                    # centroid of the other plane (face 2)
PARAMS = {"radius": 3.15, "thickness": 0.30, "fillet": 0.10}
def build(radius, thickness, fillet):
    d = cq.Vector(*TOP) - cq.Vector(*BASE); n = d.normalized()
    plane = cq.Plane(origin=cq.Vector(*BASE), xDir=n.cross(cq.Vector(0, 0, 1)).normalized(), normal=n)
    return cq.Workplane(plane).circle(radius).extrude(thickness).edges().fillet(fillet)
