from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

class Ingredient(BaseModel):
    name: str
    quantity: str

class Recipe(BaseModel):
    id: int
    title: str
    description: str
    ingredients: List[Ingredient]
    category: str

class Category(BaseModel):
    name: str
    description: Optional[str] = None

recipes: Dict[int, Recipe] = {}
categories: List[Category] = []

recipes[1] = Recipe(id=1, title="Spaghetti Carbonara", description="Classic Italian pasta dish",
                    ingredients=[Ingredient(name="Spaghetti", quantity="200g"),
                                 Ingredient(name="Pancetta", quantity="100g"),
                                 Ingredient(name="Eggs", quantity="2"),
                                 Ingredient(name="Parmesan Cheese", quantity="50g"),
                                 Ingredient(name="Pepper", quantity="to taste")],
                    category="Italian")
categories.append(Category(name="Italian", description="Italian cuisine"))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Recipe Management API"}

@app.post("/recipes/", response_model=Recipe)
def create_recipe(recipe: Recipe):
    if recipe.id in recipes:
        raise HTTPException(status_code=400, detail="Recipe with this ID already exists")
    recipes[recipe.id] = recipe
    return recipe

@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    if recipe_id in recipes:
        return recipes[recipe_id]
    else:
        raise HTTPException(status_code=404, detail="Recipe not found")

@app.get("/recipes/", response_model=List[Recipe])
def list_recipes():
    return list(recipes.values())

@app.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, updated_recipe: Recipe):
    if recipe_id in recipes:
        recipes[recipe_id] = updated_recipe
        return updated_recipe
    else:
        raise HTTPException(status_code=404, detail="Recipe not found")

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    if recipe_id in recipes:
        del recipes[recipe_id]
        return {"message": "Recipe deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Recipe not found")

@app.get("/recipes/category/{category}", response_model=List[Recipe])
def get_recipes_by_category(category: str):
    result = [recipe for recipe in recipes.values() if recipe.category.lower() == category.lower()]
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="No recipes found in this category")

@app.get("/recipes/search/", response_model=List[Recipe])
def search_recipes(ingredient: str):
    result = []
    for recipe in recipes.values():
        if any(ing.name.lower() == ingredient.lower() for ing in recipe.ingredients):
            result.append(recipe)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="No recipes found with this ingredient")

@app.post("/categories/", response_model=Category)
def create_category(category: Category):
    for cat in categories:
        if cat.name.lower() == category.name.lower():
            raise HTTPException(status_code=400, detail="Category already exists")
    categories.append(category)
    return category

@app.get("/categories/", response_model=List[Category])
def list_categories():
    return categories
