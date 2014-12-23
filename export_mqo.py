# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Script copyright (C) Thomas PORTASSAU (50thomatoes50) - Modified by sapper
# Contributors: Campbell Barton, Jiri Hnidek, Paolo Ciccone, Thomas Larsson, http://blender.stackexchange.com/users/185/adhi

"""
This script exports the active object to a Metasequoia(*.mqo) file suitable for importing into StrPix for TRLE community.

Usage:
    Unwrap a low poly mesh using "Lightmap Packed UVs" option, image size must be 256 x 256.
    Run this script from "File->Export" menu and save the *.mqo.

Parameter values:
    rot90 = True            # rot90 method changed (use -1 * v.co.z) so as not to swap left/right
    invert = True           # required due to change to rot90 method
    edge = False            # edges ignored by StrPix
    uv_exp = True           # need to access UV data
    uv_cor = True           # TRLE *.wad has origin top left same as *.mqo
    mat_exp = False         # do not use Blender material properties
    mod_exp = False         # StrPix ignores modifiers in *.mqo
    scale = user defined    # in original script, scale = 1/(scale slider value), here scale = scale slider value
    active_ob = active object's name    # unlike original script, only active object is exported
    strpix_mats = True      # material name in *.mqo is as per StrPix texturing convention

NO WIKI FOR THE MOMENT
http://tombraiderforums.com

base source from : 
http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Multi-File_packages#Simple_obj_export
"""

#import os
#import time
#import pprint
import bpy
#import mathutils
import bpy_extras.io_utils


def export_mqo(op,filepath, objects, rot90, invert, edge, uv_exp, uv_cor, mat_exp, mod_exp, scale, active_ob, strpix_mats):

    inte_mat = 0
    tmp_mat = []
    obj_tmp = []
    
    for ob in objects:
        if (active_ob) and (ob.name != active_ob):
            continue
        if not ob or ob.type != 'MESH':
            msg = '.mqo export: Cannot export - active object %s is not a mesh.\n' % ob
            print(msg)
            op.report({'ERROR'}, msg)
        else:
            inte_mat, obj_tmp = exp_obj(op, obj_tmp, ob, rot90, invert, edge, uv_exp, uv_cor, scale, mat_exp, inte_mat, tmp_mat, mod_exp, strpix_mats)

    if not obj_tmp:
        msg = ".mqo export: Aborting. No objects to export.\n"
        print(msg)
        op.report({'ERROR'}, msg)
        return
        
    with open(filepath, 'w') as fp:
        fw = fp.write
        msg = ".mqo export: Writing file"
        print(msg)
        op.report({'INFO'}, msg)
    
        fw("Metasequoia Document\nFormat Text Ver 1.0\n\nScene {\n    pos 0.0000 0.0000 1500.0000\n    lookat 0.0000 0.0000 0.0000\n    head -0.5236\n    pich 0.5236\n    bank 0.0000\n    ortho 0\n    zoom2 5.0000\n    amb 0.250 0.250 0.250\n    dirlights 1 {\n        light {\n            dir 0.408 0.408 0.816\n            color 1.000 1.000 1.000\n        }\n    }\n}\n")    

        if mat_exp:        
            mat_fw(fw, tmp_mat)
        
        if strpix_mats:
            mat_fw(fw, tmp_mat)
        
        for data in obj_tmp:
            fw(data)
        
        fw("\nEof\n")
        msg = ".mqo export: Created file %s" % filepath
        print(msg)
        op.report({'INFO'}, msg)
    return
    
