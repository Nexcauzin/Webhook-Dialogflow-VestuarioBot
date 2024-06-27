import httpx
import telegram.error
from telegram import Bot
import pandas as pd
from sheets import ler_telegram
from sheets.cadastros import fazer_login
import asyncio

token_telegram = '7047287612:AAEMimLtSeFAbVsgkY8cmGKnZZhVjon5vik'

async def send_telegram_message():
    ler_telegram.ConfereListaTelegram()
    dados_telegram = pd.read_json('cron/dados_telegram.json')
    tentas = 0

    while tentas < len(dados_telegram):
        try:
            bot = Bot(token=token_telegram)
            user_id = int(dados_telegram['ID'][tentas])

            with open('cron/MensagemTelegram.txt', 'r+', encoding='utf-8') as file:
                message = file.read()

            await bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
            tentas += 1

        except (telegram.error.NetworkError, httpx.ConnectError) as erro:
            print(f'Erro:{erro} | Iteração:{tentas}')
            continue


async def schedule_messages():
    fazer_login()  # Faz login apenas aqui uma vez

    while True:
        await send_telegram_message()
        await asyncio.sleep(15 * 24 * 60 * 60)      # 15 dias em segundos
                           #dia/hora/min/sec

async def main():
    await schedule_messages()