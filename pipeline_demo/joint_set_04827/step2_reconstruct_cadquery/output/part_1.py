"""136891_4af46e9c_0028_1 (joint_set_04827, body one): a hex nut, axis X, x in [0, 0.3], centre (y=0, z=2.5).
Six flats (inradius 0.291149; two flats perpendicular to Y), through bore r=0.17, and the six outer edges of the x=0.3 face
rounded with r=0.05 (the six small cylinders have axes along the flat edges, not along X)."""
import math, cadquery as cq
ORIGIN = (0.0, 0.0, 2.5)
PARAMS = {"inradius": 0.291149, "bore_radius": 0.17, "thickness": 0.3, "end_fillet": 0.05}
def build(inradius, bore_radius, thickness, end_fillet):
    circ = 2 * inradius / math.cos(math.pi / 6)
    nut = cq.Workplane("YZ").polygon(6, circ).extrude(thickness).rotate((0, 0, 0), (1, 0, 0), 30)   # flats at y = +-inradius
    nut = nut.faces(">X").workplane().hole(2 * bore_radius)
    nut = nut.faces(">X").edges("not %CIRCLE").fillet(end_fillet)
    return nut.translate(ORIGIN)
