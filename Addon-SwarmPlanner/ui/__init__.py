import bpy

from bpy.utils import register_class, unregister_class

from . import panels

classes = (
    panels.FD_PT_PlanningPanel,
    panels.FD_PT_PainterPanel,
    panels.FD_PT_ExportPanel,
    panels.FD_PT_SwarmArea,
    panels.FD_PT_SwarmInit,
    panels.FD_PT_SwarmPlan,
    panels.FD_PT_SwarmDistance,
    panels.FD_PT_SwarmSpeed,
)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
