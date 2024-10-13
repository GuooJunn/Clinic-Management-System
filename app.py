from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'anything'

# Set up MongoDB client
client = MongoClient('mongodb://34.196.179.164:27017')
db = client['Clinic_Cloud_DB']
billing_record = db['billing_record']
appointment_record = db['appointment_record']
appointment_history_record = db['appointment_history_record']
medicine_purchase_record = db['medicine_purchase_record']

# Set up RDS
app.config['MYSQL_HOST'] = "clouddb-app.crjeb832w24x.us-east-1.rds.amazonaws.com"
app.config['MYSQL_USER'] = "admin"
app.config['MYSQL_PASSWORD'] = "testtest"
app.config['MYSQL_DB'] = "Clinic_Cloud_DB"
#app.config['MYSQL_PORT'] = 3306  # MySQL default port

mysql = MySQL(app)

# ================================================================
#                           Login
# ================================================================

@app.route('/')
def home():
    # Clear session data when accessing the home page
    session.clear()
    # Render template for login page
    return render_template('login.html')

@app.route('/auth-login', methods=['POST'])
def auth_login():
    if request.method == 'POST':
        # Get email and password from the form
        email_input = request.form['email']
        password_input = request.form['password']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()

        # Execute SQL query to select user based on email and password
        result = cur.execute("SELECT * FROM users WHERE user_email=%s AND user_password=%s", (email_input,password_input,))
        auth_data = cur.fetchall()

        # Close the cursor
        cur.close()

        # If one user is found with the provided credentials
        if result == 1:
            for user in auth_data:
                # Redirect users to different dashboards based on their roles
                if user[5] == 'staff':
                    session['user_detail'] = user
                    session['role'] = user[5]
                    return redirect(url_for('dashboard_staff'))
                elif user[5] == 'doctor':
                    session['user_detail'] = user
                    session['role'] = user[5]
                    return redirect(url_for('dashboard_doctor'))
                elif user[5] == 'admin':
                    session['user_detail'] = user
                    session['role'] = user[5]
                    return redirect(url_for('dashboard_admin'))
                elif user[5] == 'patient':
                    session['user_detail'] = user
                    session['role'] = user[5]
                    session['patientId'] = user[6]
                    return redirect(url_for('dashboard_patient'))
                else:
                    session['error_message'] = 'Login Failed: Your user ID or password is incorrect'
                    return render_template('login.html')
         # If it is not recognized, set an error message and render the login page
        else:
            session['error_message'] = 'Login Failed: Your user ID or password is incorrect'
            return render_template('login.html')
        
@app.route('/register')
def register():
    # Render template for login page
    return render_template('register.html')

@app.route('/auth-register', methods=['POST'])
def auth_register():
    if request.method == 'POST':
        # Get email and password from the form
        nric_input = request.form['nric'] 
        email_input = request.form['email']
        password_input = request.form['password']
        contact_number_input = request.form['contact_number']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()

        # Execute SQL query to select user based on email and password
        result = cur.execute("SELECT patient_id, patient_name FROM patient_record WHERE patient_nric=%s", (nric_input,))
        record = cur.fetchone()
        print(result)

        # If one user is found with the provided credentials
        if result == 1:
            # Create a cursor to execute SQL queries
            cur = mysql.connection.cursor()
            # Execute INSERT statement to add user data
            cur.execute("INSERT INTO users(user_name, user_email, user_password, user_contact_number, user_role, patient_id) VALUE (%s, %s, %s, %s, %s, %s)", 
                        (record[1], email_input, password_input, contact_number_input, "patient", record[0],))
            # Commit the transaction
            mysql.connection.commit()
            # Close the cursor
            cur.close()
            
            return render_template('login.html')
         # If it is not recognized, set an error message and render the login page
        else:
            session['error_message'] = 'Register Failed: Please contact the staff to create a account'
            return render_template('register.html')

