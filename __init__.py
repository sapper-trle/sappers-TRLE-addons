"""
Instructions:
    3D View must be in Object Mode
    A 'MESH' object must be active
    The active object must have UVS (Lightmap packed!)
"""

bl_info = {
    "name": "Sapper's TRLE Export Addons",
    "author": "sapper",
    "blender": (2, 72, 2),
    "version": (1, 1),
    "location": "File > Export",
    "description": "Export UVs to .rec format & "
                   "Export mesh to *.mqo format for StrPix import",
    "warning": "Only available in OBJECT mode with an active, UV mapped, MESH object",
    "wiki_url": "http://www.tombraiderforums.com/showthread.php?t=208076",
    "tracker_url": "http://www.tombraiderforums.com/showthread.php?t=208076",
    "category": "Import-Export"}

#http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Multi-File_packages#init_.py
if "bpy" in locals():
    import imp
    if "texaddrec" in locals():
        imp.reload(texaddrec)
    if "export_mqo" in locals():
        imp.reload(export_mqo)

import bpy

from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       )
                       
from bpy_extras.io_utils import (ExportHelper)

def export_rec(op, filename, context):
    from . import texaddrec as ta
    print()
        
    ob = context.active_object

    if (ob != None) and (ob.type == "MESH"): 
        if len(ob.data.uv_layers) > 0:
            uv_layer = ob.data.uv_layers[0].data
            if len(uv_layer) > 0:
                msg = ".rec export: Processing UVs"
                print(msg)
                op.report({"INFO"}, msg)
                rec = ta.Rec()
                for poly in ob.data.polygons:
                    #print("Polygon index: %d, length: %d" % (poly.index, poly.loop_total))
                    print(end=".")
                    if not (poly.loop_total in [3,4]):
                        continue
                    uvs = []
                    for loop_index in poly.loop_indices:
                        uv = (uv_layer[loop_index].uv[0],1-uv_layer[loop_index].uv[1])
                        uvs.append(uv)
                    texinfo = ta.uvtotexinfo(uvs)
                    rec.addtexinfo(texinfo)
                print()
                msg = ".rec export: Writing file"
                print(msg)
                op.report({"INFO"}, msg)
                rec.write(filename)
                msg = ".rec export: Created file %s" % (filename)
                print(msg, "\n")
                op.report({"INFO"}, msg)
            else:
                msg = ".rec export aborted. No data for first UV layer"
                print(msg, "\n")
                op.report({"ERROR"}, msg)
        else:
            msg = ".rec export aborted. No UV layers"
            print(msg, "\n")
            op.report({"ERROR"}, msg)
    else:
        if ob == None:
            msg = ".rec export aborted. No active object"
            print(msg, "\n")
            op.report({"ERROR"}, msg)
        else:
            msg = ".rec export aborted. Active object is %s not MESH" % (ob.type)
            print(msg, "\n")
            op.report({"ERROR"}, msg)
    return


class ExportREC(bpy.types.Operator, ExportHelper):
    """Export UVs of active object when in Object Mode"""
    bl_idname = "io_export_scene.rec"
    bl_description = "Export Lightmap packed UVs to TextureAdd Texture Record format"
    bl_label = "Export rec"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
 
    # From ExportHelper. Filter filenames.
    filename_ext = ".rec"
    filter_glob = bpy.props.StringProperty(default="*.rec", options={'HIDDEN'})

    def execute(self, context):
        export_rec(self, self.properties.filepath, context)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        ob = context.active_object
        self.properties.filepath = ob.name
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    @classmethod  
    def poll(cls, context):  
        ob = context.active_object  
        return (ob is not None) and (ob.mode == 'OBJECT') and (ob.type=="MESH") and (len(ob.data.uv_layers) > 0)


class ExportMQO(bpy.types.Operator, ExportHelper):
    """Export active object as StrPix compatible .mqo when in Object Mode"""
    bl_idname = "io_export_scene.strpixmqo"
    bl_description = 'Export to Metasequoia format with texture info for StrPix'
    bl_label = "Export mqo"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
 
    # From ExportHelper. Filter filenames.
    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo", options={'HIDDEN'})
        
    active_only = True 
    strpix_mats = True
    rot90 = True   
    invert = True   
    edge = False
    uv_exp = True
    uv_cor = True       
    mat_exp = False    
    mod_exp = False
 
    scale = bpy.props.FloatProperty(
        name = "Scale", 
        description="Scale mesh. Number > 1 means bigger, number < 1 means smaller.", 
        default = 1, min = 0.001, max = 1000.0)
 
    def execute(self, context):
        from . import export_mqo
        active_ob = context.active_object.name
        export_mqo.export_mqo(self,
            self.properties.filepath, 
            context.scene.objects, 
            self.rot90, self.invert, self.edge, self.uv_exp, self.uv_cor, self.mat_exp, self.mod_exp,
            self.scale, active_ob, self.strpix_mats)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        ob = context.active_object
        self.properties.filepath = ob.name
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
    @classmethod  
    def poll(cls, context):  
        ob = context.active_object  
        return (ob is not None) and (ob.mode == 'OBJECT') and (ob.type=="MESH") and (len(ob.data.uv_layers) > 0)

def menu_func_export(self, context):
    self.layout.operator(ExportREC.bl_idname, text="TextureAdd (.rec)", icon="COLOR_BLUE")
    self.layout.operator(ExportMQO.bl_idname, text="StrPix Metasequoia (.mqo)", icon="COLOR_BLUE")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
