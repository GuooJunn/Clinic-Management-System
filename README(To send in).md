# Project README

## Prerequisites
- Ensure you have Visual C++ Build Tools installed. You can download and install Python from the official website: [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools).
- Ensure you have Python 3.10 interpreter installed. You can download and install Python from the official website: [Python Releases for Windows]( https://www.python.org/downloads/windows/).
- Ensure you have MySQL Community Server installed. You can download and install MySQL Community Server from the official website: [MySQL Community Downloads](https://dev.mysql.com/downloads/installer/).
- Ensure you have MySQL Workbeach installed. You can download and install MySQL Workbeach from the official website: [MySQL Community Downloads](https://dev.mysql.com/downloads/workbench/).
- Ensure you have MongoDB Community Server and MongoDB Compass installed. You can download and install MongoDB from the official website: [MongoDB Community Server Download](https://www.mongodb.com/try/download/community).

## Installation
Install the required packages:

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

    MySQL (Using MySQL Workbench)
    1. Connect to MySQL Server:
        - Open MySQL Workbench and create a new connection using your RDS endpoint or localhost.
        - Enter your MySQL credentials.
    2. Run script.sql:
        - Open script.sql in MySQL Workbench.
        - Click the Execute button to set up the database and tables.
    3. Verify:
        - Refresh the Schemas tab to confirm the database was created.
        
    Note: You can find the RDS Endpoint in your AWS Management Console:
        1. Go to Amazon RDS.
        2. Select your RDS instance.
        3. Under the Connectivity & Security tab, find the Endpoint (e.g., clouddb-app.b8.us-east-1.rds.amazonaws.com). 
        
    MongoDB (Using MongoDB Compass)
    1. Connect to MongoDB:
        - Open MongoDB Compass and connect using either your MongoDB public or private URI(*Strongly sugguest to use private for security reasons): mongodb://"Public or Private IP Address":27017 (e.g. mongodb://172.30.6.21:27017)
        
    Note: The Public or Private IP Address of your MongoDB instance can be found in your AWS EC2 dashboard
     1. Go to Amazon EC2.
     2. Select your MongoDB instance.
     3. Under the Description tab, locate the Public or Private IP (e.g., 172.30.6.21).

2. Configure MySQL(RDS) and MongoDB Client in app.py

    - Change accordingly

   MySQL(RDS)
   ```python
   app.config['MYSQL_HOST'] = "Amazon RDS Endpoint"(e.g. clouddb-app.b8.us-east-1.rds.amazonaws.com)
   app.config['MYSQL_USER'] = "root"
   app.config['MYSQL_PASSWORD'] = ""
   app.config['MYSQL_DB'] = "Clinic_Cloud_DB"
   ```
   
   - Default MySQL port is 3306. To reconfigure, add:
   ```python
    app.config['MYSQL_PORT'] = <insert port number>
   ```

   MongoDB Client
   ```python
   client = MongoClient('mongodb://Public or Private IP Address:27017') (e.g. mongodb://172.30.6.21:27017)
   ```

4. Running the Flask App:

    You can choose to run the Flask app based on your preferred method:
    
    Run locally 
    ```
    flask run 
    ```

    Access via your AWS elastic ip address 
    ```
    flask run --host=0.0.0.0 --port=5000
    ``` 

    or go to app.py --> Click "Run" --> "Start Debugging" / "Run Without Debugging" 

This will start the Flask development server. For local, and your app will be accessible at `http://127.0.0.1:5000/` while for AWS elastic IP Address, your app will be available at both `http://127.0.0.1:5000/` and `http://AWS elastic IP Address:5000/`(http://23.23.10.12:5000/) in your web browser.

**Note:** This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.

5. Other information

Default login access 
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
