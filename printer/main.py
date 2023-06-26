from fastapi import FastAPI, UploadFile, Request
import os,base64,random

app= FastAPI()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"uploads")


@app.post("/upload")
async def upload_file(request: Request):
    test = await request.json()
    raw = test["raw"]
    file = base64.b64decode(raw)
    filename = random.randint(0,100)
    SAVE_FILE_PATH = os.path.join(UPLOAD_DIR,((str)(filename)+".pdf"))
    with open(SAVE_FILE_PATH, "wb") as f:
        f.write(file)    
    return(200)

@app.get("/text")
def upload_file(text):
    return (text)

@app.get("/healthcheck")    
def health_check():
    return {"Check":200}
        
