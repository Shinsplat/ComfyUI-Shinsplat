# Shinsplat Tarterbox

import math
import traceback

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_HexToOther:
    """
    - Shinsplat Tarterbox -

    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        default = "0"
        return {
            "required": {
                "text": ("STRING", {"default": default, "multiline": False, "dynamicPrompts": False, "forceInput": True}),
                },
           }

    RETURN_TYPES = ("INT", "FLOAT", )
    RETURN_NAMES = ("_int", "_flt", )

    FUNCTION = "hex_to_other"

    CATEGORY = "advanced/Shinsplat"

    def hex_to_other(self, text):
        int_value = 0
        hex_string = text.strip()
        hex_string = hex_string.strip("#")
        try:
            if hex_string != "":
                flt_value = sum(int(x, 16) * math.pow(16, len(hex_string)-i-1) for i, x in enumerate(hex_string))
                int_value = int(flt_value)
        except Exception as e:
            txt = traceback.format_exc()
            raise Exception("Not a hex value")
            return(0,)

        return (int_value, flt_value,)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Hex To Other (Shinsplat)": Shinsplat_HexToOther
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Hex To Other (Shinsplat)": "Hex To Other (Shinsplat)"
}

