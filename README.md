# phonemic

This is a tool designed to help with sound changes. See the example file for help, or the CLI -h help menu.
This tool has been designed to have minimal required functionality and not much else; more may be added later as I see fit (one such idea is an interactive mode), but this is dependant on me seeing a need for it in my own conlanging. 

# Installation

Installation is as simple as running 'git clone https://github.com/BraffZacklin/phonemic', however if you're running Linux I would recommend creating a symlink to the tool. If you clone the repo to \~/bin as phonemic.dir, and run 'ln -s phonemic.dir/cli.py phonemic', when you next reload your terminal you should be able to run it directly from command line in any directory with simply 'phonemic'

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

Some examples of sound changes and their effects would be:

- "pit > wack"

pit > wack  
pity unchanged  
spit unchanged  
spittle unchanged  

- "\_pit > wack"

spit > swack  
pit unchanged, etc.

- "pit_ > wack"

pity > wacky

- "pit > wack & \_pit\_ > wack"

pit > wack AND spittle > swacktle (counted as one change)

# CLI

Argparse has provided a help menu for the CLI tool; the CLI tool is barebones for now. 
The only required argument is the infile; if an outfile (which can be the same as your infile, if you're brave enough) is not supplied, you will be asked later. For convenience, below are the possible arguments:

- Infile -- positional, and required
- -o -- outfile, where to save output to
- -s -- save to input, set outfile to the same as infile
- -c -- sound change to execute
- -u -- undo, undoes the last sound change
- -e -- explicit, when asked to confirm a given sound change, do not (as is default) take a blank response as affirmative, but rather repeatedly nag until either a 'y' or 'n' is given.

Note that using -c (sound change) and -u (undo) together will result in the last sound change being undone, and the given sound change being applied.

# To-Do
1. Add CLI
2. Add CLI to README.md
3. Allow comments after words and sound changes
4. Add explicit check for entries as opposed to current assumption model