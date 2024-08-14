from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List, Dict

DATABASE_URL = "sqlite:///./recipe_meal_planner.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    ingredients = relationship("Ingredient", back_populates="recipe")

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(String)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = relationship("Recipe", back_populates="ingredients")

class MealPlan(Base):
    __tablename__ = "meal_plans"
    id = Column(Integer, primary_key=True, index=True)
    meal_date = Column(String, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = relationship("Recipe")

Base.metadata.create_all(bind=engine)

class IngredientCreate(BaseModel):
    name: str
    quantity: str

class RecipeCreate(BaseModel):
    name: str
    description: str
    ingredients: List[IngredientCreate]

class MealPlanCreate(BaseModel):
    meal_date: str
    recipe_id: int

class RecipeOut(BaseModel):
    id: int
    name: str
    description: str
    ingredients: List[IngredientCreate] = []

class IngredientOut(BaseModel):
    id: int
    name: str
    quantity: str

class MealPlanOut(BaseModel):
    id: int
    meal_date: str
    recipe: RecipeOut

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/recipes/", response_model=RecipeOut)
async def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = Recipe(name=recipe.name, description=recipe.description)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    for ingredient in recipe.ingredients:
        db_ingredient = Ingredient(name=ingredient.name, quantity=ingredient.quantity, recipe_id=db_recipe.id)
        db.add(db_ingredient)
    db.commit()
    return db_recipe

@app.get("/recipes/", response_model=List[RecipeOut])
async def list_recipes(db: Session = Depends(get_db)):
    return db.query(Recipe).all()

@app.post("/meal_plans/", response_model=MealPlanOut)
async def create_meal_plan(meal_plan: MealPlanCreate, db: Session = Depends(get_db)):
    db_meal_plan = MealPlan(meal_date=meal_plan.meal_date, recipe_id=meal_plan.recipe_id)
    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan

@app.get("/meal_plans/", response_model=List[MealPlanOut])
async def list_meal_plans(db: Session = Depends(get_db)):
    return db.query(MealPlan).all()

@app.get("/shopping_list/", response_model=Dict[str, str])
async def generate_shopping_list(db: Session = Depends(get_db)):
    ingredients = db.query(Ingredient.name, Ingredient.quantity).join(Recipe).join(MealPlan).all()
    shopping_list = {}
    for ingredient in ingredients:
        if ingredient.name in shopping_list:
            shopping_list[ingredient.name] += f", {ingredient.quantity}"
        else:
            shopping_list[ingredient.name] = ingredient.quantity
    return shopping_list