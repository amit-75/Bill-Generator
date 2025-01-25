from flask import *
import datetime
import sqlite3
import database
import re

app = Flask(__name__)
app.secret_key = 'asdf@75757'

def is_valid_seller(email,password):
	conn = sqlite3.connect('Database.db')
	cur = conn.cursor()
	cur.execute("SELECT * FROM seller WHERE email=? AND password=?",(email,password))
	data = cur.fetchall()
	if data:
		return True
	return False

def seller_data(email):
	conn = sqlite3.connect('Database.db')
	cur = conn.cursor()
	cur.execute("SELECT * FROM seller WHERE email=?", (email,))
	data = cur.fetchall()
	return data

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_mobile_number(mobile_number):
    if 6<= int(mobile_number[0]) <=9 and len(mobile_number)==10 :
        return True
    else:
        return False


# ********************************** Routes **********************************
@app.route('/',methods=['GET','POST'])
def index():
	msg = False
	if 'email' in session:
		msg = True
	return render_template('index.html',msg=msg)

@app.route('/signup',methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		seller_name = request.form.get('seller_name')
		mob_no = request.form.get('mob_no')
		email = request.form.get('email')
		shop_name = request.form.get('shop_name')
		address = request.form.get('address')

		if (username and password and seller_name and mob_no and email and shop_name and address != None):
			now = datetime.datetime.now()
			current_time = now.strftime('%Y-%m-%d %H:%M:%S')
			register_date = current_time

			# check email or phone number is valid or not
			if not is_valid_email(email):
				flash("Invalid email......!")
				return redirect(url_for("signup"))

			if not is_valid_mobile_number(mob_no):
				flash("Invalid mobile number...!")
				return redirect(url_for("signup"))

			conn = sqlite3.connect('Database.db')
			cur = conn.cursor()
			seller_email_user = cur.execute("SELECT * FROM seller WHERE email=? OR username=?",(email,username)).fetchall()
			if seller_email_user:
				flash("This email or username already registered!!")
				return redirect(url_for("signup"))
			cur.execute("INSERT INTO seller(username,password,seller_name,mob_no,email,shop_name,address,register_date) VALUES(?,?,?,?,?,?,?,?)",(username,password,seller_name,mob_no,email,shop_name,address,register_date,) )
			conn.commit()
			conn.close()
			return redirect(url_for('signin'))
		return "Required all details!!!!!!!!!!"
	return render_template('signup.html')

@app.route('/signin',methods=['GET','POST'])
def signin():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')

		if is_valid_seller(email,password):
			session['email'] = email
			return redirect(url_for('index'))
		else:
			return 'Invalid email or password'
	return render_template('signin.html')

@app.route('/create_bill',methods=['GET','POST'])
def create_bill():
	msg = True
	if request.method == 'POST':
		customer_name = request.form.get('customer_name')
		cus_mob = request.form.get('cus_mob')
		cus_email = request.form.get('cus_email')
		cus_address = request.form.get('cus_address')
		product = request.form.get('product')
		quantity = request.form.get('quantity')
		price = request.form.get('price')
		totle_amount = (int(quantity) * float(price))

		# check email or phone number is valid or not
		if not is_valid_email(cus_email):
			flash("Invalid email......!")
			return redirect(url_for("create_bill"))

		if not is_valid_mobile_number(cus_mob):
			flash("Invalid mobile number...!")
			return redirect(url_for("create_bill"))

		email_in_session = session['email']
		seller = seller_data(email_in_session)
		seller_id = int(seller[0][0])

		now = datetime.datetime.now()
		current_time = now.strftime('%Y-%m-%d %H:%M:%S')
		sale_date = current_time

		conn = sqlite3.connect('Database.db')
		cur = conn.cursor()
		cur.execute('''INSERT INTO sales(seller_id,customer_name,cus_mob,cus_email,cus_address,product,quantity,price,sale_date,totle_amount) VALUES(?,?,?,?,?,?,?,?,?,?)''',(seller_id,customer_name,cus_mob,cus_email,cus_address,product,quantity,price,sale_date,totle_amount) )
		conn.commit()
		conn.close()
		customer_detail = [customer_name, cus_address, cus_mob, sale_date]
		seller_detail = [seller[0][6], seller[0][7], seller[0][4]]
		product_detail = [product, quantity, price, totle_amount]
		return render_template('bill_template.html', customer_detail=customer_detail, seller_detail=seller_detail, product_detail=product_detail)
	return render_template('create_bill.html', msg = msg)

@app.route('/my_sales',methods=['GET'])
def my_sales():
	msg = True	
	email_in_session = session['email']
	seller = seller_data(email_in_session)
	seller_id = int(seller[0][0])

	conn = sqlite3.connect('Database.db')
	cur = conn.cursor()
	cur.execute("SELECT * FROM sales WHERE seller_id = ?",(seller_id,))
	sales_data = cur.fetchall()
	return render_template('mysales.html',sales_data=sales_data, msg=msg)

@app.route('/profile', methods=['GET'])
def profile():
	msg = True
	email_in_session = session['email']
	seller = seller_data(email_in_session)
	seller_id = int(seller[0][0])

	conn = sqlite3.connect('Database.db')
	cur = conn.cursor()
	cur.execute("SELECT username,seller_name,mob_no,email,shop_name,address,register_date FROM seller WHERE id=?", (seller_id,))
	data = cur.fetchall()
	return render_template('profile.html',data=data, msg=msg)

@app.route('/printbill/<int:sale_id>')
def printbill(sale_id):
	msg = True
	conn = sqlite3.connect('Database.db')
	cur = conn.cursor()
	cur.execute("SELECT * FROM sales WHERE id=?",(sale_id,))
	sales_data = cur.fetchall()
	cur.close()

	conn = sqlite3.connect('Database.db')
	cur = conn.cursor()
	cur.execute("SELECT shop_name,address,mob_no,email FROM seller WHERE id=?",(sales_data[0][1],))
	seller = cur.fetchall()
	cur.close()

	customer_detail = [sales_data[0][2], sales_data[0][5], sales_data[0][3], sales_data[0][10]]
	product_detail = [sales_data[0][6], sales_data[0][7], sales_data[0][8], sales_data[0][9]]
	seller_detail = [seller[0][0], seller[0][1], seller[0][2], seller[0][3]]
	return render_template('bill_template.html', customer_detail=customer_detail, seller_detail=seller_detail, product_detail=product_detail)

@app.route('/logout')
def logout():
	session.pop('email')
	return redirect(url_for('signin'))

if __name__ == ('__main__'):
	app.run(debug=True)