import sqlite3

conn = sqlite3.connect('Database.db')
cur = conn.cursor()

cur.execute('''
				CREATE TABLE IF NOT EXISTS seller
				(
					id INTEGER primary key,
					username TEXT,
					password TEXT,
					seller_name TEXT,
					mob_no TEXT,
					email TEXT,
					shop_name TEXT,
					address TEXT,
					register_date TEXT
				)
			''')

cur.execute('''
				CREATE TABLE IF NOT EXISTS sales
				(
					id INTEGER primary key,
					seller_id INTEGER,
					customer_name TEXT,
					cus_mob TEXT,
					cus_email TEXT,
					cus_address TEXT,
					product TEXT,
					quantity INTEGER,
					price REAL,
					totle_amount Real,
					sale_date TEXT
				)
			''')

conn.commit()
conn.close()
