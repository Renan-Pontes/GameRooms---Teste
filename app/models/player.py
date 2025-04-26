import uuid
from datetime import datetime

class Player:
    """
    Representa um jogador no sistema
    """
    
    def __init__(self, player_id=None, name=None):
        """
        Inicializa um novo jogador
        
        Args:
            player_id: ID do jogador (gera automaticamente se None)
            name: Nome do jogador
        """
        self.id = player_id if player_id else str(uuid.uuid4())
        self.name = name
        self.room_code = None
        self.is_connected = True
        self.joined_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_host = False
        self.score = 0
        
    def to_dict(self):
        """
        Converte o objeto para um dicionário
        
        Returns:
            Dicionário com os dados do jogador
        """
        return {
            'id': self.id,
            'name': self.name,
            'is_host': self.is_host,
            'score': self.score,
            'is_connected': self.is_connected
        }
    
    def update_activity(self):
        """
        Atualiza o timestamp da última atividade do jogador
        """
        self.last_activity = datetime.now()
    
    def join_room(self, room_code, is_host=False):
        """
        Adiciona o jogador a uma sala
        
        Args:
            room_code: Código da sala
            is_host: True se o jogador for o host da sala
        """
        self.room_code = room_code
        self.is_host = is_host
        self.update_activity()
    
    def leave_room(self):
        """
        Remove o jogador da sala atual
        """
        self.room_code = None
        self.is_host = False
        self.update_activity()
    
    def set_score(self, score):
        """
        Define a pontuação do jogador
        
        Args:
            score: Nova pontuação
        """
        self.score = score
        self.update_activity()
    
    def add_score(self, points):
        """
        Adiciona pontos à pontuação do jogador
        
        Args:
            points: Pontos a serem adicionados
        """
        self.score += points
        self.update_activity()
    
    def reset_score(self):
        """
        Zera a pontuação do jogador
        """
        self.score = 0
        self.update_activity()