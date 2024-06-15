# Shinsplat Tarterbox

import ast
import traceback

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_Variables:
    """
    - Shinsplat Tarterbox -

    # Make sure to use a comma (,) after each variable section or it will not
    parse correctly, you will get an error.  This is effectively converted into
    JSON, or a simple Python dictionary.

    # The first part is the key, the variable.  The source text will have its
    same name replaced by the text, but in he source text you'll add a $ to it.
    For example, the assignments below will have its counterpart desribed as

    $THIS
    $THAT

    # and can be used in a sentence such as,

    A man is driving $THIS while drinking $THAT.

    THIS: "a black car",
    THAT: "a cup of coffee",

    # An example of how to use this is to attach a text, such as "String Interpolated"
    # or "String Literal" and pipe its TEXT output into this node, then pipe this
    # node's output to your prompt input.

    # You're not currently restricted to using capitol word variable names but it's
    # a better choice since the evaluator is designed to utilize lower case tokens.
    # Any uppercase characters are reduced to their lowercase counterparts before
    # being tokenized.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        default = '"THAT": "some text here",\n"THIS": "some other text",\n'
        return {
            "required": {
                "text": ("STRING", {"default": default, "multiline": True, "dynamicPrompts": False}),
                },
            "optional": {
                "text_in": ("STRING", {"multiline": True, "dynamicPrompts": False, "forceInput": True}),
                },

           }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("STRING", )

    FUNCTION = "variables"

    CATEGORY = "advanced/Shinsplat"

    def variables(self, text, text_in):
        t_out = text_in.split("END")[0]

        # TODO:  Proper variable interpolation, this is a quick hack for now.
        # You can't $THIS $THIS2 and expect logical results, yet.
        string_dict = "{" + text + "}"
        try:
            real_dict = ast.literal_eval(string_dict)
        except Exception as e:
            txt = traceback.format_exc()
            raise RuntimeError(txt)
            return("",)
        for k in real_dict:
            fake_v = "$" + k
            t_out = t_out.replace(fake_v, real_dict[k])

        return (t_out,)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Variables (Shinsplat)": Shinsplat_Variables
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Variables (Shinsplat)": "Variables (Shinsplat)"
}

