from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    a = 5
    a += 8
    
    return {"message": f"Hello World - {a}"}