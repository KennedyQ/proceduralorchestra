import generatecsound as CSound
import os
import subprocess

if (__name__ == "__main__"):
	currentdirectory = os.getcwd()
	notefilename = "pythoninput.txt"
	csoundfilename = "pythontest.txt"
	generator = CSound.ProceduralOrchestra()
	soprano = CSound.Performer(60,79,.45,.45,1.05,72,False,[2,2,1,2,2,2,1],False)
	alto = CSound.Performer(55,72,.1,.1,2,60,True,[2,2,1,2,2,2,1],True,1)
	tenor = CSound.Performer(48,67,.1,.1,2,60,True,[2,2,1,2,2,2,1],True,1)
	bass = CSound.Performer(41,60,.1,.1,2,48,True,[2,2,1,2,2,2,1],True,1)
	orchestra = [soprano, alto, tenor, bass]
	generator.generateNoteString(notefilename, 120, 240, orchestra)
	generator.printFormat(csoundfilename, notefilename, orchestra)
	subprocess.call(['csound', currentdirectory+"\\"+csoundfilename])