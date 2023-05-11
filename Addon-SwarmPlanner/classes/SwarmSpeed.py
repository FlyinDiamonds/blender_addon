import bpy
import numpy as np
import gpu
from gpu_extras.batch import batch_for_shader
import logging
from mathutils import Color
from .drawFunctions import enable_draw_speed

class SwarmSpeed(bpy.types.Operator):
    """Set color for selected drones"""
    bl_idname = "object.swarm_speed"
    bl_label = "Swarm - Check speed"
    bl_options = {'REGISTER', 'UNDO'}

    max_speed: bpy.props.FloatProperty(name="Max drone speed", default=5.0, min=1.0, max=10.0)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene
        fps = scene.render.fps
        original_frame = scene.frame_current
        scene.timeline_markers.clear()

        drones = [obj for obj in scene.objects if obj.name.startswith("Drone")]
        for drone in drones:
            drone["speed_intervals"] = list()

        scene.frame_set(0)
        positions = [obj.location.copy() for obj in drones]
        prev_violations = np.array([False] * len(drones))

        for frame in range(scene.frame_end+1):
            context.area.header_text_set(f"Processing frame: {frame}/{scene.frame_end}  ({round(frame/scene.frame_end*100,1)}%)")

            scene.frame_set(frame)
            position_delta = np.array([np.linalg.norm(obj.location - pos) for obj,pos in zip(drones,positions) ])
            positions = [obj.location.copy() for obj in drones]

            violations = position_delta > self.max_speed/fps

            for obj, violation, prev_violation in zip(drones, violations, prev_violations):
                if violation == prev_violation:
                    continue

                suffix = "S" if violation else "E"
                scene.timeline_markers.new(f"{obj.name[5:]}_{suffix}",frame=frame)

                if violation:
                    obj["speed_intervals"] = list(obj["speed_intervals"])+[[frame, -1]]
                else:
                    obj["speed_intervals"][-1][1] = frame

            prev_violations = violations.copy()

        scene.frame_set(original_frame)
        context.area.header_text_set(None)

        # if "active_custom_shader" in scene.keys():
        #     if scene["active_custom_shader"]:
        #         bpy.types.SpaceView3D.draw_handler_remove(scene["active_custom_shader"], 'WINDOW')
        # bpy.types.SpaceView3D.draw_handler_add(draw_speed, (), 'WINDOW', 'POST_VIEW')
        # scene["active_custom_shader"] = draw_speed
        enable_draw_speed()
        return {'FINISHED'}

