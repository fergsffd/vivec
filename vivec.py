""" Python3 """

from typing import Dict

try:
    import RPi.GPIO as GPIO
except:
    HW_MODULE_PRESENT = False
else:
    pinNum = 18
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pinNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pinNum, GPIO.RISING, bouncetime=200)
    HW_MODULE_PRESENT = True

import os, sys, getopt, datetime
import subprocess
from os.path import isfile, expanduser
import pymysql
import configparser

# Default globals. Assigned in the loadConfig and setConfig functions, nowhere else
DEBUG = False
CONFIG_DIR = expanduser('~/vivec')
CONFIG_FN = '/.vconfig'
CONFIG_FILE = CONFIG_DIR + CONFIG_FN
IMAGE_DIR = CONFIG_DIR + "/images/"
IMAGE_PREFIX = "image"
CC_COMMAND = "/usr/bin/raspistill -vf -hf -t 10 -o "  # Camera Capture
DB_USER: str = "none"
DB_NAME = "vivecdb"
DB_PWD = "password"
DB_HOST = 'LOCALHOST'

CONFIG_SECTION_NAME = 'SETTINGS'

########### DB hard coded values ###########

DB_TABLE = 'Shoes_DB'
DB_KEY = 'idShoes_table'
DB_COL_FN = 'ImageFilename'
DB_COL_DateAdded = 'DateAdded'
DB_COL_PURCH =  'PurchasePrice'
DB_COL_INV = 'InInventory'
DB_COL_OBJ_NAME = 'ShoeName'

###############################
def domainmenu():
    done = False
    ans: str = ""
    ans_list = [ '1','2','3','x']
    while not done:
        print('Main Menu')
        print('===========')
        print('1 -- Object capture')
        print('2 -- List objects')
        print('3 -- Configuration menu')
        print('x -- exit')
        ans = input('==>')
        if ans not in ans_list:
            print('Not a valid choice.\n')
        else:
            return ans
#######

def obj_capture():

    done = False
    while not done:
        ans = input('press enter key to initiate capture or press button(unavailable) or e(x)it')
        if ans == 'x':
            break
        now = datetime.datetime.now()
        fn = IMAGE_PREFIX + now.strftime('%y%m%d%H%M%S') + '.jpg'
        run_cmd = CC_COMMAND + ' ' + IMAGE_DIR + fn
        cmd_returned = subprocess.call(run_cmd, shell=True)
        print('command', run_cmd, ' returned:',cmd_returned)
        ans = input('Another capture? [y]')
        if ans != 'y' and ans != '':
            break

#######
def list_obj():
    if DEBUG:
        print('Entered listObj')
    print('listObj')
    if DEBUG:
        print('leaving listObj')
########

def config_menu():

    done = False
    msg = 'Config options: (s)how, (e)dit or e(x)it?'
    while not done:
        ans = input(msg)
        if ans == 's':
            showConfig()
        elif ans == 'e':
            chk_config = checkConfig()  # ugh! Fix this
            del chk_config['isgood']
            inputconfig(**chk_config)
        elif ans == 'x':
            done = True
# ============ Database code ===========================
# Test DB access.
# TODO Can I return itemized DB access failures?
# TODO How to determine if db structure matches what we have configured. This is a heavy lift....

def dbAvailable(dbw, dbu, dbp, dbn):
    isgood = True

    try:
        db = pymysql.connect(host=dbw, user=dbu, password=dbp, db=dbn)
    except pymysql.MySQLError as e:

        isgood = False
        if DEBUG: print('db access denied')

    try:
        db.close()
    except:
        pass

    return isgood

def dbCursor():
    print('dbCursor')
    return True


# Setup DB if not exist
def dbConfig():
    print('dbConfig')
    return True


def dbInsert():
    print('dbInsert')
    return True


def dbQuery():
    print('dbQuery')
    
    return True


# ================= End DB stuff =========================

# The method might be expanded out to make more descriptive error messages
# FIXME Is this useful? If so, fix
def inv(msg):
    return ' >>' + msg
def debugg(msg): # Quick function for my debug messages
    if DEBUG:print(msg)