def exp_obj(op, fw, ob, rot90, invert, edge, uv_exp, uv_cor, scale, mat_exp, inte_mat, tmp_mat, mod_exp, strpix_mats):
    me = ob.data
    if not me:
        return inte_mat, fw
    pi = 3.141594
    if mod_exp:
        mod = modif(ob.modifiers)
    #fw("Object \"%s\" {\n\tdepth 0\n\tfolding 0\n\tscale %.6f %.6f %.6f\n\trotation %.6f %.6f %.6f\n\ttranslation %.6f %.6f %.6f\n\tvisible 15\n\tlocking 0\n\tshading 1\n\tfacet 59.5\n\tcolor 0.898 0.498 0.698\n\tcolor_type 0\n" % (me.name, scale[0], scale[1], scale[2], 180*rotat.x/pi, 180*rotat.y/pi, 180*rotat.z/pi, loca[0], loca[1], loca[2]))
    fw.append("Object \"%s\" {\n\tdepth 0\n\tfolding 0\n\tscale 1.0 1.0 1.0\n\trotation 1.0 1.0 1.0\n\ttranslation 1.0 1.0 1.0\n\tvisible 15\n\tlocking 0\n\tshading 1\n\tfacet 59.5\n\tcolor 0.898 0.498 0.698\n\tcolor_type 0\n" % (me.name))
    if mod_exp:
        for mod_fw in mod:
            fw.append(mod_fw)
        
    msg = ".mqo export: Exporting \"%s\" object" %(ob.name)
    print(msg)
    op.report({'INFO'}, msg)
    inte_mat_obj = inte_mat
    if mat_exp:
        for mat in me.materials:
            inte_mat = mat_extract(mat, tmp_mat, inte_mat)  
    
    fw.append("\tvertex %i {\n"% (len(me.vertices)))
    for v in me.vertices:
        if rot90:
            fw.append("\t\t%.5f %.5f %.5f\n" % (v.co[0]*scale, v.co[2]*scale, -v.co[1]*scale))
        else:
            fw.append("\t\t%.5f %.5f %.5f\n" % (v.co[0]*scale, v.co[1]*scale, v.co[2]*scale))
    fw.append("\t}\n")
    
    me.update(False, True)
    faces = me.tessfaces
    lostEdges = 0
    for e in me.edges:
        if e.is_loose:
            lostEdges+=1
    if edge:
        fw.append("\tface %i {\n" % (len(faces)+lostEdges))
        for e in me.edges:
            if e.is_loose:
                fw.append("\t\t2 V(%i %i)\n" % (e.vertices[0], e.vertices[1]))
    else:
        fw.append("\tface %i {\n" % (len(faces)))
    
    me.update(False, True)     
    for f in faces:
        vs = f.vertices
        try:
            data = me.tessface_uv_textures.active.data[f.index]
            flip, type, rot = uvtotexinfo(data, len(f.vertices))
        except AttributeError:
            #print("Error in uvtotexinfo")
            flip, type, rot = 1, 0, 0
           
        if (flip, type, rot) == None:
            #print("Error in uvtotexinfo")
            flip, type, rot = 1, 0, 0    
            
        if len(f.vertices) == 3:
            if invert:
                fw.append("\t\t3 V(%d %d %d)" % (vs[(0-rot)%3], vs[(2-rot)%3], vs[(1-rot)%3]))
            else:
                fw.append("\t\t3 V(%d %d %d)" % (vs[0], vs[1], vs[2]))
        if len(f.vertices) == 4:
            if invert:
                fw.append("\t\t4 V(%d %d %d %d)" % (vs[(0-rot)%4], vs[(3-rot)%4], vs[(2-rot)%4], vs[(1-rot)%4]))
            else:
                fw.append("\t\t4 V(%d %d %d %d)" % (vs[0], vs[1], vs[2], vs[3]))
                
        if strpix_mats:
            l = " col(%.3f %.3f %.3f %.3f) dif(%.3f) amb(%.3f) emi(%.3f) spc(%.3f) power(5)\n" % (1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.0,0.0)
            fw.append(" M(%d)" % (f.index))
        else:
            fw.append(" M(%d)" % (f.material_index+inte_mat_obj))
        
        try:
            if (uv_exp):
                if len(f.vertices) == 3:
                    if uv_cor:
                        fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], 1-data.uv1[1], data.uv3[0], 1-data.uv3[1], data.uv2[0], 1-data.uv2[1]))
                        if strpix_mats:
                            tmp_mat.append('\t"%d_%d_0"%s' % (flip*(f.index+1), type, l))
                    else:
                        fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], data.uv1[1], data.uv2[0], data.uv2[1], data.uv3[0], data.uv3[1]))
                if len(f.vertices) == 4:
                    if uv_cor:
                        fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], 1-data.uv1[1], data.uv4[0], 1-data.uv4[1], data.uv3[0], 1-data.uv3[1], data.uv2[0], 1-data.uv2[1]))
                        if strpix_mats:
                            tmp_mat.append('\t"%d_%d_0"%s' % (flip*(f.index+1), type, l))                       
                    else:
                        fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], data.uv1[1], data.uv2[0], data.uv2[1], data.uv3[0], data.uv3[1], data.uv4[0], data.uv4[1]))   
        except AttributeError:
            #print("Error in exporting UVs")
            pass
        
        fw.append("\n")
    fw.append("\t}\n")
    fw.append("}\n")
    return inte_mat, fw
       
