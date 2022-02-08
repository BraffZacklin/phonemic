from re import finditer

class Reader():
	def __init__(self, infile, outfile="./outfile.txt"):
		self.infile = infile
		self.outfile = outfile
		self.readFile(infile)

	def readFile(self, infile):
		self.entries = []
		self.shifts = []
		self.entries_versions = []
		self.shifts_versions = []
		
		with open(infile, "r") as file:
			self.text_file = [line.strip() for line in file.readlines()]
			for line in self.text_file:
				# Sort out comments
				if line.startswith("//") or line == "":
					continue

				# Find sound changes
				elif self.__isShift(line):
					# Remove number from start of sound change
					self.shifts.append(line.split(".")[1].strip())
					
				# All others must be entries
				else:
					self.entries.append(line)

	def saveToFile(self, outfile, quit=False):
		self.applyChanges()
		# Overwrite self.text_file with new entries and shifts
		with open(outfile, "w") as file:
			for line in self.text_file:
				file.write(line + "\n")
		if not quit:
			self.readFile(self.infile)

	def save(self, quit=False):
		# Wrapper to allow saving with default filename
		self.saveToFile(self.outfile)

	def applyChanges(self):
		# Applies changes to entries and shifts to authoritative self.text_file
		if not self.shifts_versions and not self.entries_versions:
			return

		# Go through and compare oldest entries_versions with newest, any differences should be replaced in the textfile
		for original, current in zip(self.entries_versions[0], self.entries):
			if original != current:
				for index, line in enumerate(self.text_file):
					if original in line:
						self.text_file[index] = self.text_file[index].replace(original, current)
						break

		# Append space if not shifts already at bottom
		if self.text_file[-1].strip() and not self.__isShift(self.text_file):
			self.text_file.append("")

		# Save all new sound shifts at the bottom of the textfile
		for index, shift in enumerate(self.shifts, start=1):
			saved = False
			for line in self.text_file:
				if self.__isShift(line) and shift == line.split(". ")[1]:
					saved = True
					break
			if not saved:
				self.text_file.append(str(index) + ". " + shift)

	def undoChange(self):
		if self.entries_versions and self.shifts_versions:
			self.entries = self.entries_versions.pop()
			self.shifts = self.shifts_versions.pop()
		elif self.entries_versions or self.shifts_versions:
			raise BaseException("Shifts not in sync with entries")
		elif self.shifts:
			number = str(len(self.shifts))
			shift = self.shifts.pop()

			# Enact sound change backwards
			dictionary = self.getChangeDict(self.__reverseSoundChange(shift))
			self.updateEntries(dictionary, note_old=False)

			# Remove outdated lines from authoritative form
			temp_text = self.text_file[:]
			for line in self.text_file:
				if self.__isShift(line) and line.strip().startswith(number + ". "):
					temp_text.remove(line)
			self.text_file = temp_text[:]

			# Remove note of sound change from entries with sound change
			for entry in self.entries:
				entry_list = entry.split("-")
				# If the corresponding number of the sound change is in an entry...
				if len(entry_list) >= 3 and number in entry_list[2]:
					notes = entry_list[2].split(",")
					new_notes = []
					for note in notes:
						if number not in note:
							new_notes.append(note)
					entry_list[2] = ','.join(new_notes)
					self.entries[self.entries.index(entry)] = "-".join(entry_list)
			
	def getChangeDict(self, sound_changes):
		# Puts sound change string into list form to process simultanious changes
		changes_dict = {}
		sound_changes = [item.strip() for item in sound_changes.split("&") if item.strip() != ""]

		for sound_change in sound_changes:
			changes_dict[sound_change] = self.__searchEntries(sound_change)

		# Give user a chance to review changes
		return changes_dict

	def updateEntries(self, changes_dict, note_old=True):
		# Save state to allow undo
		self.entries_versions.append(self.entries[:])
		self.shifts_versions.append(self.shifts[:])

		if note_old:
			self.shifts.append(' & '.join(changes_dict))

		for key in changes_dict:
			for index in changes_dict[key]:
				self.entries[index] = self.__changeEntry(key, self.entries[index], note_old=note_old)

	def soundChange(self, sound_change, conword):
		rule, sub = self.__listConvert(sound_change)
		rule, start, end = self.__readRule(rule)

		if rule in conword:
			if start and end and conword == rule:
				conword = sub

			elif start and not end and conword.startswith(rule) and not conword.endswith(rule):
				conword = self.__pasteOver(conword, rule, sub, 0)

			elif not start and end and conword.endswith(rule) and not conword.startswith(rule):
				conword = self.__pasteOver(conword, rule, sub, len(conword) - len(rule))

			elif not start and not end:
				for match in self.__hasInside(rule, sub, conword):
					conword = self.__pasteOver(conword, rule, sub, match)
						
		return conword

	def previewChanges(self, dictionary):
		for key in dictionary:
			for index in dictionary[key]:
				old_word = self.__extractConword(self.entries[index])
				new_word = self.soundChange(key, old_word)
				yield old_word, new_word, key, index
		return None, None, None, None

	def __hasInside(self, rule, sub, conword):
		instances = [m.start() for m  in finditer(rule, conword)]
		indicies = []
		for match in instances:
			# Check to see we don't return any initial or final sounds
			if match != 0 and match+len(sub)+1 != len(conword):
				indicies.append(match)
		return indicies

	def __extractConword(self, entry_line):
		return entry_line.split("-")[1].split("//")[0].strip()

	def __pasteOver(self, word, rule, sub, start):
		segment1, segment2 = word[:start], word[start+len(rule):]
		return segment1 + sub + segment2

	def __changeEntry(self, sound_change, entry, note_old=True):
		old_word = self.__extractConword(entry)
		entry = entry.split("-")

		new_word = self.soundChange(sound_change, old_word)
		entry[1] = entry[1].replace(old_word, new_word)

		if note_old:
			if len(entry) < 3:
				entry.append("\t")
			elif entry[2].strip() != "":
				entry[2] += ", "
			entry[2] += f"{len(self.shifts)}. {old_word} > {new_word}"

		return "-".join(entry)

	def __searchEntries(self, sound_change):
		sound_change = self.__listConvert(sound_change)
		indicies = []

		for index, entry in enumerate(self.entries):
			conword = self.__extractConword(entry)
			if self.__match(sound_change[0], sound_change[1], conword):
				indicies.append(index)

		return indicies

	def __readRule(self, rule):
		# start/end = True means string must start/end with rule
		rule = rule.strip()

		start, end = False, False
		if rule[0] != "_":
			start = True
		if rule[-1] != "_":
			end = True
		
		rule = rule.replace("_", "")
		return rule, start, end		

	def __match(self, rule, sub, conword):
		rule, start, end = self.__readRule(rule)
		match = False

		if start and end and conword.startswith(rule) and conword.endswith(rule):
			match = True

		elif start and not end and conword.startswith(rule) and not conword.endswith(rule):
			match = True

		elif end and not start and conword.endswith(rule) and not conword.startswith(rule):
			match = True

		elif not start and not end and self.__hasInside(rule, sub, conword):
			match = True

		return match

	def __listConvert(self, sound_change):
		# Formats list so 0 is original sound, 1 is change
		if ">" in sound_change:
			change = [item.strip() for item in sound_change.split(">")]
			return change

		elif "<" in sound_change:
			change = [item.strip() for item in sound_change.split("<")]
			return [change[1], change[0]]

	def __reverseSoundChange(self, sound_change):
		final_list = []
		for change in sound_change.split("&"):
			change_list = self.__listConvert(change)
			sub, start, end = self.__readRule(change_list[0])
			new_rule = change_list[1]
			if not start:
				new_rule = "_" + new_rule
			if not end:
				new_rule += "_"
			final_list.append(new_rule + " > " + sub)

		return ' & '.join(final_list)

	def __isShift(self, line):
		# Should be formatted like N. [sound change rule]
		if ". " not in line:
			return False
		return line.split(". ")[0].isdigit()


