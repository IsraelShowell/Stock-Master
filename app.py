# Creator: Israel Showell
# Start Date: 7/27/2024
# End Date: 7/27/2024
# Project: Inventory Management - Login Backend
# Version: 1.00

# Description:
"""
This is the Back-End of the login functionality of the Inventory Management software.
"""

# These are the imported libraries I am using to make the program
from flask import Flask, render_template, request, session
from companyRegistrationForm import companyRegisterForm
from userRegistrationForm import userRegisterForm
import sqlite3

# Important variables and objects
# Required by Flask to detect the app when running 'flask run'
app = Flask(__name__)

# This is used to help protect data being sent by the app.
# This protection is used to defend against CSRF attacks.
# (Cross-Site Request Forgery)
app.secret_key = "__privatekey__"


# All HTML files are located in the 'templates' because that is where render_template looks for HTML files

# The Home Page is located as the root of the web page
@app.route('/')
def Home():
    # Home is referenced in the HTML files
    return render_template('index.html')


# The Login Page is able to detect POST and GET requests
# POST sends data, GET gets data
@app.route('/login', methods=['POST', 'GET'])
def login():
    # When the button is pressed, the user makes the page send a POST request
    if request.method == 'POST' and request.form['Username'] != "" and request.form['Password']:
        # Saves the request's data in variables
        username = request.form['Username']
        password = request.form['Password']

        # Then it connects to the database
        con = sqlite3.connect('inventory-management.db')
        # c serves as a database cursor, a control structure that enables traversal over the records in a database
        c = con.cursor()

        # statement holds an SQL Query for the users table in the users database
        # This query checks to see if the user and password entered exist in the database
        statement = "SELECT * FROM users WHERE Username=? AND Password=?;"
        # We then tell the cursor to run the query
        c.execute(statement, (username, password))

        # c.fetchone fetches the next row of a query result and returns a single tuple,
        # Or None if no more rows are available.
        if not c.fetchone():
            # If the user and password are not found, the program will not sign them in
            return render_template("login.html",error="Username or password is incorrect!")
        else:
            # If the login is right, they go to the dashboard page, and their name is displayed
            #This detects the stored session name
            session['username'] = username

            return dashboard()
    elif request.method == 'GET':
        # If the user is just going to the login page, the page is rendered by the program
        return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    # Get the username from the session
    username = session.get('username')
    # Connect to the database
    con = sqlite3.connect('inventory-management.db')
    c = con.cursor()

    # Fetch the user's company information
    # The query selects the company name, company address, and the number of employees from the companies table.
    # It uses an INNER JOIN to combine rows from the companies and users tables based on a related column between them.
    # It joins on the user_id column which is present in both tables.
    # This ensures that only the companies associated with the logged-in user are selected.

    c.execute("""
        SELECT company_name, company_address, employee_number 
        FROM companies 
        INNER JOIN users ON companies.user_id = users.user_id 
        WHERE users.username = ?
    """, (username,))

    company_info = c.fetchone()

    # Close the database connection
    con.close()

    # Pass the user's name and company information to the template
    return render_template('dashboard.html', name=username, company_info=company_info)



