import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatVectorProperty, EnumProperty, IntProperty, FloatProperty, PointerProperty


class FD_SwarmAreaProps(PropertyGroup):
    point0: FloatVectorProperty(name="Point 0", default=[-5,-5,0])
    point1: FloatVectorProperty(name="Point 1", default=[20,20,20])


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


def fd_color_method_list(self, context):
    return (('0','Pallete','Color pallete'), ('1','Picker','Color picker'))

def fd_select_mesh_poll(self, object):
    return object.type == 'MESH'


class FD_SwarmColorProps(PropertyGroup):
    color_pallette: FloatProperty(name="Vertical max drone speed", default=5.0, min=1.0, max=10.0)
    color_picker: FloatVectorProperty(
             name = "Color Picker",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0,1.0,1.0,1.0),
             size = 4
             )
    color_method_dropdown: EnumProperty(
        items=(('0','Pallete','Color pallete'), ('1','Picker','Color picker')),
        name="Color method",
        default="0",
        description="Tooltip for the Dropdownbox",
    )
    select_method_dropdown: EnumProperty(
        items=(('0','Selected','Selected drones'), ('1','In mesh','Select by object'), ('2','Random','Select random')),
        name="Select method",
        default="0",
        description="Tooltip for the Dropdownbox",
    )
    invert_selection: BoolProperty(name="Invert selection", default=False)
    select_mesh: PointerProperty(type=bpy.types.Object, poll=fd_select_mesh_poll)
    random_percentage: IntProperty(name="Percentage", default=50, min=1, max=100)
    step_change: bpy.props.BoolProperty(name="Step change", default=True)
