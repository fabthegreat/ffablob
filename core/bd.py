import psycopg2
import convertFFA2kikourou

def db_initiate(host="localhost",dbname="ffablob",user="ffablob",password="ffablob"):
    conn=psycopg2.connect(host="localhost",dbname="ffablob", user="ffablob",
                          password="ffablob")
    cur = conn.cursor()
    return cur,conn

def db_finish(cursor,connexion):
    connexion.commit()
    cursor.close()
    connexion.close()

def deco_db(func):
    def func_wrapper(*var):
        cursor,connexion=db_initiate()
        a=func(*var,cursor)
        db_finish(cursor,connexion)
        return a
    return func_wrapper

@deco_db
def check_race_new(race,cursor):
    cursor.execute("SELECT * from races WHERE race_id=%s AND epreuve=%s;",(race.race_ID,race.epreuve))
    test = cursor.fetchone()
    if test:
        return True #race exists
    else:
        return False #race does not exists

@deco_db
def insert_race_results(runner,race,cursor):
    cursor.execute("INSERT INTO race_results (rank,chrono,runner_name,runner_id,race_id,club,cat,gender,epreuve) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                   (len(race.results),race.results[-1]['temps'].chrono,runner.name,runner.runner_ID,race.race_ID,runner.club,runner.category,runner.gender,race.epreuve))

@deco_db
def insert_runner(runner,cursor):
    cursor.execute("INSERT INTO runners (runner_id,name,club,category) VALUES (%s,%s, %s, %s) ON CONFLICT DO NOTHING",
                    (runner.runner_ID,runner.name,runner.club,runner.category))

@deco_db
def insert_race(race,cursor):
    cursor.execute("INSERT INTO races (url,race_id,epreuve) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (race.urlFFA,race.race_ID,race.epreuve))


@deco_db
def fetch_race_results(race,cursor):
    cursor.execute("SELECT * from race_results WHERE race_id=%s AND epreuve=%s ORDER BY rank;",(race.race_ID,race.epreuve))
    test = cursor.fetchall()
    if test:
        for i,r in enumerate(test):
            runner_ = convertFFA2kikourou.Runner(runner_ID=r[5],name=r[1],club=r[4],category=r[2],gender=r[3])
            cr_=r[7]
            race.append_runner(runner_,cr_)





if __name__ == "__main__":
    race = convertFFA2kikourou.Race('http://bases.athle.com/asp.net/liste.aspx?frmbase=resultats&frmmode=1&frmespace=0&frmcompetition=184050&frmepreuve=30+Km')
    race.extract_runners()
    print(race.results)
    #print('Runners extracted')
    #fetch_race_results(race)
