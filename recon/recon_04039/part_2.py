"""
Reconstruction of 30297_fd93a92a_0016_1 (joint_set_04039, body two): a knob/handle.
Written from the B-Rep graph JSON (7 faces: 3 planes, 2 cylinders, 2 tori, all coaxial on +X).

  bore_radius   0.39751   screw bore along the axis (face 0), depth bore_depth (floor = face 1)
  neck_radius   0.71374   short cylindrical neck at x in [0, neck_length] (face 2)
  waist         (1.5875, 1.22428) where the two torus surfaces meet (edge 11)
  waist_arc_r   2.052388  concave arc from neck to waist (face 3, torus)
  belly_arc_r   2.106098  convex arc from waist to tip (face 4, torus); max radius 1.46912
  tip_radius    0.5969    flat end at x = length (face 5)
Units: cm.
"""
import math
import cadquery as cq

PARAMS = {"bore_radius": 0.39751, "bore_depth": 2.54, "neck_radius": 0.71374, "neck_length": 0.635,
          "waist_x": 1.5875, "waist_r": 1.22428, "waist_arc_r": 2.052388242468349,
          "belly_arc_r": 2.106098255765155, "length": 4.2799, "tip_radius": 0.5969}


def _arc_mid(a, b, radius, bulge_toward_axis):
    """Midpoint of the circular arc of given radius from a to b (profile plane, y = radial)."""
    ax, ay = a; bx, by = b
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax, by - ay
    half = math.hypot(dx, dy) / 2
    h = math.sqrt(max(radius * radius - half * half, 0.0))
    nx, ny = -dy / math.hypot(dx, dy), dx / math.hypot(dx, dy)   # unit normal to chord
    # centre is on the side away from the bulge
    sign = 1 if (bulge_toward_axis and ny > 0) or (not bulge_toward_axis and ny < 0) else -1
    cx, cy = mx + sign * h * nx, my + sign * h * ny
    ux, uy = mx - cx, my - cy
    n = math.hypot(ux, uy)
    return (cx + radius * ux / n, cy + radius * uy / n)


def build(bore_radius, bore_depth, neck_radius, neck_length, waist_x, waist_r,
          waist_arc_r, belly_arc_r, length, tip_radius):
    neck_end = (neck_length, neck_radius)
    waist = (waist_x, waist_r)
    tip = (length, tip_radius)
    m1 = _arc_mid(neck_end, waist, waist_arc_r, bulge_toward_axis=True)
    m2 = _arc_mid(waist, tip, belly_arc_r, bulge_toward_axis=False)
    # profile in the (x, r) half-plane, revolved about the X axis
    wp = (cq.Workplane("XY").moveTo(0, bore_radius).lineTo(0, neck_radius).lineTo(*neck_end)
          .threePointArc(m1, waist).threePointArc(m2, tip).lineTo(length, 0)
          .lineTo(bore_depth, 0).lineTo(bore_depth, bore_radius).close())
    return wp.revolve(360, (0, 0, 0), (1, 0, 0))
