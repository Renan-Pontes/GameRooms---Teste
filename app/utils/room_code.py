import random
import string

def generate_room_code(length=6):
    """
    Gera um código de sala único aleatório.
    
    Args:
        length: Comprimento do código (padrão: 6)
        
    Returns:
        Um código de sala alfanumérico (letras maiúsculas e números)
    """
    chars = string.ascii_uppercase + string.digits
    
    # Gera um código e verifica se já existe
    # Nota: A verificação real dependerá da nossa implementação de Room
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        
        # Importar aqui para evitar importações circulares
        from app.models.room import Room
        
        # Se o código não existir, retorna-o
        if not Room.exists(code):
            return code

def validate_room_code(code):
    """
    Verifica se um código de sala é válido (formato correto)
    
    Args:
        code: Código de sala a ser validado
        
    Returns:
        True se o código tiver o formato válido, False caso contrário
    """
    # Verifica se o código contém apenas letras maiúsculas e números
    if not code:
        return False
    
    # Verifica o comprimento (assumindo que estamos usando 6 caracteres)
    if len(code) != 6:
        return False
    
    # Verifica se contém apenas caracteres válidos (letras maiúsculas e números)
    valid_chars = set(string.ascii_uppercase + string.digits)
    return all(c in valid_chars for c in code)