from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import pymysql
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_DATABASE'] = os.getenv('MYSQL_DATABASE', 'userdata')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'username')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '20B423tian')

# Database configuration
db_config = {
    'host': 'localhost',
    'database': 'userdata',
    'user': 'username',
    'password': '20B423tian'
}

# Establish MySQL connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            database=app.config['MYSQL_DATABASE'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Sample route for login form (assuming you have form.html as in the uploaded file)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        
        # Connect to MySQL database and validate user
        connection = create_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user:
            return redirect(url_for('welcome'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('form.html')

# New route for displaying the login/signup form
@app.route('/auth_form')
def auth_form():
    return render_template('form.html')

# Route to handle authentication and account creation
@app.route('/auth', methods=['POST'])
def auth():
    username = request.form['username']
    password = request.form['password']
    action = request.form['action']

    if action == 'login':
        user_id = authenticate_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            print("User logged in:", session) 
            return redirect(url_for('user_page', username=username))
        else:
            return "Invalid credentials. Please try again."

    elif action == 'signup':
        if create_user(username, password):
            session['user_id'] = get_user_id(username)
            session['username'] = username
            return redirect(url_for('user_page', username=username))
        else:
            return "Signup failed. Username may already be taken."
    # connection = create_connection()
    # cursor = connection.cursor()

    # if action == 'login':
    #     # Attempt to log in
    #     query = "SELECT * FROM users WHERE username = %s AND password = %s"
    #     cursor.execute(query, (username, password))
    #     user = cursor.fetchone()
    #     user_id = authenticate_user(username, password)
    #     if user:
    #         session['user_id'] = user_id
    #         session['username'] = username  # Store the username in the session
    #         print(f"User logged in: {session['username']}, ID: {session['user_id']}")
    #         return redirect(url_for('user_page', username=username))
    #     else:
    #         return "Login failed. Check your credentials and try again."
    
    # elif action == 'signup':
    #     # Check if username already exists
    #     cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    #     existing_user = cursor.fetchone()
    #     if existing_user:
    #         return "Username already exists. Choose a different username."

    #     # Insert new user into database
    #     query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    #     cursor.execute(query, (username, password))
    #     connection.commit()
    #     session['user_id'] = get_user_id(username)
    #     session['username'] = username
    #     print(f"User signed up and logged in: {session['username']}, ID: {session['user_id']}")
    #     return redirect(url_for('user_page', username=username))

    # cursor.close()
    # connection.close()

# Logout route to clear the session
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))
    
# Placeholder functions for authentication and user creation
def authenticate_user(username, password):
     # Check if the user exists in the database
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            return user[0]  # Return user ID if authentication is successful
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None
    # # Replace with actual database authentication logic
    # if username == "catherine" and password == "catherine111":
    #     return 1  # Mock user ID
    # return None

def create_user(username, password):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False  # Username already exists
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return False

def get_user_id(username):
    # Mock user ID retrieval
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            return user[0]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return None
    
# Welcome route after successful login
@app.route('/welcome')
def welcome():
    return "Welcome to the application!"

app.secret_key = 'your_secret_key'  # For session management
USER_DATA_FILE = 'user_data.json'

@app.route('/')
def index():
    logged_in = 'username' in session

    # Load user posts from 'user_posts.json'
    if os.path.exists('user_posts.json'):
        with open('user_posts.json', 'r') as file:
            user_posts = json.load(file)
    else:
        user_posts = []
    
    return render_template('index.html', logged_in=logged_in, user_posts=user_posts)

# Load user data from the JSON file
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return an empty dictionary if the file doesn't exist or is empty

# Save user data to the JSON file
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    data = load_user_data()
    if username in data:
        return "Username already exists!"

    # Add new user with default level and experience
    data[username] = {'level': 1, 'experience': 0}
    save_user_data(data)
    return redirect(url_for('user_page', username=session.get('username')))

