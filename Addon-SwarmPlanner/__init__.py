import bpy

from .classes.SwarmInit import SwarmInit
from .classes.SwarmPlanner import SwarmPlanner
from .classes.SwarmExporter import SwarmExporter
from .classes.SwarmPainter import SwarmPainter
from .classes.SwarmArea import SwarmArea
from .classes.SwarmSpeed import SwarmSpeed
from .classes.SwarmDistance import SwarmDistance
from .classes import Panels

bl_info = {
    "name": "SwarmPlanner",
    "author": "Martin Prochazka",
    "description": "Swarm planning add-on",
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Object"
}


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
    lambda self, context:self.layout.operator(SwarmPlanner.bl_idname),
    lambda self, context:self.layout.operator(SwarmExporter.bl_idname),
    lambda self, context: self.layout.operator(SwarmPainter.bl_idname),
    lambda self, context: self.layout.operator(SwarmArea.bl_idname),
    lambda self, context: self.layout.operator(SwarmSpeed.bl_idname),
    lambda self, context: self.layout.operator(SwarmDistance.bl_idname),
]

files = (
    Panels,
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

    for f in files:
        f.register()

def unregister():
    for current_class in menu_classes:
        bpy.utils.unregister_class(current_class)
    for menu_function in menu_functions:
        bpy.types.VIEW3D_MT_object.remove(menu_function)

    for f in reversed(files):
        f.unregister()
