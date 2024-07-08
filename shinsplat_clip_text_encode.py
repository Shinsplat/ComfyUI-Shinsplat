# Shinsplat Tarterbox
import os
import sys
import json
import folder_paths
from . import shinsplat_functions as sf

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

    DEBUG - directive
    self.debug = True # Releases the print

    WEIGHTS - directive
    self.show_weights = True # Shows the token weights
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
        self.debug = False
        self.show_weights = False
        self.trigger = False

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

    RETURN_TYPES = ("CONDITIONING", "STRING",       "STRING",       "STRING",       "STRING",)
    RETURN_NAMES = ("CONDITIONING", "tokens_count", "tokens_used",  "tokens_out",   "prompt_out",)

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, text, pony=False, prompt_before="", prompt_after="",):

        # NOTE: I'm going to need 'l' and possibly 'g' for t5, and this is NOT
        # an SDXL specific encoder so I should be able to duplicate one into
        # the other without a problem.  Somewhere below will be the code to do
        # this.


        # ------------------------------------------------------------------------
        # load tokens
        # ------------------------------------------------------------------------
        # This is done in shinsplat_functions but I use it here as well, to tell
        # how many blocks there are and what was used.  This is NOT redundant
        # but I could do better.
        file_name = "shinsplat_tokens.json"
        script_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(script_path, file_name)
        f = open(file_path, "r", encoding="UTF-8")
        sdata = f.read()
        f.close()
        # This is the forward lookup, I'll need the reverse.
        tokens_forward = json.loads(sdata)
        del f
        del sdata
        tokens_dict = {}
        for key in tokens_forward:
            value = tokens_forward[key]
            tokens_dict[value] = key
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------

        # I need to respect the END directive in all inputs separately.
        prompt_out = text.split("END")[0]
        prompt_before = prompt_before.split("END")[0]
        prompt_after = prompt_after.split("END")[0]

        # This could be 'h' later if using SD 2.1 768 .
        # This will not exist in Cascade.  I'll change this
        # below, if needed, after getting the tokens.
        base_block = 'l'

        # I still get pony before the prompt_before, which his what is typically expected.
        # Also include the raw text output, exposed on "prompt".
        if prompt_before != "":
                #text = text + " " + prompt_before
                text = prompt_before + " " + " " + text
                # nope, don't pass inputs since they can be noodled if needed
                #prompt_out = prompt_before + " " + prompt_out

        # Put the pony stuff in if they wanted it.
        # Also include the raw text output, exposed on "prompt".
        if pony == True:
                text = "score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, BREAK" + text

        # Append this to everything else.
        if prompt_after != "":
                text = text + " " + prompt_after
                # nope, SA
                #prompt_out = prompt_out + " " + prompt_after

        tokens = dict()

        # See if there's an "END" directive first.  It's only useful a single time so take the first one
        # and ignore the rest.
        start_block = text.split("END")[0]

        # ------------------------------------------------------------------------
        # debug
        # ------------------------------------------------------------------------
        if 'DEBUG' in start_block:
            print("got DEBUG")
            self.debug = True
        if 'WEIGHTS' in start_block:
            print("got WEIGHTS")
            self.show_weights = True
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        # generic
        # ------------------------------------------------------------------------
        # used later in order to remove the directives so that they are not
        # evaluated or pushed out through the prompt.
        remove_directives = {
            'CLIP_INVERT', 'POOL_INVERT', 'CLIP_SHIFT', 'POOL_SHIFT',
            'DEBUG', 'WEIGHTS', 'STRING_TOKENS', 'NUMBER_TOKENS', 'CLEAN'}

        if self.debug == True:
            def IS_CHANGED(self):
                self.trigger = not self.trigger
                return(self.trigger)
            setattr(self.__class__, 'IS_CHANGED', IS_CHANGED)
        else:
            if hasattr(self.__class__, 'IS_CHANGED'):
                delattr(self.__class__, 'IS_CHANGED')
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        # tensor manipulation
        # ------------------------------------------------------------------------
        # These items are for goofing with some data, it doesn't appear to produce any significant value
        # except for entertainment.  If any of these keywords can see in the "prompt" output then you
        # typed them in wrong, unless it's a bug of course.
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

        # Only 1 of these will be utilized, and that will be the first one in this test, in case both
        # directives are included in the prompt.
        #
        # This one allows for raw string tokens instead of words.
        tokens_input = ""
        if 'STRING_TOKENS' in start_block:
            tokens_input = 'STRING'
        # This one allows for raw integer tokens instead of words.
        if 'NUMBER_TOKENS' in start_block:
            tokens_input = 'NUMBER'

        # Remove the directives from the block and the raw text so that it doesn't
        # get interpreted or travel to the next node.
        for t in remove_directives:
            start_block = start_block.replace(t, "")
            prompt_out = prompt_out.replace(t, "")
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------

        # Split the text into segments using the "BREAK" word as a delimiter, in caps of course.
        text_blocks = start_block.split("BREAK")

        # There are no blocks in t5, it's all one segment.
        t5xxl_block = start_block.replace("BREAK", "")

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



        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        # Add this regardless, for the updated SD3, adding a block shouldn't cause an issue.
        try:
            tokens['t5xxl'] = clip.tokenize(t5xxl_block)["t5xxl"]
        except:
            pass

        # ------------------------------------------------------------------------
        # raw tokens parsing
        # ------------------------------------------------------------------------
        # This is not related to "raw tokens output".
        #
        # Rather than adjust code that already works, and possibly breaking it with
        # additional code, I chose a less efficient method to add, or alter, the
        # previous method if conditions were just so.
        #
        # At this point I have tokens properly organized but if I'm processing
        # raw tokens then I'll trash all of that and rebuild it.
        #
        # If tokens_input is not an empty string then I need an empty token container
        # for the clip type.

