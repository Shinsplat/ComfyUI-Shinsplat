# Shinsplat Tarterbox
import os
import sys
import json
import folder_paths

from . import shinsplat_functions as sf

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
                "in1_": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                },
            "optional": {
                        "in2_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                        },
            }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("_out", )

    FUNCTION = "test"

    CATEGORY = "advanced/Shinsplat"

    def test(self, in1_="", in2_=""):

        out_ = "nothing  yet"

        return(out_)


"""
class VAEDecode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "samples": ("LATENT", ), "vae": ("VAE", )}}
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "decode"

    CATEGORY = "latent"

    def decode(self, vae, samples):
        return (vae.decode(samples["samples"]), )
"""









# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Test Node (Shinsplat)": Shinsplat_TestNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Test Node (Shinsplat)": "Test Node (Shinsplat)"
}
