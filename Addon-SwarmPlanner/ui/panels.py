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
        documentation_url = "https://github.com/FlyinDiamonds/blender_addon#flyindiamonds"
        row.operator("wm.url_open", icon='QUESTION', text="").url = documentation_url
    
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
        props = context.scene.fd_swarm_area_props

        row = layout.row()
        row.prop(props, 'point0')
        row = layout.row()
        row.prop(props, 'point1')
        row = layout.row()
        row.operator("view3d.swarm_area_button")


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
        props = context.scene.fd_swarm_init_props

        row = layout.row()
        row.prop(props, 'cnt_x')
        row.prop(props, 'cnt_y')
        row = layout.row()
        row.prop(props, 'spacing')
        row = layout.row()
        row.operator("object.swarm_init_button")




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
        props = context.scene.fd_swarm_distance_props

        row = layout.row()
        row.prop(props, 'min_distance')
        row = layout.row()
        row.operator("object.swarm_distance_button")


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
        props = context.scene.fd_swarm_speed_props

        row = layout.row()
        row.prop(props, 'max_speed_vertical')
        row = layout.row()
        row.prop(props, 'max_speed_horizontal')
        row = layout.row()
        row.operator("object.swarm_speed_button")


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
        props = context.scene.fd_swarm_planner_props

        row = layout.row()
        row.prop(props, 'min_distance')
        row = layout.row()
        row.prop(props, 'speed')
        row = layout.row()
        row.prop(props, 'use_faces')
        row = layout.row()
        row.operator("object.swarm_plan_button")



class FD_ColorPanel(Panel):
    """Creates side panel."""
    bl_label = "Swarm color"
    bl_idname = "FD_ColorPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"

    def draw_header_preset(self, context):
        layout = self.layout

        row = layout.row()
        documentation_url = "https://github.com/FlyinDiamonds/blender_addon#flyindiamonds"
        row.operator("wm.url_open", icon='QUESTION', text="").url = documentation_url

    def draw(self, context):
        pass


class FD_ColorMethod(Panel):
    """Creates side panel."""
    bl_label = "Swarm color method"
    bl_idname = "FD_ColorMethod"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"
    bl_parent_id = "FD_ColorPanel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.fd_swarm_color_props

        color_method_index = int(props.color_method_dropdown)

        row = layout.row()
        row.prop(props, 'color_method_dropdown', expand=True)

        if color_method_index == 0:
            row = layout.row()
            row.prop(props, 'color_pallette', expand=True)
        elif color_method_index == 1:
            row = layout.row()
            row.prop(props, 'color_picker')


class FD_SelectMethod(Panel):
    """Creates side panel."""
    bl_label = "Swarm select method"
    bl_idname = "FD_SelectMethod"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"
    bl_parent_id = "FD_ColorPanel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.fd_swarm_color_props

        select_method_index = int(props.select_method_dropdown)

        row = layout.row()
        row.prop(props, 'select_method_dropdown', expand=True)

        if select_method_index == 0:
            # selected in scene
            pass
        elif select_method_index == 1:
            row = layout.row()
            row.prop_search(props, "selected_mesh", context.scene, "objects")
        elif select_method_index == 2:
            row = layout.row()
            row.prop(props, 'random_percentage')

        row = layout.row()
        row.prop(props, 'invert_selection')


class FD_ColorProps(Panel):
    """Creates side panel."""
    bl_label = "Swarm apply color"
    bl_idname = "FD_ColorProps"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"
    bl_parent_id = "FD_ColorPanel"

    def draw(self, context):
        layout = self.layout
        props = context.scene.fd_swarm_color_props

        row = layout.row()
        row.prop(props, 'step_change')
        row.operator("object.swarm_paint_button")


class FD_PainterPanel(Panel):
    """Creates side panel."""
    bl_label = "Swarm painter"
    bl_idname = "FD_PainterPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FlyinDiamonds"

    def draw_header_preset(self, context):
        layout = self.layout

        row = layout.row()
        documentation_url = "https://github.com/FlyinDiamonds/blender_addon#flyindiamonds"
        row.operator("wm.url_open", icon='QUESTION', text="").url = documentation_url

    def draw(self, context):
        layout = self.layout
        props = context.scene.fd_swarm_painter_props

        # FRAMES
        frame_method_index = int(props.frame_method_dropdown)

        box = layout.box()
        row = box.row()
        row.label(text="Frames settings")
        row = box.row()
        row.prop(props, 'frame_method_dropdown', expand=True)
        if frame_method_index == 0:
            row = box.row()
            row.prop(props, 'frame_duration', expand=True)
        elif frame_method_index == 1:
            row = box.row()
            row.prop(props, 'start_frame', expand=True)
            row.prop(props, 'end_frame', expand=True)

        # COLOR
        color_method_index = int(props.color_method_dropdown)

        box = layout.box()
        row = box.row()
        row.label(text="Color settings")
        row = box.row()
        row.prop(props, 'color_method_dropdown', expand=True)
        if color_method_index == 0:
            row = box.row()
            row.prop(props, 'color_pallette', expand=True)
        elif color_method_index == 1:
            row = box.row()
            row.prop(props, 'color_picker')
        row = box.row()
        col = row.column()
        col.prop(props, 'override_background')
        col = row.column()
        col.prop(props, 'background_color_picker')
        if not props.override_background:
            col.enabled = False
        row = box.row()
        
        # SELECT
        select_method_index = int(props.select_method_dropdown)

        box = layout.box()
        row = box.row()
        row.label(text="Select settings")
        row = box.row()
        row.prop(props, 'select_method_dropdown', expand=True)
        if select_method_index == 0:
            # selected in scene
            pass
        elif select_method_index == 1:
            row = box.row()
            row.prop_search(props, "selected_mesh", context.scene, "objects")
        elif select_method_index == 2:
            row = box.row()
            row.prop(props, 'random_percentage')
        row = box.row()
        row.prop(props, 'invert_selection')
        
        # FUNCTIONS
        row = layout.row()
        row.operator("object.swarm_painter_button")


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