# ================================================================
#                           STAFF
# ================================================================
@app.route('/dashboard-staff')
def dashboard_staff():
    if session['role'] == 'staff':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated schedule data
        cur.execute("SELECT count(schedule_id) FROM schedule")
        # Fetch the updated data
        schedule_data = cur.fetchall()
        # Execute SELECT statement to fetch patient blood type data
        cur.execute("SELECT count(patient_id) FROM patient_record WHERE patient_blood_type='A+'")
        # Fetch the updated data
        bloodAplus_data = cur.fetchall()
        # Execute SELECT statement to fetch patient blood type data
        cur.execute("SELECT count(patient_id) FROM patient_record WHERE patient_blood_type='A-'")
        # Fetch the updated data
        bloodAminus_data = cur.fetchall()
        # Execute SELECT statement to fetch patient blood type data
        cur.execute("SELECT count(patient_id) FROM patient_record WHERE patient_blood_type='B+'")
        # Fetch the updated data
        bloodBplus_data = cur.fetchall()
        # Execute SELECT statement to fetch patient blood type data
        cur.execute("SELECT count(patient_id) FROM patient_record WHERE patient_blood_type='B-'")
        # Fetch the updated data
        bloodBminus_data = cur.fetchall()
        # Execute SELECT statement to fetch patient blood type data
        cur.execute("SELECT count(patient_id) FROM patient_record WHERE patient_blood_type='AB+'")
        # Fetch the updated data
        bloodABplus_data = cur.fetchall()
        # Execute SELECT statement to fetch patient blood type data
        cur.execute("SELECT count(patient_id) FROM patient_record WHERE patient_blood_type='AB-'")
        # Fetch the updated data
        bloodABminus_data = cur.fetchall()
        # Execute SELECT statement to fetch patient blood type data
        cur.execute("SELECT count(patient_id) FROM patient_record WHERE patient_blood_type='O+'")
        # Fetch the updated data
        bloodOplus_data = cur.fetchall()
        # Execute SELECT statement to fetch patient blood type data
        cur.execute("SELECT count(patient_id) FROM patient_record WHERE patient_blood_type='O-'")
        # Fetch the updated data
        bloodOminus_data = cur.fetchall()
        # Close the cursor
        cur.close()

        # MongoDB aggregation pipeline
        pipeline = [
            { '$group': {
                '_id': { 'year': { '$year': { '$dateFromString': { 'dateString': "$request_date" } } }, 
                         'month': { '$month': { '$dateFromString': { 'dateString': "$request_date" } } }
                         },
                'count': { '$sum': 1 }
            }},
            {
                '$addFields': {
                "monthName": {
                    '$switch': {
                    'branches': [
                        { 'case': { '$eq': ["$_id.month", 1] }, 'then': "January" },
                        { 'case': { '$eq': ["$_id.month", 2] }, 'then': "February" },
                        { 'case': { '$eq': ["$_id.month", 3] }, 'then': "March" },
                        { 'case': { '$eq': ["$_id.month", 4] }, 'then': "April" },
                        { 'case': { '$eq': ["$_id.month", 5] }, 'then': "May" },
                        { 'case': { '$eq': ["$_id.month", 6] }, 'then': "June" },
                        { 'case': { '$eq': ["$_id.month", 7] }, 'then': "July" },
                        { 'case': { '$eq': ["$_id.month", 8] }, 'then': "August" },
                        { 'case': { '$eq': ["$_id.month", 9] }, 'then': "September" },
                        { 'case': { '$eq': ["$_id.month", 10] }, 'then': "October" },
                        { 'case': { '$eq': ["$_id.month", 11] }, 'then': "November" },
                        { 'case': { '$eq': ["$_id.month", 12] }, 'then': "December" }
                    ],
                    'default': "Unknown"
                    }
                }
                }
            },
            {
                '$sort': { "_id.year": 1, "_id.month": 1 }
            }
        ]
        # Execute aggregation pipeline
        result = list(appointment_history_record.aggregate(pipeline))
        print(result)

        return render_template('dashboard-staff.html', schedule_data=schedule_data, bloodAplus_data=bloodAplus_data, bloodAminus_data=bloodAminus_data, bloodBplus_data=bloodBplus_data, bloodBminus_data=bloodBminus_data, bloodABplus_data=bloodABplus_data, bloodABminus_data=bloodABminus_data, bloodOplus_data=bloodOplus_data, bloodOminus_data=bloodOminus_data, visits_data=result)
    else:
        return render_template('error403.html')

@app.route('/patient-records-staff')
def patient_records_staff():
    if session['role'] == 'staff':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated patient_record data
        cur.execute("SELECT * FROM patient_record")
        # Fetch the updated data
        data = cur.fetchall()
        # Close the cursor
        cur.close()

        return render_template('patient-records-staff.html', patient_data=data)
    else:
        return render_template('error403.html')

