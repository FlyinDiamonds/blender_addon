import bpy
import numpy as np
from math import floor
from itertools import product
from mathutils import Vector
from .drawFunctions import enable_draw_distance


class SwarmDistance(bpy.types.Operator):
    """Check minimal distance between drones"""
    bl_idname = "object.swarm_distance"
    bl_label = "Swarm - Check distance"
    bl_options = {'REGISTER', 'UNDO'}
    min_distance: bpy.props.FloatProperty(name="Mininal separation", default=1.0, min=0.1, max=10.0)
    is_button: bpy.props.BoolProperty(default=False)

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
        scene = context.scene
        original_frame = scene.frame_current
        scene.timeline_markers.clear()

        drones = [obj for obj in scene.objects if obj.name.startswith("Drone")]
        for drone in drones:
            drone["collision_intervals"] = {}

        scene.frame_set(0)
        violations = {}
        for frame in range(scene.frame_end+1):
            context.area.header_text_set(f"Processing frame: {frame}/{scene.frame_end}  ({round(frame/scene.frame_end*100,1)}%)")

            scene.frame_set(frame)

            hashed = {}
            for drone in drones:
                pos = drone.location / self.min_distance
                pos_hashed = f"x{floor(pos[0])}y{floor(pos[1])}z{floor(pos[2])}"
                if pos_hashed not in hashed.keys():
                    hashed[pos_hashed] = [drone]
                else:
                    hashed[pos_hashed].append(drone)

            offsets = list(product([-1,0,1],repeat=3))
            for drone in drones:
                pos = drone.location / self.min_distance
                pos_hashed = f"x{floor(pos[0])}y{floor(pos[1])}z{floor(pos[2])}"
                hashed[pos_hashed].remove(drone)
                if not hashed[pos_hashed]:
                    hashed.pop(pos_hashed)

                for offset in offsets:
                    voxel_hash = f"x{floor(pos[0]+offset[0])}y{floor(pos[1]+offset[1])}z{floor(pos[2]+offset[2])}"
                    if voxel_hash not in hashed.keys():
                        continue
                    for candidate in hashed[voxel_hash]:
                        violation = np.linalg.norm(candidate.location - drone.location) < self.min_distance
                        violation_hash = f"{drone.name}-{candidate.name}"

                        prev_violation = False
                        if violation_hash in violations.keys():
                            prev_violation = violations[violation_hash]

                        if violation == prev_violation:
                            continue
                        violations[violation_hash] = violation

                        suffix = "S" if violation else "E"
                        scene.timeline_markers.new(f"{violation_hash}_{suffix}", frame=frame)

                        if violation_hash not in drone["collision_intervals"].keys():
                            drone["collision_intervals"][violation_hash] = [[frame, -1, int(candidate.name[5:])]]
                        elif violation:
                            drone["collision_intervals"][violation_hash].append([frame, -1, int(candidate.name[5:])])
                        else:
                            drone["collision_intervals"][violation_hash][-1][1] = frame

        scene.frame_set(original_frame)
        context.area.header_text_set(None)

        # if "active_custom_shader" in scene.keys():
        #     if scene["active_custom_shader"]:
        #         bpy.types.SpaceView3D.draw_handler_remove(scene["active_custom_shader"], 'WINDOW')
        # bpy.types.SpaceView3D.draw_handler_add(draw_distance, (), 'WINDOW', 'POST_VIEW')
        # scene["active_custom_shader"] = draw_distance
        enable_draw_distance()
        return {'FINISHED'}
    
    def update_props_from_context(self, context):
        props = context.scene.fd_swarm_distance_props
        self.min_distance = props.min_distance
