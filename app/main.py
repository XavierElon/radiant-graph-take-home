from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .api import customers_router, health_router, orders_router, analytics_router
import uvicorn
import click

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Radiant Graph API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# Include routers
app.include_router(health_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(analytics_router)

def print_api_docs_urls():
    print("\n=== API Documentation URLs ===")
    print("Swagger UI: http://localhost:8000/docs")
    print("ReDoc:      http://localhost:8000/redoc")
    print("=============================\n")

def main():
    """Production server entry point"""
    print_api_docs_urls()
    uvicorn.run(app, host="0.0.0.0", port=8000)

def dev():
    """Development server entry point"""
    print_api_docs_urls()
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