import imaplib
import email 
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup 

app = Flask(__name__)

quantidade_de_caracteres_do_codigo = 5
 
def extract_activation_code(email_content):
    # Inicializando lista para armazenar os códigos de ativação encontrados
    activation_codes = []
    
    # Usando BeautifulSoup para analisar o conteúdo HTML do e-mail
    soup = BeautifulSoup(email_content, 'html.parser')
    
    # Encontrando todas as tags <strong>
    strong_tags = soup.find_all('strong')
    
    # Iterando sobre as tags <strong> encontradas
    for strong_tag in strong_tags:
        # Extraindo o texto dentro da tag <strong>

        code = strong_tag.text.strip()
        # Adicionando o código de ativação à lista

        if(len(str(code)) == quantidade_de_caracteres_do_codigo): # Verifica se tem 5 caracteres
            if(code.isdigit()): # Verifica se são numeros
                activation_codes.append(code) # Adiciona

    return activation_codes


def get_betano_emails(email_address, password):
    try:
        # Convertendo bytes-like objects em strings UTF-8
        email_address = email_address.decode('utf-8')
        password = password.decode('utf-8')
    except UnicodeDecodeError as e:
        print("Erro ao decodificar bytes-like objects:", e)
        return None  # Retorna None se houver um erro de decodificação

    # Configurações de conexão com o servidor IMAP do Outlook
    imap_server = 'outlook.office365.com'
    imap_port = 993

    try:
        # Conectando-se ao servidor IMAP
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
 
        # Selecionando a caixa de entrada
        mail.select('Inbox')

        result, data = mail.search(None, 'FROM', 'suporte@betano.com')

        activation_codes_in_emails = []
        if result == 'OK':
            # A variável "data" conterá uma string com os números dos e-mails correspondentes
            email_numbers = data[0].split()
            for num in email_numbers:
                # Recuperando o e-mail bruto
                result, data = mail.fetch(num, '(RFC822)')
                if result == 'OK':
                    # Parseando o e-mail bruto
                    raw_email = data[0][1]
                    # Criando objeto EmailMessage
                    msg = email.message_from_bytes(raw_email)
                    # Extraindo o conteúdo do e-mail como uma string
                    email_content = msg.get_payload()
                    # Extraindo os códigos de ativação do conteúdo do e-mail
                    activation_codes = extract_activation_code(email_content)
                    # Adicionando os códigos de ativação encontrados à lista
                    activation_codes_in_emails.extend(activation_codes)

        # Fechando a conexão com o servidor IMAP
        mail.close()
        mail.logout()

    except Exception as e:
        print("Erro durante a conexão com o servidor IMAP:", e)
        return None  # Retorna None se houver um erro durante a conexão

    return activation_codes_in_emails if activation_codes_in_emails else None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_code', methods=['POST'])
def get_emails(): 
    email_address = request.form['email']
    password = request.form['password']
    email_titles = get_betano_emails(email_address.encode('utf-8'), password.encode('utf-8'))
    if email_titles:
        # Assumindo que você quer exibir apenas o primeiro código encontrado
        code = email_titles[0]
        # Supondo que você recebeu o nome do usuário como 'username'
        username = request.form.get('username')
        return render_template('get_code.html', code=code, username=username)
    else:
        return jsonify({"message": "Nenhum e-mail da Betano encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True)
