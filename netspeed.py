# netspeed printer using psutil
# September 2016
# Kyle Claisse
__module_name__ = "Network Speed Indicator" 
__module_version__ = "1.2" 
__module_description__ = "Prints out average network interface speed" 

print "\0034" + __module_name__, __module_version__,"has been loaded\003"

import xchat
from time import sleep
from psutil import net_io_counters as psutil_net_io_counters
from collections import OrderedDict as OD
import threading

#Decided against reordering. Would have had to split the check loop at lines 42-48 into
#two separate loops. This could have theoretically improved the number of checks to just
#two but at worst it could require 8 checks. Whereas the current implementation always
#requires 4 checks, no more and no less. I think on average, this way is better.
multis = OD()
multis[1] = "Bytes/s"
multis[1024] = "KiB/s"
multis[1024**2] = "MiB/s"
multis[1024**3] = "GiB/s"

sample_time = 0.5 #The longer your sample time the more accurate the results will be. Value is in seconds.

class Netspeed(threading.Thread):
    def __init__(self, output_mode):
        self.output_mode = output_mode
        super(Netspeed, self).__init__()
    
    def run(self):
        #Here we take two samples self.sample_time seconds apart and get an average network speed over time
        tx_start = psutil_net_io_counters(pernic=False)[0]
        rx_start = psutil_net_io_counters(pernic=False)[1]
        sleep(sample_time)
        tx_accum = (psutil_net_io_counters(pernic=False)[0] - tx_start)
        rx_accum = (psutil_net_io_counters(pernic=False)[1] - rx_start)
        tx_persec = float(tx_accum) / sample_time
        rx_persec = float(rx_accum) / sample_time
        #Now we figure out the multiplier and affix
        for m, affix in multis.iteritems():
            if int(tx_persec) > int(m):
                tx_affix = affix
                tx_multi = float(m)
            if int(rx_persec) > int(m):
                rx_affix = affix
                rx_multi = float(m)
        tx_final = tx_persec / tx_multi
        rx_final = rx_persec / rx_multi
        tx_text = "Up: %.2f %s" % (tx_final, tx_affix)
        rx_text = "Down: %.2f %s" % (rx_final, rx_affix)
        final_output = "%s  --  %s" % (rx_text, tx_text)
        if self.output_mode == "say":
            xchat.command("SAY %s" % final_output)
        else:
            print(final_output)


def netspeed(word, word_eol, userdata):
    #Warn the user this will take some time if the sample_time is more than 1 second
    if sample_time > 1: print "Collecting network stats, this will take %.2f seconds" % sample_time
    #Are these thread object piling up with every use??
    #Should be be .join()'ing them? Maybe we reuse some global Netspeed object to make sure each thread always gets reused.
    ns = Netspeed(userdata)
    ns.start()
    ns.join()
    return xchat.EAT_ALL
    
xchat.hook_command('netspeed', netspeed, userdata="say")
xchat.hook_command('pnetspeed', netspeed, userdata="print")

def rbunload(userdata):
    print "\0034" + __module_name__, __module_version__,"has been unloaded\003"

xchat.hook_unload(rbunload)
