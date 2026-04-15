"""
Serviço de lógica de negócio para Estoque
"""
from typing import List, Tuple
from database import DatabaseManager, Produto
from utils.validators import validar_estoque

class EstoqueService:
    """Gerencia a lógica de negócio relacionada ao estoque"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def entrada_estoque(self, produto_id: int, quantidade: int, 
                       observacao: str = "") -> Tuple[bool, str]:
        """
        Registra entrada de estoque
        Retorna: (sucesso, mensagem)
        """
        if quantidade <= 0:
            return False, "Quantidade deve ser positiva"
        
        # Verificar se produto existe
        produto = self.db.buscar_produto(produto_id)
        if not produto:
            return False, f"Produto ID {produto_id} não encontrado"
        
        # Registrar entrada
        if self.db.ajustar_estoque(produto_id, quantidade, 'ENTRADA', observacao):
            return True, f"Entrada de {quantidade} unidades registrada com sucesso!"
        else:
            return False, "Erro ao registrar entrada de estoque"
    
    def saida_estoque(self, produto_id: int, quantidade: int, 
                     observacao: str = "") -> Tuple[bool, str]:
        """
        Registra saída de estoque
        Retorna: (sucesso, mensagem)
        """
        if quantidade <= 0:
            return False, "Quantidade deve ser positiva"
        
        # Verificar se produto existe
        produto = self.db.buscar_produto(produto_id)
        if not produto:
            return False, f"Produto ID {produto_id} não encontrado"
        
        # Verificar se há estoque suficiente
        if produto.estoque < quantidade:
            return False, f"Estoque insuficiente! Disponível: {produto.estoque}"
        
        # Registrar saída (quantidade negativa)
        if self.db.ajustar_estoque(produto_id, -quantidade, 'SAIDA', observacao):
            return True, f"Saída de {quantidade} unidades registrada com sucesso!"
        else:
            return False, "Erro ao registrar saída de estoque"
    
    def ajuste_estoque(self, produto_id: int, novo_estoque: int, 
                      observacao: str = "") -> Tuple[bool, str]:
        """
        Ajusta o estoque para um valor específico
        Retorna: (sucesso, mensagem)
        """
        valido, msg = validar_estoque(novo_estoque)
        if not valido:
            return False, msg
        
        # Verificar se produto existe
        produto = self.db.buscar_produto(produto_id)
        if not produto:
            return False, f"Produto ID {produto_id} não encontrado"
        
        # Calcular diferença
        diferenca = novo_estoque - produto.estoque
        
        if diferenca == 0:
            return False, "Novo estoque é igual ao atual"
        
        # Registrar ajuste
        if self.db.ajustar_estoque(produto_id, diferenca, 'AJUSTE', observacao):
            return True, f"Estoque ajustado de {produto.estoque} para {novo_estoque}"
        else:
            return False, "Erro ao ajustar estoque"
    
    def verificar_disponibilidade(self, produto_id: int, quantidade: int) -> Tuple[bool, str]:
        """
        Verifica se há estoque disponível para uma quantidade
        Retorna: (disponível, mensagem)
        """
        produto = self.db.buscar_produto(produto_id)
        if not produto:
            return False, "Produto não encontrado"
        
        if produto.estoque < quantidade:
            return False, f"Estoque insuficiente! Disponível: {produto.estoque}"
        
        return True, "Estoque disponível"
    
    def produtos_alertas(self) -> dict:
        """
        Retorna produtos com alertas de estoque
        """
        produtos = self.db.listar_produtos(apenas_ativos=True)
        
        sem_estoque = [p for p in produtos if p.estoque == 0]
        critico = [p for p in produtos if 0 < p.estoque <= 2]
        baixo = [p for p in produtos if 2 < p.estoque <= p.estoque_minimo]
        
        return {
            'sem_estoque': sem_estoque,
            'critico': critico,
            'baixo': baixo
        }