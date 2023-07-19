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
    q = "insert into products(name,buying_price,selling_price) "\
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
 
def update_product(p):
    q = "UPDATE products SET name = %s, buying_price = %s, selling_price = %s WHERE id = %s;"
    cur.execute(q,p)
    conn.commit()
    return q

def insert_stock(v):
    vs = str(v)
    q = "insert into stock(pid,quantity,created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q

# def user_credentials(full_name, email, password, confirm_password):
def user_credentials():
    q = "INSERT INTO users (full_name, email, password,confrim_password, created_at) VALUES (%s, %s, %s, %s, NOW());"
    cur.execute(q)
    conn.commit()
    return q

def get_users():
    q = "SELECT email, password FROM users;"
    cur.execute(q)
    results = cur.fetchall()
    return results






def remaining_stock():
    q = """SELECT 
            p.name,
            COALESCE(s.stock_quantity, 0) - COALESCE(sa.sales_quantity, 0) AS closing_stock
            FROM
                (SELECT pid, SUM(quantity) AS stock_quantity FROM stock GROUP BY pid) AS s
            LEFT JOIN
                (SELECT pid, SUM(quantity) AS sales_quantity FROM sales GROUP BY pid) AS sa
            ON s.pid = sa.pid
            JOIN products p ON s.pid = p.id;"""
    cur.execute(q)
    results = cur.fetchall()
    return results

def closing_stock(cur, product_id=None):
    q = """ SELECT 
            
            COALESCE(s.stock_quantity, 0) - COALESCE(sa.sales_quantity, 0) AS closing_stock
            FROM
                (SELECT pid, SUM(quantity) AS stock_quantity FROM stock GROUP BY pid) AS s
            LEFT JOIN
                (SELECT pid, SUM(quantity) AS sales_quantity FROM sales GROUP BY pid) AS sa
            ON s.pid = sa.pid
            WHERE s.pid = %s
            GROUP BY s.stock_quantity,sa.sales_quantity;"""
    cur.execute(q, (product_id,))
    results = cur.fetchall()
    if results:
        return results[0]
    else:
        return None

   
        
    

   
    
    
   
   
    
    

    
   

