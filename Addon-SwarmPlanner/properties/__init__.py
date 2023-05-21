import bpy

from bpy.utils import register_class, unregister_class
from bpy.props import *
from .properties import FD_SwarmAreaProps

classes = [
    FD_SwarmAreaProps,
    ]

def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.fd_swarm_area_props = PointerProperty(type=FD_SwarmAreaProps)


def unregister():
    del bpy.types.Scene.fd_swarm_area_props
    
    for cls in reversed(classes):
        unregister_class(cls)
