from flask import Flask, request, jsonify
from cron import envia_promocoes
from sheets.cadastros import cadastrar_sheets_zap, cadastrar_sheets_tel
from threading import Thread
import asyncio
from flask_executor import Executor
from encomendas import rastreio

app = Flask(__name__)
executor = Executor(app)

# Variáveis para o envio periódico de mensagens:
envia_promocoes.token_telegram = '7408783735:AAF4oOtPpPGQXxpiJmXQP-_fosRZ7zjpR5g'

# Inicializando o CRON
def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(envia_promocoes.main())
    loop.close()

def start_cron():
    thread = Thread(target=start_async_loop)
    thread.start()

#Função que inicia o CRON
#start_cron()

@app.route('/', methods=['POST'])
def main_route():
    data = request.get_json(silent=True, force=True)
    contextos = data['queryResult']['outputContexts']

    numero = None # Para teste de variável

    cadastro_whatsapp_feito = False
    cadastro_telegram_feito = False

    # Bloco 1 -> Testa se é para Cadastrar na Lista de Transmissão (WhatsApp)
    try:
        for contexto in contextos:
            parametros = contexto['parameters']
            nome = parametros.get('nome')
            numero = parametros.get('numero')
            if nome and numero and not cadastro_whatsapp_feito:
                print(f'Nome: {nome} | Tel: {numero}')
                Thread(target=cadastrar_sheets_zap, args=([nome, numero],)).start()
                cadastro_whatsapp_feito = True

    except Exception as e:
        print(f"Erro no cadastro do WhatsApp: {e}")


    # Bloco 2 -> Testa se é para Cadastrar na Lista de Transmissão (Telegram)
    if numero is not None: # Para garantir que nã o vai rodar esse bloco caso o anterior tenha sido executado
        return jsonify(data)

    try:
        for contexto in contextos:
            parametros = contexto['parameters']
            nome = parametros.get('nome')
            id = data['session'].split('/')[-1]
            if nome and id and not cadastro_telegram_feito:
                print(f'Nome: {nome} | ID: {id}')
                Thread(target=cadastrar_sheets_tel, args=([nome, id],)).start()
                cadastro_telegram_feito = True
    except Exception as e:
        print(f"Erro no cadastro do Telegram: {e}")


    #Bloco 3 -> Testa se é para fazer o rastreio da encomenda
    try:
        # Obtendo as informações do Webhook
        for contexto in contextos:
            parametros = contexto['parameters']
            entrada = parametros.get('codigo')

            # Testa se é CPF
            if len(rastreio.verificaCPF(entrada)) == 11:
                cpf = rastreio.verificaCPF(entrada)
                variaveis_rastreio = rastreio.rastreioCPF(cpf)
                msg_corrigida = f"Encontrei o seu pedido aqui, o status da entrega do seu pedido é:\n{variaveis_rastreio['estado']} - {variaveis_rastreio['data']}\n\nPosso te ajudar com algo mais?\nSe sim, digite menu\nSe não, digite sair."
                print(msg_corrigida)
                data['fulfillmentText'] = msg_corrigida
                return jsonify(data)
            else:
                data['fulfillmentText'] = 'NÃO É CPF'
                return jsonify(data)

            # Se não for CPF, testa o código de rastreio:
            variaveis_rastreio = rastreio.rastreioEncomenda(entrada)
            msg_corrigida = f"Encontrei o seu pedido aqui, o status da entrega do seu pedido é:\n{variaveis_rastreio['estado']} - {variaveis_rastreio['data']}\n\nPosso te ajudar com algo mais?\nSe sim, digite menu\nSe não, digite sair."
            #print(msg_corrigida)
            data['fulfillmentText'] = msg_corrigida

    except:
        data['fulfillmentText'] = 'Verifique se o CPF ou CÓDIGO DE RASTREIO estão corretos, por favor, e tente novamente!'

    #print(data)

    return jsonify(data)

if __name__ == "__main__":
    app.debug = False
    start_cron()
    app.run()
