from flask import Flask, render_template, request, redirect
from pgfunc import fetch_data, insert_products, insert_sales

# Create an object called app
# __name__ is used to tell Flask where to access HTML Files
# All HTML files are put inside "templates" folder
# All CSS/JS/ Images are put inside "static" folder
app = Flask(__name__)

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
   return render_template('sales.html', sales=sales)

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
   
@app.route('/addsales', methods=["POST","GET"])
def addsales():
   if request.method == "POST":
      pid=request.form["pid"]
      quantity=request.form["quantity"]
      created_at=request.form["created_at"]
      sale=(pid,quantity,created_at)
      insert_sales(sale)
      return redirect("/sales")
   

app.run()


