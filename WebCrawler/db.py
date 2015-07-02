import MySQLdb


_connection = None

def get_connection():
    global _connection
    if not _connection:
        _connection = MySQLdb.connect(host="xxx.com", # your host, usually localhost
                 user="xxx", # your username
                  passwd="xxx", # your password
                  db="xxx") 
    return _connection

# List of stuff accessible to importers of this module. Just in case
__all__ = ['getConnection']
	
## Edit: actually you can still refer to db._connection
##         if you know that's the name of the variable.
## It's just left out from enumeration if you inspect the module

# import db
# conn = db.get_connection() # This will always return the same object