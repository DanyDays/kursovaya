import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
 
BOT_TOKEN = "8416178440:AAHLASuvRArpfzS_nZBSY-LRC_L0pJX1m2k"
OPENWEATHER_API_KEY = "2e17c89c2ecc73c87a5d2fd10ab1818c"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = "🌤️ Привет! Я бот для отслеживания погоды. \nПросто отправь мне название города, и я покажу текущую погоду!"
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "📖 Доступные команды: \n/start - начать работу \n/help - показать эту справку \n/weather <город> - узнать погоду в городе"
    await update.message.reply_text(help_text)

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Пожалуйста, укажи город после команды:\n/weather Москва")
        return
    city_name = " ".join(context.args)
    await get_weather_data(update, city_name)

def get_weather_from_api(city_name):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city_name,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'ru'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": "Город не найден"}
        else:
            return {"error": f"Ошибка API: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка соединения: {e}"}

async def get_weather_data(update: Update, city_name):
    weather_data = get_weather_from_api(city_name)
    if "error" in weather_data:
        await update.message.reply_text(f"❌ {weather_data['error']}")
        return
    try:
        city = weather_data["name"]
        country = weather_data['sys']['country']
        temp = round(weather_data['main']['temp'])
        feels_like = round(weather_data['main']['feels_like'])
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        description = weather_data['weather'][0]['description'].capitalize()
        wind_speed = weather_data['wind']['speed']

        weather_emojis = {
            'ясно': '☀️',
            'облачно': '☁️',
            'пасмурно': '☁️',
            'дождь': '🌧️',
            'снег': '❄️',
            'туман': '🌫️',
            'гроза': '⛈️'
        }

        emoji = "🌤️"
        for key, value in weather_emojis.items():
            if key in description.lower():
                emoji = value
                break
        weather_text = f""" {emoji} Погода в {city}, {country}:
        🌡️ Температура: {temp}°C
        🤔 Ощущается как: {feels_like}°C
        📝 Описание: {description}
        💧 Влажность: {humidity}%
        📊 Давление: {pressure} гПа
        💨 Ветер: {wind_speed} м/с"""
        await update.message.reply_text(weather_text)
    except KeyError as e:
        await update.message.reply_text("❌ Ошибка при обработке данных о погоде")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    if not message_text.startswitch('/'):
        await get_weather_data(update, message_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")
    await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    print("🤖 Бот запущен...")
    application.run_polling()

if __name__ == "__main__": main()
