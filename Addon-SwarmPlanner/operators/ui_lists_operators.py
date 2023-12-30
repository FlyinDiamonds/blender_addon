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
    bl_label = "List Actions"
    bl_description = "Add item ri group"
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
    bl_label = "List Actions"
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
    bl_label = "List Actions"
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
