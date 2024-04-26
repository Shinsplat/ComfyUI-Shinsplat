# Shinsplat Tarterbox

from .clip_text_encode import *
from .clip_text_encode_sdxl import *
from .lora_loader import *
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": Shinsplat_CLIPTextEncode,
    "Clip Text Encode SDXL (Shinsplat)": Shinsplat_CLIPTextEncodeSDXL,
    "Lora Loader (Shinsplat)": Shinsplat_LoraLoader
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": "Clip Text Encode (Shinsplat)",
    "Clip Text Encode SDXL (Shinsplat)": "Clip Text Encode SDXL (Shinsplat)",
    "Lora Loader (Shinsplat)": "Lora Loader (Shinsplat)"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
