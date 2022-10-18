__all__ = ["example_window_style"]

from omni.ui import color as cl
from omni.ui import constant as fl
import omni.kit.app
import omni.ui as ui
import pathlib

EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)
# Pre-defined constants. It's possible to change them runtime.
cl.window_attribute_bg = cl("#1f2124")
cl.window_attribute_fg = cl("#0f1115")
cl.window_hovered = cl("#FFFFFF")
cl.window_text = cl("#CCCCCC")
fl.window_convert_usd_hspacing = 5

fl.window_attr_hspacing = 10
fl.window_attr_spacing = 2
fl.window_group_spacing = 2

# The main style dict
example_window_style = {
    "HStack::convert_usd": {
    },
    "CheckBox::convert_usd": {
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_attr_hspacing,
    },
    "Label::convert_usd": {
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_convert_usd_hspacing,
    },
    "Button::convert_usd": {
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_convert_usd_hspacing,
        "background_color": cl.window_attribute_bg,
    },
    "CollapsableFrame::convert_usd": {
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_convert_usd_hspacing,
    },
    "Label::blendshapes": {
        "alignment": ui.Alignment.RIGHT_CENTER,
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_attr_hspacing,
    },
    "Button::blendshapes": {
        "background_color": cl("#bce2e8"),
        "margin_height": 1,
        "margin_width": 5,
    },
    "StringField::detail": {
        "alignment": ui.Alignment.RIGHT_CENTER,
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_attr_hspacing,
    },
    "ScrollingFrame::detail_path": {
        "background_color": cl.window_attribute_bg,
    },
    "Label::detail_path": {
        "alignment": ui.Alignment.LEFT_CENTER,
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_attr_hspacing,
        "background_color": cl.window_attribute_bg,
    },
    "Label::attribute_name": {
        "alignment": ui.Alignment.RIGHT_CENTER,
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_attr_hspacing,
    },
    "Label::attribute_name:hovered": {"color": cl.window_hovered},
    "Label::collapsable_name": {"alignment": ui.Alignment.LEFT_CENTER},
    "Slider::attribute_int:hovered": {"color": cl.window_hovered},
    "Slider": {
        "background_color": cl.window_attribute_bg,
        "draw_mode": ui.SliderDrawMode.HANDLE,
    },
    "Slider::attribute_float": {
        "draw_mode": ui.SliderDrawMode.FILLED,
        "secondary_color": cl.window_attribute_fg,
    },
    "Slider::attribute_float:hovered": {"color": cl.window_hovered},
    "Slider::attribute_vector:hovered": {"color": cl.window_hovered},
    "Slider::attribute_color:hovered": {"color": cl.window_hovered},
    "CollapsableFrame::group": {
        "margin_height": fl.window_attr_spacing,
        "margin_width": fl.window_convert_usd_hspacing,
        },
}
