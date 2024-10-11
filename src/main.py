import uvicorn
from config import app
from auth.router import auth_router as user_router


@app.get("/")
def read_root():
    return {"message": "Hello World"}


# router Setting
app.include_router(user_router, prefix="/user", tags=["user"])

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)