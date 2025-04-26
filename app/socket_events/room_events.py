from flask import session, request
from flask_socketio import emit, join_room, leave_room
from app import socketio
from app.models.room import Room
from app.utils.session_utils import get_current_player_id, get_current_room_code

@socketio.on('connect')
def handle_connect():
    """Manipula a conexão inicial do cliente ao servidor WebSocket"""
    print(f"Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Manipula a desconexão do cliente"""
    player_id = get_current_player_id()
    room_code = get_current_room_code()
    
    if not player_id or not room_code:
        return
    
    print(f"Cliente desconectado: {request.sid}, player_id: {player_id}, room: {room_code}")
    
    # Busca a sala e remove o jogador
    room = Room.get_by_code(room_code)
    if room:
        # Verifica se o jogador está na sala
        if player_id in room.players:
            # Remove o jogador da sala
            is_host = room.host_id == player_id
            new_host_id = room.remove_player(player_id)
            
            # Notifica os outros jogadores
            leave_room(room_code)
            emit('player_left', {
                'player_id': player_id,
                'players': room.players,
                'host_changed': is_host,
                'new_host_id': new_host_id
            }, to=room_code)

@socketio.on('join_room')
def handle_join_room(data):
    """
    Manipula a entrada de um jogador em uma sala
    
    Args:
        data: Dicionário com room_code, player_id, player_name
    """
    room_code = data.get('room_code')
    player_id = data.get('player_id')
    player_name = data.get('player_name')
    
    if not room_code or not player_id or not player_name:
        emit('error', {'message': 'Dados incompletos'})
        return
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room:
        emit('error', {'message': 'Sala não encontrada'})
        return
    
    # Adiciona o jogador à sala
    success = room.add_player(player_id, player_name)
    if not success:
        emit('error', {'message': 'Não foi possível entrar na sala'})
        return
    
    # Inscreve o cliente na sala do Socket.IO
    join_room(room_code)
    
    # Notifica todos os jogadores na sala
    emit('player_joined', {
        'player_id': player_id,
        'player_name': player_name,
        'players': room.players,
        'host_id': room.host_id,
        'game_in_progress': room.game_state is not None
    }, to=room_code)
    
    # Envia o estado atual do jogo para o jogador (se existir)
    if room.game_state:
        emit('game_state', room.game_state)

@socketio.on('leave_room')
def handle_leave_room(data):
    """
    Manipula a saída voluntária de um jogador da sala
    
    Args:
        data: Dicionário com room_code e player_id
    """
    room_code = data.get('room_code')
    player_id = data.get('player_id')
    
    if not room_code or not player_id:
        return
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room:
        return
    
    # Remove o jogador da sala
    is_host = room.host_id == player_id
    new_host_id = room.remove_player(player_id)
    
    # Notifica os outros jogadores
    leave_room(room_code)
    emit('player_left', {
        'player_id': player_id,
        'players': room.players,
        'host_changed': is_host,
        'new_host_id': new_host_id
    }, to=room_code)