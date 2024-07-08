import os
import ast
import json
import time
import comfy
import torch
import numpy as np
import operator
import traceback
"""
functions
"""

python_warning = """

-- WARNING! --

Python (Shinsplat) / Python - More Inputs (Shinsplat)

READ THIS!

This node set is disabled by default so that it does not automatically
run while executing an unknown work-flow.

It's important to understand that, if you did not write the code
contained within this node, you could be in danger of being infected
with MALWARE by enabling this node!  This node, its very existence,
is not in, and of itself, dangerous, but the code contained within
its text area could be harmful to your computer and personal data.

If you know what you're doing, if you wrote the code yourself, if you
know what the code does, if you've taken the time to examine the code
or maybe you just don't care and feel secure, then issue another Queue,
this message will NOT be redisplayed!

If you need to programmatically enable this node on a headless server,
without a first run interruption, you'll want to either alter the code
or write a file to its directory with the name
    "shinsplat_python_warning.done".

"""
python_warning_file = "shinsplat_python_warning.done"

if True:
    # The insertion order may be important.
    check_clip = {
        "g": {
            "clip": "sd",
            "start": 49406,
            "stop": 49407,
            "pad": 0,
            "max": 77,
            "min": 77,
        },
        "l": {
            "clip": "sd",
            "start": 49406,
            "stop": 49407,
            "pad": 49407,
            "max": 77,
            "min": 77,
            },
        "t5xxl": {
            "clip": "t5xxl",
            "start": 3,
            "stop": 1,
            "pad": 0,
            "max": 0,
            "min": 77,
            },
        }
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class ProcessOrder:
    order =  "cond_lerp, cond_lerp_tokens, cond_expand, cond_weight, cond_scale, cond_invert"
class Weight:
    methods = "+0.0, *1.0, /1, -0.0"
    operators = {
        "+": operator.add,
        "-": operator.sub,
        "/": operator.truediv, # weird monkeys
        "*": operator.mul,
    }
# --------------------------------------------------------------------------------
# convert methods
# --------------------------------------------------------------------------------
def convert_methods(methods):
    allowed = {"+", "-", "*", "/"}
    method_list = sep_to_list(methods, ",")
    new_methods = {}
    for method in method_list:
        if len(method) > 1:
            operator = method[0]
            if operator not in allowed:
                print("sf::convert_methods:disallowed operator:", operator)
                continue
            operand = method[1:]
            if operand.count(".") > 1:
                print("sf::convert_methods:repeated decimal:", operand)
                continue
            if operand.replace(".", "").isnumeric():
                new_methods[operator] = float(operand)
    return new_methods
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
# Escape the escape first or end up escaping your corrective escapes O.o
def escape(t):
    t = t.replace('\\', "\\\\")
    t = t.replace("\'", "\\\'")
    t = t.replace('\"', '\\\"')
    return t
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
# return a list of strings from a string where fields are separated by (sep)
# and common white-space
def sep_to_list(txt, sep):
    list_of_strings = "".join(txt.split()).lstrip(sep).rstrip(sep).split(sep)
    return_list = []
    for i in list_of_strings:
        # not empty then append, could have gotten ",,,,,".
        if i:
            return_list.append(i)
    return return_list
# --------------------------------------------------------------------------------
# Text to Dictionary
# --------------------------------------------------------------------------------
# Either a Python dictionary or a JSON structure in string format.
def string_to_dictionary(t):
    try:
        do = json.loads(t)
        return do
    except:
        try:
            do = ast.literal_eval(t)
            return do
        except:
            print("sf::string_to_dictionary:FAILED")
    return False
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
# Return factor percentage of base.
def percent(base=0, factor=0):
    y = base
    if base:
        x = factor / base
        y = base*x #+base
    return y
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
# I don't know what this does, I don't think I use it anymore?  Maybe I do :/
def get_sd_tokens():
    tokens = dict()
    # Create forward and reverse lookup
    file_name = "shinsplat_tokens.json"
    script_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_path, file_name)

# Original
    f = open(file_path, "r", encoding="UTF-8")
    sdata = f.read()
    f.close()
    tokens['fwd'] = json.loads(sdata)
# /

# Test
#    f = open(file_path, encoding="utf8")
#    sdata = json.load(f)
#    f.close()
    # This is the forward lookup, I'll need the reverse.
