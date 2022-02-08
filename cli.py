from reader import Reader
import argparse

def nagBool(message, explicit=False):
	while True:
		response = input(message).strip()
		if response == "" and not explicit:
			return True

		response = response.lower()
		
		if response[0] == "n":
			return False
		elif response[0] == "y":
			return True 

def nagStr(message):
	while True:
		response = input(message).strip()
		if response != "":
			return response

parser = argparse.ArgumentParser(description="Perform sound changes on text files")
parser.add_argument('infile', type=str, help="a file to read from")
parser.add_argument('-o', metavar="OUTFILE", dest='outfile', type=str, help="a file to write to")
parser.add_argument('-c', metavar="SOUND_CHANGE", dest='sound_change', type=str, help="a sound change to enact")
parser.add_argument('-u', dest='undo', action='store_const', const=True, default=False, help="Undo previous sound change")
parser.add_argument('-e', dest='explicit', action='store_const', const=True, default=False, help="Don't treat blank response as 'yes' for transformation confirmation")
parser.add_argument('-s', dest='save_to_input', action='store_const', const=True, default=False, help="Set the outfile to the same as the infile")
args = parser.parse_args()

reader = Reader(args.infile)
changed = False

if args.undo:
	reader.undoChange()
	changed = True

if args.sound_change:
	dictionary = reader.getChangeDict(args.sound_change)
	dict_copy = dictionary.copy()

	for old_word, new_word, sound_change, index in reader.previewChanges(dictionary):
		print(f"sound_change: {sound_change}, old_word: {old_word}, new_word: {new_word}")
		acceptable = nagBool("Is the above transformation acceptable? [Y/N]: ", explicit=args.explicit)
		if not acceptable:
			sub = nagStr("Okay, what do you suggest, smart guy?: ")
			print("Y'know I could've thought of that too...")
			# remove old reference in dictionary
			dict_copy[sound_change].remove(index)
			if not dict_copy[sound_change]:
				dict_copy.pop(sound_change)
			# add specific word-to-word substitution 
			dict_copy[old_word + " > " + sub] = [index]

	reader.updateEntries(dict_copy)
	changed = True

if changed:
	if args.save_to_input:
		outfile = args.infile
	elif not args.outfile:
		outfile = nagStr("Enter path to outfile: ")
	else:
		outfile = args.outfile
	reader.saveToFile(outfile, quit=True)