# Custom-OBJ-Exporter
Custom OBJ exporter that allows you to export models from scenes in Autodesk Maya as .OBJ. These then work by simply dragging them into the program again.

Just like Maya itself, this OBJ exporter creates a .obj and .mtl file.
As usual, the .obj-file saves all the vertex-data, ie position, uv, normal, and builds all faces together.
The mtl-file holds the material-data, which describes the materials defined in the .obj file.

The exporter has the choice to:
- Triangulate the model before export
- Export whole scene och just the selecte3d objects
- Export material [.mtl-file]
- Export scene i local- or worldspace

#### Written in PyMEL
