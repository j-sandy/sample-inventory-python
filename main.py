from fastapi import FastAPI, HTTPException, Depends, status
from fastapi import FastAPI, HTTPException, Depends, status, Header # Import Header
from typing import Dict, List, Optional
from datetime import date
import uuid
from models import User, LoginRequest, LoginResponse, Item # Import models from models.py

app = FastAPI()

# In-memory database
items_db: Dict[str, Item] = {}
sessions_db: Dict[str, str] = {} # session_token: username

# Hardcoded user for authentication
VALID_USERNAME = "admin"
VALID_PASSWORD = "password"

# Dependency to get current user
def get_current_user(session_token: str = Header(alias="session_token")) -> str: # Explicitly define header name
    if session_token not in sessions_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return sessions_db[session_token]

# API Endpoints

# 1. Authenticate and start session
@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    if request.username == VALID_USERNAME and request.password == VALID_PASSWORD:
        session_token = str(uuid.uuid4())
        sessions_db[session_token] = request.username
        return {"session_token": session_token}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

# 2. Logout and end session
@app.post("/logout")
async def logout(session_token: str = Depends(get_current_user)):
    # get_current_user already validates the token, so we just need to remove it
    for token, username in list(sessions_db.items()):
        if username == session_token: # session_token here is actually the username returned by get_current_user
            del sessions_db[token]
            return {"message": "Logged out successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Session not found or already logged out",
    )

# 3. Add details of item
@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def add_item(item: Item, current_user: str = Depends(get_current_user)):
    if item.item_code in items_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item with this item_code already exists")
    items_db[item.item_code] = item
    return item

# 4. Update the item details
@app.put("/items/{item_code}", response_model=Item)
async def update_item(item_code: str, updated_item: Item, current_user: str = Depends(get_current_user)):
    if item_code not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Ensure the item_code in the path matches the item_code in the request body
    if item_code != updated_item.item_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item code in path and body must match")

    items_db[item_code] = updated_item
    return updated_item

# 5. Delete the item and its details
@app.delete("/items/{item_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_code: str, current_user: str = Depends(get_current_user)):
    if item_code not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    del items_db[item_code]
    return

# 6. Fetch the item details based on item-code, procurement date, expiry date and name.
@app.get("/items/{item_code}", response_model=Item)
async def get_item_by_code(item_code: str, current_user: str = Depends(get_current_user)):
    if item_code not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return items_db[item_code]

@app.get("/items/search/", response_model=List[Item])
async def search_items(
    name: Optional[str] = None,
    procurement_date: Optional[date] = None,
    expiry_date: Optional[date] = None,
    current_user: str = Depends(get_current_user)
):
    results = []
    for item in items_db.values():
        match = True
        if name and name.lower() not in item.name.lower():
            match = False
        if procurement_date and item.procurement_date != procurement_date:
            match = False
        if expiry_date and item.expiry_date != expiry_date:
            match = False
        
        if match:
            results.append(item)
    return results
