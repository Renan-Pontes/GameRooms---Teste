from flask import session, request
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
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
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if room:
        # Verifica se o jogador está na sala
        if player_id in room.players:
            # Marca o jogador como desconectado na sala
            is_host = room.host_id == player_id
            room.mark_player_disconnected(player_id)
            
            # Notifica os outros jogadores
            leave_room(room_code)
            emit('player_disconnected', {
                'player_id': player_id,
                'player_name': room.players[player_id],
                'players': room.players,
                'disconnected_players': list(room.disconnected_players.keys()),
                'host_id': room.host_id
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
    
    # Verifica se existe algum jogador desconectado com o mesmo nome
    reconnected = False
    for pid in list(room.disconnected_players.keys()):
        info = room.disconnected_players[pid]
        if info['name'] == player_name:
            # Reconecta o jogador
            reconnected = room.reconnect_player(pid, player_id, player_name)
            if reconnected:
                break
    
    # Se o jogador foi reconectado
    if reconnected:
        # Inscreve o cliente na sala do Socket.IO
        join_room(room_code)
        
        # Notifica todos os jogadores na sala
        emit('player_rejoined', {
            'player_id': player_id,
            'player_name': player_name,
            'players': room.players,
            'disconnected_players': list(room.disconnected_players.keys()),
            'host_id': room.host_id,
            'game_in_progress': room.game_state is not None
        }, to=room_code)
        
        # Envia o estado atual do jogo para o jogador (se existir)
        if room.game_state:
            emit('game_state', room.game_state)
        
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
        'disconnected_players': list(room.disconnected_players.keys()),
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

@socketio.on('update_nickname')
def handle_update_nickname(data):
    """
    Manipula a atualização de nickname de um jogador
    
    Args:
        data: Dicionário com room_code, player_id, new_nickname
    """
    room_code = data.get('room_code')
    player_id = data.get('player_id')
    new_nickname = data.get('new_nickname', '').strip()
    
    if not room_code or not player_id or not new_nickname:
        emit('error', {'message': 'Dados incompletos'})
        return
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room:
        emit('error', {'message': 'Sala não encontrada'})
        return
    
    # Verifica se o jogador está na sala
    if player_id not in room.players:
        emit('error', {'message': 'Jogador não encontrado na sala'})
        return
    
    # Armazena o nickname antigo
    old_nickname = room.players[player_id]
    
    # Atualiza o nickname do jogador
    success = room.update_player_name(player_id, new_nickname)
    if not success:
        emit('error', {'message': 'Não foi possível atualizar o nickname. Este nome pode já estar em uso.'})
        return
    
    # Atualiza a sessão do jogador
    session['player_name'] = new_nickname
    
    # Notifica todos os jogadores na sala
    emit('nickname_updated', {
        'player_id': player_id,
        'old_nickname': old_nickname,
        'new_nickname': new_nickname,
        'players': room.players,
        'host_id': room.host_id
    }, to=room_code)