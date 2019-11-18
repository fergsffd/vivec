""" Sketch for automatic photo taking and database entry

Push Button =========================
    - give user some feedback
    
Take Photo ==========================
    ? Specify path
    - Check if path is valid
    - Acquire new filename 
    ? How to get new filename
    - Capture image from camera
    - Check if image capture successful
    
- Database Entry ====================
    - DEFAULT-> Get date from system and format for db entry
    - OPTIONAL-> Get Purchase Price and any other data
    - Build query
    - Execute query
    - Feedback to user on success/fail
    - If fail ???
    - Prompt user for continue or exit
    - Exit -> close DB -> exit script"""
   
# 
import  RPi.GPIO as GPIO
import time
from datetime import datetime
from os import listdir,system
from os.path import isfile, join, expanduser
import pymysql


pinNum = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(pinNum, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(pinNum, GPIO.RISING,bouncetime=200)

# Build your friggin .config file!
IMAGE_FILE_PATH = "here"
IMAGE_FILE_PREFIX = "there"
TIME_FORMAT = "%Y%M%d%H%M%S"
CAMERA_CAPTURE_COMMAND = "/usr/bin/raspistill -vf -hf -t 10 -o "
DB_USERNAME = "no-no"
DB_NAME = "theDB"
DB_PWD = "nope"
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
     
def switcher(x):
     switcher = {
         's' : getEntry(),
         'a' : makeQuery(),
         'x' : done=True,
         }
     return

#### 
# Sanity checks
print("Sanity checks") # Do more robust checking - writability
try:
    sdir = expanduser(IMAGE_FILE_PATH)
except:
    print('Problem with image file path: ',savedir, end='')
    exit()
    
db = pymysql.connect( user=DB_USERNAME, passwd=DB_PWD, db=DB_NAME)

cur = db.cursor()
    
######

done = False
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

