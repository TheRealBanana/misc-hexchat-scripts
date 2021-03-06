__module_name__ = "QiGen"
__module_version__ = "1.6"
__module_description__ = "Now Playing Quick Gen for MPC-HC"

# QiGen by Kyle Claisse
# For X-Chat v2.8.6 and up
# Requires: X-Chat Python Interface 0.8p1/2.6 or better
# Tested and working with Hexchat 2.10.2 and MPC-HC 1.7.10 as of March 2016.



print "\0034 "+__module_name__+" "+__module_version__+" has been loaded\003"

import re, locale, urllib2, xchat, sys

#MAKE SURE YOU HAVE MediainfoDLL.py in the same directory as this script and MediaInfo.dll in xchat's main folder!
dir = xchat.get_info("xchatdir")
sys.path.append(dir)
from MediaInfoDLL import *

################################
########### MPC INFO ###########
################################
MPC_address = "127.0.0.1"
MPC_port = "13579"
################################
########### MPC INFO ###########
################################

VIDEO_EXTENSIONS = ".avi .divx .amv .mpg .mpeg .mpe .m1v \
                   .m2v .mpv2 .mp2v .m2p .vob .evo .mod \
                   .ts .m2ts .m2t .mts .pva .tp .tpr .mp4 \
                   .m4v .mp4v .mpv4 .hdmov .mov .3gp .3gpp \
                   .3g2 .3gp2 .mkv .webm .ogm .ogv .flv .f4v \
                   .wmv .rmvb .rm .dv"

#Set locale to english united states so we can format numbers properly.
try:
    locale.setlocale(locale.LC_ALL, "en_US")
except:
    try:
        locale.setlocale(locale.LC_ALL, "US")
    
    finally:
        pass

color = {"white":"\00300", "black":"\00301", "lblue":"\00302", "green":"\00303", "red":"\00304",
"dred":"\00305", "purple":"\00306", "dyellow":"\00307", "yellow":"\00308", "bgreen":"\00309",
"dgreen":"\00310", "lgreen":"\00311", "lblue":"\00312", "bpurple":"\00313", "dgrey":"\00314",
"lgrey":"\00315", "closec":"\003", "closea":"\017", "closeb":"\002", "bold":"\002"}


PAGE_URL = "http://" + MPC_address + ":" + MPC_port + "/variables.html"

def qi_start(word, word_eol, userdata):
    context = xchat.get_context()
    channel = context.get_info('channel')
    MI = MediaInfo()
    
    # First thing we need to do is find out the filename/directory of the currently playing video.
    # To do this we will grab info from Media Player Classic's WebUI
    
    #This will return a list of 2 values
    # file_infos[0] = the directory the file is in
    # file_infos[1] = The filename
    file_infos = find_file()
    if file_infos is not None:
        #Check if the file is a video file
        print file_infos
        #Consider breaking the re.match/var assignment up from the .group() function use.
        #Instead, after running re.match, check if the result is None before accessing the group() function.
        #This would avoid a potential exception
        extension = re.match("^.*?\.([a-zA-Z0-9]{2,4})$", file_infos[0]).group(1)
        if extension not in VIDEO_EXTENSIONS:
            print color["red"] + "The file currently being played by MPC-HC is not a recognized video file. If you think this is an error you may edit VIDEO_EXTENSIONS at the top of QiGen.py."
            return xchat.EAT_ALL
        
        full_file = file_infos[0]
        
        #Now we're going to get the info on the media file from MediaInfo's DLL
        # Open up the file with mediainfodll
        MI.Open(full_file)
        
        #Getting the filesize
        filesize = int(MI.Get(Stream.General, 0, "FileSize"))
        #The size reading is in bytes, so we need to divide by 1024 to get KB's. You can edit this to get MB if you want. Make sure you change the KB to MB 5 lines below if you do.
        filesize = filesize/1024
        #Now we format the filesize with commas to make it look nice :)
        filesize = locale.format('%d', filesize, grouping=True)
        #And now we make it a string and put KB at the end
        filesize = str(filesize) + " KB"
        
        
        #Getting the duration
        #The duration is in milliseconds, so we need to convert it to Hours, Minutes, and seconds.
        duration_ms = int(MI.Get(Stream.General, 0, "Duration"))
        hours = duration_ms/3600000
        minutes = (duration_ms%3600000)/60000
        seconds = ((duration_ms%3600000)%60000)/1000
        ms_left = ((duration_ms%3600000)%60000)%1000
        #Now we make a nicely formatted string i.e. 1h 22m 43s 121ms
        #Consider rewriting the below parts using string formatters %
        if hours != 0:
            durstring = str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s " + str(ms_left) + "ms"
        elif minutes != 0:
            durstring = str(minutes) + "m " + str(seconds) + "s " + str(ms_left) + "ms"
        else:
            durstring = str(seconds) + "s " + str(ms_left) + "ms"
        
        
        #Getting the bitrate
        #The bitrate comes out first as bits per second
        bitrate = int(MI.Get(Stream.General, 0, "OverallBitRate"))
        #Convert it to Kbps, and if its over 10,000 Kbps, convert it to Mbps; for aesthetic reasons :)
        #We use 1000 instead of 1024 because thats just how its displayed in every media program out there, might as well stick with whats common.
        new_bitrate = bitrate/1000
        if new_bitrate > 10000:
            new_bitrate = new_bitrate/1000
            bitrate_string = str(new_bitrate) + " Mbps"
        else:
            bitrate_string = str(new_bitrate) + " Kbps"
            
        
        #Getting the resolution
        width = int(MI.Get(Stream.Video, 0, "Width"))
        height = int(MI.Get(Stream.Video, 0, "Height"))
        resstring = "Res: " + str(width) + "x" + str(height)
        
        
        #Thats all the info we need, now we put it all together into a nice string
        
        # These are commonly used separaters. Collapsing them into variables saves space and makes the code easier to read.
        opening = color["bold"] + color["lblue"] + "[" + color["closea"] + color["dgrey"]
        closing = color["closea"] + color["bold"] + color["lblue"] + "]" + color["closea"]
        separator = color["bold"] + " :: " + color["closea"]
        clossepopn = closing + separator + opening
        
        msgstring = "MSG " + channel + " " + color["bold"] + "Now Playing: " + color["bold"] + opening + str(file_infos[1]) + clossepopn + str(filesize) + clossepopn + str(durstring) + clossepopn + str(bitrate_string) + clossepopn + str(resstring) + closing
        xchat.command(msgstring)
        
        return xchat.EAT_ALL
    else:
        return xchat.EAT_ALL

def find_file():
    try:
        page = urllib2.urlopen(PAGE_URL)
        html = page.read()
        page.close()
        fdir = re.search('''<p id="filepath">(.*?)</p>''', html).group(1)
        filename = re.search('''<p id="file">(.*?)</p>''', html).group(1)
            
        return [fdir, filename]
    except urllib2.URLError:
        print color["red"] + "There was a problem connecting to Media Player Classic's web interface. Make sure you have it enabled and that the settings at the top of this script are correct."
        return None

def unload_cb(userdata):
    print "\0034 "+__module_name__+" "+__module_version__+" has been unloaded\003"


xchat.hook_command('npvid', qi_start)
xchat.hook_unload(unload_cb)