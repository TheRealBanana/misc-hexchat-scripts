__module_name__ = "HiLiS"
__module_version__ = "1.41"
__module_description__ = "HiLiS: Highlight Sorter"

# Highlight Sorter by Kyle Claisse.
# In X-Chat and Hexchat you have to scroll back to wherever you were highlighted to see what
# was said. This script takes all highlights and puts them into a separate tab with the date,
# time, channel, and username of the message or action that highlighted you.

#
# Ideas:
# *) Open HiLiS tabs on all servers at load to prevent unexpected focus changes when this script suddenly creates and switches to the HiLiS tab.
# *) Add option to highlight other words besides the current nickname. 


import xchat, time

def sdly(userdata):
	global startdelay, onoff
	if startdelay is not None:
		xchat.unhook(startdelay)
		startdelay = None
	onoff = "on"
	print "\00302HiLiS is now active"
	
onoff = "off"
#Wait 5 seconds before we begin watching for highlights. Sometimes scrollback can contain our username, highlighting us many
#times each time we start xchat. A delay of 5-10 seconds is enough to wait out this early period of playback.
startdelay = xchat.hook_timer(5000, sdly)

def hl_main(word, word_eol, userdata):
	if onoff == "on":
		msg_context = xchat.get_context()
		msg_chan = msg_context.get_info("channel")
		msg_server = msg_context.get_info("server")
		print_tab = xchat.find_context(server=msg_server, channel="HiLiS")
		try:
			word[2]
			rank = word[2]
		except:
			rank = ""
			
		if print_tab is None:
			msg_context.command("QUERY HiLiS")
			print_tab = xchat.find_context(server=msg_server, channel="HiLiS")
		
		event_text = userdata + " - " + msg_chan + ": \00305<\00309\002" + rank + "\017\00302" + word[0] + "\00305>\017 " + word[1]
		print_tab.prnt(event_text)
		print_tab.command("GUI COLOR 3")
	
def hiliscmd(word, word_eol, userdata):
	global onoff
	try:
		word[1]
		if word[1] == "on":
			onoff = "on"
			print "\00302HiLiS Enabled"
		elif word[1] == "off":
			onoff = "off"
			print "\00304HiLiS Disabled"
		else:
			print "Unknown command, " + str(word[1])
	except:
		print "HiLiS is " + onoff

def unload_cb(userdata):
	print "\0034 "+__module_name__+" "+__module_version__+" has been unloaded\003"

xchat.hook_print('Channel Action Hilight', hl_main, userdata="ACT")
xchat.hook_print('Channel Msg Hilight', hl_main, userdata="MSG")
xchat.hook_print('Notice', hl_main, userdata="NTC")
xchat.hook_command('hilis', hiliscmd, help="wut?")
xchat.hook_unload(unload_cb)
print "\0034 "+__module_name__+" "+__module_version__+" has been loaded\003"