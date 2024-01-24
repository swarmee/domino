############
# usage : uvicorn main:app --reload --no-access-log
############

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from middleware import JSONLogMiddleware
from routes import router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Domino",
              description= "Down sampled timeseries data", 
              openapi_tags=[
                  {
                      "name": "Extract",
                      "description": "Extract Summary",
                  },
                  {
                      "name": "Infrastructure",
                      "description": "Prometheus metrics and Kubernetes Health Probe endpoints",
                  },
              ])

# Add metrics for Prometheus
Instrumentator().instrument(app).expose(app)
# Include the routes
app.include_router(router)
# Add JSON logging
app.add_middleware(JSONLogMiddleware)
# Set the Templates Directory
app.state.templates = Jinja2Templates(directory="templates")
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
