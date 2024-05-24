# Shinsplat Tarterbox

import ast
import json
import comfy
import folder_paths
# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
class Shinsplat_LoraLoader:
    """
    - Shinsplat Tarterbox -

    I didn't write this entirely, I took this simple node from the existing ones in
    ComfyUI and I altered it to fit my needs.
    --
    When I first started making pictures with SD I didn't realize how important the
    keywords, or "trigger words", would be and neglected to copy them for later use.
    Since then I've amassed quite a few models and was unable to figure out how to
    use them without going back to the source, if I was able to even find it, and
    get the information from there.  So I copied the lora loader node and added
    some code to it that will examine the header of the safetensor file and
    spit out the key words, or phrases, that were used during training.  There's,
    often times, more key-words/phrases in the header than what was exposed to the
    general public, which may not be useful at all but I find it interesting to
    tinker with.
    """

    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "model": ("MODEL",),
                              "clip": ("CLIP", ),
                              "lora_name": (folder_paths.get_filename_list("loras"), ),
                              "strength_model": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
                              "strength_clip": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
                              "pass_through": ("BOOLEAN", {"default": False}),
                             },
                "optional": {
                            "path_in": ("STRING", {"multiline": False, "default": "", "forceInput": True}),                
                            }
                }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING",      "STRING",   "STRING")
    RETURN_NAMES = ("MODEL", "CLIP", "path_out",    "triggers", "meta")

    FUNCTION = "load_lora"

    CATEGORY = "advanced/Shinsplat"

    def load_lora(self, model, clip, lora_name, strength_model, strength_clip, pass_through=False, path_in=""):

        if strength_model == 0 and strength_clip == 0:
            return (model, clip)

        lora_path = folder_paths.get_full_path("loras", lora_name)

        # Overwrite the lora_path if pass_through is enabled.  This allows me to have separate models passing
        # through the same loras, but they are probably loaded fully again.  I used this to compare different
        # models with the same set of loras.
        if pass_through == True:
            lora_path = path_in

        path_out = lora_path
        # #

        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                temp = self.loaded_lora
                self.loaded_lora = None
                del temp

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)

        # -----------------------------------------------------------------------------
        # get_meta start
        # -----------------------------------------------------------------------------
        def get_meta(file_path, total_top=3, total_sub=3):

            #total_top = 3 # How many top level phrases to choose? {"10_monkey": <-- }
            #total_sub = 3 # How many sub level phrases to choose? {"10_monkey": "sub phrase here": -int-, "another one here": -int-, ... <--}

            f = open(file_path, "rb")
            try:
                count_block = f.read(8)
            except:
                print("shinsplat:lora_loader::get_meta reports - couldn't read file")
                return("None", "None")
            header_count = int.from_bytes(count_block, "little")
            try:
                header_bytes = f.read(header_count)
            except:
                print("shinsplat:lora_loader::get_meta reports - unexpected header block")
                f.close()
                return("None", "None")
            f.close()

            header_string = header_bytes.decode("utf-8")
            header = ast.literal_eval(header_string)

            del count_block
            del header_count
            del header_bytes
            del header_string

            triggers = "No triggers were found. see the meta output for details"
            meta_string = "No meta data was found"

            if "__metadata__" in header:
                triggers = "__metadata__ : exists\n"
                meta_raw = header['__metadata__']

                del header

                # pull out the json that's valid, convert what's not valid to a string, and structure
                # it into a dictionary that will later be json.dumps() into a formatted json string.
                meta_dict = {}
                for key in meta_raw:
                    value = meta_raw[key]
                    # valid json will be stored as a dictionary value
                    try:
                        value_valid = "[" + value + "]"
                        value_json = json.loads(value_valid)[0]
                        meta_dict[key] = value_json
                    # invalid json will be cast to a string and stored as a value
                    except:
                        meta_dict[key] = str(value)
                del meta_raw

                # I should have a valid dictionary now, which can be dumped into a json string
                meta_string = json.dumps(meta_dict, indent=4)

                if "ss_base_model_version" in meta_dict:
                    triggers += "Base Model: "
                    triggers += meta_dict['ss_base_model_version'] + "\n"

                unique_phrases = set() # There's no need to repeat a phrase

                # Grab the frequency before deleting the container, if it exists.
                if "ss_tag_frequency" in meta_dict:
                    triggers += "--\n"
                    triggers += "Below are some of the higher number training phrases.  If "
                    triggers += "you want them all then have a look at the (meta) output.\n"
                    triggers += "--\n"
                    phrases = {}
                    for phrase_index in meta_dict['ss_tag_frequency']:
                        phrase_key = phrase_index.split("_")[-1]
                        if phrase_key not in phrases:
                            phrases[phrase_key] = {}
                        for phrase in meta_dict['ss_tag_frequency'][phrase_index]:
                            # I'm not even sure this can happen but, just in case, I'll check if
                            # this has already been added.  One problem I see is that a phrase
                            # could have been repeated in a different index with a higher count,
                            # which would goof up my intent to take the highest n count of
                            # occurrences, though I don't see this happening yet.
                            if phrase in unique_phrases:
                                continue
                            unique_phrases.add(phrase)

                            # get the frequency count
                            count = meta_dict['ss_tag_frequency'][phrase_index][phrase]
                            # make it a key in this index section
                            if count not in phrases[phrase_key]:
                                phrases[phrase_key][count] = [] # make it a list
                            # add this phrase to its count key
                            phrases[phrase_key][count].append(phrase)
                else:
                    print("shinsplat:lora_loader::get_meta reports - no usable metadata")
                    return(triggers, meta_string)

                del meta_dict
                del unique_phrases

                # For each phrase index get the counts in that section and take the top
                # total_top to display in each phrase index section.  Each one of these
                # phrase indices could be very different training data, and probably is,
                # so I should provide a sample from each and I use "total_top" to count
                # how many of those I take.  This "total_top" may become a feature in
                # the future instead of hard-coded.
                for phrase_index in phrases:
                    counts = set()
                    triggers += "phrase index: " + phrase_index + "\n"
                    for phrase_count in phrases[phrase_index]:
                        counts.add(phrase_count)
                    # Sort the set into a list
                    freq = sorted(counts)

                    # I don't know if this can happen
                    if len(freq) == 0:
                        continue

                    top_count = total_top
                    while top_count > 0:
                        if len(freq) == 0:
                            break
                        count = freq.pop()
                        if len(phrases[phrase_index][count]) == 0:
                            continue
                        top_sub = total_sub
                        while top_sub > 0: # How many of these to take?
                            if len(phrases[phrase_index][count]) == 0:
                                break
                            triggers += "    " + phrases[phrase_index][count].pop() + "\n"
                            top_sub -= 1
                        top_count -= 1

                del counts
                del phrases
                del freq

            return(triggers, meta_string)
        # -----------------------------------------------------------------------------
        # get_meta end
        # -----------------------------------------------------------------------------

        triggers, meta_string = get_meta(lora_path)
        return (model_lora, clip_lora, path_out, triggers, meta_string)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Lora Loader (Shinsplat)": Shinsplat_LoraLoader
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Lora Loader (Shinsplat)": "Lora Loader (Shinsplat)"
}
