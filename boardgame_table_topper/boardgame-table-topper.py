# CadQuery
import cadquery as cq
from ocp_vscode import show
import math
from cadquery import exporters
from pathlib import Path

# Notes
# 4 layer design
# L1 is the base
# L2 is the spacer
# L3 extra spacer
# L4 is the handrest

# L1 is 1200 x 2000, play area of 1000 x 1800
# i think its possible to make a table with 2 18mm triplex. 
# if we use simple ass screw to make them we can make it really easy to assemble
# the spacer is going to be around 5 cm on the with edges on the inside so it can be used as a handle.
# saw online that the depth of a random board game table is 3 inches which is around 80 mm

# Coordinate convention:
# X = table length
# Y = table width
# Z = vertical height

# Parameter
material_thickness = 18

#length = the longest side
table_length = 1600
table_width = 1000

handrest_width = 100
finger_space = 40

screw_hole_diameter = 5

max_screw_spacing = 200

screw_insert_depth = 12
screw_insert_diameter = 6 # the necessary diameter to let wood insert bite in.

fillet_radius = 5
screwhead_depth = 5 # counter bore

# Derived Dimensions
spacer_width = handrest_width - finger_space
screw_edge_offset = spacer_width


vault_length = table_length - handrest_width * 2
vault_width = table_width - handrest_width * 2

side_spacer_length = table_length
end_spacer_length = vault_width 

# Hardware Dimensions
side_handrest_length = vault_length
end_handrest_length = table_width

# Assembly Offset

handrest_y_pos = table_width/2 - handrest_width/2
handrest_x_pos = table_length/2 - handrest_width/2

spacer_y_pos = table_width / 2 - finger_space - spacer_width / 2
spacer_x_pos = table_length / 2 - finger_space - spacer_width / 2

# Layers
layer_1 = 0
layer_2 = material_thickness
layer_3 = material_thickness * 2
layer_4 = material_thickness * 3


# Helper Functions

def loc (x,y,z):
    return cq.Location(cq.Vector(x,y,z))

def add_part (assembly, part, name, x,y,z, color):
    assembly.add(
        part,
        name=name,
        loc=loc(x,y,z),
        color = color
    )

def add_x_pair(assembly, part, name, x,y,z, color):
    add_part(assembly, part, f"{name} +X", x, y, z, color)
    add_part(assembly, part, f"{name} -X", -x, y, z, color)

def add_y_pair(assembly, part, name, x,y,z, color):
    add_part(assembly, part, f"{name} +Y", x, y, z, color)
    add_part(assembly, part, f"{name} -Y", x, -y, z, color)

def points_along_length (length, edge_offset, max_spacing):
    usable_length = length - edge_offset * 2

    if usable_length <= 0:
        return [0]
    
    gap_count = max (1,math.ceil(usable_length/max_spacing))
    spacing = usable_length / gap_count
    start = -length / 2 + edge_offset

    return [
        start + i * spacing
        for i in range(gap_count+1)
    ]
    
def part_hole_from_global_axes (global_points, part_x, part_y, part_x_size, part_y_size, clearance=0):
    local_points = []

    for gx, gy in global_points:
        lx = gx - part_x
        ly = gy - part_y

        inside_x = abs(lx) <= part_x_size/2 - clearance
        inside_y = abs(ly) <= part_y_size/2 - clearance

        if inside_x and inside_y:
            local_points.append((lx,ly))

    return local_points

# this cuts from the bottom, and affect the placement of the side hole apparently. so that way positive and negateive has been flipped for side hole
def hole_cutter (part, hole_points, hole_diameter, hole_depth=None):
    return(
        part
        .faces("<Z")
        .workplane()
        .pushPoints(hole_points)
        .hole(hole_diameter, depth=hole_depth)
    )

# Geometry
base = (cq.Workplane().box(
    table_length,
    table_width,
    material_thickness)
    .edges("|Z").fillet(fillet_radius)
    )

side_spacer = (cq.Workplane().box(
    side_spacer_length,
    spacer_width,
    material_thickness)
    .edges("|Z").fillet(fillet_radius)
    )

end_spacer = (cq.Workplane().box(
    spacer_width,
    end_spacer_length,
    material_thickness)
    .edges("|Z").fillet(fillet_radius)
    )

side_handrest_pos = (cq.Workplane().box(
    side_handrest_length,
    handrest_width,
    material_thickness)
    .edges("|Z").fillet(fillet_radius)
    )

side_handrest_neg = (cq.Workplane().box(
    side_handrest_length,
    handrest_width,
    material_thickness)
    .edges("|Z").fillet(fillet_radius)
)