# ================= Config file stuff ====================

# Set working config parameters
def setConfig(fn_path, fn_prefix, db_name, db_user, db_pass, db_host, camera):
    global IMAGE_DIR, IMAGE_PREFIX, DB_PWD, DB_NAME, DB_USER, CC_COMMAND, DB_HOST

    IMAGE_DIR = fn_path
    IMAGE_PREFIX = fn_prefix
    DB_NAME = db_name
    DB_USER = db_user
    DB_PWD = db_pass
    CC_COMMAND = camera
    DB_HOST = db_host

    debugg('Config vars set')

##############
def cameraCmdCheck(cc):
    # Check if camera command is valid. Does not check options
    #debugg('Checking camera command:', cc)
    i = 0
    for i in range(0, len(cc)):
        if cc[i] == ' ':
            break

    cam = cc[:(i + 1)]

    if not isfile(cam):
        #if DEBUG: print('Command >', cam, '< does not exist.')
        return False
    if not os.access(cam, os.X_OK):
        #if DEBUG: print('Command >', cam, '<is not executable')
        return False
    return True  # TODO  No arguments for capture command?


def checkdir(fd, msg=''):

    if not os.path.exists(fd):
        msg = msg + 'directory [' + fd + '] does not exist. '
        print(msg)
        ans = input('Attempt to create?[y/n]')
        if ans == 'y':
            os.makedirs(fd)
            return True
        if ans == 'n':
            return False
    return True


#####
def writable(fp):  # TODO Is there a better way to test?
    checkdir(fp)
    fn = fp + '/test'
    try:
        test = os.open(fn, os.O_CREAT)
    except OSError:
        print('Unable to write test file. Permissions?')
        return False
    else:
        os.remove(fn)
        return True

