import bpy

from ..utils.drone_in_mesh import is_drone_inside_mesh

import random


COLOR_PALLETTE = [
    (1.0, 1.0, 1.0, 1.0),
    (0.0, 0.0, 0.0, 1.0),
    (1.0, 0.0, 0.0, 1.0),
    (0.0, 1.0, 0.0, 1.0),
    (0.0, 0.0, 1.0, 1.0),
]

def copy_color(color):
    """Use instead of deepcopy, which fails on diffuse_color"""
    return (color[0], color[1], color[2], color[3])

def draw_painter(context, layout):
    props = context.scene.fd_swarm_painter_props
    # FRAMES
    frame_method_index = int(props.frame_method_dropdown)

    box = layout.box()
    row = box.row()
    row.label(text="Frames settings")
    row = box.row()
    row.prop(props, 'frame_method_dropdown', expand=True)
    if frame_method_index == 0:
        row = box.row()
        row.prop(props, 'frame_duration', expand=True)
    elif frame_method_index == 1:
        row = box.row()
        row.prop(props, 'start_frame', expand=True)
        row.prop(props, 'end_frame', expand=True)
    row = box.row()
    row.prop(props, 'frame_step', expand=True)

    # COLOR
    color_method_index = int(props.color_method_dropdown)

    box = layout.box()
    row = box.row()
    row.label(text="Color settings")
    row = box.row()
    row.prop(props, 'color_method_dropdown', expand=True)
    if color_method_index == 0:
        row = box.row()
        row.prop(props, 'color_pallette', expand=True)
    elif color_method_index == 1:
        row = box.row()
        row.prop(props, 'color_picker')
    elif color_method_index == 2:
        row = box.row()
        row.prop(props, 'transition_color_picker')
        row = box.row()
        row.prop(props, 'transition_color_picker_snd')
    row = box.row()
    col = row.column()
    col.prop(props, 'override_background')
    col = row.column()
    col.prop(props, 'background_color_picker')
    if not props.override_background:
        col.enabled = False
    row = box.row()
    
    # SELECT
    select_method_index = int(props.select_method_dropdown)

    box = layout.box()
    row = box.row()
    row.label(text="Select settings")
    row = box.row()
    row.prop(props, 'select_method_dropdown', expand=True)
    if select_method_index == 0:
        # selected in scene
        pass
    elif select_method_index == 1:
        row = box.row()
        row.prop_search(props, "selected_mesh", context.scene, "objects")
    elif select_method_index == 2:
        row = box.row()
        row.prop(props, 'random_percentage')
    elif select_method_index == 3:
        scn = context.scene
        row = box.row()
        
        rows = 4
        row.template_list("FD_UL_groups", "fd_swarm_group_select_list_ui", scn, "fd_swarm_group_select_list", 
            scn, "fd_swarm_group_select_index", rows=rows)

        col = row.column(align=True)

        index = "fd_swarm_group_select_index"
        path = "fd_swarm_group_select_list"

        op = col.operator("fd.ui_list_add", icon='ADD', text="")
        op.scene_index_name = index
        op.scene_path = path

        op = col.operator("fd.ui_list_remove", icon='REMOVE', text="")
        op.scene_index_name = index
        op.scene_path = path

        op = col.operator("fd.ui_list_move", icon='TRIA_UP', text="")
        op.scene_index_name = index
        op.scene_path = path
        op.action = "UP"

        op = col.operator("fd.ui_list_move", icon='TRIA_DOWN', text="")
        op.scene_index_name = index
        op.scene_path = path
        op.action = "DOWN"

        group_select_index = scn.fd_swarm_group_select_index
        group_select_list = scn.fd_swarm_group_select_list

        if group_select_index != -1:
            row = box.row()
            
            row.template_list("FD_UL_drones", "fd_swarm_group_select_drone_list_ui", group_select_list[group_select_index], "drones", 
                scn, "fd_swarm_group_select_drone_index", rows=rows)
            
            col = row.column(align=True)
            
            index = "fd_swarm_group_select_drone_index"
            path = f"fd_swarm_group_select_list[{scn.fd_swarm_group_select_index}].drones"

            op = col.operator("fd.ui_list_add", icon='ADD', text="")
            op.scene_index_name = index
            op.scene_path = path

            op = col.operator("fd.ui_list_remove", icon='REMOVE', text="")
            op.scene_index_name = index
            op.scene_path = path

            op = col.operator("fd.ui_list_move", icon='TRIA_UP', text="")
            op.scene_index_name = index
            op.scene_path = path
            op.action = "UP"

            op = col.operator("fd.ui_list_move", icon='TRIA_DOWN', text="")
            op.scene_index_name = index
            op.scene_path = path
            op.action = "DOWN"

            row = box.row()
            op = row.operator("fd.ui_list_add_selected", icon='ADD', text="Add selected")
            op.scene_index_name = index
            op.scene_path = path

            op = row.operator("fd.ui_list_remove_selected", icon='REMOVE', text="Remove selected")
            op.scene_index_name = index
            op.scene_path = path

            row = box.row()
            op = row.operator("fd.ui_list_select", icon='RESTRICT_SELECT_OFF')
            op.scene_index_name = index
            op.scene_path = path

            op = row.operator("fd.ui_list_deselect", icon='RESTRICT_SELECT_ON')
            op.scene_index_name = index
            op.scene_path = path

    row = box.row()
    row.prop(props, 'invert_selection')


