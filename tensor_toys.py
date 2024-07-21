
import os
import sys
from . import functions as sf

help ="""
The output of this tool is a string representation of a Python
dictionary structure.  It must be linked to the special node
"Clip Tokens Encode (Shinsplat)" to be of any value.  How you
get there is up to you.  For instance, if you want to modify
the values dynamically, you can utilize the Python module to
alter the container values before piping it out to the other
node.

I've included a set of templates for you already, you'll find them in
the directory structure of ./custom_nodes/ComfyUI-Shinsplat
(or just Shinsplat) and in a directory called "tensor_toys".

Node Path (usage):

    Text To Tokens (Shinsplat) -> (Clip Tokens Encode)

        This is your prompt container, what comes out is a repaired
        version of the encoded tokens in a text representation of a
        python Dictionary structure.

        Clip Tokens Encode (Shinsplat) -> (KSampler)

            This, paired with the above, comprise your cooperative
            tokenizer and encoder that is then sent into your
            work-flow.

            KSampler -> (VAE Decode)

                You're familiar with this, nothing else is different.

    Tensor Toys -> (Clip Tokens Encode)

        This connects to "Clip Tokens Encode (Shinsplat)" on the
        control_ port.

--

There is a default order of execution for these methods.  This is a comma (,)
separated string of function calls.  There's a text input area for you to alter
it.

You can see the default order by attaching a text output node to the "_control" port.

Template
    The name of the file you loaded
name
    The freeform name of the module, this will become the saved
    filename if nothing else is available, but you can change it
    during the save process.
enabled
    True/False - enable or disable the effect of this module

- cond = conditioning -
    This is the tensor weights produced by the back-end.

Suggestion:

    Test "cond_scale" features first and leave everything else at default
    values, meaning "OFF".  The cond_scale features will give you immediate
    results so that you can get a feel for how it works.

The features are applied in the order presented in "order".  This is a comma
separated string.

"order": "cond_expand,cond_weight,cond_scale,cond_invert"

cond_weight
    If enabled then the weight_amount will be applied.
cond_weight_map
    This is effectively a binary switch, 1 character per
    tensor block, 0 = skip that block.
cond_weight_method
    Some simple math here to apply to the indicated block of
    weights in the bitmap.  This string of modifiers can be
    something like +0.1, /1.02, *0.1, -0.002
cond_weight_default
    If the evaluator runs out of weight_map characters
    then the remaining are defaulted to this.
cond_expand
    Add this many more blocks, each additional block
    segment will be equal to the total already in existence.
cond_expand_map
    a text representation, like above, of the iteration map
    where a "0" indicates to skip the block and a 1 means
    to process it.  In this particular case a "0" will mean
    to leave the block alone where a "1" means to fill it
    with 0's.
cond_expand_default
    If the evaluator runs out of map tokens then this will
    used as the default for the remainder of the blocks.
cond_scale
    A floating point value to scale each of the indicated
    blocks by a percentage, positive and negative values
    can be used.
cond_scale_map
    Utilized the same as the other _map types.
cond_scale_default
    Senseless to repeat.
cond_lerp
    Comes with a set of parameters much like the others.  This
    function will interpolate the distance along each tensor
    token row using "factor" as the guide and insert that
    tensor row between the two, current and future.
cond_lerp_tokens
    This is probably immediately useless as it seems to produce
    a mish mash of this and that, images that could be akin to
    a dream, I left it in because it seems rather familiar for
    some reason and maybe, I'm hoping, by using just a mild
    touch of this, along with other modifiers, I can produce
    some interesting results, but it's not well tested yet.
pooled_fill
    Fills the pooled tensors with the weight from pooled_weight.
    I have no idea what this does but I found some interesting
    imagery zeroing out all conditioning and just letting the
    model hallucinate.  I haven't found a tool that will zero
    things out, so this turned out to be a pleasant enigma.
pooled_weight
    The weight applied to polled_fill (if enabled).  This is a
    quick hack to test zero weights on both cond and pooled and
    the results were surprising, I'll need to revisit this with
    more energy.

"""