#    tokens['fwd'] = json.loads(sdata)[0]
# /


    tokens['rev'] = dict()
    for key in tokens['fwd']:
        value = tokens['fwd'][key]
        tokens['rev'][value] = key
    return tokens
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
def text_to_tokens(tokens):

    vocab = {}
    vocab['t5xxl'] = {}
    vocab['t5xxl']['fwd'] = {}
    vocab['t5xxl']['rev'] = {}
    vocab['sd'] = {}
    vocab['sd']['fwd'] = {}
    vocab['sd']['rev'] = {}

    process = False
    for c in check_clip:
        if c in tokens:
            process = True
            break
    if process == False:
        print("sf::text_to_tokens - nothing to process")
        return ""

    # To make this simpler I'll record all known tokens which is
    # contained in two different files.

    # ------------------------------------------------------------------------
    # load T5 tokens
    # ------------------------------------------------------------------------
    base_path = comfy.__path__[0]
    tok_f = os.path.join(base_path, "t5_tokenizer", "tokenizer.json")

# Original
#    tf = open(tok_f, "r", encoding="utf-8")
#    content = tf.read()
#    tf.close()
#    td = json.loads(content)
# /

# Test
    tf = open(tok_f, encoding="utf8")
    content = json.load(tf)
    this_type = str(type(content))
#    print("=========================")
#    print("content type:", this_type)
#    print("=========================")
    tf.close()
    #td = json.loads(content)[0]
    td = content
# /



    r = td['decoder']['replacement']
    vocab['t5xxl']['fwd'] = {}
    vocab['t5xxl']['rev'] = {}
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
        # UPDATE: I don't need the weight here, or whatever it is.
        #
        # save the word token as the key into the weight and "encoded" token
        if False:
            vocab['t5xxl']['fwd'][t] = { "token": count, "weight": w, }
            # save the "encoded" token as the key
            vocab['t5xxl']['rev'][count] = { "word": t, "weight": w, }

        vocab['t5xxl']['fwd'][t] = count
        vocab['t5xxl']['rev'][count] = t

        count += 1
    # ------------------------------------------------------------------------
    # load SD tokens
    # ------------------------------------------------------------------------
    file_name = "shinsplat_tokens.json"
    script_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_path, file_name)

# Original
#    f = open(file_path, "r", encoding="UTF-8")
#    sdata = f.read()
#    f.close()
    # This is the forward lookup, I'll need the reverse.
#    data = json.loads(sdata)
# /

# Test
    f = open(file_path, encoding="utf8")
    sdata = json.load(f)
    # This is the forward lookup, I'll need the reverse.
    #data = json.loads(sdata)
    data = sdata
# /


    del f
    del sdata
    for word in data:
        value = data[word]
        vocab['sd']['fwd'][word] = value 
        vocab['sd']['rev'][value] = word

    # ------------------------------------------------------------------------
    # stringify values
    # ------------------------------------------------------------------------
    # this is the easy part, just convert token values to dictionaries with
    # some extra data.

    # I already checked to make sure that at least one clip type is supported.
    tokens_out = ""
    #tp_count = 0
    for encoding in tokens:
        if encoding not in check_clip:
            continue
        # The clip type will point to the dictionary key that I need to use.
        # if it's 'sd' then there's only one set of keys for g, l and h, which
        # all point to the key 'sd'.  The only other option, at the time
        # of this writing (6/21/2024)), is t5xxl.  Regardless which one it is
        # the structure is all the same, though xxl will have a single encoded
        # block, not less than 77 in length.
        clip_type = check_clip[encoding]['clip']

        # Now iter the blocks
        start_token = check_clip[encoding]['start']
        stop_token = check_clip[encoding]['stop']

        tp_count = 0
        for block in tokens[encoding]:
            # for the index, not really needed but could be helpful later
            # to those that don't usually Python.
            for tensor_pair in block:
                (t, w) = tensor_pair

# T
# What am I doing here?
                # Check for start token and ignore it, and always ignore it even if
                # it matches if start_token is 0 .
                if True:
