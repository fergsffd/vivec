""" Python3 """

#
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

import time
from datetime import datetime
import os, sys, getopt
from os import listdir, system, mknod
from os.path import isfile, join, expanduser
import pymysql
import configparser

## Default globals. Assigned in the loadConfig and setConfig functions, nowhere else
TEST = False  # Not checking hardware or writing to db
CONFIG_FILE = os.getcwd() + '/.vconfig'
IMAGE_DIR = os.getcwd() + "/images/"
IMAGE_PREFIX = "image"
CC_COMMAND = "/usr/bin/raspistill -vf -hf -t 10 -o "  # Camera Capture
DB_USER = ""
DB_NAME = "vivecdb"
DB_PWD = ""
DB_HOST = 'LOCALHOST'
CONFIG_SECTION_NAME = 'SETTINGS'


# ============ Database code ===========================
# Test DB access. Can I return itemized DB access failures?
def dbAvailable(dbw=DB_HOST, dbu=DB_USER, dbp=DB_PWD, dbn=DB_NAME):
    # global DB_USER,DB_PWD,DB_HOST,DB_NAME, TEST

    silent = not TEST
    print('dbAvailable dbu,dbp,dbw,dbn:', dbu, dbp, dbw, dbn)
    print('globals', DB_USER, DB_PWD, DB_HOST, DB_NAME)
    try:
        db = pymysql.connect(host=dbw,
                             user=dbu,
                             password='9612729issiS#',
                             db=dbn)
    except pymysql.MySQLError as e:
        if not silent:
            print('Got error {!r}, errno is {}'.format(e, e.args[0]))
            # print('Error Code:', err.errno)
            # print('SQLSTATE:', err.sqlmysqlstate)
            # print('Message:', err.msg)
            print('Credentials:', dbu, '@', dbw, 'db name:', dbn)
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


def dbInsert(cur):
    print('dbInsert')
    return True


def dbQuery(cur):
    print('dbQuery')
    return True


# ================= End DB stuff =========================

# The method might be expanded out to make more descriptive error messages
def inv(msg):
    return ' >>' + msg


# ================= Config file stuff ====================

# Set working config parameters
def setConfig(fn_path, fn_prefix, db_name, db_user, db_pass, db_host, camera):
    global IMAGE_DIR, IMAGE_PREFIX, DB_PWD, DB_NAME, DB_USER, CC_COMMAND
    global DB_HOST

    IMAGE_DIR = fn_path
    IMAGE_PREFIX = fn_prefix
    DB_NAME = db_name
    DB_USER = db_user
    DB_PWD = db_pass
    CC_COMMAND = camera
    DB_HOST = db_host
    """for k in dict:
        if k == 'fn_path'    : IMAGE_DIR    = dict['fn_path']
        elif k == 'fn_prefix': IMAGE_PREFIX = dict['fn_prefix']
        elif k == 'db_name'  : DB_NAME      = dict['db_name']
        elif k == 'db_user'  : DB_USER      = dict['db_user']
        elif k == 'db_pass'  : DB_PWD       = dict['db_pass']
        elif k == 'camera'   : CC_COMMAND   = dict['camera']
        elif k == 'db_host'  : DB_HOST      = dict['db_host']"""


def cameraCmdCheck(cc, silent=False):
    # Check if camera command is valid. Does not check options
    if not silent:
        print('Checking:', cc)
    for i in range(0, len(cc)):
        if cc[i] == ' ':
            break

    cam = cc[:i]

    if not isfile(cam):
        if not silent: print('Command >', cam, '< does not exist.')
        return False
    if not os.access(cam, os.X_OK):
        if not silent: print('Command >', cam, '<is not executable')
        return False
    return True  # No arguments for capture command?


###########
def checkDir(fd, silent=True, msg=''):
    if not os.path.exists(fd):
        msg = msg + 'directory [' + fd + '] does not exist. '
        if not silent:
            print(msg)
            ans = input('Attempt to create?[y/n]')
        else:
            ans = 'y'
        if ans == 'y':
            os.makedirs(fd)
            done = True
        if ans == 'n':
            return False
    return True


