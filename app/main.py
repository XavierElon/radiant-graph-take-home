from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .api import customers_router, health_router, orders_router, analytics_router
import sys
import uvicorn
import click

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Radiant Graph API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(health_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(analytics_router)

def main():
    """Production server entry point"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

def dev():
    """Development server entry point"""
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

@click.group()
def cli():
    """Radiant Graph CLI"""
    pass

@cli.command()
def start():
    """Start the production server"""
    main()

@cli.command()
def dev():
    """Start the development server"""
    dev()
    
@cli.command()
def test():
    """Run the test suite."""
    import subprocess
    subprocess.run(["pytest", "-v"])

if __name__ == "__main__":
    cli() 