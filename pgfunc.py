import psycopg2

try:
    conn = psycopg2.connect("dbname=myduka user=postgres password=1958")

    cur = conn.cursor()
except Exception as e:
    print(e)
   
def fetch_data(tbname):
    try:
        q = "SELECT * FROM " + tbname + ";"
        cur.execute(q)
        records = cur.fetchall()
        return records
    except Exception as e:
        return e
    
def insert_products(v):
    vs = str(v)
    q = "insert into products(name,buying_price,selling_price,stock_quantity) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q

def insert_sales(v):
    vs = str(v)
    q = "insert into sales(pid,quantity,created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q

def sales_per_day():
    q = "SELECT * FROM sales_per_day;"
    cur.execute(q)
    results = cur.fetchall()
    return results

def sales_per_product():
    q = "SELECT * FROM sales_per_product;"
    cur.execute(q)
    results = cur.fetchall()
    return results
    
def user_credentials():
    q = "SELECT email, password FROM users;"
    cur.execute(q)
    results = cur.fetchall()
    return results
    

    
   

