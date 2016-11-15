# Random color text changer by Kyle Claisse
#One of my first python scripts
__module_name__ = "RainbowText" 
__module_version__ = "1.0" 
__module_description__ = "Illuminate your text with colors" 
import xchat, random
print "\0034",__module_name__, __module_version__,"has been loaded\003"
colorset=['\00301','\00302','\00303','\00304','\00305','\00306','\00307','\00308','\00309','\00310','\00311','\00312','\00313','\00314','\00315','\00326','\00317','\00318','\00319',]

def rb_command(word, word_eol, userdata):
	result = ""
	for i in word_eol[1]:
		result = result + colorset[random.randint(0, 18)] + i
	xchat.command("say " + result)
	return xchat.EAT_ALL
	
def rbunload(userdata):
	print "\0034",__module_name__, __module_version__,"has been unloaded\003"

xchat.hook_unload(rbunload)
xchat.hook_command('rb', rb_command, help="Random Color Text")
