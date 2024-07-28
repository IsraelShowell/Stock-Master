# Creator: Israel Showell
# Start Date: 7/27/2024
# End Date: 7/27/2024
# Project: Inventory Management - Login Backend
# Version: 1.20

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

@app.route('/dashboard')
def dashboard():
    # Get the username from the session
    username = session.get('username')
    if not username:
        return render_template('login.html')  # Redirect to login if username is not in the session

    try:
        # Connect to the database
        con = sqlite3.connect('inventory-management.db')
        c = con.cursor()

        # Fetch the user's company information
        c.execute("""
            SELECT company_name, company_address, employee_number, company_id 
            FROM companies 
            INNER JOIN users ON companies.user_id = users.user_id 
            WHERE users.username = ?
        """, (username,))

        # Save the query result in a variable
        company_info = c.fetchone()
        if not company_info:
            return render_template('dashboard.html', error="Company information not found.")

        # Save the company id to the session
        company_id = company_info[3]
        session['company_id'] = company_id

    except Exception as e:
        print(f"Error occurred: {e}")
        return render_template('dashboard.html', error="Failed to load company information.")
    finally:
        con.close()

    # Pass the user's name and company information to the template
    return render_template('dashboard.html', name=username, company_info=company_info)

#This function updates the inventory dashboard to ensure the user's data is current!
def fetch_inventory(company_id):
    con = sqlite3.connect('inventory-management.db')
    c = con.cursor()
    c.execute("SELECT product_name, quantity, reorder_level, product_description, product_manufacturer, company_id, product_id FROM inventory WHERE company_id = ?", (company_id,))
    inventory_items = c.fetchall()
    con.close()

    #This returns a tuple of the selected data
    return inventory_items


@app.route('/inventory', methods=['POST', 'GET'])
def Inventory():

    #This gets and checks the company_id in session
    company_id = session.get('company_id')
    if not company_id:
        return render_template("dashboard.html")

    #Checks if the page is in POST
    if request.method == 'POST':

        #Saves the data from the form into these variable
        product_name = request.form.get('product_name')
        quantity = request.form.get('quantity')
        reorder_level = request.form.get('reorder_level')
        product_description = request.form.get('product_description')
        product_manufacturer = request.form.get('product_manufacturer')

        #Checks if the fields all have data in them
        if (product_name and quantity and reorder_level and product_description and product_manufacturer):
            try:
                #The program tries to make a connection to the database
                con = sqlite3.connect('inventory-management.db')
                c = con.cursor()
                c.execute(
                    "INSERT INTO inventory (product_name, quantity, reorder_level, product_description, product_manufacturer, company_id) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (product_name, quantity, reorder_level, product_description, product_manufacturer, company_id)
                )
                #If successful, the product is added into the database!
                con.commit()
                con.close()

                # Fetch the updated inventory items
                inventory_items = fetch_inventory(company_id)
                return render_template("inventory.html", inventory_items=inventory_items,
                                       success="Product added successfully!")
            except Exception as e:
                #If it fails, the query is stopped and reversed to preserve data integrity
                con.rollback()
                con.close()

                #Makes sure that the product list is updated
                inventory_items = fetch_inventory(company_id)
                return render_template("inventory.html", inventory_items=inventory_items,
                                       error="There was an error adding the product: " + str(e))
        else:
            # Makes sure that the product list is updated
            inventory_items = fetch_inventory(company_id)
            return render_template("inventory.html", inventory_items=inventory_items, error="All fields are required.")
    else:
        # Makes sure that the product list is updated
        inventory_items = fetch_inventory(company_id)
        return render_template("inventory.html", inventory_items=inventory_items)


#This is where the user can update already existing items.
@app.route('/update_inventory', methods=['POST', 'GET'])
def update_inventory():
    # Get the id from the query parameters
    product_id = request.args.get('product_id')

    # Gather the company id for future use
    company_id = session.get('company_id')
    if not company_id:
        return render_template('dashboard.html')

    # Checks if the system is in POST
    if request.method == 'POST':
        # Saves data to variables
        product_name = request.form.get('product_name')
        quantity = request.form.get('quantity')
        reorder_level = request.form.get('reorder_level')
        product_description = request.form.get('product_description')
        product_manufacturer = request.form.get('product_manufacturer')

        # Sees if the fields all contain data
        if product_name and quantity and reorder_level and product_description and product_manufacturer:
            try:
                # Tries to make connection to the database to update the information
                con = sqlite3.connect('inventory-management.db')
                c = con.cursor()
                c.execute(
                    "UPDATE inventory SET product_name = ?, quantity = ?, reorder_level = ?, product_description = ?, product_manufacturer = ? WHERE product_id = ? AND company_id = ?",
                    (product_name, quantity, reorder_level, product_description, product_manufacturer, product_id, company_id)
                )
                con.commit()
                con.close()
                inventory_items = fetch_inventory(company_id)
                return render_template("inventory.html", inventory_items=inventory_items,
                                       success="Product updated successfully!")
            except Exception as e:
                # If it fails, the query is stopped and reversed to preserve data integrity
                con.rollback()
                con.close()
                return render_template("update_inventory.html", inventory_item=(product_name, quantity, reorder_level, product_description, product_manufacturer), error="There was an error updating the product: " + str(e))
        else:
            return render_template("update_inventory.html", inventory_item=(product_name, quantity, reorder_level, product_description, product_manufacturer), error="All fields are required.")
    else:
        # This fills out the data fields to show the user what is already there
        con = sqlite3.connect('inventory-management.db')
        c = con.cursor()
        c.execute("SELECT product_name, quantity, reorder_level, product_description, product_manufacturer FROM inventory WHERE product_id = ? AND company_id = ?", (product_id, company_id))
        inventory_item = c.fetchone()
        con.close()
        if inventory_item:
            return render_template('update_inventory.html', inventory_item=inventory_item)
        else:
            inventory_items = fetch_inventory(company_id)
            return render_template("inventory.html", inventory_items=inventory_items,
                                   error="Product not found.")



@app.route('/delete_inventory_item')
def delete_inventory_item():
    # Get the id from the query parameters
    product_id = request.args.get('product_id')

    # Gather the company id for future use
    company_id = session.get('company_id')
    if not company_id:
        return render_template('dashboard.html')

    # Try to make connection to the database to delete the information
    try:
        con = sqlite3.connect('inventory-management.db')
        c = con.cursor()
        c.execute(
            "DELETE FROM inventory WHERE product_id = ? AND company_id = ?",
            (product_id, company_id)
        )
        con.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
        return render_template('dashboard.html', error="Failed to delete product.")
    finally:
        con.close()

    inventory_items = fetch_inventory(company_id)
    return render_template("inventory.html", inventory_items=inventory_items, success="Product deleted successfully!")

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

        #This allows the user to skip by adding input to the field
        if request.form.get('Skip_Button'):
            return render_template("login.html")

        # Checks to make sure all required fields are filled
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
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        reorder_level INTEGER,
        product_description TEXT NOT NULL,
        product_manufacturer TEXT NOT NULL,
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