class Shinsplat_TensorToys:
    """
    JSON/Python Dictionary generator for Tokens Encode.
    """

    def __init__(self):
        self.trigger = False

#    @classmethod
#    def IS_CHANGED(s):
#        #return self.trigger
#        return "dumb"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "order": ("STRING", {"multiline": True, "default": sf.ProcessOrder.order, "dynamicPrompts": False, "forceInput": False}),
                "template": ("STRING", {"multiline": False, "default": "empty", "dynamicPrompts": False}),
                "name": ("STRING", {"multiline": False, "default": "empty", "dynamicPrompts": False}),
                "enabled": ("BOOLEAN", {"default": True}),
                "cond_weight": ("BOOLEAN", {"default": False}),
                "cond_expand": ("BOOLEAN", {"default": False}),
                "cond_invert": ("BOOLEAN", {"default": False}),
                "cond_scale": ("BOOLEAN", {"default": False}),
                "cond_lerp": ("BOOLEAN", {"default": False}),
                "cond_lerp_tokens": ("BOOLEAN", {"default": False}),
                "pooled_fill": ("BOOLEAN", {"default": False}),

                "cond_weight_methods": ("STRING", {"multiline": False, "default": sf.Weight.methods, "dynamicPrompts": False}),

                "cond_weight_map": ("STRING", {"multiline": False, "default": "111110000000", "dynamicPrompts": False}),
                "cond_weight_default": ("BOOLEAN", {"default": True}),
                "cond_expand_amount": ("INT", {"default": 4, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
                "cond_expand_map": ("STRING", {"multiline": False, "default": "11", "dynamicPrompts": False, "forceInput": False}),
                "cond_expand_default": ("BOOLEAN", {"default": True}),
                "expand_threshold": ("INT", {"default": 10, "min": 1, "max": 0xffffffffffffffff}),

                "cond_invert_map": ("STRING", {"multiline": False, "default": "1000", "dynamicPrompts": False, "forceInput": False}),
                "cond_invert_default": ("BOOLEAN", {"default": False}),

                "cond_scale_factor": ("FLOAT", {"default": 0.0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
                "cond_scale_map": ("STRING", {"multiline": False, "default": "001", "dynamicPrompts": False, "forceInput": False}),
                "cond_scale_default": ("BOOLEAN", {"default": False}),

                "cond_lerp_factor": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0}),
                "cond_lerp_map": ("STRING", {"multiline": False, "default": "001", "dynamicPrompts": False, "forceInput": False}),
                "cond_lerp_default": ("BOOLEAN", {"default": False}),

                "pooled_weight": ("FLOAT", {"default": 0.0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
            },
            "optional": {
            },
            "hidden": {
                "content": ("STRING", {"multiline": True, "default": "{}", "dynamicPrompts": False, "forceInput": False}),
            },
        }

    RETURN_TYPES = ("STRING",   "STRING",)
    RETURN_NAMES = ("_control", "help",)
    FUNCTION = "controller_settings"
    CATEGORY = "advanced/shinsplat"

    def controller_settings(self, **kwargs):
        self.trigger = not self.trigger

        controller = ""
        if kwargs['enabled']:
            # The input items aren't nested ever, as far as I can tell, so a simple conversion is fine.
            controller = '{\n'
            for k in kwargs:
                v = kwargs[k]
                vs = str(v)
                if isinstance(v, str):
                    vs = '"' + v + '"'
                controller += "    "
                controller += '"' + k + '": ' + vs + ',\n'
            controller += '}\n'
        return (controller, help,)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Tensor Toys (Shinsplat)": Shinsplat_TensorToys,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Tensor Toys (Shinsplat)": "Tensor Toys (Shinsplat)",
}

