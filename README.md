# Project README

## Prerequisites

- Ensure you have Python interpreter installed. You can download and install Python from the official website: [python.org](https://www.python.org/downloads/).
- Ensure you have MySQL Community Server installed. You can download and install Python from the official website: (https://dev.mysql.com/downloads/installer/).
- Ensure you have MongoDB Community Server installed. You can download and install Python from the official website: ((https://www.mongodb.com/try/download/community)).

## Installation

1. Install Flask:
    ```
    pip install Flask
    ```
2. Install Flask-MySQLdb:
    ```
    pip install flask-mysqldb
    ```
3. Install Pymongo:
    ```
    pip install pymongo
    ```

## Usage

1. Setup Database:

    - Run the script.sql

2. Configure MySQL in app.py

    - Change accordingly
   ```python
   app.config['MYSQL_HOST'] = "localhost"
   app.config['MYSQL_USER'] = "root"
   app.config['MYSQL_PASSWORD'] = ""
   app.config['MYSQL_DB'] = "Clinic_Cloud_DB"
   ```
   
   - Default MySQL port is 3306. To reconfigure, add:
   ```python
    app.config['MYSQL_PORT'] = <insert port number>
   ```

4. Running the Flask App:

    You can choose to run the Flask app based on your preferred method:
    
    ```
    flask run 
    flask run --host=0.0.0.0 --port=5000

    Website: http://23.23.130.142:5000/
    ```

    or go to app.py --> Click "Run" --> "Start Debugging" / "Run Without Debugging" 

This will start the Flask development server, and your app will be accessible at `http://127.0.0.1:5000/` in your web browser.

**Note:** This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.

5. Default login access 
    ```
    1. Role: Admin 
       User: Admin
       Email: admin1@example.com
       Password: password1

    
    2. Role:Staff
       User: Staff
       Email: staff1@example.com
       Password: password1

    3. Role: Doctor
       User: Doctor
       Email: doctor1@example.com
       Password: password1

    4. Role: Patient
       User: Bobby Jackson
       Email: patient1@example.com
       Password: password1
