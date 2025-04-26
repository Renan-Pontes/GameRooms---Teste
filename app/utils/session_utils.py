from flask import session, request
import uuid

def generate_player_id():
    """
    Gera um ID único para o jogador
    
    Returns:
        Uma string com o ID do jogador
    """
    return str(uuid.uuid4())

def get_current_player_id():
    """
    Obtém o ID do jogador atual da sessão
    
    Returns:
        ID do jogador ou None se não estiver autenticado
    """
    return session.get('player_id')

def get_current_room_code():
    """
    Obtém o código da sala atual da sessão
    
    Returns:
        Código da sala ou None se não estiver em uma sala
    """
    return session.get('room_code')

def is_host():
    """
    Verifica se o jogador atual é o host da sala
    
    Returns:
        True se o jogador for o host, False caso contrário
    """
    return session.get('is_host', False)

def set_player_session(player_id, player_name, room_code, is_host=False):
    """
    Define os dados da sessão do jogador
    
    Args:
        player_id: ID do jogador
        player_name: Nome do jogador
        room_code: Código da sala
        is_host: True se o jogador for o host da sala
    """
    session['player_id'] = player_id
    session['player_name'] = player_name
    session['room_code'] = room_code
    session['is_host'] = is_host

def clear_player_session():
    """
    Limpa os dados da sessão do jogador
    """
    session.pop('player_id', None)
    session.pop('player_name', None)
    session.pop('room_code', None)
    session.pop('is_host', None)

def get_client_ip():
    """
    Obtém o endereço IP do cliente
    
    Returns:
        Endereço IP do cliente
    """
    # Tenta obter o IP real se estiver atrás de um proxy
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.environ.get('REMOTE_ADDR')
    return ip