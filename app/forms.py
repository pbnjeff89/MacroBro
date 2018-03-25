from math import isnan
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
from app.models import User

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')
	
	
class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password',
					validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')
	
	
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')
	
	
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')
			
			
class RecipeForm(FlaskForm):
	name = StringField('Recipe Name', validators=[DataRequired(),Length(max=40)])
	submit = SubmitField('Create new recipe')
	
	
class RecipeEditForm(FlaskForm):
	recipes = SelectField('Recipes', choices=[], coerce=int, validators=[Optional()])
	submit_select_recipe = SubmitField('Select Recipe')
	submit_delete_recipe = SubmitField('Delete Recipe')
	
	
class IngredientEditForm(FlaskForm):
	ingredients = SelectField('Ingredients', coerce=int, choices=[])
	new_amount = DecimalField('New amount, in grams', validators=[DataRequired()])
	submit_change_amount = SubmitField('Change amount')
	submit_add_ingredient = SubmitField('Add an ingredient')
	submit_delete_ingredient = SubmitField('Delete this ingredient')
	
	
	def validate_new_amount(self, new_amount):
		if new_amount.data <= 0.0:
			raise ValidationError('Only positive numbers!')
			
			
class IngredientSearchForm(FlaskForm):
	search_query = StringField('I\'m looking for...', validators=[DataRequired()])
	submit_search = SubmitField('Search for this!')

	
class IngredientSearchResultsForm(FlaskForm):
	possible_ingredients = SelectField('Query results', coerce=int, choices=[], validators=[DataRequired()])
	submit_choose = SubmitField('Choose this ingredient')
	
	
class AddIngredientForm(FlaskForm):
	ingredient_amt = DecimalField('Amount, in grams', validators=[DataRequired()])
	submit_add_ingredient = SubmitField('Add this ingredient')

	
	def validate_ingredient_amt(self, new_amount):
		if new_amount.data <= 0.0:
			raise ValidationError('Only positive numbers!')