class SwarmPainter(bpy.types.Operator):
    """Set color for selected drones"""
    bl_idname = "object.swarm_painter"
    bl_label = "Swarm Painter"
    bl_options = {"REGISTER", "UNDO"}

    is_button: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def __init__(self):
        self.props = None
        self.all_drones = set()
        self.inner_color = None
        self.prev_inner_color = None
        self.keyframes_to_delete = []
        self.keyframes_to_insert = []

    def invoke(self, context, event):
        if self.is_button:
            self.is_button = False
            return self.execute(context)
        else:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        draw_painter(context, layout)
        

    def execute(self, context):
        scene = bpy.data.scenes.get("Scene")
        init_frame = scene.frame_current
        self.props = context.scene.fd_swarm_painter_props
        self.resolve_all_drones(context)
        start_frame, end_frame, duration = self.get_frames(context)
        start_modulo = start_frame % self.props.frame_step

        for frame in range(start_frame - 1, end_frame + 2):
            self.resolve_current_colors(frame)

            if frame == start_frame - 1:
                continue

            self.resolve_inner_colors(frame - start_frame, duration)
            self.resolve_keyframes_to_delete(frame)
            
            if frame not in (start_frame, end_frame, end_frame + 1) and frame % self.props.frame_step != start_modulo:
                continue

            self.resolve_selection(context, scene, frame)
            self.resolve_keyframes_to_add(start_frame, end_frame, frame)

        self.delete_keyframes()
        self.insert_keyframes()
        self.set_init_frame(scene, init_frame)

        return {"FINISHED"}

    def resolve_all_drones(self, context):
        for obj in context.scene.objects:
            if not obj.name.startswith("Drone"):
                continue
            obj['prev_frame_color'] = None
            obj['cur_frame_color'] = None
            obj['prev_selected'] = False
            obj['selected'] = False
            self.all_drones.add(obj)
    
    def get_frames(self, context):
        frame_method_index = int(self.props.frame_method_dropdown)
        if frame_method_index == 0:
            start_frame = context.scene.frame_current
            end_frame = start_frame + self.props.frame_duration
        elif frame_method_index == 1:
            start_frame, end_frame = self.props.start_frame, self.props.end_frame
        return start_frame, end_frame, end_frame - start_frame
    
    def resolve_current_colors(self, frame):
        for drone in self.all_drones:
            if drone['cur_frame_color']:
                drone['prev_frame_color'] = copy_color(drone['cur_frame_color'])
            
            material = drone.data.materials[0]
            diffuse_color = COLOR_PALLETTE[1]
            if material.animation_data:
                diffuse_color = (
                    material.animation_data.action.fcurves[0].evaluate(frame),
                    material.animation_data.action.fcurves[1].evaluate(frame),
                    material.animation_data.action.fcurves[2].evaluate(frame),
                    material.animation_data.action.fcurves[3].evaluate(frame),
                )

            drone['cur_frame_color'] = copy_color(diffuse_color)
    
    def resolve_inner_colors(self, frame, duration):
        self.prev_inner_color = self.inner_color

        color_method_index = int(self.props.color_method_dropdown)
        color = None

        if color_method_index == 0:
            color = COLOR_PALLETTE[int(self.props.color_pallette)]
        elif color_method_index == 1:
            color = self.props.color_picker
        elif color_method_index == 2:
            color_parts = []

            for i in range(4):
                fst_rgba_part = self.props.transition_color_picker[i]
                snd_rgba_part = self.props.transition_color_picker_snd[i]
                color_parts.append(fst_rgba_part + (snd_rgba_part - fst_rgba_part) / duration * frame)
            color = tuple(color_parts)

        self.inner_color = color
    
    def resolve_keyframes_to_delete(self, frame):
        for drone in self.all_drones:
            if self.props.override_background or drone['selected']:
                self.keyframes_to_delete.append((drone, frame))

    def resolve_selection(self, context, scene, frame):
        select_method_index = int(self.props.select_method_dropdown)
        selected_drones = set()

        if select_method_index == 0:
            selected_drones = {
                drone for drone in self.all_drones if drone in context.selected_objects
            }
        elif select_method_index == 1:
            scene.frame_set(frame)
            if self.props.selected_mesh:
                selected_drones = {
                    drone
                    for drone in self.all_drones
                    if is_drone_inside_mesh(drone, self.props.selected_mesh)
                }
        elif select_method_index == 2:
            num_of_drones = round(len(self.all_drones) / 100 * self.props.random_percentage)
            selected_drones = set(random.sample(self.all_drones, num_of_drones))
        elif select_method_index == 3:
            drone_items = []
            if scene.fd_swarm_group_select_index != -1:
                drone_items = scene.fd_swarm_group_select_list[scene.fd_swarm_group_select_index].drones
            selected_drones = {
                item.drone for item in drone_items if item.drone is not None and scene.objects.get(item.drone.name) is not None
            }

        if self.props.invert_selection:
            selected_drones = self.all_drones - selected_drones
        
        for drone in self.all_drones:
            drone['prev_selected'] = drone['selected']
            drone['selected'] = drone in selected_drones
    
    def resolve_keyframes_to_add(self, start_frame, end_frame, frame):
        for drone in self.all_drones:
            self.resolve_prev_frame(drone, start_frame, end_frame, frame)
            self.resolve_cur_frame(drone, start_frame, end_frame, frame)

    def resolve_prev_frame(self, drone, start_frame, end_frame, frame):
        if frame == start_frame and (drone['selected'] or self.props.override_background):
            self.keyframes_to_insert.append((frame - 1, drone,  copy_color(drone['prev_frame_color'])))
        elif not drone['prev_selected'] and drone['selected']:
            self.keyframes_to_insert.append((frame - 1, drone, copy_color(self.props.background_color_picker
                                                                         if self.props.override_background else drone['prev_frame_color'])))
        elif drone['prev_selected'] and (not drone['selected'] or frame == end_frame + 1):
            self.keyframes_to_insert.append((frame - 1, drone, copy_color(self.prev_inner_color)))
        elif frame == end_frame + 1 and self.props.override_background:
            self.keyframes_to_insert.append((frame - 1, drone, copy_color(self.props.background_color_picker)))
    
    def resolve_cur_frame(self, drone, start_frame, end_frame, frame):
        if frame == start_frame:
            if drone['selected']:
                self.keyframes_to_insert.append((frame, drone, copy_color(self.inner_color)))
            elif self.props.override_background:
                self.keyframes_to_insert.append((frame, drone, copy_color(self.props.background_color_picker)))
        elif frame == end_frame + 1 and (drone['selected'] or self.props.override_background):
            self.keyframes_to_insert.append((frame, drone, copy_color(drone['cur_frame_color'])))
        elif not drone['prev_selected'] and drone['selected']:
            self.keyframes_to_insert.append((frame, drone, copy_color(self.inner_color)))
        elif drone['prev_selected'] and not drone['selected']:
            self.keyframes_to_insert.append((frame, drone, copy_color(self.props.background_color_picker
                                                                         if self.props.override_background else drone['cur_frame_color'])))
    
    def insert_keyframes(self):
        for frame, drone, diffuse_color in self.keyframes_to_insert:
            mat = drone.data.materials[0]
            mat.diffuse_color = diffuse_color
            drone["custom_color"] = [int(c * 255) for c in list(diffuse_color)[:3]]
            # print(f"Inserting keyframes on frame {frame} mat {diffuse_color}")
            mat.keyframe_insert(data_path="diffuse_color", frame=frame)
            drone.keyframe_insert(data_path='["custom_color"]', frame=frame)
    
    def delete_keyframes(self):
        for drone, frame in self.keyframes_to_delete:
            # print(f"Deleting keyframes on frame {frame}")
            mat = drone.data.materials[0]
            if bpy.data.materials[mat.name].animation_data.action is not None:
                mat.keyframe_delete(data_path="diffuse_color", frame=frame)
            if bpy.data.objects[drone.name].animation_data.action is not None:
                drone.keyframe_delete(data_path='["custom_color"]', frame=frame)
    
    def set_init_frame(self, scene, init_frame):
        if init_frame != scene.frame_current:
            scene.frame_set(init_frame)
