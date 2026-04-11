from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server is running"}

def main():
    import uvicorn
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()