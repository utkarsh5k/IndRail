import MySQLdb

def connection():
	conn=MySQLdb.connect(host="localhost",user="root", passwd="utkarsh@mit", db="Indrail")
	cur= conn.cursor()
	return cur, conn
