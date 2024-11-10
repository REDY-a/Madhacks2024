from flask import Flask, render_template, request
import json

# Initialize Flask app
app = Flask(__name__)

# Load recipes data
with open('allrecipe.json', 'r') as file:
    recipes = json.load(file)

# Function to find recipes by ingredient and return both name and time
def find_recipes_by_ingredient(ingredient_name, recipes):
    result = []
    for recipe in recipes:
        # Check if the ingredient exists in the recipe's ingredient list
        if any(ingredient['Ingredient'].lower() == ingredient_name.lower() for ingredient in recipe['Ingredients']):
            result.append((recipe['Recipe Name'], recipe['Time'], recipe))  # Include recipe object for later access
    if not result:
        return "Sorry, no recipe exists."
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        ingredient_name = request.form['ingredient_name']
        result = find_recipes_by_ingredient(ingredient_name, recipes)
        if isinstance(result, str):  # No recipes found
            return render_template('search_results.html', message=result)
        else:
            return render_template('search_results.html', recipes=result)

@app.route('/recipe/<recipe_name>')
def recipe_details(recipe_name):
    # Find the recipe details by name
    for recipe in recipes:
        if recipe['Recipe Name'] == recipe_name:
            return render_template('recipe_details.html', recipe=recipe)
    return "Recipe not found!"

if __name__ == '__main__':
    app.run(debug=True)