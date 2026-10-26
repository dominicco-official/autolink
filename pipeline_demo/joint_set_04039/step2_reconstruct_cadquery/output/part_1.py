"""
Reconstruction of 30297_fd93a92a_0015_1 (joint_set_04039, body one): a cap.
Written from the B-Rep graph JSON (6 faces: 3 planes, 3 cylinders, all coaxial on +Y).

  hole_radius  0.39751  through-hole in the floor (face 0)
  bore_radius  0.714375 inner bore that slides over the knob neck (face 1)
  wall         0.079375 outer_radius - bore_radius  (outer = 0.79375, face 3)
  floor        0.079375 floor thickness (step plane at y=floor, face 2)
  height       0.71374  overall height (top rim plane, face 4)
Units: cm.
"""
import cadquery as cq

PARAMS = {"hole_radius": 0.39751, "bore_radius": 0.714375, "wall": 0.079375,
          "floor": 0.079375, "height": 0.71374}


def build(hole_radius, bore_radius, wall, floor, height):
    outer = bore_radius + wall
    # profile in the (r, y) half-plane, revolved about the Y axis
    pts = [(hole_radius, 0), (outer, 0), (outer, height), (bore_radius, height),
           (bore_radius, floor), (hole_radius, floor)]
    return cq.Workplane("XY").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
