from flask import Flask, render_template, request
from datetime import datetime
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

#main page
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html',date=datetime.now())

# add employee page
@app.route("/addemp/",methods=['GET','POST'])
def addEmp():
    return render_template('AddEmp.html',date=datetime.now())


@app.route("/addemp/insert", methods=['POST'])
def Emp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

#Get Employee DONE
@app.route("/getemp/")
def getEmp():
    return render_template('GetEmp.html',date=datetime.now())


#Get Employee Results
@app.route("/getemp/results",methods=['GET','POST'])
def Employee():
    
     #Get Employee
     emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
     select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"

     
     cursor = db_conn.cursor()
        
     try:
         cursor.execute(select_stmt, { 'emp_id': int(emp_id) })
         # #FETCH ONLY ONE ROWS OUTPUT
         for result in cursor:
            print(result)
        

     except Exception as e:
        return str(e)
        
     finally:
        cursor.close()
    

     return render_template("GetEmpOutput.html",result=result,date=datetime.now())

# Leave
@app.route("/leave/")
def leave():
    return render_template("Leave.html",date=datetime.now())

# apply leave
@app.route("/leave/apply", methods=['GET','POST'])
def applyLeave():
    emp_id = request.form['emp_id']
    StartLeave = request.form['start_date']
    EndLeave = request.form['end_date']

    # Insert statement
    insert_stmt = "INSERT INTO leave VALUES ((%(emp_id)s),(%(start_date)s),(%(end_date)s),(%(leave_status)s))"

    cursor = db_conn.cursor()

    start_date = datetime.strptime(StartLeave,'%Y-%m-%d')
    end_date = datetime.strptime(EndLeave,'%Y-%m-%d')

    try:
        cursor.execute(insert_stmt, {'emp_id': int(emp_id), 'start_date': start_date, 'end_date': end_date, 'leave_status': 1})
        db_conn.commit()
        print(" Data Inserted into MySQL")

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template("LeaveOutput.html", date=datetime.now(), StartLeave=start_date,
    EndLeave=end_date)

# change leave
@app.route("/leave/change", methods=['GET','POST'])
def manageLeave():
    emp_id = request.form['emp_id']
    StartLeave = request.form['start_date']
    EndLeave = request.form['end_date']

    # Update statement
    update_stmt = "UPDATE leave SET start_date = (%(start_date)s), end_date = (%(end_date)s) WHERE emp_id = %(emp_id)s AND start_date = (%(start_date)s) AND end_date = (%(end_date)s)"

    cursor = db_conn.cursor()

    start_date = datetime.strptime(StartLeave,'%Y-%m-%d')
    end_date = datetime.strptime(EndLeave,'%Y-%m-%d')

    try:
        cursor.execute(update_stmt, {'emp_id': int(emp_id), 'start_date': start_date, 'end_date': end_date})
        db_conn.commit()
        print(" Data Updated Successfully")

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template("LeaveOutput.html", date=datetime.now(), StartLeave=start_date,
    EndLeave=end_date)

# cancel leave
@app.route("/leave/cancel", methods=['GET','POST'])
def cancelLeave():
    emp_id = request.form['emp_id']
    StartLeave = request.form['start_date']
    EndLeave = request.form['end_date']

    # Update statement
    update_stmt = "UPDATE leave SET leave_status = 0 WHERE emp_id = %(emp_id)s AND start_date = (%(start_date)s) AND end_date = (%(end_date)s)"

    cursor = db_conn.cursor()

    start_date = datetime.strptime(StartLeave,'%Y-%m-%d')
    end_date = datetime.strptime(EndLeave,'%Y-%m-%d')

    try:
        cursor.execute(update_stmt, {'emp_id': int(emp_id), 'start_date': start_date, 'end_date': end_date})
        db_conn.commit()
        print(" Data Updated Successfully")

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template("Leave.html", date=datetime.now())


# get leave
@app.route("/leave/get", methods=['GET','POST'])
def getLeave():
    #Get Employee
    emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    select_stmt = "SELECT * FROM leave WHERE emp_id = %(emp_id)s AND leave_status = 1"

     
    cursor = db_conn.cursor()
        
    try:
        cursor.execute(select_stmt, { 'emp_id': int(emp_id) })

        # FETCH ONLY ONE ROWS OUTPUT
        for result in cursor:
            print(result)
        

    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()
    

    return render_template("GetLeave.html",result=result,date=datetime.now())


# Wages
@app.route("/wages/")
def wages():
    return render_template("Wages.html",date=datetime.now())



# insert wages
@app.route("/wages/insert", methods=['GET','POST'])
def insertWages():
    emp_id = request.form['emp_id']
    salary = int(request.form['salary'])


    # select statement
    select_stmt = "SELECT wages_status from wages WHERE emp_id = %(emp_id)s AND wages_status = 1"

    cursor1 = db_conn.cursor()
    cursor2 = db_conn.cursor()
    cursor3 = db_conn.cursor()

    RegisterDate = datetime.now()
    register_date = RegisterDate.strftime('%Y-%m-%d')
    end_date = None

    try:
        cursor1.execute(select_stmt, { 'emp_id': int(emp_id) })
        if cursor1.rowcount == 0:

            # Insert statement
            insert_stmt = "INSERT INTO wages VALUES ((%(emp_id)s),(%(salary)s),(%(register_date)s),(%(end_date)s),(%(wages_status)s))"

            try:
                cursor2.execute(insert_stmt, {'emp_id': int(emp_id), 'salary': salary,
                 'register_date': start_date, 'end_date': end_date, 'wages_status': 1})
                db_conn.commit()
                print(" Data Inserted into MySQL")

            except Exception as e:
                return str(e)
            finally:
                cursor2.close()

        else:
            
            # Update statement
            update_stmt = "UPDATE wages SET wages_status = 0 WHERE wages_status = 1 AND emp_id = %(emp_id)s"

            try:
                cursor3.execute(update_stmt, { 'emp_id': int(emp_id) })
                db_conn.commit()
                print(" Data Updated Successfully")

                # Insert statement
                insert_stmt = "INSERT INTO wages VALUES ((%(emp_id)s),(%(salary)s),(%(register_date)s),(%(end_date)s),(%(wages_status)s))"

                try:
                    cursor2.execute(insert_stmt, {'emp_id': int(emp_id), 'salary': salary,
                     'register_date': start_date, 'end_date': end_date, 'wages_status': 1})
                    db_conn.commit()
                    print(" Data Inserted into MySQL")

                except Exception as e:
                    return str(e)
                finally:
                    cursor2.close()

            except Exception as e:
                return str(e)
            finally:
                cursor3.close()

    except Exception as e:
        return str(e)

    finally:
        cursor1.close()

    return render_template("WagesOutput.html", date=datetime.now(), RegisterDate=start_date, 
    Salary=salary)


# get wages
@app.route("/wages/get", methods=['GET','POST'])
def getWages():
    #Get Employee
    emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    select_stmt = "SELECT emp_id, salary, register_date, end_date FROM wages WHERE emp_id = %(emp_id)s AND wages_status = 1"

     
    cursor = db_conn.cursor()
        
    try:
        cursor.execute(select_stmt, { 'emp_id': int(emp_id) })

        # FETCH ONLY ONE ROWS OUTPUT
        for result in cursor:
            print(result)
        

    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()
    

    return render_template("GetWages.html",result=result,date=datetime.now())





# change port number
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
