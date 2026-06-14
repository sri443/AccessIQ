from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    upload,
    analysis,
    dashboard,
    users,
    graph,
    compliance,
    report,
    baseline,
    timeline,
    blast_radius,
    hackathon_scoring,
)

app = FastAPI(
    title="AccessIQ - Identity Risk Intelligence Platform",
    description="Identity Sprawl & Privilege Abuse Detection",
    version="1.0.0",
)

# CORS - Allow your frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - allows any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route (only ONE)
@app.get("/")
async def root():
    return {
        "name": "AccessIQ API",
        "version": "1.0.0",
        "status": "operational",
    }

# Routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(graph.router, prefix="/api/graph", tags=["Graph"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(report.router, prefix="/api/report", tags=["Report"])
app.include_router(baseline.router, prefix="/api", tags=["Baseline"])
app.include_router(timeline.router, prefix="/api", tags=["Timeline"])
app.include_router(blast_radius.router, prefix="/api", tags=["Blast Radius"])
app.include_router(hackathon_scoring.router, prefix="/api", tags=["Hackathon Scoring"])