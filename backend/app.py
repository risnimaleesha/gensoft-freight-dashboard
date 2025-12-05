from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Riz@db1234',
    'database': 'FreightDashboard'
}

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(query, params=None):
    """Execute a query and return results as list of dictionaries"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        
        # Convert datetime objects to strings and Decimal to float
        for row in results:
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, pd.Timestamp):
                    row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif hasattr(value, '__float__'):  # Handle Decimal types
                    row[key] = float(value)
        
        return results
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ============================================
# FINANCIAL ENDPOINTS
# ============================================

@app.route('/api/financial/revenue-by-month', methods=['GET'])
def get_revenue_by_month():
    """Get revenue by month - ALL DATA"""
    print("→ API called: /api/financial/revenue-by-month")
    
    query = """
        SELECT 
            DATE_FORMAT(inv_date, '%%Y-%%m') as month_year,
            DATE_FORMAT(inv_date, '%%b %%Y') as month_name,
            COUNT(DISTINCT inv_id) as invoice_count,
            SUM(inv_tot) as total_revenue,
            SUM(inv_tot) * 0.25 as estimated_profit,
            inv_def_currency as currency
        FROM tbl_invoice
        WHERE inv_cancelled_status = 0
          AND inv_date IS NOT NULL
        GROUP BY DATE_FORMAT(inv_date, '%%Y-%%m'), inv_def_currency
        ORDER BY inv_date DESC
        LIMIT 12
    """
    results = execute_query(query)
    
    if results:
        results.reverse()  # Oldest first
        print(f"✓ Found {len(results)} months of data")
    
    return jsonify(results or [])

@app.route('/api/financial/outstanding-invoices', methods=['GET'])
def get_outstanding_invoices():
    """Get outstanding invoices with aging"""
    query = """
        SELECT 
            aging_category,
            COUNT(*) as count,
            CAST(SUM(amount) AS DECIMAL(15,2)) as total_amount,
            currency
        FROM vw_outstanding_invoices
        GROUP BY aging_category, currency
        ORDER BY 
            CASE aging_category
                WHEN '0-30 days' THEN 1
                WHEN '31-60 days' THEN 2
                WHEN '61-90 days' THEN 3
                WHEN '90+ days' THEN 4
            END
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/financial/profit-by-service', methods=['GET'])
def get_profit_by_service():
    """Get profit margin by service type"""
    query = """
        SELECT 
            service_type,
            invoice_count,
            CAST(total_revenue AS DECIMAL(15,2)) as total_revenue,
            CAST(estimated_profit AS DECIMAL(15,2)) as estimated_profit,
            CAST(profit_margin AS DECIMAL(5,2)) as profit_margin
        FROM vw_profit_by_service 
        ORDER BY total_revenue DESC
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/financial/currency-exposure', methods=['GET'])
def get_currency_exposure():
    """Get currency exposure distribution"""
    query = """
        SELECT 
            currency,
            transaction_count,
            CAST(total_amount AS DECIMAL(15,2)) as total_amount,
            CAST(percentage AS DECIMAL(5,2)) as percentage
        FROM vw_currency_exposure 
        ORDER BY total_amount DESC
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/financial/summary', methods=['GET'])
def get_financial_summary():
    """Get financial summary statistics"""
    query = """
        SELECT 
            CAST(SUM(inv_tot) AS DECIMAL(15,2)) as total_revenue,
            COUNT(DISTINCT inv_id) as total_invoices,
            CAST(AVG(inv_tot) AS DECIMAL(15,2)) as avg_invoice_value,
            CAST((SELECT SUM(inv_tot) FROM tbl_invoice WHERE inv_cancelled_status = 0 AND acc_post = 0) AS DECIMAL(15,2)) as outstanding_total,
            (SELECT COUNT(*) FROM tbl_invoice WHERE inv_cancelled_status = 0 AND acc_post = 0) as outstanding_count,
            CAST((SELECT AVG(DATEDIFF(inv_edate, inv_date)) FROM tbl_invoice WHERE inv_cancelled_status = 0 AND inv_date IS NOT NULL) AS DECIMAL(10,2)) as avg_collection_days
        FROM tbl_invoice
        WHERE inv_cancelled_status = 0
          AND YEAR(inv_date) = YEAR(CURDATE())
    """
    results = execute_query(query)
    return jsonify(results[0] if results else {})

