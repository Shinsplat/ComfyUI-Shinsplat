# Shinsplat Tarterbox
import json
import os

from nodes import MAX_RESOLUTION
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_CLIPTextEncodeSDXL:
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

    I also added the ability to prepend the pony score line, which includes the
    expected BREAK.

    For the SDXL with clip_g/l I allowed for the pony score line to be prepended
    individually for each of these.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "width": ("INT", {"default": 1024.0, "min": 0, "max": MAX_RESOLUTION}),
            "height": ("INT", {"default": 1024.0, "min": 0, "max": MAX_RESOLUTION}),
            "crop_w": ("INT", {"default": 0, "min": 0, "max": MAX_RESOLUTION}),
            "crop_h": ("INT", {"default": 0, "min": 0, "max": MAX_RESOLUTION}),
            "target_width": ("INT", {"default": 1024.0, "min": 0, "max": MAX_RESOLUTION}),
            "target_height": ("INT", {"default": 1024.0, "min": 0, "max": MAX_RESOLUTION}),
            "text_g": ("STRING", {"multiline": True, "dynamicPrompts": True}), "clip": ("CLIP", ),
            "text_l": ("STRING", {"multiline": True, "dynamicPrompts": True}), "clip": ("CLIP", ),
            "pony_g": ("BOOLEAN", {"default": False}),
            "pony_l": ("BOOLEAN", {"default": False}),
            }}

    RETURN_TYPES = ("CONDITIONING", "STRING",       "STRING",       "STRING",    "STRING" )
    RETURN_NAMES = ("CONDITIONING", "tokens_count", "tokens_used",  "prompt_g", "prompt_l" )

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, width, height, crop_w, crop_h, target_width, target_height, text_g, text_l, pony_g, pony_l):

        text_g_raw = text_g
        text_l_raw = text_l

        # Put the pony stuff in if enabled.
        if pony_g == True:
                text_g = "score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, BREAK" + text_g
        if pony_l == True:
                text_l = "score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, BREAK" + text_l

        # Split the text into segments using the "BREAK" word as a delimiter, in caps of course.
        tokens = dict()

        # See if there's an "END" directive first.  It's only useful a single time so take the first one
        # and ignore the rest.
        start_block_g = text_g.split("END")[0]
        start_block_l = text_l.split("END")[0]

        text_blocks_g = start_block_g.split("BREAK")
        for block in text_blocks_g:
            if len(block.strip()) == 0:
                continue
            temp_tokens = clip.tokenize(block)
            if 'g' not in tokens:
                tokens['g'] = []
            for tensor_block in temp_tokens['g']:
                tokens['g'].append(tensor_block)

        # I need to define the 'l' key later so I need this base first specifically for this
        # SDXL encoder.  I'm doing this in case I never hit the 'g'.
        temp_tokens = dict()

        text_blocks_l = start_block_l.split("BREAK")
        for block in text_blocks_l:
            if len(block.strip()) == 0:
                continue

            temp_tokens['l'] = clip.tokenize(block)['l']
            if 'l' not in tokens:
                tokens['l'] = []
            for tensor_block in temp_tokens['l']:
                tokens['l'].append(tensor_block)

        # If I got nothing just perform a simple empty
        temp_tokens = clip.tokenize("")
        if len(tokens) == 0:
            tokens = temp_tokens
        # If any portion of l or g are empty I'll tokenize just that part.
        if 'g' in tokens:
            if len(tokens['g']) == 0:
                tokens['g'] = temp_tokens['g']
            if len(tokens['l']) == 0:
                tokens['l'] = temp_tokens['l']

        # run through the tokens
        tokens_count = ""
        last_token = "Null"

        tokens_count += "clip_g has "
        tokens_count += str(len(tokens['g'])) + " blocks\n"
        block_number = 0
        token_count = 0
        for tokens_g in tokens['g']:
            for token, weight, in tokens_g:
                if token == 49407:
                    break
                else:
                    # Save the last token before the 'stop' in case it's useful in the future.
                    last_token = token
                    token_count += 1

            block_number += 1
            # tokens are always 1 less than iter because I don't count the start token
            token_count -= 1
            tokens_count += "    Block: " + str(block_number) + " has "
            tokens_count += str(token_count) + " tokens\n"
            token_count = 0 # reset for next iter
            tokens_count += "    End Token: " + str(last_token) + "\n"

        last_token = "Null"

        tokens_count += "clip_l has "
        tokens_count += str(len(tokens['l'])) + " blocks\n"
        block_number = 0
        token_count = 0
        for tokens_l in tokens['l']:
            for token, weight, in tokens_l:
                if token == 49407:
                    break
                else:
                    # Save the last token before the 'stop' in case it's useful in the future.
                    last_token = token
                    token_count += 1

            block_number += 1
            # tokens are always 1 less than iter because I don't count the start token
            token_count -= 1
            tokens_count += "    Block: " + str(block_number) + " has "
            tokens_count += str(token_count) + " tokens\n"
            token_count = 0 # reset for next iter
            tokens_count += "    End Token: " + str(last_token) + "\n"

        # Get the actual words that were identified as tokens.
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
        for tokens_g in tokens['g']:
            block_number += 1
            tokens_used += "\n" + "- block_g: " + str(block_number) + " -\n"
            for token, weight, in tokens_g:
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
        block_number = 0
        for tokens_l in tokens['l']:
            block_number += 1
            tokens_used += "\n" + "- block_l: " + str(block_number) + " -\n"
            for token, weight, in tokens_l:
                if token == 49406: # Start token
                    continue
                if token == 49407: # End token
                    tokens_used += "\n"
                    break
                if token not in tokens_dict:
                    tokens_used += "<unk> "
                else:
                    word = tokens_dict[token].replace("</w>", "")
                    tokens_used += word + " "

        # The below code was already part of this base node.  It is responsible for
        # making sure that both g and l clips have the same amount of blocks and
        # will provide empty ones to match them.
        #
        # Despite that the block counts have to match I still exported the correct
        # input data from the prompt, this may be useful.

        if len(tokens["l"]) != len(tokens["g"]):
            empty = clip.tokenize("")
            while len(tokens["l"]) < len(tokens["g"]):
                tokens["l"] += empty["l"]
            while len(tokens["l"]) > len(tokens["g"]):
                tokens["g"] += empty["g"]

        # And finally it's sent on it's way to the fun yard.

        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)

        return ([[cond, {"pooled_output": pooled, "width": width, "height": height, "crop_w": crop_w, "crop_h": crop_h, "target_width": target_width, "target_height": target_height}]], tokens_count, tokens_used, text_g_raw, text_l_raw)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Clip Text Encode SDXL (Shinsplat)": Shinsplat_CLIPTextEncodeSDXL
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Clip Text Encode SDXL (Shinsplat)": "Clip Text Encode SDXL (Shinsplat)"
}
