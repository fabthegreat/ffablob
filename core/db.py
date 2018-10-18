import urllib.parse
import psycopg2
from psycopg2.extensions import AsIs
import design
from datetime import datetime,timedelta

def db_initiate(host="localhost",dbname="ffablob",user="ffablob",password="ffablob"):
    conn=psycopg2.connect(host="localhost",dbname="ffablob", user="ffablob",
                          password="ffablob")
    cur = conn.cursor()
    return cur,conn

def db_finish(cursor,connexion):
    connexion.commit()
    cursor.close()
    connexion.close()

def create_columns_record():
        cursor,connexion=db_initiate()
        yearnow= datetime.now().year
        yearlist = [yearnow - i for i in range(4)]
        racetypes=['10k','15k','21k','42k']

        column_list=['record_' + y + '_' + str(x) for x in yearlist for y in racetypes]
        for rc in column_list:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='runners' and column_name=%s;",(rc,))
            clmn = cursor.fetchone()
            if clmn:
                pass
            else:
                cursor.execute('ALTER TABLE runners ADD COLUMN %s interval',(AsIs(rc),))
        db_finish(cursor,connexion)

def check_race_exists(race):
        cursor,connexion=db_initiate()
        cursor.execute('SELECT * from races WHERE id=%s AND racetype=%s;',(race.ID,race.racetype))
        test = cursor.fetchone()
        db_finish(cursor,connexion)
        if test:
            return True #race exists
        else:
            return False #race does not exists

def delete_race(race):
        cursor,connexion=db_initiate()
        cursor.execute("DELETE from races WHERE id=%s AND racetype=%s;",(race.ID,race.racetype))
        db_finish(cursor,connexion)

def check_runner_exists(runner):
        cursor,connexion=db_initiate()
        cursor.execute('SELECT * from runners WHERE runner_id=%s;',(runner.ID,))
        test = cursor.fetchone()
        db_finish(cursor,connexion)
        if test:
            return True #race exists
        else:
            return False #race does not exists

def raceDB_to_race(race):
        cursor,connexion=db_initiate()
        cursor.execute("SELECT * from races WHERE id=%s AND racetype=%s ORDER BY rank;",(race.ID,race.racetype))
        rls = cursor.fetchall()
        #fetch race_name based on the first result line
        race.name = rls[0][10]
        race.date = rls[0][11]
        for rl in rls:
            rank = rl[2]
            time = design.TimeNew.time_from_timedelta(rl[3])
            name = rl[4]
            runner_ID = rl[5]
            club = rl[6]
            cat = rl[7]
            gender = rl[8]
            errcode = rl[9]
            #TODO: replace column number

            race.results.append({'errcode':errcode,'rstl':[rank,time,name,runner_ID,club,cat,gender]})
        #TODO: convert timedelat to custom Time class object...

        db_finish(cursor,connexion)

def race_to_raceDB(race):
        cursor,connexion=db_initiate()
        for r in race.results:
            cursor.execute('INSERT INTO races \
                           (id,racetype,race_name,rank,time,name,runner_id,club,category,gender,errorcode,race_date) \
                           VALUES \
                           (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(race.ID,race.racetype,race.name,r['rstl'][0],r['rstl'][1].time,r['rstl'][2],r['rstl'][3],r['rstl'][4],r['rstl'][5],r['rstl'][6],r['errcode'],race.date))
        db_finish(cursor,connexion)

def reset_races():
        cursor,connexion=db_initiate()
        cursor.execute('TRUNCATE TABLE races;')
        db_finish(cursor,connexion)

def runner_to_runnerDB(runner):
        cursor,connexion=db_initiate()

        cursor.execute('INSERT INTO runners \
                       (runner_id,name,club,category,gender) VALUES \
                       (%s,%s,%s,%s,%s)',(runner.ID,runner.name,runner.club, \
                       runner.category,runner.gender))

        for label,rst in runner.records.items():
            if rst:
                cursor.execute('UPDATE runners SET %s = %s WHERE runner_id = \
                               %s;',(AsIs(label),rst.time,runner.ID))
        db_finish(cursor,connexion)

def runnerDB_to_runner(runner):
        cursor,connexion=db_initiate()
        cursor.execute("SELECT * from runners WHERE runner_id=%s;",(runner.ID,))
        rls = cursor.fetchall()
        rls = [i for i in rls[0]]
        runner.name = rls[1]
        runner.club = rls[2]
        runner.category = rls[3]
        runner.gender = rls[4]

        #TODO: try to fetch according to keys and not indexes
        yearnow= datetime.now().year
        yearlist = range(yearnow,yearnow-4,-1)
        racetypes=['10','15','21','42']
        columnlist = ['record_'+rt+'k_'+str(y) for y in yearlist for rt in racetypes]
        runner.records = dict(zip(columnlist,[design.TimeNew.time_from_timedelta(tm) if tm is not None else None for tm in rls[5:]]))

        db_finish(cursor,connexion)

def search_DB(text):
        cursor,connexion=db_initiate()
        if text:
            cursor.execute("SELECT * from races WHERE to_tsvector('french',race_name||' '||racetype) @@ plainto_tsquery('french',%s);",(text,))
        else:
            cursor.execute("SELECT * from races")
        search_rst = cursor.fetchall()
#SELECT title FROM pgweb WHERE to_tsvector('english', body) @@ to_tsquery('english', 'friend');
        db_finish(cursor,connexion)
        return search_rst

def collect_races():
        cursor,connexion=db_initiate()
        cursor.execute("SELECT * from races;")
        races = set([(race[0],race[1]) for race in cursor.fetchall()])
        db_finish(cursor,connexion)
        return races


if __name__ == '__main__':
        #create_columns_record()
        #print(sort_search(search_DB('Trail')))

        print(collect_races())
