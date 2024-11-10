from flask import Flask, render_template, request, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = 'your_secret_key'  # For session management

USER_DATA_FILE = 'user_data.json'


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
    return redirect(url_for('user_page', username=username))

# Retrieve and display user information
@app.route('/user_page/<username>')
def user_page(username):
    data = load_user_data()
    user = data.get(username)
    if user:
        return render_template('user_page.html', username=username, level=user['level'], experience=user['experience'])
    return "User not found!"

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
def find_recipes_by_ingredient(ingredient_name, recipes):
    result = []
    for recipe in recipes:
        if any(ingredient['Ingredient'].lower() == ingredient_name.lower() for ingredient in recipe['Ingredients']):
            result.append((recipe['Recipe Name'], recipe['Time'], recipe))
    if not result:
        return "Sorry, no recipe exists."
    return result

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    # Load user posts from 'user_posts.json'
    if os.path.exists('user_posts.json'):
        with open('user_posts.json', 'r') as file:
            user_posts = json.load(file)
    else:
        user_posts = []
    
    return render_template('index.html', user_posts=user_posts)

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