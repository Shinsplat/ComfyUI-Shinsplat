# Shinsplat Tarterbox
import os
import sys
import json
import folder_paths

from . import shinsplat_functions as sf

help ="""
# This code format is akin to JSON, it's a Python
# dictionary but is indiscernible in this particular
# usage.  It's very simple and you only need to add
# a token and a weight.  The "word" key/value is not
# necessary and is there only for reference.
{
    1929: {
        "weight": 1.2,
        "word": "dog</w>",
        },
    2368: {
        "weight": 1.5,
        "word": "cat</w>",
        },
    267: {
        "weight": 1,0,
        "word": ",</w>",
    }
}
"""

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_CLIPTokensEncode:
    """
    - Shinsplat Tarterbox -

    """

    def log(self, m,  **kwargs):
        if self.debug == True:
            if self.show_weights == True:
                if 'tokens' in kwargs:
                    tokens = kwargs['tokens']
                    txt = ""
                    for tensor_type in tokens:
                        for block in tokens[tensor_type]:
                            #txt += str(tokens[tensor_type][block]) + "\n"
                            txt += str(block) + "\n"
                    m += "\n" + txt
            print("===========================================")
            print(m)
            print("===========================================")
            self.debug = False
            self.show_weights = False
            return True
        return False

    def __init__(self):
        self.debug = False


    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "clip": ("CLIP", ),
                },
            "optional": {
                        "before_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                        "after_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                        },
            }

    RETURN_TYPES = ("CONDITIONING", "STRING", )
    RETURN_NAMES = ("CONDITIONING", "prompt_", )

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, text, before_="", after_=""):

        prompt_out = before_ + " " + after_


        return ([[cond, {"pooled_output": pooled}]], prompt_out)


    # ------------------------------------------------------------------------
    # base encoder
    # ------------------------------------------------------------------------
    #def encode(self, clip, text):
    #    tokens = clip.tokenize(text)
    #    cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
    #    return ([[cond, {"pooled_output": pooled}]], )
    # ------------------------------------------------------------------------
    # /b
    # ------------------------------------------------------------------------

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Tokens Encode (Shinsplat)": Shinsplat_CLIPTokensEncode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Tokens Encode (Shinsplat)": "Clip Tokens Encode (Shinsplat)"
}
