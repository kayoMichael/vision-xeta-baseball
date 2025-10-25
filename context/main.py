from fastapi import FastAPI
from context.routes.predict import router
app = FastAPI()

app.include_router(router)

@app.get("/")
def health_check():
    """
    health check for the Context server
    :return: payload
    """
    return {"body": "special week!"}

