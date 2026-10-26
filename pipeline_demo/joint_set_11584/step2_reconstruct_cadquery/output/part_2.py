"""22003_c3e3616f_0017_2 (joint_set_11584, body two): a pin r=0.25 along -Z (z 0..-3.5) with 45-degree 0.05 chamfers at both ends
and a flat milled at y=0.2 over the first 0.8 at each end."""
import cadquery as cq
PARAMS = {"radius": 0.25, "length": 3.5, "chamfer": 0.05, "flat_y": 0.2, "flat_length": 0.8}
def build(radius, length, chamfer, flat_y, flat_length):
    pin = cq.Workplane("XY").circle(radius).extrude(-length).edges("%CIRCLE").chamfer(chamfer)
    pin = pin.rotate((0, 0, 0), (0, 0, 1), 90)        # put the surface seam inside the flats so the cones stay single faces
    for z0 in (0.0, -length + flat_length):
        pin = pin.cut(cq.Workplane("XY").box(1, 1, flat_length, centered=(True, False, False)).translate((0, flat_y, z0 - flat_length)))
    return cq.Workplane("XY").add(pin.val().clean())   # merge cone pieces split at the seam by the flat cuts


