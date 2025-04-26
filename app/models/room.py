import uuid
from datetime import datetime
from app.utils.room_code import generate_room_code

class Room:
    """
    Representa uma sala de jogo
    """
    
    # Dicionário para armazenar todas as salas ativas
    # Chave: código da sala, Valor: instância da sala
    active_rooms = {}
    
    def __init__(self, host_id, host_name):
        """
        Inicializa uma nova sala
        
        Args:
            host_id: ID do jogador host
            host_name: Nome do jogador host
        """
        self.id = str(uuid.uuid4())  # ID interno da sala
        self.code = generate_room_code()  # Código público da sala (para acesso)
        self.host_id = host_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.players = {host_id: host_name}  # Dicionário de jogadores {id: nome}
        self.player_scores = {host_id: 0}  # Pontuações dos jogadores
        self.disconnected_players = {}  # Jogadores desconectados {id: {'name': nome, 'time': timestamp, 'is_host': bool}}
        self.selected_game = None  # Jogo selecionado pelo host
        self.game_state = None  # Estado atual do jogo
        self.is_active = True
        
        # Adiciona a sala ao dicionário de salas ativas
        Room.active_rooms[self.code] = self
    
    @classmethod
    def get_by_code(cls, code):
        """
        Busca uma sala pelo código
        
        Args:
            code: Código da sala
            
        Returns:
            Instância da sala ou None se não encontrada
        """
        return cls.active_rooms.get(code)
    
    @classmethod
    def exists(cls, code):
        """
        Verifica se uma sala existe
        
        Args:
            code: Código da sala
            
        Returns:
            True se a sala existir, False caso contrário
        """
        return code in cls.active_rooms
    
    @classmethod
    def cleanup_inactive_rooms(cls, max_age_minutes=120):
        """
        Remove salas inativas
        
        Args:
            max_age_minutes: Tempo máximo de inatividade em minutos
        """
        now = datetime.now()
        rooms_to_remove = []
        
        for code, room in cls.active_rooms.items():
            # Calcula o tempo de inatividade
            inactive_time = (now - room.last_activity).total_seconds() / 60
            
            # Se a sala estiver inativa por muito tempo, marca para remoção
            if inactive_time > max_age_minutes:
                rooms_to_remove.append(code)
        
        # Remove as salas marcadas
        for code in rooms_to_remove:
            del cls.active_rooms[code]
    
    def update_activity(self):
        """
        Atualiza o timestamp da última atividade da sala
        """
        self.last_activity = datetime.now()
    
    def add_player(self, player_id, player_name):
        """
        Adiciona um jogador à sala
        
        Args:
            player_id: ID do jogador
            player_name: Nome do jogador
            
        Returns:
            True se o jogador foi adicionado, False caso contrário
        """
        # Verifica se a sala está ativa
        if not self.is_active:
            return False
        
        # Verifica se o jogo já começou (não permite novos jogadores)
        if self.game_state and self.game_state.get('status') != 'waiting':
            return False
        
        # Adiciona o jogador
        self.players[player_id] = player_name
        
        # Inicializa a pontuação do jogador
        self.player_scores[player_id] = 0
        
        # Atualiza o timestamp da última atividade
        self.update_activity()
        
        return True
    
    def remove_player(self, player_id):
        """
        Remove um jogador da sala
        
        Args:
            player_id: ID do jogador
            
        Returns:
            ID do novo host se o host foi removido, None caso contrário
        """
        # Verifica se o jogador está na sala
        if player_id not in self.players:
            return None
        
        # Remove o jogador
        del self.players[player_id]
        
        # Remove a pontuação do jogador
        if player_id in self.player_scores:
            del self.player_scores[player_id]
        
        # Atualiza o timestamp da última atividade
        self.update_activity()
        
        # Se não houver mais jogadores, desativa a sala
        if not self.players:
            self.close()
            return None
        
        # Se o host foi removido, escolhe um novo host
        if player_id == self.host_id:
            # Escolhe o primeiro jogador disponível como novo host
            new_host_id = next(iter(self.players.keys()))
            self.host_id = new_host_id
            return new_host_id
        
        return None
    
    def close(self):
        """
        Fecha a sala
        """
        self.is_active = False
        
        # Remove a sala do dicionário de salas ativas
        if self.code in Room.active_rooms:
            del Room.active_rooms[self.code]
    
    def start_game(self, game_id, initial_state):
        """
        Inicia um jogo na sala
        
        Args:
            game_id: ID do jogo
            initial_state: Estado inicial do jogo
            
        Returns:
            True se o jogo foi iniciado, False caso contrário
        """
        # Verifica se a sala está ativa
        if not self.is_active:
            return False
        
        # Verifica se há jogadores suficientes
        if len(self.players) < 2:
            return False
        
        # Define o jogo selecionado
        self.selected_game = game_id
        
        # Define o estado inicial do jogo
        self.game_state = initial_state
        
        # Atualiza o timestamp da última atividade
        self.update_activity()
        
        return True
    
    def end_game(self):
        """
        Encerra o jogo atual
        """
        self.game_state = None
        self.update_activity()
    
    def update_game_state(self, new_state):
        """
        Atualiza o estado do jogo
        
        Args:
            new_state: Novo estado do jogo
        """
        self.game_state = new_state
        self.update_activity()
    
    def to_dict(self):
        """
        Converte o objeto para um dicionário
        
        Returns:
            Dicionário com os dados da sala
        """
        return {
            'id': self.id,
            'code': self.code,
            'host_id': self.host_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'players': self.players,
            'player_scores': self.player_scores,
            'selected_game': self.selected_game,
            'game_state': self.game_state,
            'is_active': self.is_active
        }
    
    def mark_player_disconnected(self, player_id):
        """
        Marca um jogador como desconectado
        
        Args:
            player_id: ID do jogador
            
        Returns:
            True se o jogador foi marcado como desconectado, False caso contrário
        """
        # Verifica se o jogador está na sala
        if player_id not in self.players:
            return False
        
        # Marca o jogador como desconectado
        self.disconnected_players[player_id] = {
            'name': self.players[player_id],
            'time': datetime.now(),
            'is_host': self.host_id == player_id,
            'score': self.player_scores.get(player_id, 0)
        }
        
        # Atualiza o timestamp da última atividade
        self.update_activity()
        
        return True
    
    def reconnect_player(self, old_player_id, new_player_id, player_name):
        """
        Reconecta um jogador que havia sido desconectado
        
        Args:
            old_player_id: ID antigo do jogador
            new_player_id: Novo ID do jogador
            player_name: Nome do jogador
            
        Returns:
            True se o jogador foi reconectado, False caso contrário
        """
        # Verifica se o jogador está na lista de desconectados
        if old_player_id not in self.disconnected_players:
            return False
        
        # Obtém as informações do jogador desconectado
        player_info = self.disconnected_players.pop(old_player_id)
        
        # Adiciona o jogador com o novo ID
        self.players[new_player_id] = player_name
        
        # Transfere a pontuação
        self.player_scores[new_player_id] = player_info.get('score', 0)
        
        # Se o jogador era o host, atualiza o host_id
        if player_info['is_host']:
            self.host_id = new_player_id
        
        # Atualiza o timestamp da última atividade
        self.update_activity()
        
        return True
    
    def update_player_name(self, player_id, new_name):
        """
        Atualiza o nome de um jogador na sala
        
        Args:
            player_id: ID do jogador
            new_name: Novo nome do jogador
            
        Returns:
            True se o nome foi atualizado, False caso contrário
        """
        # Verifica se o jogador está na sala
        if player_id not in self.players:
            return False
        
        # Verifica se o novo nome já está em uso por outro jogador
        for pid, name in self.players.items():
            if pid != player_id and name == new_name:
                return False
        
        # Atualiza o nome do jogador
        self.players[player_id] = new_name
        
        # Atualiza o timestamp da última atividade
        self.update_activity()
        
        return True
    
    def cleanup_disconnected_players(self, max_age_minutes=5):
        """
        Remove jogadores desconectados que não se reconectaram após um determinado tempo
        
        Args:
            max_age_minutes: Tempo máximo de desconexão em minutos
        """
        now = datetime.now()
        players_to_remove = []
        
        for player_id, info in self.disconnected_players.items():
            # Calcula o tempo de desconexão
            disconnect_time = info['time']
            disconnect_duration = (now - disconnect_time).total_seconds() / 60
            
            # Se o jogador estiver desconectado por muito tempo, marca para remoção
            if disconnect_duration > max_age_minutes:
                players_to_remove.append(player_id)
        
        # Remove os jogadores marcados
        for player_id in players_to_remove:
            # Remove o jogador da lista de desconectados
            info = self.disconnected_players.pop(player_id)
            
            # Remove o jogador da sala
            if player_id in self.players:
                del self.players[player_id]
                
                # Remove a pontuação do jogador
                if player_id in self.player_scores:
                    del self.player_scores[player_id]
                
                # Se o jogador for o host, escolhe um novo host
                if info['is_host'] and self.host_id == player_id:
                    # Escolhe o primeiro jogador disponível como novo host
                    if self.players:
                        new_host_id = next(iter(self.players.keys()))
                        self.host_id = new_host_id
                    else:
                        # Se não houver mais jogadores, fecha a sala
                        self.close()
        
        # Atualiza o timestamp da última atividade
        self.update_activity()