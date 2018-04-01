from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, RecipeForm, RecipeEditForm, IngredientEditForm, IngredientSearchForm, IngredientSearchResultsForm, AddIngredientForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Recipe, Ingredient, IngredientToRecipe
from werkzeug.urls import url_parse
from difflib import get_close_matches

@app.route('/')
@app.route('/index')
@login_required
def index():
	recipes = [
				{
					'author': {'username':'Jeff'},
					'body': 'Just killed some chicken breasts and rice gonna get SWOLE.'
				},
				{
					'author': {'username':'Jeff'},
					'body': 'Check out this sick recipe for chicken creatine!'
				}
			]
	return render_template('index.html',
							recipes=recipes)

							
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html',
							form=form)
							
							
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
	
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Thanks for registering bro!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)
	
	
@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user.html', user=user, recipes=user.recipes)
	

@app.route('/new_recipe', methods=['GET','POST'])
@login_required
def new_recipe():
	recipe_form = RecipeForm()
	if recipe_form.validate_on_submit():
		user = current_user
		recipe = Recipe(body=recipe_form.name.data,
						user_id=user.id)
		db.session.add(recipe)
		db.session.commit()
		flash('New recipe added!')
		return redirect(url_for('index'))
	return render_template('new_recipe.html',
						recipe_form=recipe_form)
						
@app.route('/edit_recipe', methods=['GET','POST'])
@login_required
def edit_recipe():
	user = current_user
	recipes = user.recipes
	recipe_choices = [(recipe.id,recipe.body) for recipe in recipes]
	recipe_edit_form = RecipeEditForm()
	recipe_edit_form.recipes.choices = recipe_choices
	
	if recipe_edit_form.validate_on_submit():
		recipe_id = recipe_edit_form.recipes.data
		if recipe_edit_form.submit_select_recipe.data:
			return redirect(url_for('edit_recipe_ingredients',
											recipe_id=recipe_id))
		if recipe_edit_form.submit_delete_recipe.data:
			selected_recipe = Recipe.query.get(recipe_id)
			
			for ingredient_assoc in selected_recipe.ingredients:
				db.session.delete(ingredient_assoc)

			db.session.delete(selected_recipe)
			db.session.commit()

			return redirect(url_for('edit_recipe'))

	return render_template('edit_recipe.html',
						form=recipe_edit_form)
						
@app.route('/edit_recipe_ingredients/<recipe_id>', methods=['GET','POST'])
@login_required
def edit_recipe_ingredients(recipe_id):
	recipe = Recipe.query.get(recipe_id)
	
	if current_user.id is not recipe.user_id:
		flash('You are not allowed to change this recipe!!!')
		return redirect(url_for('index'))
		
	
	ingredient_edit_form = IngredientEditForm()
	ingredient_edit_form.ingredients.choices = [(ingredient.ingredient.id, ingredient.ingredient.description) for ingredient in recipe.ingredients]
	
	ingredient_id = ingredient_edit_form.ingredients.data
	
	if ingredient_edit_form.submit_change_amount.data:
		if ingredient_edit_form.validate_on_submit():
			ingredient_to_change = Ingredient.query.get(ingredient_id)
			ingredient_recipe_assoc = IngredientToRecipe.query. \
						filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id). \
						first_or_404()
			ingredient_recipe_assoc.ingredient_amt = float(ingredient_edit_form.new_amount.data)
			db.session.commit()
	
	if ingredient_edit_form.submit_add_ingredient.data:
		return redirect(url_for('add_ingredient', recipe_id=recipe_id))

	if ingredient_edit_form.submit_delete_ingredient.data:
		ingredient_id = ingredient_edit_form.ingredients.data
		ingredient_to_delete = Ingredient.query.get(ingredient_id)
		recipe_ingredient_assoc = IngredientToRecipe.query.filter_by(recipe_id=recipe_id, ingredient_id=ingredient_id).first_or_404()
		db.session.delete(recipe_ingredient_assoc)
		db.session.commit()
		return redirect(url_for('edit_recipe_ingredients', recipe_id=recipe_id))
			
	return render_template('edit_recipe_ingredients.html',
							edit_ingredient_form=ingredient_edit_form,
							recipe=recipe)
							
							
@app.route('/add_ingredient/<recipe_id>', methods=['GET','POST'])
@login_required
def add_ingredient(recipe_id):
	search_form = IngredientSearchForm()
	
	if search_form.validate_on_submit():
		query = search_form.search_query.data
		return redirect(url_for('query_results', recipe_id=recipe_id, query=query))

	return render_template('add_ingredient.html', search_form=search_form)
											

@app.route('/query_results', methods=['GET','POST'])
@login_required
def query_results():
	results_form = IngredientSearchResultsForm()
	
	query = str(request.args["query"])
	recipe_id = int(request.args["recipe_id"])
	
	ingredient_dict = {ingredient.description: ingredient.id for ingredient in Ingredient.query.all()}
	ingredient_names = list(ingredient_dict.keys())
	best_matches = get_close_matches(word=query.upper(), possibilities=ingredient_names,
												n=30, cutoff=0.2)
	ingredient_choices = [(ingredient_dict[best_match], best_match)for best_match in best_matches]
	results_form.possible_ingredients.choices = ingredient_choices
	
	if results_form.validate_on_submit():
		if results_form.possible_ingredients.data:
			return redirect(url_for('add_ingredient_to_recipe', recipe_id=recipe_id, ingredient_id=results_form.possible_ingredients.data))
		else:
			print('nope')
	
	return render_template('query_results.html', results_form=results_form)
	
	
@app.route('/add_ingredient_to_recipe', methods=['GET','POST'])
@login_required
def add_ingredient_to_recipe():
	recipe_id = int(request.args["recipe_id"])
	ingredient_id = int(request.args["ingredient_id"])
	add_ingredient_form = AddIngredientForm()
	
	ingredient = Ingredient.query.get(ingredient_id)
	
	if add_ingredient_form.validate_on_submit():
		recipe = Recipe.query.get(recipe_id)
		ingredient_recipe_assoc = IngredientToRecipe(ingredient_amt=float(add_ingredient_form.ingredient_amt.data))
		ingredient_recipe_assoc.recipe_id = recipe_id
		ingredient_recipe_assoc.ingredient_id = ingredient_id
		db.session.add(ingredient_recipe_assoc)
		db.session.commit()
		return redirect(url_for('edit_recipe'))
		
	
	return render_template('add_ingredient_to_recipe.html',
								add_ingredient_form=add_ingredient_form,
								ingredient=ingredient)