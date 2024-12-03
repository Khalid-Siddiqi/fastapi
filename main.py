from fastapi import FastAPI
from decouple config
app = FastAPI()

@app.get("/image")
async def test():
    return{"msg":"Hello World"}