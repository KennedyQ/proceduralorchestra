import os
import subprocess
import random
import fileinput

class Performer():
	def __init__(self, minimumnote, maximumnote, chancetodecrease, chancetoincrease, sequencemodifier, startingnote, followprevioustempo, mode, harmonize, harmonizationmode = 0):
		self.minimumnote = minimumnote
		self.maximumnote = maximumnote
		self.chancetodecrease = chancetodecrease
		self.chancetoincrease = chancetoincrease
		self.sequencemodifier = sequencemodifier
		self.startingnote = startingnote
		self.followprevioustempo = followprevioustempo
		self.mode = self.enumMode(mode)
		self.key = self.keygen()
		self.harmonize = harmonize
		self.harmonizationmode = harmonizationmode

	def __str__(self):
		printstr = ""
		printstr += str(self.minimumnote) + ", "
		printstr += str(self.maximumnote) + ", "
		printstr += str(self.chancetodecrease) + ", "
		printstr += str(self.chancetoincrease) + ", "
		printstr += str(self.sequencemodifier) + ", "
		printstr += str(self.startingnote) + ", "
		printstr += str(self.followprevioustempo) + ", "
		printstr += str(self.mode) + ", "
		printstr += str(self.harmonize) + ", "
		printstr += str(self.harmonizationmode)
		return printstr

	def enumMode(self, mode):
		if (mode == "Major" or mode == "Ionian"):
			return [2,2,1,2,2,2,1]
		elif (mode == "Dorian"):
			return [2,1,2,2,2,1,2]
		elif (mode == "Phrygian"):
			return [1,2,2,2,1,2,2]
		elif (mode == "Lydian"):
			return [2,2,2,1,2,2,1]
		elif (mode == "Mixolydian"):
			return [2,2,1,2,2,1,2]
		elif (mode == "Minor" or mode == "Aeolian"):
			return [2,1,2,2,1,2,2,]
		elif (mode == "Locrian"):
			return [1,2,2,1,2,2,2]

	def keygen(self):
		key = []
		note = self.startingnote
		modeindex = 6
		while(True):
			if(note - self.mode[modeindex] >= self.minimumnote):
				note -= self.mode[modeindex]
			else:
				break
			if(modeindex - 1 >= 0):
				modeindex -= 1
			else:
				modeindex = 6
		modeindex += 1
		modeindex = modeindex%7
		while(note <= self.maximumnote):
			key.append(note)
			note += self.mode[modeindex]
			modeindex += 1
			modeindex = modeindex%7
		note = note%self.maximumnote
		note += self.minimumnote
		return key

