bl_info = {
    "name": "SwarmPlanner",
    "author": "Martin Prochazka",
    "description": "Swarm planning add-on",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D",
    "category": "Object"
}


if 'bpy' in locals():
    print('SwarmPlanner Reloading')
    from importlib import reload
    import sys
    for k, v in list(sys.modules.items()):
        if k.startswith('Addon-SwarmPlanner.'):
            print("Reloading: ", k)
            reload(v)


import bpy

from . import operators
from . import properties
from . import ui
from .planning.statistics import statistics_usage


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
