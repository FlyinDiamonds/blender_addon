import bpy
from mathutils import Color

class SwarmPainter(bpy.types.Operator):
    """Set color for selected drones"""
    bl_idname = "object.swarm_paint"
    bl_label = "Swarm - Set color"
    bl_options = {'REGISTER', 'UNDO'}

    color: bpy.props.FloatVectorProperty(
             name = "Color Picker",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0,1.0,1.0,1.0),
             size = 4
             )
    step_change: bpy.props.BoolProperty(name="Step change", default=True)
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        for drone in context.selected_objects:
            if not drone.name.startswith("Drone"):
                continue

            current_frame = context.scene.frame_current

            mat = drone.data.materials[0]
            if self.step_change:
                mat.keyframe_insert(data_path="diffuse_color", frame=current_frame-1)
                drone.keyframe_insert(data_path='["custom_color"]', frame=current_frame-1)

            mat.diffuse_color = self.color
            drone["custom_color"] = [int(c*255) for c in list(self.color)[:3]]

            mat.keyframe_insert(data_path="diffuse_color", frame = current_frame)
            drone.keyframe_insert(data_path='["custom_color"]', frame = current_frame)

        return {'FINISHED'}

