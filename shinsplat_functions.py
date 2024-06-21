import os
import ast
import json
import comfy

"""
XL
g and l has start and end tokens: 49406 / 49407
but clip l is padded after that with the end token
while clip g is padded, after that, with 0 instead of 49407.
This can have multiple blocks, padded.

SD3
t5xxl has no start token and, like clip g, the end token
is presumed to be 0.
t5xxl is a single token block
g and l are as with the other implementations, multiple blocks of 77 padded

SD
l is the only type and has start and end tokens, 49406 / 49407
the remainder of a block is padded with end tokens. Can contain multiple
blocks.

Cascade
clip g only, start and end tokens with end padded, multiple blocks

The others may not be interesting enough to support, v2, 768/512 blah *shrugs*.

Pixart
Hogs the space without a designator.  T5 only, not the extended implementation that
people generally think it is.  Can contain multiple blocks.  No start token, I
assume the end token is a zero (0) but I don't care just yet, I just finished
goofing with it and didn't find it important enough to remember.
"""
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
def get_sd_tokens():
    tokens = dict()
    # Create forward and reverse lookup
    file_name = "shinsplat_tokens.json"
    script_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_path, file_name)
    f = open(file_path, "r", encoding="UTF-8")
    sdata = f.read()
    f.close()
    # This is the forward lookup, I'll need the reverse.
    tokens['fwd'] = json.loads(sdata)
    tokens['rev'] = dict()
    for key in tokens['fwd']:
        value = tokens['fwd'][key]
        tokens['rev'][value] = key
    return tokens
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
def tensors_to_tokens(tokens, method):

    if method == "t5":
        # ------------------------------------------------------------------------
        # load tokens
        # ------------------------------------------------------------------------
        base_path = comfy.__path__[0]
        tok_f = os.path.join(base_path, "t5_tokenizer", "tokenizer.json")
        tf = open(tok_f, "r", encoding="utf-8")
        content = tf.read()
        tf.close()
        td = json.loads(content)
        r = td['decoder']['replacement']
        tokens_fwd = {}
        tokens_rev = {}
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
            tokens_fwd[t] = { "token": count, "weight": w, }
            # save the "encoded" token as the key
            tokens_rev[count] = { "word": t, "weight": w, }
            count += 1
        # ------------------------------------------------------------------------
        # formatted string tokens output
        # ------------------------------------------------------------------------
        # Now generate the string from the token block, including weights.
        tokens_out = ""
        for block in tokens['t5xxl']:
            # for the index, not really needed but could be helpful later
            # to those that don't "Python" well.
            tp_count = 0
            for tensor_pair in block:
                (t, w) = tensor_pair
                # Start and end do not exist in T5, but I can detect the end
                # token from the zero (0) value.
                if t == 0:
                    break
                # Get the string token associated with this token value.
                # If it's not identified...
                if t not in tokens_rev:
                    token_value = "UNK"
                else:
# T
#                    breakpoint()
# /
                    token_value = tokens_rev[t]['word']
                tokens_out += \
                    '{"word": "' + token_value + '",' + ' "token": ' \
                    + str(t) + ',' + ' "weight": ' + str(w) + '},' \
                    + '"index": ' + str(tp_count) + '},\n'
                tp_count += 1
        return tokens_out

    if method == "sd":
        # ------------------------------------------------------------------------
        # load tokens
        # ------------------------------------------------------------------------
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
        # formatted string tokens output
        # ------------------------------------------------------------------------
        tokens_out = ""
        token_type = ""
        # I only need one set of tokens for this encoder, that can be 'l',
        # I'll first look for 'l', because it will have the proper end token,
        # then 'h', then 'g'.  I figure 'h' probably has an end token since
        # it's alone but I haven't tested that yet.
        if 'l' in tokens:
            token_type = 'l'
        elif 'h' in tokens:
            token_type = 'h'
        elif 'g' in tokens:
            token_type = 'g'
        else:
            print("shinsplat_functions::tensors_to_tokens - no token type found")
        if token_type != "":
            # Each block is a list of tuples, each tuple contains the encoded token
            # and then its weight value (float).
            for block in tokens[token_type]:
                # for the index, not really needed but could be helpful later
                # to those that don't "Python" well.
                tp_count = 0
                for tensor_pair in block:
                    (t, w) = tensor_pair
                    # There is a start (49406) and end (49407) token identifier,
                    # I want everything in between but not those.
                    if t == 49406:
                        continue
                    if t == 49407:
                        break
                    # Get the string token associated with this token value.
                    # If it's an unknown token...
                    if t not in tokens_dict:
                        token_value = "UNK"
                    else:
                        token_value = tokens_dict[t]
                    tokens_out += \
                        '{"word": "' + token_value + '",' + ' "token": ' \
                        + str(t) + ',' + ' "weight": ' + str(w) + '},' \
                        + '"index": ' + str(tp_count) + '},\n'
                    tp_count += 1
        return tokens_out

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
# This "text" is the formatted dictionaries that are created from the custom
# nodes I built. {"word": "", "token": int(), "weight": float(), "index": int(0),},
def tokens_to_tensors(text, method):
    pass


# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
