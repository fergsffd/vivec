""" All the database related code """
import pymysql

DB_NAME = 'Shoes'
DB_USERNAME = 'ferg'
DB_PWD = 'fireman'

# Test DB access. Can I return itemized DB access failures?
def dbAvailable( dbn=DB_NAME, dbu=DB_USERNAME, dbp=DB_PWD):
    print('DB available?')
    return True

def dbCursor():
    print('dbCursor')
    return True

# Setup DB if not exist
def dbConfig():
    