# /
                    if t == start_token and start_token:
                        continue
                    # the end token means we're done
                    if t == stop_token:
                        break

                # Get the string token associated with this token value,
                # if it doesn't exist I should make a stink about it and
                # post to the console but also ignore it.
                if t not in vocab[clip_type]['rev']:
                    print("token doesn't exist:", str(t))
                    continue
                else:
                    token_word = vocab[clip_type]['rev'][t]

     


                # I get these raw in the container, I need to re-convert them.
                token_word = escape(token_word)

                tokens_out += \
                    '{"index": ' + str(tp_count) + ', ' + '"word": "' + token_word + '",' + ' "token": ' \
                    + str(t) + ',' + ' "weight": ' + str(w) + ', ' \
                    + '"clip": "' + encoding + '",' + '},\n'
                tp_count += 1

    return tokens_out
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
def tokens_to_encoding(text):

    try:
        td = ast.literal_eval(f'[{text}]')
    except Exception as e:
        txt = traceback.format_exc()
        raise RuntimeError(txt)
        return False

    # I should check to see if any of the offered clips are compatible.
    for d in td:
        if 'clip' not in d:
            print("sf::tokens_to_tensors - incompatible data structure")
            return False
        if d['clip'] in check_clip:
            good = True
            break
    if good == False:
        print("sf::tokens_to_tensors - no recognizable encoding")
        return Fase

    # I'll organize the encodings first then split them up as needed.
    # For this first pass a keyed list of a single block is recorded for
    # easier reading and maintaining.
    cans = {}
    for d in td:
        encoding = d['clip']
        if encoding not in cans:
            cans[encoding] = []
        token = d['token']
        weight = d['weight']
        cans[encoding].append( (token, weight) )

    # This could change [] if it's Pixart-Sigma
    tokens = {}
    for encoding in cans:

        start = check_clip[encoding]['start']
        stop = check_clip[encoding]['stop']
        min = check_clip[encoding]['min']
        max = check_clip[encoding]['max']
        pad = check_clip[encoding]['pad']

        tokens[encoding] = []

        # This will hold a single block of encoded tokens with their weights.
        # If it's xxl then there's only ever 1 block.
        block = []

        block.append( (start, 1.0) )
        # Get the list for this encoding type and split it up if needed.
        pairs = cans[encoding]
        # If there's no length then add the end tokens and move on.
        if len(pairs) == 0:
            block.append( (stop, 1.0) )
            total = min - len(block)
            block.extend ( (pad, 1.0) for _ in range(total) )
            continue

        # By this time I know there's at least 1 token to process.  I have the
        # start token in "block" already, if it wasn't xxl.
        for (t, w) in pairs:
            # Presuming this is not the first pass check to see if it needs to
            # be capped.

            # UPDATE: t5xxl does have an end token, it's 1.  So I have to check for that.
            # if it required a start block then 75, if not then 77 without book ends O.o

            # This works because xxl max is 0 so it will never equal, I'll add the end token
            # on fall through.
            if len(block) + 1 == max:
                block.append( (stop, 1.0) )
                tokens[encoding].append(block)
                block = []
                block.append( (start, 1.0) )

            # UPDATE: xxl does have a start and end token, the start is 3 and the end is 1 - 6/23/2024
            # This works because the block length starts at 1 and max for xxl is 0, I'll add the end
            # token on fall through.
            else:
                if len(block) == max:
                    block = []
            # If I fell through then the block isn't full enough yet.
            block.append( (t, w) )

        # On fall through the last block was conditioned but not deposited yet,
        # since the token count didn't reach max, if needed.

        # this one takes care of anything NOT xxl, maybe.. until an update to something O.o
        if len(block) + 1 <= max:
            block.append( (stop, 1.0) )
        # This is good enough for xxl for now.
        else:
            block.append( (stop, 1.0) )
        # padding
        total = min - len(block)
        block.extend ( (pad, 1.0) for _ in range(total) )
        tokens[encoding].append(block)
    # By this point I have all tokens in the list where they belong.  The last
    # thing to do is make sure that 'g' and 'l' encodings have the same number
    # of blocks.  If either one is larger than the other then the "other" will
    # have to be padded with its corresponding end token and pad.  I don't recall
    # if this is required for 'h' or anything else, I'll burn that bridge when I
    # get to it I guess.
    if 'l' in tokens and 'g' in tokens:
        l = len(tokens['l'])
        g = len(tokens['g'])
        if l == g:
            pass
        else:
            if g > l:
                encoding = "l"
            elif l > g:
                encoding = "g"
            start = check_clip[encoding]['start']
            stop = check_clip[encoding]['stop']
            min = check_clip[encoding]['min']
            max = check_clip[encoding]['max']
            pad = check_clip[encoding]['pad']
            block = [(start, 1.0), (stop, 1.0)]
            total = min - len(block)
            block.extend ( (pad, 1.0) for _ in range(total) )
            remaining = abs(l-g)
            for i in range(remaining):
                tokens[encoding].append(block)

    return tokens
