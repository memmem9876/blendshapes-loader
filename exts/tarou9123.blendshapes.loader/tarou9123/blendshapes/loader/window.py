__all__ = ["MainWindow"]

import omni.ui as ui
import omni.usd
from .style import example_window_style
from .usd_operation import Usd_Operation
import copy
import time
import re
from functools import partial

LABEL_WIDTH = 120
SPACING = 4


class MainWindow(ui.Window):
    """The class that represents the window"""

    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = LABEL_WIDTH

        super().__init__(title, **kwargs)

        self.frame.style = example_window_style
        self.frame.set_build_fn(self._build_fn)
        self.scr = None
        self.last_select_prim = None

        self._blendshapes_basemesh = {}
        self._blendshapes_slider_oldvalue = {}
        self._blendshapes_slider_value = {}
        self._blendshapes_frame = None
        self._blendshapes_FloatSlider_list = []
        self._blendshapes_reset_val_button_list = []
        self._blendshapes_change_mesh_time = 0
        self._blendshapes_change_mesh_time_interval = 0.05
        self._blendshape_select_prim = None
        
        self._detail_label_0 = None
        self._detail_label_1 = None
        self._detail_label_2 = None
        self._detail_intslider = None

        self._checkbox_ignore_materials = None
        self._checkbox_ignore_camera = None
        self._checkbox_ignore_animations = None
        self._checkbox_ignore_light = None
        self._checkbox_export_preview_surface = None
        self._checkbox_use_meter = None
        self._checkbox_create_world_as_default_root_prim = None
        self._checkbox_embed_textures = None
        self._checkbox_convert_fbx_to_y_up = None
        self._checkbox_convert_fbx_to_z_up = None
        self._checkbox_merge_all_meshes = None
        self._checkbox_use_double_precision_to_usd_transform_op = None
        self._checkbox_ignore_pivots = None
        self._checkbox_keep_all_materials = None
        self._checkbox_smooth_normals = None
        self._button_open_gltf = None

        self._di = 0

    def destroy(self):
        super().destroy()
        self._button_open_gltf.set_clicked_fn(None)
        if self._di != 0:
            self._detail_intslider.model.remove_value_changed_fn(self._di)

    @property
    def label_width(self):
        """The width of the attribute label"""
        return self.__label_width

    @label_width.setter
    def label_width(self, value):
        """The width of the attribute label"""
        self.__label_width = value
        self.frame.rebuild()

    def _build_convert(self):
        with ui.CollapsableFrame("Convert", height=0, name="convert_usd", build_header_fn=self._build_collapsable_header):# noqa
            with ui.VStack(spacing=SPACING):
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_ignore_materials = ui.CheckBox(name="convert_usd")
                    ui.Label("ignore_materials", name="convert_usd")
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_ignore_camera = ui.CheckBox(name="convert_usd")
                    ui.Label("ignore_camera", name="convert_usd")
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_ignore_animations = ui.CheckBox(name="convert_usd")
                    ui.Label("ignore_animations", name="convert_usd")
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_ignore_light = ui.CheckBox(name="convert_usd")
                    ui.Label("ignore_light", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_export_preview_surface = ui.CheckBox(name="convert_usd")
                    ui.Label("export_preview_surface", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_use_meter = ui.CheckBox(name="convert_usd")
                    ui.Label("use_meter_as_world_unit", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_create_world_as_default_root_prim = ui.CheckBox(name="convert_usd")
                    ui.Label("create_world_as_default_root_prim", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_embed_textures = ui.CheckBox(name="convert_usd")
                    ui.Label("embed_textures", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_convert_fbx_to_y_up = ui.CheckBox(name="convert_usd")
                    ui.Label("convert_fbx_to_y_up", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_convert_fbx_to_z_up = ui.CheckBox(name="convert_usd")
                    ui.Label("convert_fbx_to_z_up", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_merge_all_meshes = ui.CheckBox(name="convert_usd")
                    ui.Label("merge_all_meshes", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_use_double_precision_to_usd_transform_op = ui.CheckBox(name="convert_usd")
                    ui.Label("use_double_precision_to_usd_transform_op", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_ignore_pivots = ui.CheckBox(name="convert_usd")
                    ui.Label("ignore_pivots", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_keep_all_materials = ui.CheckBox(name="convert_usd")
                    ui.Label("keep_all_materials", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", width=0):
                    self._checkbox_smooth_normals = ui.CheckBox(name="convert_usd")
                    ui.Label("smooth_normals", name="convert_usd", width=0)
                with ui.HStack(name="convert_usd", height=0):
                    self._button_open_gltf = ui.Button("Open Gltf", name="convert_usd", height=50)

    def _build_collapsable_header(self, collapsed, title):
        with ui.HStack():
            ui.Label(title, name="collapsable_name")

    def _build_detail(self):
        with ui.CollapsableFrame("Detail", name="group", build_header_fn=self._build_collapsable_header):
            with ui.VStack(height=0, spacing=SPACING):
                with ui.ScrollingFrame(name="detail_path", height=35):
                    self._detail_label_2 = ui.Label("", name="detail_path")
                self._detail_label_0 = ui.Label("", name="attribute_name", style={"alignment": ui.Alignment.LEFT})
                self._detail_intslider = ui.IntSlider(name="attribute_int", min=0, max=3, style={"color": 0x0})
                ui.Spacer(height=20)
                with ui.CollapsableFrame():
                    with ui.ScrollingFrame(
                        height=200, 
                            # horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                            verical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON
                            ):
                        self._detail_label_1 = ui.StringField(name="detail")
                        self._detail_label_1.multiline = True

    def _build_blendshapes(self):
        self._blendshapes_frame = ui.CollapsableFrame(
            "BlendShapes", 
            name="group", 
            build_header_fn=self._build_collapsable_header
            )
                    
    def _build_fn(self):
        """
        The method that is called to build all the UI once the window is
        visible.
        """
        self.scr = ui.ScrollingFrame()
        # bug
        self.scr.set_accept_drop_fn(self.drop_file_accept)
        self.scr.set_drop_fn(self.drop_file)
        with self.scr:
            with ui.VStack(height=0):
                self._build_convert()
                self._build_blendshapes()
                self._build_detail()
        self.init()
        self.init_convert_usd_ui()

    def drop_file(self, path):
        match = re.search(r"([^/]*?)gltf$|([^/]*?)glb$", path.mime_data)
        if not match:
            return
        filename = match.group()
        dir = path.mime_data[:path.mime_data.rfind('/')+1]
        # omni.kit.pipapi.install("pygltflib==1.15.2")
        Usd_Operation.import_handler(filename, dir, path)
        pass

    def drop_file_accept(self, path):
        match = re.search(r"glb$|gltf$", path)
        if match:
            return True
        else:
            return False

    def reset_slider(self, slider):
        slider.model.set_value(0)
        # self.change_mesh(True)

    def reset_mesh(self):
        stage = omni.usd.get_context().get_stage()
        for x in self._blendshapes_FloatSlider_list:
            x.model.set_value(0)
        for k, v in self._blendshapes_basemesh.items():
            prim = stage.GetPrimAtPath(k)
            prim.GetAttribute("points").Set(v)
        self._blendshapes_slider_value.clear()
        self._blendshapes_slider_oldvalue.clear()

    def change_mesh(self, slider, model):
        if (time.time() - self._blendshapes_change_mesh_time) < self._blendshapes_change_mesh_time_interval:
            return
        prim = Usd_Operation.get_select_prim()
        if prim is None:
            prim = self._blendshape_select_prim
            if prim is None:
                return
        if prim.GetPath().pathString not in self._blendshapes_basemesh:
            return
        self._blendshape_select_prim = prim

        pm = prim.GetAttribute("points").Get()
        stage = omni.usd.get_context().get_stage()        

        old_value = 0
        if slider.identifier in self._blendshapes_slider_oldvalue.keys():
            old_value = self._blendshapes_slider_oldvalue[slider.identifier]
        value = slider.model.get_value_as_float()
        
        difference_value = value - old_value
        prim_blendshape = stage.GetPrimAtPath(slider.identifier)
        offset = prim_blendshape.GetAttribute("offsets").Get()
        for i, tt in enumerate(offset):
            pm[i] = pm[i]+tt*difference_value
        prim.GetAttribute("points").Set(pm)

        self._blendshapes_slider_value[slider.identifier] = slider.model.get_value_as_float()
        self._blendshapes_slider_oldvalue[slider.identifier] = slider.model.get_value_as_float()

        self._blendshapes_change_mesh_time = time.time()

    def change_mesh_end(self, slider, model):
        prim = Usd_Operation.get_select_prim()
        if prim is None:
            prim = self._blendshape_select_prim
            if prim is None:
                return
        if prim.GetPath().pathString not in self._blendshapes_basemesh:
            return
        self._blendshape_select_prim = prim

        pm = prim.GetAttribute("points").Get()
        stage = omni.usd.get_context().get_stage()        

        old_value = 0
        if slider.identifier in self._blendshapes_slider_oldvalue.keys():
            old_value = self._blendshapes_slider_oldvalue[slider.identifier]
        value = slider.model.get_value_as_float()
        
        difference_value = value - old_value
        prim_blendshape = stage.GetPrimAtPath(slider.identifier)
        offset = prim_blendshape.GetAttribute("offsets").Get()
        for i, tt in enumerate(offset):
            pm[i] = pm[i]+tt*difference_value
        prim.GetAttribute("points").Set(pm)

        self._blendshapes_slider_value[slider.identifier] = slider.model.get_value_as_float()
        self._blendshapes_slider_oldvalue[slider.identifier] = slider.model.get_value_as_float()

    # called from on_stage_event
    def change_blendshapes_view(self):
        prim = Usd_Operation.get_select_prim()
        if not prim:
            if self.last_select_prim:
                prim = self.last_select_prim
            else:
                return
        if not prim.GetRelationship("skel:blendShapeTargets").IsValid():
            return

        # basemesh_save
        if prim.GetPath().pathString not in self._blendshapes_basemesh:
            pm = prim.GetAttribute("points").Get()
            prim_mesh_v = copy.deepcopy(list(pm))
            self._blendshapes_basemesh[prim.GetPath().pathString] = prim_mesh_v

        # slider_val_save
        for slider_val in self._blendshapes_FloatSlider_list:
            self._blendshapes_slider_value[slider_val.identifier] = slider_val.model.get_value_as_float()

        self._blendshapes_FloatSlider_list.clear()
        self._blendshapes_reset_val_button_list.clear()

        with self._blendshapes_frame:
            with ui.VStack(height=0, spacing=SPACING):
                # bug
                ui.Button("reset_value").set_clicked_fn(lambda: self.reset_mesh())
                for target in prim.GetRelationship("skel:blendShapeTargets").GetTargets():
                    with ui.HStack():
                        ui.Label(
                            target.pathString[target.pathString.rfind('/')+1:],
                            name="blendshapes", 
                            width=self.label_width*2
                            )
                        slider = ui.FloatSlider(name="attribute_float")
                        slider.identifier = target.pathString
                        # slider_val_set if it exists
                        if target.pathString in self._blendshapes_slider_value.keys():
                            val = self._blendshapes_slider_value[target.pathString]
                            slider.model.set_value(val)
                        # bug
                        # slider.model.add_end_edit_fn(lambda x: self.change_mesh(True))
                        # slider.model.add_value_changed_fn(lambda x: self.change_mesh(False))
                        slider.model.add_end_edit_fn(partial(self.change_mesh_end, slider))
                        slider.model.add_value_changed_fn(partial(self.change_mesh, slider))
                        self._blendshapes_FloatSlider_list.append(slider)
                        button = ui.Button(" ", name="blendshapes", width=0)
                        self._blendshapes_reset_val_button_list.append(button)
                        # button.set_clicked_fn(lambda: self.reset_slider(slider))
                        button.set_clicked_fn(partial(self.reset_slider, slider))
                return

    # called from on_stage_event
    def change_detail(self):
        prim = Usd_Operation.get_select_prim()
        if not prim:
            if self.last_select_prim:
                prim = self.last_select_prim
            else:
                return
        self.last_select_prim = prim
        self._detail_label_2.text = prim.GetPath().pathString
        value = self._detail_intslider.model.get_value_as_int()
        if value == 0:
            property = Usd_Operation.check_property_names(prim)
            self._detail_label_0.text = "Property"
            self._detail_label_1.model.set_value("\n".join(property))
        elif value == 1:
            property = Usd_Operation.check_property_names(prim)
            attr = Usd_Operation.check_attr(prim)
            self._detail_label_0.text = "Attribute"
            x = [f"{x}:{attr[i]}" for i, x in enumerate(property)]
            self._detail_label_1.model.set_value("\n".join(x))
        elif value == 2:
            property = Usd_Operation.check_property_names(prim)
            rel = Usd_Operation.check_rel(prim)
            self._detail_label_0.text = "Relationship"
            x = [f"{x}:{rel[i]}" for i, x in enumerate(property)]
            self._detail_label_1.model.set_value("\n".join(x))
        elif value == 3:
            usd_str = Usd_Operation.check_usd_str()
            self._detail_label_0.text = "usd"
            self._detail_label_1.model.set_value(usd_str)

    def init(self):
        if self._di == 0:
            # bug_00
            self._di = self._detail_intslider.model.add_value_changed_fn(lambda x: self.change_detail())
            pass
   
    def on_button_open_gltf_to_usd(self):
        # bug
        Usd_Operation.gltf_open()
        pass

    def init_convert_usd_ui(self):
        # self._checkbox_ignore_materials.model.set_value(True)
        # self._checkbox_ignore_camera.model.set_value(True)
        # self._checkbox_ignore_animations.model.set_value(True)
        # self._checkbox_ignore_light.model.set_value(True)
        # self._checkbox_export_preview_surface.model.set_value(True)
        # self._checkbox_use_meter.model.set_value(True)
        # self._checkbox_create_world_as_default_root_prim.model.set_value(True)
        # self._checkbox_embed_textures.model.set_value(True)
        # self._checkbox_convert_fbx_to_y_up.model.set_value(True)
        # self._checkbox_convert_fbx_to_z_up.model.set_value(True)
        # self._checkbox_merge_all_meshes.model.set_value(True)
        # self._checkbox_use_double_precision_to_usd_transform_op.model.set_value(True)
        # self._checkbox_ignore_pivots.model.set_value(True)
        # self._checkbox_keep_all_materials.model.set_value(True)
        # self._checkbox_smooth_normals.model.set_value(True)
        self._checkbox_embed_textures.model.set_value(True)
        self._button_open_gltf.set_clicked_fn(lambda: self.on_button_open_gltf_to_usd())
        pass

