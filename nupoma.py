
from . import functions as sf

help ="""
The term "Nuclear Popcorn Machine" was suggested by my wife, it has no meaning except to be goofy, and I think it's brilliant in its nonsensicalness.
"""

class Shinsplat_Nupoma:

    def __init__(self):
        self.trigger = False

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
                "string": ("STRING", {"multiline": False, "default": "empty", "dynamicPrompts": False}),
                "int": ("INT", {"default": 4, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
                "float": ("FLOAT", {"default": 0.0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
            },
            "optional": {
            },
            "hidden": {
            },
        }

    RETURN_TYPES = ("STRING",   "STRING",)
    RETURN_NAMES = ("_control", "help",)
    FUNCTION = "controller_settings"
    CATEGORY = "advanced/shinsplat"

# T - for testing the storage class
#    OUTPUT_NODE = True
# /

    def controller_settings(self, **kwargs):
        self.trigger = not self.trigger

        controller = ""
        if kwargs['enabled']:
            # The input items aren't nested ever, as far as I can tell, so a simple conversion is fine.
            controller = '{\n'
            for k in kwargs:
                v = kwargs[k]
                vs = str(v)
                if isinstance(v, str):
                    vs = '"' + v + '"'
                controller += "    "
                controller += '"' + k + '": ' + vs + ',\n'
            controller += '}\n'

        return (controller, help,)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Nupoma (Shinsplat)": Shinsplat_Nupoma,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Nupoma (Shinsplat)": "Nupoma (Shinsplat)",
}

