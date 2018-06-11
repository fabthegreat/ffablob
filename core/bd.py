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
        func(*var,cursor)
        db_finish(cursor,connexion)
    return func_wrapper

@deco_db
def insert_race_results(runner,race,cursor):
    cursor.execute("INSERT INTO runners (rank,chrono,runner_name,runner_id,race_id,club,cat,gender) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (rank,chrono,runner.name,runner.runner_ID,runner.club,runner.category,'test'))

@deco_db
def insert_runner(runner,cursor):
    cursor.execute("INSERT INTO runners (runner_id,name,club,category) VALUES (%s,%s, %s, %s)",
                (runner.runner_ID,runner.name,runner.club,runner.category))

@deco_db
def insert_race(race,cursor):
    cur.execute("INSERT INTO race_results (chrono,runner_id,runner_id) VALUES (%s, %s, %s)",
                (runner.runner_ID,runner.name,runner.club,runner.category))
