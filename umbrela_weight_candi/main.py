import cadquery as cq
from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults

# We will be making weight for the umbrella holder in candi tirto
# the holder is composed of 3 discs, 3 foot and 1 central pole
# each of the disc has a hole as well
# we will be making a concrete filled 3d print that fit this umbrela holder


# Physical Constraints
height = 100
top_disc_dia = 50
mid_disc_dia = top_disc_dia
bottom_disc_dia = 100
pole_dia = 30
disc_thickness = 10
foot_width = 10
foot_clearance = 20

# Editable Variable
fillet_radius = 5

# Helpers
def truncated_cone(bottom_radius,top_radius,cone_height): 
        return (
            cq.Workplane()
            .circle(bottom_radius)
            .workplane(offset=cone_height)
            .circle(top_radius)
            .loft(combine=True))



cone = truncated_cone((bottom_disc_dia+foot_clearance)/2,(top_disc_dia+foot_clearance)/2,height)

bottom_disc = cq.Workplane().cylinder(
        disc_thickness
        ,bottom_disc_dia/2
).translate((0,0,foot_clearance/2))

central_pole = cq.Workplane().cylinder(
        height+1,
        pole_dia/2
).translate((0,0,(height/2)))

foot = cq.Workplane().box(bottom_disc_dia,foot_width,height+1).translate((bottom_disc_dia/2,0,height/2))

foot_cutters = [
    foot.rotate(
        (0, 0, 0),  # rotation origin
        (0, 0, 1),  # Z rotation axis
        angle
    )
    for angle in (0, 120, 240)
]

main = cone - bottom_disc - central_pole

for cutter in foot_cutters:
        main = main - cutter

umbrela_weights = main.solids().vals()
one_weight = (
    cq.Workplane("XY")
    .newObject([umbrela_weights[0]])
)

show(umbrela_weights)