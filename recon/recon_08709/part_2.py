"""29947_0f21f39e_0019_2 (joint_set_08709, body two): a slotted lug bracket with a chamfered pin.
Plate 1.3 thick (x 0..1.3) in the YZ plane: left edge y=21 (z 83..85.1), quarter round r=1.1 to the top z=86.2, top to y=25.6,
a 174.886-degree round end r=1.1 about (25.6, 85.1) starting 1.23 deg past the top (the original sketch is slightly off-tangent), bottom line back to y=23.7, concave fillet r=0.5
about (23.7, 83.5) down to (23.2, 83.5), step to z=83 and back to y=21.  Two r=0.4 holes along X at (22.1, 85.1) and (25.6, 85.1).
A slot 0.5 wide (x 0.4..0.9) from y=24.5002 through the round end.  A pin r=0.591675 along Z at (x=0.65, y=22.10006), z 77.9..83,
with a 45-degree chamfer 0.091675 at its free end."""
import math, cadquery as cq
PARAMS = {"thickness": 1.3, "left_y": 21.0, "bottom_z": 83.0, "hole_y1": 22.1, "hole_y2": 25.6, "hole_z": 85.1, "end_radius": 1.1, "hole_radius": 0.4,
          "end_arc_deg": 174.886, "end_arc_start_deg": 88.77, "foot_y": 23.7, "foot_z": 84.0, "fillet_radius": 0.5, "slot_x0": 0.4, "slot_width": 0.5, "slot_start_y": 24.5002,
          "pin_x": 0.65, "pin_y": 22.10006, "pin_tip_z": 77.9, "pin_radius": 0.591675, "pin_chamfer": 0.091675}
def build(thickness, left_y, bottom_z, hole_y1, hole_y2, hole_z, end_radius, hole_radius, end_arc_deg, end_arc_start_deg, foot_y, foot_z, fillet_radius,
          slot_x0, slot_width, slot_start_y, pin_x, pin_y, pin_tip_z, pin_radius, pin_chamfer):
    top_z = hole_z + end_radius; half = math.radians(end_arc_deg / 2)
    start_pt = (hole_y2 + end_radius * math.cos(half), hole_z + end_radius * math.sin(half))      # arc symmetric about the +Y direction
    end_pt = (hole_y2 + end_radius * math.cos(-half), hole_z + end_radius * math.sin(-half)); mid_pt = (hole_y2 + end_radius, hole_z)
    k = math.sqrt(0.5)
    prof = (cq.Workplane("YZ").moveTo(left_y, bottom_z).lineTo(left_y, hole_z)
            .threePointArc((hole_y1 - end_radius * k, hole_z + end_radius * k), (hole_y1, top_z)).lineTo(*start_pt)
            .threePointArc(mid_pt, end_pt).lineTo(foot_y, foot_z)
            .threePointArc((foot_y - fillet_radius * k, foot_z - fillet_radius + fillet_radius * k), (foot_y - fillet_radius, foot_z - fillet_radius))
            .lineTo(foot_y - fillet_radius, bottom_z).close())
    plate = prof.extrude(thickness)
    for y in (hole_y1, hole_y2):
        plate = plate.cut(cq.Workplane("YZ", origin=(-1, y, hole_z)).circle(hole_radius).extrude(thickness + 2))
    slot = cq.Workplane("XY").box(slot_width, 5.0, 5.0, centered=(False, False, False)).translate((slot_x0, slot_start_y, foot_z - 1.5))
    plate = plate.cut(slot)
    pin = (cq.Workplane("XY", origin=(pin_x, pin_y, pin_tip_z)).circle(pin_radius).extrude(bottom_z - pin_tip_z + 0.01)
           .faces("<Z").chamfer(pin_chamfer))
    return plate.union(pin)

