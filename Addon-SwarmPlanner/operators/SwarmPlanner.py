import bpy
import bmesh
import numpy as np

from ..planning.classes import *
from ..planning.planner import plan, get_max_time, get_cheapest_flight_paths, paths_to_keyframes
from .ui_lists_operators import draw_select_groups

import logging

log = logging.getLogger(__name__)

def draw_planner(self, context):
    layout = self.layout
    props = context.scene.fd_swarm_planner_props
    method_id = props.planner_method
    vertices_select_method_id = props.vertices_select_method_dropdown
    drone_select_method_id = props.drone_select_method_dropdown
    plan_to_id = props.plan_to_dropdown

    # SELECT
    box = layout.box()
    row = box.row()
    row.label(text="Select settings")
    row = box.row()
    row.prop(props, 'drone_select_method_dropdown', expand=True)
    if drone_select_method_id == 'ALL':
        # all drones
        pass
    elif drone_select_method_id == 'SLTD':
        # selected in scene
        pass
    elif drone_select_method_id == 'GRP':
        draw_select_groups(context, box)
        
    # COLLISIONS
    row = box.row()
    row.label(text="Collisions settings")
    row = box.row()
    row.prop(props, 'planner_method', expand=True)

    if method_id == 'COL':
        row = box.row()
        row.prop(props, 'min_distance')
    elif method_id == 'SMMSH':
        row = box.row()
        row.prop_search(props, "selected_mesh", context.scene, "objects")
    
    row = box.row()
    row.prop(props, 'speed')

    # PLAN TO
    row = box.row()
    row.label(text="Plan to")
    row = box.row()
    row.prop(props, 'plan_to_dropdown', expand=True)
    if plan_to_id == 'VTX' and method_id == 'SMMSH' and props.selected_mesh:
        row = box.row()
        row.prop(props, 'vertices_select_method_dropdown', expand=True)
        if vertices_select_method_id == 'VTXGRP':
            # bpy.types.DATA_PT_vertex_groups.draw(self, context) not really user friendly
            row = box.row()
            row.label(text="Active vertex group of `Same mesh` is used")


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
        draw_planner(self, context)

    def execute(self, context):
        scene = context.scene
        FRAMERATE = scene.render.fps
        self.props = context.scene.fd_swarm_planner_props
        props = self.props
        method_id = self.props.planner_method
        plan_to_id = self.props.plan_to_dropdown
        drone_select_method_id = self.props.drone_select_method_dropdown
        vertices_select_method_id = self.props.vertices_select_method_dropdown

        if (method_id == 'SMMSH' and not self.props.selected_mesh) \
            or (drone_select_method_id == 'SLTD' and method_id == 'COL') \
            or (method_id == 'SMMSH' and plan_to_id == 'VTX' and vertices_select_method_id == 'VTXGRP' and not props.selected_mesh.vertex_groups.active):
            return {'FINISHED'}

        positions_target = self.get_targets_locations(context)
        drone_objects = self.get_drones(context)

        if not drone_objects or not positions_target:
            return {'FINISHED'}

        positions_source = []
        for drone in drone_objects:
            positions_source.append(list(drone.location))

        flight_paths = []
        position_cnt = min(len(positions_source), len(positions_target))
        if method_id == 'COL':
            flight_paths = plan(
                positions_source[:position_cnt],
                positions_target[:position_cnt],
                self.props.min_distance)
        elif (
                not self.props.drone_mapping
                or self.props.prev_plan_to_id != plan_to_id
                or self.props.selected_mesh != self.props.prev_selected_mesh 
                or (plan_to_id == 'VTX' and vertices_select_method_id == 'VTXGRP' and props.selected_mesh.vertex_groups.active_index != props.prev_vertex_group_index)
                or len(positions_target) < len(self.props.drone_mapping)
                or (drone_select_method_id != 'ALL' and {drone.name for drone in drone_objects} != {mapping.drone_name for mapping in self.props.drone_mapping})
            ):
            flight_paths = get_cheapest_flight_paths(
                positions_source[:position_cnt],
                positions_target[:position_cnt])
            self.props.prev_selected_mesh = self.props.selected_mesh
            self.props.prev_plan_to_id = plan_to_id
            try:
                props.prev_vertex_group_index = self.props.selected_mesh.vertex_groups.active_index
            except:
                pass

            self.props.drone_mapping.clear()
            for path in flight_paths:
                path.color = 0
                mapping = self.props.drone_mapping.add()
                mapping.drone_index = path.start_position_index
                mapping.target_index = path.end_position_index
                mapping.drone_name = drone_objects[mapping.drone_index].name
        else:
            for mapping in self.props.drone_mapping:
                path = FlightPath(np.array(positions_source[mapping.drone_index]), np.array(positions_target[mapping.target_index]), mapping.drone_index, mapping.target_index)
                path.color = 0
                flight_paths.append(path)
                mapping.drone_index = path.start_position_index
                mapping.target_index = path.end_position_index
                mapping.drone_name = drone_objects[mapping.drone_index].name

        frame_start = scene.frame_current
        last_frame = int(get_max_time(flight_paths, self.props.speed)*FRAMERATE) + frame_start

        if method_id == 'COL':
            paths_to_keyframes(scene, drone_objects, flight_paths, frame_start, last_frame, self.props.speed, FRAMERATE)
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
        plan_to_id = self.props.plan_to_dropdown
        method_id = self.props.planner_method
        vertices_select_method_id = self.props.vertices_select_method_dropdown
        target_object = context.active_object if method_id == 'COL' else self.props.selected_mesh

        depsgraph = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(target_object, depsgraph)

        if plan_to_id == 'FCS':
            bm.faces.ensure_lookup_table()
            for polygon in bm.faces:
                polygon_global_position = target_object.matrix_world @ polygon.calc_center_median()
                locations.append(list(polygon_global_position))
        else:
            bm.verts.ensure_lookup_table()
            for vertex in bm.verts:
                if vertices_select_method_id == 'VTXGRP':
                    try:
                        bm.verts.layers.deform.verify()
                        group_index = target_object.vertex_groups.active_index
                        deform_layer = bm.verts.layers.deform.active
                        deform_vert = vertex[deform_layer]
                        if deform_vert[group_index] == 0.0:
                            continue
                    except:
                        log.debug("Error get_targets_locations", exc_info=True)
                        continue
                vertex_global_position = target_object.matrix_world @ vertex.co
                locations.append(list(vertex_global_position))
            
        bm.free()
        return locations
    
    def get_drones(self, context):
        scene = context.scene
        drone_select_method_id = self.props.drone_select_method_dropdown
        selected_drones = []
        all_drones = []


        for object in scene.objects:
                if object.name.startswith("Drone"):
                    all_drones.append(object)
                    
        if drone_select_method_id == 'ALL':
            selected_drones = list(all_drones)
        elif drone_select_method_id == 'SLTD':
            selected_drones = [
                drone for drone in all_drones if drone in context.selected_objects
            ]
        elif drone_select_method_id == 'GRP':
            drone_items = []
            if scene.fd_swarm_group_select_index != -1:
                drone_items = scene.fd_swarm_group_select_list[scene.fd_swarm_group_select_index].drones
            selected_drones = list({
                item.drone for item in drone_items if item.drone is not None and scene.objects.get(item.drone.name) is not None
            })

        return selected_drones
