""" All the database related code """
import pymysql

DB_NAME = 'mydb'
DB_USERNAME = 'cjferg'
DB_PWD = '9612729issiS#'
DB_WHERE = 'LOCALHOST'

# Test DB access. Can I return itemized DB access failures?
def dbAvailable( dbw=DB_WHERE,  dbu=DB_USERNAME, dbp=DB_PWD, dbn=DB_NAME):
    print('DB available?')
    isgood = True
    try:
        db = pymysql.connect(dbw,dbu,dbp,dbn)
    except pymysql.MySQLError as e:
        print('Got error {!r}, errno is {}'.format(e, e.args[0]))
        #print('Error Code:', err.errno)
        #print('SQLSTATE:', err.sqlstate)
        #print('Message:', err.msg)
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
##############################
dbAvailable(dbu='monsoon' )
