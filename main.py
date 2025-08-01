from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.auth import router as auth_router
from backend.tickets import router as tickets_router

app = FastAPI(title="Fast API Ticket Master App",
    docs_url="/docs",
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
app.include_router(tickets_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Ticket Master App!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
