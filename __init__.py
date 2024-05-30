# Shinsplat Tarterbox

from .shinsplat_clip_text_encode import *
from .shinsplat_clip_text_encode_sdxl import *
from .shinsplat_lora_loader import *
from .shinsplat_sum_wrap import *
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": Shinsplat_CLIPTextEncode,
    "Clip Text Encode SDXL (Shinsplat)": Shinsplat_CLIPTextEncodeSDXL,
    "Lora Loader (Shinsplat)": Shinsplat_LoraLoader,
    "Sum Wrap (Shinsplat)": Shinsplat_SumWrap,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": "Clip Text Encode (Shinsplat)",
    "Clip Text Encode SDXL (Shinsplat)": "Clip Text Encode SDXL (Shinsplat)",
    "Lora Loader (Shinsplat)": "Lora Loader (Shinsplat)",
    "Sum Wrap (Shinsplat)": "Sum Wrap (Shinsplat)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------