from datetime import datetime
from typing import Optional

def formatar_cpf(cpf: str) -> str:
    """Formata CPF para exibição: 000.000.000-00"""
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def formatar_telefone(telefone: str) -> str:
    """Formata telefone para exibição: (00) 00000-0000 ou (00) 0000-0000"""
    telefone = ''.join(filter(str.isdigit, telefone))
    
    if len(telefone) == 11:  # Celular
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:  # Fixo
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone

def formatar_moeda(valor: float) -> str:
    """Formata valor para moeda brasileira: R$ 1.234,56"""
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def formatar_data(data: str, formato_entrada: str = "%Y-%m-%d %H:%M:%S", 
                 formato_saida: str = "%d/%m/%Y") -> str:
    """Formata data para exibição"""
    try:
        if isinstance(data, str):
            dt = datetime.strptime(data, formato_entrada)
        else:
            dt = data
        return dt.strftime(formato_saida)
    except:
        return data

def formatar_data_hora(data: str) -> str:
    """Formata data e hora para exibição: 01/01/2024 14:30"""
    return formatar_data(data, formato_saida="%d/%m/%Y %H:%M")

def formatar_peso(peso: float) -> str:
    """Formata peso para exibição: 10,5 kg"""
    return f"{peso:.1f} kg".replace('.', ',')

def limpar_cpf(cpf: str) -> str:
    """Remove formatação do CPF, deixando apenas números"""
    return ''.join(filter(str.isdigit, cpf))

def limpar_telefone(telefone: str) -> str:
    """Remove formatação do telefone, deixando apenas números"""
    return ''.join(filter(str.isdigit, telefone))

def formatar_percentual(valor: float) -> str:
    """Formata valor percentual: 15,5%"""
    return f"{valor:.1f}%".replace('.', ',')

def truncar_texto(texto: str, tamanho: int = 30) -> str:
    """Trunca texto adicionando reticências se necessário"""
    if len(texto) <= tamanho:
        return texto
    return texto[:tamanho-3] + "..."
