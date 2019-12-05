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

## Globals
TEST = False # Not checking hardware or writing to db
CONFIG_FILE = os.getcwd() +'/.vconfig'
IMAGE_FP = os.getcwd() + "/images/"
IMAGE_PREFIX = "image"
CC_COMMAND = "/usr/bin/raspistill -vf -hf -t 10 -o " # Camera Capture
DB_USER = ""
DB_NAME = "vivecdb"
DB_PWD = ""
DB_HOST = 'LOCALHOST'
CONFIG_SECTION_NAME = 'SETTINGS'

#============ Database code ===========================
# Test DB access. Can I return itemized DB access failures?
def dbAvailable( dbw=DB_HOST,  dbu=DB_USER, dbp=DB_PWD, dbn=DB_NAME, silent=True):
    isgood = True
    try:
        db = pymysql.connect(dbw,dbu,dbp,dbn)
    except pymysql.MySQLError as e:
        if not silent:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
        #print('Error Code:', err.errno)
        #print('SQLSTATE:', err.sqlstate)
        #print('Message:', err.msg)
            print('Credentials:',dbu, '@',dbw, 'db name:', dbn)
        isgood = False

    try:
        db.close()
    except:
        pass
    return isgood

def dbCursor():
    print('dbCursor')
    return True

# Setup DB if not exist
def dbConfig(testing=False):
    print('dbConfig')
    return True

def dbInsert( cur ):
    print('dbInsert')
    return True

def dbQuery( cur ):
    print('dbQuery')
    return True
#================= End DB stuff =========================

#================= Config file stuff ====================
def cameraCmdCheck( x=CC_COMMAND, silent=False):
    #Check if camera command is valid. Does not check options
    if( not silent):
        print('Checking:',x)
    for i in range(0, len(x)):
        if x[i] == ' ':
            break

    cam = x[:i]

    if( not isfile(cam) ):
        if (not silent): print('Command >', cam,'< does not exist.')
        return False
        if( not os.access( cam, os.X_OK) ):
            if( not silent): print('Command >', cam,'<is not executable')
            return  False
        else:
            return True
    return True # No arguments for capture command?
###########
def checkDir( fp, silent=True, msg='' ):
    if( not os.path.exists(fp)):
        msg = msg + 'directory [' + fp + '] does not exist. '
        if( not silent):
            print(msg)
            ans = input('Attempt to create?[y/n]')
        else: ans = 'y'
        if( ans == 'y' ):
            os.makedirs(fp)
            done = True
        if( ans == 'n' ):
            return False
    return True
#####
def writable( fp ): # Is ther a better way to test?
    checkDir( fp )
    fn = fp + '/test'
    try:
        test = os.open(fn, os.O_CREAT)
    except OSError:
        print('Unable to write test file. Permissions?')
        return False
    else:
        os.remove( fn )
        return True
###
def inputConfig(fd=False,fp=False,dbn=False,
    dbu=False,dbp=False,cam=False,dbh=False):
# the recieved parameters determine if we need to config specified value(s)
# tmp var will hold entered values until verified, then stored

# Need to break out the code for testing user supplied parameters

    global IMAGE_FP, IMAGE_PREFIX, DB_PWD, DB_NAME, DB_USER, CC_COMMAND
    global DB_HOST

    print('Using config file ', CONFIG_FILE)
    dict = {}
    done = False
    write_db_cfg = False

    while( not done):
        while( not fd ):
            msg = 'Image directory:[' + IMAGE_FP + ']'
            tmp_fp = input(msg)
            if( tmp_fp != ''):
                tmp_fp = expanduser(tmp_fp)
            else:
                tmp_fp = IMAGE_FP
            if( checkDir(tmp_fp, False, "Image ")):
                if( not writable(tmp_fp)):
                    print('Cannot write files to directory->', tmp_fp)
                else:
                    IMAGE_FP = tmp_fp
                    dict['fn_path']= IMAGE_FP
                    fd = True

        while( not fp ):
            msg = 'Image file prefix:[' + IMAGE_PREFIX + ']'
            x = input(msg )
            if( x != ''): #Do more checking for legit filename
                IMAGE_PREFIX = x
            dict['fn_prefix'] = IMAGE_PREFIX
            fp = True

        while( not dbn ): #Get a list of available DBs?
            msg = 'Database name:[' + DB_NAME + ']'
            tmp_dbn = input(msg)
            if tmp_dbn == '': #Do more checking for legit dbname
                tmp_dbn = DB_NAME
            if tmp_dbn == '':
                print('Database name cannot be blank')
            else:
                dbn = True

        while( not dbu ):
            msg = 'Database username:['+ DB_USER +']'
            tmp_dbu = input(msg)
            if( tmp_dbu == ''):
                tmp_dbu = DB_USER
            if( tmp_dbu == ''):
                print('Database username cannot be blank')
            else:
                dbu = True

        while( not dbp ): #Get a list of available DBs?
            msg = 'Database passwd:[' + DB_PWD +']'
            tmp_pwd = input(msg)
            if( tmp_pwd == ''):
                tmp_pwd = DB_PWD
            if( tmp_pwd == ''):
                print('Database password cannot be blank')
            else:
                dbp = True

        while( not dbh ): #Get a list of available DBs?
            msg = 'Hostname:[' + DB_HOST +']'
            tmp_dbw = input(msg)
            if( tmp_dbw == ''):
                tmp_dbw = DB_HOST
            if( tmp_dbw == ''):
                print('Database hostname cannot be blank')
            else:
                dbh = True

        print('Testing database access...')
        if( not dbAvailable() ):
            print('Cannot access db with supplied parameters')
            ans_done = False
            while ( not ans_done):
                ans = input('(r)etry, (s)kip or ignore & (w)rite ')
                if ans == 's':
                    ans_done = True
                elif ans == 'w':
                    ans_done = True
                    write_db_cfg = True
                else:
                    continue
        else:
            write_db_cfg = True
        if write_db_cfg:
            DB_HOST = tmp_dbw
            DB_PWD   = tmp_pwd
            DB_USER  = tmp_dbu
            DB_NAME  = tmp_dbn
            dict['db_host'] = DB_HOST
            dict['db_pass'] = DB_PWD
            dict['db_user'] = DB_USER
            dict['db_name'] = DB_NAME

        while( not cam ):
            msg = 'Camera capture command:['+ CC_COMMAND + ']'
            cc = input(msg)
            if( cc == '' ):
                cc = CC_COMMAND
            if cameraCmdCheck( cc, silent=False):
                CC_COMMAND = cc
                cam = True
            else:
                if input('Cannot locate command. Retry?[y]') != 'y':
                    print('Bad camera command')
                    cam = True
        dict['camera'] = CC_COMMAND
        done = fd and fp and dbn and dbu and dbp and cam and dbh


    parser = configparser.ConfigParser()
    if( not parser.has_section(CONFIG_SECTION_NAME) ):
        parser.add_section(CONFIG_SECTION_NAME)
    for key, value in dict.items():
        parser.set(CONFIG_SECTION_NAME, key, value)
    print('Variables to be written to config file:')
    loadConfig()
    if( input('Save?[y]') != 'y'):
        print('Changes not saved')
        return False
    else:
        file = open(CONFIG_FILE,'w')
        parser.write(file)
        file.close()
        print('Changes saved')
        return True
