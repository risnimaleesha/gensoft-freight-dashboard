Gensoft Freight Forwarding Business Dashboard

A comprehensive business intelligence dashboard for freight forwarding operations, built with Python Flask backend and modern responsive frontend.


🎯 Project Overview

This dashboard provides real-time analytics and insights for freight forwarding business operations, including:

- Financial Performance : Revenue tracking, profit margins, outstanding invoices, currency exposure
- Operational Excellence : Booking pipeline, route analysis, service distribution, container volumes
- Customer Intelligence : Client rankings, segmentation, lifetime value, activity trends
- Activity Analytics : User activity monitoring, system usage patterns, audit trails

🛠️ Technology Stack

Backend:
- Python 3.10+
- Flask (REST API)
- MySQL Database
- Flask-CORS (Cross-origin support)

Frontend:
- HTML5, CSS3, JavaScript (ES6+)
- Chart.js (Data visualization)
- Tailwind CSS (Styling)
- Responsive design

Database:
- MySQL 8.0+
- 3 main tables (47,000+ activity records)
- 15+ optimized views
- Normalized schema

📊 Features

Dashboard Views

1. Financial Dashboard
   - YTD revenue tracking
   - Outstanding invoice aging analysis
   - Profit margin by service type
   - Multi-currency exposure tracking

2. Operational Dashboard
   - Real-time booking pipeline status
   - Top 10 routes by volume and value
   - Service type distribution
   - Average booking value trends

3. Customer Dashboard
   - Top 10 client rankings with LTV
   - Customer segmentation (VIP, Premium, Standard, New)
   - New vs repeat customer analysis
   - Activity trend tracking

4. Activity Analytics** (Backend ready)
   - User productivity metrics
   - System usage patterns
   - Module-wise analytics
   - Peak hours analysis

API Endpoints

Financial:
- `GET /api/financial/summary`
- `GET /api/financial/revenue-by-month?year=2024`
- `GET /api/financial/outstanding-invoices`
- `GET /api/financial/profit-by-service`
- `GET /api/financial/currency-exposure`

Operational:
- `GET /api/operational/summary`
- `GET /api/operational/booking-pipeline`
- `GET /api/operational/top-routes?limit=10`
- `GET /api/operational/service-distribution`

Customer:
- `GET /api/customers/summary`
- `GET /api/customers/top-clients?limit=10`
- `GET /api/customers/segmentation`
- `GET /api/customers/activity-trend`

Activity:
- `GET /api/activity/summary`
- `GET /api/activity/daily-trend`
- `GET /api/activity/module-usage`

Full API documentation: [API_DOCS.md](API_DOCS.md)

🚀 Installation & Setup

Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/gensoft-freight-dashboard.git
cd gensoft-freight-dashboard
```

Step 2: Setup Database
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE FreightDashboard;"

# Import schema
mysql -u root -p FreightDashboard < database/schema.sql

# Import sample data
mysql -u root -p FreightDashboard < database/sample_data.sql

# Create views
mysql -u root -p FreightDashboard < database/views.sql
```

Step 3: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

Step 4: Configure Database Connection

Edit `backend/app.py` and update database credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'FreightDashboard',
    'port': 3306
}
```

Step 5: Run Backend Server
```bash
cd backend
python app.py
```

Server starts at: `http://localhost:5000`

Test: `http://localhost:5000/api/health`

Step 6: Open Frontend

Simply open `frontend/index.html` in your web browser.

Or use a simple HTTP server:
```bash
cd frontend
python -m http.server 8000
```

Then visit: `http://localhost:8000`

📸 Screenshots

Financial Dashboard
![Financial Dashboard](screenshots/dashboard-financial.png)

Operational Dashboard
![Operational Dashboard](screenshots/dashboard-operational.png)

Customer Intelligence
![Customer Dashboard](screenshots/dashboard-customer.png)

API Response
![API Response](screenshots/api-response.png)

🗄️ Database Schema

Tables

tbl_invoice (Invoice transactions)
- Primary Key: `inv_id`
- ~500+ records
- Tracks: Revenue, clients, dates, currencies

Cago_B (Booking records)
- Primary Key: `b_id`
- ~200+ records
- Tracks: Shipments, routes, containers, charges

Alog (Activity log)
- Primary Key: `activity_id`
- 47,000+ records
- Tracks: User activities, system actions, audit trail

Views

15+ optimized database views for:
- Financial analytics
- Operational metrics
- Customer insights
- Activity monitoring

See: [database/views.sql](database/views.sql)

🎨 Design Decisions

1. **RESTful API Architecture**: Clean separation between frontend and backend
2. **Database Views**: Pre-aggregated data for faster queries
3. **Responsive Design**: Works on desktop, tablet, and mobile
4. **Modern UI**: Gradient cards, smooth transitions, interactive charts
5. **CORS Enabled**: Frontend can run separately from backend
6. **Error Handling**: Comprehensive error messages and logging
7. **Modular Code**: Easy to extend and maintain

🔧 API Testing

Using curl:
```bash
# Health check
curl http://localhost:5000/api/health

# Financial summary
curl http://localhost:5000/api/financial/summary

# Top clients
curl http://localhost:5000/api/customers/top-clients?limit=5
```

Using Postman:
1. Import collection (coming soon)
2. Test all endpoints
3. View responses

📈 Performance

- Average API response time: < 200ms
- Database query optimization with indexes
- Views cached for repeated queries
- Efficient data aggregation
- Minimal frontend bundle size (no npm dependencies)

🔐 Security Considerations

- Input validation on all API endpoints
- SQL injection prevention (parameterized queries)
- CORS configuration for production
- Environment variables for sensitive data (recommended)
- Activity logging for audit trail

🚧 Future Enhancements

- [ ] User authentication & authorization
- [ ] Real-time data updates with WebSockets
- [ ] PDF/Excel export functionality
- [ ] Advanced filtering and date range selection
- [ ] Email notifications for key metrics
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] Activity Analytics UI (backend ready)

📝 Project Structure
