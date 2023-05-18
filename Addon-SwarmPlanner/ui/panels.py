import bpy

from bpy.types import Panel


class FD_MainPanel(Panel):
    """Creates main side panel."""
    bl_label = "Swarm planning"
    bl_idname = "FD_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyingDiamonds"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.swarm_init")
        row = layout.row()
        row.operator("object.swarm_plan")
        row = layout.row()
        row.operator("object.swarm_speed")
        row = layout.row()
        row.operator("object.swarm_distance")
        row = layout.row()
        row.operator("object.swarm_paint")
        row = layout.row()
        row.operator("object.swarm_export")

        row = layout.row()
        row.operator("wm.url_open", text="Documentation", icon="URL"
                     ).url = "https://github.com/FlyinDiamonds/blender_addon/tree/main/Addon-SwarmPlanner"


class FD_SwarmArea(Panel):
    """Creates sub-panel."""
    bl_label = "Swarm area"
    bl_idname = "FD_SwarmArea"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyingDiamonds"
    bl_parent_id = "FD_MainPanel"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("view3d.swarm_area")
