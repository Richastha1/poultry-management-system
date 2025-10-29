from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# ✅ MySQL Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="poultry_management"
    )

@app.route('/')
def index():
    return render_template('index.html')

# ➕ Add Record
@app.route('/add_record', methods=['POST'])
def add_record():
    conn = get_connection()
    cursor = conn.cursor()

    flock_id = request.form.get('flock_id')
    lot_no = request.form.get('lot_no')
    record_date = request.form.get('record_date')
    stack_male = request.form.get('stack_male', 0)
    stack_female = request.form.get('stack_female', 0)
    feed_male = request.form.get('Feed_male', 0)
    feed_female = request.form.get('Feed_female', 0)
    mortality_male = request.form.get('mortality_male', 0)
    mortality_female = request.form.get('mortality_female', 0)
    cull_male = request.form.get('cull_male', 0)
    cull_female = request.form.get('cull_female', 0)
    hatchable = request.form.get('Hetchable', 0)
    cr = request.form.get('CR', 0)
    rj = request.form.get('RJ', 0)
    db_egg = request.form.get('DB', 0)
    total_eggs = request.form.get('total_eggs', 0)
    medicine = request.form.get('medicine', '')
    vaccine = request.form.get('vaccine', '')
    remarks = request.form.get('Remarks', '')

    query = """
        INSERT INTO daily_records (
            flock_id, lot_no, record_date, stack_male, stack_female,
            feed_male, feed_female, mortality_male, mortality_female,
            cull_male, cull_female, hatchable, cr, rj, db_egg, total_eggs,
            medicine, vaccine, remarks
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    values = (
        flock_id, lot_no, record_date, stack_male, stack_female,
        feed_male, feed_female, mortality_male, mortality_female,
        cull_male, cull_female, hatchable, cr, rj, db_egg, total_eggs,
        medicine, vaccine, remarks
    )

    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

    return "<h3>✅ Record added successfully!</h3><a href='/'>Add New</a> | <a href='/daily_report'>View Daily Report</a>"

# 📅 Daily Report (Lot No + Date Range Filter)
@app.route('/daily_report', methods=['GET', 'POST'])
def daily_report():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    data = []
    selected_lot = None
    from_date = None
    to_date = None

    cursor.execute("SELECT DISTINCT lot_no FROM daily_records ORDER BY lot_no")
    lots = [row['lot_no'] for row in cursor.fetchall()]

    if request.method == 'POST':
        selected_lot = request.form.get('lot_no')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')

        query = "SELECT * FROM daily_records WHERE 1=1"
        params = []

        if selected_lot:
            query += " AND lot_no = %s"
            params.append(selected_lot)
        if from_date:
            query += " AND record_date >= %s"
            params.append(from_date)
        if to_date:
            query += " AND record_date <= %s"
            params.append(to_date)

        query += " ORDER BY record_date DESC"
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('daily_report.html', records=data, lots=lots,
                           selected_lot=selected_lot, from_date=from_date, to_date=to_date)

# 📊 Monthly Report (Lot No + Date Range Filter)
@app.route('/report', methods=['GET', 'POST'])
def report():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    monthly_data = []
    selected_lot = None
    from_date = None
    to_date = None

    cursor.execute("SELECT DISTINCT lot_no FROM daily_records ORDER BY lot_no")
    lots = [row['lot_no'] for row in cursor.fetchall()]

    if request.method == 'POST':
        selected_lot = request.form.get('lot_no')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')

        query = """
            SELECT 
                lot_no,
                DATE_FORMAT(record_date, '%M %Y') AS month,
                SUM(stack_male) AS total_stack_male,
                SUM(stack_female) AS total_stack_female,
                SUM(feed_male) AS total_feed_male,
                SUM(feed_female) AS total_feed_female,
                SUM(mortality_male) AS total_mortality_male,
                SUM(mortality_female) AS total_mortality_female,
                SUM(cull_male) AS total_cull_male,
                SUM(cull_female) AS total_cull_female,
                SUM(hatchable) AS total_hatchable,
                SUM(cr) AS total_cr,
                SUM(rj) AS total_rj,
                SUM(db_egg) AS total_db_egg,
                SUM(total_eggs) AS total_eggs
            FROM daily_records
            WHERE 1=1
        """
        params = []

        if selected_lot:
            query += " AND lot_no = %s"
            params.append(selected_lot)
        if from_date:
            query += " AND record_date >= %s"
            params.append(from_date)
        if to_date:
            query += " AND record_date <= %s"
            params.append(to_date)

        query += " GROUP BY lot_no, DATE_FORMAT(record_date, '%M %Y') ORDER BY month DESC"

        cursor.execute(query, tuple(params))
        monthly_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('monthly_report.html', reports=monthly_data, lots=lots,
                           selected_lot=selected_lot, from_date=from_date, to_date=to_date)

if __name__ == '__main__':
    app.run(debug=True)
