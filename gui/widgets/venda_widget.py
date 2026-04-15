"""
Widget de gerenciamento de vendas (PDV)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox,
    QFormLayout, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt
from utils.formatters import formatar_moeda, formatar_data_hora
from config.settings import FORMAS_PAGAMENTO


class VendaWidget(QWidget):
    """Widget de PDV (Ponto de Venda)"""
    
    def __init__(self, venda_service, produto_service, cliente_service):
        super().__init__()
        self.venda_service = venda_service
        self.produto_service = produto_service
        self.cliente_service = cliente_service
        self.carrinho = []
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("💰 PONTO DE VENDA (PDV)")
        titulo.setProperty("class", "title")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Splitter para dividir em duas colunas
        splitter = QSplitter(Qt.Horizontal)
        
        # === COLUNA ESQUERDA: Adicionar produtos ===
        widget_esquerda = QWidget()
        layout_esquerda = QVBoxLayout()
        
        # Seleção de produto
        group_produto = QGroupBox("Adicionar Produto ao Carrinho")
        form_produto = QFormLayout()
        
        self.combo_produto = QComboBox()
        self.combo_produto.currentIndexChanged.connect(self._atualizar_info_produto)
        form_produto.addRow("Produto:", self.combo_produto)
        
        self.label_estoque = QLabel("-")
        form_produto.addRow("Estoque:", self.label_estoque)
        
        self.label_preco = QLabel("-")
        form_produto.addRow("Preço Unit.:", self.label_preco)
        
        self.spin_quantidade = QSpinBox()
        self.spin_quantidade.setMinimum(1)
        self.spin_quantidade.valueChanged.connect(self._calcular_subtotal)
        form_produto.addRow("Quantidade:", self.spin_quantidade)
        
        self.label_subtotal = QLabel("R$ 0,00")
        self.label_subtotal.setStyleSheet("font-weight: bold; font-size: 14px;")
        form_produto.addRow("Subtotal:", self.label_subtotal)
        
        btn_adicionar = QPushButton("➕ Adicionar ao Carrinho")
        btn_adicionar.setProperty("class", "success")
        btn_adicionar.clicked.connect(self._adicionar_ao_carrinho)
        form_produto.addRow(btn_adicionar)
        
        group_produto.setLayout(form_produto)
        layout_esquerda.addWidget(group_produto)
        
        # Cliente (opcional)
        group_cliente = QGroupBox("Cliente (Opcional)")
        form_cliente = QFormLayout()
        
        self.combo_cliente = QComboBox()
        self.combo_cliente.addItem("Cliente não identificado", None)
        form_cliente.addRow("Cliente:", self.combo_cliente)
        
        group_cliente.setLayout(form_cliente)
        layout_esquerda.addWidget(group_cliente)
        
        layout_esquerda.addStretch()
        widget_esquerda.setLayout(layout_esquerda)
        splitter.addWidget(widget_esquerda)
        
        # === COLUNA DIREITA: Carrinho e finalização ===
        widget_direita = QWidget()
        layout_direita = QVBoxLayout()
        
        # Carrinho
        label_carrinho = QLabel("🛒 CARRINHO DE COMPRAS")
        label_carrinho.setProperty("class", "subtitle")
        layout_direita.addWidget(label_carrinho)
        
        self.tabela_carrinho = QTableWidget()
        self.tabela_carrinho.setColumnCount(5)
        self.tabela_carrinho.setHorizontalHeaderLabels([
            "Produto", "Qtd", "Preço Unit.", "Subtotal", "Ação"
        ])
        self.tabela_carrinho.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_carrinho.setMaximumHeight(250)
        layout_direita.addWidget(self.tabela_carrinho)
        
        # Totais
        group_totais = QGroupBox("Totais")
        form_totais = QFormLayout()
        
        self.label_valor_total = QLabel("R$ 0,00")
        self.label_valor_total.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_totais.addRow("Valor Total:", self.label_valor_total)
        
        self.spin_desconto = QDoubleSpinBox()
        self.spin_desconto.setPrefix("R$ ")
        self.spin_desconto.setMaximum(999999.99)
        self.spin_desconto.valueChanged.connect(self._calcular_total)
        form_totais.addRow("Desconto:", self.spin_desconto)
        
        self.label_valor_final = QLabel("R$ 0,00")
        self.label_valor_final.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        form_totais.addRow("Valor Final:", self.label_valor_final)
        
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(FORMAS_PAGAMENTO)
        form_totais.addRow("Pagamento:", self.combo_pagamento)
        
        group_totais.setLayout(form_totais)
        layout_direita.addWidget(group_totais)
        
        # Botões finais
        btn_layout = QHBoxLayout()
        
        btn_limpar = QPushButton("🗑️ Limpar Carrinho")
        btn_limpar.setProperty("class", "warning")
        btn_limpar.clicked.connect(self._limpar_carrinho)
        btn_layout.addWidget(btn_limpar)
        
        btn_finalizar = QPushButton("✅ FINALIZAR VENDA")
        btn_finalizar.setProperty("class", "success")
        btn_finalizar.setMinimumHeight(50)
        btn_finalizar.clicked.connect(self._finalizar_venda)
        btn_layout.addWidget(btn_finalizar)
        
        layout_direita.addLayout(btn_layout)
        
        widget_direita.setLayout(layout_direita)
        splitter.addWidget(widget_direita)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # Carregar dados iniciais
        self.atualizar_dados()
    
    def atualizar_dados(self):
        """Atualiza produtos e clientes"""
        # Carregar produtos
        self.combo_produto.clear()
        produtos = self.produto_service.listar_produtos(apenas_ativos=True)
        produtos = [p for p in produtos if p.estoque > 0]  # Apenas com estoque
        
        for produto in produtos:
            self.combo_produto.addItem(
                f"{produto.nome} - {produto.marca} ({produto.tipo_animal})",
                produto.id
            )
        
        # Carregar clientes
        self.combo_cliente.clear()
        self.combo_cliente.addItem("Cliente não identificado", None)
        clientes = self.cliente_service.listar_clientes(apenas_ativos=True)
        
        for cliente in clientes:
            self.combo_cliente.addItem(cliente.nome, cliente.id)
    
    def _atualizar_info_produto(self):
        """Atualiza informações do produto selecionado"""
        produto_id = self.combo_produto.currentData()
        if not produto_id:
            return
        
        produto = self.produto_service.buscar_produto(produto_id)
        if produto:
            self.label_estoque.setText(str(produto.estoque))
            self.label_preco.setText(formatar_moeda(produto.preco_venda))
            self.spin_quantidade.setMaximum(produto.estoque)
            self.spin_quantidade.setValue(1)
            self._calcular_subtotal()
    
    def _calcular_subtotal(self):
        """Calcula o subtotal do item"""
        produto_id = self.combo_produto.currentData()
        if not produto_id:
            return
        
        produto = self.produto_service.buscar_produto(produto_id)
        if produto:
            quantidade = self.spin_quantidade.value()
            subtotal = produto.preco_venda * quantidade
            self.label_subtotal.setText(formatar_moeda(subtotal))
    
    def _adicionar_ao_carrinho(self):
        """Adiciona produto ao carrinho"""
        produto_id = self.combo_produto.currentData()
        if not produto_id:
            QMessageBox.warning(self, "Aviso", "Selecione um produto!")
            return
        
        produto = self.produto_service.buscar_produto(produto_id)
        quantidade = self.spin_quantidade.value()
        
        # Verificar se já existe no carrinho
        for item in self.carrinho:
            if item['produto_id'] == produto_id:
                nova_qtd = item['quantidade'] + quantidade
                if nova_qtd > produto.estoque:
                    QMessageBox.warning(
                        self, "Estoque Insuficiente",
                        f"Estoque disponível: {produto.estoque}\nJá no carrinho: {item['quantidade']}"
                    )
                    return
                item['quantidade'] = nova_qtd
                item['subtotal'] = item['quantidade'] * produto.preco_venda
                self._atualizar_tabela_carrinho()
                self._calcular_total()
                return
        
        # Adicionar novo item
        self.carrinho.append({
            'produto_id': produto_id,
            'nome': produto.nome,
            'quantidade': quantidade,
            'preco_unitario': produto.preco_venda,
            'subtotal': quantidade * produto.preco_venda
        })
        
        self._atualizar_tabela_carrinho()
        self._calcular_total()
    
    def _atualizar_tabela_carrinho(self):
        """Atualiza a tabela do carrinho"""
        self.tabela_carrinho.setRowCount(0)
        
        for item in self.carrinho:
            row = self.tabela_carrinho.rowCount()
            self.tabela_carrinho.insertRow(row)
            
            self.tabela_carrinho.setItem(row, 0, QTableWidgetItem(item['nome']))
            self.tabela_carrinho.setItem(row, 1, QTableWidgetItem(str(item['quantidade'])))
            self.tabela_carrinho.setItem(row, 2, QTableWidgetItem(formatar_moeda(item['preco_unitario'])))
            self.tabela_carrinho.setItem(row, 3, QTableWidgetItem(formatar_moeda(item['subtotal'])))
            
            btn_remover = QPushButton("🗑️")
            btn_remover.setProperty("class", "danger")
            btn_remover.clicked.connect(lambda checked, r=row: self._remover_do_carrinho(r))
            self.tabela_carrinho.setCellWidget(row, 4, btn_remover)
    
    def _remover_do_carrinho(self, row):
        """Remove item do carrinho"""
        if 0 <= row < len(self.carrinho):
            self.carrinho.pop(row)
            self._atualizar_tabela_carrinho()
            self._calcular_total()
    
    def _calcular_total(self):
        """Calcula os totais da venda"""
        valor_total = sum(item['subtotal'] for item in self.carrinho)
        desconto = self.spin_desconto.value()
        valor_final = max(0, valor_total - desconto)
        
        self.label_valor_total.setText(formatar_moeda(valor_total))
        self.label_valor_final.setText(formatar_moeda(valor_final))
    
    def _limpar_carrinho(self):
        """Limpa o carrinho"""
        if not self.carrinho:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar",
            "Deseja limpar todo o carrinho?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.carrinho.clear()
            self._atualizar_tabela_carrinho()
            self._calcular_total()
            self.spin_desconto.setValue(0)
    
    def _finalizar_venda(self):
        """Finaliza a venda"""
        if not self.carrinho:
            QMessageBox.warning(self, "Aviso", "Carrinho vazio!")
            return
        
        cliente_id = self.combo_cliente.currentData()
        forma_pagamento = self.combo_pagamento.currentText()
        desconto = self.spin_desconto.value()
        
        # Confirmar venda
        valor_final = sum(item['subtotal'] for item in self.carrinho) - desconto
        
        reply = QMessageBox.question(
            self, "Confirmar Venda",
            f"Finalizar venda no valor de {formatar_moeda(valor_final)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Processar venda
        sucesso, mensagem, venda_id = self.venda_service.criar_venda(
            cliente_id=cliente_id,
            itens=self.carrinho,
            forma_pagamento=forma_pagamento,
            desconto=desconto
        )
        
        if sucesso:
            QMessageBox.information(
                self, "Sucesso",
                f"✅ {mensagem}\n\n💰 Valor: {formatar_moeda(valor_final)}"
            )
            self._limpar_carrinho()
            self.spin_desconto.setValue(0)
            self.atualizar_dados()
        else:
            QMessageBox.critical(self, "Erro", f"❌ {mensagem}")