import bpy
from mathutils import Color
from bpy.props import BoolProperty, FloatVectorProperty, EnumProperty, IntProperty, FloatProperty, PointerProperty

from ..properties.properties import fd_color_method_list_old, fd_color_pallette_list, fd_select_method_list, fd_select_mesh_poll
from ..utils.drone_in_mesh import is_drone_inside_mesh

import random


COLOR_PALLETTE = [
    (1.0, 1.0, 1.0, 1.0),
    (0.0, 0.0, 0.0, 1.0),
    (1.0, 0.0, 0.0, 1.0),
    (0.0, 1.0, 0.0, 1.0),
    (0.0, 0.0, 1.0, 1.0),
]


class SwarmPainterBaseOld:
    """Initialize drone swarm"""
    color_method_dropdown: EnumProperty(
        items=fd_color_method_list_old,
        name="Color method",
        default=0,
        description="Pick method for drone painting",
    )
    color_pallette: EnumProperty(
        items=fd_color_pallette_list,
        name="Color pallette",
        default=0,
        description="Pick color from color pallette",
    )
    color_picker: FloatVectorProperty(
             name = "Color Picker",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0,1.0,1.0,1.0),
             size = 4
             )
    select_method_dropdown: EnumProperty(
        items=fd_select_method_list,
        name="Select method",
        default=0,
        description="Pick method for drone selection",
    )
    selected_mesh: PointerProperty(name="Select mesh", type=bpy.types.Object, poll=fd_select_mesh_poll)
    random_percentage: IntProperty(name="Percentage to select", default=50, min=1, max=100)
    invert_selection: BoolProperty(name="Invert selection", default=False)
    step_change: BoolProperty(name="Step change", default=True)

    @classmethod
    def draw_with_layout(self, context, layout):
        # TODO may be extract to function as name(obj: Obj, context, layout), not sure if its good way
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

        props = context.scene.fd_swarm_color_props

        row = layout.row()
        row.prop(props, 'step_change')
        row.operator("object.swarm_paint_button")

    def execute(self, context):
        drones = []
        all_drones = {drone for drone in context.scene.objects if drone.name.startswith("Drone")}

        color_method_index = int(self.color_method_dropdown)
        if color_method_index == 0:
            color = COLOR_PALLETTE[int(self.color_pallette)]
        elif color_method_index == 1:
            color = self.color_picker

        select_method_index = int(self.select_method_dropdown)
        if select_method_index == 0:
            drones = [drone for drone in all_drones if drone in context.selected_objects]
        elif select_method_index == 1:
            if self.selected_mesh:
                drones = [drone for drone in all_drones if is_drone_inside_mesh(drone, self.selected_mesh)]
        elif select_method_index == 2:
            num_of_drones = round(len(all_drones) / 100 * self.random_percentage)
            drones = random.sample(all_drones, num_of_drones)

        if self.invert_selection:
            drones = [drone for drone in all_drones if drone not in drones]

        for drone in drones:
            current_frame = context.scene.frame_current

            mat = drone.data.materials[0]
            if self.step_change:
                mat.keyframe_insert(data_path="diffuse_color", frame=current_frame-1)
                drone.keyframe_insert(data_path='["custom_color"]', frame=current_frame-1)

            mat.diffuse_color = color
            drone["custom_color"] = [int(c*255) for c in list(color)[:3]]

            mat.keyframe_insert(data_path="diffuse_color", frame = current_frame)
            drone.keyframe_insert(data_path='["custom_color"]', frame = current_frame)

        return {'FINISHED'}

    def update_props_from_context(self, context):
        props = context.scene.fd_swarm_color_props
        self.select_method_dropdown, self.color_method_dropdown = props.select_method_dropdown, props.color_method_dropdown
        self.color_pallette, self.color_picker, self.color_method_dropdown = props.color_pallette, props.color_picker, props.color_method_dropdown
        self.invert_selection, self.step_change, self.random_percentage = props.invert_selection, props.step_change, props.random_percentage
        self.selected_mesh = props.selected_mesh
        

class SwarmPainterOld(bpy.types.Operator, SwarmPainterBaseOld):
    """Set color for selected drones"""
    bl_idname = "object.swarm_paint"
    bl_label = "Swarm - Set color"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        self.draw_with_layout(context, self.layout)

    def invoke(self, context, event):
        self.update_props_from_context(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class SwarmPainterButtonOld(bpy.types.Operator, SwarmPainterBaseOld):
    """Set color for selected drones"""
    bl_idname = "object.swarm_paint_button"
    bl_label = "Swarm - Set color"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        self.draw_with_layout(context, self.layout)

    def invoke(self, context, event):
        self.update_props_from_context(context)
        return self.execute(context)
