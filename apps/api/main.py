from fastapi import FastAPI

app = FastAPI(title="SMART-MINE AI API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
