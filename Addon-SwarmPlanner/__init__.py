import bpy

from . import operators
from . import properties
from . import ui
from .planning.statistics import statistics_usage


bl_info = {
    "name": "SwarmPlanner",
    "author": "Martin Prochazka",
    "description": "Swarm planning add-on",
    "blender": (3, 6, 0),
    "location": "View3D",
    "category": "Object"
}


modules = (
    properties,
    operators,
    ui,
)


def register():
    statistics_usage()
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
