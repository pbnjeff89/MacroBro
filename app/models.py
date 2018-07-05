from datetime import datetime
from time import time

from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt

from app import app


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    recipes = db.relationship('Recipe', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(selfself, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class IngredientToRecipe(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    ingredient_amt = db.Column(db.Float)
    recipe = db.relationship('Recipe', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipes')

    def get_protein_scaled(self):
        return round(self.ingredient.protein * self.ingredient_amt / 100, 2)

    def get_fat_scaled(self):
        return round(self.ingredient.fat * self.ingredient_amt / 100, 2)

    def get_carbohydrates_scaled(self):
        return round(self.ingredient.carbohydrates * self.ingredient_amt / 100, 2)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ingredients = db.relationship('IngredientToRecipe', back_populates='recipe')

    def get_macro_totals(self):
        protein_total = fat_total = carbohydrates_total = 0

        for ingredient in self.ingredients:
            scaling_factor = ingredient.ingredient_amt / 100.0
            the_ingredient = ingredient.ingredient
            protein_total += the_ingredient.protein * scaling_factor
            fat_total += the_ingredient.fat * scaling_factor
            carbohydrates_total += the_ingredient.carbohydrates * scaling_factor

        return round(protein_total, 2), round(fat_total, 2), round(carbohydrates_total, 2)

    def __repr__(self):
        return '<Recipe {}>'.format(self.body)


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(140), index=True)
    protein = db.Column(db.Float, index=True)
    fat = db.Column(db.Float, index=True)
    saturated_fat = db.Column(db.Float, index=True)
    monounsaturated_fat = db.Column(db.Float, index=True)
    polyunsaturated_fat = db.Column(db.Float, index=True)
    cholesterol = db.Column(db.Float, index=True)
    carbohydrates = db.Column(db.Float, index=True)
    fiber = db.Column(db.Float, index=True)
    sugar = db.Column(db.Float, index=True)
    recipes = db.relationship('IngredientToRecipe', back_populates='ingredient')

    def __repr__(self):
        return '<Ingredient {}>'.format(self.description)


@login.user_loader
def load_user(_id):
    return User.query.get(int(_id))
