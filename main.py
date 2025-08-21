import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types

# Берём токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- команды бота ---
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот на Render 🌐")

@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    await message.answer("Команды: /start, /help")

# --- сервер для Render ---
app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret")
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render сам даст ссылку
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return {"ok": True}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
