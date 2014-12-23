"""
TextureAdd Texture Record format
"""

#import math

REC_HEADER = \
"""#TextureAdd Texture Records File

If you edit these by hand here is the texture format to follow...

[Texture#]
X(0 - 255)
Y(0 - 255)
Width(1 - 256)
Height(1 - 256)
FlipX(-1 or 0)
FlipY(-1 or 0)
Page(1 and up)

If you edit the textures by hand make sure the amount of textures is correct...
[Amount_Of_Textures]
%d

You can edit the textures starting from [Texture2], don't edit or remove [Texture1], you can remove textures by deleting the texture block, and changing the amount of textures up top to the correct value..."""


class TexInfo:
    __slots__ = ["index","x", "y", "width", "height", "flipx", "flipy", "page"]
    
    def __init__(self, origin, width, height,page=1,flipx=-1,flipy=-1):
        self.index = -1
        self.x = origin[0]
        self.y = origin[1]
        self.width = width
        self.height = height
        self.flipx = flipx
        self.flipy = flipy
        self.page = page
        return
        
    def __str__(self):
        s = "\n[Texture%d]\n"%(self.index)+ \
            "%d\n"%(self.x)+ \
            "%d\n"%(self.y)+ \
            "%d\n"%(self.width)+ \
            "%d\n"%(self.height)+ \
            "%d\n"%(self.flipx)+ \
            "%d\n"%(self.flipy)+ \
            "%d\n"%(self.page)
        return s

class Rec:
    __slots__=["texinfos", "count"]
    
    def __init__(self):
        self.count = 0
        self.texinfos = []
        tex1 = TexInfo((0,0),1,1,1,0,0)
        self.addtexinfo(tex1)
        return
    
    def addtexinfo(self, texinfo):
        self.count += 1
        texinfo.index = self.count
        self.texinfos.append(texinfo)
        return
            
    def writeheader(self, f, count):
        f.write(REC_HEADER % (count))
        return
    
    def write(self, path):
        with open(path, "w") as g:
            self.writeheader(g, self.count)
            for tx in self.texinfos:
                g.write(str(tx))
        return
        
def uvtotexinfo(uvs, imgsize=256):
    points = [(round(uv[0]*imgsize),round(uv[1]*imgsize)) for uv in uvs]
    #points = [(math.trunc(uv[0]*imgsize),math.trunc(uv[1]*imgsize)) for uv in uvs]
    points.sort()
    if len(uvs)==4:
        p1 = points[0]
        p4 = points[1]
        p2 = points[2]
        p3 = points[3]
        return TexInfo(p1, p2[0]-p1[0], p4[1] - p1[1])
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
            return TexInfo(p1, p[0]-p1[0], p4[1] - p1[1])
        else:
            p = left[0]
            p2=right[0]
            p3=right[1]
            if p[1]==p2[1]:
                p1 = p
            else:
                p1 = (p[0], p2[1])
            return TexInfo(p1, p3[0]-p[0], p3[1]-p2[1])
    else:
        return None
