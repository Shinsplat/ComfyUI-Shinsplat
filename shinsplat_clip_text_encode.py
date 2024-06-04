# Shinsplat Tarterbox
import os
import sys
import json
import folder_paths

debug = False


# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_CLIPTextEncode:
    """
    - Shinsplat Tarterbox -

    This adds some directives to the Text Encode nodes.  We can use BREAK directly
    and it will split up your prompt into different segments.

    There's an END directive that will ignore everything after it, which is a useful
    tool when you want to just go to the top of your prompt and test something simple.

    Since I really needed a token counter I decided to add that to this node so that
    it would at least be somewhat useful.

    I also added a token expander, which the back-end does already and I just grab the
    associated words from the token numbers.  This will display the word tokens that
    where inferred.

    "BREAK" - directive
    I also added the ability to prepend the pony score line, which includes the
    expected BREAK.

    "END" - directive
    When this is encountered nothing after it will be conditioned.

    "prompt" - output
    is a text output that you can deliver to the text input of another node.
    The usefulness of this for me was that I can have the same prompt in mulitple
    segments easily.

    Pony tags will not be included in the output text, prompt.  However, the input
    text "prompt_before" and "prompt_after" will be added to the "prompt".

    For the SDXL with clip_g/l I allowed for the pony score line to be prepended
    individually for each of these.

    These last two are only for the regular encoder, which of course also works for
    SDXL models.

    "prompt_before" - input
    A text input prepended to the existing prompt, but after any pony tags if applicable.

    "prompt_after" - input
    A text input appended to the existing prompt.

    "CLIP_INVERT / POOL_INVERT / CLIP_SHIFT / POOL_SHIFT" - directive
    I'm having some fun goofing with the data, these just do a bit of fiddling with
    the return values of tensors.  How I manipulate them probably isn't important
    and certainly doesn't seem to produce any practical results so this is just for
    entertainment.

    There are two blocks returned, cond seems to be the clip side and pool is something
    else, each with different lengths of tensors it seams.  The clip and pool weights will be
    shifted by half of their length, which is the only value that seems to provide
    a visual that isn't garbage, and the invert method will just flip the array's of each.
    """

    def log(self, m):
        if debug == True:
            print("===========================================")
            print(m)
            print("===========================================")
            return True
        return False
    
    def __init__(self):
        self.trigger = False
        if debug == True:
            def IS_CHANGED(self):
                self.trigger = not self.trigger
                return(self.trigger)
            setattr(self.__class__, 'IS_CHANGED', IS_CHANGED)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "clip": ("CLIP", ),
                "pony": ("BOOLEAN", {"default": False}),
                },
            "optional": {
                        "prompt_before": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                        "prompt_after": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                        },
            }

    RETURN_TYPES = ("CONDITIONING", "STRING",       "STRING",       "STRING", )
    RETURN_NAMES = ("CONDITIONING", "tokens_count", "tokens_used",  "prompt", )

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, text, pony=False, prompt_before="", prompt_after=""):

        text_raw = text

        # This could be 'h' later if using SD 2.1 768 .
        # This will not exist in Cascade.  I'll change this
        # below, if needed, after getting the tokens.
        base_block = 'l'

        # I still get pony before the prompt_before, which his what is typically expected.
        # Also include the raw text output, exposed on "prompt".
        if prompt_before != "":
                text = text + " " + prompt_before
                text_raw = prompt_before + " " + text_raw

        # Put the pony stuff in if they wanted it.
        # Also include the raw text output, exposed on "prompt".
        if pony == True:
                text = "score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, BREAK" + text

        # Append this to everything else.
        if prompt_after != "":
                text = text + " " + prompt_after
                text_raw = text_raw + " " + prompt_after

        tokens = dict()

        # See if there's an "END" directive first.  It's only useful a single time so take the first one
        # and ignore the rest.
        start_block = text.split("END")[0]

        # ------------------------------------------------------------------------
        # tensor manipulation
        # ------------------------------------------------------------------------
        # These items are for goofing with some data, it doesn't appear to produce any significant value
        # except for entertainment.  If any of these keywords can see in the "prompt" output then you
        # typed them in wrong, unless it's a bug of course.
        remove_types = {'CLIP_INVERT', 'POOL_INVERT', 'CLIP_SHIFT', 'POOL_SHIFT'}
        clip_invert = False
        pool_invert = False
        clip_shift = False
        pool_shift = False
        if 'CLIP_INVERT' in start_block:
            clip_invert = True
        if 'POOL_INVERT' in start_block:
            pool_invert = True
        if 'CLIP_SHIFT' in start_block:
            clip_shift = True
        if 'POOL_SHIFT' in start_block:
            pool_shift = True
        # Remove the directives from the block and the raw text so that it doesn't
        # get interpreted or travel to the next node.
        for t in remove_types:
            start_block = start_block.replace(t, "")
            text_raw = text_raw.replace(t, "")
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------

        # Split the text into segments using the "BREAK" word as a delimiter, in caps of course.
        text_blocks = start_block.split("BREAK")

        # Iterate over each block and have the clip encode their types.
        for block in text_blocks:
            # I won't create an entire block for white-space.
            if len(block.strip()) == 0:
                continue
            temp_tokens = clip.tokenize(block)

