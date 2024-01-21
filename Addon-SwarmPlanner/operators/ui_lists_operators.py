import bpy

from bpy.props import EnumProperty, StringProperty

class UIListOperatorBase:
    scene_index_name: StringProperty()
    scene_path: StringProperty()

    def __init__(self) -> None:
        self.index = -1
        self.collection = None

    def resolve_attr(self, context):
        scn = context.scene
        self.index = getattr(scn, self.scene_index_name)
        path = self.scene_path.replace("[", ".").replace("]", "").split(".")

        try:
            path_obj = scn
            for path_item in path:
                try:
                    path_obj = path_obj[int(path_item)]
                except ValueError:
                    path_obj = getattr(path_obj, path_item)
            self.collection = path_obj
        except (IndexError, AttributeError):
            pass

class UIListOperatorAdd(bpy.types.Operator, UIListOperatorBase):
    """Add item to group"""
    bl_idname = "fd.ui_list_add"
    bl_label = "List add"
    bl_description = "Add item to group"
    bl_options = {'REGISTER'}


    def invoke(self, context, event):
        self.resolve_attr(context)
        scn = context.scene

        if self.collection is not None:
            item = self.collection.add()
            item.id = len(self.collection)
            setattr(scn, self.scene_index_name, len(self.collection) - 1)

        return {"FINISHED"}


class UIListOperatorRemove(bpy.types.Operator, UIListOperatorBase):
    """Remove item from group"""
    bl_idname = "fd.ui_list_remove"
    bl_label = "List remove"
    bl_description = "Remove item from group"
    bl_options = {'REGISTER'}


    def invoke(self, context, event):
        self.resolve_attr(context)
        scn = context.scene

        if self.index != -1 and self.collection is not None:
            self.collection.remove(self.index)
            setattr(scn, self.scene_index_name, self.index - 1)

        return {"FINISHED"}


class UIListOperatorMove(bpy.types.Operator, UIListOperatorBase):
    """Move item up or down"""
    bl_idname = "fd.ui_list_move"
    bl_label = "List move"
    bl_description = "Move item up or down"
    bl_options = {'REGISTER'}

    action: EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", "")
        ))


    def invoke(self, context, event):
        self.resolve_attr(context)
        scn = context.scene

        if self.collection is not None:
            if self.action == 'DOWN' and self.index < len(self.collection) - 1:
                self.collection.move(self.index, self.index + 1)
                setattr(scn, self.scene_index_name, self.index + 1)
            elif self.action == 'UP' and self.index >= 1:
                self.collection.move(self.index, self.index - 1)
                setattr(scn, self.scene_index_name, self.index - 1)
        return {"FINISHED"}
    
class UIListOperatorAddSelected(bpy.types.Operator, UIListOperatorBase):
    """Add selected drones to group"""
    bl_idname = "fd.ui_list_add_selected"
    bl_label = "List add selected"
    bl_description = "Add selected drones to group"
    bl_options = {'REGISTER'}


    def invoke(self, context, event):
        self.resolve_attr(context)
        scn = context.scene

        selected_drones = {obj for obj in context.selected_objects if obj.type == 'MESH' and obj.name.startswith("Drone")}

        if self.collection is not None:
            for drone in selected_drones:
                if all(drone != item.drone for item in self.collection):
                    item = self.collection.add()
                    item.id = len(self.collection)
                    item.drone = drone
                    setattr(scn, self.scene_index_name, len(self.collection) - 1)

        return {"FINISHED"}

class UIListOperatorRemoveSelected(bpy.types.Operator, UIListOperatorBase):
    """Remove selected drones from group"""
    bl_idname = "fd.ui_list_remove_selected"
    bl_label = "List remove selected"
    bl_description = "Remove selected drones from group"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        self.resolve_attr(context)
        scn = context.scene

        selected_drones = {obj for obj in context.selected_objects if obj.type == 'MESH' and obj.name.startswith("Drone")}

        if self.collection is not None:
            for drone in selected_drones:
                for i, item in enumerate(self.collection):
                    if item.drone == drone:
                        self.collection.remove(i)
                        setattr(scn, self.scene_index_name, len(self.collection) - 1)

        return {"FINISHED"}

class UIListOperatorSelect(bpy.types.Operator, UIListOperatorBase):
    """Select drones from group"""
    bl_idname = "fd.ui_list_select"
    bl_label = "Select"
    bl_description = "Select drones from group"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        self.resolve_attr(context)

        if self.collection is not None:
            for item in self.collection:
                if item.drone is not None and context.scene.objects.get(item.drone.name) is not None:
                    item.drone.select_set(True)

        return {"FINISHED"}

class UIListOperatorDeselect(bpy.types.Operator, UIListOperatorBase):
    """Deselect drones from group"""
    bl_idname = "fd.ui_list_deselect"
    bl_label = "Deselect"
    bl_description = "Deselect drones from group"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        self.resolve_attr(context)

        if self.collection is not None:
            for item in self.collection:
                if item.drone is not None and context.scene.objects.get(item.drone.name) is not None:
                    item.drone.select_set(False)

        return {"FINISHED"}


class FD_UL_groups(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="Group", emboss=False, translate=False, icon='GROUP_VERTEX')


    def invoke(self, context, event):
        pass

class FD_UL_drones(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.drone:
            layout.label(text=item.drone.name, icon='MESH_CUBE')
        else:
            layout.prop_search(item, "drone", context.scene, "objects", text="", icon='MESH_CUBE')


    def invoke(self, context, event):
        pass

def draw_select_groups(context, box):
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
