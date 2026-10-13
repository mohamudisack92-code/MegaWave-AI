import asyncio, json, os, websockets
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
DERIV_TOKEN = os.getenv("DERIV_TOKEN")
APP_ID = "1089"

async def deriv_ticks():
    uri = f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"authorize": DERIV_TOKEN}))
        await ws.recv()
        await ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        while True:
            msg = json.loads(await ws.recv())
            if "tick" in msg:
                yield float(msg["tick"]["quote"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ MegaWave-AI Bot Online!\nUse /analyze for signal")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Analyzing market...")
    prices = []
    async for p in deriv_ticks():
        prices.append(p)
        if len(prices) >= 50:
            break
    # Simple logic - replace with your Hama strategy later
    last = prices[-1]
    avg = sum(prices[-10:])/10
    if last > avg:
        sig = "🟢 CALL (UP) - Price above avg"
    else:
        sig = "🔴 PUT (DOWN) - Price below avg"
    await update.message.reply_text(f"MegaWave Signal:\n{sig}\nPrice: {last}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    app.run_polling()

if __name__ == "__main__":
    main()
