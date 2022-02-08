# phonemic

This is a tool designed to help with sound changes. See the example file for help, or the CLI -h help menu.

# text file syntax

This tool specifically works with a pre-defined format for text files. Fortunately, it's not too complicated.

There are 3 particular symbols that the text file format uses:

- "-": used to separate parts of an entry, which must be at least a gloss and a word arranged like "gloss - word", and previous versions of a word are noted after a second tac, "gloss - word - older versions", where the older versions have a number indicating what sound change they belong to and show the old word and the new word, e.g. "1. ursus < hrktos", of which there may be multiple separated by commas
- "N.": used to indicate sound changes chronologically 
- "//": used to designate comments at the start of a line; attaching them elsewhere may produce weird functionality; adding comments after a gloss should be safe as these are never read, adding comments after a word may result in the comment being sound-change'd, adding them after the older versions notes or the sound change notes may also result in this.

These above symbols should not be used anywhere in your gloss. 

Apart from comments, which are saved and ignored, there are two other types of lines in the textfile: sound change notes, which are defined as starting with N. (that is, a number like 128 and a full stop), and entries, which right now is everything not a comment or a sound change note -- the program expects entries to contain at least one tac "-", before which is the gloss (e.g. 2SG) and after which is the word (e.g. "You").

# Sound Changes

As mention above, sound changes have a specific format. The symbols used in sound changes are as follows:

- ">" or "<": used to indicate direction of a sound change
- "\_": used as a wildcard, e.g. "\_pit > wack" indicates changing any words ending in 'pit' to end in 'wack' -- this sound change would leave words like 'pit', 'pity', and 'spittle' unchanged, but would change 'spit' to 'swack'.
- "&": indicates multiple simultanious sound changes

# CLI

TBA

# To-Do
1. Add CLI
2. Add CLI to README.md
3. Allow comments after words and sound changes
4. Add explicit check for entries as opposed to current assumption model