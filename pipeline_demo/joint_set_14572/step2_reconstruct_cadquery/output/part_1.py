"""55817_6ac2912d_0016_1 (joint_set_14572, body one): a crank lever. Hub r=0.2381 (axis Y, y 0..0.3968) with a pin r=0.11905 on top
(y 0.3968..2.6987); a tapered arm (thickness y 0..0.1984) whose sides are the tangent lines between the hub circle and an end
circle r=0.1984 at x=1.299751; a pin r=0.0794 hanging below the end (y -0.3175..0)."""
import math, cadquery as cq
PARAMS = {"hub_radius": 0.2381, "hub_height": 0.3968, "top_pin_radius": 0.11905, "top_pin_top_y": 2.6987, "arm_thickness": 0.1984,
          "end_x": 1.299751, "end_radius": 0.1984, "bottom_pin_radius": 0.0794, "bottom_pin_length": 0.3175}
def build(hub_radius, hub_height, top_pin_radius, top_pin_top_y, arm_thickness, end_x, end_radius, bottom_pin_radius, bottom_pin_length):
    r1, r2, d = hub_radius, end_radius, end_x
    phi = math.asin((r1 - r2) / d); nx, nz = math.sin(phi), math.cos(phi)       # outward normal of the upper tangent line (x, z)
    P1, P2 = (r1 * nx, r1 * nz), (d + r2 * nx, r2 * nz)
    # arm outline: tangent lines + end arc; closed with a chord inside the hub so the hub cylinder is a single face after the union
    arm = (cq.Workplane("XZ").moveTo(*P1).lineTo(*P2).threePointArc((d + r2, 0), (P2[0], -P2[1])).lineTo(P1[0], -P1[1])
           .close().extrude(-arm_thickness))                                             # XZ normal is -Y; extrude -t goes +Y
    hub = cq.Workplane("XZ").circle(hub_radius).extrude(-hub_height)
    top_pin = cq.Workplane("XZ", origin=(0, hub_height, 0)).circle(top_pin_radius).extrude(-(top_pin_top_y - hub_height))
    bottom_pin = cq.Workplane("XZ", origin=(d, -bottom_pin_length, 0)).circle(bottom_pin_radius).extrude(-bottom_pin_length)
    body = arm.union(hub).union(top_pin).union(bottom_pin)
    return cq.Workplane("XY").add(body.val().clean())      # merge co-planar / co-cylindrical faces split by the booleans