# --------------------------------------------------------------------------------
# adjust tensors
# --------------------------------------------------------------------------------
# Adjust the tensors directly.
def adjust_tensors(cond=[], pooled=[], args=dict()):

    # The logical order of execution may need to start with lerp, then expand,
    # then the others don't matter so much.

    # ----------------------------------------------------------------------------
    # expand
    # ----------------------------------------------------------------------------
    def cond_expand(cond):

        if args['cond_expand']:
            print("sf::cond_expand:enabled")

            # Everything should be separate.  Here I expand the tensor blocks by the
            # amount indicated, multiplying the size by ['cond_expand'].
            repeats = args['cond_expand_amount']
            if repeats >= args['expand_threshold']:
                txt = 'tensor size exceeds warning threshold in "cond_expand_amount": ' + str(args['cond_expand_amount'])
                print(txt)
                raise Exception(txt)
                return None

            # This should happen very fast but then I have to see if filling is needed.
            cond = cond.repeat(1, repeats+1, 1)
            cond_new_size = len(cond[0])

            matrix_block = cond.numpy().copy()

            bitmap = [int(d) for d in str(args['cond_expand_map'])]
            bitmap.reverse() # I'll pop so I need to reverse it
            default = args['cond_expand_default']

            # Overwrite a block
            for root in range(len(matrix_block)): # This should be a 1, so far
                for token_row in range(0, len(matrix_block[root]), data['cond_old_size']):

                    process = False

                    # see if the bitmap has leftovers
                    if len(bitmap):
                        if bitmap.pop():
                            process = True
                    # or maybe the default is to process (1) ?
                    elif default:
                            process = True
                    if process:
                        for token_block in range(token_row, data['cond_old_size']+token_row):
                            for tensor_flt in range(len(matrix_block[root][token_block])):
                                matrix_block[root][token_block][tensor_flt] = 0.0

            cond = torch.tensor(matrix_block)

        return cond
    # ----------------------------------------------------------------------------
    # weights
    # ----------------------------------------------------------------------------
    # I put back the ability to divide
    def cond_weight(cond):
        if args['cond_weight']:
            print("sf::cond_weight:enabled")

            bitmap = [int(d) for d in str(args['cond_weight_map'])]
            bitmap.reverse() # I'll pop so I need to reverse it
            default = args['cond_weight_default']

            matrix_block = cond.numpy().copy()

            for root in range(len(matrix_block)):

                for token_matrix in range(len(matrix_block[root])):

                    # see if the bitmap has left overs
                    if len(bitmap):
                        if not bitmap.pop():
                            continue
                    # if I ran out of leftovers what's the default?
                    else:
                        if not default:
                            break

                    for flt in range(len(matrix_block[root][token_matrix])):
                        f_value = matrix_block[root][token_matrix][flt]
                        f_result = f_value
                        for o in data['methods']:
                            m_value = data['methods'][o]
                            f_result = Weight.operators[o](f_result, m_value)
                        matrix_block[root][token_matrix][flt] = f_result

            cond = torch.tensor(matrix_block)

        return cond
    # ----------------------------------------------------------------------------
    # scale %
    # ----------------------------------------------------------------------------
    def cond_scale(cond):
        if args['cond_scale']:
            print("sf::cond_scale:enabled")

            bitmap = [int(d) for d in str(args['cond_scale_map'])]
            bitmap.reverse() # I'll pop so I need to reverse it
            default = args['cond_scale_default']
            factor = args['cond_scale_factor']

            matrix_block = cond.numpy()

            for root in range(len(matrix_block)):

                for token_matrix in range(len(matrix_block[root])):

                    # see if the bitmap has left overs
                    if len(bitmap):
                        if not bitmap.pop():
                            continue
                    # if I ran out of leftovers what's the default?
                    else:
                        if not default:
                            break

                    for flt in range(len(matrix_block[root][token_matrix])):
                        v = matrix_block[root][token_matrix][flt]

                        vf = percent(base=v, factor=factor)
                        vs = v + vf
                        matrix_block[root][token_matrix][flt] = vs

            cond = torch.tensor(matrix_block)

        return cond
    # ----------------------------------------------------------------------------
    # invert
    # ----------------------------------------------------------------------------
    def cond_invert(cond):
        if args['cond_invert']:
            print("sf::cond_invert:enabled")

            matrix_block = cond.numpy().copy()
            bitmap = [int(d) for d in str(args['cond_invert_map'])]
            bitmap.reverse() # I'll pop so I need to reverse it
            default = args['cond_invert_default']

            for root in range(len(matrix_block)):

                for token_block in range(len(matrix_block[root])):

                    # see if the bitmap has left overs
                    if len(bitmap):
                        if not bitmap.pop():
                            continue
                    # if I ran out of leftovers what's the default?
                    else:
                        if not default:
                            break
                    matrix_block[root][token_block] = matrix_block[root][token_block][::-1] # reverse
            cond = torch.tensor(matrix_block)
        return cond
    # ----------------------------------------------------------------------------
    # lerp
    # ----------------------------------------------------------------------------
    def cond_lerp(cond):
        if args['cond_lerp']:
            print("sf::cond_lerp:enabled")

            bitmap = [int(d) for d in str(args['cond_lerp_map'])]
            bitmap.reverse() # I'll pop so I need to reverse it
            default = args['cond_lerp_default']
            factor = args['cond_lerp_factor']
            matrix_block = cond.numpy()
            #matrix_lerp = np.array()
            matrix_lerp = []

            ceiling = len(matrix_block[0])
            for row in range(ceiling):
                npl_0 = matrix_block[0][row]
                matrix_lerp.append(npl_0.tolist())
                if len(bitmap):
                    if not bitmap.pop():
                        continue
                else:
                    if not default:
                        continue
                if row != ceiling-1:
                    npl_1 = matrix_block[0][row+1]
                    lerp = npl_0 + (npl_1 - npl_0) * factor
                    matrix_lerp.append(lerp.tolist())

            # This one needs to be re-tensored, there's more blocks interweaved.
            cond = torch.tensor([matrix_lerp])

            # After a lerp the data has doubled, almost, - 1.  I have to record
            # this as the new block size or the other functions will not have a
            # correct alignment.
            data['cond_old_size'] = len(cond[0])

        return cond

    # ----------------------------------------------------------------------------
    # lerp_tokens
    # ----------------------------------------------------------------------------
    # This is a test to lerp tensor floats instead of traversing the entire block.  Just
    # like the "lerp" function this will duplicate the tensors, and subsequently the
    # rows, since I'll have left overs to move into a new block, if applicable.
    #
    # XL has 77 tokens token rows per block, meaning the number of rows are divisible
    # by 77.  They are 2048 tensors per token.
    #
    # SD3 is a minimum of 77, at 4096 tensors per token, but this grows by row instead
    # of a 77 block, so NOT divisible by 77.  Each of these have to be manipulated
    # differently with regard to extending the block.  For XL I'll have to add 77 tokens
    # for each block that goes over, and it will go over because I'm inserting lerp
    # values.  For SD3 I can just append any extras without doing that goofy stuff.
    # But, for just experimentation, I'll see what complaints I get from XL if I don't
    # submit 77 token rows when it expects it. UPDATE: (yea that broke it I think).

    # I'll use the cond_lerp original and ask arguments if "tokens" are enabled which
    # will swap out the function object to this one instead, for testing.

    def cond_lerp_tokens(cond):
        if args['cond_lerp_tokens']:
            print("sf::lerp_tokens:enabled")

            # For lerp_tokens I won't check the bitmap yet, this will be quite
            # complicated to think about, but if I get any usable results from
            # this then I'll consider it, I don't expect anything since, if
            # this did anything, it would have been done already I'm guessing.

            # The lerp is going to generate extra rows.  If I leave off the last
            # transitional lerp then I don't have to worry about the block size,
            # it will reproduce itself, in size, doubling it without spares.  Ok,
            # here we go O.o

