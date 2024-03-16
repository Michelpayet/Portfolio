from flask import Flask, render_template, redirect, request, session, jsonify, flash
import requests
import sqlite3
from urllib.parse import unquote
from helpers import login_required, apology, get_username_from_db
from werkzeug.security import check_password_hash, generate_password_hash

# Create the flask app
app = Flask(__name__)

# Replace with your Spoonacular API key
API_KEY = '######################'

# App secret_key
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Define the route for the "Home" button
@app.route('/what_to_cook', methods=['GET'])
@login_required
def home():
    user_name = get_username_from_db(session["user_id"])

    # Render the main page with empty recipe list and search query
    return render_template('index.html', recipes=[], search_query='', user_name=user_name)

# Define the main route for the app
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_name = get_username_from_db(session["user_id"])

    if request.method == 'POST':
        # If a form is submitted
        query = request.form.get('search_query', '')
        # Perform a search for recipes with the given query
        recipes = search_recipes(query)
        # Render the main page with the search results and the search query
        return render_template('index.html', recipes=recipes, search_query=query, user_name=user_name)
    
    # If it's a GET request or no form submitted
    search_query = request.args.get('search_query', '')
    decoded_search_query = unquote(search_query)
    # Perform a search for recipes with the decoded search query
    recipes = search_recipes(decoded_search_query)
    # Render the main page
    return render_template('index.html', recipes=recipes, search_query=decoded_search_query, user_name=user_name)

# Saving a recipe
@app.route('/save_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def save_recipe(recipe_id):
        # Get the user ID from the session
        user_id = session.get("user_id")

        # Check if the recipe is already saved by the user
        conn = sqlite3.connect('users.db')
        db = conn.cursor()
        db.execute("SELECT * FROM saved_meal WHERE user_id = ? AND meal_id = ?", (user_id, recipe_id))
        existing_recipe = db.fetchone()
        conn.close()

        if existing_recipe:
            # If the recipe already exists, redirect without saving again
            flash("Recipe already saved")
            return redirect('/')

        response = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}')
        if response.status_code == 200:
            recipe_data = response.json()
            # Save recipe to SQLite database
            conn = sqlite3.connect('users.db')
            db = conn.cursor()
            db.execute("INSERT INTO saved_meal (user_id, meal_id) VALUES (?, ?)", (user_id, recipe_id))
            conn.commit()
            conn.close()

        # Redirect the user to the homepage or any other appropriate page
        return redirect('/profile')

# Remove saved recipe from profile
@app.route('/delete_saved_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def delete_saved_recipe(recipe_id):
    # Get the user ID from the session
    user_id = session.get("user_id")

    # Check if the recipe exists in the saved_meal table
    conn = sqlite3.connect('users.db')
    db = conn.cursor()
    db.execute("SELECT * FROM saved_meal WHERE user_id = ? AND meal_id = ?", (user_id, recipe_id))
    existing_recipe = db.fetchone()

    if existing_recipe:
        # If the recipe exists, delete it from the database
        db.execute("DELETE FROM saved_meal WHERE user_id = ? AND meal_id = ?", (user_id, recipe_id))
        conn.commit()
        conn.close()
        flash("Recipe deleted successfully")
    else:
        flash("Recipe not found in your saved recipes")

    # Redirect the user to the profile page or any other appropriate page
    return redirect('/profile')

# Function to search for recipes based on the provided query
def search_recipes(query):
    url = f'https://api.spoonacular.com/recipes/complexSearch'
    params = {
        'apiKey': API_KEY,
        'query': query,
        'number': 10,
        'instructionsRequired': True,
        'addRecipeInformation': True,
        'fillIngredients': True,
    }

    # Send a GET request to the Spoonacular API with the query parameters
    response = requests.get(url, params=params)
    # If the API call is successful
    if response.status_code == 200:
        # Parse the API response as JSON data
        data = response.json()
        # Return the list of recipe results
        return data['results']
    # If the API call is not successful
    return []

# Route to view a specific recipe with a given recipe ID
@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):

    # Get the search query from the URL query parameters
    search_query = request.args.get('search_query', '')
    # Get the referer URL to check if it's from profile page
    referer_url = request.referrer
    from_profile = False
    if referer_url.endswith('/profile'):
        from_profile = True

    # Query database for the user_name of the active user
    user_name = get_username_from_db(session["user_id"])

    # Get the search query from the URL query parameters
    search_query = request.args.get('search_query', '')
    # Build the URL to get information about the specific recipe ID from Spoonacular API
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {
        'apiKey': API_KEY,
    }

    # Send a GET request to the Spoonacular API to get the recipe information
    response = requests.get(url, params=params)
    # If the API call is successful
    if response.status_code == 200:
        recipe = response.json()
        return render_template('view_recipe.html', recipe=recipe, search_query=search_query, from_profile=from_profile, user_name=user_name)
    return "Recipe not found", 404

