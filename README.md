# ComfyUI-Shinsplat
ComfyUI Node alterations that I found useful in my own projects and for friends.  At some point I'll probably make custom nodes from scratch but I started this with existing nodes and altered them to fit my needs.

# :wrench: ComfyUI Convenience Nodes

## Nodes

- Clip Text Encode (Shinsplat)
- Clip Text Encode SDXL (Shinsplat)
- Lora Loader (Shinsplat)

Clip Text Encode (Shinsplat) and Clip Text Encode SDXL (Shinsplat)

	These two nodes allow the use of the "BREAK" directive.

	During my search for nodes that break up context in a prompt I discovered
	a handful that purported to perform this task.  After utilizing all of them
	I did not get any consistent described results, from any of them.

	After deep diving into the code, and realizing I may have to write my own
	node(s), I discovered that these fancy nodes didn't do what I thought they
	should.

	As a result I chose to implement the well known BREAK directive, that so many
	seem to be using in Automatic1111, into ComfyUI myself.  I don't actually
	know how well this BREAK directive is supposed to perform, at least as far
	as a1111 is concerned, but I know what it is supposed to do and I made
	sure it does just that, breaks up prompts into blocks, ending one and
	starting another.

	While I don't see how it effects my prompts in some positive way I do
	believe it does something, though I'm not quite sure how useful it is,
	or if it is useful at all.

	As an aside, and probably a lot more important, I wanted, for quite awhile,
	to have a prompt evaluation tool so I wrote it.  Along with the block and
	token data, that is presented as a result of my attempt at the BREAK
	directive, I also implemented a prompt expander, which is a second text
	output from these two nodes, showing you exactly what the interpreter
	sees as prompts.

	I also added an "END" directive.  So often I've just wanted to alter the
	prompt at the top and skip everything else, as a quick test, but I've
	had to resort to using the to using the 'C' style block comment /*...*/,
	which is fine but inconvenient, so I can now just put my short prompt
	finish it with END and the remaining text won't be evaluated.

	I also added a "prompt" output, since I was uncertain where to find one
	that just piped the text out in order to share with other nodes.  The
	encoder doesn't receive the commented out bits since it is intercepted
	before it even gets to the node so you won't get a prompt text output
	that contains //this here .. or .. /* that there */ .  The node does not
	have access to this.  One might wonder why I didn't just use a text node
	to begin with and I would nod but also know that the ones I've used do
	not support filtering comments.

	For those who use the PonyXL models there is a "pony" switch to add the
	score data to the beginning of your prompt automatically, without having
	to type it, and it will also add the expected "BREAK" command, so the
	prepended line to your prompt will be ...

	score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, BREAK

	What I have learned, at least I think I have, is that it's best to have
	all scores included, though it can still pose a mystery and sometimes I
	find that removing lower scores can fix a broken prompt but I know that
	the issue is elsewhere.  So, if you are tired of adding this string of
	scores to your prompts you can easily just use one of my Text Encoders
	and enable the "pony" switch.

	The SDXL version of the Clip Text Encode have _g and _l input strings
	and the reason for the separation doesn't appear to be documented.  As
	a programmer I can imagine how this came to be, an uncertainty necessitated
	the presence of control features in order to test how the back-end responded
	and there was no definitive result but they thought it best to leave in
	these options, and they do alter the image in some distinct ways though
	I'm uncertain if it's valuable or not.  As a result I've put the pony
	switch on both _g and _l terms.  What I have noticed, however, is if you
	use the same prompt criteria in both _g and _l text areas you get the same
	result as if you had used the simple Clip Text Encoder, if using the
	default resolutions, which duplicates the _l into _g on the back-end.

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

Lora Loader (Shinsplat)

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
	other is the entirety of the meta-data, which could be huge	or almost nothing
	at all.

	I see a growing trend, or maybe it's a default feature, of meta-data being
	stripped, or simply not included, in these files and I hope that will change
	in the future so that we always have a way to identify trigger phrases.
