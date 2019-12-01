# Working on the config file stuff
# maybe code allowing to specify config file from command line

import configparser, os
from os.path import isfile, expanduser

CONFIG_FILE = os.getcwd() +'/.vconfig'
# Defaults
IMAGE_FP = os.getcwd() + "/vivec/images/"
IMAGE_PREFIX = "image"
CC_COMMAND = "/usr/bin/raspistill -vf -hf -t 10 -o " # Camera Capture
DB_USER = ""
DB_NAME = "vivecdb"
DB_PWD = ""
CONFIG_SECTION_NAME = 'SETTINGS'
######
def cameraCmdCheck( x=CC_COMMAND, silent=False):
    #Check if camera command is valid. Does not check options
    if( not silent):
        print('Checking:',x)
    for i in range(0, len(x)):
        if x[i] == ' ':
            break

    cam = x[:i]
    if( not silent ): print('cam: ', cam)
    if( not isfile(cam) ):
        if (not silent): print('Command does not exist.')
        return False
        if( not os.access( cam, os.X_OK) ):
            if( not silent): print('Command is not executable')
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

def inputConfig():
    print('Using config file ', CONFIG_FILE)

    global IMAGE_FP, IMAGE_PREFIX, DB_PWD, DB_NAME, DB_USER, CC_COMMAND

    done = False
    while( not done ):
        msg = 'Image directory:[' + IMAGE_FP + ']'
        x = input(msg)
        if( x != ''):
            IMAGE_FP = expanduser(x)
        if( checkDir(IMAGE_FP, False, "Image ")):
            if( not writable(IMAGE_FP)):
                print('Cannot write files to directory->', IMAGE_FP)
            else:
                dict = { 'fn_path' : IMAGE_FP }
                done = True
    done = False
    while( not done):
        msg = 'Image file prefix:[' + IMAGE_PREFIX + ']'
        x = input(msg )
        if( x != ''): #Do more checking for legit filename
            IMAGE_PREFIX = x
        dict['fn_prefix'] = IMAGE_PREFIX
        done = True
    done = False
    while( not done ): #Get a list of available DBs?
        msg = 'Database name:[' + DB_NAME + ']'
        x = input(msg)
        if( x != ''): #Do more checking for legit dbname
            DB_NAME = x
        if( DB_NAME == ''):
            print('Database name cannot be blank')
        else:
            dict['db_name'] = DB_NAME
            done = True
    done = False
    while( not done ):
        msg = 'Database username:['+ DB_USER +']'
        x = input(msg)
        if( x != ''):
            DB_USER = x
        if( DB_USER == ''):
            print('Database username cannot be blank')
        else:
            dict['db_user'] = DB_USER
            done = True
    done = False
    while( not done ): #Get a list of available DBs?
        msg = 'Database passwd:[' + DB_PWD +']'
        x = input(msg)
        if( x != ''):
            DB_PWD = x
        if( DB_PWD == ''):
            print('Database password cannot be blank')
        else:
            dict['db_pass'] = DB_PWD
            done = True
    done = False
    while( not done ):
        msg = 'Camera capture command:['+ CC_COMMAND + ']'
        cc = input(msg)
        if( cc != '' ):
            if( cameraCmdCheck( cc ) ):
                CC_COMMAND = cc
                done = True
            else:
                if( input('Cannot locate command. Retry?[y/n]') != 'y'):
                    done = True
        else:
            done = True
    dict['camera'] = CC_COMMAND


    if( not parser.has_section(CONFIG_SECTION_NAME) ):
        parser.add_section(CONFIG_SECTION_NAME)
    for key, value in dict.items():
        parser.set(CONFIG_SECTION_NAME, key, value)
    file = open(CONFIG_FILE,'w')

    parser.write(file)
    file.close()
    print('config file written')

    return True
## end inputConfig

def loadConfig( show=True ): #Loads values
    global IMAGE_FP, IMAGE_PREFIX, DB_PWD, DB_NAME
    global DB_USER, CC_COMMAND
    parser.read(CONFIG_FILE)
    for sect in parser.sections():
       if( show ):
           print('Section:', sect)
       for k,v in parser.items(sect):
          if( show ):
              print(' {} = {}'.format(k,v))
          if( k == 'fn_path') :
              IMAGE_FP = expanduser(v)
              checkDir(IMAGE_FP, False, 'Image ')
          if( k == 'fn_prefix'): IMAGE_PREFIX = v
          if( k == 'db_name'):   DB_NAME = v
          if( k == 'db_user'):   DB_USER = v
          if( k == 'db_pass'):   DB_PWD = v
          if( k == 'camera'):    CC_COMMAND = v
       if( show ):
           print()
###
def checkConfig(silent=False):
# Coded this function to use possible future robust validity checks
    isgood = True
    if( not checkDir(IMAGE_FP, False, "Image " )):
        print('Problem with image directory. Suggest you edit config file')
        isgood = False
    if( IMAGE_PREFIX == ''):
        print('Probem with image file prefix(is blank)')
        isgood = False
    if( DB_PWD == ''):
        print('Problem with database password(is blank)')
        isgood = False
    if( DB_USER == ''):
        print('Problem with database username(is blank)')
        isgood = False
    if( DB_NAME == ''):
        print('Problem with database name(is blank)')
        isgood = False
    if( not cameraCmdCheck( CC_COMMAND, True)):
        print('Problem with camera command')
        isgood = False
    return isgood
#########################################################

parser = configparser.ConfigParser()
if( not isfile(expanduser(CONFIG_FILE)) ):
    print('Cannot locate config file:',CONFIG_FILE)
    x = input('Create config file?[y/n]')
    if( x == 'y'):
        if( not inputConfig() ):
            print('inputConfig failed -- exiting')
            exit()
    else:
        print('Cannot proceed without config file -- exiting')
        exit()

done = False
loadConfig(False)
if( not checkConfig() ):
    ans = input('Do you wish to edit config file? [y] ')
    if( ans == 'y' or ans == '' ):
        inputConfig()
while ( not done ):
    x = input('(s)how, (e)dit or e(x)it? ')
    if( x == 's'):
        loadConfig(True)
    if( x == 'e'):
        inputConfig()
    if( x == 'x'):
        done = True
exit()
