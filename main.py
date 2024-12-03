from fastapi import FastAPI,status, HTTPException
from decouple import config
from pydantic import BaseModel
from supabase import create_client, Client
from datetime import datetime
url = config("SUPERBASE_URL")
key = config("SUPERBASE_KEY")

class PatientBioData(BaseModel):
    Patient_ID: int
    First_Name: str
    Last_name: str
    Email: str
    Phone_No: int
    CNIC: int

app = FastAPI()
supabase: Client = create_client(url,key)

#Bio Data

@app.get("/bio")
async def get_image():
    image = supabase.table("Bio_Data").select("*").execute()
    return image

@app.get("/bio/{id}")
async def get_image(id:int):
    image = supabase.table("Bio_Data").select("*").eq("Patient_ID",id).execute()
    return image

@app.post("/bio/", status_code=status.HTTP_201_CREATED)
async def post_image(data: PatientBioData):
    try:
        response = supabase.table("Bio_Data").insert({
            "Patient_ID": data.Patient_ID,
            "Full_Name": data.First_Name,
            "Last_name": data.Last_name,
            "Email": data.Email,
            "Phone_No": data.Phone_No,
            "CNIC": data.CNIC
        }).execute()
        
        # Check if insertion was unsuccessful
        if not response.data:
            raise HTTPException(status_code=400, detail="Error inserting data: " + str(response))
        
        return {"message": "Data inserted successfully", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Image Data
class PatientImageData(BaseModel):
    Patient_ID: int
    Image: str  # Base64-encoded image
    Category: int

@app.post("/image/")
async def upload_image(data: PatientImageData):
    try:
        # Get today's date as an integer (e.g., YYYYMMDD format)
        today_date = int(datetime.now().strftime("%Y%m%d"))

        # Count how many images have been uploaded today by this patient
        response_count = supabase.table("Patient_Image_Data").select("*").eq("Patient_ID", data.Patient_ID).eq("Date", today_date).execute()
        daily_image_count = len(response_count.data) + 1

        # Insert new record into the database
        response_insert = supabase.table("Patient_Image_Data").insert({
            "Patient_ID": data.Patient_ID,
            "Image": data.Image,
            "Category": data.Category,
            "Date": today_date,
            "Image_of_day": daily_image_count
        }).execute()

        if not response_insert.data:
            raise HTTPException(status_code=400, detail="Error uploading image data")

        return {
            "message": "Image uploaded successfully",
            "daily_image_count": daily_image_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))