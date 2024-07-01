import bpy

from .SwarmInit import SwarmInit, SwarmLand
from .SwarmPlanner import SwarmPlanner
from .SwarmExporter import SwarmExporter
from .SwarmPainter import SwarmPainter
from .SwarmArea import SwarmArea
from .SwarmSpeed import SwarmSpeed
from .SwarmDistance import SwarmDistance
from .SwarmRender import SwarmRender
from .ui_lists_operators import UIListOperatorAdd, UIListOperatorRemove, UIListOperatorMove, UIListOperatorAddSelected, UIListOperatorRemoveSelected, UIListOperatorSelect, UIListOperatorDeselect, FD_UL_groups, FD_UL_drones

ul_lists = [
    FD_UL_groups,
    FD_UL_drones,
]


menu_functions = []

menu_classes = (
    UIListOperatorAdd,
    UIListOperatorRemove,
    UIListOperatorMove,
    UIListOperatorAddSelected,
    UIListOperatorRemoveSelected,
    UIListOperatorSelect,
    UIListOperatorDeselect,
    SwarmPlanner,
    SwarmInit,
    SwarmLand,
    SwarmExporter,
    SwarmRender,
    SwarmPainter,
    SwarmArea,
    SwarmSpeed,
    SwarmDistance,
)


def get_menu_func(cls):
    def fun(self, context):
        return self.layout.operator(cls.bl_idname)
    return fun


def register():
    for cls in ul_lists:
        bpy.utils.register_class(cls)

    for cls in menu_classes:
        bpy.utils.register_class(cls)
        menu_functions.append(get_menu_func(cls))
        bpy.types.VIEW3D_MT_object.append(menu_functions[-1])

def unregister():
    for cls in reversed(ul_lists):
        bpy.utils.unregister_class(cls)

    for fun in reversed(menu_functions):
        bpy.types.VIEW3D_MT_object.remove(fun)
    for cls in reversed(menu_classes):
        bpy.utils.unregister_class(cls)
