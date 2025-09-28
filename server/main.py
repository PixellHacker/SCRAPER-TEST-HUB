import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

app=FastAPI(title="Scraper Test Hub API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from twitter_scraper import search_twitter_hazards
@app.get("/api/twitter/search")
def twitter_search(limit:int=Query(10,ge=1,le=100)):
    if not os.getenv("TWITTER_BEARER_TOKEN"):
        return {"error":"TWITTER_BEARER_TOKEN missing on server"}
    return search_twitter_hazards(limit=limit)

from youtube_scraper import YouTubeScraper  # already in server dir

@app.get("/api/youtube/scrape")
def youtube_scrape(max_results: int = Query(8, ge=1, le=30)):
    scraper = YouTubeScraper()
    # This returns a dict[hazard_category: list[VideoInfo]]
    results = scraper.scrape_all_hazards(max_results_per_query=max_results)
    serializable = {
        k: [v.__dict__ for v in lst] for k, lst in results.items()
    }
    return {"results": serializable}
