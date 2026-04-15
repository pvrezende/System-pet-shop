from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Cliente:
    """Modelo de dados para Cliente"""
    id: Optional[int] = None
    nome: str = ""
    cpf: str = ""
    telefone: str = ""
    email: str = ""
    endereco: str = ""
    data_cadastro: Optional[str] = None
    ativo: bool = True
    
    def __post_init__(self):
        if self.data_cadastro is None:
            self.data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class Produto:
    """Modelo de dados para Produto (Ração)"""
    id: Optional[int] = None
    nome: str = ""
    tipo_animal: str = ""  # 'gato' ou 'cão'
    marca: str = ""
    peso: float = 0.0
    preco_custo: float = 0.0
    preco_venda: float = 0.0
    estoque: int = 0
    estoque_minimo: int = 5
    codigo_barras: str = ""
    data_cadastro: Optional[str] = None
    ativo: bool = True
    
    def __post_init__(self):
        if self.data_cadastro is None:
            self.data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def margem_lucro(self) -> float:
        """Calcula a margem de lucro em percentual"""
        if self.preco_custo <= 0:
            return 0.0
        return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
    
    @property
    def valor_estoque(self) -> float:
        """Calcula o valor total do estoque"""
        return self.preco_venda * self.estoque
    
    @property
    def status_estoque(self) -> str:
        """Retorna o status do estoque"""
        if self.estoque == 0:
            return "SEM ESTOQUE"
        elif self.estoque <= 2:
            return "CRÍTICO"
        elif self.estoque <= self.estoque_minimo:
            return "BAIXO"
        return "OK"

@dataclass
class Venda:
    """Modelo de dados para Venda"""
    id: Optional[int] = None
    cliente_id: Optional[int] = None
    data_venda: Optional[str] = None
    valor_total: float = 0.0
    desconto: float = 0.0
    valor_final: float = 0.0
    forma_pagamento: str = "Dinheiro"
    status: str = "Concluída"  # Concluída, Cancelada
    observacoes: str = ""
    
    def __post_init__(self):
        if self.data_venda is None:
            self.data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.valor_final == 0.0:
            self.valor_final = self.valor_total - self.desconto

@dataclass
class ItemVenda:
    """Modelo de dados para Item de Venda"""
    id: Optional[int] = None
    venda_id: int = 0
    produto_id: int = 0
    produto_nome: str = ""
    quantidade: int = 0
    preco_unitario: float = 0.0
    subtotal: float = 0.0
    
    def __post_init__(self):
        if self.subtotal == 0.0:
            self.subtotal = self.quantidade * self.preco_unitario

@dataclass
class MovimentacaoEstoque:
    """Modelo de dados para Movimentação de Estoque"""
    id: Optional[int] = None
    produto_id: int = 0
    tipo_movimentacao: str = ""  # 'ENTRADA', 'SAIDA', 'AJUSTE', 'VENDA'
    quantidade: int = 0
    estoque_anterior: int = 0
    estoque_atual: int = 0
    data_movimentacao: Optional[str] = None
    observacao: str = ""
    
    def __post_init__(self):
        if self.data_movimentacao is None:
            self.data_movimentacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")