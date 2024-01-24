# routes.py
from fastapi import APIRouter, Header, Request, Query, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, Union
from models import UserAgentEnum
from prometheus_client import generate_latest
from forecasting import create_time_series, perform_forecasting, graph_forecast, graph_forecast_test
from middleware import logger
from datetime import datetime

router = APIRouter()


@router.get("/summary/data/raw",
            tags=["Extract"])
async def read_root(request: Request,
                    reporting_entity_id: Optional[int] = Query(description="filter by reporting entity id",
                                                     gt=999,
                                                     lt=999999,
                                                     example=1000),
                    correlation_id: Optional[str] = Header(None),
                    accept: Optional[str] = Header("application/json",
                                                   description="Media type(s) that is/are acceptable for the response."),
                    user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                                             description="Information about the user agent originating the request.")):
    logger.info("Getting data from data store", extra={
                "correlation_id": request.state.correlation_id})
    df = create_time_series(reporting_entity_id)
    response = Response(df.to_json(orient='records'),
                        media_type='application/json')
    response.headers["reporting-entity-id-filter"] = str(reporting_entity_id)
    return response


@router.get("/summary/forecast/raw",
            tags=["Create"])
async def read_root(request: Request,
                    reporting_entity_id: int = Query(description="filter by reporting entity id",
                                                     gt=999,
                                                     lt=999999,
                                                     example=1000),
                    correlation_id: Optional[str] = Header(None),
                    accept: Optional[str] = Header("application/json",
                                                   description="Media type(s) that is/are acceptable for the response."),
                    user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                                             description="Information about the user agent originating the request.")):
    logger.info("Getting data from data store", extra={
                "correlation_id": request.state.correlation_id})
    df = create_time_series(reporting_entity_id)
    forecast = perform_forecasting(df)
    return forecast.to_dict('records')


@router.get("/summary/forecast/chart",
            tags=["Create"],
            response_class=HTMLResponse
            )
async def return_chart(request: Request,
                       reporting_entity_id: int = Query(description="filter by reporting entity id",
                                                        gt=999,
                                                        lt=999999,
                                                        example=1000),
                       correlation_id: Optional[str] = Header(None),
                       accept: Optional[str] = Header("application/json",
                                                      description="Media type(s) that is/are acceptable for the response."),
                       user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                                                description="Information about the user agent originating the request."),
                       download: bool = False
                       ):
    df = create_time_series(reporting_entity_id)
    forecast = perform_forecasting(df)
    dataframe_html = forecast[['ds', 'y']].to_html(classes="table table-striped", index=False)
    dataframe_html = dataframe_html.replace('<th>', '<th style="text-align:center;">')
    plotly_chart = graph_forecast(forecast)
    # Convert the Plotly chart to HTML
    plotly_html = plotly_chart.to_html(full_html=False)
    date_generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response =  request.app.state.templates.TemplateResponse("chart.html",
                                                        {"request": request,
                                                         "plotly_html": plotly_html,
                                                         "reporting_entity_id": reporting_entity_id,
                                                         "date_generated" : date_generated,
                                                         "dataframe_html" : dataframe_html
                                                         })
    if download:
        response.headers["Content-Disposition"] =  f"attachment; filename={reporting_entity_id}-chart.html"
    return response


@router.get("/")
def root():
    return RedirectResponse(url="/test/forecast/chart")

@router.get("/test/forecast/chart",
            tags=["Create"],
            response_class=HTMLResponse
            )
async def return_chart(
                       reporting_entity_id: Optional[int] = Query(None, description="filter by reporting entity id",
                                                        gt=999,
                                                        lt=999999,
                                                        example=1000),
                       correlation_id: Optional[str] = Header(None),
                       accept: Optional[str] = Header("application/json",
                                                      description="Media type(s) that is/are acceptable for the response."),
                       user_agent: Optional[Union[UserAgentEnum, str]] = Header(UserAgentEnum.curl,
                                                                                description="Information about the user agent originating the request."),
                       ):
    if reporting_entity_id is None:
        reporting_entity_id = 1000
    df = create_time_series(reporting_entity_id)
    forecast = perform_forecasting(df)
    plotly_chart = graph_forecast_test(forecast, reporting_entity_id)
    # Convert the Plotly chart to HTML
    plotly_html = plotly_chart.to_html(full_html=False)
    return plotly_html



# Define the metrics endpoint so it appears in the swagger page
@router.get("/metrics",
            include_in_schema=True,
            operation_id="metrics_get",
            tags=["Infrastructure"])
async def metrics():
    return generate_latest().decode("utf-8")


# Liveness probe endpoint
@router.get("/healthz", tags=["Infrastructure"])
async def healthz():
    return {"status": "ok"}

# Readiness probe endpoint
@router.get("/readyz", tags=["Infrastructure"])
async def readyz():
    # Add logic to check if the service is ready to handle traffic

    return {"status": "ok"}