import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatVectorProperty, EnumProperty, IntProperty, FloatProperty, StringProperty, PointerProperty, CollectionProperty


class FD_SwarmAreaProps(PropertyGroup):
    point0: FloatVectorProperty(name="Point 0", default=[-5, -5, 0])
    point1: FloatVectorProperty(name="Point 1", default=[20, 20, 20])


class FD_SwarmInitProps(PropertyGroup):
    cnt_x: IntProperty(name="X Count", default=2, min=1, max=100)
    cnt_y: IntProperty(name="Y Count", default=2, min=1, max=100)
    spacing: FloatProperty(name="Spacing", default=2.0, min=1.0, max=5.0)


class FD_SwarmDistanceProps(PropertyGroup):
    min_distance: FloatProperty(name="Mininal separation", default=1.0, min=0.1, max=10.0)


class FD_SwarmSpeedProps(PropertyGroup):
    max_speed_vertical: FloatProperty(name="Vertical max drone speed", default=5.0, min=1.0, max=10.0)
    max_speed_horizontal: FloatProperty(name="Horizontal max drone speed", default=5.0, min=1.0, max=10.0)


def fd_color_method_list(self, context):
    return (('0', 'Pallete', 'Color pallete', 'COLOR', 0),
            ('1', 'Picker', 'Color picker', 'EYEDROPPER', 1),
            ('2', 'Transition', 'Pick transition', 'COLORSET_07_VEC', 2))


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
            ('2', 'Random', 'Select random', 'TEXTURE', 2),
            ('3', 'Group', 'Select by group', 'GROUP_VERTEX', 3))

def fd_select_method_planner_list(self, context):
    return (('0', 'All', 'All drones', 'LIGHTPROBE_GRID', 0),
            ('1', 'Selected', 'Selected drones', 'RESTRICT_SELECT_OFF', 1),
            ('2', 'Group', 'Select by group', 'GROUP_VERTEX', 2))

def fd_planner_method_list(self, context):
    return (('0', 'Check colissions', 'Check drone colissions', 'MOD_PHYSICS', 0),
            ('1', 'Same mesh', 'Plan transition to same mesh', 'MESH_MONKEY', 1))

def fd_plan_to_list(self, context):
    return (('0', 'Vertices', 'Map drones to vertices', 'VERTEXSEL', 0),
            ('1', 'Faces', 'Map drones to faces', 'FACESEL', 1))


def fd_select_mesh_poll(self, obj):
    return obj.type == 'MESH' and not obj.name.startswith("Drone")

def fd_drone_poll(self, obj):
    return obj.type == 'MESH' and obj.name.startswith("Drone")


class FD_SwarmPlannerMapping(PropertyGroup):
    drone_name: StringProperty(name="Drone name")
    drone_index: IntProperty(name="Drone index", default=-1)
    target_index: IntProperty(name="Vertex/edge/face index", default=-1)


class FD_SwarmPlannerProps(PropertyGroup):
    min_distance: FloatProperty(name="Minimal distance", default=2.0, min=1.0, max=5.0)
    speed: FloatProperty(name="Drone speed", default=5.0, min=1.0, max=10.0)
    planner_method: EnumProperty(
        items=fd_planner_method_list,
        name="Method",
        default=0,
        description="Pick method for planning transition",
    )
    plan_to_dropdown: EnumProperty(
        items=fd_plan_to_list,
        name="Plan to",
        default=0,
        description="Pick entity to plan transitions to",
    )
    select_method_dropdown: EnumProperty(
        items=fd_select_method_planner_list,
        name="Select method",
        default=0,
        description="Pick method for drone selection",
    )
    selected_mesh: PointerProperty(name="Select mesh", type=bpy.types.Object, poll=fd_select_mesh_poll)
    prev_selected_mesh: PointerProperty(name="Prev selected mesh", type=bpy.types.Object, poll=fd_select_mesh_poll)
    prev_plan_to_index: IntProperty(name="Index of prev plan to enum", default=-1)
    drone_mapping: CollectionProperty(type=FD_SwarmPlannerMapping)


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
    override_background: BoolProperty(name="Override background", default=True)
    select_method_dropdown: EnumProperty(
        items=fd_select_method_list,
        name="Select method",
        default=0,
        description="Pick method for drone selection",
    )
    selected_mesh: PointerProperty(name="Select mesh", type=bpy.types.Object, poll=fd_select_mesh_poll)
    random_percentage: IntProperty(name="Percentage to select", default=50, min=1, max=100)
    invert_selection: BoolProperty(name="Invert selection", default=False)
    keep_colors: BoolProperty(name="Keep last color", default=True)
    start_frame: IntProperty(name="Start frame", default=0, min=0)
    end_frame: IntProperty(name="End frame", default=100, min=1)
    frame_duration: IntProperty(name="Frame duration", default=10, min=0, max=1000)
    frame_step: IntProperty(name="Frame step", default=1, min=1, max=100)
    transition_color_picker: FloatVectorProperty(
             name = "Transition from",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0, 1.0, 1.0, 1.0),
             size = 4
    )
    transition_color_picker_snd: FloatVectorProperty(
             name = "Transition to",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0, 1.0, 1.0, 1.0),
             size = 4
    )

class FD_SelectGroupDrone(bpy.types.PropertyGroup):
    drone: PointerProperty(type=bpy.types.Object, poll=fd_drone_poll)

class FD_SelectGroup(bpy.types.PropertyGroup):
    name: StringProperty()
    drones: CollectionProperty(type=FD_SelectGroupDrone)


class FD_SwarmRenderProps(PropertyGroup):
    camera_name: StringProperty(name="Camera")
    start: IntProperty(name="Start", default=1)
    end: IntProperty(name="End", default=100)