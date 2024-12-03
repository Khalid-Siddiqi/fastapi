from fastapi import FastAPI,status
from decouple import config
from supabase import create_client, Client

url = config("SUPERBASE_URL")
key = config("SUPERBASE_KEY")


app = FastAPI()
supabase: Client = create_client(url,key)

@app.get("/image")
async def get_image():
    image = supabase.table("Patient_Bio_Data").select("*").execute()
    return image

@app.get("/image/{id}")
async def get_image(id:int):
    image = supabase.table("Patient_Bio_Data").select("*").eq("Patient_ID",id).execute()
    return image
@app.post("/image/", status_code=status.HTTP_201_CREATED)
async def post_image():
    image = supabase.table("Patient_Bio_Data").insert()