# The registrationForm Page is able to detect POST and GET requests
# POST sends data, GET gets data
@app.route('/registrationform', methods=['POST', 'GET'])
def userRegistrationForm():
    # This creates an object named PingPong based off of the form defined in the userRegistrationForm module
    registerUserForm = userRegisterForm()

    # The program connects to the database
    db2 = sqlite3.connect('inventory-management.db')
    # c serves as a database cursor, a control structure that enables traversal over the records in a database
    c = db2.cursor()

    # When the button is pressed, the user makes the page send a POST request
    if request.method == 'POST':
        # Checks to make sure all required fields are filled
        if (request.form["Username"] != "" and request.form["Password"] != "" and
                request.form["phoneNumber"] != "" and request.form["Address"] != "" and
                request.form["Gender"] != "" and request.form["Age"] != ""):

            # Saves the request's data in variables
            username = request.form['Username']
            password = request.form['Password']
            phoneNumber = request.form['phoneNumber']
            address = request.form['Address']
            gender = request.form['Gender']
            age = request.form['Age']

            # statement holds an SQL Query for the users table in the users database
            # This query checks to see if the user and password entered exist in the database
            statement = "SELECT * FROM users WHERE username=? AND password=?;"

            # We then tell the cursor to run the query
            c.execute(statement, (username, password))

            # Stores the result of the query in the data variable
            data = c.fetchone()

            # If the data matches both the password and username, then the user will be taken to the error page
            if data:
                return render_template("error.html")
            else:
                # If at least the Password or Username are different from what is in the database
                if not data:
                    # Then the user's username and password will be added into the database
                    c.execute(
                        "INSERT INTO users (username, password, phone_number, address, gender, age) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (username, password, phoneNumber, address, gender, age))
                    db2.commit()

                    session['username'] = username

                    statement = "SELECT user_id FROM users WHERE username=?;"

                    # We then tell the cursor to run the query
                    # This returns a tuple for the .fetchone()
                    c.execute(statement, (username,))

                    data = c.fetchone()

                    #Gets the first value from the tuple
                    session['user_id'] = data[0]

                    db2.close()
                    # Then they are taken to the company register page

                    registerCompanyForm = companyRegisterForm()
                    return render_template('company_register.html', form=registerCompanyForm, error="Please fill all the fields!")
        else:
            # If any field is empty, return the registration form with an error message
            return render_template('register.html', form=registerUserForm, error="A field is empty. Please fill all the fields!")

    # When a user first goes to the register page, the page is rendered with a fresh form
    elif request.method == 'GET':
        return render_template('register.html', form=registerUserForm)

@app.route('/companyregistrationform', methods=['POST', 'GET'])
def companyRegistrationForm():
    # This creates an object named registerCompanyForm based on the form defined in the companyRegisterForm module
    registerCompanyForm = companyRegisterForm()

    # The program connects to the database
    db2 = sqlite3.connect('inventory-management.db')
    # c serves as a database cursor, a control structure that enables traversal over the records in a database
    c = db2.cursor()

    # When the button is pressed, the user makes the page send a POST request


    if request.method == 'POST':
        # Checks to make sure all required fields are filled
        if request.form.get('Skip_Button'):
            return render_template("login.html")

        if (request.form["companyName"] != "" and request.form["companyAddress"] != "" and
                request.form["employeeNumber"] != ""):
            # This allows the user to skip adding a company!
            # Saves the request's data in variables
            companyName = request.form['companyName']
            companyAddress = request.form['companyAddress']
            employeeNumber = request.form['employeeNumber']

            # statement holds an SQL Query for the companies table in the database
            # This query checks to see if the company already exists in the database
            statement = f"SELECT * FROM companies WHERE company_name='{companyName}';"

            # We then tell the cursor to run the query
            c.execute(statement)

            # Stores the result of the query in the data variable
            data = c.fetchone()

            # If the data matches the company name, then the user will be taken to the error page
            if data:
                return render_template("company_error.html")
            else:
                # If the company name is not in the database
                # Then the company's details will be added into the database
                userid = session.get("user_id")
                c.execute("INSERT INTO companies (company_name, company_address, employee_number,user_id) "
                              "VALUES (?, ?, ?, ?)",
                              (companyName, companyAddress, employeeNumber, userid))
                db2.commit()
                db2.close()
                # Then they are taken to a confirmation page
                return render_template("login.html")
        else:
            # This allows the user to skip adding a company!
            if request.form.get('Skip_Button') or not request.form.get('Skip_Button'):
                return render_template("login.html")
            
            # If any field is empty, return the registration form with an error message
            return render_template('company_register.html', form=registerCompanyForm, error="Please fill all fields.")

      # When a user first goes to the register page, the page is rendered with a fresh form
    elif request.method == 'GET':
        if request.form.get('Skip_Button'):
            return render_template("login.html")
        return render_template('company_register.html', form=registerCompanyForm)


# This is the start-up function that runs when I run flask app in the command line to start the development server
def startup():
    # Connects to the database
    con = sqlite3.connect('inventory-management.db')
    # Sets a cursor
    user_cursor = con.cursor()

    #This creates the users Table
    user_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        phone_number INTEGER NOT NULL,
        address TEXT NOT NULL,
        gender TEXT NOT NULL,
        age INTEGER NOT NULL
    )
    """)

    #This creates the businesses Table
    user_cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies(
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL UNIQUE,
        company_address TEXT NOT NULL,
        employee_number INTEGER NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    #This creates the inventory Table
    user_cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory(
        inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        reorder_level INTEGER,
        company_id INTEGER,
        FOREIGN KEY(company_id) REFERENCES companies(company_id)
    )
    """)

    #Commits the changes and close the connection
    con.commit()
    con.close()

# This needs to be outside the __name__ part, because Flask skips over it.
startup()
if __name__ == '__main__':
    app.run()

# End of Script
