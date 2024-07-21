# Shinsplat Tarterbox
import os
import json
import comfy # initially to get a relative path
import folder_paths
from . import functions as sf
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
    We seem to have about 128 tokens unaccounted for.  I presume that they didn't
    need to move into another page and just didn't have a need for the remainder in
    this block, and 128 is, as you may know, a convenient block (7Fh is 128d countable).

    "END" - directive
    When this is encountered nothing after it will be conditioned.  This directive
    can be used in clip_l, clip_g and t5xxl..

    "CLIP_INVERT / POOL_INVERT / CLIP_SHIFT / POOL_SHIFT" - directive
    I'm having some fun goofing with the data, these just do a bit of fiddling with
    the return values of tensors.  How I manipulate them probably isn't important
    and certainly doesn't seem to produce any practical results so this is just for
    entertainment.

    """
    def log(self, m):
        if self.debug:
            print(m)

    def __init__(self):
        self.debug = False
        # Make a couple of lookup tables for the tokens.
        base_path = comfy.__path__[0]
        tok_f = os.path.join(base_path, "t5_tokenizer", "tokenizer.json")
        tf = open(tok_f, "r", encoding="utf-8")
        content = tf.read()
        tf.close()
        td = json.loads(content)
        r = td['decoder']['replacement']
        self.tokens_fwd = {}
        self.tokens_rev = {}
        # I want a forward and reverse lookup, I think O.o
        count = 0
        for t,w in td['model']['vocab']:
            if r in t:
                # True then r is 1 character key, I guess I should keep it
                if len(t) == 1:
                    pass
                # or remove the obfikoodle, I've only seen starts, not ends, though
                # there appears to be reference to change this later *shrugs*
                else:
                    t = t.lstrip(r)
            # save the word token as the key into the weight and "encoded" token
            self.tokens_fwd[t] = { "token": count, "weight": w, }
            # save the "encoded" token as the key
            self.tokens_rev[count] = { "token": t, "weight": w, }
            count += 1
        del content
        del td
        # data['model']['vocab'][1782] # token for "dog".

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

    RETURN_TYPES = ("CONDITIONING", "STRING",     "STRING",     "STRING", )
    RETURN_NAMES = ("CONDITIONING", "prompt_out", "tokens_raw", "tokens_out", )

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, clip_l, clip_g, t5xxl, empty_padding, prompt_before="", prompt_after=""):

# T
        #prompt_before = prompt_before.split("END")[0]
        #prompt_after = prompt_after.split("END")[0]

        # ------------------------------------------------------------------------
        print("t5xxl has been temporarily modified to include prompt_before/after : line 130", __file__)
        t5xxl = prompt_before + " " + t5xxl + " " + prompt_after
        # ------------------------------------------------------------------------
# /

        # ------------------------------------------------------------------------
        # END directive
        # ------------------------------------------------------------------------
        # I want to find the 'END' directive and ignore everything after, so I'll
        # change the strings and pass the changed ones along.
        clip_l = clip_l.split("END")[0]
        clip_g = clip_g.split("END")[0]
        t5xxl = t5xxl.split("END")[0]
        # ------------------------------------------------------------------------
        # set variables to indicate tensor manipulation types
        # ------------------------------------------------------------------------
        remove_directives = ['CLIP_INVERT', 'POOL_INVERT', 'CLIP_SHIFT', 'POOL_SHIFT', 'DEBUG']

        self.debug = False
        if 'DEBUG' in t5xxl:
            self.debug = True

        clip_invert = False
        pool_invert = False
        clip_shift = False
        pool_shift = False
        if 'CLIP_INVERT' in t5xxl:
            clip_invert = True
        if 'POOL_INVERT' in t5xxl:
            pool_invert = True
        if 'CLIP_SHIFT' in t5xxl:
            clip_shift = True
        if 'POOL_SHIFT' in t5xxl:
            pool_shift = True
        # Remove the directives from the block and the raw text so that it doesn't
        # get interpreted or travel to the next node.
        for t in remove_directives:
            t5xxl = t5xxl.replace(t, "")
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        # get raw tokens, the data will be appended to the tensors at the end.
        raw_tokens = []
        if "RAW" in t5xxl:
            rt = t5xxl.split("RAW")[-1]
            t5xxl = t5xxl.split("RAW")[0]
            rtt = rt.strip()
            if rtt != "":
                raw_tokens = rtt.split()
                print("raw tokens:", rtt)

        # Do this to the custom input as well, I don't want to pass END directives along
        # I'll test embedding clip splits after this.
        prompt_before = prompt_before.split("END")[0]
        prompt_after = prompt_after.split("END")[0]

        # TODO:  add input filters to split this up, not sure what I'm going to
        # do with prompt/before|after yet.  I suspect that the separated clips
        # will function as mysteriously as the one for the specific XL variation.
        # I could make a simple node that takes the ports and splits them up into
        # segments of ... cl, cg, t5 and the added pb and pa. *shrugs* whatever.
        #
        # Output all of the text, sandwiched, including active directives.
        prompt_out = prompt_before
        prompt_out += clip_l + " CLIP_L " + clip_g + " CLIP_G " + t5xxl + " T5XXL "
        prompt_out += " " + prompt_after

        # Don't pass the directives to other places, it's only for THIS node's use.
        for rd in remove_directives:
           prompt_out = prompt_out.replace(rd, "")

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
        # raw tokens
        if len(raw_tokens):
            for t in raw_tokens:
                if t.isnumeric():
                    tup = (int(t), 1.0)
                    # If there's no text delivered then RAW will be the only thing standing.
                    if 't5xxl'  not in tokens:
                        tokens["t5xxl"] = clip.tokenize("")["t5xxl"]
                    if len(tokens['t5xxl']) == 0:
                       tokens["t5xxl"].append([])

                    tokens['t5xxl'][0].append(tup)

        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)


        # ------------------------------------------------------------------------
        # tokens_out
        # ------------------------------------------------------------------------
        # At this point I have the token values and weights.  I can send it along
        # to the string generator that creates the invididual dictionaries, just
        # like with SD, but note that I'm only converting T5 since I don't see
        # a value in highly manipulating 'l' and 'g' at this point, maybe I'll
        # revisit this later.

        tokens_out = sf.text_to_tokens(tokens)

        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        # I can grab the tokens now and lookup the word portion.
        tokens_raw = ""
        # My testing shows that there's only 1 block, not broken up, despite that
        # it is formed similarly to the other clip doohickeys.
        if len(tokens['t5xxl']):
            t5 = tokens['t5xxl'][0]
            for t,NUL in t5:
                # It's presumed that it's padding if 0 .
                if t == 0:
                    continue
                if t not in self.tokens_rev:
                    pass
                else:
                    word = self.tokens_rev[t]['token']
                    weight = self.tokens_rev[t]['weight']
                    tokens_raw += word + ":" + str(t) + ":" + str(weight) + "\n"
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------

        # ------------------------------------------------------------------------
        # tensor manipulation
        # ------------------------------------------------------------------------
        # Reverse or shift the tensors.  It's just a fun visual to watch, you don't
        # know what you'll get but it hasn't bee completely useless.
        if clip_invert:
            self.log("    -> clip_invert - enabled")
            tb_count = 0
            for tb in cond:
                t_count = 0
                for t in tb:
                    # I don't know the methods in a tensor in order to reverse
                    # so I'll pass it to a list first and put it all back float
                    # by float.
                    floats_list = [a for a in t]
                    floats_list.reverse()
                    f_count = 0
                    for f in floats_list:
                        cond[tb_count][t_count][f_count] = f
                        f_count += 1
                    t_count += 1
                tb_count += 1
        # pool
        if pool_invert:
            self.log("    -> pool_invert - enabled")
            tp_count = 0
            for tp in pooled:
                pooled_list = [a for a in tp]
                pooled_list.reverse()
                f_count = 0
                for f in tp:
                    pooled[tp_count][f_count] = pooled_list[f_count]
                    f_count += 1
                tp_count += 1
        if clip_shift:
            self.log("    -> clip_shift - enabled")
            tb_count = 0
            for tb in cond:
                t_count = 0
                for t in tb:
                    # I have the tensor list for this block in t, because this is
                    # greater than 0 I'll pop tensor_shift floats off the end.
                    float_list = [a for a in t]
                    clip_half = int( len(float_list) / 2 )
                    for i in range(clip_half):
                        float_list.insert(len(float_list) + 1, float_list.pop(0))
                    # put it all back
                    f_count = 0
                    for f in float_list:
                        cond[tb_count][t_count][f_count] = f
                        f_count += 1
                    t_count += 1
                tb_count += 1
        if pool_shift:
            self.log("    -> pool_shift - enabled")
            tp_count = 0
            for tp in pooled:
                float_list = [a for a in tp]
                pool_half =  int( len(float_list) / 2 )
                for i in range(pool_half):
                    float_list.insert(len(float_list) + 1, float_list.pop(0))
                f_count = 0
                for f in tp:
                    pooled[tp_count][f_count] = float_list[f_count]
                    f_count += 1
                tp_count += 1
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------

        return ([[cond, {"pooled_output": pooled}]], prompt_out, tokens_raw, tokens_out)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode T5 (Shinsplat)": Shinsplat_CLIPTextEncodeT5
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode T5 (Shinsplat)": "Clip Text Encode T5 (Shinsplat)"
}
