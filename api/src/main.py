import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title="Personal Finance Tracker",
    docs_url="/api/openapi/",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
