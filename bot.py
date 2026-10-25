import asyncio
import logging
import urllib.parse
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = "8989233616:AAG_vtA6d72txtqEuFdzW7S7y66ylTtVXoQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def get_cs2_skin_price(skin_name: str) -> dict | None:
    # Используем асинхронный запрос через aiohttp и публичное API цен
    encoded_name = urllib.parse.quote(skin_name)
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=5&market_hash_name={encoded_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        return {
                            "lowest_price": data.get("lowest_price", "Нет данных"),
                            "median_price": data.get("median_price", "Нет данных"),
                            "volume": data.get("volume", "0")
                        }
                else:
                    print(f"Ошибка Steam API: статус {response.status}")
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            
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
    
    price_info = await get_cs2_skin_price(skin_name)
    
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