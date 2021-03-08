import fileinput
import subprocess

def noteToFreq(note):
    baseFreq = 440 #frequency of A4
    frequency = (baseFreq / 32) * (2 ** ((note - 9) / 12))
    return frequency

def printFormat(notes):
	with open('pythontest.txt', 'w') as f:
		filestring = "<CsoundSynthesizer>\n\n" + \
		"\t<CsOptions>\n\n" + \
		"\t</CsOptions>\n" + \
		"\t<CsInstruments>\n\n" + \
		"\tsr = 44100\n" + \
		"\tnchnls = 2\n" + \
		"\t0dbfs = 1\n\n" + \
		"\tinstr 1\n\n" + \
		"\t\tiFreq = p4\n" + \
		"\t\tiAmp = p5\n" + \
		"\t\tiAtt = 0.1\n" + \
		"\t\tiDec = 0.4\n" + \
		"\t\tiSus = 0.6\n" + \
		"\t\tiRel = 0\n" + \
		"\t\tkEnv madsr iAtt, iDec, iSus, iRel\n" + \
		"\t\taOut vco2 iAmp, iFreq\n" + \
		"\t\tout aOut*kEnv\n\n" + \
		"\tendin\n\n" + \
		"\t</CsInstruments>\n" + \
		"\t<CsScore>\n\n"
		notenum = 0
		optionsentinel = True
		bpm = 0
		currenttime = 0
		for l in fileinput.input():
			line = l.split()
			if optionsentinel:
				bpm = int(line[0])
				optionsentinel = False
			else:
				notelength = (60/bpm) * float(line[2])
				filestring = filestring + "\t\ti " + line[0] + " " + str(currenttime) + " " + str(notelength) + " " + str(noteToFreq(int(line[1]))) + " " + str(1) + "\n"
				currenttime += notelength
				notenum += 1
		filestring = filestring + "\n\t</CsScore>\n" + \
		"</CsoundSynthesizer>"
		f.write(filestring)
		f.close()
		

printFormat(1);
subprocess.call(['csound', 'C:\\Users\\pixel\\csound\\pythontest.txt'])
