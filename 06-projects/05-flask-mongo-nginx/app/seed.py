"""
Seed script — populates MongoDB with sample books.
Run via: make seed
Or directly: docker compose exec app python seed.py
"""
import os
from pymongo import MongoClient

client = MongoClient(os.environ["MONGO_URI"])
db = client.get_default_database()
books = db["books"]

sample_books = [
    {"title": "The Phoenix Project",       "author": "Gene Kim",           "year": 2013},
    {"title": "The DevOps Handbook",       "author": "Gene Kim",           "year": 2016},
    {"title": "Site Reliability Engineering", "author": "Google SRE Team", "year": 2016},
    {"title": "Accelerate",                "author": "Nicole Forsgren",    "year": 2018},
    {"title": "Docker Deep Dive",          "author": "Nigel Poulton",      "year": 2023},
]

books.delete_many({})
result = books.insert_many(sample_books)
print(f"Inserted {len(result.inserted_ids)} books.")
