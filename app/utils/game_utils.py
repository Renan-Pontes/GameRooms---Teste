import json
import os
import random
from pathlib import Path

# Diretório onde os dados dos jogos serão armazenados
GAMES_DATA_DIR = Path(__file__).parent.parent / 'data' / 'games'

def get_available_games():
    """
    Retorna a lista de jogos disponíveis
    
    Returns:
        Uma lista de dicionários com informações sobre os jogos
    """
    games = [
        {
            'id': 'trivia',
            'name': 'Quiz de Conhecimentos',
            'description': 'Responda perguntas de conhecimentos gerais',
            'min_players': 2,
            'max_players': 8,
            'icon': 'quiz_icon.png'
        },
        {
            'id': 'word_game',
            'name': 'Jogo de Palavras',
            'description': 'Adivinhe a palavra com base nas dicas',
            'min_players': 2,
            'max_players': 6,
            'icon': 'words_icon.png'
        },
        {
            'id': 'drawing',
            'name': 'Desenho & Adivinhação',
            'description': 'Um jogador desenha, os outros adivinham',
            'min_players': 3,
            'max_players': 8,
            'icon': 'drawing_icon.png'
        }
    ]
    
    return games

def load_game_data(game_id):
    """
    Carrega os dados de um jogo específico
    
    Args:
        game_id: Identificador do jogo
        
    Returns:
        Um dicionário com os dados do jogo ou None se o jogo não existir
    """
    try:
        file_path = GAMES_DATA_DIR / f"{game_id}.json"
        
        # Se o arquivo existir, carrega os dados
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Caso contrário, retorna dados de demonstração
        # Em produção, você teria arquivos JSON reais para cada jogo
        if game_id == 'trivia':
            return {
                'name': 'Quiz de Conhecimentos',
                'questions': [
                    {
                        'text': 'Qual é a capital do Brasil?',
                        'options': ['Rio de Janeiro', 'São Paulo', 'Brasília', 'Salvador'],
                        'correct': 2  # Índice da resposta correta (Brasília)
                    },
                    {
                        'text': 'Qual é o maior planeta do sistema solar?',
                        'options': ['Terra', 'Marte', 'Júpiter', 'Saturno'],
                        'correct': 2  # Júpiter
                    },
                    # Mais perguntas seriam adicionadas aqui
                ]
            }
        
        # Adicione mais jogos conforme necessário
        
        return None
    except Exception as e:
        print(f"Erro ao carregar dados do jogo {game_id}: {e}")
        return None

def initialize_game_state(game_id, players):
    """
    Inicializa o estado de um jogo
    
    Args:
        game_id: Identificador do jogo
        players: Dicionário de jogadores {player_id: player_name}
        
    Returns:
        Um dicionário com o estado inicial do jogo
    """
    game_data = load_game_data(game_id)
    
    if game_id == 'trivia':
        # Escolhe perguntas aleatórias para o jogo
        questions = random.sample(game_data['questions'], min(5, len(game_data['questions'])))
        
        return {
            'game_id': game_id,
            'current_round': 0,
            'total_rounds': len(questions),
            'questions': questions,
            'current_question': questions[0],
            'answers': {},  # Será preenchido com as respostas dos jogadores
            'scores': {player_id: 0 for player_id in players},
            'players': players,
            'status': 'waiting_for_answers'
        }
    
    elif game_id == 'word_game':
        # Lógica para inicializar o jogo de palavras
        # ...
        pass
    
    elif game_id == 'drawing':
        # Lógica para inicializar o jogo de desenho
        # ...
        pass
    
    # Estado genérico caso o jogo não seja reconhecido
    return {
        'game_id': game_id,
        'players': players,
        'status': 'not_implemented'
    }