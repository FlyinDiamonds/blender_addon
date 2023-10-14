import bpy

from .SwarmInit import SwarmInit
from .SwarmPlanner import SwarmPlanner, SwarmPlannerButton
from .SwarmExporter import SwarmExporter
from .SwarmPainter import SwarmPainter, SwarmPainterButton
from .SwarmArea import SwarmArea, SwarmAreaButton
from .SwarmSpeed import SwarmSpeed, SwarmSpeedButton
from .SwarmDistance import SwarmDistance, SwarmDistanceButton


menu_classes = (
    SwarmPlanner,
    SwarmInit,
    SwarmExporter,
    SwarmPainter,
    SwarmArea,
    SwarmSpeed,
    SwarmDistance,
)


menu_functions = [
    lambda self, context: self.layout.operator(SwarmInit.bl_idname),
    lambda self, context: self.layout.operator(SwarmPlanner.bl_idname),
    lambda self, context: self.layout.operator(SwarmExporter.bl_idname),
    lambda self, context: self.layout.operator(SwarmPainter.bl_idname),
    lambda self, context: self.layout.operator(SwarmArea.bl_idname),
    lambda self, context: self.layout.operator(SwarmSpeed.bl_idname),
    lambda self, context: self.layout.operator(SwarmDistance.bl_idname),
]

button_classes = (
    SwarmAreaButton,
    SwarmDistanceButton,
    SwarmSpeedButton,
    SwarmPlannerButton,
    SwarmPainterButton,
)


def register():
    bpy.utils.register_class(SwarmInit)
    bpy.types.VIEW3D_MT_object.append(menu_functions[0])

    bpy.utils.register_class(SwarmPlanner)
    bpy.types.VIEW3D_MT_object.append(menu_functions[1])

    bpy.utils.register_class(SwarmExporter)
    bpy.types.VIEW3D_MT_object.append(menu_functions[2])

    bpy.utils.register_class(SwarmPainter)
    bpy.types.VIEW3D_MT_object.append(menu_functions[3])

    bpy.utils.register_class(SwarmArea)
    bpy.types.VIEW3D_MT_object.append(menu_functions[4])

    bpy.utils.register_class(SwarmSpeed)
    bpy.types.VIEW3D_MT_object.append(menu_functions[5])

    bpy.utils.register_class(SwarmDistance)
    bpy.types.VIEW3D_MT_object.append(menu_functions[6])

    for current_class in button_classes:
        bpy.utils.register_class(current_class)

def unregister():
    for current_class in reversed(button_classes):
        bpy.utils.unregister_class(current_class)
    for current_class in menu_classes:
        bpy.utils.unregister_class(current_class)
    for menu_function in menu_functions:
        bpy.types.VIEW3D_MT_object.remove(menu_function)
