__author__ = 'anthony'
try:
    import psycopg2
    import  sys
    from log import log
except ImportError,e:
    print "import error :", str(e)

log = log('pgrx.log')

class database(object):
    """class general db"""

    def __init__(self):
        self.connecction
        self.cursor
        self.date
        self.time
        self.version

    def executequery(self, query):
       self.cursor.execute(query)
       self.data = self.cursor.fetchall()
       self.connecction.commit()
       return self.data


    def executupdateequery(self, query):
        self.cursor.execute(query)
        self.data = self.cursor.statusmessage
        self.connecction.commit()
        return self.data


    def disconect(self):
        self.closecursor()
        self.connecction.close()

    def closecursor(self):
        self.cursor.close()


class databasepg(database):
    """class conecction to general PG"""

    def __init__(self,passwd,server="localhost",db="postgres",usr="postgres",port="5432"):
        try:
            self.connecction = psycopg2.connect(host=server,database=db, user=usr, port=port, password=passwd)
            self.cursor = self.connecction.cursor()
            self.con = 1
        except Exception, e:
            print 'Error connecting to server: ', str(e)
            log.info(str(e))
            self.con = 0
            sys.exit()




    def get_date(self):
        query = "select current_date::text"
        self.date = self.executequery(query)
        return self.date

    def get_time(self):
        query = "select to_char(current_timestamp,'HH24:MI:SS')"
        self.time = self.executequery(query)
        return self.time


    def get_version(self):
        query = "select  current_setting('server_version')"
        self.version = self.executequery(query)
        return self.version

    def get_tablespace(self):
        query = 'select spcname, round((pg_tablespace_size(spcname)/1024)/1024.0,2)::text from pg_tablespace'
        self.tablespace = self.executequery(query)
        return self.tablespace

    def get_uptime(self):
        query = "select substring (pg_postmaster_start_time()::text from 1 for position('.' in pg_postmaster_start_time()::text::text)-1)"
        self.time = self.executequery(query)
        return self.time

    def get_roles(self):
        query = 'SELECT rolname from pg_roles where rolcanlogin=false'
        self.roles = self.executequery(query)
        return self.roles


    def get_users(self):
       query = 'SELECT rolname from pg_roles where rolcanlogin=true'
       self.users = self.executequery(query)
       return self.users

    def get_databases(self):
       query = "select datname from pg_database  where datname not like 'template%'"
       self.databases = self.executequery(query)
       return self.databases

    def get_databases_count(self):
       query = "select count(datname) as cantidad from pg_database  where datname not like 'template%'"
       self.databases_count = self.executequery(query)
       return self.databases_count

    def get_databases_commit(self):
       query = "select datname,xact_commit from pg_stat_database  where datname not like 'template%' and xact_commit<>0 "
       self.databases_count = self.executequery(query)
       return self.databases_count

    def get_databases_rollback(self):
       query = "select datname,xact_rollback from pg_stat_database  where datname not like 'template%' and xact_rollback<>0"
       self.databases_count = self.executequery(query)
       return self.databases_count

    def get_databases_statitistic(self):
       query = "select datname,round(((pg_database_size(datname)/1024)/1024::numeric),2)::double precision,numbackends,xact_commit,xact_rollback,blks_read,blks_hit,tup_fetched,tup_inserted,tup_updated,tup_deleted from pg_stat_database   where datname not like 'template%'"
       self.databases_count = self.executequery(query)
       return self.databases_count


