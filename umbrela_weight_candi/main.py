import cadquery as cq
from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults

# Physical Constraints
height = 100
top_disc_dia = 50
mid_disc_dia = top_disc_dia
bottom_disc_dia = 100
pole_dia = 15
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
).translate((0,0,foot_clearance))

central_pole = cq.Workplane().cylinder(
        height,
        pole_dia/2
).translate((0,0,(height/2)+1))

# foot = cq.Workplane().box()

main = cone - bottom_disc - central_pole


show(main)
 