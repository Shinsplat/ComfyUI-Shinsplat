# Shinsplat Tarterbox

"""
@author: Shinsplat
@title: ComfyUI-Shinsplat
@nickname: shinsplat
@description:

ComfyUI Node alterations that I found useful in my own projects and for friends.
"""

from .shinsplat_clip_text_encode import *
from .shinsplat_clip_text_encode_T5 import *
from .shinsplat_clip_text_encode_SD3 import *
from .shinsplat_clip_text_encode_sdxl import *
from .shinsplat_lora_loader import *
from .shinsplat_sum_wrap import *
from .shinsplat_green_box import *
from .shinsplat_python import *
from .shinsplat_python_more import *
from .shinsplat_string_interpolated import *
from .shinsplat_variables import *

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": Shinsplat_CLIPTextEncode,
    "Clip Text Encode T5 (Shinsplat)": Shinsplat_CLIPTextEncodeT5,
    "Clip Text Encode SD3 (Shinsplat)": Shinsplat_CLIPTextEncodeSD3,
    "Clip Text Encode SDXL (Shinsplat)": Shinsplat_CLIPTextEncodeSDXL,
    "Lora Loader (Shinsplat)": Shinsplat_LoraLoader,
    "Sum Wrap (Shinsplat)": Shinsplat_SumWrap,
    "Green Box (Shinsplat)": Shinsplat_GreenBox,
    "Python (Shinsplat)": Shinsplat_Python,
    "Python - More Inputs (Shinsplat)": Shinsplat_PythonMore,
    "String Interpolated (Shinsplat)": Shinsplat_StringInterpolated,
    "Variables (Shinsplat)": Shinsplat_Variables,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": "Clip Text Encode (Shinsplat)",
    "Clip Text Encode T5 (Shinsplat)": "Clip Text Encode T5 (Shinsplat)",
    "Clip Text Encode SD3 (Shinsplat)": "Clip Text Encode SD3 (Shinsplat)",
    "Clip Text Encode SDXL (Shinsplat)": "Clip Text Encode SDXL (Shinsplat)",
    "Lora Loader (Shinsplat)": "Lora Loader (Shinsplat)",
    "Green Box (Shinsplat)": "Green Box (Shinsplat)",
    "Python (Shinsplat)": "Python (Shinsplat)",
    "Python - More Inputs (Shinsplat)": "Python - More Inputs (Shinsplat)",
    "String Interpolated (Shinsplat)": "String Interpolated (Shinsplat)",
    "Variables (Shinsplat)": "Variables (Shinsplat)",
}
WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
