# Shinsplat Tarterbox
import os
import sys
import json
import folder_paths

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_CLIPTextEncodeSD3:
    """
    - Shinsplat Tarterbox -

    "END" - directive
    When this is encountered nothing after it will be conditioned.  This directive
    can be used in clip_l, clip_g and t5xxl..
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP", ),
                "clip_l": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "clip_g": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "t5xxl": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "empty_padding": (["none", "empty_prompt"], )
                },
            "optional": {
                        "prompt_before": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                        "prompt_after": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                        },
            }

    RETURN_TYPES = ("CONDITIONING", "STRING", )
    RETURN_NAMES = ("CONDITIONING", "prompt_out", )

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, clip_l, clip_g, t5xxl, empty_padding, prompt_before="", prompt_after=""):

        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        # I want to find the 'END' directive and ignore everything after, so I'll
        # change the strings and pass the changed ones along.
        clip_l = clip_l.split("END")[0]
        clip_g = clip_g.split("END")[0]
        t5xxl = t5xxl.split("END")[0]

        # TODO:  add input filters to split this up, not sure what I'm going to
        # do with prompt/before|after yet.  I suspect that the separated clips
        # will function as mysteriously as the one for the specific XL variation.
        # I could make a simple node that takes the ports and splits them up into
        # segments of ... cl, cg, t5 and the added pb and pa. *shrugs* whatever.
        #
        # Output all of the text, sandwiched, including active directives.
        prompt_out = prompt_before
        prompt_out += " CLIP_L " + clip_l + " CLIP_G " + clip_g + " T5XXL " + t5xxl
        prompt_out += " " + prompt_after
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        no_padding = empty_padding == "none"
        tokens = clip.tokenize(clip_g)
        if len(clip_g) == 0 and no_padding:
            tokens["g"] = []
        if len(clip_l) == 0 and no_padding:
            tokens["l"] = []
        else:
            tokens["l"] = clip.tokenize(clip_l)["l"]
        if len(t5xxl) == 0 and no_padding:
            tokens["t5xxl"] =  []
        else:
            tokens["t5xxl"] = clip.tokenize(t5xxl)["t5xxl"]
        if len(tokens["l"]) != len(tokens["g"]):
            empty = clip.tokenize("")
            while len(tokens["l"]) < len(tokens["g"]):
                tokens["l"] += empty["l"]
            while len(tokens["l"]) > len(tokens["g"]):
                tokens["g"] += empty["g"]
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)

        return ([[cond, {"pooled_output": pooled}]], prompt_out)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode SD3 (Shinsplat)": Shinsplat_CLIPTextEncodeSD3
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode SD3 (Shinsplat)": "Clip Text Encode SD3 (Shinsplat)"
}
