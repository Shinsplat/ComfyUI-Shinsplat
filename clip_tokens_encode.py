# Shinsplat Tarterbox
import os
import ast
import sys
import json
import traceback
import folder_paths

from . import functions as sf

help ="""
"""

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_CLIPTokensEncode:
    """
    - Shinsplat Tarterbox -

    """
    def __init__(self):
        self.control_ = ""
        self.cond = None
        self.pooled = None
        self.cd = {}
        self.tokens_out = {}
        self.text = ""
        self.before_ = ""
        self.after_ = ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP", ),
                "tokens_": ("STRING", {"multiline": True, "dynamicPrompts": False, "forceInput": True}),
                "empty_padding": (["none", "empty_prompt"], )
                },
            "optional": {
                        "control_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                

                        # I didn't have time to work these in, it doesn't work yet.
                        #"before_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                        #"after_": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                        },
            }

    RETURN_TYPES = ("CONDITIONING", "STRING", )
    RETURN_NAMES = ("CONDITIONING", "_tokens", )

    #OUTPUT_NODE = True

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, tokens_="", empty_padding="none", control_="", before_="", after_=""):

        # kludge / work this out later.. I changed "text" to "tokens_" because it's goofy to have
        # the tokens be sandwiched.
        text = tokens_

        # before_ and after_ are not conditioned to work yet, they do NOT work, so I've disabled
        # them for now, I'm not even sure they're very useful and don't have time to work it out
        # just yet.
        rerun = False
        if text != self.text:
            self.text = text
            rerun = True
        if self.before_ != before_:
            self.before_ = before_
            rerun = True
        if self.after_ != after_:
            self.after_ = after_
            rerun = True
        if self.control_ != control_:
            self.control_ = control_
            rerun = True

        if rerun == True:

            tokens_out = text
            prompt = before_ + " " + text + " " + after_
            if prompt.strip() != "":
                tokens = sf.tokens_to_encoding(prompt)
            else:
                tokens = clip.tokenize("")

            # what clip is this and is something missing?
            tokens_ref = clip.tokenize("")

            # ------------------------------------------------------------------
            # rerun
            # ------------------------------------------------------------------
            if True:
                # I forget which one, g or l, that has to be repeated for the other, I'll just do both
                fill = False
                target = None
                if 'l' in tokens and 'g' not in tokens:
                    target = 'g'
                    source = 'l'
                    fill = True
                elif 'g' in tokens and 'l' not in tokens:
                    target = 'l'
                    source = 'g'
                    fill = True

                if fill:
                    start = sf.check_clip[target]['start']
                    stop = sf.check_clip[target]['stop']
                    min = sf.check_clip[target]['min']
                    max = sf.check_clip[target]['max']
                    pad = sf.check_clip[target]['pad']

                    # This works for XL
                    tokens[target] = tokens[source].copy()

                    # If this exists then I want to send blank blocks for the missing clip so just
                    # overwrite each block with its corresponding start, end and pad.  NOTE: It may
                    # be enough to just scratch the first two elements into compliance, which I will
                    # test .. start/stop . UPDATE: nope, the tokens seem to be read even if the
                    # intention is for them to do nothing.

                    # SD3
                    if 't5xxl' in tokens_ref:
                        # This will be a reference, don't have to put it back.
                        bList = tokens[target]
                        block_count = 0
                        for block in bList:
                            tuple_count = 0
                            for element in block:
                                bList[block_count][tuple_count] = (pad, 1.0)
                                tuple_count += 1
                            # scratch the beginning
                            bList[block_count][0] = (start, 1.0)
                            bList[block_count][1] = (stop, 1.0)
                            block_count += 1

                    # I do this later now, and check if it needs to be blank or filled/padded.
                    #
                    # If this doesn't exist then I only need 1 block for it, whatever is in ref.
                    if False:
                        target = 't5xxl'
                        if target in tokens_ref and target not in tokens:
                            tokens[target] = tokens_ref[target]


            # Part of the above code deals with duplicating 'l' or 'g' to the other if needed.
            # t5xxl is checked to make sure it needs duplication, where, if it's missing,
            # then the clip is presumed to be SD or XL and one has to be cloned into the
            # other, if missing, or that's the ComfyUI method.  What I'm doing now is
            # checking the tokens_ref which will tell me which clip is missing.  It
            # doesn't matter if I create an encoding that isn't compatible, it just won't
            # be read.

            # What's left, whatever is missing I'll fill in with blanks or an empty

            # Gather a list of encodings, remember not to alter an entity that you're
            # iterating over, and a generator will use up more memory.
            encs = []
            for encoding in sf.check_clip:
                if encoding not in tokens:
                    encs.append(encoding)
            for encoding in encs:
                if encoding in tokens_ref:
                    if empty_padding == "none":
                        tokens[encoding] = []
                    else:
                        tokens[encoding] = tokens_ref[encoding]

            # Insertion order
            tokens2 = tokens
            del tokens
            tokens = {}
            for encoding in sf.check_clip:
                if encoding in tokens2 and encoding in tokens_ref:
                    tokens[encoding] = tokens2[encoding]

            self.cond, self.pooled = clip.encode_from_tokens(tokens, return_pooled=True)

            # Now I can pipe some data into the control_ input to change how I want
            # the function to perform.
            process = False
            if control_.strip() != "":
                    cd = sf.string_to_dictionary(control_)
                    if cd:
                        self.cd = cd
                        process = True
                    else:
                        # If there's an error I still want to process their Queue
                        return ([[self.cond, {"pooled_output": self.pooled}]], self.tokens_out)
            if process:
                self.cond, self.pooled = sf.adjust_tensors(cond=self.cond, pooled=self.pooled, args=self.cd)
            else:
                print("skipping sf.adjust_tensors")

            self.tokens_out = str(tokens)
            # ------------------------------------------------------------------
            #
            # ------------------------------------------------------------------

        if 'break' in self.cd:
            if self.cd['break']:
                cond = self.cond # for convenience
                pooled = self.pooled
                breakpoint()

        return ([[self.cond, {"pooled_output": self.pooled}]], self.tokens_out)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Tokens Encode (Shinsplat)": Shinsplat_CLIPTokensEncode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Tokens Encode (Shinsplat)": "Clip Tokens Encode (Shinsplat)"
}
