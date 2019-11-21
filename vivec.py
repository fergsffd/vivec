""" Python3 """

#
import  RPi.GPIO as GPIO
import time
from datetime import datetime
from os import listdir,system
from os.path import isfile, join, expanduser
import pymysql
import configparser


pinNum = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(pinNum, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(pinNum, GPIO.RISING,bouncetime=200)

# Build your friggin .config file!
IMAGE_FILE_PATH = "~/vivec/images/"
IMAGE_FILE_PREFIX = "image"
TIME_FORMAT = "%Y%M%d%H%M%S"
CAMERA_CAPTURE_COMMAND = "/usr/bin/raspistill -vf -hf -t 10 -o "
DB_USERNAME = ""
DB_NAME = ""
DB_PWD = ""
TIMEOUT = 12 # Program will end

###########################d
def makeFn(savedir): # Make filename from prefix and timestamp
     #print(listdir(savedir))
     dt = datetime.today()
     fn = savedir + IMAGE_FILE_PREFIX + dt.strftime("%y%m%d%H%M%S")
     return(fn)

def getImage(sdir):
     cam = CAMERA_CAPTURE_COMMAND + makeFn(sdir) + '.jpg'
     system(cam)

def makeQuery(savedir):
     print("makeQuery")
     getImage(savedir);

def doQuery(  ):
     print("doQuery")

#######
def (checks): # Sanity checks
    print("Sanity checks") # Do more robust checking

    try:
        sdir = expanduser(IMAGE_FILE_PATH)
    except:
        print('Problem with image file path: ',savedir, end='')
        exit()

    try:
	print('Check for disk writability?')
    except:
	print('Unable to write image files to:', IMAGE_FILE_PATH, end='')

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

#######
def getConfig( confFn="~/.vivec/vivec.conf"): # Maybe take a command line path to conf file
    done = False
    try:
         if( not isfile(confFn ):
             print('Cannot locate config file:', confFn, end='')
	     fnPath= confFn
	     fnPrefix=''
	     dbName=''
	     dbUser=''
	     dbpasswd=''
	     while( not done ):
                 x = input('would you like to create one (y/n)? ')
		 if( x == 'y' ):

                    fnPath = input('Directory to store image files? [', fnPath, ']'  end='')
		    if( not os.path_isdir( os.path.expanduser(fnPath)):
		    fnPrefix = input('Image filename prefix? ', end='')
		    dbName

###### Main ######


done = False
if( not getConfig():
    print('Problem with loading config file')

x = 0
msg = "ended"

while not done:
    a = input('(s)how, (a)dd or e(x)it')
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