end_handrest_pos = (cq.Workplane().box(
    handrest_width,
    end_handrest_length,
    material_thickness)
    .edges("|Z").fillet(fillet_radius)
)

end_handrest_neg = (cq.Workplane().box(
    handrest_width,
    end_handrest_length,
    material_thickness)
    .edges("|Z").fillet(fillet_radius)
)
# Global screw hole points

side_screw_xs = (points_along_length(
    side_spacer_length,
    finger_space+spacer_width/2,
    max_screw_spacing
))

end_screw_ys = (points_along_length(
    end_spacer_length,
    screw_edge_offset,
    max_screw_spacing
))

screw_points = []

#Points for side +y
screw_points += [
    (x, spacer_y_pos)
    for x in side_screw_xs
]

#Points for side -y
screw_points += [
    (x, -spacer_y_pos)
    for x in side_screw_xs
]

#Points for end +x
screw_points += [
    (spacer_x_pos, y)
    for y in end_screw_ys
]

#Points for end -x
screw_points += [
    (-spacer_x_pos,y)
    for y in end_screw_ys
]


# Define local holes
base_hole_points = part_hole_from_global_axes ( 
    screw_points,
    part_x=0,
    part_y=0,
    part_x_size=table_length,
    part_y_size=table_width,
    clearance=screw_hole_diameter
)

side_spacer_hole_points = part_hole_from_global_axes (
    screw_points,
    part_x=0,
    part_y=spacer_y_pos,
    part_x_size=side_spacer_length,
    part_y_size=spacer_width,
    clearance=screw_hole_diameter
)

end_spacer_hole_points = part_hole_from_global_axes (
    screw_points,
    part_x=spacer_x_pos,
    part_y=0,
    part_x_size=spacer_width,
    part_y_size=end_spacer_length,
    clearance=screw_hole_diameter
)

side_handrest_pos_hole_points = part_hole_from_global_axes(
    screw_points,
    part_x=0,
    part_y=-handrest_y_pos,
    part_x_size=side_handrest_length,
    part_y_size=handrest_width,
    clearance=screw_hole_diameter
)

side_handrest_neg_hole_points = part_hole_from_global_axes(
    screw_points,
    part_x=0,
    part_y=handrest_y_pos,
    part_x_size=side_handrest_length,
    part_y_size=handrest_width,
    clearance=screw_hole_diameter
)

end_handrest_pos_holes = part_hole_from_global_axes(
    screw_points,
    part_x=handrest_x_pos,
    part_y=0,
    part_x_size=handrest_width,
    part_y_size=end_handrest_length,
    clearance=screw_hole_diameter
)

end_handrest_neg_holes = part_hole_from_global_axes(
    screw_points,
    part_x=-handrest_x_pos,
    part_y=0,
    part_x_size=handrest_width,
    part_y_size=end_handrest_length,
    clearance=screw_hole_diameter
)

# Cut holes

base = hole_cutter(
    base,
    base_hole_points,
    screw_hole_diameter,
    hole_depth=material_thickness
    )

side_spacer = hole_cutter(
    side_spacer,
    side_spacer_hole_points,
    screw_hole_diameter,
    hole_depth=material_thickness
)

end_spacer = hole_cutter(
    end_spacer,
    end_spacer_hole_points,
    screw_hole_diameter,
    hole_depth=material_thickness
)

# Handrest threaded insert hole

side_handrest_pos = hole_cutter(
    side_handrest_pos,
    side_handrest_pos_hole_points,
    screw_insert_diameter,
    hole_depth=screw_insert_depth
)

side_handrest_neg = hole_cutter(
    side_handrest_neg,
    side_handrest_neg_hole_points,
    screw_insert_diameter,
    hole_depth=screw_insert_depth
)

end_handrest_pos = hole_cutter(
    end_handrest_pos,
    end_handrest_pos_holes,
    screw_insert_diameter,
    hole_depth=screw_insert_depth
)

end_handrest_neg = hole_cutter(
    end_handrest_neg,
    end_handrest_neg_holes,
    screw_insert_diameter,
    hole_depth=screw_insert_depth
)

# Base screw head counterbore

base = hole_cutter(
    base,
    base_hole_points,
    screwhead_depth,
    hole_depth=screwhead_depth
    )

# Assembly

assm = cq.Assembly()

add_part(
    assm,
    base,
    "Base",
    0,0,layer_1,
    cq.Color(0.8,0.8,0.8)
)

add_y_pair(
    assm,
    side_spacer,
    "Side Spacer 1",
    0,spacer_y_pos,layer_2,
    cq.Color(1,0,0)
)

