from fastapi import FastAPI
from decouple import config
from supabase import create_client, Client

url = config("SUPERBASE_URL")
key = config("SUPERBASE_KEY")


app = FastAPI()
supabase: Client = create_client(url,key)

@app.get("/image")
async def get_image():
    image = supabase.table("Patient_image_data")
    return{"msg":"Hello World"}