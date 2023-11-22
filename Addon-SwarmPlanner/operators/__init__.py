import bpy

from .SwarmInit import SwarmInit
from .SwarmPlanner import SwarmPlanner
from .SwarmExporter import SwarmExporter
from .SwarmPainter import SwarmPainter
from .SwarmArea import SwarmArea
from .SwarmSpeed import SwarmSpeed
from .SwarmDistance import SwarmDistance

menu_functions = []

menu_classes = (
    SwarmPlanner,
    SwarmInit,
    SwarmExporter,
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
    for cls in menu_classes:
        bpy.utils.register_class(cls)
        menu_functions.append(get_menu_func(cls))
        bpy.types.VIEW3D_MT_object.append(menu_functions[-1])

def unregister():
    for fun in menu_functions:
        bpy.types.VIEW3D_MT_object.remove(fun)
    for cls in menu_classes:
        print(cls.__name__)
        bpy.utils.unregister_class(cls)
