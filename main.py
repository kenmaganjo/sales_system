from flask import Flask, render_template, request, redirect, url_for,flash,session,send_file
import psycopg2
from pgfunc import fetch_data, insert_products, insert_sales,sales_per_day, revenue_per_day,revenue_per_month, sales_per_product, user_credentials, get_users, update_product, insert_stock, remaining_stock, closing_stock, product_id
import pygal
from datetime import datetime, timedelta
from functools import wraps
import barcode
from PIL import Image
from barcode import generate
from barcode import Code128
from barcode.writer import ImageWriter
import os
import pandas as pd
conn = psycopg2.connect("dbname=myduka user=postgres password=1958")
cur = conn.cursor()
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "ken2020"

# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder
# All CSS/JS/ Images are put inside "static" folder
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

@app.route('/addsales', methods=["POST", "GET"])
def addsales():
    if request.method == "POST":
        pid_from_form = int(request.form["pid"])
        quantity = int(request.form["quantity"])
        # Retrieve the remaining stock for all products as a list of dictionaries
        remaining_stock_results = remaining_stock()
        # Convert the list of dictionaries to a dictionary with "pid" as key and "closing_stock" as value
        remaining_stock_dict = {result["pid"]: result["closing_stock"] for result in remaining_stock_results}
        if pid_from_form not in remaining_stock_dict:
            flash("The product is out of stock. Kindly restock.", category="error")
            return redirect("/sales")
        available_stock = remaining_stock_dict[pid_from_form]
        if quantity > available_stock:
            flash("The quantity you have entered exceeds our current stock. Kindly input a valid quantity within the available stock limit.", category="error")
            return redirect("/sales")
        else:
     
            sale = (pid_from_form, quantity, 'now()')
            insert_sales(sale)
            flash("Congratulations! The sale has been successfully completed!", category="success")
            return redirect("/sales")
    else:
        flash("The sale did not go through. Please try again.", category="error")
        return redirect("/sales")

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
   #Line chart to show sales quantity per day
   daily_sales = sales_per_day()
   dates = []
   sales = []
   for i in daily_sales:
      dates.append(i[0])
      sales.append(i[1])
   chart = pygal.Line()
   chart.title = "Sales Quantity per Day"
   chart.x_labels = dates
   chart.add("Sales", sales)
   #Chart to show sales quantity per product
   product_sale = sales_per_product()
   product_name = []
   sales = []
   for i in product_sale:
      product_name.append(i[0])
      sales.append(i[1])
   bar_chart = pygal.Bar()
   bar_chart.title = 'Sales Quantity per Product'
   bar_chart.x_labels = product_name
   bar_chart.add('Sales', sales)
   #Graph to show remaining stock.
   stock_data = remaining_stock()
   product_names = []
   stock_remaining = []
   for data in stock_data:
        product_name = data.get('name')  
        closing_stock = int(data.get('closing_stock', 0))  
        if product_name:
            product_names.append(product_name)
            stock_remaining.append(closing_stock)
   bar_graph = pygal.Bar()
   bar_graph.title = 'Remaining Stock per Product'
   bar_graph.x_labels = product_names
   bar_graph.add('Stock(Qty)', stock_remaining)
   #Graph to show revenue per day
   daily_revenue = revenue_per_day()
   dates = []
   sales_revenue_per_day = [] 
   for i in daily_revenue:
    dates.append(i[0])
    sales_revenue_per_day.append(i[1]) 
   line_chart = pygal.Line()
   line_chart.title = "Sales Revenue per Day"
   line_chart.x_labels = dates
   line_chart.add("Revenue(KSh)", sales_revenue_per_day)
   #Graph to show revenue per month
   monthly_revenue = revenue_per_month()
   dates = []
   sales_revenue_per_month = [] 
   for i in monthly_revenue:
    dates.append(i[0])
    sales_revenue_per_month.append(i[1]) 
   line_graph = pygal.Line()
   line_graph.title = "Sales Revenue per Month"
   line_graph.x_labels = dates
   line_graph.add("Revenue(KSh)", sales_revenue_per_month)

   line_graph = line_graph.render_data_uri()
   line_chart = line_chart.render_data_uri()
   bar_graph = bar_graph.render_data_uri()
   chart = chart.render_data_uri()
   bar_chart = bar_chart.render_data_uri()
   return render_template('dashboard.html', chart=chart, bar_chart=bar_chart, bar_graph=bar_graph, line_chart=line_chart, line_graph=line_graph)

@app.context_processor
def inject_remaining_stock():
    def remain_stock(product_id=None):
        stock = closing_stock(cur, product_id) 
        return stock if stock is not None else 0
    return {'remain_stock': remain_stock}

@app.context_processor
def inject_datetime():
    now = datetime.now()
    return {'current_date': now.strftime('%d-%m-%Y'), 'current_time': now.strftime('%I:%M:%S %p')}

@app.context_processor
def generate_barcode():
    ids = product_id()
    barcode_paths = [f"static/barcode/{pid}.png" for pid_tuple in ids
                     for pid in [pid_tuple[0]]
                     if isinstance(pid_tuple[0], int)] 

    for pid_tuple, barcode_path in zip(ids, barcode_paths):
        pid = pid_tuple[0]
        code = Code128(str(pid), writer=ImageWriter())
        code.save(barcode_path)
    return {'generate_barcode': generate_barcode}
   
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
        hashed_password = generate_password_hash(confirm_password)
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
                        (full_name, email, hashed_password, hashed_password))
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

@app.route('/export', methods=['POST'])
def export_data():
    prods = fetch_data("products")
    # Creating a DataFrame from the retrieved data
    df = pd.DataFrame(prods, columns=["id", "name", "buying_price", "selling_price", "bar_code"])
     # Convert numeric columns to numeric format
    numeric_columns = ["buying_price", "selling_price"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
    df = df.sort_values(by="id")
    file_path = os.path.join("downloads", "exported_products.xlsx")
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

@app.route('/import', methods=['POST'])
def import_data():
    if 'file' not in request.files:
        return "No file part" 
    file = request.files['file']    
    if file.filename == '':
        return "No selected file"
    if file:    
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)
        df = pd.read_excel(file_path)
        #Insert data into the "products" table
        for index, row in df.iterrows():
            values = (row['name'], row['buying_price'], row['selling_price'])
            insert_products(values)
        os.remove(file_path)
        flash('Data imported successfully!', category='success')
        return redirect("/products")
    return "Import failed"

if not os.path.exists('uploads'):
        os.makedirs('uploads')

if not os.path.exists('downloads'):
        os.makedirs('downloads')

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
    flash('"You have been logged out. To regain access, please log in."', category='error')
    return redirect('/')       


app.run(debug=True)



