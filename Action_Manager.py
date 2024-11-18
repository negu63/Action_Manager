import bpy
import os

bl_info = {
    "name": "Action Manager",
    "author": "negu63",
    "version": (1, 0, 0),
    "blender": (4, 1, 1),
    "location": "View3D > UI > Action Manager",
    "description": (
        "Manage and append actions from external .blend files. "
    ),
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

class ActionListItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Action Name")
    file_path: bpy.props.StringProperty(name="Blend File Path")

class ACTIONMANAGER_PT_MainPanel(bpy.types.Panel):
    bl_label = "Action Manager"
    bl_idname = "ACTIONMANAGER_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Action Manager"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Folder input
        layout.prop(scene, "action_manager_folder", text="Folder")
        layout.operator("actionmanager.load_actions", text="Load Actions")

        # Scrollable list
        row = layout.row()
        row.template_list(
            "ACTIONMANAGER_UL_ActionList",  # List class ID
            "",  # Unique list ID
            scene,  # Data source
            "action_manager_list",  # Property name for the list
            scene,  # Active item index source
            "action_manager_list_index"  # Active item index property
        )

        # Append button for selected action
        if len(scene.action_manager_list) > 0:
            layout.operator("actionmanager.append_action", text="Append Action")

            # Show file name of selected action
            index = scene.action_manager_list_index
            if 0 <= index < len(scene.action_manager_list):
                selected_action = scene.action_manager_list[index]
                layout.label(text=f"File: {os.path.basename(selected_action.file_path)}", icon='FILE_BLEND')

class ACTIONMANAGER_UL_ActionList(bpy.types.UIList):
    """Custom UIList for actions"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='ACTION')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")

class ACTIONMANAGER_OT_LoadActions(bpy.types.Operator):
    """Operator to load actions from blend files"""
    bl_idname = "actionmanager.load_actions"
    bl_label = "Load Actions"

    def execute(self, context):
        scene = context.scene
        folder_path = scene.action_manager_folder

        if not os.path.isdir(folder_path):
            self.report({'ERROR'}, "Invalid folder path")
            return {'CANCELLED'}

        scene.action_manager_list.clear()  # Clear the existing list
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".blend"):
                file_path = os.path.join(folder_path, file_name)
                with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
                    for action_name in data_from.actions:
                        new_item = scene.action_manager_list.add()
                        new_item.name = action_name
                        new_item.file_path = file_path

        return {'FINISHED'}

class ACTIONMANAGER_OT_AppendAction(bpy.types.Operator):
    """Operator to append selected action"""
    bl_idname = "actionmanager.append_action"
    bl_label = "Append Action"

    def execute(self, context):
        scene = context.scene
        index = scene.action_manager_list_index

        if index < 0 or index >= len(scene.action_manager_list):
            self.report({'ERROR'}, "No action selected")
            return {'CANCELLED'}

        selected_action = scene.action_manager_list[index]
        try:
            with bpy.data.libraries.load(selected_action.file_path, link=False) as (data_from, data_to):
                if selected_action.name in data_from.actions:
                    data_to.actions = [selected_action.name]
                else:
                    self.report({'ERROR'}, f"Action '{selected_action.name}' not found in {selected_action.file_path}")
                    return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ActionListItem)
    bpy.utils.register_class(ACTIONMANAGER_PT_MainPanel)
    bpy.utils.register_class(ACTIONMANAGER_UL_ActionList)
    bpy.utils.register_class(ACTIONMANAGER_OT_LoadActions)
    bpy.utils.register_class(ACTIONMANAGER_OT_AppendAction)

    bpy.types.Scene.action_manager_folder = bpy.props.StringProperty(
        name="Folder Path", subtype='DIR_PATH'
    )
    bpy.types.Scene.action_manager_list = bpy.props.CollectionProperty(type=ActionListItem)
    bpy.types.Scene.action_manager_list_index = bpy.props.IntProperty()

def unregister():
    bpy.utils.unregister_class(ActionListItem)
    bpy.utils.unregister_class(ACTIONMANAGER_PT_MainPanel)
    bpy.utils.unregister_class(ACTIONMANAGER_UL_ActionList)
    bpy.utils.unregister_class(ACTIONMANAGER_OT_LoadActions)
    bpy.utils.unregister_class(ACTIONMANAGER_OT_AppendAction)

    del bpy.types.Scene.action_manager_folder
    del bpy.types.Scene.action_manager_list
    del bpy.types.Scene.action_manager_list_index

if __name__ == "__main__":
    register()
