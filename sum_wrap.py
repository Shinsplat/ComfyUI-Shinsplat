# Shinsplat Tarterbox

import time

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_SumWrap:
    """
    - Shinsplat Tarterbox -

    start - where to start
    step - what to add
    ceiling - the ceiling where we return to "start"
    wrap - where to return to after hitting the ceiling
    clear - reset the stored data, or just replace the node

    t_out - where we are now (string for convenience)
    i_out - integer output
    """

    def __init__(self):
        self.data = {
            "t_out": "0",
            "start": True,
        }

    def get_id(self):
        return time.time()

    @classmethod
    def INPUT_TYPES(s):
        return {
                    "required": {
                        "start":   ("INT", {"default": 0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
                        "step":    ("INT", {"default": 1, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
                        "ceiling": ("INT", {"default": 1, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
                        "wrap":    ("INT", {"default": 1, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
                        "clear":   ("BOOLEAN", {"default": False}),
                    },
            }

    RETURN_TYPES = ("STRING",  "INT",)
    RETURN_NAMES = ("txt_out", "int_out",)

    #OUTPUT_NODE = True

    FUNCTION = "wrap"

    CATEGORY = "advanced/Shinsplat"

    @classmethod
    def IS_CHANGED(self, **kwargs):
        return float("nan")

    def wrap(self, start=0, step=1, ceiling=1, wrap=1, clear=False):

        if clear == True:
            t_out = str(start)
            self.data['t_out'] = t_out
            print("sum_wrap: data cleared, make sure to turn this off for your next queue")
        else:
            # First run?
            if self.data['start'] == True:
                self.data['start'] = False
                t_out = str(start)
                self.data['t_out'] = t_out
            else:
                t_out = self.data['t_out']

        i_out = int(t_out)

        if i_out == ceiling:
            self.data['t_out'] = str(wrap)
        else:
            next_out = i_out + step
            self.data['t_out'] = str(next_out)

        return(t_out, i_out,)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Sum Wrap (Shinsplat)": Shinsplat_SumWrap
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Sum Wrap (Shinsplat)": "Sum Wrap (Shinsplat)"
}

