# Extension BlendShapes Loader

- Place the gltf file with blendshapes on the stage.
- Select a mesh with blendshapes and you will see a list of blendshapes.
- Blendshapes can be changed using slider.

![Videoconvert](https://user-images.githubusercontent.com/109241141/188797589-6a633385-7809-49f2-87c0-6d86f47280bf.gif)

![Video2](https://user-images.githubusercontent.com/109241141/188795824-b1ac9872-fa03-4145-872f-0a4983bf5fca.gif)

# To Use

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
`git://github.com/memmem9876/blendshapes-loader.git?branch=main&dir=exts`

# Known Limitations

- When a gltf file is converted, any characters that cannot be attached to the prim's name are replaced with _.
The original name is stored in a text file stored in the output_convert folder


