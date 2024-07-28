# Creator: Israel Showell
# Start Date: 7/27/2024
# End Date: 7/28/2024
# Project: Inventory Management - Login Backend
# Version: 1.30

# Description:
"""
This is the Back-End of the registration functionality of the Inventory Management software.
"""

#These are the imported libraries I am using to make the program
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,IntegerField,TextAreaField,SubmitField
from wtforms.validators import ValidationError, DataRequired

#Here, I create a form format that will be rendered by app.py and by the HTML page
class userRegisterForm(FlaskForm):

    #Creates the username field and requires users to use it.
    Username=StringField(label="Username",validators=[DataRequired()])

    #Creates the password field and requires users to use it.
    Password=PasswordField(label="Password",validators=[DataRequired()])

    #Creates the phone field and requires users to use it.
    phoneNumber=IntegerField(label="Mobile Number",validators=[DataRequired()])

    # Creates the businessAddress TextAreaField
    Address = TextAreaField(label="Address")

    #Creates the Gender field
    Gender=StringField(label="Gender")

    #Creates the username field and requires users to use it.
    Age=IntegerField(label="Age")

    #Creates the button for users to submit their form
    Submit=SubmitField(label="Send")

#End of Script
