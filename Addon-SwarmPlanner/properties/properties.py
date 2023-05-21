import bpy

from bpy.types import PropertyGroup
from bpy.props import FloatVectorProperty


class FD_SwarmAreaProps(PropertyGroup):
    point0: FloatVectorProperty(name="Point 0", default=[-5,-5,0])
    point1: FloatVectorProperty(name="Point 1", default=[20,20,20])
