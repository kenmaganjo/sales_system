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

def revenue_per_day():
    q = "SELECT TO_CHAR(DATE(s.created_at), 'DD-MM-YYYY') AS sale_date, SUM(s.quantity * p.selling_price) AS revenue FROM sales s JOIN products p ON s.pid = p.id GROUP BY DATE(s.created_at) ORDER BY DATE(s.created_at) DESC;"
    cur.execute(q)
    results = cur.fetchall()
    return results

def net_profit_per_day():
    q = """SELECT
        transaction_date,
        gross_profit - COALESCE(SUM(amount), 0) AS net_profit
        FROM (
        SELECT
            DATE(s.created_at) AS transaction_date,
            SUM(s.quantity * (p.selling_price - p.buying_price)) AS gross_profit
        FROM sales s
        JOIN products p ON s.pid = p.id
        GROUP BY DATE(s.created_at)
        ) AS gross_profit_table
        LEFT JOIN expenses e ON gross_profit_table.transaction_date = DATE(e.created_at)
        GROUP BY gross_profit_table.transaction_date, gross_profit
        ORDER BY gross_profit_table.transaction_date DESC;"""
    cur.execute(q)
    results = cur.fetchall()
    return results

def net_profit_per_month():
    q = """WITH MonthlyExpenses AS (
        SELECT TO_CHAR(created_at, 'MM-YYYY') AS month,
           SUM(amount) AS expenses
        FROM expenses
        GROUP BY TO_CHAR(created_at, 'MM-YYYY')
        ),
        MonthlyRevenue AS (
        SELECT TO_CHAR(s.created_at, 'MM-YYYY') AS month,
           SUM(s.quantity * p.selling_price) AS revenue,
           SUM(s.quantity * p.buying_price) AS cogs
        FROM sales s
        JOIN products p ON s.pid = p.id
        GROUP BY TO_CHAR(s.created_at, 'MM-YYYY')
        )
        SELECT m.month,
            COALESCE(r.revenue, 0) - COALESCE(e.expenses, 0) - COALESCE(r.cogs, 0) AS net_profit
        FROM (
            SELECT DISTINCT month FROM MonthlyExpenses
        UNION
            SELECT DISTINCT month FROM MonthlyRevenue
        ) m
        LEFT JOIN MonthlyRevenue r ON m.month = r.month
        LEFT JOIN MonthlyExpenses e ON m.month = e.month
        ORDER BY m.month DESC;"""
    cur.execute(q)
    results = cur.fetchall()
    return results

def revenue_per_month():
    q = "SELECT TO_CHAR(s.created_at, 'MM-YYYY') AS sale_month, SUM(s.quantity * p.selling_price) AS revenue FROM sales s JOIN products p ON s.pid = p.id GROUP BY TO_CHAR(s.created_at, 'MM-YYYY') ORDER BY TO_CHAR(s.created_at, 'MM-YYYY') DESC;"
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

def insert_expense(v):
    vs = str(v)
    q = "insert into expenses(name,category,amount,created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q

def update_expense(p):
    q = "UPDATE expenses SET name = %s, category = %s, amount = %s WHERE id = %s;"
    cur.execute(q,p)
    conn.commit()
    return q

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
            p.name, p.id as pid,
            COALESCE(s.stock_quantity, 0) - COALESCE(sa.sales_quantity, 0) AS closing_stock
            FROM
                (SELECT pid, SUM(quantity) AS stock_quantity FROM stock GROUP BY pid) AS s
            LEFT JOIN
                (SELECT pid, SUM(quantity) AS sales_quantity FROM sales GROUP BY pid) AS sa
            ON s.pid = sa.pid
            JOIN products p ON s.pid = p.id;"""
    cur.execute(q)
    results = cur.fetchall()
    # Convert the list of tuples to a list of dictionaries
    column_names = [desc[0] for desc in cur.description]
    results_as_dicts = [dict(zip(column_names, row)) for row in results]
    return results_as_dicts

def closing_stock(cur, product_id=None):
    q = """
    SELECT
        COALESCE(s.stock_quantity, 0) - COALESCE(sa.sales_quantity, 0) AS closing_stock
    FROM
        (SELECT pid, SUM(quantity) AS stock_quantity FROM stock GROUP BY pid) AS s
    LEFT JOIN
        (SELECT pid, SUM(quantity) AS sales_quantity FROM sales GROUP BY pid) AS sa
    ON s.pid = sa.pid
    """
    if product_id is not None:
        q += " WHERE s.pid = %s"
        cur.execute(q, (product_id,))
    else:
        cur.execute(q)

    result = cur.fetchone()
    return result[0] if result else 0

def product_id():
    q = "SELECT id FROM products;"
    cur.execute(q)
    results = cur.fetchall()
    return results


    

   
        
    

   
    
    
   
   
    
    

    
   

