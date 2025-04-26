/**
 * Script principal do Jogo na TV
 */

// Aguardar o carregamento completo do DOM
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips (Bootstrap)
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers (Bootstrap)
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-fechar alertas após 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Converter campos de código de sala para maiúsculas
    var roomCodeInputs = document.querySelectorAll('input[name="room_code"]');
    roomCodeInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    });
});

/**
 * Gera um ID único (para uso temporário)
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * Copia texto para a área de transferência
 * @param {string} text - Texto a ser copiado
 * @param {Element} button - Botão que foi clicado (opcional)
 */
function copyToClipboard(text, button) {
    // Cria um elemento temporário
    var temp = document.createElement('textarea');
    temp.value = text;
    document.body.appendChild(temp);
    
    // Seleciona e copia o texto
    temp.select();
    document.execCommand('copy');
    
    // Remove o elemento temporário
    document.body.removeChild(temp);
    
    // Feedback visual (se um botão foi fornecido)
    if (button) {
        var originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-2"></i>Copiado!';
        button.classList.add('btn-success');
        button.classList.remove('btn-primary');
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
        }, 2000);
    }
}

/**
 * Exibe uma notificação temporária
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo de notificação ('success', 'error', 'warning', 'info')
 * @param {number} duration - Duração em milissegundos (padrão: 3000)
 */
function showNotification(message, type, duration) {
    // Configuração padrão
    type = type || 'info';
    duration = duration || 3000;
    
    // Cria o elemento de notificação
    var notification = document.createElement('div');
    notification.className = 'notification notification-' + type;
    
    // Ícone baseado no tipo
    var icon = '';
    switch (type) {
        case 'success':
            icon = '<i class="fas fa-check-circle me-2"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-exclamation-circle me-2"></i>';
            break;
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle me-2"></i>';
            break;
        default:
            icon = '<i class="fas fa-info-circle me-2"></i>';
    }
    
    // Define o conteúdo
    notification.innerHTML = icon + message;
    
    // Adiciona ao corpo do documento
    document.body.appendChild(notification);
    
    // Anima a entrada
    setTimeout(function() {
        notification.classList.add('show');
    }, 10);
    
    // Remove após a duração especificada
    setTimeout(function() {
        notification.classList.remove('show');
        setTimeout(function() {
            document.body.removeChild(notification);
        }, 300);
    }, duration);
}