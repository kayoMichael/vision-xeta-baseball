from fastapi import FastAPI
from context.routes.predict import predict_router
from context.routes.prospect import prospect_router
from context.routes.card_info import card_router
app = FastAPI()

app.include_router(predict_router)
app.include_router(prospect_router)
app.include_router(card_router)

@app.get("/")
def health_check():
    """
    health check for the Context server
    :return: payload
    """
    return {"body": "special week!"}

