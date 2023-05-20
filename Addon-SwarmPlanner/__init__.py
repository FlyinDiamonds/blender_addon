import bpy

from . import operators
from . import properties
from . import ui


bl_info = {
    "name": "SwarmPlanner",
    "author": "Martin Prochazka",
    "description": "Swarm planning add-on",
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Object"
}


modules = (
    properties,
    operators,
    ui,
)


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
