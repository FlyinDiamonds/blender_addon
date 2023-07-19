import bpy
from mathutils import Color
from bpy.props import (
    BoolProperty,
    FloatVectorProperty,
    EnumProperty,
    IntProperty,
    FloatProperty,
    PointerProperty,
)

from ..properties.properties import (
    fd_frame_method_list,
    fd_color_method_list,
    fd_color_pallette_list,
    fd_select_method_list,
    fd_select_mesh_poll,
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


class SwarmPainterBase:
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
    background_color: BoolProperty(name="Override background", default=True)
    select_method_dropdown: EnumProperty(
        items=fd_select_method_list,
        name="Select method",
        default=0,
        description="Pick method for drone selection",
    )
    selected_mesh: PointerProperty(name="Select mesh", type=bpy.types.Object, poll=fd_select_mesh_poll)
    random_percentage: IntProperty(name="Percentage to select", default=50, min=1, max=100)
    invert_selection: BoolProperty(name="Invert selection", default=False)
    step_change: BoolProperty(name="Step change", default=True)
    start_frame: IntProperty(name="Start frame", default=0, min=0)
    end_frame: IntProperty(name="End frame", default=100, min=1)
    frame_duration: IntProperty(name="Frame duration", default=10, min=0)

    def execute(self, context):
        scene = bpy.data.scenes.get("Scene")
        all_drones = self.get_all_drones(context)
        start_frame, end_frame = self.get_frames(context)
        keyframes = []
        keyframes_to_delete = []
        inner_color = None

        for frame in range(start_frame - 1, end_frame + 2):
            scene.frame_set(frame)
            self.set_colors_on_frames(all_drones)

            if frame == start_frame - 1:
                continue

            prev_inner_color = inner_color
            inner_color = self.resolve_inner_color(frame)
            self.resolve_selection(context, all_drones)

            for drone in all_drones:
                self.resolve_prev_frame(drone, keyframes, start_frame, end_frame, frame, prev_inner_color)
                if self.background_color or drone['selected']:
                    keyframes_to_delete.append((drone, frame))
                self.resolve_cur_frame(drone, keyframes, start_frame, end_frame, frame, inner_color)

        self.delete_keyframes(keyframes_to_delete)
        self.insert_keyframes(keyframes)

        return {"FINISHED"}

    def resolve_prev_frame(self, drone, keyframes, start_frame, end_frame, frame, prev_inner_color):
        if frame == start_frame and (drone['selected'] or self.background_color):
            keyframes.append((frame - 1, drone,  copy_color(drone['prev_frame_color'])))
        elif not drone['prev_selected'] and drone['selected']:
            keyframes.append((frame - 1, drone, copy_color(self.background_color_picker
                                                                         if self.background_color else drone['prev_frame_color'])))
        elif drone['prev_selected'] and (not drone['selected'] or frame == end_frame + 1):
            keyframes.append((frame - 1, drone, copy_color(prev_inner_color)))
        elif frame == end_frame + 1 and self.background_color:
            keyframes.append((frame - 1, drone, copy_color(self.background_color_picker)))
    
    def resolve_cur_frame(self, drone, keyframes, start_frame, end_frame, frame, inner_color):
        if frame == start_frame:
            if drone['selected']:
                keyframes.append((frame, drone, copy_color(inner_color)))
            elif self.background_color:
                keyframes.append((frame, drone, copy_color(self.background_color_picker)))
        elif frame == end_frame + 1 and (drone['selected'] or self.background_color):
            keyframes.append((frame, drone, copy_color(drone['cur_frame_color'])))
        elif not drone['prev_selected'] and drone['selected']:
            keyframes.append((frame, drone, copy_color(inner_color)))
        elif drone['prev_selected'] and not drone['selected']:
            keyframes.append((frame, drone, copy_color(self.background_color_picker
                                                                         if self.background_color else drone['cur_frame_color'])))

    def set_colors_on_frames(self, all_drones):
        for drone in all_drones:
            if drone['cur_frame_color']:
                drone['prev_frame_color'] = copy_color(drone['cur_frame_color'])
            drone['cur_frame_color'] = copy_color(drone.data.materials[0].diffuse_color)
        
    def resolve_inner_color(self, frame):
        color_method_index = int(self.color_method_dropdown)
        color = None

        if color_method_index == 0:
            color = COLOR_PALLETTE[int(self.color_pallette)]
        elif color_method_index == 1:
            color = self.color_picker
        elif color_method_index == 2:
            # TODO find value for color
            pass

        return color

    def resolve_selection(self, context, all_drones):
        select_method_index = int(self.select_method_dropdown)
        selected_drones = set()
        if select_method_index == 0:
            selected_drones = {
                drone for drone in all_drones if drone in context.selected_objects
            }
        elif select_method_index == 1:
            if self.selected_mesh:
                selected_drones = {
                    drone
                    for drone in all_drones
                    if is_drone_inside_mesh(drone, self.selected_mesh)
                }
        elif select_method_index == 2:
            num_of_drones = round(len(all_drones) / 100 * self.random_percentage)
            selected_drones = set(random.sample(all_drones, num_of_drones))

        if self.invert_selection:
            selected_drones = all_drones - selected_drones
        
        for drone in all_drones:
            drone['prev_selected'] = drone['selected']
            drone['selected'] = drone in selected_drones

    def get_all_drones(self, context):
        all_drones = set()
        for obj in context.scene.objects:
            if not obj.name.startswith("Drone"):
                continue
            obj['prev_frame_color'] = None
            obj['cur_frame_color'] = None
            obj['prev_selected'] = False
            obj['selected'] = False
            all_drones.add(obj)
        return all_drones

    def get_frames(self, context):
        frame_method_index = int(self.frame_method_dropdown)
        if frame_method_index == 0:
            start_frame = context.scene.frame_current
            end_frame = start_frame + self.frame_duration
        elif frame_method_index == 1:
            start_frame, end_frame = self.start_frame, self.end_frame
        return start_frame, end_frame
    
    def insert_keyframes(self, keyframes):
        for frame, drone, diffuse_color in keyframes:
            mat = drone.data.materials[0]
            mat.diffuse_color = diffuse_color
            drone["custom_color"] = [int(c * 255) for c in list(diffuse_color)[:3]]
            print(f"Inserting keyframes on frame {frame} mat {diffuse_color}")
            mat.keyframe_insert(data_path="diffuse_color", frame=frame)
            drone.keyframe_insert(data_path='["custom_color"]', frame=frame)
    
    def delete_keyframes(self, keyframes_to_delete):
        for drone, frame in keyframes_to_delete:
            print(f"Deleting keyframes on frame {frame}")
            mat = drone.data.materials[0]
            mat.keyframe_delete(data_path="diffuse_color", frame=frame)
            drone.keyframe_delete(data_path='["custom_color"]', frame=frame)
        
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
        self.background_color, self.background_color_picker = (
            props.background_color,
            props.background_color_picker,
        )
        self.step_change = props.step_change
        self.selected_mesh, self.invert_selection, self.random_percentage = (
            props.selected_mesh,
            props.invert_selection,
            props.random_percentage,
        )
        self.start_frame, self.end_frame, self.frame_duration = (
            props.start_frame,
            props.end_frame,
            props.frame_duration,
        )


class SwarmPainter(bpy.types.Operator, SwarmPainterBase):
    """Set color for selected drones"""
    bl_idname = "object.swarm_painter"
    bl_label = "Swarm - Set color"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        self.update_props_from_context(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class SwarmPainterButton(bpy.types.Operator, SwarmPainterBase):
    """Set color for selected drones"""

    bl_idname = "object.swarm_painter_button"
    bl_label = "Swarm - Set color"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        self.update_props_from_context(context)
        return self.execute(context)
