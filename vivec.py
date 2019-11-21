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
from os import listdir,system
from os.path import isfile, join, expanduser
import pymysql
import configparser
import sys, getopt


# Build your friggin .config file!
CONFIG_FILE_DEFAULT = expanduser('~/vivec/.v_config')
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
TIMEOUT = 12 # Program will end

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
            HW_MODULE_PRESENT = False
            DB_WRITE = False

def writable( fn ):
    if( not isfile( os.mknod( fn, mode=600)) ):
        return False
    else:
        os.remove('fn')
        return true

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

#######
def checks(): # Sanity checks
    print("Sanity checks") # Do more robust checking

    try:
        sdir = expanduser(IMAGE_FILE_PATH_FINAL)
    except:
        print('Problem with image file path: ',IMAGE_FILE_PATH_FINAL, end='')
        exit()

    try:
        db = pymysql.connect( user=DB_USERNAME, passwd=DB_PWD, db=DB_NAME)
    except:
	    print('Problem with database: ', DB_NAME, end='')
	    exit()
    cur = db.cursor()

    try:
         print('checking for camera...')
    except:
         print('Unable to find camera')
def makeConfig():
    print("Let's make a config file")

#######
def getConfig(): # Maybe take a command line path to conf file
    if( not isfile(CONFIG_FILE_FINAL)):
        print('Cannot locate config file:', CONFIG_FILE_FINAL, end='')
        if( input('Make a configuration file? [y/n]') == 'y'):
            c_done = False
            while( not c_done):
                fn = input('Path for config file, (x) to exit:[',CONFIG_FILE_FINAL,']:')
                if( fn == ''):
                    fn = CONFIG_FILE_FINAL
                else if( fn == 'x'):
                    return False
                fn = expanduser(fn)
                if( not writable( fn )):
                   print('Unable to create file as specified:', fn, end='')
                else:
                    c_done = true
                    CONFIG_FILE_FINAL = fn
        c_done = False
        while( not c_done):
            fp = input('Image file path, (x) to exit:[',IMAGE_FILE_PATH_FINAL,']:')
            if( fp == ''):
                fp = IMAGE_FILE_PATH_FINAL
            else if( fp == 'x'):
                return False
            fn = expanduser(fp) + "test"
            if( not writable( fn )):
               print('Unable to create image file in directory:', IMAGE_FILE_PATH_FINAL, end='')
            else:
                c_done = true
                IMAGE_FILE_PATH_FINAL = fp
        c_done = False
        while( not c_done):
            i = input('Image filename prefix, (x) to exit:[',IMAGE_PREFIX_FINAL,']:')
            if( i == 'x'):
                return False
            if( i == ''):
                c_done = True
            else:
                c_done = True
                IMAGE_PREFIX_FINAL = i #Should check for valid text

    dbName=''
    dbUser=''
    dbpasswd=''
    while( not done ):
        x = input('would you like to create one (y/n)? ')
        if( x == 'y' ):
            fnPath = input('Directory to store image files? [', fnPath, ']',  end='')
            if( not os.path_isdir( os.path.expanduser(fnPath))):
                fnPrefix = input('Image filename prefix? ', end='')
        else:
            done = True
            exit() #####
###### Main ######
if __name__ == "__main__":
    main(sys.argv[1:])
if( not HW_MODULE_PRESENT ):
    print('No Raspberry Pi modules available')
done = False
if( not getConfig()):
    print('Problem with loading config file')

x = 0
msg = "ended"

while not done:
    a = input('(s)how, (a)dd or e(x)it', end='')
if( input('?') != 'x'):
     # if GPIO.event_detected(pinNum):
    print('button pressed')
    makeQuery(sdir)
    x+=1
    if ( x> 3 ):
         done = True
         msg = 'reached button pressed limit'
    else:
         exit()

# End main loop
print("program", msg)
exit()
