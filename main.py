from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import requests
import time

app = FastAPI()

# API_KEY for authentication
API_KEY = 'somerandomkey'
api_key_header = APIKeyHeader(name="X-API-Key")
# cache for caching subsequent GET requests for 300 sec(5 minutes)
cache = {}
cache_expiration = 300


# Dependency method to verify if the provided API_KEY is valid or not
def verify_api_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")


# root url for FastAPI
@app.get("/")
async def root():
    return {"message": "Hello World"}


# GET method for fetching and caching product categories using Dependency Injection of FastAPI
@app.get("/product/categories", dependencies=[Depends(verify_api_key)])
async def get_product_categories():
    # Fetching the current time to calculate the expiry time after 5 minutes
    current_time = time.time()
    # Checking if the cache dict has some value. If it has stored values, then sending a response header as "Hit"
    if "categories" in cache and current_time < cache['categories_expiration']:
        return JSONResponse(content=cache["categories"], headers={"X-Cache": "Hit"})

    response = requests.get('https://fakestoreapi.com/products/categories')
    # On getting a successful response, storing the result in cache and setting the expiration time
    if response.status_code == 200:
        cache["categories"] = response.json()
        cache["categories_expiration"] = current_time + cache_expiration
        return JSONResponse(content=cache["categories"], headers={"X-Cache": "Miss"})
    else:
        return JSONResponse(status_code=response.status_code, content={"message": "Error fetching categories"})


# POST method to add an item(dictionary) into the products list
@app.post("/products", dependencies=[Depends(verify_api_key)])
async def add_product(product: dict):
    response = requests.post('https://fakestoreapi.com/products', json=product)
    data = response.json()
    return JSONResponse(status_code=response.status_code, content=data)
