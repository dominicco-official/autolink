"""55634_3b61fa4d_0049_2 (joint_set_12396, body two): a thin plate with two holes and a side tab.
Plate 0.2 thick in X (x -12.6625..-12.4625), y 0..0.8, z -120.75..-118.25, two r=0.1 holes along X at z=-120.35 and -118.65 (y=0.4).
Tab (y 0.3..0.5) sticking out in -X: straight top edge z=-119.05 to x=-13.48, rounded nose made of two r=0.12 arcs (centres
(-13.48,-119.17) and (-13.48,-119.1423): the original sketch is not a single arc), a slanted lower edge back to the plate, hole r=0.08 at (-13.35,-119.2)."""
import math, cadquery as cq
PARAMS = {"plate_x0": -12.6625, "plate_t": 0.2, "plate_h": 0.8, "z0": -120.75, "z1": -118.25, "hole_r": 0.1, "hole_y": 0.4, "hole_z1": -120.35, "hole_z2": -118.65,
          "tab_y0": 0.3, "tab_y1": 0.5, "tab_top_z": -119.05, "nose_x": -13.48, "nose_r": 0.12, "noseA_z": -119.17, "noseA_deg": 83.4, "noseB_z": -119.1423, "noseB_deg": 44.7,
          "slant_dx": 0.781, "slant_dz": -0.625, "tab_hole_r": 0.08, "tab_hole_x": -13.35, "tab_hole_z": -119.2}
def _arc(c, r, a0, a1):
    m = math.radians((a0 + a1) / 2); e = math.radians(a1)
    return (c[0] + r * math.cos(m), c[1] + r * math.sin(m)), (c[0] + r * math.cos(e), c[1] + r * math.sin(e))
def build(plate_x0, plate_t, plate_h, z0, z1, hole_r, hole_y, hole_z1, hole_z2, tab_y0, tab_y1, tab_top_z, nose_x, nose_r, noseA_z, noseA_deg, noseB_z, noseB_deg,
          slant_dx, slant_dz, tab_hole_r, tab_hole_x, tab_hole_z):
    plate = cq.Workplane("XY").box(plate_t, plate_h, z1 - z0, centered=False).translate((plate_x0, 0, z0))
    for z in (hole_z1, hole_z2): plate = plate.cut(cq.Workplane("YZ", origin=(plate_x0 - 1, hole_y, z)).circle(hole_r).extrude(plate_t + 2))
    A = (nose_x, noseA_z); B = (nose_x, noseB_z)
    mA, eA = _arc(A, nose_r, 90, 90 + noseA_deg)
    aB0 = math.degrees(math.atan2(eA[1] - B[1], eA[0] - B[0])); mB, eB = _arc(B, nose_r, aB0, aB0 + noseB_deg)
    t = (plate_x0 - eB[0]) / slant_dx; end = (plate_x0, eB[1] + slant_dz * t)
    tab = (cq.Workplane("XZ", origin=(0, tab_y0, 0)).moveTo(plate_x0 + 0.1, tab_top_z).lineTo(nose_x, tab_top_z).threePointArc(mA, eA).threePointArc(mB, eB)
           .lineTo(*end).lineTo(plate_x0 + 0.1, end[1]).close().extrude(-(tab_y1 - tab_y0)))
    tab = tab.cut(cq.Workplane("XZ", origin=(tab_hole_x, -1, tab_hole_z)).circle(tab_hole_r).extrude(-3))
    return cq.Workplane("XY").add(plate.union(tab).val().clean())
