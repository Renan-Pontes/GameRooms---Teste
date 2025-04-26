from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models.room import Room
from app.utils.session_utils import (
    generate_player_id, 
    set_player_session, 
    clear_player_session, 
    get_current_player_id
)
from app.utils.room_code import validate_room_code

# Criar blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Rota para a página inicial"""
    # Limpa a sessão se o usuário estiver voltando para a página inicial
    if 'player_id' in session and 'room_code' in session:
        clear_player_session()
        
    return render_template('index.html')

@main_bp.route('/create', methods=['GET', 'POST'])
def create_room():
    """Rota para criar uma nova sala"""
    if request.method == 'POST':
        # Obtém o nome do jogador do formulário
        player_name = request.form.get('player_name', '').strip()
        
        # Valida o nome do jogador
        if not player_name:
            flash('Por favor, insira seu nome.', 'error')
            return render_template('create_room.html')
        
        # Gera um ID único para o jogador
        player_id = generate_player_id()
        
        # Cria uma nova sala
        room = Room(host_id=player_id, host_name=player_name)
        
        # Define os dados da sessão
        set_player_session(player_id, player_name, room.code, is_host=True)
        
        # Redireciona para a interface do celular com a nova sala
        return redirect(url_for('mobile.room_controller', code=room.code))
    
    # Se for uma requisição GET, exibe o formulário
    return render_template('create_room.html')

@main_bp.route('/join', methods=['GET', 'POST'])
def join_room():
    """Rota para entrar em uma sala existente"""
    if request.method == 'POST':
        # Obtém os dados do formulário
        player_name = request.form.get('player_name', '').strip()
        room_code = request.form.get('room_code', '').strip().upper()
        
        # Valida os dados
        if not player_name:
            flash('Por favor, insira seu nome.', 'error')
            return render_template('join_room.html')
            
        if not room_code:
            flash('Por favor, insira o código da sala.', 'error')
            return render_template('join_room.html')
        
        # Valida o formato do código da sala
        if not validate_room_code(room_code):
            flash('Código de sala inválido. Use letras maiúsculas e números.', 'error')
            return render_template('join_room.html')
        
        # Verifica se a sala existe
        room = Room.get_by_code(room_code)
        if not room:
            flash('Sala não encontrada. Verifique o código e tente novamente.', 'error')
            return render_template('join_room.html')
        
        # Verifica se a sala está ativa
        if not room.is_active:
            flash('Esta sala não está mais ativa.', 'error')
            return render_template('join_room.html')
        
        # Gera um ID único para o jogador
        player_id = generate_player_id()
        
        # Adiciona o jogador à sala
        success = room.add_player(player_id, player_name)
        if not success:
            flash('Não foi possível entrar na sala. O jogo já pode ter começado.', 'error')
            return render_template('join_room.html')
        
        # Define os dados da sessão
        set_player_session(player_id, player_name, room_code, is_host=False)
        
        # Redireciona para a interface do celular
        return redirect(url_for('mobile.room_controller', code=room_code))
    
    # Se for uma requisição GET, exibe o formulário
    return render_template('join_room.html')

@main_bp.route('/how-to-play')
def how_to_play():
    """Rota para a página de instruções"""
    return render_template('how_to_play.html')

@main_bp.route('/about')
def about():
    """Rota para a página Sobre"""
    return render_template('about.html')

@main_bp.route('/exit-room')
def exit_room():
    """Rota para sair de uma sala"""
    # Obtém os dados da sessão
    player_id = get_current_player_id()
    room_code = session.get('room_code')
    
    if player_id and room_code:
        # Busca a sala
        room = Room.get_by_code(room_code)
        if room:
            # Remove o jogador da sala
            room.remove_player(player_id)
    
    # Limpa a sessão
    clear_player_session()
    
    # Redireciona para a página inicial
    return redirect(url_for('main.index'))