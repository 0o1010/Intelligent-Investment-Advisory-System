from app.api import create_app

app = create_app()
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='main:app', host="localhost", port=8000, reload=True)
