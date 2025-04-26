from flask import Flask
from flask_socketio import SocketIO

# Criar a instância SocketIO fora da função factory
socketio = SocketIO()

def create_app(test_config=None):
    """Função factory para criar a aplicação Flask"""
    # Criar e configurar a aplicação
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Configurações padrão
    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG=True,
    )
    
    if test_config is None:
        # Carregar configurações da instância, se existir
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Carregar as configurações de teste passadas como parâmetro
        app.config.from_mapping(test_config)
    
    # Inicializar extensions
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Registrar blueprints
    from app.routes.main_routes import main_bp
    from app.routes.tv_routes import tv_bp
    from app.routes.mobile_routes import mobile_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(tv_bp, url_prefix='/tv')
    app.register_blueprint(mobile_bp, url_prefix='/mobile')
    
    # Importar eventos do Socket.IO
    from app.socket_events import room_events, game_events
    
    return app