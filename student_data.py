from flask import Flask, request, render_template, jsonify
import pandas as pd
from flask_mail import Mail, Message
userdetails = pd.DataFrame(columns=['Email', 'Password', 'Name', 'Age', 'Education', 'Placement-Status','Resume','Company'])
placementdetails = pd.DataFrame(columns=['Company','Position','Salary','Requirements', 'Email'])



app = Flask(__name__, static_url_path='/static')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'nandabhavesh2003@gmail.com'
app.config['MAIL_PASSWORD'] = 'kzan jqgh rdve zuks'
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/student_login_index.html', methods=['GET', 'POST'])
def student_login():
    return render_template('student_login_index.html')


# Excel file path
excel_file_path = 'data.xlsx'
excel_file_path2 = 'data2.xlsx'


# Read existing data from the Excel file
try:
    userdetails = pd.read_excel(excel_file_path, engine='openpyxl')
except FileNotFoundError:
    pass  # File not found, create an empty DataFrame


# Read existing data from the Excel file
try:
    placementdetails = pd.read_excel(excel_file_path2, engine='openpyxl')
except FileNotFoundError:
    pass  # File not found, create an empty DataFrame

userdetails['Company'] = userdetails['Company'].fillna('')

@app.route('/data', methods=['POST'])
def process_data():
    global userdetails 
    if request.method == 'POST':
        data_from_html = request.form
        email = data_from_html.get('email_input')
        password = data_from_html.get('password_input')
        name = data_from_html.get('name_input')
        age = data_from_html.get('age_input')
        education = data_from_html.get('education_input')
        placement = data_from_html.get('placement_status')
        resume = data_from_html.get('resume')
        print("Received form data:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Name: {name}")
        print(f"Age: {age}")
        print(f"Education: {education}")
        print(f"Placement_Status: {placement}")
        print(f"Resume Google Drive Link: {resume}")
        login_data = {
        'Email': [email],
        'Password': [password],
        'Name': [name],
        'Age': [age],
        'Education': [education],
        'Placement-Status': [placement],
        'Resume': [resume]
        }
        userdetails = pd.concat([userdetails, pd.DataFrame(login_data, index=[0])], ignore_index=True)
        print(userdetails)
        userdetails.to_excel(excel_file_path, index=False, engine='openpyxl')
        return jsonify(success=True, error="Account Created Successfully🎉 You can now Login")
    return render_template('student_login_index.html')


@app.route('/logdata', methods=['POST'])
def logprocess_data():
    if request.method == 'POST':
        global user_info
        data_from_html = request.form
        logemail = data_from_html.get('logemail')
        logpassword = data_from_html.get('logpassword')
        matching_user = userdetails[(userdetails['Email'] == logemail) & (userdetails['Password'] == logpassword)]
        if not matching_user.empty:
            user_info = matching_user.to_dict(orient='records')[0]
            return jsonify(success=True)
        else:
            return jsonify(success=False, error2="Incorrect Email or Password")
    return render_template('student_login_index.html')


@app.route('/student_index.html', methods=['GET', 'POST'])
def student_index():
    global user_info
    if user_info:
        return render_template('student_index.html', data=user_info)


@app.route('/index.html', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/admin_login_index.html', methods=['GET', 'POST'])
def admin_login():
    return render_template('admin_login_index.html')


@app.route('/admin-log-data', methods=['POST'])
def adminlogprocess_data():
    if request.method == 'POST':
        data_from_html = request.form
        logemail = data_from_html.get('logemail')
        logpassword = data_from_html.get('logpassword')
        if logemail == 'admin@gmail.com' and logpassword == 'admin': 
            return jsonify(success=True)
        else:
            return jsonify(success=False, error4="Incorrect Email or Password")
    return render_template('admin_login_index.html')


@app.route('/admin_index.html', methods=['GET', 'POST'])
def submit():
    msg = None
    global placementdetails

    if request.method == 'POST':
        company = request.form.get('company')
        position = request.form.get('position')
        salary = request.form.get('salary')
        requirements = request.form.get('requirememts')
        email = request.form.get('email')

        # Check if the data already exists in placementdetails
        if not placementdetails[
            (placementdetails['Company'] == company) &
            (placementdetails['Position'] == position) &
            (placementdetails['Salary'] == salary) &
            (placementdetails['Requirements'] == requirements)
        ].empty:
            msg = None
        else:
            # Add the new data to placementdetails
            placement_data = {
                'Company': [company],
                'Position': [position],
                'Salary': [salary],
                'Requirements': [requirements],
                'Email':[email],
            }
            placementdetails = pd.concat(
                [placementdetails, pd.DataFrame(placement_data, index=[0])],
                ignore_index=True
            )

            # Save to Excel file
            placementdetails.to_excel(excel_file_path2, index=False, engine='openpyxl')
            msg = "Successfully added🎉"

    return render_template('admin_index.html', data=userdetails, msg=msg, placementdetails=placementdetails)


@app.route('/placementapply.html', methods=['GET', 'POST'])
def submit2():
    global placementdetails
    global user_info
    msg2 = None
    if request.method == 'POST':
        # Get the company name from the form submission
        company_name = request.form.get('company_name')

        # Check if user_info is available (user is logged in)

        # Update the 'Company' column in userdetails DataFrame with the selected company name
        userdetails.loc[userdetails['Email'] == user_info['Email'], 'Company'] = company_name

        # Save the updated DataFrame to the Excel file
        userdetails.to_excel(excel_file_path, index=False, engine='openpyxl')
        msg2 = "Successfully Applied🎉"
        
        # Send an email to the company's email address
        company_row = placementdetails[placementdetails['Company'] == company_name].iloc[0]
        company_email = company_row['Email']
        send_email(company_name, company_email, user_info)
            
    return render_template('placementapply.html', placementdetails=placementdetails,msg2=msg2)


# ... (your existing routes and code)

def send_email(company_name, company_email, user_info):
    subject = 'New Placement Application'
    body = f'The student with email {user_info["Email"]} has applied for a position at {company_name}.\n\nStudent Details:\n\n'
    
    fields_to_include = ['Name', 'Email', 'Age', 'Education','Resume']
    for field in fields_to_include:
        body += f"{field}: {user_info.get(field, 'N/A')}\n"

    msg = Message(subject, sender='nandabhavesh2003@gmail.com', recipients=[company_email])
    msg.body = body

    try:
        mail.send(msg)
        print(f"Email sent to {company_email} for {company_name}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")


@app.route('/remove-placement', methods=['POST'])
def remove_placement():
    global placementdetails
    if request.method == 'POST':
        data = request.json
        index_to_remove = int(data.get('index', -1))

        if 0 <= index_to_remove < len(placementdetails):
            # Remove the detail at the specified index
            placementdetails = placementdetails.drop(index=index_to_remove).reset_index(drop=True)

            # Save the updated DataFrame to the Excel file
            placementdetails.to_excel(excel_file_path2, index=False, engine='openpyxl')

            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Invalid index")
    return jsonify(success=False, error="Invalid request")


@app.route('/college_login_index.html', methods=['GET', 'POST'])
def college_login():
    return render_template('college_login_index.html')


if __name__ == '__main__':
    app.run(debug=True)
