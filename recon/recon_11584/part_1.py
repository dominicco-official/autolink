"""22003_c3e3616f_0017_1 (joint_set_11584, body one): a half-disc bracket with a rounded tab. Half disc r=2.5 (axis X, x 0..0.8, the
half below y=0); tab 1.2 wide (z +-0.6) from y=0 to y=1.5 topped by a semicircle r=0.6; a through hole r=0.25 along X at y=1.5 with
45-degree 0.05 chamfers on both faces; a small cross-drilled hole r=0.12645 from the top of the tab into the hole, tilted ~3.4 degrees."""
import cadquery as cq
PARAMS = {"disc_radius": 2.5, "thickness": 0.8, "tab_width": 1.2, "tab_height": 1.5, "tab_radius": 0.6, "hole_radius": 0.25, "hole_chamfer": 0.05,
          "drill_radius": 0.12645, "drill_dir_y": -0.998, "drill_dir_z": -0.060, "drill_pt_y": 1.624145, "drill_pt_z": 0.008619}
def build(disc_radius, thickness, tab_width, tab_height, tab_radius, hole_radius, hole_chamfer, drill_radius, drill_dir_y, drill_dir_z, drill_pt_y, drill_pt_z):
    R, T, w, h, r = disc_radius, thickness, tab_width, tab_height, tab_radius
    prof = (cq.Workplane("YZ").moveTo(0, -R).threePointArc((-R, 0), (0, R)).lineTo(0, w / 2).lineTo(h, w / 2)
            .threePointArc((h + r, 0), (h, -w / 2)).lineTo(0, -w / 2).close())          # (y, z) profile, normal +X
    body = prof.extrude(T)
    body = body.cut(cq.Workplane("YZ", origin=(-1, h, 0)).circle(hole_radius).extrude(T + 2))
    body = body.faces("<X").edges(cq.selectors.RadiusNthSelector(0)).chamfer(hole_chamfer).faces(">X").edges(cq.selectors.RadiusNthSelector(0)).chamfer(hole_chamfer)
    d = cq.Vector(0, drill_dir_y, drill_dir_z).normalized(); p = cq.Vector(T / 2, drill_pt_y, drill_pt_z)
    drill = cq.Workplane(cq.Plane(origin=p - d * 2, normal=d, xDir=cq.Vector(1, 0, 0))).circle(drill_radius).extrude(2.0 + (drill_pt_y - tab_height) / abs(drill_dir_y))   # from above the tab down to the hole axis
    return cq.Workplane("XY").add(body.cut(drill).val().clean())

