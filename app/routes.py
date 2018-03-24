from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, RecipeForm, RecipeEditForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Recipe
from werkzeug.urls import url_parse

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
	
	selected_recipe = None
	
	if recipe_edit_form.submit_select_recipe.data:
		selected_recipe_id = recipe_edit_form.recipes.data
		selected_recipe = Recipe.query.get(selected_recipe_id)
	
	return render_template('edit_recipe.html',
						form=recipe_edit_form,
						recipe=selected_recipe)
	