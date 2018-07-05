# MacroBro

A web app for collecting and easy editing for recipes with macronutrient information.

# Nutrient database information

All ingredients were taken from:

* U.S. Department of Agriculture, Agricultural Research Service. 20xx. USDA National Nutrient Database for Standard Reference, Release . Nutrient Data Laboratory Home Page, http://www.ars.usda.gov/nutrientdata
* U.S. Department of Agriculture, Agricultural Research Service. 20xx. USDA Branded Food Products Database . Nutrient Data Laboratory Home Page, http://ndb.nal.usda.gov

The file containing all the information was downloaded from the USDA website and is located at `ingredients/ABBREV.txt`. `populate_ingredients.py` was used to populate a database so as to avoid querying the USDA website directly.

# Acknowledgments

* [Miguel Grinberg] for writing a comprehensive tutorial for Flask. A lot of the source code is inspired by the structure of `microblog`.