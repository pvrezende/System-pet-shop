"""
Serviço de lógica de negócio para Produtos
"""
from typing import List, Optional, Tuple
from database import DatabaseManager, Produto
from utils.validators import validar_preco, validar_peso, validar_estoque
from config.settings import TIPOS_ANIMAIS

class ProdutoService:
    """Gerencia a lógica de negócio relacionada a produtos"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def _normalizar_tipo_animal(self, tipo: str) -> Optional[str]:
        """Normaliza o tipo de animal (aceita 'cao' como 'cão')"""
        tipo_lower = tipo.lower().strip()
        
        if tipo_lower == 'cao':
            return 'cão'
        elif tipo_lower in TIPOS_ANIMAIS:
            return tipo_lower
        return None
    
    def _validar_produto(self, produto: Produto) -> Tuple[bool, str]:
        """Valida todos os campos de um produto"""
        
        # Validar nome
        if not produto.nome or len(produto.nome.strip()) < 3:
            return False, "Nome do produto deve ter pelo menos 3 caracteres"
        
        # Validar tipo de animal
        tipo_normalizado = self._normalizar_tipo_animal(produto.tipo_animal)
        if not tipo_normalizado:
            return False, f"Tipo de animal deve ser 'gato' ou 'cão'"
        produto.tipo_animal = tipo_normalizado
        
        # Validar marca
        if not produto.marca or len(produto.marca.strip()) < 2:
            return False, "Marca deve ter pelo menos 2 caracteres"
        
        # Validar peso
        valido, msg = validar_peso(produto.peso)
        if not valido:
            return False, msg
        
        # Validar preço de custo
        if produto.preco_custo < 0:
            return False, "Preço de custo não pode ser negativo"
        
        # Validar preço de venda
        valido, msg = validar_preco(produto.preco_venda)
        if not valido:
            return False, msg
        
        # Validar que preço de venda é maior que custo
        if produto.preco_custo > 0 and produto.preco_venda <= produto.preco_custo:
            return False, "Preço de venda deve ser maior que o preço de custo"
        
        # Validar estoque
        valido, msg = validar_estoque(produto.estoque)
        if not valido:
            return False, msg
        
        # Validar estoque mínimo
        if produto.estoque_minimo < 0:
            return False, "Estoque mínimo não pode ser negativo"
        
        return True, ""
    
    def cadastrar_produto(self, produto: Produto) -> Tuple[bool, str, Optional[int]]:
        """
        Cadastra um novo produto
        Retorna: (sucesso, mensagem, id_produto)
        """
        # Validar dados
        valido, mensagem = self._validar_produto(produto)
        if not valido:
            return False, mensagem, None
        
        # Criar produto no banco
        produto_id = self.db.criar_produto(produto)
        
        if produto_id:
            return True, f"Produto '{produto.nome}' cadastrado com sucesso!", produto_id
        else:
            return False, "Erro ao cadastrar produto no banco de dados", None
    
    def buscar_produto(self, produto_id: int) -> Optional[Produto]:
        """Busca um produto pelo ID"""
        return self.db.buscar_produto(produto_id)
    
    def listar_produtos(self, tipo_animal: Optional[str] = None, 
                       apenas_ativos: bool = True) -> List[Produto]:
        """Lista produtos com filtros"""
        if tipo_animal:
            tipo_animal = self._normalizar_tipo_animal(tipo_animal)
        
        return self.db.listar_produtos(tipo_animal, apenas_ativos)
    
    def atualizar_produto(self, produto_id: int, **kwargs) -> Tuple[bool, str]:
        """
        Atualiza um produto existente
        Retorna: (sucesso, mensagem)
        """
        # Verificar se produto existe
        produto = self.db.buscar_produto(produto_id)
        if not produto:
            return False, f"Produto ID {produto_id} não encontrado"
        
        # Validar campos se fornecidos
        if 'tipo_animal' in kwargs:
            tipo_normalizado = self._normalizar_tipo_animal(kwargs['tipo_animal'])
            if not tipo_normalizado:
                return False, "Tipo de animal inválido"
            kwargs['tipo_animal'] = tipo_normalizado
        
        if 'peso' in kwargs:
            valido, msg = validar_peso(kwargs['peso'])
            if not valido:
                return False, msg
        
        if 'preco_venda' in kwargs:
            valido, msg = validar_preco(kwargs['preco_venda'])
            if not valido:
                return False, msg
        
        if 'preco_custo' in kwargs and kwargs['preco_custo'] < 0:
            return False, "Preço de custo não pode ser negativo"
        
        # Atualizar no banco
        if self.db.atualizar_produto(produto_id, **kwargs):
            return True, "Produto atualizado com sucesso!"
        else:
            return False, "Erro ao atualizar produto"
    
    def deletar_produto(self, produto_id: int) -> Tuple[bool, str]:
        """
        Desativa um produto (soft delete)
        Retorna: (sucesso, mensagem)
        """
        produto = self.db.buscar_produto(produto_id)
        if not produto:
            return False, f"Produto ID {produto_id} não encontrado"
        
        if self.db.deletar_produto(produto_id):
            return True, f"Produto '{produto.nome}' desativado com sucesso!"
        else:
            return False, "Erro ao desativar produto"
    
    def produtos_estoque_baixo(self) -> List[Produto]:
        """Retorna produtos com estoque baixo ou crítico"""
        return self.db.produtos_estoque_baixo()
    
    def calcular_valor_total_estoque(self) -> float:
        """Calcula o valor total do estoque"""
        produtos = self.db.listar_produtos(apenas_ativos=True)
        return sum(p.valor_estoque for p in produtos)
    
    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas gerais dos produtos"""
        produtos = self.db.listar_produtos(apenas_ativos=True)
        
        total_produtos = len(produtos)
        produtos_gatos = len([p for p in produtos if p.tipo_animal == 'gato'])
        produtos_caes = len([p for p in produtos if p.tipo_animal == 'cão'])
        
        valor_total_estoque = sum(p.valor_estoque for p in produtos)
        produtos_sem_estoque = len([p for p in produtos if p.estoque == 0])
        produtos_estoque_baixo = len([p for p in produtos if 0 < p.estoque <= p.estoque_minimo])
        
        # Top 5 mais caros
        mais_caros = sorted(produtos, key=lambda p: p.preco_venda, reverse=True)[:5]
        
        # Top 5 maior estoque
        maior_estoque = sorted(produtos, key=lambda p: p.estoque, reverse=True)[:5]
        
        # Top 5 maior margem de lucro
        maior_margem = sorted(
            [p for p in produtos if p.preco_custo > 0],
            key=lambda p: p.margem_lucro,
            reverse=True
        )[:5]
        
        return {
            'total_produtos': total_produtos,
            'produtos_gatos': produtos_gatos,
            'produtos_caes': produtos_caes,
            'valor_total_estoque': valor_total_estoque,
            'produtos_sem_estoque': produtos_sem_estoque,
            'produtos_estoque_baixo': produtos_estoque_baixo,
            'mais_caros': mais_caros,
            'maior_estoque': maior_estoque,
            'maior_margem': maior_margem
        }
    