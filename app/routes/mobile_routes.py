from flask import Blueprint, render_template, abort, redirect, url_for, session, jsonify
from app.models.room import Room
from app.utils.session_utils import get_current_player_id, get_current_room_code, is_host
from app.utils.game_utils import get_available_games

# Criar blueprint
mobile_bp = Blueprint('mobile', __name__)

@mobile_bp.route('/room/<code>')
def room_controller(code):
    """
    Rota principal para a interface do celular
    
    Args:
        code: Código da sala
    """
    # Verifica se o jogador está autenticado
    player_id = get_current_player_id()
    if not player_id:
        # Redireciona para a página de entrada na sala
        return redirect(url_for('main.join_room'))
    
    # Verifica se o código da sala na URL corresponde ao da sessão
    session_room_code = get_current_room_code()
    if session_room_code != code:
        # Redireciona para a sala correta
        if session_room_code:
            return redirect(url_for('mobile.room_controller', code=session_room_code))
        else:
            return redirect(url_for('main.join_room'))
    
    # Verifica se a sala existe
    room = Room.get_by_code(code)
    if not room:
        abort(404, description="Sala não encontrada")
    
    # Verifica se a sala está ativa
    if not room.is_active:
        abort(410, description="Esta sala não está mais ativa")
    
    # Verifica se o jogador está na sala
    if player_id not in room.players:
        # Redireciona para a entrada na sala
        return redirect(url_for('main.join_room'))
    
    # Determina se o jogador é o host
    is_player_host = room.host_id == player_id
    
    # Renderiza a interface do celular
    return render_template('mobile/controller.html', 
                          room=room,
                          player_id=player_id,
                          player_name=room.players[player_id],
                          is_host=is_player_host,
                          available_games=get_available_games())

@mobile_bp.route('/api/games')
def get_games():
    """API para listar jogos disponíveis"""
    return jsonify({
        'success': True,
        'games': get_available_games()
    })

@mobile_bp.route('/api/player-info')
def player_info():
    """API para obter informações do jogador atual"""
    # Verifica se o jogador está autenticado
    player_id = get_current_player_id()
    room_code = get_current_room_code()
    
    if not player_id or not room_code:
        return jsonify({
            'success': False,
            'error': 'Jogador não autenticado'
        }), 401
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room:
        return jsonify({
            'success': False,
            'error': 'Sala não encontrada'
        }), 404
    
    # Verifica se o jogador está na sala
    if player_id not in room.players:
        return jsonify({
            'success': False,
            'error': 'Jogador não está na sala'
        }), 403
    
    # Retorna as informações do jogador
    return jsonify({
        'success': True,
        'data': {
            'player_id': player_id,
            'player_name': room.players[player_id],
            'room_code': room_code,
            'is_host': room.host_id == player_id,
            'score': room.player_scores.get(player_id, 0)
        }
    })

@mobile_bp.route('/game-controls/<game_id>')
def game_controls(game_id):
    """
    Renderiza os controles específicos para um jogo
    
    Args:
        game_id: Identificador do jogo
    """
    # Verifica se o jogador está autenticado
    player_id = get_current_player_id()
    room_code = get_current_room_code()
    
    if not player_id or not room_code:
        abort(401, description="Não autenticado")
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room:
        abort(404, description="Sala não encontrada")
    
    # Verifica se o jogador está na sala
    if player_id not in room.players:
        abort(403, description="Você não está nesta sala")
    
    # Renderiza os controles específicos do jogo
    template_name = f'mobile/games/{game_id}_controls.html'
    
    return render_template(template_name,
                          room=room,
                          player_id=player_id,
                          player_name=room.players[player_id],
                          is_host=room.host_id == player_id)