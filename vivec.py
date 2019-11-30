""" Python3 """

#
try:
    import  RPi.GPIO as GPIO
except:
    HW_MODULE_PRESENT = False
else:
    pinNum = 18
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pinNum, GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pinNum, GPIO.RISING,bouncetime=200)
    HW_MODULE_PRESENT = True

import time
from datetime import datetime
import os, sys, getopt
from os import listdir,system, mknod
from os.path import isfile, join, expanduser
import pymysql
import configparser

# Build your friggin .config file!
CONFIG_FILE_DEFAULT = expanduser('~/vivec/.config')
CONFIG_FILE_FINAL = CONFIG_FILE_DEFAULT
IMAGE_FILE_PATH_DEFAULT = expanduser("~/vivec/images/")
IMAGE_FILE_PATH_FINAL = IMAGE_FILE_PATH_DEFAULT
IMAGE_PREFIX_DEFAULT = "image"
IMAGE_PREFIX_FINAL = IMAGE_PREFIX_DEFAULT
TIME_FORMAT = "%Y%M%d%H%M%S"
CAMERA_CAPTURE_COMMAND = "/usr/bin/raspistill -vf -hf -t 10 -o "
DB_WRITE = True
DB_USERNAME = ""
DB_NAME = ""
DB_PWD = ""
##
TIMEOUT = 12 # Program will end
TEST = False


def printUsage():
    print('Usage: vivec.py [OPTION]')
    print(' -h,  --help                   usage information')
    print(' -c,  --config="<configfile>"  path to configuration file')
    print(' -t   --test                   no hardware or db writes')
###########################
def main(argv):
     try:
         opts, args = getopt.getopt(argv,"htc:",['help','test',"config="])
     except getopt.GetoptError:
         printUsage()
         sys.exit(2)
     for opt, arg in opts:
         if( opt == '-h' or opt == '--help'):
            printUsage()
            sys.exit()
         elif opt in ("-c", "--config"):
            IMAGE_FILE_PREFIX_FINAL = arg
         elif opt in ('-t', '--test'):
            TEST = True
            DB_WRITE = False
################################
def writable( fn ): # Is ther a better way to test?
    #test = os.open(fn, os.O_CREAT)
    try:
        test = os.open(fn, os.O_CREAT)
    except OSError:
        print('OS error')
        return False
    else:
        #os.close( test )
        print(' removing ',fn)
        os.remove( fn )
        return True
###
def makeFn(): # Make filename from prefix and timestamp
     #print(listdir(savedir))
     dt = datetime.today()
     fn = IMAGE_FILE_PATH_FINAL + IMAGE_PREFIX_FINAL + dt.strftime("%y%m%d%H%M%S")
     return(fn)
def getImage(sdir):
     cam = CAMERA_CAPTURE_COMMAND + makeFn() + '.jpg'
     system(cam)

def makeQuery():
     print("makeQuery")
     getImage();
def doQuery(  ):
     print("doQuery")
###
def makeConfig():
    global CONFIG_FILE_FINAL, IMAGE_FILE_PATH_FINAL, IMAGE_PREFIX_FINAL
    done = False
    print("Let's make a config file")
    while( not done):
        msg = 'Path for config file, (x) to exit:[' + CONFIG_FILE_FINAL + ']:'
        fn = input(msg)
        if( fn == ''):
            fn = CONFIG_FILE_FINAL
        elif( fn == 'x'):
            return False
        fn = expanduser(fn)
        if( not writable( fn )):
           print('Unable to create file as specified:', fn)
        else:
            done = True
            CONFIG_FILE_FINAL = fn
    done = False
    while( not done):
        msg = 'Image file path, (x) to exit:[' +IMAGE_FILE_PATH_FINAL + ']:'
        fp = input(msg)
        if( fp == ''):
            fp = IMAGE_FILE_PATH_FINAL
        elif( fp == 'x'):
            return False
        fn = expanduser(fp) + "test"
        print('fn = ',fn)
        if( not writable( fn )):
           print('Unable to create image file in directory:', IMAGE_FILE_PATH_FINAL)
        else:
            done = True
            IMAGE_FILE_PATH_FINAL = fp
    done = False
    while( not done):
        msg = 'Image filename prefix, (x) to exit:['+IMAGE_PREFIX_FINAL +']:'
        i = input(msg)
        if( i == 'x'):
            return False
        elif( i == ''):
            done = True
        else:
            done = True
            IMAGE_PREFIX_FINAL = i #Should check for valid text

    dbName=''
    dbUser=''
    dbpasswd=''
    return True
#######
def getConfig(): # Maybe take a command line path to conf file
    global CONFIG_FILE_FINAL, IMAGE_FILE_PATH_FINAL, IMAGE_PREFIX_FINAL

    if( not isfile(CONFIG_FILE_FINAL)):
        done = False
        print('Cannot locate config file:', CONFIG_FILE_FINAL)
        while( not done):
            if( input('Make a configuration file? [y/n]') == 'y'):
                done = makeConfig()
            else:
                print('Config file unavailable. Exiting')
                exit()
    print('getConfig success')
    return True
###
def prtConfig(): #Print config fileinfo
    return True

###### Main ######
if __name__ == "__main__":
    main(sys.argv[1:])

if( not HW_MODULE_PRESENT ):
    print('No Raspberry Pi modules available')
done = False
if( not getConfig()):
    print('Problem with loading config file')

exit()
