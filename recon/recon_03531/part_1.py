"""56480_dcc89e9a_0024_1 (joint_set_03531, body one): a small rectangular block (key) that drops into the pocket of body two.
6 planes. bbox x 2.239662-2.379799, y 1.4-1.6, z 9.227169-9.367306."""
import cadquery as cq
ORIGIN = (2.239662, 1.4, 9.227169)
PARAMS = {"size_x": 0.140137, "height": 0.2, "size_z": 0.140137}
def build(size_x, height, size_z):
    return cq.Workplane("XY").box(size_x, height, size_z, centered=False).translate(ORIGIN)
