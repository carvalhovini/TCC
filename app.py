from flask import Flask, request, jsonify, render_template
from twilio.rest import Client
import json

app = Flask(__name__)

# Configurações do Twilio
account_sid = 'ACa627819f49beb8d8c3f670fab3b9df16'
auth_token = '288b4a4ea626bcf396fcc93aa6e61cb8'
twilio_number = 'whatsapp:+14155238886'  # Este é o número de sandbox do Twilio para WhatsApp
client = Client(account_sid, auth_token)

# Carregar dados fictícios de empresas de um arquivo JSON
with open('empresas.json') as f:
    empresas_data = json.load(f)

empresas = {empresa['nome']: empresa for empresa in empresas_data}

templates = {
    'bem_vindo': 'Bem-vindo à CNT, {nome_empresa}! Estamos aqui para ajudar.',
    'aviso': 'Lembramos que o prazo para envio de documentos é {data_limite}.'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar_empresa', methods=['POST'])
def cadastrar_empresa():
    data = request.json
    nome = data['nome']
    cnpj = data['cnpj']
    estado = data['estado']
    numero = data['numero']
    empresas[nome] = {
        'cnpj': cnpj,
        'estado': estado,
        'numero': numero
    }
    return jsonify({'status': 'Empresa cadastrada com sucesso!'})

@app.route('/empresas', methods=['GET'])
def listar_empresas():
    estado = request.args.get('estado')
    if estado:
        filtered_empresas = {nome: dados for nome, dados in empresas.items() if dados['estado'].lower() == estado.lower()}
    else:
        filtered_empresas = empresas
    return jsonify({'empresas': [{'nome': nome, 'estado': dados['estado'], 'numero': dados['numero']} for nome, dados in filtered_empresas.items()]})

@app.route('/configurar_template', methods=['POST'])
def configurar_template():
    data = request.json
    nome = data['nome']
    mensagem = data['mensagem']
    templates[nome] = mensagem
    return jsonify({'status': 'Template criado/editado com sucesso!'})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    sistema = data.get('sistema', 'N/A')
    filtro = data.get('filtro')
    filtro_valor = data.get('filtro_valor')
    empresas_selecionadas = data.get('empresas', [])
    message_body = f"{sistema}: {data['message']}"

    if filtro == 'todos':
        empresas_selecionadas = [dados['numero'] for nome, dados in empresas.items()]
    elif filtro == 'estado':
        empresas_selecionadas = [dados['numero'] for nome, dados in empresas.items() if dados['estado'].lower() == filtro_valor.lower()]

    for empresa in empresas_selecionadas:
        to_number = 'whatsapp:' + empresa
        if data['type'] == 'texto':
            message = client.messages.create(body=message_body, from_=twilio_number, to=to_number)
        elif data['type'] == 'link':
            message = client.messages.create(body=message_body, from_=twilio_number, to=to_number)
        elif data['type'] == 'imagem':
            media_url = data['message']  # Assumindo que a mensagem contém a URL da imagem
            message = client.messages.create(media_url=[media_url], from_=twilio_number, to=to_number)
        elif data['type'] == 'audio':
            media_url = data['message']  # Assumindo que a mensagem contém a URL do áudio
            message = client.messages.create(media_url=[media_url], from_=twilio_number, to=to_number)
        elif data['type'] == 'video':
            media_url = data['message']  # Assumindo que a mensagem contém a URL do vídeo
            message = client.messages.create(media_url=[media_url], from_=twilio_number, to=to_number)

    return jsonify({'status': 'Messages sent successfully'})

if __name__ == '__main__':
    app.run(debug=True)