add_x_pair(
    assm,
    end_spacer,
    "End Spacer 1",
    spacer_x_pos,0,layer_2,
    cq.Color(0,0,1)
)

add_y_pair(
    assm,
    side_spacer,
    "Side Spacer 2",
    0,spacer_y_pos,layer_3,
    cq.Color(1,0,0)
)

add_x_pair(
    assm,
    end_spacer,
    "End Spacer 2",
    spacer_x_pos,0,layer_3,
    cq.Color(0,0,1)
)

add_part(
    assm,
    side_handrest_pos,
    "Side Handrest +Y",
    0,
    handrest_y_pos,
    layer_4,
    cq.Color(1,1,0)
)

add_part(
    assm,
    side_handrest_neg,
    "Side Handrest -Y",
    0,
    -handrest_y_pos,
    layer_4,
    cq.Color(1,1,0)
)

add_part(
    assm,
    end_handrest_pos,
    "End Handrest +X",
    handrest_x_pos,
    0,
    layer_4,
    cq.Color(0,1,1)
)

add_part(
    assm,
    end_handrest_neg,
    "End Handrest -X",
    -handrest_x_pos,
    0,
    layer_4,
    cq.Color(0,1,1)
)

show(assm)

# Export DXF

script_dir = Path(__file__).resolve().parent
export_dir = script_dir / "exports" / f"Ukuran {table_length}x{table_width}mm"
export_dir.mkdir(exist_ok=True)

## Helper for export

# Sanitizer
def slug(text):
    return text.lower().replace(" ","_").replace("+","pos").replace("-","neg")


def export_face_to_dxf (part,index, name, qty, x_size, y_size, thickness=material_thickness, face="<Z"):
    filename = f"{index:02d}_{slug(name)}_{qty}pcs_{x_size}x{y_size}x{thickness}mm.dxf"
    exporters.export(
        part.faces(face).val(),
        str(export_dir / filename)
    )

# Export Table

dxf_exports = [
    {
        "name" : "Base",
        "part" : base,
        "qty" : 1,
        "x_size" : table_length,
        "y_size" : table_width
    },
    {
        "name" : "side spacer",
        "part" : side_spacer,
        "qty" : 4,
        "x_size" : side_spacer_length,
        "y_size" : spacer_width
    },
    {
        "name" : "end spacer",
        "part" : end_spacer,
        "qty" : 4,
        "x_size" : spacer_width,
        "y_size" : end_spacer_length
    },
    {
        "name" : "side handrest pos",
        "part" : side_handrest_pos,
        "qty" : 1,
        "x_size" : side_handrest_length,
        "y_size" : handrest_width
    },
    {
        "name" : "side handrest neg",
        "part" : side_handrest_neg,
        "qty" : 1,
        "x_size" : side_handrest_length,
        "y_size" : handrest_width
    },
    {
        "name" : "end handrest pos",
        "part" : end_handrest_pos,
        "qty" : 1,
        "x_size" : handrest_width,
        "y_size" : end_handrest_length
    },
    {
        "name" : "end handrest neg",
        "part" : end_handrest_neg,
        "qty" : 1,
        "x_size" : handrest_width,
        "y_size" : end_handrest_length
    }
]

for index,item in enumerate(dxf_exports,start=1):
    export_face_to_dxf(
        index=index,
        part=item["part"],
        name=item["name"],
        qty=item["qty"],
        x_size=item["x_size"],
        y_size=item["y_size"],
        thickness=material_thickness,
        face="<Z"
    )

# Instruksi Potong

notes = f"""
INSTRUKSI POTONG CNC

Material: plywood/triplek {material_thickness} mm
Satuan: mm

Potong semua part sesuai file DXF.

Jumlah dan ukuran:
- Base: {table_length} x {table_width} mm — 1 pcs
- Side Spacer: {side_spacer_length} x {spacer_width} mm — 4 pcs
- End Spacer: {spacer_width} x {end_spacer_length} mm — 4 pcs
- Side Handrest: {side_handrest_length} x {handrest_width} mm — 2 pcs
- End Handrest: {handrest_width} x {end_handrest_length} mm — 2 pcs

Lubang:
- Lubang tembus: Ø{screw_hole_diameter} mm
- Lubang setengah pada handrest: kedalaman {screw_insert_depth} mm dari sisi bawah
- Jangan tembuskan lubang setengah sampai sisi atas handrest

Jangan resize / scale file DXF.
"""

(export_dir / "instruksi_potong_cnc.txt").write_text(
    notes.strip(),
    encoding="utf-8"
)