import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatVectorProperty, EnumProperty, IntProperty, FloatProperty, PointerProperty


class FD_SwarmAreaProps(PropertyGroup):
    point0: FloatVectorProperty(name="Point 0", default=[-5, -5, 0])
    point1: FloatVectorProperty(name="Point 1", default=[20, 20, 20])


class FD_SwarmInitProps(PropertyGroup):
    cnt_x: IntProperty(name="X Count", default=2, min=1, max=100)
    cnt_y: IntProperty(name="Y Count", default=2, min=1, max=100)
    spacing: FloatProperty(name="Spacing", default=2.0, min=1.0, max=5.0)


class FD_SwarmDistanceProps(PropertyGroup):
    min_distance: FloatProperty(name="Mininal separation", default=1.0, min=0.1, max=10.0)


class FD_SwarmPlannerProps(PropertyGroup):
    min_distance: FloatProperty(name="Minimal distance", default=2.0, min=1.0, max=5.0)
    speed: FloatProperty(name="Drone speed", default=5.0, min=1.0, max=10.0)
    use_faces: BoolProperty(name="Use faces", default=False)


class FD_SwarmSpeedProps(PropertyGroup):
    max_speed_vertical: FloatProperty(name="Vertical max drone speed", default=5.0, min=1.0, max=10.0)
    max_speed_horizontal: FloatProperty(name="Horizontal max drone speed", default=5.0, min=1.0, max=10.0)


def fd_color_method_list_old(self, context):
    return (('0', 'Pallete', 'Color pallete', 'COLOR', 0),
            ('1', 'Picker', 'Color picker', 'EYEDROPPER', 1))

def fd_color_method_list(self, context):
    return (('0', 'Pallete', 'Color pallete', 'COLOR', 0),
            ('1', 'Picker', 'Color picker', 'EYEDROPPER', 1),
            ('2', 'Transition', 'Pick transition', 'EYEDROPPER', 2))


def fd_frame_method_list(self, context):
    return (('0', 'Duration', 'Start effect from current frame', 0),
            ('1', 'Range', 'Start effect from start frame', 1))


def fd_color_pallette_list(self, context):
    return (('0', 'WHITE', 'White color', 'SNAP_FACE', 0),
            ('1', 'BLACK', 'Black color', 'SEQUENCE_COLOR_09', 1),
            ('2', 'RED', 'Red color', 'SEQUENCE_COLOR_01', 2),
            ('3', 'GREEN', 'Green color', 'SEQUENCE_COLOR_04', 3),
            ('4', 'BLUE', 'Blue color', 'SEQUENCE_COLOR_05', 4))


def fd_select_method_list(self, context):
    return (('0', 'Selected', 'Selected drones', 'RESTRICT_SELECT_OFF', 0),
            ('1', 'In mesh', 'Select by object', 'MESH_MONKEY', 1),
            ('2', 'Random', 'Select random', 'TEXTURE', 2))


def fd_select_mesh_poll(self, object):
    return object.type == 'MESH' and not object.name.startswith("Drone")


class FD_SwarmColorProps(PropertyGroup):
    color_method_dropdown: EnumProperty(
        items=fd_color_method_list_old,
        name="Color method",
        default=0,
        description="Pick method for drone painting",
    )
    color_pallette: EnumProperty(
        items=fd_color_pallette_list,
        name="Color pallette",
        default=0,
        description="Pick color from color pallette",
    )
    color_picker: FloatVectorProperty(
             name = "Color Picker",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0, 1.0, 1.0, 1.0),
             size = 4
             )
    select_method_dropdown: EnumProperty(
        items=fd_select_method_list,
        name="Select method",
        default=0,
        description="Pick method for drone selection",
    )
    selected_mesh: PointerProperty(name="Select mesh", type=bpy.types.Object, poll=fd_select_mesh_poll)
    random_percentage: IntProperty(name="Percentage to select", default=50, min=1, max=100)
    invert_selection: BoolProperty(name="Invert selection", default=False)
    step_change: BoolProperty(name="Step change", default=True)


class FD_SwarmPainterProps(PropertyGroup):
    frame_method_dropdown: EnumProperty(
        items=fd_frame_method_list,
        name="Frame method",
        default=0,
        description="Pick method for animation frames",
    )
    color_method_dropdown: EnumProperty(
        items=fd_color_method_list,
        name="Color method",
        default=0,
        description="Pick method for drone painting",
    )
    color_pallette: EnumProperty(
        items=fd_color_pallette_list,
        name="Color pallette",
        default=0,
        description="Pick color from color pallette",
    )
    color_picker: FloatVectorProperty(
             name = "Color",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0, 1.0, 1.0, 1.0),
             size = 4
             )
    background_color_picker: FloatVectorProperty(
             name = "Background color",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (0.0, 0.0, 0.0, 1.0),
             size = 4
             )
    background_color: BoolProperty(name="Override background", default=True)
    select_method_dropdown: EnumProperty(
        items=fd_select_method_list,
        name="Select method",
        default=0,
        description="Pick method for drone selection",
    )
    selected_mesh: PointerProperty(name="Select mesh", type=bpy.types.Object, poll=fd_select_mesh_poll)
    random_percentage: IntProperty(name="Percentage to select", default=50, min=1, max=100)
    invert_selection: BoolProperty(name="Invert selection", default=False)
    step_change: BoolProperty(name="Step change", default=True)
    start_frame: IntProperty(name="Start frame", default=0, min=0)
    end_frame: IntProperty(name="End frame", default=100, min=1)
    frame_duration: IntProperty(name="Frame duration", default=10, min=0)