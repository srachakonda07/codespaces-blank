import datetime
from flask import Flask, request, jsonify, session
import psycopg2
import os
import logging
from flask_cors import CORS
from prefix_middleware import PrefixMiddleware
import msal
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
CORS(app)
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api')

conn = psycopg2.connect(os.environ.get("db_url"))
cur = conn.cursor()

# Configure MSAL client
msal_client = msal.ConfidentialClientApplication(
    client_id='your_client_id',
    client_credential='your_client_secret',
    authority='https://login.microsoftonline.com/your_tenant_id',
)

# Decorator to require authentication
def require_auth(view_func):
    @wraps(view_func)
    def decorated(*args, **kwargs):
        if 'access_token' not in session:
            return 'Unauthorized', 401
        return view_func(*args, **kwargs)
    return decorated


logging.basicConfig(filename='app_logger.log', level=logging.INFO)

@app.route('/search', methods=['POST'])
def search():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    query = data['query']
    conn.rollback()
    cur.execute(f"SELECT * FROM suppliers WHERE name LIKE '%{query}%'")
    suppliers = cur.fetchall()
    cur.execute(f"SELECT * FROM products WHERE name LIKE '%{query}%'")
    products = cur.fetchall()
    cur.execute(f"SELECT * FROM purchase_orders WHERE order_status LIKE '%{query}%'")
    orders = cur.fetchall()
    logging.info(f'Search executed for query: {query}')
    return jsonify({'suppliers': suppliers, 'products': products, 'orders': orders})

@app.route('/filter', methods=['POST'])
def filter():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    filter_type = data['type']
    filter_value = data['value']
    conn.rollback()
    cur.execute(f"SELECT * FROM {filter_type} WHERE name LIKE '%{filter_value}%'")
    results = cur.fetchall()
    logging.info(f'Filter executed for type: {filter_type} and value: {filter_value}')
    return jsonify({'results': results})

@app.route('/multiple_search', methods=['POST'])
def multiple_search():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    queries = data['queries']
    results = []
    conn.rollback()
    for query in queries:
        cur.execute(f"SELECT * FROM suppliers WHERE name LIKE '%{query}%'")
        suppliers = cur.fetchall()
        cur.execute(f"SELECT * FROM products WHERE name LIKE '%{query}%'")
        products = cur.fetchall()
        cur.execute(f"SELECT * FROM purchase_orders WHERE order_status LIKE '%{query}%'")
        orders = cur.fetchall()
        results.append({'suppliers': suppliers, 'products': products, 'orders': orders})
    logging.info(f'Multiple search executed for queries: {queries}')
    return jsonify({'results': results})





logging.basicConfig(filename='app_logger.log', level=logging.INFO)

@app.route('/dashboard', methods=['GET'])
def get_dashboard():
    conn.rollback()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM dashboard_preferences WHERE user_id = %s", (request.args.get('user_id'),))
        dashboard_preferences = cur.fetchall()
        logging.info('Fetched dashboard preferences for user_id: %s', request.args.get('user_id'))
        return jsonify(dashboard_preferences), 200
    except Exception as e:
        logging.error('Failed to fetch dashboard preferences: %s', e)
        return jsonify({'error': 'Failed to fetch dashboard preferences'}), 500

@app.route('/alerts', methods=['GET'])
def get_alerts():
    conn.rollback()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM alerts WHERE user_id = %s", (request.args.get('user_id'),))
        alerts = cur.fetchall()
        logging.info('Fetched alerts for user_id: %s', request.args.get('user_id'))
        return jsonify(alerts), 200
    except Exception as e:
        logging.error('Failed to fetch alerts: %s', e)
        return jsonify({'error': 'Failed to fetch alerts'}), 500





logging.basicConfig(filename='app_logger.log', level=logging.INFO)

@app.route('/api/reporting', methods=['POST'])
def reporting():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        cur.execute("INSERT INTO reports (user_id, report_type, report_data) VALUES (%s, %s, %s)",
                    (data['user_id'], data['report_type'], data['report_data']))
        conn.commit()
        logging.info('Report created successfully')
        return jsonify({"message": "Report created successfully"}), 201
    except Exception as e:
        logging.error(str(e))
        conn.rollback()
        return jsonify({"message": "Error creating report"}), 500

@app.route('/api/comparison', methods=['POST'])
def comparison():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        cur.execute("INSERT INTO supplier_comparisons (user_id, comparison_data) VALUES (%s, %s)",
                    (data['user_id'], data['comparison_data']))
        conn.commit()
        logging.info('Comparison created successfully')
        return jsonify({"message": "Comparison created successfully"}), 201
    except Exception as e:
        logging.error(str(e))
        conn.rollback()
        return jsonify({"message": "Error creating comparison"}), 500





logging.basicConfig(filename='app_logger.log', level=logging.INFO)

@app.route('/startTransaction', methods=['POST'])
def start_transaction():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("INSERT INTO purchase_orders (user_id, supplier_id, product_id, order_status, order_date) VALUES (%s, %s, %s, %s, %s)", (data['user_id'], data['supplier_id'], data['product_id'], 'Pending', data['order_date']))
        conn.commit()
        logging.info('Transaction started')
        return jsonify({'message': 'Transaction started'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'Error starting transaction'}), 500

@app.route('/endTransaction', methods=['POST'])
def end_transaction():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("UPDATE purchase_orders SET order_status = %s WHERE id = %s", ('Completed', data['order_id']))
        conn.commit()
        logging.info('Transaction ended')
        return jsonify({'message': 'Transaction ended'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'Error ending transaction'}), 500

