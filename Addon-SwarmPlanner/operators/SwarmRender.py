import bpy
import math
from mathutils import Vector
from ..utils.common import get_all_drones


class SwarmRender(bpy.types.Operator):
    """Render drone animation"""
    bl_idname = "object.swarm_render"
    bl_label = "Swarm - Render"
    bl_options = {'REGISTER', 'UNDO'}

    camera_name: bpy.props.StringProperty(name="Camera")
    is_button: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "camera_name", bpy.data, "cameras", text="Camera")
        if self.camera_name and bpy.data.cameras.get(self.camera_name):
            layout.prop(bpy.data.cameras[self.camera_name], "lens")

    def invoke(self, context, event):
        if self.is_button:
            self.update_props_from_context(context)
            self.is_button = False
            return self.execute(context)
        else:
            self.update_props_from_context(context)
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

    def execute(self, context):
        self.all_drones = get_all_drones(context)
        self.cam = bpy.context.scene.camera = self.get_or_create_camera(self.camera_name)
        self.light = self.get_or_create_light()

        self.prepare_camera()

        light_rotation = (math.radians(45), math.radians(-45), math.radians(45))
        self.prepare_light(light_rotation)

        self.set_output_dimensions(1920, 1280, 100)
        bpy.ops.render.render('INVOKE_DEFAULT')
        return {'FINISHED'}
    
    @staticmethod
    def get_or_create_camera(camera_name):
        if not camera_name:
            camera_name = "Camera"
        camera_obj = bpy.data.objects.get(camera_name)
        if camera_obj is None:
            camera_data = bpy.data.cameras.new(name=camera_name)
            camera_obj = bpy.data.objects.new(camera_name, camera_data)
            bpy.context.view_layer.active_layer_collection.collection.objects.link(camera_obj)
        return camera_obj
    
    @staticmethod
    def get_or_create_light():
        light_obj = bpy.data.objects.get("Light")
        if light_obj is None:
            light_data = bpy.data.lights.new(name="Light", type='SUN')
            light_obj = bpy.data.objects.new("Light", light_data)
            bpy.context.view_layer.active_layer_collection.collection.objects.link(light_obj)
        return light_obj
    
    @staticmethod
    def set_output_dimensions(dimension_x, dimension_y, percentage):
        scene = bpy.data.scenes["Scene"]
        scene.render.resolution_x = dimension_x
        scene.render.resolution_y = dimension_y
        scene.render.resolution_percentage = percentage
    
    def prepare_camera(self):
        if not self.all_drones:
            return

        center = sum((obj.location for obj in self.all_drones), Vector()) / len(self.all_drones)
        direction = self.cam.location - center
        rot_quat = direction.to_track_quat('Z', 'Y')
        self.cam.rotation_euler = rot_quat.to_euler()

    def prepare_light(self, rotation):
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        self.light.rotation_euler = rotation
        self.light.data.energy = 2

    def update_props_from_context(self, context):
        pass
        # props = context.scene.fd_swarm_init_props
        # self.cnt_x, self.cnt_y, self.spacing = props.cnt_x, props.cnt_y, props.spacing
