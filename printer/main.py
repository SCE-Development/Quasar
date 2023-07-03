import base64
import random
import os
import enum

from fastapi import FastAPI, UploadFile, Request, HTTPException

app= FastAPI()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"uploads")

class returnValues(enum.Enum):
    Error_400 = ("error_400",HTTPException(status_code=400, detail="No data passed"))
    Success_200 = ("success_200",200)

    def __init__(self, name, status):
        self.name = name
        self.status = status
     
@app.post("/upload")
async def upload_file(request: Request):
    data = await request.json()
    if "raw" not in data:
        raise returnValues.Error_400.status
    rawData = data["raw"]
    file = base64.b64decode(rawData)
    filename = random.randint(0,100)
    SAVE_FILE_PATH = os.path.join(UPLOAD_DIR,((str)(filename)+".pdf"))
    with open(SAVE_FILE_PATH, "wb") as f:
        f.write(file)    
    return(returnValues.Success_200.status)

@app.get("/healthcheck")    
def health_check():
    return {"Check":200}
        
