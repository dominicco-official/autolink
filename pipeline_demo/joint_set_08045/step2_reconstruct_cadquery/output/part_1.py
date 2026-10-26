"""55717_8ee13ef1_0016_1 (joint_set_08045, body one): a hemisphere (dome cap).
Graph: plane at z=0 (normal -Z) and a sphere face r=0.635 above it. Axis Z."""
import math, cadquery as cq
PARAMS = {"radius": 0.635}
def build(radius):
    r = radius; m = (r * math.cos(math.pi / 4), r * math.sin(math.pi / 4))
    # quarter-disc profile in the (x, z) half-plane, revolved about Z
    return cq.Workplane("XZ").moveTo(0, 0).lineTo(r, 0).threePointArc(m, (0, r)).close().revolve(360, (0, 0, 0), (0, 1, 0))
