import sqlite3
defaultpath = 'survey.db'

class SQLdb:
    def __init__(self, fn=defaultpath):
        'Open a survey db'
        # Connect to SQLITE3 db
        self.fn  = fn
        self.con = sqlite3.connect(fn)
        self.cur = self.con.cursor()
        self.log = []

    def reconnect(self):
        'Close the connection and open it again'
        self.cur.close()
        self.con.close()
        self.con = sqlite3.connect(self.fn)
        self.cur = self.con,cursor()
        
    def add_question_table(self, fn_in, overwrite=False):
        'Add table of questions to DB'
        #TODO: add backup flag: rename current db with timestamp and recreate db
        if overwrite:
            self.drop_table('questions')
        self.cur.execute('CREATE TABLE IF NOT EXISTS questions (num, text)')
        with open(fn_in,'r') as f:
            for line in f:
                # Example of line:
                # line = '23. I do work.'
                periodsplit = line.split('.')
                num = int(periodsplit[0])
                question = '.'.join(periodsplit[1:]).strip()
                #cur.execute('INSERT INTO questions VALUES (?,"?")',(num,question))#PROBABLY BROKEN
                self.cur.execute('INSERT INTO questions VALUES (%d,"%s")'%(num,question))
        # Commit
        self.con.commit()
    
    def drop_table(self, table):
        'Search for <table> in DB, deletes it if it exists'
        self.cur.execute('DROP TABLE IF EXISTS ?',(table))
        self.con.commit()
        # Reconnect needed when dropping tables
        self.reconnect()
    
    def fetch_question(self,num):
        '''
        Fetch a question with given <num> from question table in SQL db at <fn>
        Return value is a (int,str) tuple, or None if question table doesn't exist
        '''
        self.cur.execute('SELECT * FROM questions WHERE num=%d'%num)
        qn = self.cur.fetchone()
        return qn

    def close(self):
        'Close the db'
        self.cur.close()
        self.con.close()

if __name__ == '__main__':
    sql = SQLdb()
    sql.add_question_table('questions.txt')
    sql.close()
    del sql
