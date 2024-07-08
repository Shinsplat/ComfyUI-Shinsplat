# Shinsplat Tarterbox
import os
import sys
import json
import folder_paths
from . import shinsplat_functions as sf

help ="""
"""
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_TextToTokensSD3:
    """
    - Shinsplat Tarterbox -

    This tool is for generating tokens for use with "Clip Tokens Encode SD3 (Shinsplat)".
    You can use interpolated methods like (blue:1.4) and {random|wildcards}.  Your
    words will be split up into token values along with the weights where you can
    then adjust each weight individually.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":
            {
                "clip": ("CLIP", ),
                "clip_l": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "clip_g": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "t5xxl": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                #"empty_padding": (["none", "empty_prompt"], )
            },
        }

    RETURN_TYPES = ("STRING",   "STRING",   "STRING",   "STRING", )
    RETURN_NAMES = ("clip_l",       "clip_g",       "t5xxl",     "_tokens", )
    FUNCTION = "to_tokens"

    CATEGORY = "advanced/Shinsplat"

    def to_tokens(self, clip, clip_l, clip_g, t5xxl):

        clip_l = clip_l.split("END")[0]
        clip_g = clip_g.split("END")[0]
        t5xxl = t5xxl.split("END")[0]

        tokens_out = ""

        tokens = clip.tokenize(clip_g)
        tokens["l"] = clip.tokenize(clip_l)["l"]
        tokens["t5xxl"] = clip.tokenize(t5xxl)["t5xxl"]
        if len(tokens["l"]) != len(tokens["g"]):
            empty = clip.tokenize("")
            while len(tokens["l"]) < len(tokens["g"]):
                tokens["l"] += empty["l"]
            while len(tokens["l"]) > len(tokens["g"]):
                tokens["g"] += empty["g"]

        if len(tokens):
            tokens_out = sf.text_to_tokens(tokens)

# T
#        print("TEXT TO TOKENS")
#        breakpoint()
# /

        return (clip_l, clip_g, t5xxl, tokens_out,)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Text To Tokens SD3 (Shinsplat)": Shinsplat_TextToTokensSD3
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Text To Tokens SD3 (Shinsplat)": "Text To Tokens SD3 (Shinsplat)"
}
