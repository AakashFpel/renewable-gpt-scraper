from fastapi import FastAPI, Query
from regulatory_scraper import generate_summary

app = FastAPI()

@app.get("/get-latest-summary")
def get_latest_summary(api_key: str = Query(...)):
    summary = generate_summary(api_key)
    return {"summary": summary}