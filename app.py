from flask import Flask, request, jsonify, render_template
from twilio.rest import Client
import json
import os

app = Flask(__name__)

# Configurações do Twilio - Utilize variáveis de ambiente para maior segurança
account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'ACa627819f49beb8d8c3f670fab3b9df16')
auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'bda534c7ce63efb0aa616d707c1dae91')
twilio_number = os.getenv('TWILIO_NUMBER', 'whatsapp:+13613385594')
client = Client(account_sid, auth_token)

# Carregar dados fictícios de empresas de um arquivo JSON
with open('empresas.json') as f:
    empresas_data = json.load(f)

empresas = {empresa['nome']: empresa for empresa in empresas_data}

templates = {
    'bem_vindo': 'Bem-vindo ao Sistema Transportador! Estamos aqui para ajudar.',
    'aviso': 'Lembramos que o prazo para envio de documentos é amanhã.'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar_empresa', methods=['POST'])
def cadastrar_empresa():
    data = request.json
    nome = data.get('nome')
    cnpj = data.get('cnpj')
    estado = data.get('estado')
    numero = data.get('numero')

    if not all([nome, cnpj, estado, numero]):
        return jsonify({'status': 'Erro: Todos os campos são obrigatórios.'}), 400

    empresas[nome] = {
        'cnpj': cnpj,
        'estado': estado,
        'numero': numero
    }
    return jsonify({'status': 'Empresa cadastrada com sucesso!'})

@app.route('/empresas', methods=['GET'])
def listar_empresas():
    estado = request.args.get('estado')
    filtered_empresas = {nome: dados for nome, dados in empresas.items() if not estado or dados['estado'].lower() == estado.lower()}
    return jsonify({
        'empresas': [{'nome': nome, 'estado': dados['estado'], 'numero': dados['numero']} for nome, dados in filtered_empresas.items()]
    })

@app.route('/configurar_template', methods=['POST'])
def configurar_template():
    data = request.json
    nome = data.get('nome')
    mensagem = data.get('mensagem')

    if not nome or not mensagem:
        return jsonify({'status': 'Erro: Nome e mensagem são obrigatórios.'}), 400

    templates[nome] = mensagem
    return jsonify({'status': 'Template criado/editado com sucesso!'})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    sistema = data.get('sistema', 'N/A')
    filtro = data.get('filtro')
    filtro_valor = data.get('filtro_valor')
    empresas_selecionadas = data.get('empresas', [])
    message_body = f"{sistema}: {data.get('message', '')}"

    if filtro == 'todos':
        empresas_selecionadas = [dados['numero'] for nome, dados in empresas.items()]
    elif filtro == 'estado' and filtro_valor:
        empresas_selecionadas = [dados['numero'] for nome, dados in empresas.items() if dados['estado'].lower() == filtro_valor.lower()]

    if not empresas_selecionadas:
        return jsonify({'status': 'Erro: Nenhuma empresa encontrada com o critério fornecido.'}), 404

    for numero in empresas_selecionadas:
        to_number = f'whatsapp:{numero}'
        msg_type = data.get('type', 'texto')
        media_url = data.get('message') if msg_type in ['imagem', 'audio', 'video'] else None

        message = client.messages.create(
            body=message_body if msg_type == 'texto' else None,
            from_=twilio_number,
            to=to_number,
            media_url=[media_url] if media_url else None
        )

    return jsonify({'status': 'Mensagens enviadas com sucesso!'})

if __name__ == '__main__':
    app.run(debug=True)
