from fastapi import FastAPI

app = FastAPI(title="File Handler")


@app.get("/")
def read_root():
    return {"hello": "world"}