import bpy

from ..planning.planner import plan, get_max_time


class SwarmPlanner(bpy.types.Operator):
    """Plan drone swarm transition to selected formation"""
    bl_idname = "object.swarm_plan"
    bl_label = "Swarm - Plan transition"
    bl_options = {'REGISTER', 'UNDO'}
    is_button: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def __init__(self):
        self.props = None

    def invoke(self, context, event):
        if self.is_button:
            self.is_button = False
            return self.execute(context)
        else:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

    def execute(self, context):
        scene = context.scene
        FRAMERATE = scene.render.fps
        self.props = context.scene.fd_swarm_planner_props

        positions_source = []
        positions_target = []

        drone_objects = []

        for object in scene.objects:
            if object.name.startswith("Drone"):
                drone_objects.append(object)
                positions_source.append(list(object.location))

        positions_target = self.get_targets_locations(context)

        position_cnt = min(len(positions_source), len(positions_target))
        flight_paths = plan(
            positions_source[:position_cnt],
            positions_target[:position_cnt],
            self.props.min_distance)

        frame_start = scene.frame_current
        last_frame = int(get_max_time(flight_paths, self.props.speed)*FRAMERATE) + frame_start
        for path in flight_paths:
            dt = path.color / self.props.speed
            dframe = int(dt*FRAMERATE)
            frame_cnt = int(path.length/self.props.speed*FRAMERATE)

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

    def get_targets_locations(self, context):
        locations = []
        plan_to_index = int(self.props.plan_to_dropdown)
        method_index = int(self.props.planner_method)
        target_object = context.active_object if method_index == 0 else self.props.selected_mesh

        if plan_to_index == 1:
            for polygon in target_object.data.polygons:
                polygon_global_position = target_object.matrix_world @ polygon.center
                locations.append(list(polygon_global_position))
        else:
            for vertex in target_object.data.vertices:
                vertex_global_position = target_object.matrix_world @ vertex.co
                locations.append(list(vertex_global_position))
        return locations
