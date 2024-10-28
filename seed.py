# Shinsplat Tarterbox

help = """
Why? Cos people doing dums.
"""


# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_Seed:

    @classmethod
    def INPUT_TYPES(s):
            return {"required": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)

    FUNCTION = "seaD"

    CATEGORY = "advanced/Shinsplat"

    def seaD(self, seed=0):

        return(seed,)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Seed (Shinsplat)": Shinsplat_Seed
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Seed (Shinsplat)": "Seed (Shinsplat)"
}


