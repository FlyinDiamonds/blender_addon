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
        name="Color",
        subtype="COLOR",
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        size=4,
    )
    background_color_picker: FloatVectorProperty(
        name="Background",
        subtype="COLOR",
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0, 1.0),
        size=4,
    )
    background_color: BoolProperty(name="Override background", default=True)
    fade_out: BoolProperty(name="Fade out", default=False)
    select_method_dropdown: EnumProperty(
        items=fd_select_method_list,
        name="Select method",
        default=0,
        description="Pick method for drone selection",
    )
    selected_mesh: PointerProperty(
        name="Select mesh", type=bpy.types.Object, poll=fd_select_mesh_poll
    )
    random_percentage: IntProperty(
        name="Percentage to select", default=50, min=1, max=100
    )
    invert_selection: BoolProperty(name="Invert selection", default=False)
    step_change: BoolProperty(name="Step change", default=True)
    start_frame: IntProperty(name="Start frame", default=0, min=0)
    end_frame: IntProperty(name="End frame", default=100, min=1)
    frame_duration: IntProperty(name="Frame duration", default=10, min=0)

    def execute(self, context):
        scene = bpy.data.scenes.get("Scene")
        all_drones = self.get_all_drones(context)
        start_frame, end_frame = self.get_frames(context)

        for frame in range(start_frame - 1, end_frame + 2):
            scene.frame_set(frame)
            drones, background_drones = self.sort_drones(context, all_drones)

            for drone in background_drones:
                color = self.get_drone_color(context, True)

            for drone in drones:
                if drone.previous_color is None:
                    pass

                mat = drone.data.materials[0]
                if self.step_change:
                     self.insert_keyframes(frame - 1, drone, mat)

                mat.diffuse_color = color
                drone["custom_color"] = [int(c * 255) for c in list(color)[:3]]

                self.insert_keyframes(frame, drone, mat)

        return {"FINISHED"}

    def insert_keyframes(self, frame, drone, mat):
        mat.keyframe_insert(data_path="diffuse_color", frame=frame)
        drone.keyframe_insert(data_path='["custom_color"]', frame=frame)

    def get_drone_color(self, context, is_background):
        color_method_index = int(self.color_method_dropdown)
        color = None
        if color_method_index == 0:
            color = COLOR_PALLETTE[int(self.color_pallette)]
            # colors_frames = [(start_frame, end_frame, COLOR_PALLETTE[int(self.color_pallette)])]
        elif color_method_index == 1:
            color = self.color_picker
            # colors_frames = [(start_frame, end_frame, self.color_picker)]
        elif color_method_index == 2:
            color = self.color_picker
            # colors_frames = [COLOR_PALLETTE] # TODO picker
        
        return color

    def sort_drones(self, context, all_drones):
        drones = set()
        background_drones = set()
        select_method_index = int(self.select_method_dropdown)
        if select_method_index == 0:
            drones = {
                    drone for drone in all_drones if drone in context.selected_objects
                }
        elif select_method_index == 1:
            if self.selected_mesh:
                drones = {
                        drone
                        for drone in all_drones
                        if is_drone_inside_mesh(drone, self.selected_mesh)
                    }
        elif select_method_index == 2:
            num_of_drones = round(len(all_drones) / 100 * self.random_percentage)
            drones = set(random.sample(all_drones, num_of_drones))

        if self.background_color:
            background_drones = all_drones - drones
        if self.invert_selection:
            drones, background_drones = background_drones, drones
        return drones,background_drones

    def get_all_drones(self, context):
        all_drones = []
        for obj in context.scene.objects:
            if not obj.name.startswith("Drone"):
                continue
            if not hasattr(obj, 'previous_color'):
                obj.previous_color = None
            all_drones.append(obj)
        return all_drones

    def get_frames(self, context):
        frame_method_index = int(self.frame_method_dropdown)
        if frame_method_index == 0:
            start_frame = context.scene.frame_current
            end_frame = start_frame + self.frame_duration
        elif frame_method_index == 1:
            start_frame, end_frame = self.start_frame, self.end_frame
        return start_frame,end_frame

    def update_props_from_context(self, context):
        props = context.scene.fd_swarm_painter_props
        self.select_method_dropdown, self.color_method_dropdown = (
            props.select_method_dropdown,
            props.color_method_dropdown,
        )
        self.color_pallette, self.color_picker, self.color_method_dropdown = (
            props.color_pallette,
            props.color_picker,
            props.color_method_dropdown,
        )
        self.background_color, self.background_color_picker, self.fade_out = (
            props.background_color,
            props.background_color_picker,
            props.fade_out,
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
