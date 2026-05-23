import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# 🧠 AI NSFW check
def check_nsfw(image_path):
    try:
        url = "https://api.deepai.org/api/nsfw-detector"

        with open(image_path, "rb") as f:
            r = requests.post(
                url,
                files={"image": f},
                headers={"api-key": "free-key"}
            )

        data = r.json()
        return data["output"]["nsfw_score"]

    except:
        return 0.0


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    user = msg.from_user
    chat_id = update.effective_chat.id

    file_path = None

    try:
        # medya al
        if msg.photo:
            file = await context.bot.get_file(msg.photo[-1].file_id)
            file_path = "img.jpg"
            await file.download_to_drive(file_path)

        elif msg.video or msg.animation:
            file = await context.bot.get_file(
                (msg.video or msg.animation).file_id
            )
            file_path = "vid.mp4"
            await file.download_to_drive(file_path)

        else:
            return

        # AI analiz
        score = check_nsfw(file_path)
        print("NSFW SCORE:", score)

        if score >= 0.65:
            # mesaj sil
            await msg.delete()

            # uyarı
            await context.bot.send_message(
                chat_id,
                f"⚠️ {user.first_name} +18 içerik yasaktır."
            )

    except Exception as e:
        print("Hata:", e)

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, handler)
)

print("AI MOD BOT AKTİF")
app.run_polling()
