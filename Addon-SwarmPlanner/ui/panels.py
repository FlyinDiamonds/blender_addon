import bpy

from bpy.types import Panel


class FD_PlanningPanel(Panel):
    """Creates side panel."""
    bl_label = "Swarm planning"
    bl_idname = "FD_PlanningPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"

    def draw_header_preset(self, context):
        layout = self.layout

        row = layout.row()
        documentation_url = "https://github.com/FlyinDiamonds/blender_addon/tree/main/Addon-SwarmPlanner"
        # row.operator("fd.open_help_url", icon='QUESTION', text="").url = documentation_url

    def draw(self, context):
        pass


class FD_SwarmArea(Panel):
    """Creates sub-panel."""
    bl_label = "Swarm area"
    bl_idname = "FD_SwarmArea"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"
    bl_parent_id = "FD_PlanningPanel"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("view3d.swarm_area")


class FD_SwarmInit(Panel):
    """Creates sub-panel."""
    bl_label = "Swarm init"
    bl_idname = "FD_SwarmInit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"
    bl_parent_id = "FD_PlanningPanel"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.swarm_init")


class FD_SwarmPlan(Panel):
    """Creates sub-panel."""
    bl_label = "Swarm plan"
    bl_idname = "FD_SwarmPlan"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"
    bl_parent_id = "FD_PlanningPanel"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.swarm_plan")



class FD_SwarmDistance(Panel):
    """Creates sub-panel."""
    bl_label = "Swarm distance"
    bl_idname = "FD_SwarmDistance"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"
    bl_parent_id = "FD_PlanningPanel"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.swarm_distance")


class FD_SwarmSpeed(Panel):
    """Creates sub-panel."""
    bl_label = "Swarm speed"
    bl_idname = "FD_SwarmSpeed"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"
    bl_parent_id = "FD_PlanningPanel"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.swarm_speed")


class FD_ColorPanel(Panel):
    """Creates side panel."""
    bl_label = "Swarm color"
    bl_idname = "FD_ColorPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.swarm_paint")


class FD_ExportPanel(Panel):
    """Creates side panel."""
    bl_label = "Swarm export"
    bl_idname = "FD_ExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.swarm_export")
