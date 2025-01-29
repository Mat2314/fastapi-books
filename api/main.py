from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    a = 5
    a += 8
    print("Comment CI tests")
    
    return {"message": f"Hello World"}