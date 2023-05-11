import bpy

from ..planning.planner import plan_fastest, get_max_time

class SwarmPlanner(bpy.types.Operator):
    """Plan drone swarm transition to selected formation"""
    bl_idname = "object.swarm_plan"
    bl_label = "Swarm - Plan transition"
    bl_options = {'REGISTER', 'UNDO'}

    MINIMUM_DISTANCE: bpy.props.FloatProperty(name="Minimal distance", default=2.0, min=1.0, max=5.0)
    SPEED: bpy.props.FloatProperty(name="Drone speed", default=5.0, min=1.0, max=10.0)
    USE_FACES: bpy.props.BoolProperty(name="Use faces", default=False)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene
        FRAMERATE = scene.render.fps

        positions_source = []
        positions_target = []

        drone_objects = []

        for object in scene.objects:
            if object.name.startswith("Drone"):
                drone_objects.append(object)
                positions_source.append(list(object.location))

        target_object = context.active_object

        if self.USE_FACES:
            for polygon in target_object.data.polygons:
                polygon_global_position = target_object.matrix_world @ polygon.center
                positions_target.append(list(polygon_global_position))
        else:
            for vertex in target_object.data.vertices:
                vertex_global_position = target_object.matrix_world @ vertex.co
                positions_target.append(list(vertex_global_position))


        position_cnt = min(len(positions_source), len(positions_target))
        flight_paths = plan_fastest(
            positions_source[:position_cnt],
            positions_target[:position_cnt],
            self.SPEED, self.MINIMUM_DISTANCE)

        frame_start = scene.frame_current
        last_frame = int(get_max_time(flight_paths, self.SPEED)*FRAMERATE) + frame_start
        for path in flight_paths:
            dt = path.color / self.SPEED
            dframe = int(dt*FRAMERATE)
            frame_cnt = int(path.length/self.SPEED*FRAMERATE)

            current_drone = drone_objects[path.start_position_index]
            current_drone.location = path.start
            current_drone.keyframe_insert(data_path="location", frame=frame_start + dframe)

            current_drone.location = path.end
            end_frame = frame_start + dframe + frame_cnt
            current_drone.keyframe_insert(data_path="location", frame=end_frame)
            current_drone.keyframe_insert(data_path="location", frame=last_frame)

            for fcurve in current_drone.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = "LINEAR"

            if end_frame > context.scene.frame_end:
                context.scene.frame_end = end_frame

        return {'FINISHED'}

