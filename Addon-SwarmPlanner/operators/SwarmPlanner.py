import bpy
import bmesh
import numpy as np

from ..planning.classes import *
from ..planning.planner import plan, get_max_time, get_cheapest_flight_paths

def draw_planner(context, layout):
    props = context.scene.fd_swarm_planner_props
    method_index = int(props.planner_method)

    box = layout.box()
    row = box.row()
    row.prop(props, 'planner_method', expand=True)

    row = box.row()
    row.prop(props, 'plan_to_dropdown', expand=True)
    row = box.row()
    row.prop(props, 'speed')

    if method_index == 0:
        row = box.row()
        row.prop(props, 'min_distance')
    elif method_index == 1:
        row = box.row()
        row.prop_search(props, "selected_mesh", context.scene, "objects")


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
    
    def draw(self, context):
        layout = self.layout
        draw_planner(context, layout)

    def execute(self, context):
        scene = context.scene
        FRAMERATE = scene.render.fps
        self.props = context.scene.fd_swarm_planner_props
        method_index = int(self.props.planner_method)
        plan_to_index = int(self.props.plan_to_dropdown)

        if method_index == 1 and not self.props.selected_mesh:
            return {'FINISHED'}

        positions_source = []
        positions_target = self.get_targets_locations(context)
        drone_objects = []

        for object in scene.objects:
            if object.name.startswith("Drone"):
                drone_objects.append(object)
                positions_source.append(list(object.location))

        flight_paths = []
        position_cnt = min(len(positions_source), len(positions_target))
        if method_index == 0:
            flight_paths = plan(
                positions_source[:position_cnt],
                positions_target[:position_cnt],
                self.props.min_distance)
        elif (
                not self.props.drone_mapping 
                or self.props.selected_mesh != self.props.prev_selected_mesh 
                or len(positions_target) < len(self.props.drone_mapping)
                or self.props.prev_plan_to_index != plan_to_index
            ):
            flight_paths = get_cheapest_flight_paths(
                positions_source[:position_cnt],
                positions_target[:position_cnt])
            self.props.prev_selected_mesh = self.props.selected_mesh
            self.props.prev_plan_to_index = plan_to_index
            for path in flight_paths:
                path.color = 0
                mapping = self.props.drone_mapping.add()
                mapping.drone_index = path.start_position_index
                mapping.target_index = path.end_position_index
        else:
            for mapping in self.props.drone_mapping:
                path = FlightPath(np.array(positions_source[mapping.drone_index]), np.array(positions_target[mapping.target_index]), mapping.drone_index, mapping.target_index)
                path.color = 0
                flight_paths.append(path)
                mapping.drone_index = path.start_position_index
                mapping.target_index = path.end_position_index

        frame_start = scene.frame_current
        last_frame = int(get_max_time(flight_paths, self.props.speed)*FRAMERATE) + frame_start

        if method_index == 0:
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
        else:
            if last_frame > context.scene.frame_end:
                context.scene.frame_end = last_frame

            for path in flight_paths:
                current_drone = drone_objects[path.start_position_index]
                current_drone.location = path.start
                current_drone.keyframe_insert(data_path="location", frame=frame_start)

                current_drone.location = path.end
                current_drone.keyframe_insert(data_path="location", frame=last_frame)

                for fcurve in current_drone.animation_data.action.fcurves:
                    for keyframe in fcurve.keyframe_points:
                        keyframe.interpolation = "LINEAR"

        return {'FINISHED'}

    def get_targets_locations(self, context):
        locations = []
        plan_to_index = int(self.props.plan_to_dropdown)
        method_index = int(self.props.planner_method)
        target_object = context.active_object if method_index == 0 else self.props.selected_mesh

        depsgraph = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object( target_object, depsgraph )

        if plan_to_index == 1:
            bm.faces.ensure_lookup_table()
            for polygon in bm.faces:
                polygon_global_position = target_object.matrix_world @ polygon.calc_center_median()
                locations.append(list(polygon_global_position))
        else:
            bm.verts.ensure_lookup_table()
            for vertex in bm.verts:
                vertex_global_position = target_object.matrix_world @ vertex.co
                locations.append(list(vertex_global_position))
            
        bm.free()
        return locations
