import pandas as pd
from sheets import cadastros

def ConfereListaTelegram():
    sheet = cadastros.abrir_planilha()
    print('(TELEGRAM) URL Aberto e planilha importada!')
    worksheet = sheet.worksheet("PromPeriodicaTel")
    dados = worksheet.get_all_values()
    colunas = dados.pop(0)
    infos_telegram = pd.DataFrame(data=dados, columns=colunas)
    print(infos_telegram)
    infos_telegram.to_json('cron/dados_telegram.json', orient='records')
