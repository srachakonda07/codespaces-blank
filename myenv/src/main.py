from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import hashlib

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Pydantic model for the item
class Item(BaseModel):
    name: str  # Name of the item
    price: float  # Price of the item
    quantity: int  # Quantity of the item


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/json/")
async def create_json_item(item: Item):
    text = item.name
    checksum = hashlib.md5(text.encode()).hexdigest()
    # Process the JSON data here
    
    # Get the participant's name from the item
    participant_name = item.name
    print(participant_name)
    
    # Create a customized welcome message
    welcome_message = f"Welcome, {participant_name}!"
    
    return {"message": f"JSON item created successfully with text: {text}", "checksum": checksum, "welcome_message": welcome_message}
