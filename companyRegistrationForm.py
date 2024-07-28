# Creator: Israel Showell
# Start Date: 7/27/2024
# End Date: 7/27/2024
# Project: Inventory Management - Login Backend
# Version: 1.00

# Description:
"""
This is the Back-End of the registration functionality of the Inventory Management software.
"""

#These are the imported libraries I am using to make the program
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,TextAreaField,SubmitField
from wtforms.validators import DataRequired

#Here, I create a form format that will be rendered by app.py and by the HTML page
class companyRegisterForm(FlaskForm):

    #Creates the companyName field and requires users to use it.
    companyName=StringField(label="Company Name",validators=[DataRequired()])

    #Creates the businessAddress TextAreaField
    companyAddress=TextAreaField(label="Company Address")

    # #Creates the employeeNumber field and requires users to use it.
    employeeNumber=IntegerField(label="Number of Employees: ")

    #Creates the button for users to submit their form
    Submit=SubmitField(label="Send")

#End of Script
