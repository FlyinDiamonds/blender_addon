import bpy

from bpy.utils import register_class, unregister_class
from bpy.props import *
from .properties import (
    FD_SwarmAreaProps,
    FD_SwarmInitProps,
    FD_SwarmDistanceProps,
    FD_SwarmPlannerProps,
    FD_SwarmPlannerMapping,
    FD_SwarmSpeedProps,
    FD_SwarmPainterProps,
    FD_SelectGroupDrone,
    FD_SelectGroup,
    FD_SwarmRenderProps,
)

classes = [
    FD_SwarmAreaProps,
    FD_SwarmInitProps,
    FD_SwarmDistanceProps,
    FD_SwarmPlannerMapping,
    FD_SwarmPlannerProps,
    FD_SwarmSpeedProps,
    FD_SwarmPainterProps,
    FD_SelectGroupDrone,
    FD_SelectGroup,
    FD_SwarmRenderProps,
]

def select_group_callback(self, context):
    if self.fd_swarm_group_select_index >= 0:
        self.fd_swarm_group_select_drone_index = min(self.fd_swarm_group_select_drone_index, len(self.fd_swarm_group_select_list[self.fd_swarm_group_select_index].drones)-1)

def register():
    for cls in classes:
        register_class(cls)

    scene = bpy.types.Scene
    scene.fd_swarm_area_props = PointerProperty(type=FD_SwarmAreaProps)
    scene.fd_swarm_init_props = PointerProperty(type=FD_SwarmInitProps)
    scene.fd_swarm_distance_props = PointerProperty(type=FD_SwarmDistanceProps)
    scene.fd_swarm_planner_props = PointerProperty(type=FD_SwarmPlannerProps)
    scene.fd_swarm_speed_props = PointerProperty(type=FD_SwarmSpeedProps)
    scene.fd_swarm_painter_props = PointerProperty(type=FD_SwarmPainterProps)
    scene.fd_swarm_render_props = PointerProperty(type=FD_SwarmRenderProps)
    scene.fd_swarm_group_select_list = CollectionProperty(type=FD_SelectGroup)
    scene.fd_swarm_group_select_drone_index = bpy.props.IntProperty(default=-1)
    scene.fd_swarm_group_select_index = bpy.props.IntProperty(update=select_group_callback, default=-1)



def unregister():
    scene = bpy.types.Scene
    del scene.fd_swarm_painter_props
    del scene.fd_swarm_speed_props
    del scene.fd_swarm_planner_props
    del scene.fd_swarm_distance_props
    del scene.fd_swarm_init_props
    del scene.fd_swarm_area_props
    del scene.fd_swarm_render_props


    for cls in reversed(classes):
        unregister_class(cls)
