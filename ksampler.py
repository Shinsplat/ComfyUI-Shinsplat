
# The base code was taken from nodes.py utilizing KSamper class and ksampler_common function.
# There's no real need for it except to prevent a user from modifying their internal model
# structure without the forethought to use the proper node to fix it after the generation.
# I may decide on the dual node process anyway, or if I figure out how the patcher works
# I'll use that instead of this convoluted method.

import os
import sys
from . import functions as sf
import comfy
import latent_preview

help ="""
"""
class Shinsplat_KSampler:

    def __init__(self):
        pass

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = "advanced/shinsplat"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":
                {"model": ("MODEL",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step":0.1, "round": 0.01}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                "positive": ("CONDITIONING", ),
                "negative": ("CONDITIONING", ),
                "latent_image": ("LATENT", ),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                 },
            "optional": {
                "control_": ("STRING", {"multiline": True, "dynamicPrompts": False, "forceInput": True}),
            },
            "hidden": {
            },
        }
    def sample(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=1.0, control_=""):
        def dejector(
            model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent,
            denoise=1.0, disable_noise=False, start_step=None, last_step=None,
            force_full_denoise=False, control_=""
            ):

            # M
            if control_ != "":
                print("=================")
                print("changing model...")
                print("=================")
                cd = sf.string_to_dictionary(control_)
                model = sf.model_hijack(model=model, args=cd)
            # /

            latent_image = latent["samples"]
            latent_image = comfy.sample.fix_empty_latent_channels(model, latent_image)

            if disable_noise:
                noise = torch.zeros(latent_image.size(), dtype=latent_image.dtype, layout=latent_image.layout, device="cpu")
            else:
                batch_inds = latent["batch_index"] if "batch_index" in latent else None
                noise = comfy.sample.prepare_noise(latent_image, seed, batch_inds)

            noise_mask = None
            if "noise_mask" in latent:
                noise_mask = latent["noise_mask"]

            callback = latent_preview.prepare_callback(model, steps)
            disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
            samples = comfy.sample.sample(
                model, noise, steps, cfg, sampler_name, scheduler,
                positive, negative, latent_image, denoise=denoise,
                disable_noise=disable_noise, start_step=start_step,
                last_step=last_step, force_full_denoise=force_full_denoise,
                noise_mask=noise_mask, callback=callback, disable_pbar=disable_pbar, seed=seed
                )
            out = latent.copy()
            out["samples"] = samples

            # M
            # Restore the model.
            if control_ != "":
                print("==================")
                print("restoring model...")
                print("==================")
                model = sf.model_release(model=model)
            # /

            return (out, )

        return dejector(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise, control_=control_)
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "KSampler (Shinsplat)": Shinsplat_KSampler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KSampler (Shinsplat)": "KSampler (Shinsplat)",
}

