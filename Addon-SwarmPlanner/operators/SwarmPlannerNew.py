from typing import Dict, List
import bpy
from ..planning.classes import *
import numpy as np

from ..planning.planner import get_max_time, get_cheapest_flight_paths


class SwarmPlannerNew(bpy.types.Operator):
    """Plan drone swarm transition to selected formation"""
    bl_idname = "object.swarm_plan_new"
    bl_label = "Swarm - Plan transition New"
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
        props = context.scene.fd_swarm_planner_props

        box = layout.box()
        row = box.row()
        row.label(text="SELECT")
        row = box.row()
        row.prop_search(props, "selected_mesh", context.scene, "objects")


    def execute(self, context):
        scene = context.scene
        FRAMERATE = scene.render.fps
        self.props = context.scene.fd_swarm_planner_props

        positions_target = self.get_targets_locations()
        positions_source = []

        drone_objects = []

        for object in scene.objects:
            if object.name.startswith("Drone"):
                drone_objects.append(object)
                positions_source.append(list(object.location))

        flight_paths = []
        if not self.props.drone_mapping or self.props.selected_mesh != self.props.prev_selected_mesh:
            # position_cnt = min(len(positions_source), len(positions_target))
            flight_paths = get_cheapest_flight_paths(
                positions_source,
                positions_target)
            for path in flight_paths:
                mapping = self.props.drone_mapping.add()
                mapping.drone_index = path.start_position_index
                mapping.target_index = path.end_position_index
            self.props.prev_selected_mesh = self.props.selected_mesh
        else:
            for mapping in self.props.drone_mapping:
                path = FlightPath(np.array(positions_source[mapping.drone_index]), np.array(positions_target[mapping.target_index]), mapping.drone_index, mapping.target_index)
                flight_paths.append(path)
                mapping.drone_index = path.start_position_index
                mapping.target_index = path.end_position_index

        for path in flight_paths:
            path.color = 0

        frame_start = scene.frame_current
        last_frame = int(get_max_time(flight_paths, self.props.speed)*FRAMERATE) + frame_start

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
    
    def get_targets_locations(self) -> List[float]:
        locations = []

        if self.props.use_faces: # == "FACES":
            for polygon in self.props.selected_mesh.data.polygons:
                polygon_global_position = self.props.selected_mesh.matrix_world @ polygon.center
                locations.append(list(polygon_global_position))
        elif self.props.use_faces == "EDGES":
            pass
        else:
            for vertex in self.props.selected_mesh.data.vertices:
                vertex_global_position = self.props.selected_mesh.matrix_world @ vertex.co
                locations.append(list(vertex_global_position))
        return locations
