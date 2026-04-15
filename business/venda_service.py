"""
Serviço de lógica de negócio para Vendas
"""
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from database import DatabaseManager, Venda, ItemVenda
from utils.validators import validar_desconto

class VendaService:
    """Gerencia a lógica de negócio relacionada a vendas"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def criar_venda(self, cliente_id: Optional[int], itens: List[Dict],
                   forma_pagamento: str, desconto: float = 0.0,
                   observacoes: str = "") -> Tuple[bool, str, Optional[int]]:
        """
        Cria uma nova venda
        itens: lista de dicts com {'produto_id': int, 'quantidade': int}
        Retorna: (sucesso, mensagem, id_venda)
        """
        
        if not itens:
            return False, "Carrinho vazio! Adicione produtos para vender", None
        
        # Validar e calcular totais
        valor_total = 0.0
        itens_venda = []
        
        for item in itens:
            produto_id = item.get('produto_id')
            quantidade = item.get('quantidade', 0)
            
            if quantidade <= 0:
                return False, f"Quantidade inválida para o produto", None
            
            # Buscar produto
            produto = self.db.buscar_produto(produto_id)
            if not produto:
                return False, f"Produto ID {produto_id} não encontrado", None
            
            if not produto.ativo:
                return False, f"Produto '{produto.nome}' está inativo", None
            
            # Verificar estoque
            if produto.estoque < quantidade:
                return False, f"Estoque insuficiente para '{produto.nome}'! Disponível: {produto.estoque}", None
            
            # Calcular subtotal
            subtotal = produto.preco_venda * quantidade
            valor_total += subtotal
            
            # Criar item de venda
            item_venda = ItemVenda(
                produto_id=produto_id,
                produto_nome=produto.nome,
                quantidade=quantidade,
                preco_unitario=produto.preco_venda,
                subtotal=subtotal
            )
            itens_venda.append((item_venda, produto))
        
        # Validar desconto
        valido, msg = validar_desconto(desconto, valor_total)
        if not valido:
            return False, msg, None
        
        valor_final = valor_total - desconto
        
        # Criar venda no banco
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                
                # Inserir venda
                cursor.execute('''
                    INSERT INTO vendas (cliente_id, valor_total, desconto, valor_final, forma_pagamento, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (cliente_id, valor_total, desconto, valor_final, forma_pagamento, observacoes))
                
                venda_id = cursor.lastrowid
                
                # Inserir itens da venda e baixar estoque
                for item_venda, produto in itens_venda:
                    # Inserir item
                    cursor.execute('''
                        INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (venda_id, item_venda.produto_id, item_venda.quantidade,
                          item_venda.preco_unitario, item_venda.subtotal))
                    
                    # Baixar estoque
                    estoque_anterior = produto.estoque
                    estoque_novo = estoque_anterior - item_venda.quantidade
                    
                    cursor.execute(
                        'UPDATE produtos SET estoque = ? WHERE id = ?',
                        (estoque_novo, produto.id)
                    )
                    
                    # Registrar movimentação
                    cursor.execute('''
                        INSERT INTO movimentacoes_estoque 
                        (produto_id, tipo_movimentacao, quantidade, estoque_anterior, estoque_atual, observacao)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (produto.id, 'VENDA', item_venda.quantidade, estoque_anterior, 
                          estoque_novo, f'Venda #{venda_id}'))
                
                conn.commit()
                
                return True, f"Venda #{venda_id} realizada com sucesso!", venda_id
                
        except Exception as e:
            return False, f"Erro ao processar venda: {str(e)}", None
    
    def buscar_venda(self, venda_id: int) -> Optional[Dict]:
        """Busca uma venda completa com seus itens"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                
                # Buscar venda
                cursor.execute('SELECT * FROM vendas WHERE id = ?', (venda_id,))
                venda_row = cursor.fetchone()
                
                if not venda_row:
                    return None
                
                venda = Venda(**dict(venda_row))
                
                # Buscar itens da venda
                cursor.execute('''
                    SELECT iv.*, p.nome as produto_nome
                    FROM itens_venda iv
                    JOIN produtos p ON iv.produto_id = p.id
                    WHERE iv.venda_id = ?
                ''', (venda_id,))
                
                itens_rows = cursor.fetchall()
                itens = [ItemVenda(**dict(row)) for row in itens_rows]
                
                # Buscar cliente se houver
                cliente = None
                if venda.cliente_id:
                    cliente = self.db.buscar_cliente(venda.cliente_id)
                
                return {
                    'venda': venda,
                    'itens': itens,
                    'cliente': cliente
                }
                
        except Exception as e:
            print(f"❌ Erro ao buscar venda: {e}")
            return None
    
    def listar_vendas(self, data_inicio: Optional[str] = None,
                     data_fim: Optional[str] = None,
                     cliente_id: Optional[int] = None) -> List[Venda]:
        """Lista vendas com filtros opcionais"""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM vendas WHERE 1=1'
                params = []
                
                if data_inicio:
                    query += ' AND date(data_venda) >= date(?)'
                    params.append(data_inicio)
                
                if data_fim:
                    query += ' AND date(data_venda) <= date(?)'
                    params.append(data_fim)
                
                if cliente_id:
                    query += ' AND cliente_id = ?'
                    params.append(cliente_id)
                
                query += ' ORDER BY data_venda DESC'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [Venda(**dict(row)) for row in rows]
                
        except Exception as e:
            print(f"❌ Erro ao listar vendas: {e}")
            return []
    
    def cancelar_venda(self, venda_id: int, motivo: str = "") -> Tuple[bool, str]:
        """
        Cancela uma venda e devolve produtos ao estoque
        Retorna: (sucesso, mensagem)
        """
        venda_completa = self.buscar_venda(venda_id)
        
        if not venda_completa:
            return False, f"Venda #{venda_id} não encontrada"
        
        venda = venda_completa['venda']
        
        if venda.status == 'Cancelada':
            return False, "Venda já está cancelada"
        
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                
                # Devolver produtos ao estoque
                for item in venda_completa['itens']:
                    # Buscar estoque atual
                    cursor.execute('SELECT estoque FROM produtos WHERE id = ?', (item.produto_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        estoque_anterior = row['estoque']
                        estoque_novo = estoque_anterior + item.quantidade
                        
                        # Atualizar estoque
                        cursor.execute(
                            'UPDATE produtos SET estoque = ? WHERE id = ?',
                            (estoque_novo, item.produto_id)
                        )
                        
                        # Registrar movimentação
                        cursor.execute('''
                            INSERT INTO movimentacoes_estoque 
                            (produto_id, tipo_movimentacao, quantidade, estoque_anterior, estoque_atual, observacao)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (item.produto_id, 'ENTRADA', item.quantidade, estoque_anterior,
                              estoque_novo, f'Cancelamento venda #{venda_id} - {motivo}'))
                
                # Atualizar status da venda
                observacao_cancelamento = f"CANCELADA - {motivo}" if motivo else "CANCELADA"
                cursor.execute(
                    'UPDATE vendas SET status = ?, observacoes = ? WHERE id = ?',
                    ('Cancelada', observacao_cancelamento, venda_id)
                )
                
                conn.commit()
                
                return True, f"Venda #{venda_id} cancelada e produtos devolvidos ao estoque"
                
        except Exception as e:
            return False, f"Erro ao cancelar venda: {str(e)}"
    
    def obter_estatisticas_vendas(self, data_inicio: Optional[str] = None,
                                  data_fim: Optional[str] = None) -> dict:
        """Retorna estatísticas de vendas para um período"""
        vendas = self.listar_vendas(data_inicio, data_fim)
        
        vendas_concluidas = [v for v in vendas if v.status == 'Concluída']
        
        total_vendas = len(vendas_concluidas)
        valor_total = sum(v.valor_final for v in vendas_concluidas)
        ticket_medio = valor_total / total_vendas if total_vendas > 0 else 0
        total_descontos = sum(v.desconto for v in vendas_concluidas)
        
        # Vendas por forma de pagamento
        formas_pagamento = {}
        for venda in vendas_concluidas:
            forma = venda.forma_pagamento
            if forma not in formas_pagamento:
                formas_pagamento[forma] = {'quantidade': 0, 'valor': 0.0}
            formas_pagamento[forma]['quantidade'] += 1
            formas_pagamento[forma]['valor'] += venda.valor_final
        
        return {
            'total_vendas': total_vendas,
            'valor_total': valor_total,
            'ticket_medio': ticket_medio,
            'total_descontos': total_descontos,
            'formas_pagamento': formas_pagamento
        }