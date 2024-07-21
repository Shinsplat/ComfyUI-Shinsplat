# Shinsplat Tarterbox
import os
import sys
import json
import folder_paths

from . import functions as sf

help ="""
nothing
"""

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_TestNode:
    """
    - Shinsplat Tarterbox -

    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text_": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                },
            "optional": {
                        "in_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                        },
            }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("_out", )

    FUNCTION = "test"

    CATEGORY = "advanced/Shinsplat"

    def IS_CHANGED(c):
        return

    def test(self, text_="", in_=""):

        print("=====================================")
        print("test node runs")
        print("=====================================")

        #self.trigger = not self.trigger

        out_ = in_ + " " + text_

        return(out_,)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Test Node (Shinsplat)": Shinsplat_TestNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Test Node (Shinsplat)": "Test Node (Shinsplat)"
}
