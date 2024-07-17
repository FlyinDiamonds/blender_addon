import bpy
import addon_utils
from mathutils import Vector
from ..utils.common import get_all_drones, update_from_property_group
from bpy.props import IntProperty, StringProperty, BoolProperty
import os
import logging

logger = logging.getLogger(__name__)


def draw_render(context, layout, props_obj=None):
    if props_obj is None:
        props_obj = context.scene.fd_swarm_render_props

    row = layout.row()
    row.prop(props_obj, "start_frame")
    row.prop(props_obj, "end_frame")
    row = layout.row()
    row.prop(props_obj, "auto_focus")
    row = layout.row()
    row.prop_search(props_obj, "camera_name", bpy.data, "cameras", text="Camera")


class SwarmRender(bpy.types.Operator):
    """Render drone animation"""
    bl_idname = "object.swarm_render"
    bl_label = "Swarm - Render"
    bl_options = {'REGISTER', 'UNDO'}

    camera_name: StringProperty(name="Camera")
    auto_focus: BoolProperty(default=True, name="Auto focus")
    start_frame: IntProperty(name="Start frame", default=0, min=0)
    end_frame: IntProperty(name="End frame", default=100, min=1)

    is_button: BoolProperty(default=False, options={'HIDDEN'})

    def draw(self, context):
        layout = self.layout
        draw_render(context, layout, self)

    def invoke(self, context, event):
        update_from_property_group(self, context.scene.fd_swarm_render_props)

        if self.is_button:
            self.is_button = False
            return self.execute(context)
        else:
            return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        scene = bpy.context.scene
        prev_frame_start, prev_frame_end = scene.frame_start, scene.frame_end
        scene.frame_start, scene.frame_end = self.start_frame, self.end_frame

        self.all_drones = get_all_drones(context)
        self.cam = scene.camera = self.get_or_create_camera(self.camera_name)

        self.prepare_camera()
        self.prepare_hdri()

        for obj in context.scene.objects:
            if obj not in self.all_drones:
                obj.hide_render = True
        
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
        scene.render.image_settings.file_format = 'FFMPEG'

        bpy.ops.render.render(animation=True)
        scene.frame_start, scene.frame_end = prev_frame_start, prev_frame_end
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
    
    
    def prepare_camera(self):
        if not self.all_drones:
            return
        
        if self.auto_focus:
            self.clear_camera_keyframes()
            step = 10
            for frame in range(self.start_frame, self.end_frame + step, step):
                self.focus_camera(frame)
                self.cam.keyframe_insert(data_path="rotation_euler", frame=frame)

    def clear_camera_keyframes(self):
        if self.cam.animation_data and self.cam.animation_data.action:
            fcurves = self.cam.animation_data.action.fcurves
            for fcurve in fcurves:
                if fcurve.data_path == "rotation_euler":
                    self.cam.animation_data.action.fcurves.remove(fcurve)
    
    def focus_camera(self, frame):
        center = sum((self.get_object_location_at_frame(obj, frame) for obj in self.all_drones), Vector()) / len(self.all_drones)
        direction = self.cam.location - center
        rot_quat = direction.to_track_quat('Z', 'Y')
        self.cam.rotation_euler = rot_quat.to_euler()

    
    def prepare_hdri(self):
        hdri_path = None
        for mod in addon_utils.modules():
            if mod.bl_info.get("name") == "SwarmPlanner":
                root_dir = os.path.dirname(mod.__file__)
                hdri_path = os.path.join(os.path.join(root_dir, "textures"), "symmetrical_garden_02_2k.hdr")
                break

        scene = bpy.context.scene
        scene.render.film_transparent = True

        node_tree = scene.world.node_tree
        tree_nodes = node_tree.nodes
        tree_nodes.clear()


        node_text_coords = tree_nodes.new(type="ShaderNodeTexCoord")
        node_mapping = tree_nodes.new(type="ShaderNodeMapping")
        node_environment = tree_nodes.new('ShaderNodeTexEnvironment')


        node_light_path = tree_nodes.new(type="ShaderNodeLightPath")
        node_background = tree_nodes.new(type='ShaderNodeBackground')
        node_background_black = tree_nodes.new(type='ShaderNodeBackground')

        node_mix_shader = tree_nodes.new(type='ShaderNodeMixShader')

        node_output = tree_nodes.new(type='ShaderNodeOutputWorld')

        node_environment.image = bpy.data.images.load(hdri_path)
        node_background.inputs[1].default_value = 5.0


        links = node_tree.links
        links.new(node_text_coords.outputs["Generated"], node_mapping.inputs["Vector"])

        links.new(node_mapping.outputs["Vector"], node_environment.inputs["Vector"])

        links.new(node_environment.outputs["Color"], node_background.inputs["Color"])

        links.new(node_light_path.outputs["Is Camera Ray"], node_mix_shader.inputs["Fac"])
        links.new(node_background.outputs["Background"], node_mix_shader.inputs["Shader"])
        links.new(node_background_black.outputs["Background"], node_mix_shader.inputs["Shader"])

        links.new(node_mix_shader.outputs["Shader"], node_output.inputs["Surface"])

    def get_object_location_at_frame(self, obj, frame):
        if not obj.animation_data or not obj.animation_data.action:
            return obj.location
        
        try:
            loc_x_curve = obj.animation_data.action.fcurves[0]
            loc_y_curve = obj.animation_data.action.fcurves[1]
            loc_z_curve = obj.animation_data.action.fcurves[2]
        except IndexError:
            logger.debug(f"Object '{obj}' does not have enough f-curves for location")
            return obj.location

        loc_x = loc_x_curve.evaluate(frame)
        loc_y = loc_y_curve.evaluate(frame)
        loc_z = loc_z_curve.evaluate(frame)
        
        return Vector((loc_x, loc_y, loc_z))