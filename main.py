from flask import Flask, render_template, request, redirect, url_for, session
from pgfunc import fetch_data, insert_products, insert_sales,sales_per_day, sales_per_product, user_credentials, update_product
import pygal

# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder
# All CSS/JS/ Images are put inside "static" folder
app = Flask(__name__)
app.secret_key = "ken2020"

# a route is an extension of url which loads you a html page
# @ - a decorator(its in-built ) make something be static
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products():
   prods = fetch_data("products")
   return render_template('products.html', products=prods)
  
@app.route("/sales")
def sales():
   sales = fetch_data("sales")
   prods = fetch_data("products")
   return render_template('sales.html', sales=sales, prods=prods)

@app.route('/addproducts', methods=["POST","GET"])
def addproducts():
   if request.method == "POST":
      name=request.form["name"]
      buying_price=request.form["buying_price"]
      selling_price=request.form["selling_price"]
      stock_quantity=request.form["stock_quantity"]
      product=(name,buying_price,selling_price,stock_quantity)
      insert_products(product)
      return redirect("/products")
   
@app.route('/editproduct', methods=["POST", "GET"])
def editproduct():
    if request.method == "POST":
      id = request.form['id']
      name = request.form['name']
      buying_price = request.form['buying_price']
      selling_price = request.form['selling_price']
      stock_quantity = request.form['stock_quantity']
      product=(name,buying_price,selling_price,stock_quantity,id)
      update_product(product)
      return redirect("/products")
    
@app.route('/addsales', methods=["POST","GET"])
def addsales():
   if request.method == "POST":
      pid=request.form["pid"]
      quantity=request.form["quantity"]
      sale=(pid,quantity,'now()')
      insert_sales(sale)
      return redirect("/sales")
   
@app.route("/dashboard")
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
   # To get raw SVG data for the 2 graphs above, and passing them into the template.
   chart = chart.render_data_uri()
   bar_chart = bar_chart.render_data_uri()
   return render_template('dashboard.html', chart=chart, bar_chart=bar_chart)

@app.route('/login', methods=["POST","GET"])
def login():
   if request.method == "POST":
      user = request.form["email_address"]
      session["user"] = user
      return redirect(url_for("user"))
   else:
      if "name" in session:
         return redirect(url_for("login"))
   login = user_credentials()
   email = []
   password = []
   for i in login:
         email, password = i
         print(email,password)
   return render_template('login.html', login=login)

@app.route('/user')
def user():
   if "user" in session:
      user = session["user"]
      return f"{user}"
   else:
      return redirect(url_for("login"))
   
@app.route('/logout')
def logout():
   session.pop("user", default=None)
   return redirect(url_for("login"))

@app.route('/register', methods=["POST","GET"])
def register():
   return render_template("register.html")

app.run(debug=True)