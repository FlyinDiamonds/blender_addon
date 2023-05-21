import bpy

from bpy.types import PropertyGroup
from bpy.props import FloatVectorProperty


class FD_SwarmAreaProps(PropertyGroup):
    point0: FloatVectorProperty(name="Point 0", default=[-5,-5,0])
    point1: FloatVectorProperty(name="Point 1", default=[20,20,20])


class FD_SwarmInitProps(PropertyGroup):
    cnt_x: bpy.props.IntProperty(name="X Count", default=2, min=1, max=100)
    cnt_y: bpy.props.IntProperty(name="Y Count", default=2, min=1, max=100)
    spacing: bpy.props.FloatProperty(name="Spacing", default=2.0, min=1.0, max=5.0)


class FD_SwarmDistanceProps(PropertyGroup):
    min_distance: bpy.props.FloatProperty(name="Mininal separation", default=1.0, min=0.1, max=10.0)


class FD_SwarmPlannerProps(PropertyGroup):
    min_distance: bpy.props.FloatProperty(name="Minimal distance", default=2.0, min=1.0, max=5.0)
    speed: bpy.props.FloatProperty(name="Drone speed", default=5.0, min=1.0, max=10.0)
    use_faces: bpy.props.BoolProperty(name="Use faces", default=False)


class FD_SwarmSpeedProps(PropertyGroup):
    max_speed: bpy.props.FloatProperty(name="Max drone speed", default=5.0, min=1.0, max=10.0)
