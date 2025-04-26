from flask import session
from flask_socketio import emit
from app import socketio
from app.models.room import Room
from app.utils.session_utils import get_current_player_id, get_current_room_code, is_host
from app.utils.game_utils import initialize_game_state, get_available_games

@socketio.on('select_game')
def handle_select_game(data):
    """
    Manipula a seleção de um jogo pelo host
    
    Args:
        data: Dicionário com game_id
    """
    room_code = get_current_room_code()
    player_id = get_current_player_id()
    game_id = data.get('game_id')
    
    if not room_code or not player_id or not game_id:
        emit('error', {'message': 'Dados incompletos'})
        return
    
    # Verifica se o jogador é o host
    if not is_host():
        emit('error', {'message': 'Apenas o líder pode selecionar o jogo'})
        return
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room:
        emit('error', {'message': 'Sala não encontrada'})
        return
    
    # Verifica se o jogador é realmente o host da sala
    if room.host_id != player_id:
        emit('error', {'message': 'Você não é o líder desta sala'})
        return
    
    # Atualiza o tipo de jogo selecionado
    room.selected_game = game_id
    
    # Notifica todos os jogadores sobre a seleção do jogo
    emit('game_selected', {
        'game_id': game_id,
        'game_info': next((g for g in get_available_games() if g['id'] == game_id), None)
    }, to=room_code)

@socketio.on('start_game')
def handle_start_game():
    """
    Manipula o início do jogo pelo host
    """
    room_code = get_current_room_code()
    player_id = get_current_player_id()
    
    if not room_code or not player_id:
        emit('error', {'message': 'Dados incompletos'})
        return
    
    # Verifica se o jogador é o host
    if not is_host():
        emit('error', {'message': 'Apenas o líder pode iniciar o jogo'})
        return
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room:
        emit('error', {'message': 'Sala não encontrada'})
        return
    
    # Verifica se o jogador é realmente o host da sala
    if room.host_id != player_id:
        emit('error', {'message': 'Você não é o líder desta sala'})
        return
    
    # Verifica se um jogo foi selecionado
    if not room.selected_game:
        emit('error', {'message': 'Nenhum jogo selecionado'})
        return
    
    # Inicializa o estado do jogo
    room.game_state = initialize_game_state(room.selected_game, room.players)
    
    # Notifica todos os jogadores sobre o início do jogo
    emit('game_started', room.game_state, to=room_code)