###
def inputconfig(fd=False, fp=False, dbn=False, dbu=False, dbp=False, cam=False, dbh=False):
    # the recieved parameters determine if we need to config specified value(s)
    # tmp var will hold entered values until verified, then stored

    # I breakout the db fail params because I may give more detailed access error
    # feedback ( bad credentail vs schema or table not found)

    # Need to break out the code for testing user supplied parameters
    if DEBUG: print('Entering inputConfig')
    conf_val = {}  # Store values for writing to file
    done = False
    fd_done = False
    fp_done = False
    dbn_done = False
    dbu_done = False
    dbp_done = False
    dbh_done = False
    cam_done = False

    while not done:
        while not fd_done:
            msg = 'Image directory:[' + IMAGE_DIR + ']'
            if not fd: msg = inv(msg)
            tmp_fd = input(msg)
            if tmp_fd != '':
                tmp_fd = expanduser(tmp_fd)
            else:
                tmp_fd = IMAGE_DIR
            if checkdir(tmp_fd, "Image "):
                if not writable(tmp_fd):
                    print('Cannot write files to directory->', tmp_fd)
                else:
                    conf_val['fn_path'] = tmp_fd
                    fd_done = True
                    fd = True

        while not fp_done:
            msg = 'Image filename prefix:[' + IMAGE_PREFIX + ']'
            if not fp:
                msg = inv(msg)
            tmp_fp = input(msg)
            if tmp_fp == '':  # Do more checking for legit filename
                tmp_fp = IMAGE_PREFIX
            if tmp_fp == '':
                print('Image filename prefix cannot be blank')
            else:
                conf_val['fn_prefix'] = tmp_fp
                fp_done = True
                fp = True

        while not dbn_done:  # Get a list of available DBs?
            msg = 'Database name:[' + DB_NAME + ']'
            if not dbn: msg = inv(msg)
            tmp_dbn = input(msg)
            if tmp_dbn == '':  # Do more checking for legit dbname
                tmp_dbn = DB_NAME
            if tmp_dbn == '':
                print('Database name cannot be blank')
            else:
                dbn_done = True
                dbn = True
                conf_val['db_name'] = tmp_dbn

        while not dbu_done:
            msg = 'Database username:[' + DB_USER + ']'
            if not dbu: msg = inv(msg)
            tmp_dbu = input(msg)
            if tmp_dbu == '':
                tmp_dbu = DB_USER
            if tmp_dbu == '':
                print('Database username cannot be blank')
            else:
                dbu_done = True
                dbu = True
                conf_val['db_user'] = tmp_dbu

        while not dbp_done:  # Get a list of available DBs?
            msg = 'Database password:[' + DB_PWD + ']'
            if not dbp: msg = inv(msg)
            tmp_pwd = input(msg)
            if tmp_pwd == '':
                tmp_pwd = DB_PWD
            if tmp_pwd == '':
                print('Database password cannot be blank')
            else:
                dbp_done = True
                dbp = True
                conf_val['db_pass'] = tmp_pwd

        while not dbh_done:  # Get a list of available DBs?
            msg = 'Hostname:[' + DB_HOST + ']'
            if not dbh: msg = inv(msg)
            tmp_dbw = input(msg)
            if tmp_dbw == '':
                tmp_dbw = DB_HOST
            if tmp_dbw == '':
                print('Database hostname cannot be blank')
            else:
                dbh_done = True
                dbh = True
                conf_val['db_host'] = tmp_dbw

        print('Testing database access...') # FIXME Something is broken here. (d)iscard changes cause loop
        if not dbAvailable(dbu=conf_val['db_user'], dbp=conf_val['db_pass'], dbn=conf_val['db_name'],
                           dbw=conf_val['db_host']):
            print('Cannot access db with supplied parameters')
            db_good = False
        else:
            print('Access granted')
            db_good = True

        while not cam_done:
            msg = 'Camera capture command:[' + CC_COMMAND + ']'
            if not cam: msg = inv(msg)
            tmp_cc = input(msg)
            if tmp_cc == '':
                tmp_cc = CC_COMMAND
            if cameraCmdCheck(tmp_cc):
                cam_done = True
                conf_val['camera'] = tmp_cc
            else:
                ans_done = False
                while not ans_done:
                    ans = input('Problem with camera command. (r)etry, (d)iscard or (i)gnore and accept)? ')
                    if ans == 'i':
                        cam_done = True
                        ans_done = True
                        conf_val['camera'] = tmp_cc
                    elif ans == 'd':
                        cam_done = True
                        cam = True
                        ans_done = True
                        conf_val['camera'] = CC_COMMAND
                    elif ans == 'r':
                        ans_done = True

        conf_done = fd and fp and dbn and dbu and dbp and cam and dbh and db_good

        while not conf_done:
            ans = input('Problem with configuration. (r)etry, (d)iscard changes or ignore & (w)rite ')
            if ans == 'd':
                return False
            elif ans == 'w':
                conf_done = True
                done = True
            elif ans == 'r':
                conf_done = True
            else:
                print('Invalid choice')

    print('Variables to be written to config file:')
    setConfig(**conf_val)
    showConfig()
    if input('Save?[y]') != 'y':
        print('Changes not saved')
        return False
    else:  # Write out config file
        # print(conf_val)
        setConfig(**conf_val)
        parser = configparser.ConfigParser()
        if not parser.has_section(CONFIG_SECTION_NAME):
            parser.add_section(CONFIG_SECTION_NAME)
        for key, value in conf_val.items():
            parser.set(CONFIG_SECTION_NAME, key, value)
        file = open(CONFIG_FILE, 'w')
        parser.write(file)
        file.close()
        print('Changes saved')
        return True

# end inputConfig

def loadConfig():
    global IMAGE_DIR, IMAGE_PREFIX, DB_PWD, DB_NAME
    global DB_USER, CC_COMMAND, DB_HOST

    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    for sect in parser.sections():
        if DEBUG:
            print('Section:', sect)
        for k, v in parser.items(sect):
            if DEBUG:
                print(' {} = {}'.format(k, v))
            if k == 'fn_path':
                IMAGE_DIR = expanduser(v)
            elif k == 'fn_prefix':
                IMAGE_PREFIX = v
            elif k == 'db_name':
                DB_NAME = v
            elif k == 'db_user':
                DB_USER = v
            elif k == 'db_pass':
                DB_PWD = v
            elif k == 'camera':
                CC_COMMAND = v
            elif k == 'db_host':
                DB_HOST = v


