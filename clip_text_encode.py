# Shinsplat Tarterbox
import json
import os
import sys
import folder_paths

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_CLIPTextEncode:
    """
    - Shinsplat Tarterbox -

    I didn't write this entirely, I took this simple node from the existing ones in
    ComfyUI and I altered it to fit my needs.
    --
    I attempted to implement the a1111 BREAK directive in ComfyUI, and it kind of works.
    It doesn't have the desired effect but it does do some interesting and fun things.

    Since I really needed a token counter I decided to add that to this node so that
    it would at least be somewhat useful.

    I also added a token expander, which the back-end does already and I just grab the
    associated words from the token numbers.  This will display the word tokens that
    where inferred.

    I also added the ability to prepend the pony score line, which includes the
    expected BREAK.

    There's an END directive that, when used in a prompt, will ignore everything after it.
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "clip": ("CLIP", ),
                "pony": ("BOOLEAN", {"default": False}),
                }
            }

    RETURN_TYPES = ("CONDITIONING", "STRING",       "STRING",       "STRING")
    RETURN_NAMES = ("CONDITIONING", "tokens_count", "tokens_used",  "prompt")

    FUNCTION = "encode"

    CATEGORY = "advanced/Shinsplat"

    def encode(self, clip, text, pony):

        text_raw = text

        # This could be 'h' later if using SD 2.1 768 .
        base_block = 'l'

        # Put the pony stuff in if they wanted it.
        if pony == True:
                text = "score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, BREAK" + text

        tokens = dict()

        # See if there's an "END" directive first.  It's only useful a single time so take the first one
        # and ignore the rest.
        start_block = text.split("END")[0]

        # Split the text into segments using the "BREAK" word as a delimiter, in caps of course.
        text_blocks = start_block.split("BREAK")
        # Iterate over each block and have the clip encode their 'l' and 'g'.
        for block in text_blocks:
            # I won't create an entire block for white-space.
            if len(block.strip()) == 0:
                continue
            temp_tokens = clip.tokenize(block)
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
            # 'g' exists in XL models
            if 'g' in temp_tokens:
                if 'g' not in tokens:
                    tokens['g'] = []
                for tensor_block in temp_tokens['g']:
                    tokens['g'].append(tensor_block)

        # If I didn't get any good tokens then this will pose a problem,
        # just default to what it would normally do.
        if len(tokens) == 0:
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
            file_name = "tokens.json"
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
