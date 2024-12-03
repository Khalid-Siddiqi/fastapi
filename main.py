from fastapi import status
from fastapi import FastAPI, File, UploadFile, HTTPException
from decouple import config
from pydantic import BaseModel
from supabase import create_client, Client
from datetime import datetime
import uuid

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
# POST / Insert Data
class PatientImageData(BaseModel):
    Patient_ID: int
    Category: int
    
@app.post("/image/")
async def upload_image(data: PatientImageData, file: UploadFile = File(...)):
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, detail="Unsupported file type. Only JPG and PNG are allowed."
            )

        # Get today's date as an integer (e.g., YYYYMMDD format)
        today_date = int(datetime.now().strftime("%Y%m%d"))

        # Generate a unique file name
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Upload the file to Supabase storage
        bucket_name = "DFU_image"
        response_storage = supabase.storage.from_(bucket_name).upload(unique_filename, file.file)

        if not response_storage:
            raise HTTPException(status_code=500, detail="Failed to upload the image to storage")

        # Get the public URL of the uploaded file
        public_url = supabase.storage.from_(bucket_name).get_public_url(unique_filename)

        # Count how many images have been uploaded today by this patient
        response_count = (
            supabase.table("Patient_Image_Data")
            .select("*")
            .eq("Patient_ID", data.Patient_ID)
            .eq("Date", today_date)
            .execute()
        )
        daily_image_count = len(response_count.data) + 1

        # Insert new record into the database
        response_insert = supabase.table("Patient_Image_Data").insert({
            "Patient_ID": data.Patient_ID,
            "Image": public_url,
            "Category": data.Category,
            "Date": today_date,
            "Image_of_day": daily_image_count
        }).execute()

        if not response_insert.data:
            raise HTTPException(status_code=400, detail="Error uploading image data")

        return {
            "message": "Image uploaded successfully",
            "daily_image_count": daily_image_count,
            "image_url": public_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Get / Retrieve Data
class QueryImageData(BaseModel):
        Patient_ID: int
        Date: int
        Image_of_day: int    

@app.get("/image")
async def get_image(patient_id: int, date: int, image_of_day: int):
    try:
        # Query the database for the specific record
        response = supabase.table("Patient_Image_Data").select("*") \
            .eq("Patient_ID", patient_id) \
            .eq("Date", date) \
            .eq("Image_of_day", image_of_day).execute()

        # Check if the record exists
        if not response.data:
            raise HTTPException(status_code=404, detail="No image found for the given criteria")

        # Return the image data
        return {
            "message": "Image retrieved successfully",
            "data": response.data[0]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