##################################################

def checkConfig():
    # Coded this function to use possible future robust validity checks

    # Returns a list of valid(False) and invalid(True) config entries

    dict: Dict[str, bool] = {'isgood': True}

    if DEBUG:
        print('Entered checkConfig')

    if not checkdir(IMAGE_DIR, "Image "):
        print('Problem with image directory.')
        dict['fd'] = True
        dict['isgood'] = False
    else:
        dict['fd'] = True

    if IMAGE_PREFIX == '':
        print('Probem with image file prefix(is blank)')
        dict['fp'] = True
        dict['isgood'] = False
    else:
        dict['fp'] = False

    if not cameraCmdCheck(CC_COMMAND):
        print('Problem with camera command')
        dict['cam'] = True
        dict['isgood'] = False
    else:
        dict['cam'] = False

    if not dbAvailable(dbn=DB_NAME, dbu=DB_USER, dbp=DB_PWD, dbw=DB_HOST):
        print('Problem with database access')
        dict['dbn'] = True
        dict['dbu'] = True
        dict['dbp'] = True
        dict['dbh'] = True
        dict['isgood'] = False
    else:
        dict['dbn'] = False
        dict['dbu'] = False
        dict['dbp'] = False
        dict['dbh'] = False

    return dict


### end checkConfig

def showConfig():
    print('Image file directory:', IMAGE_DIR)
    print('Image file prefix   :', IMAGE_PREFIX)
    print('Database username   :', DB_USER)
    print('Database name       :', DB_NAME)
    print('Database hostname   :', DB_HOST)
    print('Database password not shown')
    print('Camera capture cmd  :', CC_COMMAND)


# ================= End config stuff ======================

def printUsage():
    print('Usage: vivec.py [OPTION]')
    print(' -h,  --help                   usage information')
    print(' -c,  --config="<configfile>"  path to configuration file')
    print(' -t   --test                   no hardware or db writes')


###########################
def main(argv):
    global CONFIG_DIR, CONFIG_FN, CONFIG_FILE, DEBUG

    try:
        opts, args = getopt.getopt(argv, "htc:", ['help', 'test', "config="])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h' or opt == '--help':
            printUsage()
            sys.exit()
        elif opt in ("-c", "--config"):
            cnf = expanduser(arg)
            if isfile(cnf):
                CONFIG_FILE = cnf
            else:
                print('config file does not exist')
                exit()
        elif opt in ('-t', '--test'):
            DEBUG = True
        if DEBUG: print('Test flag on')

    if not isfile(CONFIG_FILE):
        print('Cannot locate config file:', CONFIG_FILE)
        x = input('Create config file?[y]')
        if x == 'y':
            dir_done = False
            tmp_cnf = ''
            while not dir_done:
                msg = 'Path for config file?[', os.getcwd(), ' ]?'
                ans: str = input(msg)
                if ans == '':
                    tmp_cnf = CONFIG_DIR
                else:
                    tmp_cnf = expanduser(tmp_cnf)
                if not checkdir(tmp_cnf):
                    print('Cannot create config file directory', tmp_cnf)
                else:
                    CONFIG_FILE = tmp_cnf + CONFIG_FN
                    dir_done = True

            if not inputconfig():
                print('inputConfig failed -- exiting')
                exit()
        else:
            print('Cannot proceed without config file -- exiting')
            exit()
    loadConfig()
    chk_config = checkConfig()
    if not chk_config['isgood']:
        print('Problem with config. Would you like to enter new config params?', end='')
        if input('') == 'y':
            inputconfig(**chk_config)
    del chk_config['isgood']
    # Initial config check done
    done = False
    menu = ""
    while not done: # Main Menu
        menu = domainmenu()
        if menu == '1':
            obj_capture()
        elif menu == '2':
            list_obj()
        elif menu == '3':
            config_menu()
        elif menu == 'x':
            done = True

################################

###### Main ######
if __name__ == "__main__":
    main(sys.argv[1:])

exit()
