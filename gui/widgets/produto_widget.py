"""
Widget de gerenciamento de produtos
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDoubleSpinBox, QSpinBox, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox, QGroupBox
)
from PyQt5.QtCore import Qt
from database.models import Produto
from utils.formatters import formatar_moeda, formatar_peso
from config.settings import TIPOS_ANIMAIS


class ProdutoDialog(QDialog):
    """Dialog para cadastro/edição de produto"""
    
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.produto = produto
        self.setWindowTitle("✏️ Editar Produto" if produto else "➕ Novo Produto")
        self.setMinimumWidth(500)
        self._init_ui()
        
        if produto:
            self._carregar_dados()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Ex: Royal Canin Adult")
        form_layout.addRow("Nome:*", self.input_nome)
        
        self.input_tipo = QComboBox()
        self.input_tipo.addItems(["cão", "gato"])
        form_layout.addRow("Tipo Animal:*", self.input_tipo)
        
        self.input_marca = QLineEdit()
        self.input_marca.setPlaceholderText("Ex: Royal Canin")
        form_layout.addRow("Marca:*", self.input_marca)
        
        self.input_peso = QDoubleSpinBox()
        self.input_peso.setRange(0.01, 50.0)
        self.input_peso.setValue(1.0)
        self.input_peso.setSuffix(" kg")
        form_layout.addRow("Peso:*", self.input_peso)
        
        self.input_preco_custo = QDoubleSpinBox()
        self.input_preco_custo.setRange(0.0, 999999.99)
        self.input_preco_custo.setPrefix("R$ ")
        self.input_preco_custo.setDecimals(2)
        form_layout.addRow("Preço Custo:", self.input_preco_custo)
        
        self.input_preco_venda = QDoubleSpinBox()
        self.input_preco_venda.setRange(0.01, 999999.99)
        self.input_preco_venda.setPrefix("R$ ")
        self.input_preco_venda.setDecimals(2)
        form_layout.addRow("Preço Venda:*", self.input_preco_venda)
        
        self.input_estoque = QSpinBox()
        self.input_estoque.setRange(0, 999999)
        form_layout.addRow("Estoque Inicial:", self.input_estoque)
        
        self.input_estoque_minimo = QSpinBox()
        self.input_estoque_minimo.setRange(0, 999)
        self.input_estoque_minimo.setValue(5)
        form_layout.addRow("Estoque Mínimo:", self.input_estoque_minimo)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def _carregar_dados(self):
        """Carrega dados do produto no formulário"""
        self.input_nome.setText(self.produto.nome)
        self.input_tipo.setCurrentText(self.produto.tipo_animal)
        self.input_marca.setText(self.produto.marca)
        self.input_peso.setValue(self.produto.peso)
        self.input_preco_custo.setValue(self.produto.preco_custo)
        self.input_preco_venda.setValue(self.produto.preco_venda)
        self.input_estoque.setValue(self.produto.estoque)
        self.input_estoque_minimo.setValue(self.produto.estoque_minimo)
    
    def get_dados(self):
        """Retorna os dados do formulário"""
        return Produto(
            id=self.produto.id if self.produto else None,
            nome=self.input_nome.text().strip(),
            tipo_animal=self.input_tipo.currentText(),
            marca=self.input_marca.text().strip(),
            peso=self.input_peso.value(),
            preco_custo=self.input_preco_custo.value(),
            preco_venda=self.input_preco_venda.value(),
            estoque=self.input_estoque.value(),
            estoque_minimo=self.input_estoque_minimo.value()
        )


class ProdutoWidget(QWidget):
    """Widget de gerenciamento de produtos"""
    
    def __init__(self, produto_service, estoque_service):
        super().__init__()
        self.produto_service = produto_service
        self.estoque_service = estoque_service
        self._init_ui()
        self.atualizar_lista()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        titulo = QLabel("📦 GERENCIAMENTO DE PRODUTOS")
        titulo.setProperty("class", "title")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        btn_novo = QPushButton("➕ Novo Produto")
        btn_novo.setProperty("class", "success")
        btn_novo.clicked.connect(self._novo_produto)
        header_layout.addWidget(btn_novo)
        
        layout.addLayout(header_layout)
        
        # Filtros
        filtro_layout = QHBoxLayout()
        
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("🔍 Buscar por nome, marca...")
        self.input_busca.textChanged.connect(self.atualizar_lista)
        filtro_layout.addWidget(self.input_busca)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "cão", "gato"])
        self.combo_tipo.currentTextChanged.connect(self.atualizar_lista)
        filtro_layout.addWidget(self.combo_tipo)
        
        layout.addLayout(filtro_layout)
        
        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "Tipo", "Marca", "Peso", "Preço Custo", 
            "Preço Venda", "Estoque", "Status"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.doubleClicked.connect(self._editar_produto)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        btn_editar = QPushButton("✏️ Editar")
        btn_editar.clicked.connect(self._editar_produto)
        btn_layout.addWidget(btn_editar)
        
        btn_entrada = QPushButton("📥 Entrada Estoque")
        btn_entrada.setProperty("class", "success")
        btn_entrada.clicked.connect(self._entrada_estoque)
        btn_layout.addWidget(btn_entrada)
        
        btn_saida = QPushButton("📤 Saída Estoque")
        btn_saida.setProperty("class", "warning")
        btn_saida.clicked.connect(self._saida_estoque)
        btn_layout.addWidget(btn_saida)
        
        btn_deletar = QPushButton("🗑️ Desativar")
        btn_deletar.setProperty("class", "danger")
        btn_deletar.clicked.connect(self._deletar_produto)
        btn_layout.addWidget(btn_deletar)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def atualizar_lista(self):
        """Atualiza a lista de produtos"""
        tipo_filtro = self.combo_tipo.currentText()
        tipo = None if tipo_filtro == "Todos" else tipo_filtro
        
        produtos = self.produto_service.listar_produtos(tipo)
        
        # Filtrar por busca
        busca = self.input_busca.text().lower()
        if busca:
            produtos = [p for p in produtos if 
                       busca in p.nome.lower() or busca in p.marca.lower()]
        
        self.tabela.setRowCount(0)
        
        for produto in produtos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            self.tabela.setItem(row, 0, QTableWidgetItem(str(produto.id)))
            self.tabela.setItem(row, 1, QTableWidgetItem(produto.nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(produto.tipo_animal.upper()))
            self.tabela.setItem(row, 3, QTableWidgetItem(produto.marca))
            self.tabela.setItem(row, 4, QTableWidgetItem(formatar_peso(produto.peso)))
            self.tabela.setItem(row, 5, QTableWidgetItem(formatar_moeda(produto.preco_custo)))
            self.tabela.setItem(row, 6, QTableWidgetItem(formatar_moeda(produto.preco_venda)))
            self.tabela.setItem(row, 7, QTableWidgetItem(str(produto.estoque)))
            
            # Status
            item_status = QTableWidgetItem(produto.status_estoque)
            if produto.status_estoque == "SEM ESTOQUE":
                item_status.setForeground(Qt.red)
            elif produto.status_estoque == "CRÍTICO":
                item_status.setForeground(Qt.darkRed)
            elif produto.status_estoque == "BAIXO":
                item_status.setForeground(Qt.darkYellow)
            else:
                item_status.setForeground(Qt.darkGreen)
            
            self.tabela.setItem(row, 8, item_status)
    
    def _novo_produto(self):
        """Abre dialog para novo produto"""
        dialog = ProdutoDialog(self)
        if dialog.exec_():
            produto = dialog.get_dados()
            sucesso, mensagem, _ = self.produto_service.cadastrar_produto(produto)
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.atualizar_lista()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
    
    def _editar_produto(self):
        """Edita o produto selecionado"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um produto!")
            return
        
        produto_id = int(self.tabela.item(row, 0).text())
        produto = self.produto_service.buscar_produto(produto_id)
        
        if not produto:
            QMessageBox.critical(self, "Erro", "Produto não encontrado!")
            return
        
        dialog = ProdutoDialog(self, produto)
        if dialog.exec_():
            dados = dialog.get_dados()
            sucesso, mensagem = self.produto_service.atualizar_produto(
                produto_id,
                nome=dados.nome,
                tipo_animal=dados.tipo_animal,
                marca=dados.marca,
                peso=dados.peso,
                preco_custo=dados.preco_custo,
                preco_venda=dados.preco_venda,
                estoque_minimo=dados.estoque_minimo
            )
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.atualizar_lista()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
    
    def _entrada_estoque(self):
        """Registra entrada de estoque"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um produto!")
            return
        
        produto_id = int(self.tabela.item(row, 0).text())
        produto = self.produto_service.buscar_produto(produto_id)
        
        from PyQt5.QtWidgets import QInputDialog
        quantidade, ok = QInputDialog.getInt(
            self, "Entrada de Estoque",
            f"Produto: {produto.nome}\nEstoque atual: {produto.estoque}\n\nQuantidade de entrada:",
            1, 1, 9999
        )
        
        if ok:
            sucesso, mensagem = self.estoque_service.entrada_estoque(
                produto_id, quantidade, "Entrada manual"
            )
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.atualizar_lista()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
    
    def _saida_estoque(self):
        """Registra saída de estoque"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um produto!")
            return
        
        produto_id = int(self.tabela.item(row, 0).text())
        produto = self.produto_service.buscar_produto(produto_id)
        
        from PyQt5.QtWidgets import QInputDialog
        quantidade, ok = QInputDialog.getInt(
            self, "Saída de Estoque",
            f"Produto: {produto.nome}\nEstoque atual: {produto.estoque}\n\nQuantidade de saída:",
            1, 1, produto.estoque
        )
        
        if ok:
            sucesso, mensagem = self.estoque_service.saida_estoque(
                produto_id, quantidade, "Saída manual"
            )
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.atualizar_lista()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
    
    def _deletar_produto(self):
        """Desativa o produto selecionado"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um produto!")
            return
        
        produto_id = int(self.tabela.item(row, 0).text())
        produto = self.produto_service.buscar_produto(produto_id)
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"Deseja realmente desativar o produto '{produto.nome}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            sucesso, mensagem = self.produto_service.deletar_produto(produto_id)
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.atualizar_lista()
            else:
                QMessageBox.warning(self, "Erro", mensagem)