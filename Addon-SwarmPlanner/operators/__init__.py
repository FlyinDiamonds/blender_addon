import bpy

from .SwarmInit import SwarmInit, SwarmInitButton
from .SwarmPlanner import SwarmPlanner, SwarmPlannerButton
from .SwarmPlannerNew import SwarmPlannerNew
from .SwarmExporter import SwarmExporter
from .SwarmPainter import SwarmPainter, SwarmPainterButton
from .SwarmArea import SwarmArea, SwarmAreaButton
from .SwarmSpeed import SwarmSpeed, SwarmSpeedButton
from .SwarmDistance import SwarmDistance, SwarmDistanceButton
from .SwarmPainterOld import SwarmPainterOld, SwarmPainterButtonOld

menu_functions = []

menu_classes = (
    SwarmPlanner,
    SwarmInit,
    SwarmExporter,
    SwarmPainter,
    SwarmArea,
    SwarmSpeed,
    SwarmDistance,
    SwarmPainterOld,
    SwarmPlannerNew,
)

button_classes = (
    SwarmAreaButton,
    SwarmInitButton,
    SwarmDistanceButton,
    SwarmSpeedButton,
    SwarmPlannerButton,
    SwarmPainterButton,
    SwarmPainterButtonOld,
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

    for current_class in button_classes:
        bpy.utils.register_class(current_class)

def unregister():
    for cls in reversed(button_classes):
        bpy.utils.unregister_class(cls)
    for fun in menu_functions:
        bpy.types.VIEW3D_MT_object.remove(fun)
    for cls in menu_classes:
        print(cls.__name__)
        bpy.utils.unregister_class(cls)
