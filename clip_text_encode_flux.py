import node_helpers

class Shinsplat_CLIPTextEncodeFlux:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "clip": ("CLIP", ),
            "clip_l": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            "t5xxl": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            }}

    RETURN_TYPES = ("CONDITIONING", "STRING",       "STRING",)
    RETURN_NAMES = ("CONDITIONING", "_clip_l",      "_t5xxl",)

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, clip_l, t5xxl, guidance):
        # ST - for the convenient "END" directive.

        clip_l = clip_l.split("END")[0]
        t5xxl = t5xxl.split("END")[0]

        tokens = clip.tokenize(clip_l)
        tokens["t5xxl"] = clip.tokenize(t5xxl)["t5xxl"]

        output = clip.encode_from_tokens(tokens, return_pooled=True, return_dict=True)
        cond = output.pop("cond")
        output["guidance"] = guidance
        return ([[cond, output]], clip_l, t5xxl)

NODE_CLASS_MAPPINGS = {
    "Shinsplat_CLIPTextEncodeFlux": Shinsplat_CLIPTextEncodeFlux,
}