@app.route('/add-patient-records-staff', methods=['POST'])
def add_patient_records_staff():
    if request.method == 'POST':
        # Get information of new patient from the form
        name_input = request.form['add_name']
        age_input = request.form['add_age']
        nirc_input = request.form['add_nirc']
        gender_input = request.form['add_gender']
        blood_type_input = request.form['add_blood_type']
        medical_condition_input = request.form['add_medical_condition']
        covid_vacc_status_input = request.form['add_covid_vacc_status']
        allergies_input = request.form['add_allergies']
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()

        # Check if the patient_nric already exists
        cur.execute("SELECT * FROM patient_record WHERE patient_nric = %s", (nirc_input,))
        existing_patient = cur.fetchone()

        if existing_patient:
            # If the patient_nric already exists, show error message
            flash('Patient with this NRIC already exists. Please use a different NRIC.', 'danger')
            cur.close()
            return redirect(url_for('patient_records_staff'))

        # Execute INSERT statement to add patient_record data
        cur.execute("INSERT INTO patient_record (patient_name, patient_age, patient_gender, patient_blood_type, patient_medical_condition, patient_date_of_enrollment, patient_date_of_last_update, patient_covid_vacc_status, patient_allergies, patient_nric) VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                    (name_input, age_input, gender_input, blood_type_input, medical_condition_input, today_date, today_date, covid_vacc_status_input, allergies_input, nirc_input))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('patient_records_staff'))

@app.route('/schedule-staff')
def schedule_staff():
    if session['role'] == 'staff':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated schedule data
        cur.execute("SELECT s.schedule_id, s.schedule_request_date, s.schedule_purpose_of_visit, s.schedule_remarks, s.patient_id, s.staff_id,  p.patient_name, u.user_name FROM schedule s, patient_record p, users u WHERE s.patient_id=p.patient_id AND s.staff_id=u.user_id")
        # Fetch the updated data
        manual_schedule_data = cur.fetchall()
        # Execute SELECT statement to fetch updated schedule data
        cur.execute("SELECT s.schedule_id, s.schedule_request_date, s.schedule_purpose_of_visit, s.patient_id, s.staff_id,  p.patient_name FROM schedule s, patient_record p WHERE s.patient_id=p.patient_id AND s.staff_id IS NULL")
        # Fetch the updated data
        appointment_schedule_data = cur.fetchall()
        # Execute SELECT statement to fetch patient name data
        cur.execute("SELECT patient_id, patient_name FROM patient_record")
        # Fetch the updated data
        patient_data = cur.fetchall()
        # Execute SELECT statement to fetch doctor name data
        cur.execute("SELECT user_id, user_name FROM users WHERE user_role='doctor'")
        # Fetch the updated data
        doctor_data = cur.fetchall()
        # Close the cursor
        cur.close()

        return render_template('schedule-staff.html', appointment_data=appointment_schedule_data, schedule_data=manual_schedule_data, patient_list=patient_data, doctor_list=doctor_data)
    else:
        return render_template('error403.html')

@app.route('/add-schedule-staff', methods=['POST'])
def add_schedule_staff():
    if request.method == 'POST':
        # Get information of new schedule from the form
        patient_id_input = request.form['add_patient_name_data_id']
        purpose_input = request.form['add_purpose']
        request_date_input = request.form['add_request_date']
        doctor_id_input = request.form['add_assigned_doctor_data_id']
        remark_input = request.form['add_remark']
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute INSERT statement to add schedule data
        cur.execute("INSERT INTO schedule (schedule_request_date, schedule_purpose_of_visit, schedule_remarks, schedule_creation_date, patient_id, staff_id) VALUE (%s, %s, %s, %s, %s, %s)", 
                    (request_date_input, purpose_input, remark_input, today_date, int(patient_id_input), int(doctor_id_input)))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('schedule_staff'))
    
