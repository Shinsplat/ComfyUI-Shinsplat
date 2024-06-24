# Shinsplat Tarterbox

import traceback

debug = False

help = """
# Variables are available by name as you see them in the UI ...
#
#   str_in1
#   str_out ... etc.
#
# Perform your task on the input and output and pass your outputs
# as you see fit.
#
print("Hello world!")
"""
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_PythonMore:
    """
    - Shinsplat Tarterbox -

    A simple Python execute process, allowing you to hand craft your own data
    manipulation schemes in the work-flow.

    - enabled -
    If enabled is False then the input will be passed to the output untouched,
    no matter what you have in your code/text box.
    """

    def log(self, m):
        if debug == True:
            print(m)

    def __init__(self):
        # trigger is just a switch for each rerun
        self.trigger = False

    def IS_CHANGED(s, **kwargs):
        return("junk")

    @classmethod
    def INPUT_TYPES(s):

        return {
                    "required": {
                        "code": ("STRING", {"default": help, "multiline": True, "dynamicPrompts": False}),
                        "enabled": ("BOOLEAN", {"default": True}),
                    },
                    "optional": {
                        "str_in1": ("STRING", {"default": help, "multiline": True, "dynamicPrompts": False, "forceInput": True}),
                        "str_in2": ("STRING", {"default": help, "multiline": True, "dynamicPrompts": False, "forceInput": True}),
                        "int_in1": ("INT", {"default":  0, "forceInput": True}),
                        "int_in2": ("INT", {"default":  0, "forceInput": True}),
                        "float_in1": ("FLOAT", {"default":  0.0, "forceInput": True}),
                        "float_in2": ("FLOAT", {"default":  0.0, "forceInput": True}),
                        "bool_in1": ("BOOLEAN", {"default":  False, "forceInput": True}),
                        "bool_in2": ("BOOLEAN", {"default":  False, "forceInput": True}),
                    },
            }

    RETURN_TYPES = ("STRING",   "INT",      "FLOAT",     "BOOLEAN",  "STRING",)
    RETURN_NAMES = ("str_out",  "int_out",  "float_out", "bool_out", "help",)

    OUTPUT_NODE = True

    FUNCTION = "run"

    CATEGORY = "advanced/Shinsplat"

    def run(self,
        text="", code="", enabled=True,
        str_in1="", str_in2="", int_in1=0, int_in2=0, float_in1=0.0, float_in2=0.0, bool_in1=False, bool_in2=False):

        # I need this in order to pass back changes to these containers from the compiled code.
        global str_out, int_out, float_out, bool_out

        # If the node is disabled then just pass the inputs to the outputs.
        if enabled == False:
            str_out = str_in1
            int_out = int_in1
            float_out = float_in1
            bool_out = bool_in1
            return(str_out, int_out, float_out, bool_out, help)

        # A default set of containers, it's not expected that they'll use all of them and they
        # have to be defined on the outputs.
        str_out = ""
        int_out = 0
        float_out = 0.0
        bool_out = False

        # I have to build a function in order to simplify output names.  This means that I won't
        # have access to the input names so I have to pass those to the function as arguments.
        # These are deposited as text but then compiled with "global" so that changes in their
        # code are reflect on these outputs without having to use "self.".
        #header = "def funkshun(**kwargs):\n"

        # This function text can be used in the def and call, so I'll only have to change it
        # in one place, **kwargs was driving me apples.
        call_line = "(str_in1=str_in1, str_in2=str_in2, int_in1=int_in1, int_in2=int_in2, float_in1=float_in1, float_in2=float_in2, bool_in1=bool_in1, bool_in2=bool_in2)"

        header = "def funkshun" + call_line + ":\n"
        # Note the space, I'll match this when going through the lines, I only need one
        # since I don't need to care about looking at it.
        header += " global str_out, int_out, float_out, bool_out\n"
        # Finally the function needs to be called so this goes at the end.
        footer = "funkshun" + call_line + "\n"
        # Compose the code, the real code, break up the code into lines and add the required
        # space before each line of code since this is contained within a function.
        lines = code.splitlines()
        body = ""
        for l in lines:
            body += " " + l + "\n"
        # I can overwrite "code" now, it won't be used again for anything.
        code = header + body + footer

        # Compile and run it.
        try:
            c = compile(code, "multistring", 'exec')
            exec(c)
        except Exception as e:
            txt = traceback.format_exc()
            raise RuntimeError(txt)

        return(str_out, int_out, float_out, bool_out, help)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Python - More Inputs (Shinsplat)": Shinsplat_PythonMore
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Python - More Inputs (Shinsplat)": "Python - More Inputs (Shinsplat)"
}

