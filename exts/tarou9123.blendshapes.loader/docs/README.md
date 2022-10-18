# Extension BlendShapes Loader

- Place the gltf file with blendshapes on the stage.
- Select a mesh with blendshapes and you will see a list of blendshapes.
- Blendshapes can be changed using slider.

# ToUse

- Set the checkbox for the Convert option and click the Open Gltf button or drop a glb or gltf file from the Content window into the blendshapes Loader window
The converted mesh will be displayed on the stage

- Select a mesh with blendshapes.
A list of blendshapes will appear in the window
The shape of the mesh that moves the slider will change

- Select a prim and slide the slider at the bottom to
properties, attributes, and relationships.

# Adding Extensions

Launch the Omniverse Kit-based app and click
Extension Manager -> Gear Icon -> Extension Search Path
Add a search path
`git://github.com/tanakatarou9123rog/blendshapes-loader.git?branch=master&dir=exts`

# Known Limitations

- When a gltf file is converted, any characters that cannot be attached to the prim's name are replaced with _.
The original name is stored in a text file stored in the output_convert folder


