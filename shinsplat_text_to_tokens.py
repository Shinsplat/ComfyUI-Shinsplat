# Shinsplat Tarterbox
import os
import sys
import json
import folder_paths
from . import shinsplat_functions as sf

help ="""
# before_ / after_ are inputs that will sandwich the
# main text area and is standard text.
# _prompt
# is standard text output, not formatted tokens.
# _tokens
# is a text representation of a list of dictionaries
# representing values of tokens.  Pipe this through
# Clip Tokens Encode.
#
# This is a commented line, you can include it in your
# token definitions to keep notes.
#
# This tool is just a text input that converts your
# words into encoded tokens for the output.  I works
# in conjunction with the shinsplat_clip_tokens_encode
# node, which will deposit raw tokens into the tensors,
# allowing you to apply weight to each token separately
# instead of a split word being weighted all the same.
#
# An explanation of the output ...
#
# The "word" key is not used internally, it's there for
# reference only.
#
# "index" is a unique number and is the place in the
# generated list.  This visual will allow you to manipulate
# the data programmatically, possibly through my Python
# nodes, in case you need to identify a specific token.
# This is not a magical number, you can find this number
# yourself by iterating through the zero (0) indexed list.
#
# All of the below token definitions are correctly
# formatted, though they all look a little different.
{
    "token": 1929,
    "weight": 1.2,
    "word": "dog</w>",
    "index": 0,
},

{ "token": 1929, "weight": 1.2, "index": 1},
{ "token": 2368, "weight": 1.5, "word": "cat</w>", "index": 2},
{   "token": 267,
    "weight": 1.0,
    "word": ",</w>","index": 3
},
{
"token": 267,
"weight": 1.0,
"word": ",</w>",
"index": 4,
},
"""
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_TextToTokens:
    """
    - Shinsplat Tarterbox -

    This tool is for generating tokens for use with "Clip Tokens Encode (Shinsplat)".
    You can use interpolated methods like (blue:1.4) and {random|wildcards}.  Your
    words will be split up into token values along with the weights where you can
    then adjust each weight individually.
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
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP", ),
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                },
            "optional": {
                        "before_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                        "after_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                        },
            }

    RETURN_TYPES = ("STRING",  "STRING", )
    RETURN_NAMES = ("_prompt", "_tokens", )

    FUNCTION = "to_tokens"

    CATEGORY = "advanced/Shinsplat"

    def to_tokens(self, clip, text, before_="", after_=""):

        text = text.split("END")[0]
        before_ = before_.split("END")[0]
        after_ = after_.split("END")[0]
        prompt_local = before_ + " " + text + " " + after_
        tokens = clip.tokenize(prompt_local)
        tokens_out = sf.text_to_tokens(tokens)
        return (text, tokens_out,)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Text To Tokens (Shinsplat)": Shinsplat_TextToTokens
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Text To Tokens (Shinsplat)": "Text To Tokens (Shinsplat)"
}
