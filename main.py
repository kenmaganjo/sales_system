from flask import Flask, render_template, request, redirect, url_for,flash,session,g
import psycopg2
from pgfunc import fetch_data, insert_products, insert_sales,sales_per_day, sales_per_product, user_credentials, get_users, update_product, insert_stock, remaining_stock, closing_stock
import pygal
from datetime import datetime, timedelta
from functools import wraps
conn = psycopg2.connect("dbname=myduka user=postgres password=1958")
cur = conn.cursor()
from werkzeug.security import generate_password_hash, check_password_hash

# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder
# All CSS/JS/ Images are put inside "static" folder
app = Flask(__name__)
app.secret_key = "ken2020"

# a route is an extension of url which loads you a html page
# @ - a decorator(its in-built ) make something be static

def login_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if not session.get('logged_in') and not session.get('registered'):
            return redirect('/login') 
        return view_func(*args, **kwargs)
    return decorated_view

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/products")
@login_required
def products():
   prods = fetch_data("products")
   return render_template('products.html', products=prods)
 
@app.route('/addproducts', methods=["POST","GET"])
def addproducts():
   if request.method == "POST":
      name=request.form["name"]
      buying_price=request.form["buying_price"]
      selling_price=request.form["selling_price"]
      product=(name,buying_price,selling_price)
      insert_products(product)
      flash("Success! The product has been added successfully!", category="success")
      return redirect("/products")
   else:
      flash("The product could not be added at this moment. Please try again.", category="error")
   
@app.route('/editproduct', methods=["POST", "GET"])
def editproduct():
    if request.method == "POST":
      id = request.form['id']
      name = request.form['name']
      buying_price = request.form['buying_price']
      selling_price = request.form['selling_price']
      product=(name,buying_price,selling_price,id)
      update_product(product)
      flash("Success! The product has been edited successfully!", category="success")
      return redirect("/products")
    else:
      flash("The product could not be edited at this moment. Please try again.", category="error")
    
@app.route("/sales")
@login_required
def sales():
   sales = fetch_data("sales")
   prods = fetch_data("products")
   return render_template('sales.html', sales=sales, prods=prods)
    
@app.route('/addsales', methods=["POST","GET"])
def addsales():
   if request.method == "POST":
      pid=request.form["pid"]
      quantity=request.form["quantity"]
      sale=(pid,quantity,'now()')
      insert_sales(sale)
      flash("Congratulations! The sale has been successfully completed!", category="success")
      return redirect("/sales")
   else:
      flash("The sale did not go through. Please try again.", category="error")
   
@app.route("/stock")
@login_required
def stock():
   stock = fetch_data("stock")
   prods = fetch_data("products")
   return render_template('stock.html', stock=stock, prods=prods)

@app.route('/addstock', methods=["POST","GET"])
def addstock():
   if request.method == "POST":
      pid=request.form["pid"]
      quantity=request.form["quantity"]
      stock=(pid,quantity,'now()')
      insert_stock(stock)
      flash("Success! The stock has been successfully added!", category="success")
      return redirect("/stock")
   else:
      flash("The item could not be added at this moment. Please try again.", category="error")

@app.route("/dashboard")
@login_required
def dashboard():
   # Line chart to show sales per day
   daily_sales = sales_per_day()
   dates = []
   sales = []
   for i in daily_sales:
      dates.append(i[0])
      sales.append(i[1])
   chart = pygal.Line()
   chart.title = "Sales per Day"
   chart.x_labels = dates
   chart.add("Sales", sales)
   # Bar chart to show sales per product
   product_sale = sales_per_product()
   product_name = []
   sales = []
   for i in product_sale:
      product_name.append(i[0])
      sales.append(i[1])
   bar_chart = pygal.Bar()
   bar_chart.title = 'Sales per Product'
   bar_chart.x_labels = product_name
   bar_chart.add('Sales', sales)
   # Bar graph to show remaining stock.
   stock_data = remaining_stock()
   product_names = []
   stock_remaining = []

   for name, quantity in stock_data:
        product_names.append(name)
        stock_remaining.append(quantity)

   bar_graph = pygal.Bar()
   bar_graph.title = 'Remaining Stock'
   bar_graph.x_labels = product_names
   bar_graph.add('Stock', stock_remaining)

   bar_graph = bar_graph.render_data_uri()
   chart = chart.render_data_uri()
   bar_chart = bar_chart.render_data_uri()
   return render_template('dashboard.html', chart=chart, bar_chart=bar_chart, bar_graph=bar_graph)
# To add remaining stock field to the products table.
@app.context_processor
def inject_remaining_stock():
    def remain_stock(product_id=None):
        stock = closing_stock(cur, product_id)  # Pass the database cursor as an argument
        return stock[0] if stock is not None else 0
    return {'remain_stock': remain_stock}



@app.route('/signup', methods=["POST", "GET"])
def user_added():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Validation checks before registration
        if len(full_name) < 1:
            flash('Full name must be greater than 1 character.', category='error')
            return redirect("/register")
        elif len(email) < 10:
            flash('Email must be greater than 10 characters.', category='error')
            return redirect("/register")
        elif password != confirm_password:
            flash('Passwords don\'t match. Please try again', category='error')
            return redirect("/register")
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', category='error')
            return redirect("/register")

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        # To check if the email already exists in the database
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            if result[0] > 0:
                flash('Email already exists! Please use another email!', category='error')
                return redirect("/register")
            else:
                # Adding the new user to the database, after all checks are passed.
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (full_name, email, password, confirm_password, created_at) VALUES (%s, %s, %s, %s, now())",
                        (full_name, email, hashed_password, confirm_password))
                conn.commit()
                flash('Account created successfully!', category='success')

    session['registered'] = True
    return render_template("index.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users = get_users()
        if users:
            for user in users:
                db_email = user[0]
                db_password_hash = user[1]

                if db_email == email and check_password_hash(db_password_hash, password):
                    flash('Authentication has been successfully verified!', category='success')
                    session['logged_in'] = True
                    return redirect("/")
            else:
                flash('Incorrect email or password, please try again.', category='error')
                return redirect("/login")

    return render_template("login.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'),404
    

@app.route("/register") 
def register():
   return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out. Would you like to gain access? Kindly log in.', category='error')
    return redirect('/login')

app.run(debug=True)