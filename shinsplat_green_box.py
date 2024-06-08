# Shinsplat Tarterbox

import ast
import time
import traceback

debug = True

help = """

You'll need to format your prompt(s) a certain way for them to be added as a list.

Each item (prompt) must be enclosed in double or single quotation marks and ending with a comma (,).  If you need to use quotation marks within your prompt, in order to quote something, you will use single quotes (') to enclose your prompt.  The following evaluates without errors, because the instructions have been commented out using the "#" symbol.  This text, itself, is not compatible.

# This is a comment.
# You can keep notes here, it won't cause an error.
# The following are prompt elements to iterate through...

"a fiddly widdly on a boat of goats",
"a horse full of barns",
"a clown with a broken laugh",

# - ADVANCED -

# Using quoted material

"a T-Shirt with the text 'Happy Day' written on it.",

# Alternatively swap your quotes, using singles to enclose
# your prompt, which will pass exactly the same thing as
# the above...

'a T-Shirt with the text "Happy Day" written on it.',

# The freedom to compose, start with a quote on a single line if you like.

"
This is a prompt element.  Extra space is striped out as being superfluous,
the evaluator reads tokens out of words so as long as you have spaces in
the right places (np) you're fine, extra is of no concern.
",

# If, for some goofy reason, you need to arbitrarily pass quotes, or some
# other normally evaluated characters, to the parser, you need to double
# escape it...

'a prompt of quotes \\'\\'\\'\\"',
"another prompt of quotes \\"\\'\\"\\'",

# There are two directives that you can use in a comment and, if present,
# the action will be taken, even though it is not evaluated.  These two
# directives are CLEAN and DUST and their upper case versions must be used.
# SD only reads lower-case so this allows us to issue commands in upper-case.
#
# DUST - reset this node on the next run, make sure to remove this key word after
# CLEAN - rest this node and all those down the chain, remove this after.

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
    This switch effects all nodes and will force your iterations to start from the
    beginning.  After a single run, with this enabled, switch it back off or you'll
    get only the first prompt of each chained node.
    """

    # This will be switched to True if any node has "start_over": True
    clean = False

    def log(self, m):
        if debug == True:
            print(m)

    def __init__(self):
        # trigger is just a switch for each rerun
        self.trigger = False
        self.start = True # False after the first run so I know when to stop and recycle.
        prompts = []

    def IS_CHANGED(s, **kwargs):
        self.trigger = not self.trigger
        return(self.trigger)

    @classmethod
    def INPUT_TYPES(s):
        return {
                    "required": {
                        "text": ("STRING", {"default": "", "multiline": True, "dynamicPrompts": False}),
                        "loop": ("BOOLEAN", {"default": False}),
                        "enabled": ("BOOLEAN", {"default": True}),
                        "start_over": ("BOOLEAN", {"default": False}),
                    },
                    "optional": {
                            "chain": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                            },
            }

    RETURN_TYPES = ("STRING", "STRING",   "STRING",)
    RETURN_NAMES = ("chain",  "prompt",   "help",)

    #OUTPUT_NODE = True

    FUNCTION = "select"

    CATEGORY = "advanced/Shinsplat"

    def select(self, text="", loop=False, enabled=True, chain="", start_over=False):

        # Set the node's global
        clean = start_over
        if clean == True:
            self.start = True
            return(str([]), "", help)

        # Nothing in, nothing out.
        if text == "" and chain == "":
            #if hasattr(self.__class__, 'IS_CHANGED'):
            #    delattr(self.__class__, 'IS_CHANGED')
            self.start = True
            self.prompts = []
            # return chain, text_out and help
            return ("", "", help)

        # Even if disabled I still want to pass "chain" along.
        chains = []
        if chain != "":
            chains = ast.literal_eval(chain)

        if enabled == False:
            self.start = True
            self.prompts = []
            # return chain, text_out and help
            return (str(chains), "", help)

        # First run?
        if self.start == True:
            try:
                # Add the missing brackets to represent a list containing strings,
                # then evaluate.
                self.prompts = ast.literal_eval("[" + text + "]")
            except Exception as e:
                print("=====================================")
                print("Python list format error!")
                print("-------------------------------------")
                print(traceback.format_exc())
                print("=====================================")
                raise RuntimeError("Your text needs to be valid Python code, a dictionary.")
                return (str(chains), "", help)

            # It's possible that a crafty person will try to add these to a string representation    
            # of a list, which will break the process.  So I'll test the first element to make sure
            # that it's not a list, hence they didn't add the "[]" to enclose their prompt, good.
            if len(self.prompts) > 0:
                if not isinstance(self.prompts[0], str):
                    raise RuntimeError("The prompt is malformed and should not represent a", str( type(self.prompts[0]) ) )
                    return(str(chain), "", help)

            #setattr(self.__class__, 'IS_CHANGED', IS_CHANGED)
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

        return(str(chains), prompt,  help)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Green Box (Shinsplat)": Shinsplat_GreenBox
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Green Box (Shinsplat)": "Green Box (Shinsplat)"
}

