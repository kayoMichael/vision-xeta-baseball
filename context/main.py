from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def health_check():
    """
    health check for the Context server
    :return: payload
    """
    return {"body": "special week!"}

