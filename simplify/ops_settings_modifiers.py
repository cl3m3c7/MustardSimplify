import bpy
from bpy.props import *


class MustardSimplify_SetModifier(bpy.types.PropertyGroup):
    name: StringProperty(default="")
    disp_name: StringProperty(default="")
    icon: StringProperty(default="")
    simplify: BoolProperty(default=True)
    type: StringProperty(default="OBJECT")


class MustardSimplify_SetModifiers(bpy.types.PropertyGroup):
    modifiers: CollectionProperty(type=MustardSimplify_SetModifier)


class MUSTARDSIMPLIFY_OT_MenuModifiersSelect(bpy.types.Operator):
    """Select the modifiers affected by the simplification process"""
    bl_idname = "mustard_simplify.menu_modifiers_select"
    bl_label = "Select Modifiers to Simplify"

    type: EnumProperty(items=[("OBJECT", "Objects", "Object", "MESH_DATA", 0),
                              ("GPENCIL", "Grease Pencil", "Grease Pencil", "OUTLINER_DATA_GREASEPENCIL", 1)])

    @classmethod
    def poll(cls, context):
        # Enable operator only when the scene is not simplified
        settings = bpy.context.scene.MustardSimplify_Settings
        return not settings.simplify_status

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):

        def add_modifier(collection, name, disp_name, icon, simplify, type):
            for el in collection:
                if el.name == name:
                    return False
            add_item = collection.add()
            add_item.name = name
            add_item.disp_name = disp_name
            add_item.icon = icon
            add_item.simplify = simplify
            add_item.type = type
            return True

        scene = bpy.context.scene
        settings = scene.MustardSimplify_Settings
        modifiers = scene.MustardSimplify_SetModifiers.modifiers
        addon_prefs = context.preferences.addons["MustardSimplify"].preferences

        # Extract type of modifiers for Objects
        rna = bpy.ops.object.modifier_add.get_rna_type()
        mods_list = rna.bl_rna.properties['type'].enum_items.keys()

        # Make the list
        # This is done at run-time, so it should be version agnostic
        if len(mods_list) != len(modifiers):

            modifiers.clear()

            for m in [x for x in mods_list if not "GREASE_PENCIL_" in x]:

                # Change the displayed name
                disp_name = m.replace("_", " ")
                disp_name = disp_name.title()
                disp_name = disp_name.replace("Uv", "UV")

                icon = "MOD_" + m
                simplify = True

                # Manage single exceptions
                if m in ["MESH_CACHE", "MESH_SEQUENCE_CACHE", "LAPLACIANDEFORM", "MESH_DEFORM", "SURFACE_DEFORM",
                         "SURFACE"]:
                    icon = "MOD_MESHDEFORM"
                if m in ["LAPLACIANDEFORM"]:
                    icon = "MOD_MESHDEFORM"
                    disp_name = "Laplacian Deform"
                elif m in ["NORMAL_EDIT", "WEIGHTED_NORMAL"]:
                    icon = "MOD_NORMALEDIT"
                elif m in ["UV_PROJECT", "UV_WARP"]:
                    icon = "MOD_UVPROJECT"
                elif m in ['VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_PROXIMITY']:
                    icon = "MOD_VERTEX_WEIGHT"
                elif m in ['DECIMATE']:
                    icon = "MOD_DECIM"
                elif m in ['EDGE_SPLIT']:
                    icon = "MOD_EDGESPLIT"
                elif m in ['NODES']:
                    icon = "GEOMETRY_NODES"
                elif m in ['MULTIRES']:
                    icon = "MOD_MULTIRES"
                elif m in ["MESH_TO_VOLUME", "VOLUME_TO_MESH", "VOLUME_DISPLACE"]:
                    icon = "VOLUME_DATA"
                elif m in ["WELD"]:
                    icon = "AUTOMERGE_OFF"
                elif m in ['SIMPLE_DEFORM']:
                    icon = "MOD_SIMPLEDEFORM"
                elif m in ['SMOOTH', 'CORRECTIVE_SMOOTH']:
                    icon = "MOD_SMOOTH"
                if m in ["LAPLACIANSMOOTH"]:
                    icon = "MOD_SMOOTH"
                    disp_name = "Laplacian Smooth"
                elif m in ["HOOK"]:
                    icon = m
                elif m in ["COLLISION"]:
                    icon = "MOD_PHYSICS"
                elif m in ["DYNAMIC_PAINT"]:
                    icon = "MOD_DYNAMICPAINT"
                elif m in ["PARTICLE_SYSTEM"]:
                    icon = "MOD_PARTICLES"
                elif m in ["SOFT_BODY"]:
                    icon = "MOD_SOFT"

                if m in settings.modifiers_ignore:
                    simplify = False

                add_modifier(modifiers, m, disp_name, icon, simplify, "OBJECT")

            if addon_prefs.debug:
                print("Mustard Simplify - Modifiers List generated for Objects")

        # Extract type of modifiers for Grease Pencil
        rna = bpy.ops.object.gpencil_modifier_add.get_rna_type()
        mods_list = rna.bl_rna.properties['type'].enum_items.keys()

        # Make the list
        # This is done at run-time, so it should be version agnostic
        if len(mods_list) != len(modifiers):

            for m in mods_list:

                # Change the displayed name
                disp_name = m.replace("_", " ")
                if "GP_" in m:
                    disp_name = disp_name[3:]
                disp_name = disp_name.title()
                disp_name = disp_name.replace("Uv", "UV")

                icon = "MOD_" + m[3:]
                simplify = True

                # Manage single exceptions
                if m in ["GP_TEXTURE"]:
                    icon = "TEXTURE"
                elif m in ['GP_WEIGHT_ANGLE', 'GP_WEIGHT_PROXIMITY']:
                    icon = "MOD_VERTEX_WEIGHT"
                elif m in ["GP_MULTIPLY"]:
                    icon = "GP_MULTIFRAME_EDITING"
                elif m in ["GP_SUBDIV"]:
                    icon = "MOD_SUBSURF"
                elif m in ["GP_THICK"]:
                    icon = "MOD_THICKNESS"
                elif m in ["GP_HOOK"]:
                    icon = m[3:]
                elif m in ["GP_COLOR"]:
                    icon = "MOD_HUE_SATURATION"

                if m in settings.modifiers_ignore:
                    simplify = False

                add_modifier(modifiers, m, disp_name, icon, simplify, "GPENCIL")

            if addon_prefs.debug:
                print("Mustard Simplify - Modifiers List generated for Grease Pencil objects")

        return context.window_manager.invoke_props_dialog(self, width=780)

    def draw(self, context):

        scene = bpy.context.scene
        modifiers = scene.MustardSimplify_SetModifiers.modifiers

        layout = self.layout

        layout.prop(self, "type", expand=True)

        box = layout.box()

        row = box.row()
        col = row.column()

        if self.type == "OBJECT":

            for m in [x for x in modifiers if x.type == "OBJECT"]:
                if m.name in ["ARRAY", "ARMATURE", "CLOTH"]:
                    col = row.column()
                row2 = col.row()
                row2.prop(m, 'simplify', text="")
                # Avoid missing icon error
                try:
                    row2.label(text=m.disp_name, icon=m.icon)
                except:
                    row2.label(text=m.disp_name, icon="BLANK1")

        if self.type == "GPENCIL":

            for m in [x for x in modifiers if x.type == "GPENCIL"]:
                if m.name in ["GP_TEXTURE", "GP_ARRAY", "GP_ARMATURE", "GP_COLOR"]:
                    col = row.column()
                row2 = col.row()
                row2.prop(m, 'simplify', text="")
                # Avoid missing icon error
                try:
                    row2.label(text=m.disp_name, icon=m.icon)
                except:
                    row2.label(text=m.disp_name, icon="BLANK1")


def register():
    bpy.utils.register_class(MustardSimplify_SetModifier)

    bpy.utils.register_class(MustardSimplify_SetModifiers)
    bpy.types.Scene.MustardSimplify_SetModifiers = PointerProperty(type=MustardSimplify_SetModifiers)

    bpy.utils.register_class(MUSTARDSIMPLIFY_OT_MenuModifiersSelect)


def unregister():
    bpy.utils.unregister_class(MUSTARDSIMPLIFY_OT_MenuModifiersSelect)
    bpy.utils.unregister_class(MustardSimplify_SetModifiers)
    bpy.utils.unregister_class(MustardSimplify_SetModifier)