@app.route('/update-schedule-staff', methods=['POST'])
def update_schedule_staff():
    if request.method == 'POST':
        # Get information of new schedule from the form
        id_input = request.form['edit_id']
        purpose_input = request.form['edit_purpose']
        request_date_input = request.form['edit_request_date']
        doctor_id_input = request.form['edit_assigned_doctor_data_id']
        remark_input = request.form['edit_remark']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute UPDATE statement to update schedule data
        cur.execute("UPDATE schedule SET schedule_purpose_of_visit=%s, schedule_request_date=%s, schedule_remarks=%s, staff_id=%s WHERE schedule_id=%s", 
                    (purpose_input, request_date_input, remark_input, int(doctor_id_input), id_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        # Find schedule id in appointment record
        record = appointment_record.find_one({'schedule_id': id_input})
        # delete appointment record and add to history appointment record
        if record:
            appointment_record.delete_one({'schedule_id': id_input})
            history_data = {"request_date":f"{record['request_date']}", "purpose":f"{record['purpose']}", "patient_id":f"{record['patient_id']}", "schedule_id":f"{record['schedule_id']}"}
            appointment_history_record.insert_one(history_data)

        return redirect(url_for('schedule_staff'))
    
@app.route('/delete-schedule-staff', methods=['POST'])
def delete_schedule_staff():
    if request.method == 'POST':
        # Get information of new schedule from the form
        id_input = request.form['delete_id']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute DELETE statement to delete schedule data
        cur.execute("DELETE FROM schedule WHERE schedule_id=%s", (id_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('schedule_staff'))
    
@app.route('/billing-staff')
def billing_staff():
    if session['role'] == 'staff':
        # Execute billing_record data
        data = list(billing_record.find({}, {'_id': 0}))

        return render_template('billing-staff.html', billing_data=data)
    else:
        return render_template('error403.html')

# ================================================================
#                           Doctor
# ================================================================
@app.route('/dashboard-doctor')
def dashboard_doctor():
    today_date = datetime.today().strftime('%Y-%m-%d')
    if session['role'] == 'doctor':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated schedule data
        cur.execute("SELECT count(schedule_id) FROM schedule WHERE schedule_request_date=%s AND staff_id=%s",(today_date, session['user_detail'][0]))
        # Fetch the updated data
        schedule_data = cur.fetchall()
        # Execute SELECT statement to fetch updated medicine data
        cur.execute("SELECT medicine_name, medicine_manufacturer_name, medicine_quantity FROM medicine_inventory WHERE medicine_quantity<(SELECT AVG(medicine_quantity) FROM medicine_inventory)")
        # Fetch the updated data
        medicine_data = cur.fetchall()
        # Close the cursor
        cur.close()

        return render_template('dashboard-doctor.html', schedule_data=schedule_data, medicine_data=medicine_data)
    else:
        return render_template('error403.html')

@app.route('/schedule-doctor')
def schedule_doctor():
    if session['role'] == 'doctor':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated schedule data
        cur.execute("SELECT s.schedule_id, s.schedule_request_date, s.schedule_purpose_of_visit, s.schedule_remarks, s.patient_id, s.staff_id,  p.patient_name, u.user_name FROM schedule s, patient_record p, users u WHERE s.patient_id=p.patient_id AND s.staff_id=u.user_id")
        # Fetch the updated data
        data = cur.fetchall()
        # Close the cursor
        cur.close()

        return render_template('schedule-doctor.html', schedule_data=data)
    else:
        return render_template('error403.html')
    
@app.route('/consultation-doctor/<int:id>', methods=['GET','POST'])
def consultation_doctor(id):
    if session['role'] == 'doctor':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated schedule data
        cur.execute("SELECT s.schedule_purpose_of_visit, s.schedule_remarks, s.patient_id, s.staff_id,  p.patient_name, u.user_name FROM schedule s, patient_record p, users u WHERE s.patient_id=p.patient_id AND s.staff_id=u.user_id AND s.schedule_id=%s", (id,))
        # Fetch the updated data
        data = cur.fetchall()
        # Execute SELECT statement to fetch updated medicine_inventory data
        cur.execute("SELECT * FROM medicine_inventory")
        # Fetch the updated data
        med_data = cur.fetchall()
        # Close the cursor
        cur.close()

        session['scheduleId'] = id

        return render_template('consultation-doctor.html', schedule_data=data, medicine_data=med_data)
    else:
        return render_template('error403.html')

@app.route('/add-consultation-doctor', methods=['POST'])
def add_consultation_doctor():
    if request.method == 'POST':
        # Get information of new medicine inventory from the form
        today_date = datetime.today().strftime('%Y-%m-%d')
        remark_input = request.form['add_remark']
        diagnosis_input = request.form['add_diagnosis']
        staffId_input = request.form['add_doctor_id']
        patientId_input = request.form['add_patient_id']
        session['patientId'] = patientId_input


        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute INSERT statement to add consultation record data
        cur.execute("INSERT INTO consultation_record (consultation_record_creation_date, consultation_remarks, consultation_diagnosis_remark, staff_id, patient_id) VALUE (%s, %s, %s, %s, %s)", 
                    (today_date, remark_input, diagnosis_input, staffId_input, patientId_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('prescription_doctor'))

@app.route('/prescription-doctor')
def prescription_doctor():
    today_date = datetime.today().strftime('%Y-%m-%d')
    # Create a cursor to execute SQL queries
    cur = mysql.connection.cursor()
    # Execute SELECT statement to fetch updated consultation id data
    cur.execute("SELECT consultation_id FROM consultation_record WHERE consultation_record_creation_date=%s AND staff_id=%s AND patient_id=%s",(today_date, session['user_detail'][0],session['patientId'],))
    # Fetch the updated data
    consultationId_data = cur.fetchall()
    # Execute SELECT statement to fetch updated prescription record data
    cur.execute("SELECT p.prescription_id, m.medicine_name, p.medicine_quantity, p.prescription_price, p.prescription_remark, p.prescription_record_creation_date FROM prescription_record p, medicine_inventory m WHERE p.medicine_id=m.medicine_id AND p.consultation_id=%s", (consultationId_data[0][0],))
    # Fetch the updated data
    prescription_data = cur.fetchall()
    # Execute SELECT statement to fetch updated medicine list data
    cur.execute("SELECT medicine_id, medicine_name, medicine_price FROM medicine_inventory")
    # Fetch the updated data
    medicine_list_data = cur.fetchall()
    # Close the cursor
    cur.close()

    return render_template('prescription-doctor.html', prescription_data=prescription_data, consultationId_data=consultationId_data, medicine_list=medicine_list_data)
    
@app.route('/add-prescription-doctor', methods=['POST'])
def add_prescription_doctor():
    today_date = datetime.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        # Get information of new medicine inventory from the form
        consultationId_input = request.form['add_consultation_id']
        date_input = today_date
        medicineId_input = request.form['add_medicine_name_data_id']
        quantity_input = request.form['add_quantity']
        price_input = request.form['add_price']
        remark_input = request.form['add_remark']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute INSERT statement to add medicine inventory data
        cur.execute("INSERT INTO prescription_record (consultation_id, prescription_record_creation_date, medicine_id, medicine_quantity, prescription_price, prescription_remark) VALUE (%s, %s, %s, %s, %s, %s)", 
                    (consultationId_input, date_input, medicineId_input, quantity_input, price_input, remark_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('prescription_doctor'))

@app.route('/delete-prescription-doctor', methods=['POST'])
def delete_prescription_doctor():
    if request.method == 'POST':
        # Get information of new medicine from the form
        id_input = request.form['delete_id']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute DELETE statement to delete prescription data
        cur.execute("DELETE FROM prescription_record WHERE prescription_id=%s", (id_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('prescription_doctor'))
    
@app.route('/return-schedule-doctor', methods=['POST'])
def return_schedule_doctor():
    if request.method == 'POST':
        # Get information from the form
        consultationId_input = request.form['consultation_id']
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated total billing sum data
        cur.execute("SELECT patient_name FROM patient_record WHERE patient_id=%s",(session['patientId'],))
        # Fetch the updated data
        patient_data = cur.fetchall()
        # Execute SELECT statement to fetch updated total billing sum data
        cur.execute("SELECT sum(prescription_price) FROM prescription_record WHERE consultation_id=%s",(consultationId_input,))
        # Fetch the updated data
        totalSum_data = cur.fetchall()
        for data in totalSum_data:
            if data[0] == None:
                sum = 0
            else:
                sum = round(data[0],2)

        # Execute DELETE statement to delete schedule data
        cur.execute("DELETE FROM schedule WHERE schedule_id=%s", (session['scheduleId'],))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        data = {"consultant_date":f"{today_date}", "billing_total":f"{sum}", "billing_status":"Unpaid", "patient_id":f"{session['patientId']}", "patient_name":f"{patient_data[0][0]}"}
        billing_record.insert_one(data)

        session.pop('patientId')
        session.pop('scheduleId')

        return redirect(url_for('schedule_doctor'))

@app.route('/medicine-inventory-doctor')
def medicine_inventory_doctor():
    if session['role'] == 'doctor':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated medicine inventory data
        cur.execute("SELECT * FROM medicine_inventory")
        # Fetch the updated data
        data = cur.fetchall()
        # Close the cursor
        cur.close()
        return render_template('medicine-inventory-doctor.html', medicine_data=data)
    else:
        return render_template('error403.html')
    
@app.route('/add-medicine-inventory-doctor', methods=['POST'])
def add_medicine_inventory_doctor():
    if request.method == 'POST':
        # Get information of new medicine inventory from the form
        name_input = request.form['add_name']
        price_input = request.form['add_price']
        side_effect_input = request.form['add_side_effect']
        usage_input = request.form['add_usage']
        manufacturer_input = request.form['add_manufacturer']
        pack_size_label_input = request.form['add_pack_size_label']
        composition_1_input = request.form['add_composition_1']
        composition_2_input = request.form['add_composition_2']
        remarks_input = request.form['add_remarks']
        quantity_input = request.form['add_quantity']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute INSERT statement to add medicine inventory data
        cur.execute("INSERT INTO medicine_inventory (medicine_name, medicine_price, medicine_side_effect, medicine_usage, medicine_manufacturer_name, medicine_pack_size_label, medicine_composition_1, medicine_composition_2, medicine_remarks, medicine_quantity) VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                    (name_input, price_input, side_effect_input, usage_input, manufacturer_input, pack_size_label_input, composition_1_input, composition_2_input, remarks_input, quantity_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('medicine_inventory_doctor'))
    
@app.route('/update-medicine-inventory-doctor', methods=['POST'])
def update_medicine_inventory_doctor():
    if request.method == 'POST':
        # Get information of new medicine from the form
        id_input = request.form['edit_id']
        name_input = request.form['edit_name']
        price_input = request.form['edit_price']
        side_effect_input = request.form['edit_side_effect']
        usage_input = request.form['edit_usage']
        manufacturer_input = request.form['edit_manufacturer']
        pack_size_label_input = request.form['edit_pack_size_label']
        composition_1_input = request.form['edit_composition_1']
        composition_2_input = request.form['edit_composition_2']
        remarks_input = request.form['edit_remarks']
        quantity_input = request.form['edit_quantity']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute UPDATE statement to update medicine data
        cur.execute("UPDATE medicine_inventory SET medicine_name=%s, medicine_price=%s, medicine_side_effect=%s, medicine_usage=%s, medicine_manufacturer_name=%s, medicine_pack_size_label=%s, medicine_composition_1=%s, medicine_composition_2=%s, medicine_remarks=%s, medicine_quantity=%s WHERE medicine_id=%s", 
                    (name_input, price_input, side_effect_input, usage_input, manufacturer_input, pack_size_label_input, composition_1_input, composition_2_input, remarks_input, quantity_input, id_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('medicine_inventory_doctor'))
    
@app.route('/delete-medicine-inventory-doctor', methods=['POST'])
def delete_medicine_inventory_doctor():
    if request.method == 'POST':
        # Get information of new medicine from the form
        id_input = request.form['delete_id']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute DELETE statement to delete medicine data
        cur.execute("DELETE FROM medicine_inventory WHERE medicine_id=%s", (id_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('medicine_inventory_doctor'))

# ================================================================
#                           Admin
# ================================================================
@app.route('/dashboard-admin')
def dashboard_admin():
    if session['role'] == 'admin':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated user type data
        cur.execute("SELECT count(user_id) FROM users WHERE user_role='admin'")
        # Fetch the updated data
        adminCount_data = cur.fetchall()
        # Execute SELECT statement to fetch updated user type data
        cur.execute("SELECT count(user_id) FROM users WHERE user_role='staff'")
        # Fetch the updated data
        staffCount_data = cur.fetchall()
        # Execute SELECT statement to fetch updated user type data
        cur.execute("SELECT count(user_id) FROM users WHERE user_role='doctor'")
        # Fetch the updated data
        doctorCount_data = cur.fetchall()
        # Close the cursor
        cur.close()
        return render_template('dashboard-admin.html', adminCount_data=adminCount_data, staffCount_data=staffCount_data, doctorCount_data=doctorCount_data)
    else:
        return render_template('error403.html')

@app.route('/user-management-admin')
def user_management_admin():
    if session['role'] == 'admin':

        email_exists = request.args.get('email_exists', default=False, type=bool)
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated user data
        cur.execute("SELECT * FROM users")
        # Fetch the updated data
        data = cur.fetchall()
        # Close the cursor
        cur.close()

        return render_template('user-management-admin.html', user_data=data,  email_exists=email_exists)
    else:
        return render_template('error403.html')

@app.route('/add-user-management-admin', methods=['POST'])
def add_user_management_admin():
    if request.method == 'POST':
        name_input = request.form['add_name']
        email_input = request.form['add_email']
        password_input = request.form['add_password']
        contact_number_input = request.form['add_contact_number']
        role_input = request.form['add_role']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute the search statement to find if the email is used in the database
        cur.execute("SELECT user_email FROM users WHERE user_email = %s", (email_input,))
        
        #Get the results
        existing_email = cur.fetchone()
        
        #If user exist, show pop up 
        if existing_email:
            cur.close()
            return redirect(url_for('user_management_admin', email_exists=True))
        
        # If the email is not use, execute INSERT statement to add user data
        cur.execute("INSERT INTO users(user_name, user_email, user_password, user_contact_number, user_role) VALUES (%s, %s, %s, %s, %s)", 
                    (name_input, email_input, password_input, contact_number_input, role_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('user_management_admin'))
    
@app.route('/update-user-management-admin', methods=['POST'])
def update_user_management_admin():
    if request.method == 'POST':
        # Get information of the user from the form
        id_input = request.form['edit_id']
        name_input = request.form['edit_name']
        email_input = request.form['edit_email']
        password_input = request.form['edit_password']
        contact_number_input = request.form['edit_contact_number']
        role_input = request.form['edit_role']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute the search statement to find if the email is used in the database, excluding the current user
        cur.execute("SELECT user_email FROM users WHERE user_email = %s AND user_id != %s", (email_input, id_input))
        
        # Get the results
        existing_email = cur.fetchone()
        
        # If user exists, show pop up 
        if existing_email:
            cur.close()
            return redirect(url_for('user_management_admin', email_exists=True))
        
        # If no account exists with the provided email, execute an UPDATE statement to update user data
        cur.execute("UPDATE users SET user_name=%s, user_email=%s, user_password=%s, user_contact_number=%s, user_role=%s WHERE user_id=%s", 
                    (name_input, email_input, password_input, contact_number_input, role_input, id_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('user_management_admin'))
    
@app.route('/delete-user-management-admin', methods=['POST'])
def delete_user_management_admin():
    if request.method == 'POST':
        # Get information of new user from the form
        id_input = request.form['delete_id']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute DELETE statement to delete user data
        cur.execute("DELETE FROM users WHERE user_id=%s", (id_input,))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('user_management_admin'))
    
# ================================================================
#                           PATIENT
# ================================================================
@app.route('/dashboard-patient')
def dashboard_patient():
    if session['role'] == 'patient':
        # MongoDB aggregation pipeline
        pipeline = [
            { '$match': { 'patient_id': f"{session['patientId']}" } },
            { '$group': {
                '_id': "$medicine_name",
                'total_quantity': { '$sum': { '$toInt': "$medicine_quantity" } }
            }},
            { '$sort': { 'total_quantity': -1 } }
        ]
        # Execute aggregation pipeline
        result = list(medicine_purchase_record.aggregate(pipeline))

        return render_template('dashboard-patient.html', preference_data=result)
    else:
        return render_template('error403.html')

@app.route('/appointment-patient')
def appointment_patient():
    if session['role'] == 'patient':
        # Execute appointment_record data
        data = list(appointment_record.find({"patient_id": f"{session['patientId']}"}))

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated schedule data
        cur.execute("SELECT schedule_request_date, schedule_purpose_of_visit FROM schedule WHERE patient_id=%s AND staff_id IS NOT NULL", (session['patientId'],))
        # Fetch the updated data
        schedule_data = cur.fetchall()
        # Close the cursor
        cur.close()

        return render_template('appointment-patient.html', appointment_data=data, schedule_data=schedule_data)
    else:
        return render_template('error403.html')

@app.route('/add-appointment-patient', methods=['POST'])
def add_appointment_patient():
    if request.method == 'POST':
        # Get information of new user from the form
        request_date_input = request.form['add_request_date']
        purpose_input = request.form['add_purpose']
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute INSERT statement to add schedule data
        cur.execute("INSERT INTO schedule(schedule_request_date, schedule_purpose_of_visit, schedule_remarks, schedule_creation_date, patient_id, staff_id) VALUE (%s, %s, %s, %s, %s, %s)", 
                    (request_date_input, purpose_input, "", today_date, session['patientId'], None,))
        # Commit the transaction
        mysql.connection.commit()
        # Fetch the last inserted ID
        cur.execute("SELECT LAST_INSERT_ID()")
        new_schedule_id = cur.fetchone()[0]
        # Close the cursor
        cur.close()

        # Create appointment record
        data = {"request_date":f"{request_date_input}", "purpose":f"{purpose_input}", "patient_id":f"{session['patientId']}", "schedule_id":f"{new_schedule_id}"}
        appointment_record.insert_one(data)

        return redirect(url_for('appointment_patient'))
    
@app.route('/update-appointment-patient', methods=['POST'])
def update_appointment_patient():
    if request.method == 'POST':
        # Get information of new user from the form
        id_input = request.form['edit_id']
        request_date_input = request.form['edit_request_date']
        purpose_input = request.form['edit_purpose']

        # Update appointment record
        data = { 'request_date':request_date_input, 'purpose':purpose_input}
        appointment_record.update_one({"_id": ObjectId(id_input)}, {"$set": data})

        # Get schedule id from appointment record
        record = appointment_record.find_one({'_id': ObjectId(id_input)}, {'schedule_id': 1})

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute UPDATE statement to update user data
        cur.execute("UPDATE schedule SET schedule_request_date=%s, schedule_purpose_of_visit=%s WHERE schedule_id=%s", 
                    (request_date_input, purpose_input, record['schedule_id'],))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        return redirect(url_for('appointment_patient'))
    
@app.route('/delete-appointment-patient', methods=['POST'])
def delete_appointment_patient():
    if request.method == 'POST':
        # Get information of new user from the form
        id_input = request.form['delete_id']

        # Get schedule id from appointment record
        record = appointment_record.find_one({'_id': ObjectId(id_input)}, {'schedule_id': 1})

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute DELETE statement to delete schedule data
        cur.execute("DELETE FROM schedule WHERE schedule_id=%s", (record['schedule_id'],))
        # Commit the transaction
        mysql.connection.commit()
        # Close the cursor
        cur.close()

        # Delete appointment record
        appointment_record.delete_one({"_id": ObjectId(id_input)})

        return redirect(url_for('appointment_patient'))
    
@app.route('/pharmacy-patient')
def pharmacy_patient():
    if session['role'] == 'patient':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated consultation data
        cur.execute("SELECT consultation_id, consultation_record_creation_date FROM consultation_record WHERE patient_id=%s", (session['patientId'],))
        # Fetch the updated data
        data = cur.fetchall()
        # Close the cursor
        cur.close()

        return render_template('pharmacy-patient.html', consultation_data=data)
    else:
        return render_template('error403.html')
    
@app.route('/pharmacy-medicine-patient/<int:id>')
def pharmacy_medicine_patient(id):
    if session['role'] == 'patient':
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute SELECT statement to fetch updated consultation data
        cur.execute("SELECT p.medicine_id, p.medicine_quantity, p.prescription_price, m.medicine_name FROM prescription_record p, medicine_inventory m WHERE p.consultation_id=%s AND p.medicine_id=m.medicine_id", (id,))
        # Fetch the updated data
        data = cur.fetchall()
        # Close the cursor
        cur.close()

        session['medicineCart'] = data

        return render_template('pharmacy-medicine-patient.html', prescription_data=data)
    else:
        return render_template('error403.html')
    
@app.route('/add-pharmacy-medicine-purchase-patient', methods=['POST'])
def add_pharmacy_medicine_purchase_patient():
    if request.method == 'POST':
        for item in session['medicineCart']:
            # Create medicine record
            data = {"medicine_name":f"{item[3]}", "medicine_quantity":f"{item[1]}", "medicine_price":f"{item[2]}", "patient_id":f"{session['patientId']}"}
            medicine_purchase_record.insert_one(data)

            # Create a cursor to execute SQL queries
            cur = mysql.connection.cursor()
            # Execute SELECT statement to fetch updated consultation data
            cur.execute("SELECT medicine_quantity FROM medicine_inventory WHERE medicine_id=%s", (item[0],))
            # Fetch the updated data
            medicine_quantity_data = cur.fetchall()
            # Execute UPDATE statement to update user data
            cur.execute("UPDATE medicine_inventory SET medicine_quantity=%s WHERE medicine_id=%s", (medicine_quantity_data[0][0]-item[1], item[0],))
            # Commit the transaction
            mysql.connection.commit()
            # Close the cursor
            cur.close()

        return redirect(url_for('pharmacy_patient'))
    else:
        return render_template('error403.html')

@app.route('/billing-patient')
def billing_patient():
    if session['role'] == 'patient':
        # Execute billing_record data
        data = list(billing_record.find({"patient_id": f"{session['patientId']}"}))

        return render_template('billing-patient.html', billing_data=data)
    else:
        return render_template('error403.html')
    
@app.route('/delete-billing-patient', methods=['POST'])
def delete_billing_patient():
    if request.method == 'POST':
        # Get information of new user from the form
        id_input = request.form['delete_id']
        # Delete record
        result = billing_record.delete_one({"_id": ObjectId(id_input)})

        return redirect(url_for('billing_patient'))

# ================================================================
#                           Profile
# ================================================================

@app.route('/profile')
def profile():
    # Render template for profile page
    return render_template('profile.html')

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if request.method == 'POST':
        # Get name, password and contact number from the form
        name_input = request.form['name']
        password_input = request.form['password']
        contact_number_input = request.form['contact_number']

        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        # Execute the UPDATE statement to update user data
        cur.execute("UPDATE users SET user_name=%s, user_password=%s, user_contact_number=%s  WHERE user_id=%s", (name_input, password_input, contact_number_input, session['user_detail'][0],))
        # Commit the transaction
        mysql.connection.commit()
        # Execute SELECT statement to fetch updated user data
        cur.execute("SELECT * FROM users WHERE user_id=%s", (session['user_detail'][0],))
        # Fetch the updated data
        data = cur.fetchall()
        # Close the cursor
        cur.close()

        # Fetch the updated data
        for user in data:
            session['user_detail'] = user

        return redirect(url_for('profile'))

if __name__ == '__main__':
    #app.run(debug=True)
    #app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='23.23.130.142', port=5000)