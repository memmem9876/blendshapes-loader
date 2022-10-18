from pxr import Usd, UsdGeom, UsdSkel
import omni.usd
import asyncio
import os
import numpy as np
import struct
import re

try:
    from pygltflib import GLTF2
except:# noqa
    omni.kit.pipapi.install("pygltflib==1.15.3")
    from pygltflib import GLTF2


class Usd_Operation():
    _input_path = ""
    _output_path = ""
    _window = None

    def __init__(self, window):
        self._usd_context = omni.usd.get_context()
        self._events = self._usd_context.get_stage_event_stream()
        self._stage_event_delegate = self._events.create_subscription_to_pop(
            self.on_stage_event, name="se"
        )
        self._window = window
        Usd_Operation._window = window
        self._di = 0

        self._input_path = ""
        self._output_path = ""
        self._prim_blendshapes = []

    def destroy(self):
        self._events = None
        self._stage_event_delegate.unsubscribe()
        if self._di != 0:
            self._window._detail_intslider.model.remove_value_changed_fn(self._di)
        self._usd_context = None
        self._window = None
        Usd_Operation._window = None

    def on_stage_event(self, event):
        self._window.change_detail()
        self._window.change_blendshapes_view()
        
        # get_prim = Usd_Operation.get_select_prim()
        # if get_prim is None:
        #    return
        # self._prim = get_prim
    
    # default_filter_handler
    def default_filter_handler(filename: str, filter_postfix: str, filter_ext: str) -> bool:
        if not filename:
            return False
        ext = os.path.splitext(filename)
        if ext[1] in filter_ext:
            return True
        else:
            return False

    # import_handler
    def import_handler(filename, dirname, selections):
        if filename == "" or dirname == "":
            return
        print(selections)
        Usd_Operation._input_path = f"{dirname}{filename}"
        Usd_Operation._output_path = f"{dirname}output_convert/{filename}.usd"
        
        # delete_prim
        stage = omni.usd.get_context().get_stage()
        defaultPrim = stage.GetDefaultPrim()
        defaultPrimPath = defaultPrim.GetPath().pathString
        rootpath = filename[:filename.rfind('.')]
        path = defaultPrimPath + "/" + re.sub(r"[^a-zA-Z0-9]", "_", rootpath)

        prim = stage.GetPrimAtPath(path)
        if prim.IsValid():
            stage.RemovePrim(path)            
        Usd_Operation.gltf_covert(Usd_Operation._window, Usd_Operation._input_path, Usd_Operation._output_path)
        return

    def gltf_open():
        fet = [(".gltf|.glb", ""), ("", "")]
        file_importer = omni.kit.window.file_importer.get_file_importer()
        file_importer.show_window(
            title="Import_Gltf",
            import_handler=Usd_Operation.import_handler,
            file_filter_handler=Usd_Operation.default_filter_handler,
            file_extension_types=fet
            )
        # omni.kit.pipapi.install("pygltflib==1.15.3")

    # usd_instance
    def usd_instance():
        stage = omni.usd.get_context().get_stage()
        # Get default prim.
        defaultPrim = stage.GetDefaultPrim()
        defaultPrimPath = defaultPrim.GetPath().pathString
        ip = Usd_Operation._input_path
        rootpath = ip[ip.rfind('/')+1:ip.rfind('.')]
        path = defaultPrimPath + "/" + re.sub(r"[^a-zA-Z0-9]", "_", rootpath)

        # TopPrim Usd Set
        prim_x = UsdGeom.Xform.Define(stage, path)
        prim_x.GetPrim().GetReferences().AddReference(Usd_Operation._output_path)
        
        return [x for x in Usd.PrimRange(prim_x.GetPrim()) if UsdGeom.Mesh(x)]

    # gltf_load get blendshapes
    def gltf_load(mesh_names):
        # from pygltflib import GLTF2
        meshstr = ""

        local_input_path = omni.client.get_local_file(Usd_Operation._input_path)
        print(local_input_path[0])
        print(local_input_path[1])
        gltf = GLTF2().load(local_input_path[1])
        for mesh in gltf.meshes:
            meshstr += f":meshname:{mesh.name}\n"
            mesh_names[mesh.name] = {}
            if "targetNames" not in mesh.extras:
                continue
            targetNames = mesh.extras["targetNames"]
            for targetName in targetNames:
                mesh_names[mesh.name][targetName] = []
                meshstr += targetName+"\n"
            for primitive in mesh.primitives:                
                for i in range(len(primitive.targets)):
                    # print("blendshape: "+targetNames[i])
                    accessor_target = gltf.accessors[primitive.targets[i]["POSITION"]]
                    bufferView_target = gltf.bufferViews[accessor_target.bufferView]
                    buffer_target = gltf.buffers[bufferView_target.buffer]
                    data_target = gltf.get_data_from_buffer_uri(buffer_target.uri)
                    if data_target is None:
                        local_input_path_bin = omni.client.get_local_file(
                            Usd_Operation._input_path[:Usd_Operation._input_path.rfind('.')]+".bin"
                            )
                        data_target = gltf.get_data_from_buffer_uri(local_input_path_bin[1])
                        if data_target is None:
                            print("gltf_load_err")
                            continue
                    for i0 in range(accessor_target.count):
                        # the location in the buffer of this vertex
                        index = bufferView_target.byteOffset + accessor_target.byteOffset + i0*12
                        d = data_target[index:index+12]  # the vertex data
                        v = struct.unpack("<fff", d)   # convert from base64 to three floats
                        mesh_names[mesh.name][targetNames[i]].append(v)
                    # print()
                continue
        # print("meshname: "+name)
        omni.client.write_file(
            Usd_Operation._output_path[:Usd_Operation._output_path.rfind(".")]+"_name_list.txt",
            bytes(meshstr, 'utf-8')
            )
        return

    # create_blendshapes usd_add_blendshape
    def create_blendshapes(mesh_prims, blendshapes, use_meter_as_world_unit):
        # meshname:blendshapes
        #          blendshapes          
        # 
        # for k, v in mesh_names.items():
        #        print("mesh_name: "+k)
        #        for w,z in v.items():
        #            print("blendshape_name: "+w)
        #            for z0 in z:
        #                print(z0)
        # 
        if use_meter_as_world_unit:
            scale = 1
        else:
            scale = 100

        print("createblendshapes")
        
        for i, (meshname, blendshapenames) in enumerate(blendshapes.items()):
            stage = omni.usd.get_context().get_stage()

            print(meshname)
            for blendshape_index, (blendshapename, vs) in enumerate(blendshapenames.items()):
                print(blendshapename)
                mesh_v = mesh_prims[i].GetAttribute("points").Get()
                print("meshv_cout:   "+str(len(mesh_v)))
                print("shape_cout:   "+str(len(vs)))
                if len(mesh_v) != len(vs):
                    continue
                
                vsn = np.array(vs)
                blendshape_data = []
                blendshape_indices = [x for x in range(len(vsn))]
                for index, v in enumerate(vsn):
                    offset = v * scale
                    blendshape_data.append(offset)
                
                # blendshape_prim = UsdSkel.BlendShape.Define(
                # stage, mesh_prims[i].GetPath().AppendChild("shape"+str(blendshape_index))) # 
                blendshape_prim = UsdSkel.BlendShape.Define(
                    stage, 
                    mesh_prims[i].GetPath().AppendChild(
                        f"I_{blendshape_index:04}_"+re.sub(r"[^a-zA-Z0-9]", "_", blendshapename)
                        )
                    )
                # vertex_pos
                blendshape_prim.CreateOffsetsAttr().Set(blendshape_data)
                # vertex_index
                blendshape_prim.CreatePointIndicesAttr().Set(blendshape_indices)

            # Apply BindingAPI onto Mesh, then associate the blend shape targets with the mesh.
            blendshapes_attr = []
            blendshapes_path = []
            for blendshape_index, (blendshapename, vs) in enumerate(blendshapenames.items()):
                # blendshapes_attr.append("shape"+str(blendshape_index))
                blendshapes_attr.append(f"I_{blendshape_index:04}_"+re.sub(r"[^a-zA-Z0-9]", "_", blendshapename))
                # blendshapes_path.append(mesh_prims[i].GetPath().pathString+"/"+"shape"+str(blendshape_index))
                blendshapes_path.append(
                    mesh_prims[i].GetPath().pathString+"/"+f"I_{blendshape_index:04}_"+re.sub(
                        r"[^a-zA-Z0-9]", "_", blendshapename
                        )
                    )

            meshBinding = UsdSkel.BindingAPI.Apply(mesh_prims[i])
            meshBinding.CreateBlendShapesAttr().Set(blendshapes_attr)
            meshBinding.CreateBlendShapeTargetsRel().SetTargets(blendshapes_path)
            # meshBinding.Apply(mesh_prims[i])

    # gltf_covert
    def gltf_covert(_window, input_obj, output_usd):
        def progress_callback(current_step: int, total: int):
            print(f"{current_step} of {total}")

        async def convert_asset_to_usd(input_asset: str, output_usd: str):
            # Input options are defaults.
            converter_context = omni.kit.asset_converter.AssetConverterContext()
            converter_context.ignore_materials = Usd_Operation._window._checkbox_ignore_materials.model.get_value_as_bool()  # noqa
            converter_context.ignore_camera = Usd_Operation._window._checkbox_ignore_camera.model.get_value_as_bool()  # noqa
            converter_context.ignore_animations = Usd_Operation._window._checkbox_ignore_animations.model.get_value_as_bool()  # noqa
            converter_context.ignore_light = Usd_Operation._window._checkbox_ignore_light.model.get_value_as_bool()  # noqa
            converter_context.export_preview_surface = Usd_Operation._window._checkbox_export_preview_surface.model.get_value_as_bool()  # noqa
            converter_context.use_meter_as_world_unit = Usd_Operation._window._checkbox_use_meter.model.get_value_as_bool()  # noqa
            converter_context.create_world_as_default_root_prim = Usd_Operation._window._checkbox_create_world_as_default_root_prim.model.get_value_as_bool() # noqa
            converter_context.embed_textures = Usd_Operation._window._checkbox_embed_textures.model.get_value_as_bool()  # noqa
            converter_context.convert_fbx_to_y_up = Usd_Operation._window._checkbox_convert_fbx_to_y_up.model.get_value_as_bool()  # noqa
            converter_context.convert_fbx_to_z_up = Usd_Operation._window._checkbox_convert_fbx_to_z_up.model.get_value_as_bool()  # noqa
            converter_context.merge_all_meshes = Usd_Operation._window._checkbox_merge_all_meshes.model.get_value_as_bool()  # noqa
            converter_context.use_double_precision_to_usd_transform_op = Usd_Operation._window._checkbox_use_double_precision_to_usd_transform_op.model.get_value_as_bool() # noqa
            converter_context.ignore_pivots = Usd_Operation._window._checkbox_ignore_pivots.model.get_value_as_bool()  # noqa
            converter_context.keep_all_materials = Usd_Operation._window._checkbox_keep_all_materials.model.get_value_as_bool()  # noqa
            converter_context.smooth_normals = Usd_Operation._window._checkbox_smooth_normals.model.get_value_as_bool()  # noqa
            instance = omni.kit.asset_converter.get_instance()
            task = instance.create_converter_task(input_asset, output_usd, progress_callback, converter_context)

            success = await task.wait_until_finished()
            if not success:
                # carb.log_error(task.get_status(), task.get_detailed_error())
                return
            print("converting done")

            # get blendshapes from gltf
            blendshapes = {}
            Usd_Operation.gltf_load(blendshapes)
            mesh_prims = Usd_Operation.usd_instance()
            Usd_Operation.create_blendshapes(mesh_prims, blendshapes, converter_context.use_meter_as_world_unit)

        # Convert to USD
        asyncio.ensure_future(convert_asset_to_usd(input_obj, output_usd))

    # export_PropertyNames
    def check_property_names(prim):
        return prim.GetPropertyNames()

    # export__check_attr
    def check_attr(prim):
        return [str(prim.GetAttribute(x).Get()) for x in prim.GetPropertyNames()]

    # export__check_rel
    def check_rel(prim):
        rels = []
        for x in prim.GetPropertyNames():
            if prim.GetRelationship(x).IsValid():
                rels.append(str(prim.GetRelationship(x).GetTargets()))
            else:
                rels.append("")
        return rels

    # check_dir select prim
    def get_select_prim():
        stage = omni.usd.get_context().get_stage()
        selection = omni.usd.get_context().get_selection()
        paths = selection.get_selected_prim_paths()
        if len(paths) == 0:
            return None
        prim = stage.GetPrimAtPath(paths[0])
        return prim

    # export str usd
    def check_usd_str():
        stage = omni.usd.get_context().get_stage()
        return stage.ExportToString()

    # check_dir select prim
    def checkprimdir():
        stage = omni.usd.get_context().get_stage()
        selection = omni.usd.get_context().get_selection()
        paths = selection.get_selected_prim_paths()
        for path in paths:
            prim = stage.GetPrimAtPath(path)
            prim.GetTypeName()
            print(dir(prim))
        return
