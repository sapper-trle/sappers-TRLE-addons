sappers-TRLE-addons
===================

Blender addons for Tomb Raider Level Editor builders.

With these two addons builders can export a UV mapped low poly mesh for import into StrPix.

The .mqo exporter exports the model to Metasequoia (.mqo) format with material names in a special format that is understood by StrPix's MQO importer so the mesh can be automatically textured.

The .rec exporter exports the UVs to a text file suitable for import into TextureAdd.
The UVs are assumed to be rectangles or triangles which are one corner of a rectangle. Lightmap packed UVs satisfy this requirement.
TextureAdd uses the .rec file to define the textures from a 256 x 256 image that are used for each face of the mesh.
version v2.4 adds option in export file dialog to export UVs according to 128 x 128 image. The 128 x 128 image must be located in the top left corner of the texture page in TextureAdd.

For Blender 2.72 to 2.79 use version v1.1 (Click on "Releases").
For Blender 2.80 use version v2.x.
For Blender 2.81 must use version v2.3 or higher. 