# ============================================
# OPERATIONAL ENDPOINTS
# ============================================

@app.route('/api/operational/booking-pipeline', methods=['GET'])
def get_booking_pipeline():
    """Get booking pipeline by status"""
    query = """
        SELECT 
            status,
            booking_count,
            CAST(total_value AS DECIMAL(15,2)) as total_value,
            CAST(avg_value AS DECIMAL(15,2)) as avg_value
        FROM vw_booking_pipeline 
        ORDER BY status
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/operational/top-routes', methods=['GET'])
def get_top_routes():
    """Get top routes by volume"""
    limit = request.args.get('limit', 10)
    query = f"""
        SELECT 
            route,
            shipment_count,
            total_containers,
            CAST(total_value AS DECIMAL(15,2)) as total_value,
            CAST(avg_value AS DECIMAL(15,2)) as avg_value
        FROM vw_top_routes 
        LIMIT {limit}
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/operational/service-distribution', methods=['GET'])
def get_service_distribution():
    """Get service type distribution"""
    query = """
        SELECT 
            service_type,
            booking_count,
            total_containers,
            CAST(total_revenue AS DECIMAL(15,2)) as total_revenue,
            CAST(percentage AS DECIMAL(5,2)) as percentage
        FROM vw_service_distribution 
        ORDER BY booking_count DESC
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/operational/booking-value-trend', methods=['GET'])
def get_booking_value_trend():
    """Get average booking value trend"""
    query = """
        SELECT 
            quarter,
            booking_count,
            CAST(avg_booking_value AS DECIMAL(15,2)) as avg_booking_value,
            CAST(total_value AS DECIMAL(15,2)) as total_value
        FROM vw_booking_value_trend 
        ORDER BY quarter
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/operational/summary', methods=['GET'])
def get_operational_summary():
    """Get operational summary statistics"""
    query = """
        SELECT 
            COUNT(CASE WHEN b_status IN (0, 1) THEN 1 END) as active_bookings,
            CAST(AVG(bk_chgs_tot_selling) AS DECIMAL(15,2)) as avg_booking_value,
            SUM(b_n_cntr_fcl) as total_containers,
            CAST(SUM(bk_chgs_tot_selling) AS DECIMAL(15,2)) as pipeline_value,
            COUNT(b_id) as total_bookings
        FROM Cago_B
        WHERE inv_cancelled_status = 0
    """
    results = execute_query(query)
    return jsonify(results[0] if results else {})

# ============================================
# CUSTOMER ENDPOINTS
# ============================================

