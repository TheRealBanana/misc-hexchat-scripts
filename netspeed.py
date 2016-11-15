# netspeed printer using psutil
# September 2016
# Kyle Claisse

__module_name__ = "Network Speed Indicator" 
__module_version__ = "1.0" 
__module_description__ = "Prints out average network interface speed over the last 2 seconds" 

print "\0034" + __module_name__, __module_version__,"has been loaded\003"

import xchat
from time import sleep
from psutil import net_io_counters as psutil_net_io_counters
from collections import OrderedDict as OD
import threading



multis = OD()
multis[1] = "Bytes/s"
multis[1024] = "KiB/s"
multis[1024**2] = "MiB/s"
multis[1024**3] = "GiB/s"
sample_time = 0.5 #The longer your sample time the more accurate the results will be


class Netspeed(threading.Thread):
    def __init__(self):
        self.sstart = psutil_net_io_counters(pernic=False)[0]
        self.rstart = psutil_net_io_counters(pernic=False)[1]
        super(Netspeed, self).__init__()
    
    def run(self):
        #Here we take two samples self.sample_time seconds apart and get an average network speed over time
        s_accum = 0
        r_accum = 0
        sleep(sample_time)
        s_accum += (psutil_net_io_counters(pernic=False)[0] - self.sstart)
        r_accum += (psutil_net_io_counters(pernic=False)[1] - self.rstart)
        s_persec = float(s_accum) / sample_time
        r_persec = float(r_accum) / sample_time
        #Now we figure out the multiplier and affix
        for m, affix in multis.iteritems():
            if int(s_persec) > int(m):
                saffix = affix
                smulti = float(m)
            if int(r_persec) > int(m):
                raffix = affix
                rmulti = float(m)
        sfinal = s_persec / smulti
        rfinal = r_persec / rmulti
        stext = "Up: %.2f %s" % (sfinal, saffix)
        rtext = "Down: %.2f %s" % (rfinal, raffix)
        final_output = "%s  --  %s" % (rtext, stext)
        xchat.command("SAY %s" % final_output)


def netspeed(word, word_eol, userdata):
    #Warn the user this will take some time if the sample_time is more than 1 second
    if sample_time > 1: print "Collecting network stats, this will take %.2f seconds" % sample_time
    ns = Netspeed()
    ns.start()
    
xchat.hook_command('netspeed', netspeed)

def rbunload(userdata):
    print "\0034" + __module_name__, __module_version__,"has been unloaded\003"

xchat.hook_unload(rbunload)