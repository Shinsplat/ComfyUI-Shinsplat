# Shinsplat Tarterbox
import os
import json
import comfy
import folder_paths
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_CLIPTextEncodeT5:
    """
    - Shinsplat Tarterbox -

    This is not a replacement for the SD3 encoder, it is an experimental alternative
    to examine and modify the weights deep inside the tensors.

    There are no instructions, but ...

    "RAW" - directive
    Everything after this keyword will be understood as a white-space delimited
    sequence of actual encoded token values, delivered in a tensor block without
    interpolation.

    For now this has to be at the end of your prompt, but before the 'END' directive,
    and is for testing only.  Hopefully this has an effect of digging deep into the
    model to find a path that was either refined out of it or just very hard to get to.

    There appear to be a total of 32100, ranging from value 0 to 32099.  Of these
    there are 100 tokens at the end with an identity of "<extra_id_??> and the ?? is
    a 2 digit text number string.  Digging into the model using these numbers, from
    32099 to 32100.  These extras are in descending order...

    <extra_id_99>
    ...
    <extra_id_0>

    Applying tokens higher than 32127 will result in an error, I'm not sure, yet, if
    there can be different ranges at higher values, not tested, but I've tried
    32200 with no luck.

    _recap_
    Tokens: 32100
    Start/End: 0 - 32099
    Extra from 32000 - 32099
    Unexplored: 32100 - ?
    Max: 32127

    Conclusion:
    We seem to have about 128 tokens unaccounted for.  I presume that that they didn't
    need to move into another page and just didn't have a need for the remainder in this
    block, and 128 is, as you may know, a convenient block (7Fh is 128d countable).

    "END" - directive
    When this is encountered nothing after it will be conditioned.  This directive
    can be used in clip_l, clip_g and t5xxl..
    """

    def __init__(self):
        base_path = comfy.__path__[0]
        tok_f = os.path.join(base_path, "t5_tokenizer", "tokenizer.json")
        tf = open(tok_f, "r", encoding="utf-8")
        content = tf.read()
        tf.close()
        td = json.loads(content)
        r = td['decoder']['replacement']
        self.tokens_fwd = {}
        self.tokens_rev = {}
        count = 0
        for t,w in td['model']['vocab']:
            if r in t:
                if len(t) == 1:
                    pass
                else:
                    t = t.lstrip(r)
            self.tokens_fwd[t] = { "token": count, "weight": w, }
            self.tokens_rev[count] = { "token": t, "weight": w, }
            count += 1
        del content
        del td

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

    RETURN_TYPES = ("CONDITIONING", "STRING", "STRING", )
    RETURN_NAMES = ("CONDITIONING", "prompt_out", "tokens_out", )

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, clip_l, clip_g, t5xxl, empty_padding, prompt_before="", prompt_after=""):

        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        clip_l = clip_l.split("END")[0]
        clip_g = clip_g.split("END")[0]
        t5xxl = t5xxl.split("END")[0]

        raw_tokens = []
        if "RAW" in t5xxl:
            rt = t5xxl.split("RAW")[-1]
            t5xxl = t5xxl.split("RAW")[0]
            rtt = rt.strip()
            if rtt != "":
                raw_tokens = rtt.split()
                print("raw tokens:", rtt)

        prompt_before = prompt_before.split("END")[0]
        prompt_after = prompt_after.split("END")[0]
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

        if len(raw_tokens):
            for t in raw_tokens:
                if t.isnumeric():
                    tup = (int(t), 1.0)
                    tokens['t5xxl'][0].append(tup)

        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        tokens_out = ""
        if len(tokens['t5xxl']):
            t5 = tokens['t5xxl'][0]
            for t,NUL in t5:
                # It's presumed that it's padding if 0 .
                if t == 0:
                    continue
                if t not in self.tokens_rev:
                    print("missing token:", str(t))
                else:
                    word = self.tokens_rev[t]['token']
                    weight = self.tokens_rev[t]['weight']
                    tokens_out += word + ":" + str(weight) + "\n"
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        return ([[cond, {"pooled_output": pooled}]], prompt_out, tokens_out)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode T5 (Shinsplat)": Shinsplat_CLIPTextEncodeT5
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode T5 (Shinsplat)": "Clip Text Encode T5 (Shinsplat)"
}
