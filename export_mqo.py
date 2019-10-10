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
    scale = user defined                 # in original script, scale = 1/(scale slider value), here scale = scale slider value
    active_ob = active object's name     # unlike original script, only active object is exported
    texture = optional texture file name # texture name will be referenced by materials so model will be textured in Metasequoia

Notes:
    Blender has Z axis up whereas Metasequoia has Y axis up so axes are swapped keeping left and right preserved 
    Faces and UVs are inverted (opposite winding) due to swap of up axis
    UVs are corrected since TRLE *.wad has origin top left same as *.mqo whereas Blender has origin bottom left
    Material name in *.mqo is as per StrPix texturing convention

NO WIKI FOR THE MOMENT
http://tombraiderforums.com

base source from : 
http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Multi-File_packages#Simple_obj_export
"""

import bpy
import bpy_extras.io_utils

def export_mqo(op,filepath, objects, scale, active_ob, texture):

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
            inte_mat, obj_tmp = exp_obj(op, obj_tmp, ob, scale, inte_mat, tmp_mat, texture)

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
        
        mat_fw(fw, tmp_mat)
        
        for data in obj_tmp:
            fw(data)
        
        fw("Eof\n")
        msg = ".mqo export: Created file %s" % filepath
        print(msg)
        op.report({'INFO'}, msg)
    return
    
def exp_obj(op, fw, ob, scale, inte_mat, tmp_mat, texture):
    me = ob.data
    if not me:
        return inte_mat, fw

    fw.append("Object \"%s\" {\n\tdepth 0\n\tfolding 0\n\tscale 1 1 1\n\trotation 0 0 0\n\ttranslation 0 0 0\n\tvisible 15\n\tlocking 0\n\tshading 1\n\tfacet 59.5\n\tcolor 0.898 0.498 0.698\n\tcolor_type 0\n" % (me.name))
        
    msg = ".mqo export: Exporting \"%s\" object" %(ob.name)
    print(msg)
    op.report({'INFO'}, msg)
    inte_mat_obj = inte_mat 
    
    fw.append("\tvertex %i {\n"% (len(me.vertices)))
    for v in me.vertices:
        fw.append("\t\t%.5f %.5f %.5f\n" % (v.co[0]*scale, v.co[2]*scale, -v.co[1]*scale)) # swap y and z keeping left and right the same
    fw.append("\t}\n")
    
    me.update(calc_loop_triangles=True)
    facecount, ngons = getFacesCount(me)
    # using loop_triangles is no good
    # no guarantee that UVs will be right angled triangles
    # need to convert ngons to quads or triangles before unwrapping mesh 
    # the code using the loop_triangles stays only for reference
    if ngons > 0:
        msg = ".mqo export: Ngons found. Convert to quads/triangles and unwrap mesh again"
        print(msg)
        op.report({"ERROR"}, msg)
        fw =[]
        return inte_mat, fw

    fw.append("\tface %i {\n" % (facecount))

    if ngons==0:
        faces = me.polygons
    else:
        faces = []
        for f in me.polygons:
            if len(f.vertices) < 5:
                faces.append(f)
            else:
                tris = [tri for tri in me.loop_triangles if tri.polygon_index == f.index]
                faces.extend(tris)
    uv_layer = me.uv_layers.active.data
    count = 0
    for f in faces:
        uvs =[]
        if hasattr(f,"loop_indices"): #polygons
            for loop_index in f.loop_indices:
                uvs.append(uv_layer[loop_index].uv)
        else:
            for loop_index in f.loops: #loop_triangles
                uvs.append(uv_layer[loop_index].uv)

        flip, typ, rot = uvtotexinfo(uvs, len(f.vertices))
          
        if (flip, typ, rot) == None:
            #print("Error in uvtotexinfo")
            flip, typ, rot = 1, 0, 0 

        vs = f.vertices            
        if len(f.vertices) == 3:
            fw.append("\t\t3 V(%d %d %d)" % (vs[(0-rot)%3], vs[(2-rot)%3], vs[(1-rot)%3])) # change winding and the first vert
            order=[(0-rot)%3, (2-rot)%3, (1-rot)%3]
            uvs = [uvs[order[0]], uvs[order[1]], uvs[order[2]]]

        if len(f.vertices) == 4:
            fw.append("\t\t4 V(%d %d %d %d)" % (vs[(0-rot)%4], vs[(3-rot)%4], vs[(2-rot)%4], vs[(1-rot)%4])) # change winding and the first vert
            order=[(0-rot)%4, (3-rot)%4, (2-rot)%4, (1-rot)%4]
            uvs = [uvs[order[0]], uvs[order[1]], uvs[order[2]],uvs[order[3]]]                

        s = "tex(\"%s\")" % texture if texture else ""
        l = " col(%.3f %.3f %.3f %.3f) dif(%.3f) amb(%.3f) emi(%.3f) spc(%.3f) power(5) %s\n" % (1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.0,0.0,s)
        fw.append(" M(%d)" % (count)) # was  f.index
      
        if len(f.vertices) == 3:
            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f)" % (uvs[0][0], 1-uvs[0][1], uvs[1][0], 1-uvs[1][1], uvs[2][0], 1-uvs[2][1]))
            tmp_mat.append('\t"%d_%d_0"%s' % (flip*(count+1), typ, l)) # was f.index+1

        if len(f.vertices) == 4:
            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f)" % (uvs[0][0], 1-uvs[0][1], uvs[1][0], 1-uvs[1][1], uvs[2][0], 1-uvs[2][1], uvs[3][0], 1-uvs[3][1]))
            tmp_mat.append('\t"%d_%d_0"%s' % (flip*(count+1), typ, l)) # was f.index+1                       

        fw.append("\n")
        count += 1
    fw.append("\t}\n")
    fw.append("}\n")
    return inte_mat, fw    
    
def mat_fw(fw, tmp):
    fw("Material %d {\n" % (len(tmp)))
    for mat in tmp:
        fw("%s" % (mat))
    fw("}\n")
    
def uvtotexinfo(data, size=3, imgsize=256):
    # data = uvs must be rectangles or right angled triangles
    # returns flip - Texture horizontal flip. -1 = flipped, 1 = not flipped
    # returns type - Quad = 0, Triangle - corner of rectangle used from following list.
    #                [0 = top left, 2 = top right, 4 = bottom right, 6 = bottom left]
    # returns rot  - number of 90 degree CW rotations.
    #                Quad - to get UVs[0] to top left, Triangle - to get UVs[0] to right angle

    uvs = [data[0], data[2], data[1]] # rot90
    if size == 4:
            uvs = [data[0], data[3], data[2], data[1]] # rot90
    points = [(round(uv[0]*imgsize),round(uv[1]*imgsize)) for uv in uvs]
    points_unsorted = points[:]
    first = points_unsorted[0]
    points.sort()
    
    if isclockwise(points_unsorted):
        flip = 1
    else:
        flip = -1
        
    if len(uvs)==4:
        typ = 0
        
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
        return flip, typ, rot
        
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
                typ = 4
            else:
                typ = 6
                
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
            return flip, typ, rot
        else:
            p = left[0]
            p2=right[0]
            p3=right[1]
            if p[1]==p2[1]:
                p1 = p
            else:
                p1 = (p[0], p2[1])
                
            if flip < 0:
                typ = 0
            else:
                typ = 2

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
            return flip, typ, rot
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

def getFacesCount(msh):
    quads=0
    tris=0
    ngons=0
    for p in msh.polygons:
        vcount = len(p.vertices)
        if vcount==3:
            tris += 1
        elif vcount==4:
            quads += 1
        else:
            ngons += 1
    if ngons==0:
        return len(msh.polygons), ngons
    msh.calc_loop_triangles()
    ngon_tris = len(msh.loop_triangles) - (2*quads) - tris
    return quads + tris + ngon_tris, ngons
        