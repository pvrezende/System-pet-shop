import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações do Banco de Dados
DATABASE = {
    'name': 'petshop.db',
    'path': BASE_DIR / 'petshop.db'
}

# Configurações da Aplicação
APP_CONFIG = {
    'name': 'System Pet Shop',
    'version': '2.0.0',
    'company': 'Pet Systems',
    'window_title': '🐾 Sistema System  Pet Shop',
    'min_width': 1200,
    'min_height': 700
}

# Configurações de Estoque
ESTOQUE_CONFIG = {
    'alerta_minimo': 5,  # Alerta quando estoque <= 5
    'alerta_critico': 2   # Alerta crítico quando estoque <= 2
}

# Configurações de Relatórios
REPORT_CONFIG = {
    'export_dir': BASE_DIR / 'relatorios',
    'backup_dir': BASE_DIR / 'backups'
}

# Criar diretórios se não existirem
REPORT_CONFIG['export_dir'].mkdir(exist_ok=True)
REPORT_CONFIG['backup_dir'].mkdir(exist_ok=True)

# Tipos de animais válidos
TIPOS_ANIMAIS = ['gato', 'cão']

# Formas de pagamento
FORMAS_PAGAMENTO = [
    'Dinheiro',
    'Débito',
    'Crédito à Vista',
    'Crédito Parcelado',
    'PIX',
    'Boleto'
]

# Configurações de UI
UI_CONFIG = {
    'colors': {
        'primary': '#2C3E50',
        'secondary': '#3498DB',
        'success': '#27AE60',
        'warning': '#F39C12',
        'danger': '#E74C3C',
        'info': '#1ABC9C'
    },
    'fonts': {
        'family': 'Segoe UI',
        'size_small': 9,
        'size_normal': 10,
        'size_large': 12,
        'size_title': 14
    }
}