from app import db
from app.models import Ingredient
import pandas as pd

columns = ['NDB_No.','Shrt_Desc','Water','Energ_Kcal','Protein','Lipid_Tot','Ash',
            'Carbohydrt','Fiber_TD','Sugar_Tot','Calcium','Iron','Magnesium','Phosphorus',
            'Potassium','Sodium','Zinc','Copper','Manganese','Selenium','Vit_C','Thiamin',
            'Riboflavin','Niacin','Panto_acid','Vit_B6','Folate_Tot','Folic_acid','Food_Folate',
            'Folate_DFE','Choline_Tot','Vit_B12','Vit_A_IU','Vit_A_RAE','Retinol','Alpha_Carot',
            'Beta_Carot','Beta_Crypt','Lycopene','Lut_and_Zea','Vit_E','Vit_D_mcg','Vit_D_IU','Vit_K',
            'FA_Sat','FA_Mono','FA_Poly','Cholestrl','GmWt_1','GmWt_Desc1','GmWt_2','GmWt_Desc2',
            'Refuse_Pct']
			
nutritional_info = pd.read_csv('ingredients/ABBREV.txt', sep='^', encoding='latin1', header=None)
nutritional_info.columns = columns

drop_columns = ['NDB_No.','Water','Energ_Kcal','Ash',
            'Calcium','Iron','Magnesium','Phosphorus',
            'Potassium','Sodium','Zinc','Copper','Manganese','Selenium','Vit_C','Thiamin',
            'Riboflavin','Niacin','Panto_acid','Vit_B6','Folate_Tot','Folic_acid','Food_Folate',
            'Folate_DFE','Choline_Tot','Vit_B12','Vit_A_IU','Vit_A_RAE','Retinol','Alpha_Carot',
            'Beta_Carot','Beta_Crypt','Lycopene','Lut_and_Zea','Vit_E','Vit_D_mcg','Vit_D_IU','Vit_K',
            'GmWt_1','GmWt_Desc1','GmWt_2','GmWt_Desc2',
            'Refuse_Pct']

nutritional_info = nutritional_info.drop(drop_columns, axis=1)
nutritional_info = nutritional_info[['Shrt_Desc','Protein','Lipid_Tot','FA_Sat','FA_Mono','FA_Poly','Cholestrl','Carbohydrt','Fiber_TD','Sugar_Tot']]

for field in nutritional_info.columns:
    if nutritional_info[field].dtype == object:
        nutritional_info[field] = nutritional_info[field].str.strip('~')

# renaming
nutritional_info.columns = ['description','protein','fat','saturated_fat','monounsaturated_fat','polyunsaturated_fat',
								'cholesterol','carbohydrates','fiber','sugar']

nutritional_info.to_sql(name='ingredient', con=db.engine, if_exists='append', index=False)
