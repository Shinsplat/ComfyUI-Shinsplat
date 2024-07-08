# Shinsplat Tarterbox

import ast
import time
import traceback

debug = True
clean = False

help = """
---------------------------------------------------------------------------
My previous rendition of this had you enclose your prompts in quotation marks,
since I wanted to evaluate each line and be able to ignore # comments but
somewhere in my defective thinking I assumed the parser was ignoring new lines,
and it is not.

So, the way to proceed is to use 1 prompt per line, ending it
with a return <enter> if you want to include more prompts than 1.  Extra new
lines will be ignored so you can add double space for better readability.

I could have easily stripped out the # comment line but I have no idea if
anyone wants to use the hashmark in their prompt, and have no clue if it's
even useful.  So, as it stands, no comments, sorry.

With the current implementation it would stand to reason that, eventually,
I can add a file reader to replace the input.  It looks like this implementation
would support existing wildcard files.
---------------------------------------------------------------------------

This is a prompt,

This is another prompt

There's a cat walking on a sidewalk wearing a hat

a cyborg is standing in the middle of a big city street, cars all around, day time,
a robot is eating cereal on a farm, cereal box on the table, sun shining through the window, 1960s setting


"""


# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_GreenBox:
    """
    - Shinsplat Tarterbox -

    Internally these prompt elements are converted to a list of strings.  You are
    providing the conditioned enclosures in order for the parser to turn them into
    Python lists, this seems to be the simplest method.  Your prompts will consists
    of "quoted words, descriptions, just like you would normally, but will start with
    a single or double quote and end with the same and a comma", .  Examples are
    shown in the "help" output.

    This will iterate through the texts and add it to your output, on each generation.
    When it reaches the end of the list it will start over.  Unlike random prompts,
    or wild-cards, this will use the text only once, until it runs out, and then
    roll-over if enabled.  Unlike other nodes that I've run into this is a single
    encompassing combiner, where you can chain these together and link the chain
    input and output, ultimately resulting in the end nodes` output containing all
    other output in the chain.

    If you're using the Shinsplat Clip Text Encoder then you'll notice a convenient
    hook-up for text, where you can add these to prompt_before, prompt_after or both.

    - loop -
    This will start the prompt list from the top after running out, if the generations
    continue.  Those without loop enabled will issue an empty string on return when
    it runs out of prompts.

    - start_over -
    This will reset the node data and start from the beginning.  I've chosen to keep
    this local, instead of affecting all of the nodes, since it's the most logical
    and easier path.

    "END" - directive
    everything after this uppercase word is ignored

    - chain -
    Pipe these node together using this, ultimately ending in the "prompt" output.

    - _int, _flt -
    An attempt will be made to produce integers and floating points for these outputs.
    I initially added these so that I could iterate generations using the same seed
    for a specific number of generations, so that I could add different prompts or
    in put, for those/that same seeds.

    """

    def log(self, m):
        if debug == True:
            print(m)

    def __init__(self):
        # trigger is just a switch for each rerun
        #self.trigger = False
        self.start = True # False after the first run so I know when to stop and recycle.
        prompts = []

    def IS_CHANGED(c):
        return

    @classmethod
    def INPUT_TYPES(s):
        return {
                    "required": {
                        "text": ("STRING", {"default": "", "multiline": True, "dynamicPrompts": False}),
                        "loop": ("BOOLEAN", {"default": True}),
                        "enabled": ("BOOLEAN", {"default": True}),
                        "start_over": ("BOOLEAN", {"default": False}),
                    },
                    "optional": {
                            "chain": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                            },
            }

    RETURN_TYPES = ("STRING", "STRING", "INT",  "FLOAT", "STRING",)
    RETURN_NAMES = ("chain",  "prompt", "_int", "_flt",  "help",)

    #OUTPUT_NODE = True

    FUNCTION = "select"

    CATEGORY = "advanced/Shinsplat"

    def select(self, text="", loop=False, enabled=True, chain="", start_over=False, seed=0):

        if 'END' in text:
            text = text.split("END")[0]

        clean = start_over

        # Set the node's global
        if clean == True:
            self.start = True
            return(str([]), "", help)

        # Nothing in, nothing out.
        if text == "" and chain == "":
            self.start = True
            self.prompts = []
            # return chain, text_out and help
            return (str([]), "", help)

        # Even if disabled I still want to pass "chain" along.
        chains = []
        if chain != "":
            chains = ast.literal_eval(chain)

        if enabled == False:
            self.start = True
            self.prompts = []
            prompt = " ".join(chains)
            # return chain, text_out and help
            return (str(chains), prompt, help)

        # First run?
        if self.start == True:
            try:

                # split everything up at the \n, creating a list
                temp = text.splitlines()
                # ignore all empty elements and create a new list
                self.prompts = [] # start over
                for l in temp:
                    if l == "":
                        continue
                    self.prompts.append(l)
            except Exception as e:
                print("=====================================")
                print("- SOMETHING WENT WRONG, READ BELOW -")
                print("-------------------------------------")
                print(traceback.format_exc())
                print("=====================================")
                raise RuntimeError("")
                return (str(chains), "", help)

            self.start = False
            # Flip it backwards because I'm always going to do a .pop().
            self.prompts.reverse()

        # I check the length of the list to see if this will be the last one, a length of 1, and
        # I'll pop that one but also set things for a rerun, or to stop, because I know the next
        # run would be a (0) and we can't pop that O.o
        #
        # Disable repeat on next pass, if this is the last element, unless loop is enabled then we start over.
        if len(self.prompts) == 1:
            if loop == True:
                # On the next run the prompts will be filled again.
                self.start = True

        # If I've been here before and ran out of prompts, then loop wasn't enabled at that time
        # so I hit the zero and need to test it again for loop.
        if len(self.prompts) == 0 and loop == True:
                self.start = True

        # The outgoing prompt needs all of its previous chains.
        prompt = ""
        # If there is anything in the chain then add it to the outgoing prompt.
        if len(chains):
            prompt = " ".join(chains) + " "

        # ... then append our single prompt, unless less the list is empty.  If the list IS empty then
        # we've already fulfilled our part and loop wasn't enabled for this node.
        if len(self.prompts):
            this_prompt = self.prompts.pop()
            # and add this prompt instance to the chain
            chains.append(this_prompt)
        else:
            this_prompt = ""

        prompt += this_prompt

        # The _int and _flt can only be used as a single item so check the prompt for
        # compatibility.
        _int = 0
        _flt = 0.0
        str_num = prompt.strip()
        try:
            _int = int(str_num)
            _flt = float(_int)
        except:
            pass
        try:
            _flt = float(str_num)
        except:
            pass

        return(str(chains), prompt, _int, _flt, help)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Green Box (Shinsplat)": Shinsplat_GreenBox
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Green Box (Shinsplat)": "Green Box (Shinsplat)"
}
WEB_DIRECTORY = "./web"



