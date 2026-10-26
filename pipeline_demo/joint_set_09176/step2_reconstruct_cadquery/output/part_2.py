"""63166_658ce590_0004_2 (joint_set_09176, body two): a half-tube saddle along Y: tube inner r=0.104403, outer r=0.15, axis at (x=-0.78, z=-4.5),
y from 1.35 to 7.34, kept above the plane z = -4.550495 (cut slightly below the axis)."""
import cadquery as cq
AXIS = (-0.78, -4.5)
PARAMS = {"inner_radius": 0.104403, "outer_radius": 0.15, "y_start": 1.35, "length": 5.99, "cut_offset": 0.050495}
def build(inner_radius, outer_radius, y_start, length, cut_offset):
    x0, z0 = AXIS
    tube = cq.Workplane("XZ", origin=(x0, y_start, z0)).circle(outer_radius).circle(inner_radius).extrude(-length)
    keep = cq.Workplane("XY").box(2 * outer_radius + 1, length + 1, outer_radius + 1, centered=(True, False, False)).translate((x0, y_start - 0.5, z0 - cut_offset))
    return tube.intersect(keep)
