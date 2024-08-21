import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
from decimal import Decimal
from datetime import date

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Function to create a database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Moiz_Khan786',
            database='expenses_insight'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Function to execute a query
def execute_query(query, values=None):
    connection = get_db_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor()

        # Execute the query with or without values
        cursor.execute(query, values if values else ())

        # Determine if the query is a SELECT or not
        if query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
        else:
            # For INSERT, UPDATE, DELETE, etc., commit the transaction
            connection.commit()
            results = cursor.rowcount  # Returns the number of rows affected

        cursor.close()
        connection.close()
        return results
    except mysql.connector.Error as err:
        print(f"Query Error: {err}")
        return None

def create_hash(password):
    password_bytes = password.encode('utf-8')
    # Create an MD5 hash object
    hash_object = hashlib.md5(password_bytes)
    # Get the hexadecimal representation of the hash
    hashed_password = hash_object.hexdigest()
    return hashed_password

def check_pass(hashed_pass, pass_list):
    return hashed_pass in pass_list

def create_new_id():
    query = 'SELECT MAX(User_id) FROM users'
    result = execute_query(query)
    new_user_id = result[0][0] if result[0][0] is not None else 0
    new_user_id += 1
    return str(new_user_id)


def get_exp_id():
    query='SELECT MAX(Exp_id) FROM expenses'
    result = execute_query(query)
    user_exp_id = result[0][0] if result[0][0] is not None else 0
    user_exp_id += 1
    return str(user_exp_id)
    
def summ_of_expenses(user_id_know):
    try:
        query_sum = 'SELECT SUM(amount) FROM expenses WHERE User_id =  %s'
        sum_result = execute_query(query_sum, (user_id_know,))  # Make sure to pass the query and parameters correctly
        sum = sum_result[0] if sum_result else 0  # Handle the case where sum_result is None or empty
        return sum
    except Exception as e:
        return e

# Route to show the login screen
@app.route('/')
def show_login_screen():
    return render_template('index.html')

# Route to handle login submission and checking
@app.route('/login', methods=['POST'])
def app_login():
    user_input_usr_name = request.form.get('username')
    user_input_usr_pass = request.form.get('password')

    if not user_input_usr_name or not user_input_usr_pass:
        return "No input provided. Please try again."

    hashed_pass = create_hash(user_input_usr_pass)

    if user_input_usr_name.isdigit():
        query = 'SELECT User_id FROM users WHERE User_id = %s'
        pass_query = 'SELECT Pass_Hash FROM users WHERE User_id = %s'
        user_list = [t[0] for t in execute_query(query, (int(user_input_usr_name),))]
        pass_list = [t[0] for t in execute_query(pass_query, (int(user_input_usr_name),))]
        is_digit = True
    else:
        query = 'SELECT User_Name FROM users WHERE User_Name = %s'
        pass_query = 'SELECT Pass_Hash FROM users WHERE User_Name = %s'
        user_list = [t[0] for t in execute_query(query, (user_input_usr_name,))]
        pass_list = [t[0] for t in execute_query(pass_query, (user_input_usr_name,))]
        is_digit = False

    if pass_list is None:
        return "Database error occurred."

    pass_true = check_pass(hashed_pass, pass_list)

    if is_digit:
        if int(user_input_usr_name) in user_list and pass_true:
            session['user_id'] = user_input_usr_name
            view_query = 'SELECT * FROM expenses WHERE User_id = %s'
            session['view_query'] = view_query
            session['is_digit'] = is_digit
            return redirect(url_for('welcome'))
    else:
        if user_input_usr_name in user_list and pass_true:
            session['user_id'] = user_input_usr_name
            view_query = 'SELECT User_id FROM users WHERE User_Name = %s'
            session['view_query'] = view_query
            session['is_digit'] = is_digit
            return redirect(url_for('welcome'))

    return render_template('user_not_found.html')

@app.route('/welcome')
def welcome():
    return render_template('new.html')

@app.route('/welcome/view_expenses', methods=['GET'])
def view_expenses():
    is_digit = session.get('is_digit')
    user_id = session.get('user_id')  # Retrieve user ID from session
    view_query = session.get('view_query')

    print(f"Executing query: {view_query} with value: {user_id}")  # Debugging

    if is_digit:
        user_expenses = execute_query(view_query, (user_id,))
        if user_expenses:
            cleaned_results = [
                    (
                        t[0], 
                        t[1], 
                        float(t[2]) if isinstance(t[2], Decimal) else t[2], 
                        t[3], 
                        t[4].strftime('%Y-%m-%d') if isinstance(t[4], date) else t[4], 
                        t[5]
                    )
                    for t in user_expenses
                ]
            summ_of_exp = summ_of_expenses(user_id)
            if summ_of_exp :
                print(summ_of_exp[0])
                return render_template('expenses.html', expenses=cleaned_results, sum=summ_of_exp[0])
        else:
            return f"No expenses found for this user. {user_id}, {view_query}"
    else:
        user_id_know = [t[0] for t in execute_query(view_query, (user_id,))]
        view_query = 'SELECT * FROM expenses WHERE User_id = %s'
        user_expenses = execute_query(view_query, (user_id_know[0],))
        if user_expenses:
            cleaned_results = [
                    (
                        t[0], 
                        t[1], 
                        float(t[2]) if isinstance(t[2], Decimal) else t[2], 
                        t[3], 
                        t[4].strftime('%Y-%m-%d') if isinstance(t[4], date) else t[4], 
                        t[5]
                    )
                    for t in user_expenses
                ]
            summ_of_exp = summ_of_expenses(user_id_know)
            if summ_of_exp :
                print(summ_of_exp[0])
                return render_template('expenses.html', expenses=cleaned_results, sum=summ_of_exp[0])
        else:
            return render_template('no_expenses_found.html')
    
@app.route('/create_new')
def create_new():
    return render_template('create_new.html')

@app.route('/userdata', methods=['POST'])
def user_data():
    new_user_name = request.form.get('username')  # Removed trailing comma
    new_user_pass = request.form.get('password')  # Removed trailing comma
    new_user_email = request.form.get('email')
    
    new_id = create_new_id()
    pass_hash = create_hash(new_user_pass)
    
    new_user_query = 'INSERT INTO users (User_id, User_Name, Pass_Hash, email_id) VALUES (%s, %s, %s, %s)'
    new_user_values = (new_id, new_user_name, pass_hash, new_user_email)
    
    # Call the function with the query and the values
    try:
        execute_query(new_user_query, new_user_values)
    except Exception as e:
        return f"an error occured {e}"
    if new_user_query:
        return render_template('new_user.html')
    
@app.route('/welcome/add_expenses', methods=['POST'])
def add_expenses():
    return render_template('add_expenses.html')

@app.route('/welcome/user_data_exp', methods=['POST'])
def user_data_exp():
    user_id = session.get('user_id')
    user_id_query = session.get('view_query')
    user_id_know = [t[0] for t in execute_query(user_id_query, (user_id,))]
    user_amt = request.form.get('amount')
    user_name = request.form.get('name')
    user_date = request.form.get('date')
    user_desc = request.form.get('description')
    user_exp_id = get_exp_id()
    add_exp_query = 'INSERT INTO expenses (Exp_id, User_id, amount, name, date, description) VALUES (%s, %s, %s, %s, %s, %s)'
    new_user_values = (user_exp_id, user_id_know[0], user_amt, user_name, user_date, user_desc)
    try:
        execute_query(add_exp_query, new_user_values)
    except Exception as e:
        return f"an error occured {e}"
    return render_template('data_added.html')


if __name__ == '__main__':
    app.run(debug=True)