import bpy

from bpy.utils import register_class, unregister_class

from . import panels

classes = (
    panels.FD_PlanningPanel,
    panels.FD_SwarmArea,
    panels.FD_SwarmInit,
    panels.FD_SwarmPlan,
    panels.FD_SwarmDistance,
    panels.FD_SwarmSpeed,
    panels.FD_ColorPanel,
    panels.FD_ExportPanel,
)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)