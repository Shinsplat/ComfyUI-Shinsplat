# Shinsplat Tarterbox

"""
@author: Shinsplat
@title: Shinsplat
@nickname: shinsplat
@description:
whatever
@license:
If you infer one you're making a mistake.  Your output belongs to you, the code belongs to, most likely not you.
"""

from .test_node import *
from .clip_text_encode import *
from .clip_text_encode_T5 import *
from .clip_text_encode_SD3 import *
from .clip_text_encode_sdxl import *
from .lora_loader import *
from .sum_wrap import *
from .green_box import *
from .python import *
from .python_more import *
from .string_interpolated import *
from .variables import *
from .hex_to_other import *
from .clip_tokens_encode import *
from .text_to_tokens import *
from .text_to_tokens_SD3 import *
from .tensor_toys import *
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Test Node (Shinsplat)": Shinsplat_TestNode,
    "Clip Text Encode (Shinsplat)": Shinsplat_CLIPTextEncode,
    "Clip Text Encode T5 (Shinsplat)": Shinsplat_CLIPTextEncodeT5,
    "Clip Text Encode SD3 (Shinsplat)": Shinsplat_CLIPTextEncodeSD3,
    "Clip Text Encode SDXL (Shinsplat)": Shinsplat_CLIPTextEncodeSDXL,
    "Clip Tokens Encode (Shinsplat)": Shinsplat_CLIPTokensEncode,
    "Tensor Toys (Shinsplat)": Shinsplat_TensorToys,
    "Text To Tokens (Shinsplat)": Shinsplat_TextToTokens,
    "Text To Tokens SD3 (Shinsplat)": Shinsplat_TextToTokensSD3,
    "Lora Loader (Shinsplat)": Shinsplat_LoraLoader,
    "Sum Wrap (Shinsplat)": Shinsplat_SumWrap,
    "Green Box (Shinsplat)": Shinsplat_GreenBox,
    "Python (Shinsplat)": Shinsplat_Python,
    "Python - More Inputs (Shinsplat)": Shinsplat_PythonMore,
    "String Interpolated (Shinsplat)": Shinsplat_StringInterpolated,
    "Variables (Shinsplat)": Shinsplat_Variables,
    "Hex To Other (Shinsplat)": Shinsplat_HexToOther,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Test Node (Shinsplat)": "Test Node (Shinsplat)",
    "Clip Text Encode (Shinsplat)": "Clip Text Encode (Shinsplat)",
    "Clip Text Encode T5 (Shinsplat)": "Clip Text Encode T5 (Shinsplat)",
    "Clip Text Encode SD3 (Shinsplat)": "Clip Text Encode SD3 (Shinsplat)",
    "Clip Text Encode SDXL (Shinsplat)": "Clip Text Encode SDXL (Shinsplat)",
    "Clip Tokens Encode (Shinsplat)": "Clip Tokens Encode (Shinsplat)",
    "Tensor Toys (Shinsplat)": "Tensor Toys (Shinsplat)",
    "Text To Tokens (Shinsplat)": "Text To Tokens (Shinsplat)",
    "Text To Tokens SD3 (Shinsplat)": "Text To Tokens SD3 (Shinsplat)",
    "Lora Loader (Shinsplat)": "Lora Loader (Shinsplat)",
    "Green Box (Shinsplat)": "Green Box (Shinsplat)",
    "Python (Shinsplat)": "Python (Shinsplat)",
    "Python - More Inputs (Shinsplat)": "Python - More Inputs (Shinsplat)",
    "String Interpolated (Shinsplat)": "String Interpolated (Shinsplat)",
    "Variables (Shinsplat)": "Variables (Shinsplat)",
    "Hex To Other (Shinsplat)": "Hex To Other (Shinsplat)",
}
WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
