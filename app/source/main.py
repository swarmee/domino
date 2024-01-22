############
# usage : uvicorn main:app --reload --no-access-log
############

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from middleware import JSONLogMiddleware
from routes import router

app = FastAPI(title="Domino",
              description= "Down sampled timeseries data", 
              openapi_tags=[
                  {
                      "name": "Extract",
                      "description": "Extract Summary",
                  },
                  {
                      "name": "Prometheus Metrics",
                      "description": "Prometheus metrics endpoint",
                  },
              ])

# Add metrics for Prometheus
Instrumentator().instrument(app).expose(app)
# Include the routes
app.include_router(router)
# Add JSON logging
app.add_middleware(JSONLogMiddleware)
