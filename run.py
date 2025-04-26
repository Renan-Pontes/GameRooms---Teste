import os
from dotenv import load_dotenv
import eventlet
from datetime import datetime
from app import create_app, socketio

# Carregar variáveis de ambiente
load_dotenv()

# Criar a aplicação usando a factory
app = create_app()

# Função para limpar jogadores desconectados
def cleanup_disconnected_players():
    from app.models.room import Room
    
    while True:
        # Limpa jogadores desconectados em cada sala
        for room in Room.active_rooms.values():
            room.cleanup_disconnected_players()
        
        # Limpa salas inativas
        Room.cleanup_inactive_rooms()
        
        # Aguarda 1 minuto antes da próxima verificação
        eventlet.sleep(60)

# Se este arquivo for executado diretamente, inicie o servidor
if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Iniciando servidor no endereço {host}:{port}...")
    print(f"Para acessar de outros dispositivos na mesma rede, use o IP local do servidor")
    
    # Inicia a tarefa de limpeza de jogadores desconectados
    eventlet.spawn(cleanup_disconnected_players)
    
    # Inicia o servidor
    socketio.run(app, 
                host=host, 
                port=port, 
                debug=app.config.get('DEBUG', True))