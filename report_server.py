import uvicorn
from fastapi import FastAPI

from admin_report import create_report
from create_bot import bot

app = FastAPI()


@app.get('/report')
async def create_admin_report():
    msg = await create_report()
    return {"msg": msg}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
