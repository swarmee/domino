# routes.py
from fastapi import APIRouter, Header, Request, Query, Response
from fastapi.responses import HTMLResponse
from typing import Optional, Union
from models import UserAgentEnum, Message
from prometheus_client import generate_latest
from business_logic import process_request
import time
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from forecasting import create_time_series, perform_forecasting, graph_forecast
from middleware import logger

router = APIRouter()


@router.get("/summary/data/raw",
            tags=["Extract"])
async def read_root(request: Request, reporting_entity_id: int = Query(description="filter by reporting entity id", example=1000),
    correlation_id: Optional[str] = Header(None),
    accept: Optional[str] = Header("application/json",
                                   description="Media type(s) that is/are acceptable for the response."),
    user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                             description="Information about the user agent originating the request.")):
    logger.info("Getting data from data store", extra={"correlation_id": request.state.correlation_id})
    df = create_time_series(reporting_entity_id)
    response = Response(df.to_json(orient='records'),
                        media_type='application/json')
    response.headers["reporting-entity-id-filter"] = str(reporting_entity_id)
    return response


@router.get("/summary/forecast/raw",
            tags=["Create"])
async def read_root(correlation_id: Optional[str] = Header(None),
                    accept: Optional[str] = Header("application/json",
                                                   description="Media type(s) that is/are acceptable for the response."),
                    user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                                             description="Information about the user agent originating the request.")):
    df = create_time_series()
    forecast = perform_forecasting(df)
    return forecast.to_dict('records')


@router.get("/summary/forecast/chart",
            tags=["Create"],
            response_class=HTMLResponse
            )
async def return_chart(correlation_id: Optional[str] = Header(None),
                       accept: Optional[str] = Header("application/json",
                                                      description="Media type(s) that is/are acceptable for the response."),
                       user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                                                description="Information about the user agent originating the request.")):
    df = create_time_series()
    forecast = perform_forecasting(df)
    plotly_chart = graph_forecast(forecast)
    # Convert the Plotly chart to HTML
    plotly_html = plotly_chart.to_html(full_html=False)

    return plotly_html


# Define the metrics endpoint so it appears in the swagger page
@router.get("/metrics",
            include_in_schema=True,
            operation_id="metrics_get",
            tags=["Prometheus Metrics"])
async def metrics():
    return generate_latest().decode("utf-8")