## end inputConfig

def loadConfig( show=True ):
    global IMAGE_FP, IMAGE_PREFIX, DB_PWD, DB_NAME
    global DB_USER, CC_COMMAND,DB_HOST

    parser = parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    for sect in parser.sections():
       if( show ):
           print('Section:', sect)
       for k,v in parser.items(sect):
          if( show ):
              print(' {} = {}'.format(k,v))
          if k == 'fn_path'    : IMAGE_FP = expanduser(v)
          elif k == 'fn_prefix': IMAGE_PREFIX = v
          elif k == 'db_name'  : DB_NAME = v
          elif k == 'db_user'  : DB_USER = v
          elif k == 'db_pass'  : DB_PWD = v
          elif k == 'camera'   : CC_COMMAND = v
          elif k == 'db_host'  : DB_HOST = v
       if( show ):
           print()
###
def checkConfig(silent=False):
# Coded this function to use possible future robust validity checks
# Database check happens elswhere

    if( not silent ): print('checking config file')
    dict = { 'isgood' : True }
    if( not checkDir(IMAGE_FP, False, "Image " )):
        print('Problem with image directory.')
        dict['fd'] = True
        dict['isgood'] = False

    if( IMAGE_PREFIX == ''):
        print('Probem with image file prefix(is blank)')
        dict['fp'] = True
        dict['isgood'] = False

    if( not cameraCmdCheck( CC_COMMAND, True )):
        print('Problem with camera command')
        dict['cam'] = True
        dict['isgood'] = False

    if( dict['isgood'] ): print(' config OK')

    return dict
### end checkConfig

def showConfig(  ):
    print('Image file directory:', IMAGE_FP)
    print('Image file prefix   :', IMAGE_PREFIX)
    print('Database username   :', DB_USER )
    print('Database name       :', DB_NAME)
    print('Database hostname   :', DB_HOST)
    print('Database password not shown')
    print('Camera capture cmd  :', CC_COMMAND)

#================= End config stuff ======================

def printUsage():
    print('Usage: vivec.py [OPTION]')
    print(' -h,  --help                   usage information')
    print(' -c,  --config="<configfile>"  path to configuration file')
    print(' -t   --test                   no hardware or db writes')
###########################
def main(argv):

     global CONFIG_FILE
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
            cnf = expanduser( arg )
            if( isfile( cnf )):
                CONFIG_FILE = cnf
            else:
                print('config file does not exist')
                exit()
         elif opt in ('-t', '--test'):
            TEST = True

     if( not isfile(CONFIG_FILE)):
         print('Cannot locate config file:',CONFIG_FILE)
         x = input('Create config file?[y]')
         if( x == 'y'):
             if( not inputConfig() ):
                 print('inputConfig failed -- exiting')
                 exit()
         else:
             print('Cannot proceed without config file -- exiting')
             exit()
     chk_config = checkConfig()
     if not dbAvailable():
         print('dbproblem')
     if( not chk_config['isgood']):
         del chk_config['isgood']

         print('Problem with config. Would you like to enter new config param?[y]')
         if input('') == 'y':
            inputConfig( **chk_config )
     done = False
     msg = 'Config options: (s)how, (e)dit or e(x)it?'
     while not done:
         ans = input(msg)
         if ans == 's': showConfig()
         elif ans == 'e': inputConfig()
         elif ans == 'x': done = True


# Phew! config stuff done!

################################

###### Main ######
if __name__ == "__main__":
    main(sys.argv[1:])

exit()