def testUndo(reader):
	reader.undoChange()
	reader.save()

def testMultipleSoundChange(reader):
	sound_change = "pit > wack & _pit > wack"
	dictionary = reader.getChangeDict(sound_change)
	reader.updateEntries(dictionary)
	reader.save()

def testSoundChange(reader):
	patterns = ["_pit", "pit", "pit_", "_pit_"]
	for pattern in patterns:
		sound_change = pattern + " > wack" # looks like "pit > wack"
		dictionary = reader.getChangeDict(sound_change) # Dictionary of words that can be changed

		for old_word, new_word, key, index in reader.previewChanges(dictionary):  # Generator to display them all
			print(f"sound_change: {sound_change}, old_word: {old_word}, new_word: {new_word}") 		# 	can edit to confirm/deny

		reader.updateEntries(dictionary) # Apply all

	reader.save() # Save everything

def testEndSubs(reader):
	dictionary = reader.getChangeDict("_pit > wack & _pat > putty & _puck > pu")
	reader.updateEntries(dictionary)
	reader.save()

if __name__ == "__main__":
	reader = Reader("./test.txt")
	
	# Doing more than one test and expecting continuity but not getting it?
	#	Open the subsequent tests with Reader("./outfile.txt")
	#	Calls to 'save' reload the infile
	#	Alternatively, before the method call Reader.readFile("./outfile.txt")

	#testSoundChange(reader)
	#testMultipleSoundChange(reader)
	testEndSubs(reader)
	#reader.readFile("./outfile.txt")
	#testUndo(reader)