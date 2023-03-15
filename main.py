from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
import pikepdf
from starlette.responses import RedirectResponse
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request):
    form = await request.form()
    pdf = form["pdf"].file
    filename = str(uuid.uuid4()) + ".pdf"
    with open("uploads/" + filename, "wb") as f:
        f.write(pdf.read())
    with pikepdf.open("uploads/" + filename) as pdf:
        pdf.save("success/" + filename)
    os.remove("uploads/" + filename)
    # return {"filename": filename}
    return RedirectResponse(url=f"/success/{filename}")


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = "success/" + filename
    return FileResponse(file_path, filename=filename)


@app.post("/success/{filename}", response_class=HTMLResponse)
async def success(request: Request, filename: str):
    return templates.TemplateResponse("success.html", {"request": request, "filename": filename})


@app.get("/clear",response_class=HTMLResponse)
async def clear(request: Request):
    for file_name in os.listdir("uploads"):
        os.remove("uploads/" + file_name)
    for file_name in os.listdir("success"):
        os.remove("success/" + file_name)
    return templates.TemplateResponse("success_clear.html", {"request": request})

if __name__ == '__main__':

    uvicorn.run(app, host="127.0.0.1", port=9222)