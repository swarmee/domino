# routes.py
from fastapi import APIRouter, Header, Body, Query
from typing import Optional, Union
from models import UserAgentEnum, Message
from prometheus_client import generate_latest
from business_logic import process_request
import time
import pandas as pd
import numpy as np
import datetime
from log_setup import logger
import random
from dateutil.relativedelta import relativedelta


router = APIRouter()

def create_time_series():
    time_series = []
    y_value = 1000000

    for month in range(48):
        date = (datetime.datetime(2019, 1, 1) + relativedelta(months=+month)).strftime('%Y-%m-%d')
        jump = random.choice([random.uniform(1, 2), random.uniform(100, 999900)]) * random.choice([2, 1,1,55])
        y_value += jump
        time_series.append({"ds": date, "y": int(y_value)})

    return time_series


@router.get("/summary",
            tags=["Create"])
async def read_root(correlation_id: Optional[str] = Header(None),
                    accept: Optional[str] = Header("application/json",
                                                   description="Media type(s) that is/are acceptable for the response."),
                    user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                                             description="Information about the user agent originating the request.")):
    start_time = time.time()
    response = create_time_series()
    end_time = time.time()
    processing_time = end_time - start_time
    logger.info(f'Processing time for the API route: {processing_time} seconds')

    return response


# Define the metrics endpoint so it appears in the swagger page
@router.get("/metrics",
            include_in_schema=True,
            operation_id="metrics_get",
            tags=["Prometheus Metrics"])
async def metrics():
    return generate_latest().decode("utf-8")