class ProceduralOrchestra():

	def noteToFreq(self, note):
   		a = 440 #frequency of A4 (common value is 440Hz)
  	 	return (a / 32) * (2 ** ((note - 9) / 12))

	def generateNoteString(self, filename, bpm, length, instruments):
		with open(filename, 'w') as f:
			durations = [0.5, 1, 2, 4]
			savednotelengths = {}
			savednotes = []
			newsavednotes = []
			previouskey = []
			instrumentid = 1
			filestring = str(bpm) + "\n"
			for instrument in instruments:
				if (instrumentid > 1):
					filestring += "\n"
				sequence = 0
				minnote = instrument.minimumnote
				maxnote = instrument.maximumnote
				chancetodecrease = instrument.chancetodecrease
				chancetoincrease = instrument.chancetoincrease
				sequencemodifier = instrument.sequencemodifier
				note = instrument.key.index(instrument.startingnote)
				keymax = len(instrument.key) - 1
				random.seed()
				i = 0
				cumuldur = 0
				if (not instrument.harmonize):
					while cumuldur < length:
						r = random.random()
						if (sequence > 0):
							if (r <= chancetodecrease*(sequencemodifier**sequence)):
								new = note - random.randrange(1,4)
								if (new < 0):
									note = 0
								else:
									note = new
								sequence = -1
							elif (r <= chancetoincrease+chancetodecrease):
								new = note + random.randrange(1,4)
								if (new > keymax):
									note = keymax
									sequence = 15
								else:
									note = new
									sequence += 1
						elif (sequence < 0):
							if (r <= chancetoincrease*(sequencemodifier**(1*sequence))):
								new = note + random.randrange(1,5)
								if (new > keymax):
									note = keymax
								else:
									note = new
								sequence = 1
							elif (r <= chancetoincrease+chancetodecrease):
								new = note - random.randrange(1,5)
								if (new < 0):
									note = 0
									sequence = -15
								else:
									note = new
									sequence -= 1
						else:
							if (r <= chancetodecrease):
								new = note - random.randrange(1,5)
								if (new < 0):
									note = 0
								else:
									note = new
								sequence = -1
							elif (r <= chancetoincrease+chancetodecrease):
								new = note + random.randrange(1,5)
								if (new > keymax):
									note = keymax
								else:
									note = new
								sequence = 1
						noteduration = self.selectDuration(instrument, durations, savednotelengths, cumuldur, length)
						if (cumuldur + noteduration == length):
							note = instrument.key.index(instrument.startingnote)
						filestring += str(instrumentid) + " " + str(instrument.key[note]) + " " + str(noteduration)
						cumuldur += noteduration
						newsavednotes.append([instrument.key[note], cumuldur])
						if (not cumuldur == length):
							filestring += "\n"
						i += 1
				elif (instrument.harmonizationmode == 1):
					harmony = [0,2,4,7]
					mergedkey = self.mergekeys(previouskey, instrument.key)
					while cumuldur < length:
						j = 0
						while(cumuldur > savednotes[j][1]):
							j += 1
						lastkeynote = mergedkey.index(savednotes[j][0])
						mykeynote = mergedkey.index(instrument.key[note])
						r = random.random()
						if (sequence > 0):
							if (r <= chancetodecrease*(sequencemodifier**sequence)):
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote -= 1
								harmonyindex = harmony.index((lastkeynote - mykeynote) % 7)
								new = lastkeynote - ((lastkeynote - mykeynote) + (harmony[harmonyindex+1] - harmony[harmonyindex]))
								while(new < 0):
									new += (harmony[harmonyindex+1] - harmony[harmonyindex])
									harmonyindex -= 1
									if (harmonyindex < 0):
										harmonyindex = len(harmony)-2
								note = new
								sequence = -1
							elif (r <= chancetoincrease+chancetodecrease):
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote += 1
								harmonyindex = harmony.index((lastkeynote - mykeynote) % 7)
								if (harmonyindex == 0):
									new = lastkeynote
								else:
									new = lastkeynote - ((lastkeynote - mykeynote) - (harmony[harmonyindex] - harmony[harmonyindex-1]))
								while(new >= len(instrument.key)):
									new -= (harmony[harmonyindex] - harmony[harmonyindex-1])
									harmonyindex += 1
									harmonyindex = harmonyindex%len(harmony)
									if (harmonyindex == 0):
										harmonyindex = 1
								note = new
								sequence += 1
							else:
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote += 1
								new = lastkeynote - (lastkeynote - mykeynote)
								while(new < 0):
									new += (harmony[harmonyindex+1] - harmony[harmonyindex])
									harmonyindex -= 1
									if (harmonyindex < 0):
										harmonyindex = len(harmony)-2
								while(new >= len(instrument.key)):
									new -= (harmony[harmonyindex] - harmony[harmonyindex-1])
									harmonyindex += 1
									harmonyindex = harmonyindex%len(harmony)
									if (harmonyindex == 0):
										harmonyindex = 1
								note = new
						elif (sequence < 0):
							if (r <= chancetoincrease*(sequencemodifier**(1*sequence))):
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote += 1
								harmonyindex = harmony.index((lastkeynote - mykeynote) % 7)
								if (harmonyindex == 0):
									new = savednotes[j][0]
								else:
									new = savednotes[j][0] - ((lastkeynote - mykeynote) - (harmony[harmonyindex] - harmony[harmonyindex-1]))
								while(new >= len(instrument.key)):
									new -= (harmony[harmonyindex] - harmony[harmonyindex-1])
									harmonyindex += 1
									harmonyindex = harmonyindex%len(harmony)
									if (harmonyindex == 0):
										harmonyindex = 1
								note = new
								sequence = 1
							elif (r <= chancetoincrease+chancetodecrease):
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote -= 1
								harmonyindex = harmony.index((lastkeynote - mykeynote) % 7)
								while(new < 0):
									new += (harmony[harmonyindex+1] - harmony[harmonyindex])
									harmonyindex -= 1
									if (harmonyindex < 0):
										harmonyindex = len(harmony)-2
								note = new
								sequence -= 1
							else:
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote += 1
								new = lastkeynote - (lastkeynote - mykeynote)
								while(new < 0):
									new += (harmony[harmonyindex+1] - harmony[harmonyindex])
									harmonyindex -= 1
									if (harmonyindex < 0):
										harmonyindex = len(harmony)-2
								while(new >= len(instrument.key)):
									new -= (harmony[harmonyindex] - harmony[harmonyindex-1])
									harmonyindex += 1
									harmonyindex = harmonyindex%len(harmony)
									if (harmonyindex == 0):
										harmonyindex = 1
								note = new
						else:
							if (r <= chancetodecrease):
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote -= 1
								harmonyindex = harmony.index((lastkeynote - mykeynote) % 7)
								new = lastkeynote - ((lastkeynote - mykeynote) + (harmony[harmonyindex+1] - harmony[harmonyindex]))
								while(new < 0):
									new += (harmony[harmonyindex+1] - harmony[harmonyindex])
									harmonyindex -= 1
									if (harmonyindex < 0):
										harmonyindex = len(harmony)-2
								note = new
								sequence = -1
							elif (r <= chancetoincrease+chancetodecrease):
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote += 1
								harmonyindex = harmony.index((lastkeynote - mykeynote) % 7)
								if (harmonyindex == 0):
									new = lastkeynote
								else:
									new = lastkeynote - ((lastkeynote - mykeynote) - (harmony[harmonyindex] - harmony[harmonyindex-1]))
								while(new >= len(instrument.key)):
									new -= (harmony[harmonyindex] - harmony[harmonyindex-1])
									harmonyindex += 1
									harmonyindex = harmonyindex%len(harmony)
									if (harmonyindex == 0):
										harmonyindex = 1
								note = new
								sequence = 1
							else:
								while(((lastkeynote - mykeynote) % 7) not in harmony):
									mykeynote += 1
								new = lastkeynote - (lastkeynote - mykeynote)
								while(new < 0):
									new += (harmony[harmonyindex+1] - harmony[harmonyindex])
									harmonyindex -= 1
									if (harmonyindex < 0):
										harmonyindex = len(harmony)-2
								while(new >= len(instrument.key)):
									new -= (harmony[harmonyindex] - harmony[harmonyindex-1])
									harmonyindex += 1
									harmonyindex = harmonyindex%len(harmony)
									if (harmonyindex == 0):
										harmonyindex = 1
								note = new
						noteduration = self.selectDuration(instrument, durations, savednotelengths, cumuldur, length)
						if (cumuldur + noteduration == length):
							note = instrument.key.index(instrument.startingnote)
						filestring += str(instrumentid) + " " + str(instrument.key[note]) + " " + str(noteduration)
						cumuldur += noteduration
						newsavednotes.append([instrument.key[note], cumuldur])
						if (not cumuldur == length):
							filestring += "\n"
						i += 1
				savednotes = newsavednotes
				newsavednotes = []
				previouskey = instrument.key
				instrumentid += 1
			f.write(filestring)
			f.close()

	def mergekeys(self, keyA, keyB):
		lenA = len(keyA)
		lenB = len(keyB)
		newkey = []
		if (keyA[lenA-1] > keyB[lenB-1]):
			if keyA[0] < keyB[0]:
				return keyA
			else:
				newkey = keyB[0:keyB.index(keyA[0])] + keyA[::]
		else:
			if keyB[0] < keyA[0]:	
				return keyB
			else:
				newkey = keyA[0:keyA.index(keyB[0])] + keyB[::]
		return newkey
					
	def printFormat(self, csoundfilename, notefile, instruments):
		with open(csoundfilename, 'w') as f:
			filestring = "<CsoundSynthesizer>\n\n" + \
			"\t<CsOptions>\n\n" + \
			"\t</CsOptions>\n" + \
			"\t<CsInstruments>\n\n" + \
			"\tsr = 44100\n" + \
			"\tnchnls = 2\n" + \
			"\t0dbfs = 1\n\n"
			instrumentid = 1
			for instrument in instruments:
				filestring += "\tinstr " + str(instrumentid) + "\n\n" + \
				"\t\tiFreq = p4\n" + \
				"\t\tiAmp = p5\n" + \
				"\t\tiAtt = 0.1\n" + \
				"\t\tiDec = 0.4\n" + \
				"\t\tiSus = 0.6\n" + \
				"\t\tiRel = 0.01\n" + \
				"\t\tkEnv madsr iAtt, iDec, iSus, iRel\n" + \
				"\t\taOut vco2 iAmp, iFreq\n" + \
				"\t\touts aOut*kEnv*.1, aOut*kEnv*.1\n\n" + \
				"\tendin\n\n"
				instrumentid += 1
			filestring += "\t</CsInstruments>\n" + \
			"\t<CsScore>\n\n"
			notenum = 0
			optionsentinel = True
			bpm = 0
			currenttime = 0
			currentinstrument = 1
			notestring = open(notefile, 'r')
			notestringlines = notestring.readlines()
			notestring.close()
			for l in notestringlines:
				line = l.split()
				if optionsentinel:
					bpm = int(line[0])
					optionsentinel = False
				else:
					if (not currentinstrument == line[0]):
						currentinstrument = line[0]
						currenttime = 0
					notelength = (60/bpm) * float(line[2])
					filestring = filestring + "\t\ti " + line[0] + " " + str(currenttime) + " " + str(notelength) + " " + str(self.noteToFreq(int(line[1]))) + " " + str(1) + "\n"
					currenttime += notelength
					notenum += 1
			filestring = filestring + "\n\t</CsScore>\n" + \
			"</CsoundSynthesizer>"
			f.write(filestring)
			f.close()

	def selectDuration(self, instrument, durations, savedDurations, currentDur, piecelength):
		if (not instrument.followprevioustempo):
			durrand = random.randrange(0,4)
			selectedDur = durations[durrand]
			while (selectedDur + currentDur > piecelength):
				durrand = random.randrange(0,4)
				selectedDur = durations[durrand]
			savedDurations[currentDur] = selectedDur
			return selectedDur
		else:
			return savedDurations[currentDur]
		
if (__name__ == "__main__"):
	currentdirectory = os.getcwd()
	notefilename = "pythoninput.txt"
	csoundfilename = "pythontest.txt"
	generator = ProceduralOrchestra()
	orchestra = []
	settingsSentinel = False
	bpm = 0
	duration = 0
	for l in fileinput.input():
		inputs = l.split(",")
		if (not settingsSentinel):
			bpm = int(inputs[0])
			duration = int(inputs[1])
			settingsSentinel = True
		else:
			if (len(inputs) > 9):
				harmonymode = int(inputs[9])
			else:
				harmonymode = 0
			if (inputs[6] == "True"):
				rhythmbool = True
			else:
				rhythmbool = False
			if (inputs[8] == "True"):
				harmonybool = True
			else:
				harmonybool = False
			newinstrument = Performer(int(inputs[0]),int(inputs[1]),float(inputs[2]),float(inputs[3]),float(inputs[4]),int(inputs[5]),rhythmbool,inputs[7],harmonybool,harmonymode)
			orchestra.append(newinstrument)
	generator.generateNoteString(notefilename, bpm, duration, orchestra)
	generator.printFormat(csoundfilename, notefilename, orchestra)
	subprocess.call(['csound', currentdirectory+"\\"+csoundfilename])