@socketio.on('game_action')
def handle_game_action(data):
    """
    Manipula uma ação de jogo de um jogador
    
    Args:
        data: Dicionário com informações da ação (depende do jogo)
    """
    room_code = get_current_room_code()
    player_id = get_current_player_id()
    action = data.get('action')
    
    if not room_code or not player_id or not action:
        emit('error', {'message': 'Dados incompletos'})
        return
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room or not room.game_state:
        emit('error', {'message': 'Jogo não encontrado'})
        return
    
    # Verifica se o jogador está na sala
    if player_id not in room.players:
        emit('error', {'message': 'Você não está nesta sala'})
        return
    
    # Processa a ação de acordo com o tipo de jogo
    game_id = room.game_state.get('game_id')
    
    # Exemplo para jogo de Trivia
    if game_id == 'trivia':
        if action == 'answer':
            answer_index = data.get('answer_index')
            
            # Verifica se a resposta é válida
            if answer_index is None or not isinstance(answer_index, int):
                emit('error', {'message': 'Resposta inválida'})
                return
            
            # Adiciona a resposta ao estado do jogo
            if 'answers' not in room.game_state:
                room.game_state['answers'] = {}
            
            # Registra a resposta (apenas uma por jogador)
            room.game_state['answers'][player_id] = answer_index
            
            # Notifica todos sobre a nova resposta (sem revelar se está correta)
            emit('player_answered', {
                'player_id': player_id,
                'player_name': room.players[player_id]
            }, to=room_code)
            
            # Verifica se todos responderam
            if len(room.game_state['answers']) == len(room.players):
                # Verifica as respostas
                current_question = room.game_state['current_question']
                correct_index = current_question['correct']
                
                # Atualiza pontuações
                for pid, answer in room.game_state['answers'].items():
                    if answer == correct_index:
                        room.game_state['scores'][pid] += 10
                
                # Notifica resultados da rodada
                emit('round_results', {
                    'answers': room.game_state['answers'],
                    'correct_index': correct_index,
                    'scores': room.game_state['scores']
                }, to=room_code)
                
                # Avança para a próxima pergunta ou finaliza o jogo
                room.game_state['current_round'] += 1
                
                # Verifica se o jogo acabou
                if room.game_state['current_round'] >= room.game_state['total_rounds']:
                    # Jogo finalizado
                    room.game_state['status'] = 'game_over'
                    
                    # Encontra o vencedor
                    max_score = -1
                    winners = []
                    
                    for pid, score in room.game_state['scores'].items():
                        if score > max_score:
                            max_score = score
                            winners = [pid]
                        elif score == max_score:
                            winners.append(pid)
                    
                    # Notifica fim de jogo
                    emit('game_over', {
                        'winners': winners,
                        'final_scores': room.game_state['scores']
                    }, to=room_code)
                else:
                    # Próxima pergunta
                    room.game_state['current_question'] = room.game_state['questions'][room.game_state['current_round']]
                    room.game_state['answers'] = {}
                    room.game_state['status'] = 'waiting_for_answers'
                    
                    # Notifica nova pergunta
                    emit('new_question', {
                        'question': room.game_state['current_question']['text'],
                        'options': room.game_state['current_question']['options'],
                        'round': room.game_state['current_round'] + 1,
                        'total_rounds': room.game_state['total_rounds']
                    }, to=room_code)
    
    # Adicione lógica para outros tipos de jogos conforme necessário
    elif game_id == 'word_game':
        # Lógica para o jogo de palavras
        pass
    
    elif game_id == 'drawing':
        # Lógica para o jogo de desenho
        if action == 'draw':
            # Coordenadas do desenho
            x = data.get('x')
            y = data.get('y')
            color = data.get('color', '#000000')
            thickness = data.get('thickness', 2)
            
            # Envia as coordenadas para todos os jogadores
            emit('draw_update', {
                'player_id': player_id,
                'x': x,
                'y': y,
                'color': color,
                'thickness': thickness
            }, to=room_code)
        
        elif action == 'clear_canvas':
            # Limpa o canvas
            emit('clear_canvas', {
                'player_id': player_id
            }, to=room_code)
        
        elif action == 'guess':
            # Processa a tentativa de adivinhação
            guess = data.get('guess', '').strip().lower()
            correct_word = room.game_state.get('word', '').lower()
            
            # Verifica se a adivinhação está correta
            if guess == correct_word:
                # Atualiza a pontuação
                room.game_state['scores'][player_id] += 5
                
                # Notifica acerto
                emit('correct_guess', {
                    'player_id': player_id,
                    'player_name': room.players[player_id],
                    'word': correct_word,
                    'scores': room.game_state['scores']
                }, to=room_code)
                
                # Passa para a próxima rodada
                # (lógica adicional seria necessária)
            else:
                # Notifica tentativa incorreta
                emit('wrong_guess', {
                    'player_id': player_id,
                    'player_name': room.players[player_id],
                    'guess': guess
                }, to=room_code)

@socketio.on('end_game')
def handle_end_game():
    """
    Manipula o encerramento de um jogo pelo host
    """
    room_code = get_current_room_code()
    player_id = get_current_player_id()
    
    if not room_code or not player_id:
        return
    
    # Verifica se o jogador é o host
    if not is_host():
        emit('error', {'message': 'Apenas o líder pode encerrar o jogo'})
        return
    
    # Busca a sala
    room = Room.get_by_code(room_code)
    if not room:
        return
    
    # Verifica se o jogador é realmente o host da sala
    if room.host_id != player_id:
        emit('error', {'message': 'Você não é o líder desta sala'})
        return
    
    # Encerra o jogo
    room.game_state = None
    room.selected_game = None
    
    # Notifica todos os jogadores
    emit('game_ended', {'message': 'O jogo foi encerrado pelo líder'}, to=room_code)