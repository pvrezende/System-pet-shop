"""
Widget do Dashboard - Visão geral do sistema
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.formatters import formatar_moeda


class DashboardWidget(QWidget):
    """Dashboard com visão geral do sistema"""
    
    def __init__(self, produto_service, venda_service, estoque_service, cliente_service):
        super().__init__()
        self.produto_service = produto_service
        self.venda_service = venda_service
        self.estoque_service = estoque_service
        self.cliente_service = cliente_service
        
        self._init_ui()
        self.atualizar_dados()
    
    def _init_ui(self):
        """Inicializa a interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("📊 DASHBOARD - VISÃO GERAL")
        titulo.setProperty("class", "title")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Cards de estatísticas
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        # Card: Total de Produtos
        self.card_produtos = self._criar_card("📦", "Total de Produtos", "0", "card-info")
        cards_layout.addWidget(self.card_produtos, 0, 0)
        
        # Card: Valor do Estoque
        self.card_valor_estoque = self._criar_card("💰", "Valor do Estoque", "R$ 0,00", "card-success")
        cards_layout.addWidget(self.card_valor_estoque, 0, 1)
        
        # Card: Produtos em Alerta
        self.card_alertas = self._criar_card("⚠️", "Alertas de Estoque", "0", "card-warning")
        cards_layout.addWidget(self.card_alertas, 0, 2)
        
        # Card: Total de Clientes
        self.card_clientes = self._criar_card("👥", "Total de Clientes", "0", "card-info")
        cards_layout.addWidget(self.card_clientes, 1, 0)
        
        # Card: Vendas Hoje
        self.card_vendas_hoje = self._criar_card("💳", "Vendas Hoje", "R$ 0,00", "card-success")
        cards_layout.addWidget(self.card_vendas_hoje, 1, 1)
        
        # Card: Total Vendas
        self.card_total_vendas = self._criar_card("📈", "Total de Vendas", "0", "card-info")
        cards_layout.addWidget(self.card_total_vendas, 1, 2)
        
        layout.addLayout(cards_layout)
        
        # Seção: Produtos com Estoque Baixo
        label_baixo = QLabel("⚠️ PRODUTOS COM ESTOQUE BAIXO")
        label_baixo.setProperty("class", "subtitle")
        layout.addWidget(label_baixo)
        
        self.tabela_estoque_baixo = QTableWidget()
        self.tabela_estoque_baixo.setColumnCount(5)
        self.tabela_estoque_baixo.setHorizontalHeaderLabels(["Produto", "Tipo", "Marca", "Estoque", "Status"])
        self.tabela_estoque_baixo.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_estoque_baixo.setMaximumHeight(200)
        self.tabela_estoque_baixo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_estoque_baixo.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabela_estoque_baixo)
        
        # Botão atualizar
        btn_atualizar = QPushButton("🔄 Atualizar Dashboard")
        btn_atualizar.clicked.connect(self.atualizar_dados)
        layout.addWidget(btn_atualizar)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _criar_card(self, icone, titulo, valor, classe="card"):
        """Cria um card de estatística"""
        card = QFrame()
        card.setProperty("class", classe)
        card.setMinimumHeight(120)
        
        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignCenter)
        
        # Ícone
        label_icone = QLabel(icone)
        label_icone.setAlignment(Qt.AlignCenter)
        font_icone = QFont()
        font_icone.setPointSize(32)
        label_icone.setFont(font_icone)
        card_layout.addWidget(label_icone)
        
        # Valor
        label_valor = QLabel(valor)
        label_valor.setAlignment(Qt.AlignCenter)
        label_valor.setObjectName("card_valor")
        font_valor = QFont()
        font_valor.setPointSize(18)
        font_valor.setBold(True)
        label_valor.setFont(font_valor)
        card_layout.addWidget(label_valor)
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setAlignment(Qt.AlignCenter)
        font_titulo = QFont()
        font_titulo.setPointSize(10)
        label_titulo.setFont(font_titulo)
        card_layout.addWidget(label_titulo)
        
        card.setLayout(card_layout)
        return card
    
    def _atualizar_valor_card(self, card, novo_valor):
        """Atualiza o valor de um card"""
        label_valor = card.findChild(QLabel, "card_valor")
        if label_valor:
            label_valor.setText(novo_valor)
    
    def atualizar_dados(self):
        """Atualiza todos os dados do dashboard"""
        # Estatísticas de produtos
        stats_produtos = self.produto_service.obter_estatisticas()
        self._atualizar_valor_card(self.card_produtos, str(stats_produtos['total_produtos']))
        self._atualizar_valor_card(self.card_valor_estoque, 
                                   formatar_moeda(stats_produtos['valor_total_estoque']))
        
        total_alertas = (stats_produtos['produtos_sem_estoque'] + 
                        stats_produtos['produtos_estoque_baixo'])
        self._atualizar_valor_card(self.card_alertas, str(total_alertas))
        
        # Estatísticas de clientes
        stats_clientes = self.cliente_service.obter_estatisticas()
        self._atualizar_valor_card(self.card_clientes, str(stats_clientes['total_clientes']))
        
        # Estatísticas de vendas
        from datetime import datetime
        hoje = datetime.now().strftime("%Y-%m-%d")
        stats_vendas = self.venda_service.obter_estatisticas_vendas(hoje, hoje)
        
        self._atualizar_valor_card(self.card_vendas_hoje, 
                                   formatar_moeda(stats_vendas['valor_total']))
        self._atualizar_valor_card(self.card_total_vendas, str(stats_vendas['total_vendas']))
        
        # Atualizar tabela de estoque baixo
        self._atualizar_tabela_estoque_baixo()
    
    def _atualizar_tabela_estoque_baixo(self):
        """Atualiza a tabela de produtos com estoque baixo"""
        produtos = self.produto_service.produtos_estoque_baixo()
        
        self.tabela_estoque_baixo.setRowCount(0)
        
        for produto in produtos[:10]:  # Mostrar apenas os 10 primeiros
            row = self.tabela_estoque_baixo.rowCount()
            self.tabela_estoque_baixo.insertRow(row)
            
            self.tabela_estoque_baixo.setItem(row, 0, QTableWidgetItem(produto.nome))
            self.tabela_estoque_baixo.setItem(row, 1, QTableWidgetItem(produto.tipo_animal.upper()))
            self.tabela_estoque_baixo.setItem(row, 2, QTableWidgetItem(produto.marca))
            self.tabela_estoque_baixo.setItem(row, 3, QTableWidgetItem(str(produto.estoque)))
            
            # Status com cor
            item_status = QTableWidgetItem(produto.status_estoque)
            if produto.status_estoque == "SEM ESTOQUE":
                item_status.setForeground(Qt.red)
            elif produto.status_estoque == "CRÍTICO":
                item_status.setForeground(Qt.darkRed)
            elif produto.status_estoque == "BAIXO":
                item_status.setForeground(Qt.darkYellow)
            
            self.tabela_estoque_baixo.setItem(row, 4, item_status)