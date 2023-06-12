import bpy

from bpy.utils import register_class, unregister_class
from bpy.props import *
from .properties import (
    FD_SwarmAreaProps,
    FD_SwarmInitProps,
    FD_SwarmDistanceProps,
    FD_SwarmPlannerProps,
    FD_SwarmSpeedProps,
    FD_SwarmColorProps,
    FD_SwarmPainterProps,
)

classes = [
    FD_SwarmAreaProps,
    FD_SwarmInitProps,
    FD_SwarmDistanceProps,
    FD_SwarmPlannerProps,
    FD_SwarmSpeedProps,
    FD_SwarmColorProps,
    FD_SwarmPainterProps,
]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.fd_swarm_area_props = PointerProperty(type=FD_SwarmAreaProps)
    bpy.types.Scene.fd_swarm_init_props = PointerProperty(type=FD_SwarmInitProps)
    bpy.types.Scene.fd_swarm_distance_props = PointerProperty(type=FD_SwarmDistanceProps)
    bpy.types.Scene.fd_swarm_planner_props = PointerProperty(type=FD_SwarmPlannerProps)
    bpy.types.Scene.fd_swarm_speed_props = PointerProperty(type=FD_SwarmSpeedProps)
    bpy.types.Scene.fd_swarm_color_props = PointerProperty(type=FD_SwarmColorProps)
    bpy.types.Scene.fd_swarm_painter_props = PointerProperty(type=FD_SwarmPainterProps)


def unregister():
    del bpy.types.Scene.fd_swarm_painter_props
    del bpy.types.Scene.fd_swarm_color_props
    del bpy.types.Scene.fd_swarm_speed_props
    del bpy.types.Scene.fd_swarm_planner_props
    del bpy.types.Scene.fd_swarm_distance_props
    del bpy.types.Scene.fd_swarm_init_props
    del bpy.types.Scene.fd_swarm_area_props


    for cls in reversed(classes):
        unregister_class(cls)
