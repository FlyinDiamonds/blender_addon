import bpy
from mathutils import Color
from bpy.props import BoolProperty, FloatVectorProperty, EnumProperty, IntProperty, FloatProperty, PointerProperty


class SwarmPainterBase:
    """Initialize drone swarm"""
    color_pallette: FloatProperty(name="Vertical max drone speed", default=5.0, min=1.0, max=10.0)
    color_picker: FloatVectorProperty(
             name = "Color Picker",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0,1.0,1.0,1.0),
             size = 4
             )
    color_method_dropdown: EnumProperty(
        items=(('0','Pallete','Color pallete'), ('1','Picker','Color picker')),
        name="Color method",
        default="0",
        description="Tooltip for the Dropdownbox",
    )
    select_method_dropdown: EnumProperty(
        items=(('0','Selected','Selected drones'), ('1','In mesh','Select by object'), ('2','Random','Select random')),
        name="Select method",
        default="0",
        description="Tooltip for the Dropdownbox",
    )
    invert_selection: BoolProperty(name="Invert selection", default=False)
    select_mesh: PointerProperty(type=bpy.types.Object)
    random_percentage: IntProperty(name="Percentage", default=50, min=1, max=100)
    step_change: bpy.props.BoolProperty(name="Step change", default=True)

    def execute(self, context):
        color_method_index = int(self.color_method_dropdown)
        if color_method_index == 0:
            color = self.color_pallette
        elif color_method_index == 1:
            color = self.color_picker

        select_method_index = int(self.select_method_dropdown)
        all_drones = {drone for drone in context.scene.objects if drone.name.startswith("Drone")} # TODO not only selected
        if select_method_index == 0:
            drones = [drone for drone in all_drones if drone in context.selected_objects]
        elif select_method_index == 1:
            drones = self.select_mesh
        elif select_method_index == 2:
            drones = context.selected_objects # TODO random
        
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
        self.select_mesh = props.select_mesh
        

class SwarmPainter(bpy.types.Operator, SwarmPainterBase):
    """Set color for selected drones"""
    bl_idname = "object.swarm_paint"
    bl_label = "Swarm - Set color"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self.update_props_from_context(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    

class SwarmPainterButton(bpy.types.Operator, SwarmPainterBase):
    """Set color for selected drones"""
    bl_idname = "object.swarm_paint_button"
    bl_label = "Swarm - Set color"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self.update_props_from_context(context)
        return self.execute(context)


