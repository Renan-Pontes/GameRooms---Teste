from flask import Blueprint, render_template, abort, jsonify
from app.models.room import Room
from app.utils.game_utils import get_available_games

# Criar blueprint
tv_bp = Blueprint('tv', __name__)

@tv_bp.route('/display/<code>')
def display(code):
    """
    Rota para a interface de TV que exibe o jogo
    
    Args:
        code: Código da sala
    """
    # Verifica se a sala existe
    room = Room.get_by_code(code)
    if not room:
        abort(404, description="Sala não encontrada")
    
    # Verifica se a sala está ativa
    if not room.is_active:
        abort(410, description="Esta sala não está mais ativa")
    
    # Renderiza a página da TV
    return render_template('tv/display.html', 
                          room=room, 
                          available_games=get_available_games())

@tv_bp.route('/api/room/<code>')
def room_status(code):
    """
    API para obter o status atual da sala
    
    Args:
        code: Código da sala
    """
    # Verifica se a sala existe
    room = Room.get_by_code(code)
    if not room:
        return jsonify({
            'success': False,
            'error': 'Sala não encontrada'
        }), 404
    
    # Retorna os dados da sala
    return jsonify({
        'success': True,
        'data': {
            'code': room.code,
            'host_id': room.host_id,
            'players': room.players,
            'player_scores': room.player_scores,
            'selected_game': room.selected_game,
            'game_in_progress': room.game_state is not None,
            'is_active': room.is_active
        }
    })

@tv_bp.route('/qr/<code>')
def qr_code(code):
    """
    Rota para exibir um QR code para entrar na sala
    
    Args:
        code: Código da sala
    """
    # Verifica se a sala existe
    room = Room.get_by_code(code)
    if not room:
        abort(404, description="Sala não encontrada")
    
    # Renderiza a página do QR code
    return render_template('tv/qr_code.html', room=room)