#####
def writable(fp):  # Is ther a better way to test?
    checkDir(fp)
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
def inputConfig(fd=False, fp=False, dbn=False, dbu=False, dbp=False, cam=False, dbh=False):
    # the recieved parameters determine if we need to config specified value(s)
    # tmp var will hold entered values until verified, then stored

    # I breakout the db fail params because I may give more detailed access error
    # feedback ( bad credentail vs schema or table not found)

    # Need to break out the code for testing user supplied parameters

    # global IMAGE_DIR, IMAGE_PREFIX, DB_PWD, DB_NAME
    # global DB_USER, CC_COMMAND,DB_HOST

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
            if checkDir(tmp_fd, False, "Image "):
                if not writable(tmp_fd):
                    print('Cannot write files to directory->', tmp_fd)
                else:
                    conf_val['fn_path'] = tmp_fd
                    fd_done = True
                    fd = True

        while not fp_done:
            msg = 'Image filename prefix:[' + IMAGE_PREFIX + ']'
            if not fp: msg = inv(msg)
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

        print('Testing database access...')
        print('globals', DB_USER, DB_PWD, DB_HOST, DB_NAME)
        print()
        if not dbAvailable():
            print('Cannot access db with supplied parameters')
            db_good = False
        else:
            db_good = True

        while not cam_done:
            msg = 'Camera capture command:[' + CC_COMMAND + ']'
            if not cam: msg = inv(msg)
            tmp_cc = input(msg)
            if tmp_cc == '':
                tmp_cc = CC_COMMAND
            if cameraCmdCheck(tmp_cc, silent=False):
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

        done = fd and fp and dbn and dbu and dbp and cam and dbh and db_good

        while not done:
            ans = input('Problem with configuration. (r)etry, (d)iscard changes or ignore & (w)rite ')
            if ans == 'd':
                return False
            elif ans == 'w':
                done = True
            else:
                continue

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


## end inputConfig

def loadConfig():
    global IMAGE_DIR, IMAGE_PREFIX, DB_PWD, DB_NAME
    global DB_USER, CC_COMMAND, DB_HOST

    parser = parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    for sect in parser.sections():
        if TEST:
            print('Section:', sect)
        for k, v in parser.items(sect):
            if TEST:
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
        if TEST:
            print('db_pass:', DB_PWD)
        # setConfig()


###
def checkConfig(fd=IMAGE_DIR, fp=IMAGE_PREFIX, cam=CC_COMMAND):
    # Coded this function to use possible future robust validity checks

    # Returns a list of valid(False) and invalid(True) config entries

    silent = not TEST
    if silent: print('checking config file')
    dict = {'isgood': True}
    if not checkDir(fd, False, "Image "):
        print('Problem with image directory.')
        dict['fd'] = True
        dict['isgood'] = False
    else:
        dict['fd'] = True

    if fp == '':
        print('Probem with image file prefix(is blank)')
        dict['fp'] = True
        dict['isgood'] = False
    else:
        dict['fp'] = False

    if not cameraCmdCheck(cam, True):
        print('Problem with camera command')
        dict['cam'] = True
        dict['isgood'] = False
    else:
        dict['cam'] = False

    print('checkConfig')
    print('globals', DB_USER, DB_PWD, DB_HOST, DB_NAME)
    print()
    if not dbAvailable():
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

    if dict['isgood'] and not silent: print(' config OK')

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
    global CONFIG_FILE, TEST  # , DB_USER, DB_PWD, DB_HOST, DB_NAME
    # global IMAGE_DIR, IMAGE_PREFIX, CC_COMMAND

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
            TEST = True
        if TEST: print('Test flag on')

    if not isfile(CONFIG_FILE):
        print('Cannot locate config file:', CONFIG_FILE)
        x = input('Create config file?[y]')
        if x == 'y':
            dir_done = False
            while not dir_done:
                msg = 'Path for config file?[', os.getcwd(), ' ]?'
                ans: str = input(msg)
                if ans == '':
                    tmp_cnf = os.getcwd() + "/.vconfig"
                tmp_cnf = expanduser(tmp_cnf) + '/.vconfig'
                if not checkDir(tmp_cnf):
                    print('Cannot create config file', tmp_cnf)
                else:
                    CONFIG_FILE = tmp_cnf
                    dir_done = True

            if not inputConfig():
                print('inputConfig failed -- exiting')
                exit()
        else:
            print('Cannot proceed without config file -- exiting')
            exit()
    loadConfig()
    chk_config = checkConfig()
    if not chk_config['isgood']:
        del chk_config['isgood']
        print('Problem with config. Would you like to enter new config params?', end='')
        if input('') == 'y':
            inputConfig(**chk_config)
    done = False
    msg = 'Config options: (s)how, (e)dit or e(x)it?'
    while not done:
        ans = input(msg)
        if ans == 's':
            showConfig()
        elif ans == 'e':
            chk_config = checkConfig()
            if not chk_config['isgood']:
                del chk_config['isgood']
            inputConfig(**chk_config)
        elif ans == 'x':
            done = True


# Phew! config stuff done!

################################

###### Main ######
if __name__ == "__main__":
    main(sys.argv[1:])

exit()
