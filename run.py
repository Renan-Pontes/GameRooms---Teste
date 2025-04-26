import os
from dotenv import load_dotenv
from app import create_app, socketio

# Carregar variáveis de ambiente
load_dotenv()

# Criar a aplicação usando a factory
app = create_app()

# Se este arquivo for executado diretamente, inicie o servidor
if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Iniciando servidor no endereço {host}:{port}...")
    print(f"Para acessar de outros dispositivos na mesma rede, use o IP local do servidor")
    
    # Removi o parâmetro allow_unsafe_werkzeug que estava causando o erro
    socketio.run(app, 
                host=host, 
                port=port, 
                debug=app.config.get('DEBUG', True))