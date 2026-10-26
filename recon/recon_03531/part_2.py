"""56480_dcc89e9a_0042_1 (joint_set_03531, body two): a block with four vertical corner fillets and a square pocket in the top.
Block x 1.8-2.8 (L=1.0), y 0.8-1.4 (H=0.6), z 9.0-9.6 (W=0.6); fillet r=0.1 on the 4 Y-parallel edges;
pocket 0.140137 square, 0.2 deep, centred at (2.30973, 9.297238) (slightly off the block centre)."""
import cadquery as cq
ORIGIN = (1.8, 0.8, 9.0)
PARAMS = {"length": 1.0, "height": 0.6, "width": 0.6, "corner_fillet": 0.1, "pocket_size": 0.140137, "pocket_depth": 0.2, "pocket_dx": 0.50973, "pocket_dz": 0.297238}
def build(length, height, width, corner_fillet, pocket_size, pocket_depth, pocket_dx, pocket_dz):
    block = cq.Workplane("XY").box(length, height, width, centered=False).edges("|Y").fillet(corner_fillet)
    pocket = (cq.Workplane("XY").box(pocket_size, pocket_depth, pocket_size, centered=(True, False, True))
              .translate((pocket_dx, height - pocket_depth, pocket_dz)))
    return block.cut(pocket).translate(ORIGIN)
