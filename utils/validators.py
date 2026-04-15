import re
from typing import Optional, Tuple

def validar_cpf(cpf: str) -> bool:
    """Valida um CPF brasileiro"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    
    if digito1 != int(cpf[9]):
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    
    return digito2 == int(cpf[10])

def validar_telefone(telefone: str) -> bool:
    """Valida um telefone brasileiro (fixo ou celular)"""
    telefone = re.sub(r'\D', '', telefone)
    
    # Deve ter 10 dígitos (fixo) ou 11 dígitos (celular)
    if len(telefone) not in [10, 11]:
        return False
    
    # DDD válido (código de área)
    ddd = int(telefone[:2])
    if ddd < 11 or ddd > 99:
        return False
    
    return True

def validar_email(email: str) -> bool:
    """Valida um endereço de e-mail"""
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_preco(preco: float) -> Tuple[bool, str]:
    """Valida um preço"""
    if preco <= 0:
        return False, "Preço deve ser maior que zero"
    if preco > 999999.99:
        return False, "Preço muito alto"
    return True, ""

def validar_peso(peso: float) -> Tuple[bool, str]:
    """Valida um peso"""
    if peso <= 0:
        return False, "Peso deve ser maior que zero"
    if peso > 50:  # Limite de 50kg por embalagem
        return False, "Peso não pode exceder 50kg"
    return True, ""

def validar_estoque(estoque: int) -> Tuple[bool, str]:
    """Valida um valor de estoque"""
    if estoque < 0:
        return False, "Estoque não pode ser negativo"
    if estoque > 999999:
        return False, "Valor de estoque muito alto"
    return True, ""

def validar_desconto(desconto: float, valor_total: float) -> Tuple[bool, str]:
    """Valida um desconto"""
    if desconto < 0:
        return False, "Desconto não pode ser negativo"
    if desconto > valor_total:
        return False, "Desconto não pode ser maior que o valor total"
    if desconto > valor_total * 0.5:  # Máximo 50% de desconto
        return False, "Desconto máximo permitido: 50%"
    return True, ""