# New
            # UPDATE: 6/3/2024 - I'll get back to this later, it's supposed to make things
            # easier to maintain.  I'll be iterating over the types instead of asking what
            # they are.  This should partially future proof it.

            # Depending on the tech temp_tokens will contain 1 or more of the following...
            # l, g, h.  Cascade uses 'g' only but it won't complain if I toss it an 'l',
            # it just won't get used.
            if False:
                for base_block in temp_tokens:
                    tokens[base_block] = []
                    for tensor_block in temp_tokens[base_block]:
                        tokens[base_block].append(tensor_block)

# /

            else:

                if "l" not in temp_tokens and 'h' not in temp_tokens:
                    base_block = "g"

                # concatenate each 'l' and 'g' tensor block into the target for return
                #
                # is it XL or SD?
                # 'l' always exists, this node should be compatible with SD and XL.

                # In case they are using SD 2.1, 768 ?  It's contained in 'h' layer
           
                if 'h' in temp_tokens:
                    base_block = 'h'

                if base_block in temp_tokens:
                    if base_block not in tokens:
                        tokens[base_block] = []
                    for tensor_block in temp_tokens[base_block]:
                        tokens[base_block].append(tensor_block)

                # 'g' exists in XL models and Cascade
                if 'g' in temp_tokens:
                    if 'g' not in tokens:
                        tokens['g'] = []
                    for tensor_block in temp_tokens['g']:
                        tokens['g'].append(tensor_block)


        # If I didn't get any good tokens then this will pose a problem,
        # just default to what it would normally do.
        if len(tokens) == 0:
            self.log("no tokens")
            #tokens = clip.tokenize(text)
            tokens = clip.tokenize(start_block)

        # I'll gather the token data so they can use it as a guide to structure their prompt better.
        #
        # Iterate over the blocks and get the count for each of them.
        #
        # I don't need to count the first one because it's always 49406, the special start token, so I'll subtract
        # 1 from the total.  I just need to find the end token, which is 49407.
        #
        # I only have to tell them about one set of blocks because they are mirrored in the simpler clip encoder.

        tokens_count = ""
        last_token = "Null"

        tokens_count += "clip has "
        tokens_count += str(len(tokens[base_block])) + " blocks\n"
        block_number = 0
        token_count = 0
        for tokens_base_block in tokens[base_block]:
            for token, weight, in tokens_base_block:
                if token == 49407:
                    break
                else:
                    # Save the last token before the 'stop' in case it's useful in the future.
                    last_token = token
                    token_count += 1

            block_number += 1
            # tokens are always 1 less than iter because we don't count the start token
            token_count -= 1
            tokens_count += "    Block: " + str(block_number) + " has "
            tokens_count += str(token_count) + " tokens\n"
            token_count = 0 # reset for next iter
            tokens_count += "    End Token: " + str(last_token) + "\n"

        # Get the actual words that were identified as tokens.  I only need to iterate the 'l' here,
        # in the XL version I'll do both 'l' and 'g'.
        #
        # Load the tokens file if it's not already in memory...
        try:
            json_loaded
        except:
            file_name = "shinsplat_tokens.json"
            script_path = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(script_path, file_name)
            f = open(file_path, "r", encoding="UTF-8")
            sdata = f.read()
            f.close()
            # This is the forward lookup, I'll need the reverse.
            tokens_fwd = json.loads(sdata)
            del f
            del sdata
            tokens_dict = {}
            for key in tokens_fwd:
                value = tokens_fwd[key]
                tokens_dict[value] = key
            del tokens_fwd
            json_loaded = True

        # Pull out the token words using the integer.
        tokens_used = ""
        block_number = 0
        for tokens_base_block in tokens[base_block]:
            block_number += 1
            tokens_used += "\n" + "- block: " + str(block_number) + " -\n"
            for token, weight, in tokens_base_block:
                if token == 49406: # Start token
                    continue
                if token == 49407: # End token
                    tokens_used += "\n"
                    break
                if token not in tokens_dict:
                    tokens_used += "<unk> "
                else:
                    word =  tokens_dict[token].replace("</w>", "")
                    tokens_used += word + " "

        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)

        # ------------------------------------------------------------------------
        # tensor manipulation
        # ------------------------------------------------------------------------
        # Reverse or shift the tensors.  It's just a fun visual to watch, you don't
        # know what you'll get but it hasn't bee completely useless.
        if clip_invert:
            self.log("clip_invert")
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
            self.log("pool_invert")
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
            self.log("clip_shift")
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
            self.log("pool_shift")
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

        return ([[cond, {"pooled_output": pooled}]], tokens_count, tokens_used, text_raw)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": Shinsplat_CLIPTextEncode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": "Clip Text Encode (Shinsplat)"
}