# Retrieve and display user information
@app.route('/user_page/<username>')
def user_page(username):
    print("Session contents:", session)

    if 'user_id' not in session or session.get('username') != username:
        print("User not logged in. Redirecting to auth_form.")
        return redirect(url_for('auth_form')) # Redirect to homepage if not logged in

     # Fetch user information from the database
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()

        if not user_data:
            return "User not found!"
        
        # Render the user page with user-specific data
        return render_template('user_page.html', username=user_data['username'], experience=user_data.get('experience', 50))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "An error occurred while retrieving user data."

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    # data = load_user_data()
    # user = data.get(username)
    # if user:
    #     return render_template('user_page.html', username=username, level=user['level'], experience=user['experience'])
    # return "User not found!"

# Update user experience and level
@app.route('/gain_experience/<username>/<int:amount>')
def gain_experience(username, amount):
    data = load_user_data()
    user = data.get(username)
    
    if user:
        user['experience'] += amount
        # Check if experience reaches or exceeds 100
        if user['experience'] >= 100:
            user['level'] += 1
            user['experience'] -= 100  # Carry over remaining experience if it exceeds 100
        
        save_user_data(data)
        return redirect(url_for('user_page', username=username))
    return "User not found!"

# Load recipes from JSON file
with open('allrecipe.json', 'r') as file:
    recipes = json.load(file)

# Function to find recipes by ingredient
import re

# Function to convert time to minutes for sorting
def convert_time_to_minutes(time_str):
    match = re.match(r"(\d+)\s*(minutes|hour)", time_str)
    if match:
        value, unit = match.groups()
        value = int(value)
        if unit == "hour":
            return value * 60  # Convert hours to minutes
        else:
            return value
    return 0  # Default if no match found

def find_recipes_by_ingredient(ingredient_name, recipes):
    result = []
    for recipe in recipes:
        # Check if the ingredient exists in the recipe's ingredient list
        if any(ingredient['Ingredient'].lower() == ingredient_name.lower() for ingredient in recipe['Ingredients']):
            result.append((recipe['Recipe Name'], recipe['Time'], recipe))  # Append recipe name, time, and recipe details

    if not result:
        return "Sorry, no recipe exists."
    
    # Sort the result by time (convert time to minutes)
    result.sort(key=lambda x: convert_time_to_minutes(x[1]))  # Sorting by the time (second element in tuple)
    
    return result

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        ingredient_name = request.form['ingredient_name']
        result = find_recipes_by_ingredient(ingredient_name, recipes)
        if isinstance(result, str):
            return render_template('search_result.html', message=result)
        else:
            return render_template('search_result.html', recipes=result)

@app.route('/recipe/<recipe_name>')
def recipe_details(recipe_name):
    for recipe in recipes:
        if recipe['Recipe Name'] == recipe_name:
            return render_template('recipe_details.html', recipe=recipe)
    return "Recipe not found!"

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user_post = {
                'username': request.form['username'],
                'image': os.path.join(app.config['UPLOAD_FOLDER'], filename),
                'recipe': request.form['recipe_name']
            }
            if os.path.exists('user_posts.json'):
                with open('user_posts.json', 'r') as file:
                    user_posts = json.load(file)
            else:
                user_posts = []
            user_posts.append(user_post)
            with open('user_posts.json', 'w') as file:
                json.dump(user_posts, file)
            return redirect(url_for('user_posts'))
    else:
        return render_template('upload.html')

@app.route('/user_posts')
def user_posts():
    if os.path.exists('user_posts.json'):
        with open('user_posts.json', 'r') as file:
            user_posts = json.load(file)
    else:
        user_posts = []
    return render_template('user_posts.html', user_posts=user_posts)

# @app.route('/user_page')
# def user_page():
#     user_data = {
#         'username': 'JohnDoe',  # Replace with dynamic data if needed
#         'level': 1,              # Replace with dynamic level
#         'experience': 30,         # Replace with dynamic experience percentage
#     }
#     return render_template('user_page.html', username=user_data['username'],
#                            level=user_data['level'], experience=user_data['experience'])

if __name__ == '__main__':
    app.run(debug=True)