@app.route('/refundTransaction', methods=['POST'])
def refund_transaction():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("UPDATE purchase_orders SET order_status = %s WHERE id = %s", ('Refunded', data['order_id']))
        conn.commit()
        logging.info('Transaction refunded')
        return jsonify({'message': 'Transaction refunded'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'Error refunding transaction'}), 500

@app.route('/reportIssue', methods=['POST'])
def report_issue():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("INSERT INTO bugs (description, status) VALUES (%s, %s)", (data['description'], 'Open'))
        conn.commit()
        logging.info('Issue reported')
        return jsonify({'message': 'Issue reported'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'Error reporting issue'}), 500





logging.basicConfig(filename='app_logger.log', level=logging.INFO)

@app.route('/login', methods=['POST'])
def login():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    username = data['username']
    password = data['password']
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cur.fetchone()
    if user:
        logging.info(f"User {username} logged in at {datetime.now()}")
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/order', methods=['POST'])
def generate_order():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    user_id = data['user_id']
    supplier_id = data['supplier_id']
    product_id = data['product_id']
    order_status = data['order_status']
    order_date = data['order_date']
    delivery_date = data['delivery_date']
    cur.execute("INSERT INTO purchase_orders (user_id, supplier_id, product_id, order_status, order_date, delivery_date, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (user_id, supplier_id, product_id, order_status, order_date, delivery_date, datetime.now(), datetime.now()))
    conn.commit()
    logging.info(f"Order generated by user {user_id} at {datetime.now()}")
    return jsonify({"message": "Order generated successfully"}), 201

@app.route('/order/<int:order_id>', methods=['GET'])
def track_order(order_id):
    conn.rollback()
    cur = conn.cursor()

    cur.execute("SELECT * FROM purchase_orders WHERE id = %s", (order_id,))
    order = cur.fetchone()
    if order:
        logging.info(f"Order {order_id} tracked at {datetime.now()}")
        return jsonify({"order": order}), 200
    else:
        return jsonify({"message": "Order not found"}), 404





logging.basicConfig(filename='app_logger.log', level=logging.INFO)

@app.route('/compare', methods=['POST'])
def compare():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        query = "SELECT * FROM suppliers WHERE id IN %s"
        cur.execute(query, (data['supplier_ids'],))
        results = cur.fetchall()
        logging.info('Comparison executed successfully')
        return jsonify(results), 200
    except Exception as e:
        conn.rollback()
        logging.error('Error executing comparison: {}'.format(str(e)))
        return jsonify({'error': 'Error executing comparison'}), 500
    finally:
        cur.close()





logging.basicConfig(filename='app_logger.log', level=logging.INFO)

@app.route('/addSupplier', methods=['POST'])
@app.route('/addProduct', methods=['POST'])
def add_product():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("INSERT INTO products (supplier_id, name, description, price, inventory_level, alert_level) VALUES (%s, %s, %s, %s, %s, %s)",
                    (data['supplier_id'], data['name'], data['description'], data['price'], data['inventory_level'], data['alert_level']))
        conn.commit()
        logging.info('Product added successfully')
        return jsonify({'message': 'Product added successfully'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'An error occurred'}), 500

@app.route('/updateProduct', methods=['PUT'])
def update_product():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("UPDATE products SET name = %s, description = %s, price = %s, inventory_level = %s, alert_level = %s WHERE id = %s",
                    (data['name'], data['description'], data['price'], data['inventory_level'], data['alert_level'], data['id']))
        conn.commit()
        logging.info('Product updated successfully')
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'An error occurred'}), 500





logging.basicConfig(filename='app_logger.log', level=logging.INFO)

@app.route('/supplier', methods=['POST'])
def add_supplier():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("INSERT INTO suppliers (name, address, contact, email, credit_terms, performance_history, breach_history) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (data['name'], data['address'], data['contact'], data['email'], data['credit_terms'], data['performance_history'], data['breach_history']))
        conn.commit()
        logging.info('Supplier added successfully')
        return jsonify({'message': 'Supplier added successfully'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'Error while adding supplier'}), 500

@app.route('/inventory', methods=['POST'])
def add_inventory():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("INSERT INTO products (supplier_id, name, description, price, inventory_level, alert_level) VALUES (%s, %s, %s, %s, %s, %s)",
                    (data['supplier_id'], data['name'], data['description'], data['price'], data['inventory_level'], data['alert_level']))
        conn.commit()
        logging.info('Inventory added successfully')
        return jsonify({'message': 'Inventory added successfully'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'Error while adding inventory'}), 500

@app.route('/alert', methods=['POST'])
def add_alert():
    conn.rollback()
    cur = conn.cursor()

    data = request.get_json()
    try:
        conn.rollback()
        cur.execute("INSERT INTO alerts (user_id, product_id, alert_type, alert_details, alert_status) VALUES (%s, %s, %s, %s, %s)",
                    (data['user_id'], data['product_id'], data['alert_type'], data['alert_details'], data['alert_status']))
        conn.commit()
        logging.info('Alert added successfully')
        return jsonify({'message': 'Alert added successfully'}), 200
    except Exception as e:
        logging.error(str(e))
        return jsonify({'message': 'Error while adding alert'}), 500



@app.route('/import-schema', methods=['POST'])
def import_schema_endpoint():
    conn = psycopg2.connect(os.environ.get("db_url"))
    cursor = conn.cursor()
    with open('database/db_script.sql', 'r') as file:
        schema_sql = file.read()
    cursor.execute(schema_sql)
    conn.commit()
    return 'Schema imported successfully.'

if __name__ == "__main__":
    app.run(host='0.0.0.0')