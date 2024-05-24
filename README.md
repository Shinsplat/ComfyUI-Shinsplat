# ComfyUI-Shinsplat
ComfyUI Node alterations that I found useful in my own projects and for friends.

Clip Text Encoders add functionality like BREAK, END, pony.
Lora loader extracts metadata and keywords.

We have a channel in our learning server (Community College) on Discord: https://critters.xyz/sd/

# :wrench: ComfyUI Convenience Nodes

## Nodes

- These modified (Clip Text Encode) and (Clip Text Encode SDXL) nodes allows the use of BREAK so you can split up your context, the END directive that allows you to skip all text after, pony features and a prompt counter with token display.
- This modified (Lora Loader) will automatically extract metadata and potentially read trigger phrases/words.

##	BREAK

	These two nodes allow the use of the "BREAK" directive.

	During my search for nodes that break up context in a prompt I discovered
	a handful that purported to perform this task.  After utilizing all of them
	I did not get any consistent described results, from any of them.

	After creating my BREAK alternative I found that "Conditioning (Concat)"
	performs similarly but I like having the convenience of being able to put
	BREAK in my prompt wherever I want.

	While I have never experienced BREAK in my travels with Automatic1111,
	which was brief, I've read that this special term is used in their prompt
	evaluator in order to generate separate blocks, possibly in an attempt to
	control context.  While the implementation intent does not appear to control
	context, in any significant way, my altered node does allow this directive
	to designate where a block starts, by ending a previous block.

## PROMPTS

	I wanted, for quite awhile, to have a prompt evaluation tool so I wrote it.
	Along with the block and token data, that is presented as a result of my
	attempt at the BREAK directive, I also implemented a prompt expander, which
	is a second text output from these two nodes, showing you exactly what the
	interpreter sees as prompts.

	I also added a "prompt" output, since I was uncertain where to find one
	that just piped the text out in order to share with other nodes.  The
	encoder doesn't receive the commented out bits since it is intercepted
	before it even gets to the node so you won't get a prompt text output
	that contains //this here .. or .. /* that there */ .  The node does not
	have access to this.  One might wonder why I didn't just use a text node
	to begin with and I would nod but also know that the ones I've used do
	not support filtering comments.

## END

	I also added an "END" directive.  So often I've just wanted to alter the
	prompt at the top and skip everything else, as a quick test, but I've
	had to resort to using the 'C' style block comment /*...*/, which is fine
	but inconvenient, so I can now just put my short prompt, finish it with END,
	and the remaining text won't be evaluated.

## PONY

	For those who use the PonyXL models there is a "pony" switch to add the
	score data to the beginning of your prompt automatically, without having
	to type it, and it will also add the expected "BREAK" command, so the
	prepended line to your prompt will be ...

	score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, BREAK

	What I have learned, at least I think I have, is that it's best to have
	all scores included, though it can still pose a mystery and sometimes I
	find that removing lower scores can fix a broken prompt but I know that
	the issue is elsewhere.

	The SDXL version of the Clip Text Encode have _g and _l input strings
	and the reason for the separation doesn't appear to be documented.

	I'm uncertain if it's valuable or not but I added the pony switch to both
	the _g and _l terms separately.  With respect to the SDXL and Simple
	encoder, what I have noticed is if you use the same prompt criteria in
	both _g and _l text areas you get the same result as if you had used the
	simple Clip Text Encoder, if using the default resolutions, which
	duplicates the _l into _g on the back-end.

	Note that, before these nodes, your BREAK command did absolutely nothing
	to condition your prompt in ComfyUI and is, instead, lowercased to a term,
	whatever "break" does.  In my implementation the uppercase word, BREAK,
	never gets past to a token block and is removed by my code.  If you
	actually want to say "break" just do so, the lower case version is passed
	to the evaluator.  As a matter of fact you'll notice that, at least in
	ComfyUI, everything is reduced to lowercase anyway and this is why I can
	implement a directive structure using upper case terms, which I may add
	to later.

	Also note that it doesn't matter where you place directive code, it will
	be removed and your prompt will be restructured without it.

Lora Loader

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

	For now it can only read Kohya headers for specific data, as far as I know,
	but there are two outputs, one for cherry picked data for convenience, and the
	other is the entirety of the meta-data, which could be huge or almost nothing
	at all.

	I see a growing trend, or maybe it's a default feature, of meta-data being
	stripped, or simply not included, in these files and I hope that will change
	in the future so that we always have a way to identify trigger phrases.

## pass_through

	You can use this to pass the text path from one lora to another.  I use this
	in order to test different checkpoint models with the same set of loras.

	This probably loads the lora each time it's addressed.  Use the path_out
	to the path_in of the target loras, then enable pass_through on the target.

Sum Wrap

	An incrementor with a target (ceiling), steps to that target and what to
	revert to after reaching the target (wrap).  Negative and positive values
	can be used.  If you do your math wrong it will overshoot, that's up to you.
	
    start - where to start
    step - what to add
    ceiling - the ceiling where we return to "start"
    wrap - where to return to after hitting the ceiling
    clear - reset the stored data

    t_out - where we are now (string for convenience)
    i_out - integer output

