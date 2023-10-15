import bpy
from mathutils import Color
from bpy.props import (
    BoolProperty,
    FloatVectorProperty,
    EnumProperty,
    IntProperty,
)

from ..properties.properties import (
    fd_frame_method_list,
    fd_color_method_list,
    fd_color_pallette_list,
    fd_select_method_list,
)
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
    row = box.row()
    row.prop(props, 'invert_selection')


class SwarmPainter(bpy.types.Operator):
    """Set color for selected drones"""
    bl_idname = "object.swarm_painter"
    bl_label = "Swarm Painter"
    bl_options = {"REGISTER", "UNDO"}

    frame_method_dropdown: EnumProperty(
        items=fd_frame_method_list,
        name="Frame method",
        default=0,
        description="Pick method for animation frames",
    )
    color_method_dropdown: EnumProperty(
        items=fd_color_method_list,
        name="Color method",
        default=0,
        description="Pick method for drone painting",
    )
    color_pallette: EnumProperty(
        items=fd_color_pallette_list,
        name="Color pallette",
        default=0,
        description="Pick color from color pallette",
    )
    color_picker: FloatVectorProperty(
             name = "Color",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0, 1.0, 1.0, 1.0),
             size = 4
             )
    background_color_picker: FloatVectorProperty(
             name = "Background color",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (0.0, 0.0, 0.0, 1.0),
             size = 4
             )
    override_background: BoolProperty(name="Override background", default=True)
    select_method_dropdown: EnumProperty(
        items=fd_select_method_list,
        name="Select method",
        default=0,
        description="Pick method for drone selection",
    )
    # selected_mesh: PointerProperty(name="Select mesh", type=bpy.types.Object, poll=fd_select_mesh_poll)
    random_percentage: IntProperty(name="Percentage to select", default=50, min=1, max=100)
    invert_selection: BoolProperty(name="Invert selection", default=False)
    start_frame: IntProperty(name="Start frame", default=0, min=0)
    end_frame: IntProperty(name="End frame", default=100, min=1)
    frame_duration: IntProperty(name="Frame duration", default=10, min=0, max=1000)
    frame_step: IntProperty(name="Frame step", default=1, min=1, max=100)
    transition_color_picker: FloatVectorProperty(
             name = "Transition from",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0, 1.0, 1.0, 1.0),
             size = 4
    )
    transition_color_picker_snd: FloatVectorProperty(
             name = "Transition to",
             subtype = "COLOR",
             min = 0.0,
             max = 1.0,
             default = (1.0, 1.0, 1.0, 1.0),
             size = 4
    )

    all_drones = set()
    inner_color = None
    prev_inner_color = None
    keyframes_to_delete = []
    keyframes_to_insert = []
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
    
    def draw(self, context):
        layout = self.layout
        draw_painter(context, layout)
        

    def execute(self, context):
        scene = bpy.data.scenes.get("Scene")
        init_frame = scene.frame_current
        self.reset_class_attributes()
        self.resolve_all_drones(context)
        start_frame, end_frame, duration = self.get_frames(context)
        start_modulo = start_frame % self.frame_step

        for frame in range(start_frame - 1, end_frame + 2):
            self.resolve_current_colors(frame)

            if frame == start_frame - 1:
                continue

            self.resolve_inner_colors(frame - start_frame, duration)
            self.resolve_keyframes_to_delete(frame)
            
            if frame not in (start_frame, end_frame, end_frame + 1) and frame % self.frame_step != start_modulo:
                continue

            self.resolve_selection(context, scene, frame)
            self.resolve_keyframes_to_add(start_frame, end_frame, frame)

        self.delete_keyframes()
        self.insert_keyframes()
        self.set_init_frame(scene, init_frame)

        return {"FINISHED"}

    def reset_class_attributes(self):
        self.all_drones = set()
        self.inner_color = None
        self.prev_inner_color = None
        self.keyframes_to_delete = []
        self.keyframes_to_insert = []

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
        frame_method_index = int(self.frame_method_dropdown)
        if frame_method_index == 0:
            start_frame = context.scene.frame_current
            end_frame = start_frame + self.frame_duration
        elif frame_method_index == 1:
            start_frame, end_frame = self.start_frame, self.end_frame
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

        color_method_index = int(self.color_method_dropdown)
        color = None

        if color_method_index == 0:
            color = COLOR_PALLETTE[int(self.color_pallette)]
        elif color_method_index == 1:
            color = self.color_picker
        elif color_method_index == 2:
            color_parts = []

            for i in range(4):
                fst_rgba_part = self.transition_color_picker[i]
                snd_rgba_part = self.transition_color_picker_snd[i]
                color_parts.append(fst_rgba_part + (snd_rgba_part - fst_rgba_part) / duration * frame)
            color = tuple(color_parts)

        self.inner_color = color
    
    def resolve_keyframes_to_delete(self, frame):
        for drone in self.all_drones:
            if self.override_background or drone['selected']:
                self.keyframes_to_delete.append((drone, frame))

    def resolve_selection(self, context, scene, frame):
        select_method_index = int(self.select_method_dropdown)
        selected_drones = set()
        if select_method_index == 0:
            selected_drones = {
                drone for drone in self.all_drones if drone in context.selected_objects
            }
        elif select_method_index == 1:
            scene.frame_set(frame)
            if self.selected_mesh:
                selected_drones = {
                    drone
                    for drone in self.all_drones
                    if is_drone_inside_mesh(drone, self.selected_mesh)
                }
        elif select_method_index == 2:
            num_of_drones = round(len(self.all_drones) / 100 * self.random_percentage)
            selected_drones = set(random.sample(self.all_drones, num_of_drones))

        if self.invert_selection:
            selected_drones = self.all_drones - selected_drones
        
        for drone in self.all_drones:
            drone['prev_selected'] = drone['selected']
            drone['selected'] = drone in selected_drones
    
    def resolve_keyframes_to_add(self, start_frame, end_frame, frame):
        for drone in self.all_drones:
            self.resolve_prev_frame(drone, start_frame, end_frame, frame)
            self.resolve_cur_frame(drone, start_frame, end_frame, frame)

    def resolve_prev_frame(self, drone, start_frame, end_frame, frame):
        if frame == start_frame and (drone['selected'] or self.override_background):
            self.keyframes_to_insert.append((frame - 1, drone,  copy_color(drone['prev_frame_color'])))
        elif not drone['prev_selected'] and drone['selected']:
            self.keyframes_to_insert.append((frame - 1, drone, copy_color(self.background_color_picker
                                                                         if self.override_background else drone['prev_frame_color'])))
        elif drone['prev_selected'] and (not drone['selected'] or frame == end_frame + 1):
            self.keyframes_to_insert.append((frame - 1, drone, copy_color(self.prev_inner_color)))
        elif frame == end_frame + 1 and self.override_background:
            self.keyframes_to_insert.append((frame - 1, drone, copy_color(self.background_color_picker)))
    
    def resolve_cur_frame(self, drone, start_frame, end_frame, frame):
        if frame == start_frame:
            if drone['selected']:
                self.keyframes_to_insert.append((frame, drone, copy_color(self.inner_color)))
            elif self.override_background:
                self.keyframes_to_insert.append((frame, drone, copy_color(self.background_color_picker)))
        elif frame == end_frame + 1 and (drone['selected'] or self.override_background):
            self.keyframes_to_insert.append((frame, drone, copy_color(drone['cur_frame_color'])))
        elif not drone['prev_selected'] and drone['selected']:
            self.keyframes_to_insert.append((frame, drone, copy_color(self.inner_color)))
        elif drone['prev_selected'] and not drone['selected']:
            self.keyframes_to_insert.append((frame, drone, copy_color(self.background_color_picker
                                                                         if self.override_background else drone['cur_frame_color'])))
    
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
        
    def update_props_from_context(self, context):
        props = context.scene.fd_swarm_painter_props
        self.select_method_dropdown, self.color_method_dropdown, self.frame_method_dropdown = (
            props.select_method_dropdown,
            props.color_method_dropdown,
            props.frame_method_dropdown,
        )
        self.color_pallette, self.color_picker, self.color_method_dropdown = (
            props.color_pallette,
            props.color_picker,
            props.color_method_dropdown,
        )
        self.override_background, self.background_color_picker = (
            props.override_background,
            props.background_color_picker,
        )
        self.selected_mesh, self.invert_selection, self.random_percentage = (
            props.selected_mesh,
            props.invert_selection,
            props.random_percentage,
        )
        self.start_frame, self.end_frame, self.frame_duration, self.frame_step = (
            props.start_frame,
            props.end_frame,
            props.frame_duration,
            props.frame_step
        )
        self.transition_color_picker, self.transition_color_picker_snd = (
            props.transition_color_picker,
            props.transition_color_picker_snd
        )