@app.route('/api/customers/top-clients', methods=['GET'])
def get_top_clients():
    """Get top clients ranking"""
    limit = request.args.get('limit', 10)
    query = f"""
        SELECT 
            client_id,
            client_name,
            total_bookings,
            CAST(total_revenue AS DECIMAL(15,2)) as total_revenue,
            CAST(estimated_ltv AS DECIMAL(15,2)) as estimated_ltv,
            CAST(avg_invoice_value AS DECIMAL(15,2)) as avg_invoice_value,
            first_transaction,
            last_transaction,
            customer_age_days
        FROM vw_top_clients 
        LIMIT {limit}
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/customers/segmentation', methods=['GET'])
def get_customer_segmentation():
    """Get customer segmentation"""
    query = """
        SELECT 
            segment,
            customer_count,
            CAST(segment_revenue AS DECIMAL(15,2)) as segment_revenue,
            CAST(avg_customer_value AS DECIMAL(15,2)) as avg_customer_value
        FROM vw_customer_segmentation 
        ORDER BY 
            CASE segment
                WHEN 'VIP (>1M)' THEN 1
                WHEN 'Premium (500K-1M)' THEN 2
                WHEN 'Standard (100K-500K)' THEN 3
                WHEN 'New (<100K)' THEN 4
            END
    """
    results = execute_query(query)
    return jsonify(results or [])

@app.route('/api/customers/activity-trend', methods=['GET'])
def get_customer_activity():
    """Get customer activity trend - SIMPLIFIED"""
    print("→ API called: /api/customers/activity-trend")
    
    query = """
        SELECT 
            DATE_FORMAT(inv_date, '%%Y-%%m') as month,
            DATE_FORMAT(inv_date, '%%b %%Y') as month_name,
            DATE_FORMAT(inv_date, '%%b') as month_short,
            COUNT(DISTINCT client_id) as total_customers
        FROM tbl_invoice
        WHERE inv_cancelled_status = 0
          AND client_id > 0
          AND inv_date IS NOT NULL
        GROUP BY DATE_FORMAT(inv_date, '%%Y-%%m')
        ORDER BY inv_date DESC
        LIMIT 12
    """
    results = execute_query(query)
    
    if results:
        results.reverse()  # Oldest first
        # Add new vs repeat (approximation for display)
        for row in results:
            total = row['total_customers']
            row['new_customers'] = max(1, int(total * 0.3))
            row['repeat_customers'] = total - row['new_customers']
        print(f"✓ Found {len(results)} months of customer data")
    
    return jsonify(results or [])

@app.route('/api/customers/summary', methods=['GET'])
def get_customer_summary():
    """Get customer summary statistics"""
    query = """
        SELECT 
            COUNT(DISTINCT client_id) as total_customers,
            CAST(AVG(customer_revenue) AS DECIMAL(15,2)) as avg_customer_value,
            (SELECT COUNT(DISTINCT client_id) 
             FROM tbl_invoice 
             WHERE inv_cancelled_status = 0 
               AND YEAR(inv_date) = YEAR(CURDATE())) as ytd_active_customers,
            (SELECT COUNT(DISTINCT client_id) 
             FROM tbl_invoice 
             WHERE inv_cancelled_status = 0 
               AND inv_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)) as new_customers_3m
        FROM (
            SELECT client_id, SUM(inv_tot) as customer_revenue
            FROM tbl_invoice
            WHERE inv_cancelled_status = 0 AND client_id > 0
            GROUP BY client_id
        ) as customer_data
    """
    results = execute_query(query)
    return jsonify(results[0] if results else {})

# ============================================
# GENERAL ENDPOINTS
# ============================================

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get overall dashboard summary"""
    query = "SELECT * FROM vw_dashboard_summary"
    results = execute_query(query)
    return jsonify(results[0] if results else {})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    connection = get_db_connection()
    if connection:
        connection.close()
        return jsonify({"status": "healthy", "database": "connected"})
    return jsonify({"status": "unhealthy", "database": "disconnected"}), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "message": "Gensoft Business Dashboard API",
        "version": "1.0",
        "endpoints": {
            "financial": [
                "/api/financial/revenue-by-month",
                "/api/financial/outstanding-invoices",
                "/api/financial/profit-by-service",
                "/api/financial/currency-exposure",
                "/api/financial/summary"
            ],
            "operational": [
                "/api/operational/booking-pipeline",
                "/api/operational/top-routes",
                "/api/operational/service-distribution",
                "/api/operational/booking-value-trend",
                "/api/operational/summary"
            ],
            "customers": [
                "/api/customers/top-clients",
                "/api/customers/segmentation",
                "/api/customers/activity-trend",
                "/api/customers/summary"
            ],
            "general": [
                "/api/dashboard/summary",
                "/api/health"
            ]
        }
    })

if __name__ == '__main__':
    print("Starting Gensoft Dashboard API Server...")
    print("Server running on http://localhost:5000")
    print("\nTest the API:")
    print("  - Health Check: http://localhost:5000/api/health")
    print("  - API Docs: http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)
