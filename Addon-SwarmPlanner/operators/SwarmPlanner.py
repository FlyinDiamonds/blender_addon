import bpy

from ..planning.planner import plan_fastest, get_max_time


class SwarmPlannerBase:
    """Plan drone swarm transition to selected formation"""

    min_distance: bpy.props.FloatProperty(name="Minimal distance", default=2.0, min=1.0, max=5.0)
    speed: bpy.props.FloatProperty(name="Drone speed", default=5.0, min=1.0, max=10.0)
    use_faces: bpy.props.BoolProperty(name="Use faces", default=False)

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

        if self.use_faces:
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
            self.speed, self.min_distance)

        frame_start = scene.frame_current
        last_frame = int(get_max_time(flight_paths, self.speed)*FRAMERATE) + frame_start
        for path in flight_paths:
            dt = path.color / self.speed
            dframe = int(dt*FRAMERATE)
            frame_cnt = int(path.length/self.speed*FRAMERATE)

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
    
    def update_props_from_context(self, context):
        props = context.scene.fd_swarm_planner_props
        self.min_distance, self.speed, self.use_faces = props.min_distance, props.speed, props.use_faces


class SwarmPlanner(bpy.types.Operator, SwarmPlannerBase):
    """Plan drone swarm transition to selected formation"""
    bl_idname = "object.swarm_plan"
    bl_label = "Swarm - Plan transition"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self.update_props_from_context(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class SwarmPlannerButton(bpy.types.Operator, SwarmPlannerBase):
    """Plan drone swarm transition to selected formation"""
    bl_idname = "object.swarm_plan_button"
    bl_label = "Swarm - Plan transition"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self.update_props_from_context(context)
        return self.execute(context)
