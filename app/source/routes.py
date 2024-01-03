# routes.py
from fastapi import APIRouter, Header, Body, Query
from typing import Optional, Union
from models import UserAgentEnum, Message
from prometheus_client import generate_latest
from business_logic import process_request
import time
import pandas as pd
import numpy as np
    

router = APIRouter()


@router.get("/summary",
             tags=["Create"])
async def read_root(count: int = Query(None),
                    correlation_id: Optional[str] = Header(None),
                    accept: Optional[str] = Header("application/json",
                                                   description="Media type(s) that is/are acceptable for the response."),
                    user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                                             description="Information about the user agent originating the request.")):
    start_time = time.time()
    df1 = pd.DataFrame(np.random.rand(count, count))
    df3 = df1.mul(df1)
    end_time = time.time()
    processing_time = end_time - start_time

    headers = {
        "Processing-Time": str(processing_time)
    }

    return headers


# Define the metrics endpoint so it appears in the swagger page
@router.get("/metrics",
            include_in_schema=True,
            operation_id="metrics_get",
            tags=["Prometheus Metrics"])
async def metrics():
    return generate_latest().decode("utf-8")