@app.route('/profile')
@login_required
def profile():

    user_name = get_username_from_db(session["user_id"])

    # Get the user ID from the session
    user_id = session.get("user_id")

    # Initialize the database connection
    conn = get_db_connection()
    db = conn.cursor()

    # Fetch saved recipes for the current user
    db.execute("SELECT meal_id FROM saved_meal WHERE user_id = ?", (user_id,))
    saved_recipes = db.fetchall()

    saved_recipe_data = []
    # Loop through saved recipes and fetch recipe information from API
    for saved_recipe in saved_recipes:
        recipe_id = saved_recipe["meal_id"]
        response = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}')
        if response.status_code == 200:
            recipe_data = response.json()
            saved_recipe_data.append(recipe_data)
        else:
            print(f"Failed to fetch recipe with ID {recipe_id}")

    print("Saved Recipes:", saved_recipe_data)  # Debugging statement

    return render_template("profile.html", user_name=user_name, saved_recipes=saved_recipe_data)

@app.route('/about')
def about():
    user_name = None

    if "user_id" in session:
        conn = get_db_connection()
        db = conn.cursor()

        # Query database for the user_name of the active user
        db.execute("SELECT user_name FROM users WHERE id = ?", (session["user_id"],))
        user = db.fetchone()

        user_name = user["user_name"] if user else None

    return render_template("about.html", user_name=user_name)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Login user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        conn = get_db_connection()
        db = conn.cursor()

        # Query database for username
        db.execute("SELECT * FROM users WHERE user_name = ?", (request.form.get("username"),))
        rows = db.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Fetch saved recipes for the logged-in user
        db.execute("SELECT meal_id FROM saved_meal WHERE user_id = ?", (session["user_id"],))
        saved_recipes = db.fetchall()

        saved_recipe_data = []
        # Loop through saved recipes and fetch recipe information from API
        for saved_recipe in saved_recipes:
            recipe_id = saved_recipe["meal_id"]
            response = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}')
            if response.status_code == 200:
                recipe_data = response.json()
                saved_recipe_data.append(recipe_data)
            else:
                print(f"Failed to fetch recipe with ID {recipe_id}")

        # Query database for the user_name of the active user
        user_name = get_username_from_db(session["user_id"])

        return render_template("profile.html", user_name=user_name, saved_recipes=saved_recipe_data)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Forget user"""
    session.clear()

    return redirect("/login")


@app.route("/join", methods=["GET", "POST"])
def join():
    """Register user"""
    # forget user id
    session.clear()
    

    if request.method == "POST":

        # Add the user's entry into the database
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if fields are not empty
        if not username or not password or not confirmation:
            return apology("Please fill in all the fields")

        # Check if password matches the confirmation
        if password != confirmation:
            return apology("Password does not match")
        
        conn = get_db_connection()
        db = conn.cursor()

        hashed = generate_password_hash(password)

        # The username field is already UNIQUE so we can do this:
        try:
            new_user = db.execute("INSERT INTO users (user_name, hash) VALUES(?, ?)", (username, hashed))
            conn.commit()
            db.close()
        except:
            db.close()
            return apology("Username already exist. Please choose a different one")
            


        # Get the ID of the newly inserted user
        new_user= db.lastrowid

        # remember logged in user
        session["user_id"] = new_user

        # redirect to homepage
        return redirect("/login")

    # If user reached via GET
    else:
        return render_template("join.html")

# Route to delete user and associated data
@app.route('/delete_user', methods=['POST', 'GET'])
@login_required
def delete_user():
    if request.method == 'GET':
        # If the request method is GET, render a confirmation page
        return render_template('confirm_delete.html')
    elif request.method == 'POST':
        # If the request method is POST (from the confirmation page)
        # Proceed with the deletion process
        if request.form.get('confirm_delete') == 'yes':
            user_id = session.get("user_id")

            # Connect to the database
            conn = get_db_connection()
            db = conn.cursor()

            # Delete user's saved recipes
            db.execute("DELETE FROM saved_meal WHERE user_id = ?", (user_id,))
            conn.commit()

            # Delete user from users table
            db.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()

            # Close database connection
            conn.close()

            # Clear session
            session.clear()

            flash("Your account has been deleted successfully")
            return redirect('/')
        else:
            # If the user didn't confirm deletion, redirect back to the homepage
            return redirect('/')

# Run the app in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)