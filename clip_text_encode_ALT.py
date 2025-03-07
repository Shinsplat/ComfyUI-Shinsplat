# Shinsplat Tarterbox

#from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_CLIPTextEncodeALT:
    """
    - Shinsplat Tarterbox -

    Clip_L is enabled by default, allowing the expected text to be duplicated cross
    to t5 as well.  However, my experience shows that clip_l can introduce artifacts
    and hallucinations so I personally choose not to use it so I created this option
    to turn it off.

    There's an END directive that will ignore everything after it, which is a useful
    tool when you want to just go to the top of your prompt and test something simple.

    "END" - directive
    When this is encountered nothing after it will be conditioned.

    "prompt_before" - input
    A text input prepended to the existing prompt.

    "prompt_after" - input
    A text input appended to the existing prompt.

    "_prompt_out", output node, contains the text inside the encoder block only, not before/after,
    so that you can use it in other areas without having to retype that section elsewhere.

    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True, "tooltip": "The text to be encoded."}),
                "clip": ("CLIP", {"tooltip": "The CLIP model used for encoding the text."}),
                "clip_l": ("BOOLEAN", {"default": True}),
                #"clip_zero": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                        "prompt_before": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                        "prompt_after": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            },
        }
    RETURN_TYPES = ("CONDITIONING", "STRING",)
    RETURN_NAMES = ("CONDITIONING", "_prompt_out",)

    OUTPUT_TOOLTIPS = ("A conditioning containing the embedded text used to guide the diffusion model with directives.",)
    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"
    DESCRIPTION = "Encodes a text prompt using a CLIP model into an embedding that can be used to guide the diffusion model towards generating specific images."

    #def encode(self, clip, text, clip_l=True, clip_zero=True, prompt_before="", prompt_after="",):
    def encode(self, clip, text, clip_l=True, prompt_before="", prompt_after="",):
        if clip is None:
            raise RuntimeError("ERROR: clip input is invalid: None\n\nIf the clip is from a checkpoint loader node your checkpoint does not contain a valid clip or text encoder model.")

        # B
        text = text.split("END")[0]
        prompt_out = text
        prompt_before = prompt_before.split("END")[0]
        prompt_after = prompt_after.split("END")[0]
        if prompt_before != "":
                text = prompt_before + " " + " " + text
        if prompt_after != "":
                text = text + " " + prompt_after
        # /B

        tokens = clip.tokenize(text)

        # B
        if not clip_l:
            if 'l' in tokens:
                tokens["l"] = clip.tokenize("")['l']
        # /B

        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)

        return ([[cond, {"pooled_output": pooled}]], prompt_out)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode ALT (Shinsplat)": Shinsplat_CLIPTextEncodeALT
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode ALT (Shinsplat)": "Clip Text Encode ALT (Shinsplat)"
}
