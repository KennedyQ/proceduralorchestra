import os
import subprocess
import random

class Performer():
	def __init__(self, minimumnote, maximumnote, chancetodecrease, chancetoincrease, sequencemodifier, startingnote, followprevious):
		self.minimumnote = minimumnote
		self.maximumnote = maximumnote
		self.chancetodecrease = chancetodecrease
		self.chancetoincrease = chancetoincrease
		self.sequencemodifier = sequencemodifier
		self.startingnote = startingnote
		self.followprevious = followprevious

def noteToFreq(note):
    a = 440 #frequency of A4 (common value is 440Hz)
    return (a / 32) * (2 ** ((note - 9) / 12))

def generateNoteString(filename, bpm, length, instruments):
	with open(filename, 'w') as f:
		durations = [0.5, 1, 2, 4]
		savednotelengths = ""
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
			note = instrument.startingnote
			random.seed()
			i = 0
			cumuldur = 0
			while cumuldur < length:
				r = random.random()
				if (sequence > 0):
					if (r <= chancetodecrease*(sequencemodifier**sequence)):
						new = note - random.randrange(1,5)
						if (new < minnote):
							note = minnote
						else:
							note = new
						sequence = -1
					elif (r <= chancetoincrease+chancetodecrease):
						new = note + random.randrange(1,5)
						if (new > maxnote):
							note = maxnote
							sequence = 15
						else:
							note = new
							sequence += 1
				elif (sequence < 0):
					if (r <= chancetoincrease*(sequencemodifier**(-1*sequence))):
						new = note + random.randrange(1,5)
						if (new > maxnote):
							note = maxnote
						else:
							note = new
						sequence = 1
					elif (r <= chancetoincrease+chancetodecrease):
						new = note - random.randrange(1,5)
						if (new < minnote):
							note = minnote
							sequence = -15
						else:
							note = new
							sequence -= 1
				else:
					if (r <= chancetodecrease):
						new = note - random.randrange(1,5)
						if (new < minnote):
							note = minnote
						else:
							note = new
						sequence = -1
					elif (r <= chancetoincrease+chancetodecrease):
						new = note + random.randrange(1,5)
						if (new > maxnote):
							note = maxnote
						else:
							note = new
						sequence = 1
				if (not instrument.followprevious):
					durrand = random.randrange(0,4)
					while (durations[durrand] + cumuldur > length):
						durrand = random.randrange(0,4)
					filestring += str(instrumentid) + " " + str(note) + " " + str(durations[durrand])
					savednotelengths += str(durrand)
					cumuldur += durations[durrand]
				else:
					filestring += str(instrumentid) + " " + str(note) + " " + str(durations[int(savednotelengths[i])])
					cumuldur += durations[int(savednotelengths[i])]
				if (not cumuldur == length):
					filestring += "\n"
				i += 1
			instrumentid += 1
		f.write(filestring)
		f.close()
					
def printFormat(csoundfilename, notefile, instruments):
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
			"\t\touts aOut*kEnv, aOut*kEnv\n\n" + \
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
				filestring = filestring + "\t\ti " + line[0] + " " + str(currenttime) + " " + str(notelength) + " " + str(noteToFreq(int(line[1]))) + " " + str(1) + "\n"
				currenttime += notelength
				notenum += 1
		filestring = filestring + "\n\t</CsScore>\n" + \
		"</CsoundSynthesizer>"
		f.write(filestring)
		f.close()
		
if (__name__ == "__main__"):
	currentdirectory = os.getcwd()
	notefilename = "pythoninput.txt"
	csoundfilename = "pythontest.txt"
	testInstrument = Performer(40,64,.45,.45,1.05,52,False)
	testInstrument2 = Performer(16,40,.45,.45,1.05,28,False)
	testInstrument3 = Performer(28,52,.45,.45,1.05,40,True)
	orchestra = [testInstrument, testInstrument3, testInstrument2]
	generateNoteString(notefilename, 120, 240, orchestra)
	printFormat(csoundfilename, notefilename, orchestra)
	subprocess.call(['csound', currentdirectory+"\\"+csoundfilename])