# working on it !

        if tokens_input != "":
            self.log("raw tokens input:" + tokens_input)
            # Iterate over each block and have the clip encode their types.  These
            # have already been broken up with the BREAK directive but in this process
            # I'll have to actually count the tokens and create additional blocks,
            # within a block, if it runs over.  We get 75 tokens and then I add the
            # start and stop values.  To easily get the start and stop values of a
            # token type I can issue an empty string to the tokenizer and it will
            # return a block of 77 per type, of which the first two elements in each
            # block (list) will be start and stop respectively.
            start_end = clip.tokenize("")
            end_tokens = {}
            for t in start_end:
                end_tokens[t] = {"start": 0, "stop": 0,}
                end_tokens[t]['start'] =  start_end[t][0][0][0]
                end_tokens[t]['stop'] =  start_end[t][0][0][1]
            # Now I have start and stop tokens for this model type.  I'll free up
            # the list
            del start_end
            for block in text_blocks:
                # I won't create an entire block for white-space.
                if len(block.strip()) == 0:
                    continue
                # For each of these blocks I have to observe the request for BREAK, but
                # also have to make sure that each block fits into a tensor block, which
                # is 77 tokens, two of those are end tokens so are not evaluated.  That
                # means that I have to make sure I have 75 tokens or less per segment
                # that I generate.  In order to achieve that I'll first remove all words
                # that don't exist in the vocab, evaluate what's left, and generate the
                # data needed.
                split_words = block.split()
                good_words = []

                print("===========================================")
                print("split_words:\n", split_words)
                print("===========================================")


#                temp_tokens = clip.tokenize("")

# ########
        # ------------------------------------------------------------------------
        #
        # ------------------------------------------------------------------------
        # If I didn't get any good tokens then this will pose a problem,
        # just default to what it would normally do.

        # I might have t5 tokens only, so this won't work these days but I'll write
        # some additional code before, before the process ends, to fill 'l' and 'g'
        # with blanks.
        if len(tokens) == 0:
            self.log("no tokens")
            #tokens = clip.tokenize(text)
            tokens = clip.tokenize(start_block)

        # I'll only run into an issue where I need this is when there's nothing
        # to deliver from the text input, so in that case I'll just write blank.
        tok = clip.tokenize("")
        if 'l'  not in tokens:
            if 'l' in tok:
                tokens['l'] = tok['l']
        if 'g' not in tokens:
            if 'g' in tok:
                tokens['g'] = tok['g']

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
        if base_block in tokens:
            tokens_count += str(len(tokens[base_block])) + " blocks\n"
        else:
            tokens_count += " 0 blocks\n"
        block_number = 0
        token_count = 0

        # I don't want to manipulate data that isn't there.
        if base_block in tokens:
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

        # debug
        self.log("weights:\n", tokens=tokens)

        # ------------------------------------------------------------------------
        # tensor manipulation
        # ------------------------------------------------------------------------
        # Reverse or shift the tensors.  It's just a fun visual to watch, you don't
        # know what you'll get but it hasn't bee completely useless.
        if clip_invert:
            self.log("clip_invert - enabled")
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
            self.log("pool_invert - enabled")
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
            self.log("clip_shift - enabled")
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
            self.log("pool_shift - enabled")
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

        tokens_out = sf.text_to_tokens(tokens)
# T
#        breakpoint()
# /

        return ([[cond, {"pooled_output": pooled}]], tokens_count, tokens_used, tokens_out, prompt_out)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": Shinsplat_CLIPTextEncode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode (Shinsplat)": "Clip Text Encode (Shinsplat)"
}
