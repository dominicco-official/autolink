"""137295_a2385b57_0000_2 (joint_set_13082, body two): a plug with a rounded head and a through bore, axis Z.
Read from the 9-face graph: shaft cylinder r=2.5 (height 2.5), through-bore r=1.82631, head disc r=4.5 with a
full half-round rim (torus, tube r=0.5 -> max r=5.0), head top plane, concave fillet r=0.5 into a boss cylinder
r=2.5 (height 0.5), top annulus. Dataset position: axis through (0, -0.035366), bottom at z=-0.130697."""
import math, cadquery as cq

ORIGIN = (0.0, -0.035366, -0.130697)
PARAMS = {"bore_radius": 1.82631, "shaft_radius": 2.5, "shaft_height": 2.5, "head_radius": 4.5, "rim_radius": 0.5,
          "boss_fillet": 0.5, "boss_radius": 2.5, "boss_height": 0.5}

def build(bore_radius, shaft_radius, shaft_height, head_radius, rim_radius, boss_fillet, boss_radius, boss_height):
    b, r, h, R, t, f, rb, hb = bore_radius, shaft_radius, shaft_height, head_radius, rim_radius, boss_fillet, boss_radius, boss_height
    z_head = h; z_top = h + 2 * t                       # head underside / top
    k = 1 / math.sqrt(2)
    wp = (cq.Workplane("XZ").moveTo(b, 0).lineTo(r, 0).lineTo(r, z_head).lineTo(R, z_head)
          .threePointArc((R + t, z_head + t), (R, z_top))                       # half-round rim
          .lineTo(rb + f, z_top)
          .threePointArc((rb + f - f * k, z_top + f - f * k), (rb, z_top + f))  # concave fillet into the boss
          .lineTo(rb, z_top + f + hb).lineTo(b, z_top + f + hb).close())
    return wp.revolve(360, (0, 0, 0), (0, 1, 0)).translate(ORIGIN)
