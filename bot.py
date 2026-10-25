import asyncio
import logging
import urllib.parse
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = "8989233616:AAG_vtA6d72txtqEuFdzW7S7y66ylTtVXoQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_cs2_skin_price(skin_name: str) -> dict | None:
    # Кодируем название предмета для ссылки
    encoded_name = urllib.parse.quote(skin_name)
    
    # currency=5 — цена в рублях (1 — в долларах)
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=5&market_hash_name={encoded_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get("success"):
            return {
                "lowest_price": data.get("lowest_price", "Нет данных"),
                "median_price": data.get("median_price", "Нет данных"),
                "volume": data.get("volume", "0")
            }
    except Exception as e:
        print(f"Ошибка при запросе к Steam: {e}")
        
    return None

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Привет! Я бот по ценам на скины CS2.**\n\n"
        "Отправь мне полное название скина на английском, например:\n"
        "`AK-47 | Redline (Field-Tested)`\n"
        "`USP-S | Flashback (Field-Tested)`",
        parse_mode="Markdown"
    )

@dp.message()
async def check_skin_handler(message: types.Message):
    skin_name = message.text.strip()
    await message.answer(f"🔍 Ищу цену для `{skin_name}`...", parse_mode="Markdown")
    
    price_info = get_cs2_skin_price(skin_name)
    
    if price_info:
        response_text = (
            f"🎯 **Предмет:** {skin_name}\n"
            f"💰 **Минимальная цена:** {price_info['lowest_price']}\n"
            f"📈 **Средняя цена:** {price_info['median_price']}\n"
            f"📊 **Продано за 24ч:** {price_info['volume']} шт."
        )
        await message.answer(response_text, parse_mode="Markdown")
    else:
        await message.answer(
            "❌ **Скин не найден!**\n"
            "Убедись, что название написано строго на английском и совпадает с Торговой площадкой Steam."
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())