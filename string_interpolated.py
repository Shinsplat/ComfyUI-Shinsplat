# Shinsplat Tarterbox

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_StringInterpolated:
    """
    - Shinsplat Tarterbox -

    Nothing exciting to see here.

    I didn't find a text outputter thingy that had dynamicPrompts enable *shrugs*
    I may add more silly things to this later.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                },
            }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("STRING", )

    FUNCTION = "interpolate"

    CATEGORY = "advanced/Shinsplat"

    def interpolate(self, text):
        t_out = text.split("END")[0]
        return (t_out,)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "String Interpolated (Shinsplat)": Shinsplat_StringInterpolated
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "String Interpolated (Shinsplat)": "String Interpolated (Shinsplat)"
}

