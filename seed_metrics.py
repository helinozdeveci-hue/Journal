import sqlite3
from db import create_metric

metrics = [
    "stomach ache",
    "sad",
    "stress",
    "calm",
    "energy",
    "happy",
    "nausea",
    "anxious",
    "depressed",
    "interest in activities",
    "anger",
    "excitable",
    "mood swings",
    "aggressive",
    "impulsive",
    "irritable",
    "hyperactive",
    "attention problems",
    "focus problems",
    "forgetfulness"
]

def seed_metrics():
    for m in metrics:
        try:
            create_metric(m)
        except sqlite3.IntegrityError:
            pass