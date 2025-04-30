from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
import time
import uvicorn

from backend.auth import router as auth_router
from backend.movies import router as movies_router

app = FastAPI(title="Fast API Movies App",
    docs_url="/movies-docs",
    version="0.0.1")

origins = ["http://localhost:3000",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(movies_router.router)
app.include_router(movies_router.playlist_router)

@app.get("/")  # Corrected line: added parentheses
async def root():
    return {"message": "Welcome to the FastAPI Movies App!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
