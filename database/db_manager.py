"""
Gerenciador principal do banco de dados SQLite
"""
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from contextlib import contextmanager

from config.settings import DATABASE, REPORT_CONFIG
from .models import Cliente, Produto, Venda, ItemVenda, MovimentacaoEstoque


class DatabaseManager:
    """Gerencia todas as operações com o banco de dados"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DATABASE['path'])
        self._init_database()
        self._insert_test_data()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexões ao banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Inicializa todas as tabelas do banco de dados"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de Clientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT UNIQUE,
                    telefone TEXT NOT NULL,
                    email TEXT,
                    endereco TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabela de Produtos (Rações) - ATUALIZADA
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    tipo_animal TEXT NOT NULL CHECK (tipo_animal IN ('gato', 'cão')),
                    marca TEXT NOT NULL,
                    peso REAL NOT NULL CHECK (peso > 0),
                    preco_custo REAL NOT NULL DEFAULT 0 CHECK (preco_custo >= 0),
                    preco_venda REAL NOT NULL CHECK (preco_venda > 0),
                    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
                    estoque_minimo INTEGER DEFAULT 5,
                    codigo_barras TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabela de Vendas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    valor_total REAL NOT NULL CHECK (valor_total >= 0),
                    desconto REAL DEFAULT 0 CHECK (desconto >= 0),
                    valor_final REAL NOT NULL CHECK (valor_final >= 0),
                    forma_pagamento TEXT NOT NULL,
                    status TEXT DEFAULT 'Concluída' CHECK (status IN ('Concluída', 'Cancelada')),
                    observacoes TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            ''')
            
            # Tabela de Itens de Venda
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS itens_venda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venda_id INTEGER NOT NULL,
                    produto_id INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                    preco_unitario REAL NOT NULL CHECK (preco_unitario > 0),
                    subtotal REAL NOT NULL CHECK (subtotal >= 0),
                    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id)
                )
            ''')
            
            # Tabela de Movimentações de Estoque
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id INTEGER NOT NULL,
                    tipo_movimentacao TEXT NOT NULL CHECK (tipo_movimentacao IN ('ENTRADA', 'SAIDA', 'AJUSTE', 'VENDA')),
                    quantidade INTEGER NOT NULL,
                    estoque_anterior INTEGER NOT NULL,
                    estoque_atual INTEGER NOT NULL,
                    data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observacao TEXT,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id)
                )
            ''')
            
            # Criar índices para melhor performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_produtos_tipo ON produtos(tipo_animal)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_produtos_estoque ON produtos(estoque)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data_venda)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_clientes_cpf ON clientes(cpf)')
            
            conn.commit()
            print("✅ Banco de dados inicializado com sucesso!")
    
    def _insert_test_data(self):
        """Insere dados de teste apenas se o banco estiver vazio"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM produtos")
            count = cursor.fetchone()[0]
            
            if count == 0:
                test_products = [
                    ("Royal Canin Adult", "cão", "Royal Canin", 15.0, 70.0, 89.90, 12, 5),
                    ("Whiskas Adulto Peixe", "gato", "Whiskas", 3.0, 18.0, 24.50, 8, 5),
                    ("Pedigree Adulto Carne", "cão", "Pedigree", 20.0, 50.0, 65.00, 15, 5),
                    ("Golden Gatos Castrados", "gato", "Golden", 10.1, 60.0, 78.90, 6, 5),
                    ("Hill's Science Diet Adult", "cão", "Hill's", 12.0, 110.0, 145.00, 4, 3),
                    ("Friskies Adulto Frango", "gato", "Friskies", 7.5, 32.0, 42.80, 20, 8),
                    ("Premier Pet Adulto", "cão", "Premier Pet", 15.0, 75.0, 98.50, 9, 5),
                    ("Purina Cat Chow Adulto", "gato", "Purina", 10.1, 52.0, 68.90, 11, 5),
                    ("Eukanuba Puppy", "cão", "Eukanuba", 3.0, 42.0, 56.00, 7, 5),
                    ("Royal Canin Kitten", "gato", "Royal Canin", 4.0, 40.0, 52.90, 5, 3),
                ]
                
                cursor.executemany('''
                    INSERT INTO produtos (nome, tipo_animal, marca, peso, preco_custo, preco_venda, estoque, estoque_minimo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', test_products)
                
                # Cliente de teste
                cursor.execute('''
                    INSERT INTO clientes (nome, cpf, telefone, email)
                    VALUES ('Cliente Padrão', '00000000000', '(27) 99999-9999', 'cliente@exemplo.com')
                ''')
                
                conn.commit()
                print(f"✅ {len(test_products)} produtos e 1 cliente de teste inseridos!")
            else:
                print(f"ℹ️ Banco já possui {count} produtos cadastrados.")
    
    # ==================== MÉTODOS DE PRODUTOS ====================
    
    def criar_produto(self, produto: Produto) -> Optional[int]:
        """Cria um novo produto no banco de dados"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO produtos (nome, tipo_animal, marca, peso, preco_custo, preco_venda, 
                                        estoque, estoque_minimo, codigo_barras, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (produto.nome, produto.tipo_animal, produto.marca, produto.peso,
                      produto.preco_custo, produto.preco_venda, produto.estoque,
                      produto.estoque_minimo, produto.codigo_barras, produto.ativo))
                
                produto_id = cursor.lastrowid
                
                # Registrar movimentação de estoque inicial se houver
                if produto.estoque > 0:
                    self._registrar_movimentacao(
                        cursor, produto_id, 'ENTRADA', produto.estoque, 0, produto.estoque,
                        'Estoque inicial'
                    )
                
                return produto_id
        except sqlite3.Error as e:
            print(f"❌ Erro ao criar produto: {e}")
            return None
    
    def buscar_produto(self, produto_id: int) -> Optional[Produto]:
        """Busca um produto pelo ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,))
                row = cursor.fetchone()
                
                if row:
                    return Produto(**dict(row))
                return None
        except sqlite3.Error as e:
            print(f"❌ Erro ao buscar produto: {e}")
            return None
    
    def listar_produtos(self, tipo_animal: Optional[str] = None, 
                       apenas_ativos: bool = True) -> List[Produto]:
        """Lista produtos com filtros opcionais"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM produtos WHERE 1=1'
                params = []
                
                if apenas_ativos:
                    query += ' AND ativo = 1'
                
                if tipo_animal:
                    query += ' AND tipo_animal = ?'
                    params.append(tipo_animal)
                
                query += ' ORDER BY nome'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [Produto(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Erro ao listar produtos: {e}")
            return []
    
    def atualizar_produto(self, produto_id: int, **kwargs) -> bool:
        """Atualiza um produto existente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                campos_permitidos = ['nome', 'tipo_animal', 'marca', 'peso', 'preco_custo',
                                   'preco_venda', 'estoque_minimo', 'codigo_barras', 'ativo']
                
                updates = []
                valores = []
                
                for campo, valor in kwargs.items():
                    if campo in campos_permitidos:
                        updates.append(f"{campo} = ?")
                        valores.append(valor)
                
                if not updates:
                    return False
                
                valores.append(produto_id)
                query = f"UPDATE produtos SET {', '.join(updates)} WHERE id = ?"
                
                cursor.execute(query, valores)
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"❌ Erro ao atualizar produto: {e}")
            return False
    
    def deletar_produto(self, produto_id: int) -> bool:
        """Desativa um produto (soft delete)"""
        return self.atualizar_produto(produto_id, ativo=False)
    
    def ajustar_estoque(self, produto_id: int, quantidade: int, 
                       tipo: str = 'AJUSTE', observacao: str = '') -> bool:
        """Ajusta o estoque de um produto e registra a movimentação"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Buscar estoque atual
                cursor.execute('SELECT estoque FROM produtos WHERE id = ?', (produto_id,))
                row = cursor.fetchone()
                
                if not row:
                    print(f"❌ Produto {produto_id} não encontrado")
                    return False
                
                estoque_anterior = row['estoque']
                estoque_novo = estoque_anterior + quantidade
                
                if estoque_novo < 0:
                    print(f"❌ Estoque insuficiente! Estoque atual: {estoque_anterior}")
                    return False
                
                # Atualizar estoque
                cursor.execute(
                    'UPDATE produtos SET estoque = ? WHERE id = ?',
                    (estoque_novo, produto_id)
                )
                
                # Registrar movimentação
                self._registrar_movimentacao(
                    cursor, produto_id, tipo, abs(quantidade),
                    estoque_anterior, estoque_novo, observacao
                )
                
                return True
        except sqlite3.Error as e:
            print(f"❌ Erro ao ajustar estoque: {e}")
            return False
    
    def _registrar_movimentacao(self, cursor, produto_id: int, tipo: str,
                               quantidade: int, estoque_anterior: int,
                               estoque_atual: int, observacao: str = ''):
        """Registra uma movimentação de estoque (método interno)"""
        cursor.execute('''
            INSERT INTO movimentacoes_estoque 
            (produto_id, tipo_movimentacao, quantidade, estoque_anterior, estoque_atual, observacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (produto_id, tipo, quantidade, estoque_anterior, estoque_atual, observacao))
    
    def produtos_estoque_baixo(self) -> List[Produto]:
        """Retorna produtos com estoque baixo ou zerado"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM produtos 
                    WHERE ativo = 1 AND estoque <= estoque_minimo
                    ORDER BY estoque ASC
                ''')
                rows = cursor.fetchall()
                return [Produto(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Erro ao buscar produtos com estoque baixo: {e}")
            return []
    
    # ==================== MÉTODOS DE CLIENTES ====================
    
    def criar_cliente(self, cliente: Cliente) -> Optional[int]:
        """Cria um novo cliente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO clientes (nome, cpf, telefone, email, endereco, ativo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (cliente.nome, cliente.cpf, cliente.telefone, cliente.email,
                      cliente.endereco, cliente.ativo))
                
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"❌ CPF {cliente.cpf} já cadastrado!")
            return None
        except sqlite3.Error as e:
            print(f"❌ Erro ao criar cliente: {e}")
            return None
    
    def buscar_cliente(self, cliente_id: int) -> Optional[Cliente]:
        """Busca um cliente pelo ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
                row = cursor.fetchone()
                
                if row:
                    return Cliente(**dict(row))
                return None
        except sqlite3.Error as e:
            print(f"❌ Erro ao buscar cliente: {e}")
            return None
    
    def buscar_cliente_por_cpf(self, cpf: str) -> Optional[Cliente]:
        """Busca um cliente pelo CPF"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM clientes WHERE cpf = ?', (cpf,))
                row = cursor.fetchone()
                
                if row:
                    return Cliente(**dict(row))
                return None
        except sqlite3.Error as e:
            print(f"❌ Erro ao buscar cliente por CPF: {e}")
            return None
    
    def listar_clientes(self, apenas_ativos: bool = True) -> List[Cliente]:
        """Lista todos os clientes"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM clientes'
                if apenas_ativos:
                    query += ' WHERE ativo = 1'
                query += ' ORDER BY nome'
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                return [Cliente(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Erro ao listar clientes: {e}")
            return []
    
    def atualizar_cliente(self, cliente_id: int, **kwargs) -> bool:
        """Atualiza um cliente existente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                campos_permitidos = ['nome', 'cpf', 'telefone', 'email', 'endereco', 'ativo']
                
                updates = []
                valores = []
                
                for campo, valor in kwargs.items():
                    if campo in campos_permitidos:
                        updates.append(f"{campo} = ?")
                        valores.append(valor)
                
                if not updates:
                    return False
                
                valores.append(cliente_id)
                query = f"UPDATE clientes SET {', '.join(updates)} WHERE id = ?"
                
                cursor.execute(query, valores)
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"❌ Erro ao atualizar cliente: {e}")
            return False
    
    def deletar_cliente(self, cliente_id: int) -> bool:
        """Desativa um cliente (soft delete)"""
        return self.atualizar_cliente(cliente_id, ativo=False)
    
    # ==================== BACKUP ====================
    
    def criar_backup(self, nome_arquivo: Optional[str] = None) -> bool:
        """Cria um backup do banco de dados"""
        try:
            if not nome_arquivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"backup_petshop_{timestamp}.db"
            
            caminho_backup = REPORT_CONFIG['backup_dir'] / nome_arquivo
            shutil.copy2(self.db_path, caminho_backup)
            
            print(f"✅ Backup criado: {caminho_backup}")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return False