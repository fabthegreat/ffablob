import psycopg2
from psycopg2.extensions import AsIs
import design
import datetime

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
        yearnow= datetime.datetime.now().year
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

def raceDB_to_race(race):
        cursor,connexion=db_initiate()
        cursor.execute("SELECT * from races WHERE id=%s AND racetype=%s ORDER BY rank;",(race.ID,race.racetype))
        rls = cursor.fetchall()
        for rl in rls:
            race.results.append({'errcode':rl[9],'rstl':list(rl[2:-1])})

        # convert timedelat to custom Time class object...

        db_finish(cursor,connexion)

def race_to_raceDB(race):
        cursor,connexion=db_initiate()
        for r in race.results:
            cursor.execute('INSERT INTO races (id,racetype,rank,time,name,runner_id,club,category,gender,errorcode) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(race.ID,race.racetype,r['rstl'][0],r['rstl'][1].time,r['rstl'][2],r['rstl'][3],r['rstl'][4],r['rstl'][5],r['rstl'][6],r['errcode']))
        db_finish(cursor,connexion)


if __name__ == '__main__':
    create_columns_record()