def mat_extract(mat, tmp, index):
    # not used in this modified script
    #l = "\t\"" + mat.name + "\" " + "col(" + str(mat.diffuse_color[0]) + " " + str(mat.diffuse_color[1]) + " " + str(mat.diffuse_color[2]) + " " + str(mat.alpha) + ")" + " dif(" + str(mat.diffuse_intensity) + ")" + " amb(" + str(mat.ambient) + ")" + " emi(" + str(mat.emit) + ")" + " spc(" + str(mat.specular_intensity) + ")" + " power(5)\n"
    alpha = ''
    diffuse = ''
    print("added mat:%s / index #%i" % (mat.name,index))
    l = "\t\"%s\" col(%.3f %.3f %.3f %.3f) dif(%.3f) amb(%.3f) emi(%.3f) spc(%.3f) power(5)" % (mat.name, mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2], mat.alpha, mat.diffuse_intensity, mat.ambient, mat.emit, mat.specular_intensity)
    for tex in mat.texture_slots.values():
        if tex != None:
            if tex.use and tex.texture.type == 'IMAGE' and tex.texture.image != None:
                if tex.use_map_alpha and alpha == '' :
                    if tex.texture.image.filepath.find("//") != -1:
                        alpha = tex.texture.image.name
                    else:
                        alpha = tex.texture.image.filepath
                if tex.use_map_color_diffuse and diffuse == '' :
                    if tex.texture.image.filepath.find("//") != -1:
                        diffuse = tex.texture.image.name
                    else:
                        diffuse = tex.texture.image.filepath
    l = l +  " tex(\"" + diffuse + "\") aplane(\"" + alpha + "\")"
     
    tmp.append(l+"\n")
    return index + 1
    
    
def mat_fw(fw, tmp):
    fw("Material  %d {\n" % (len(tmp)))
    for mat in tmp:
        fw("%s" % (mat))
    fw("}\n")
    
def modif(modifiers):
    # not used in this modified script
    tmp = []
    axis = 0
    for mod in modifiers.values():
        if mod.type == "MIRROR":
            print("exporting mirror")
            if mod.use_mirror_merge:
                tmp.append("\tmirror 2\n\tmirror_dis %.3f\n" % mod.merge_threshold)
            else:
                tmp.append("\tmirror 1\n")
            if mod.use_x:
                axis = 1
            if mod.use_y:
                axis = axis + 2
            if mod.use_z:
                axis = axis + 4
        if mod.type == "SUBSURF":
            print("exporting subsurf")
            tmp.append("\tpatch 3\n\tpatchtri 0\n\tsegment %i\n" % mod.render_levels)
    return tmp
    
def uvtotexinfo(data, size=3, imgsize=256):
    # returns flip - Texture horizontal flip. -1 = flipped, 1 = not flipped
    # returns type - Quad = 0, Triangle - corner of rectangle used from following list.
    #                [0 = top left, 2 = top right, 4 = bottom right, 6 = bottom left]
    # returns rot  - number of 90 degree CW rotations.
    #                Quad - to get UVs[0] to top left, Triangle - to get UVs[0] to right angle

    uvs = [data.uv1, data.uv3, data.uv2] # rot90
    if size == 4:
            uvs = [data.uv1, data.uv4, data.uv3, data.uv2] # rot90
    points = [(round(uv[0]*imgsize),round(uv[1]*imgsize)) for uv in uvs]
    points_unsorted = points[:]
    first = points_unsorted[0]
    points.sort()
    
    if isclockwise(points_unsorted):
        flip = 1
    else:
        flip = -1
        
    if len(uvs)==4:
        type = 0
        
        # points[1]---------points[3]
        #    |                 |
        # points[0]---------points[2]
        
        # p4-------p3
        # |         |
        # p1-------p2 
 
        p1 = points[0]
        p4 = points[1]
        p2 = points[2]
        p3 = points[3]

        if flip > 0:
            if p1 == first:
                rot = 1
            elif p3 == first:
                rot = 3
            elif p2 == first:
                rot = 2
            else:
                rot = 0
        else:
            if p1 == first:
                rot = 3
            elif p2 == first:
                rot = 1
            elif p4 == first:
                rot = 3
            else:
                rot = 0                    
        return flip, type, rot
        
    elif len(uvs)==3:
        left = []
        right = []
        left.append(points[0])
        if points[1][0] == points[0][0]:
            left.append(points[1])
        else:
            right.append(points[1])
        right.append(points[2])
        
        if len(left) == 2:
            p1 =left[0]
            p4 = left[1]
            p = right[0]
            
            if flip < 0:
                type = 4
            else:
                type = 6
                
            if p4 == first:
                if flip < 0:
                    rot = 1
                else:
                    rot = 2
            elif p == first:
                if flip < 0:
                    rot = 2
                else:
                    rot = 1
            else:
                rot = 0
            return flip, type, rot
        else:
            p = left[0]
            p2=right[0]
            p3=right[1]
            if p[1]==p2[1]:
                p1 = p
            else:
                p1 = (p[0], p2[1])
                
            if flip < 0:
                type = 0
            else:
                type = 2

            if p2 == first:
                if flip < 0:
                    rot = 1
                else:
                    rot = 2
            elif p == first:
                if flip < 0 :
                    rot = 2
                else:
                    rot = 1
            else:
                rot = 0
            return flip, type, rot
    else:
        return None

def isclockwise(points):
    """polygon winding determination
       used on UVs to determine flipped UVs"""
    sum = 0.0
    for i in range(len(points)):
        v1 = points[i]
        v2 = points[(i+1) % len(points)]
        sum += ((v2[0] - v1[0]) * (v2[1] + v1[1]))
    return sum > 0.0
        