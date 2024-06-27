import requests
from bs4 import BeautifulSoup
import re
import json

codigoValido = '''
{
    "fulfillmentMessages": [
        {
            "text": {
                "text": [
                    "Encontrei o seu pedido aqui, o status da entrega do seu pedido é:\n{} - {}\nPosso te ajudar com algo mais?\nSe sim, digite menu\nSe não, digite sair."
                ]
            }
        }
    ]
}
'''

def verificaCPF(valor):
    # Remover todos os caracteres não numéricos
    numeros = re.sub(r'\D', '', valor)
    # Pegar apenas os primeiros 11 caracteres
    numeros = numeros[:11]
    return numeros

def rastreioCPF(cpf):
    return 10

def rastreioEncomenda(cod_rastreio):
    url = f"https://linketrack.com/{cod_rastreio}/html?utm_source=link"

    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.content  # Isso aqui é o dado bruto
    else:
        print('No momento meu sistema não consegue acessar os dados da sua encomenda 😔')

    soup = BeautifulSoup(html_content, "html.parser")  # Arquivo no formato HTML

    # Infos para a análise
    invalido = str(soup.find_all(lambda elemento: re.search('var codigoInvalido = false;', elemento.text)))
    valido = str(soup.find_all(lambda elemento: re.search('var codigo =', elemento.text)))

    # Bloco que não achou o código de rastreio
    if invalido[13:27] == 'codigoInvalido':
        #print(f'O código fornecido ({cod_rastreio}) não é válido, confira se ele está correto!')
        return True

    # Bloco que achou o código de rastreio e extrai as informações
    else:
        regex_variavel = r"var\s+(\w+)\s*=\s*'(.*?)';"
        ocorrencias = re.findall(regex_variavel, valido)

        data_html = str(soup.find('div', class_='servico italic'))

        variaveis_rastreio = {}

        variaveis_rastreio['data'] = data_html[66:88]
        print(ocorrencias)
        for ocorrencia in ocorrencias:
            variaveis_rastreio[ocorrencia[0]] = ocorrencia[1]

        # Imprimindo na tela para debugar o que foi feito
        #print(f'=========== INFORMAÇÕES DO RASTREIO ===========')
        #print(f"Código informado: {variaveis_rastreio['codigo']}")
        #print(f"Data da movimentação: {variaveis_rastreio['data']}")
        #print(f"Estado da encomenda: {variaveis_rastreio['estado']}")

        resposta = codigoValido.format(variaveis_rastreio['estado'], variaveis_rastreio['data'])
        output = json.loads(resposta)
        return output