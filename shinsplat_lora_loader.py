# Shinsplat Tarterbox

import os
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

    - meta data and trigger phrase visual -
    does not contact civitai, it extracts the data directly from the file.

    - sharing paths between lora loders -
    pass_through -  when enabled will read the path_out from another of these nodes, or even
                    a text node, and load the LoRA from that path.
    path_out     -  a text type used for the path_in of another of these nodes.

    - saving and extracting prompt data associated with a particular lora -
    prompt_in    -  a text prompt associated with this LoRA that will be saved to a file
                    a file is created with the lora base name and extension .prompt.txt
                    if you move your lora file you aught to move this prompt file as well
    prompt_out   -  a text output associated with this LoRA that will be extracted from a file

    - weight_clip / weight_model -
    An iterator process that takes text floats as input and sequences through them as floats.
    """

    def __init__(self):
        self.loaded_lora = None

        # Shinsplat
        self.trigger = False
        self.start = True
        self.weights = {
            "model": [],
            "clip": [],
        }
        # If incoming data doesn't match what was saved then it has to be reprocessed.
        self.backups = {
            "strength_model": 0.0,
            "strength_clip": 0.0,
            "weights_model": "",
            "weights_clip": "",
        }

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
                            #"path_in": ("STRING", {"multiline": True, "default": "", "forceInput": True}),                
                            #"prompt_in": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                            #"weight_model": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                            #"weight_clip": ("STRING", {"multiline": True, "default": "", "forceInput": True}),

                            "path_in": ("STRING", {"default": "", "forceInput": True}),                
                            "prompt_in": ("STRING", {"default": "", "forceInput": True}),
                            "weight_model": ("STRING", {"default": "", "forceInput": True}),
                            "weight_clip": ("STRING", {"default": "", "forceInput": True}),
                            },
                }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING",      "STRING",      "STRING",   "STRING", )
    RETURN_NAMES = ("MODEL", "CLIP", "path_out",    "prompt_out",  "triggers", "meta")

    FUNCTION = "load_lora"

    CATEGORY = "advanced/Shinsplat"

    def load_lora(
        self, model, clip, lora_name, strength_model, strength_clip,
        pass_through=False, path_in="", prompt_in="", weight_model="", weight_clip=""):

        # If there's anything on the weights line the node has to re-run.
        weight_clip = weight_clip.strip()
        weight_model = weight_model.strip()

        # I'll set a flag for later testing.  It tells me if something changed.  It may appear
        # that this isn't needed, because something changing triggers the node to run but, at
        # some point, I will make sure the node continues to run, even when something doesn't
        # change, in order to iterate over the list of floats the node is given.
        something_changed = False
        # yea, I could do "or" on all of these but I'm not gunna O.o
        if self.backups['strength_clip'] != strength_clip:
            something_changed = True
        if self.backups['strength_model'] != strength_model:
            something_changed = True
        if self.backups['weights_clip'] != weight_clip:
            something_changed = True
        if self.backups['weights_model'] != weight_model:
            something_changed = True

        if something_changed == True:
            self.start = True
            if hasattr(self.__class__, 'IS_CHANGED'):
                delattr(self.__class__, 'IS_CHANGED')

        # If the node is triggered it's because it's a first run or re-run was enabled.
        # If there's no input then there shouldn't be a trigger.  I don't have to worry
        # about the strength change, only my own parameters, the strength change will do
        # its own thing and my added code will conform.
        if weight_model != "" or weight_clip != "":

            # The node triggers the the test above runs, and I'm here now.  Is it the
            # first run?
            if self.start == True:
                self.start = False

                # Used later in case any input changes.
                self.backups['strength_clip'] = strength_clip
                self.backups['strength_model'] = strength_model
                self.backups['weights_model'] = weight_model
                self.backups['weights_clip'] = weight_clip

                def IS_CHANGED(self):
                    self.trigger = not self.trigger
                    return not self.trigger
                setattr(self.__class__, 'IS_CHANGED', IS_CHANGED)

                # The longest list of floats will be used for the iterator, the
                # next list will be padded with the "strength_" of its counterpart
                # since this code has to run each time anyway.  After the entire
                # sequence has been exhausted I can I can turn off re-run and allow
                # the pre-defined weights to drop through, at which point the LoRA
                # won't have to recondition the model anymore, in case they run over.

                # Convert the float string representations into actual floats.  We
                # might get int representations and that's fine too.
                model_string = weight_model.split()
                clip_string = weight_clip.split()
                self.weights['model'] = [float(a) for a in model_string]
                self.weights['clip'] = [float(a) for a in clip_string]

                # Which one is longer?  This portion is inefficient but highly readable.
                padding_required = False
                if len(self.weights['model']) > len(self.weights['clip']):
                    padding_required = True
                    fill = "clip"
                    filler = strength_clip
                if len(self.weights['clip']) > len(self.weights['model']):
                    padding_required = True
                    fill = "model"
                    filler= strength_model
                if padding_required:
                    count = abs( len(self.weights['clip']) - len(self.weights['model']) )
                    print(str(count))
                    # I know what the target is now, iterate the longest.
                    for i in range(count):
                        self.weights[fill].append(filler)

                # Now I'll run out of both at the same time.

                # I'll be popping off the end so reverse the lists.
                self.weights['model'].reverse()
                self.weights['clip'].reverse()

        # Here we go, I only need to test one because the length of will should
        # equal, either when we start or after filling.
        if len(self.weights['model']):
            strength_model = self.weights['model'].pop()
            strength_clip = self.weights['clip'].pop()
        else:
            # I've reached the end or the lists were never populated.  Remove
            # the re-run and reset the start flag.
            self.start = True
            if hasattr(self.__class__, 'IS_CHANGED'):
                delattr(self.__class__, 'IS_CHANGED')

        # This wasn't documented but it's obvious that there's no sense in
        # running of there's no weights to change.
        if strength_model == 0 and strength_clip == 0:
            return (model, clip)

        lora_path = folder_paths.get_full_path("loras", lora_name)

        # Overwrite the lora_path if pass_through is enabled.  This allows me to have separate models passing
        # through the same loras, but they are probably loaded fully again.  I used this to compare different
        # models with the same set of loras.
        if pass_through == True:
            lora_path = path_in

        path_out = lora_path

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
        # lora prompt start
        # -----------------------------------------------------------------------------

        # Get the entire path to the lora file but strip off the extension.
        file_base = os.path.splitext(lora_path)[0]
        # Add an extension that makes it obvious what it is.
        prompt_file = file_base + ".prompt.txt"

        # If the prompt_in has content, and it's not just whitespace, it should
        # be written to the file.
        prompt_content = prompt_in.strip()

        # If it's empty open the file for reading only.  This works if the input
        # isn't connected or if the content text box is just whitespace or empty.
        if prompt_content == "":
            try:
                f = open(prompt_file, "r", encoding="utf-8")
                prompt_content = f.read()
                f.close()
            except:
                print("file", prompt_file, "does not exist")
        # If there's content on the input then it should always be deposited into
        # the file.
        else:
            try:
                f = open(prompt_file, "w", encoding="utf-8")
                f.write(prompt_content)
                f.close()
            except:
                print("shinsplat_lora_loader::prompt file save failed, check folder/file permissions at", prompt_file)

        # The prompt_content already contains what's needed for the prompt_out at this point.
        prompt_out = prompt_content

        # -----------------------------------------------------------------------------
        # lora prompt end
        # -----------------------------------------------------------------------------

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
        return (model_lora, clip_lora, path_out, prompt_out, triggers, meta_string)

# --------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Lora Loader (Shinsplat)": Shinsplat_LoraLoader
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Lora Loader (Shinsplat)": "Lora Loader (Shinsplat)"
}