# Not using yet
            bitmap = [int(d) for d in str(args['cond_lerp_map'])]
            bitmap.reverse() # I'll pop so I need to reverse it
            default = args['cond_lerp_default']
# /
            factor = args['cond_lerp_factor']
            matrix_block = cond.numpy()
            #matrix_lerp = np.array()
            matrix_lerp = []

            ceiling = len(matrix_block[0])

            # I won't process the last float, I'll just "continue".
            for row in range(ceiling):
                floats = []
                wall = int( len(matrix_block[0][row]) / 2 )
                wall_pointer = 0 # I reset this on half of the wall

                for f_count in range(wall):
                    wall_pointer += 1

                    flt_0 = matrix_block[0][row][f_count]
                    floats.append(flt_0)

                    flt_1 = matrix_block[0][row][f_count+1]
                    lerp = flt_0 + (flt_1 - flt_0) * factor
                    floats.append(lerp)

                    # don't hit the wall brutha
                    # this is half the distance, that's my wall, which will fill the "floats" will a full row
                    if wall_pointer == wall:
                        wall_pointer = 0
                        # If I get to the wall I have to append floats and move on.
                        matrix_lerp.append(floats)
                        floats = []
                        continue

            # This one needs to be re-tensored, there's more blocks interweaved.
            cond = torch.tensor([matrix_lerp])

            # After a lerp the data has doubled, almost, - 1.  I have to record
            # this as the new block size or the other functions will not have a
            # correct alignment.
            data['cond_old_size'] = len(cond[0])

        return cond

    # ----------------------------------------------------------------------------
    # matrix @
    # ----------------------------------------------------------------------------
    # dot product
    #a = [
    #    [ 2, 1, 1
    #    [5, 5, 4],
    #    [1, 2, 3],
    #    ]
    #b = [2, 1, 1]
    # (5*2) + (5*1) + (4*1)
    # 19
    #  7
    #result = np.dot(a, b) # = 19, 7
    def cond_rotate(cond):
        if False:
            if args['cond_rotate']:
                    print("sf::cond_rotate:enabled")
                    if False:
                        k = args['cond_rotate_k']
                        axes = args['cond_rotate_axes']

                        matrix_block = cond.numpy()
                        bnp = np.rot90(matrix_block[0], k=k, axes=axes)
                        cnpc = bnp.copy()
                        cnp = [torch.tensor(cnpc)]
                        cond = cnp
        return cond
    # ----------------------------------------------------------------------------
    # pooled -test
    # ----------------------------------------------------------------------------
    def pooled_fill(pooled):
        if args['pooled_fill']:
            pooled_array = pooled.numpy()
            for p in range(len(pooled_array[0])):
                pooled_array[0][p] = args['pooled_weight']
        return pooled
    # ----------------------------------------------------------------------------
    #
    # ----------------------------------------------------------------------------
    defaults = {

        "order": ProcessOrder.order,
        "cond_weight": False,
        "cond_weight_operands": "0.0, 0.0, 0.0, 0.0",
        "cond_weight_operators": Weight.methods,

        # The original methods will be a string of comma separated modifiers.  These
        # will be translated into something usable before use.
        "cond_weight_methods": Weight.methods,

        "cond_weight_map": "0",
        "cond_weight_default": 0, # unmapped blocks will be weight altered?
        "cond_expand": False,
        "cond_expand_amount": 0,
        "cond_expand_map": "000000", # a text representation of a bitmap, 0 = don't fill with first blocks (leave zeros), 1 = fill
        "cond_expand_default": 0,
        "expand_threshold": 10,
        "cond_invert": False,
        "cond_invert_map": "0",
        "cond_invert_default": 0,
        "cond_scale": False,
        "cond_scale_factor": 0,
        "cond_scale_map": "0",
        "cond_scale_default": 0,
        "cond_lerp": False,
        "cond_lerp_map": "10",
        "cond_lerp_factor": 0.0,
        "cond_lerp_tokens": False,

        # Mostly just a test for now but I got interesting results zeroing this out, no prompt and zero the cond, on XL.
        "pooled_fill": False,
        "pooled_weight": 0.0,
        }

    for d in defaults:
        if d not in args:
            args[d] = defaults[d]

    # used in functions
    data = {}
    #data['cond'] = cond
    data['cond_old_size'] = len(cond[0])
    data['cond_new_size'] = data['cond_old_size']
    data['methods'] = convert_methods(args['cond_weight_methods'])
    # ----------------------------------------------------------------------------
    # process order
    # ----------------------------------------------------------------------------
    # From the list offered, or the defaults, I place these dictionary items into
    # a function list to run.
    functions = {
        "cond_expand": cond_expand,
        "cond_weight": cond_weight,
        "cond_scale": cond_scale,
        "cond_invert": cond_invert,
        "cond_lerp": cond_lerp,
        "cond_lerp_tokens": cond_lerp_tokens,
        }

    # comma separated, see class, more convenient for transferring data through the work-flow
    # with respect to js
    proc = sep_to_list(ProcessOrder.order, ",")
    for p in proc:
        cond = functions[p](cond)

# T - a test for now
    pooled = pooled_fill(pooled)
# /

    return (cond, pooled)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------

