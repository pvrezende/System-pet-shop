"""
Widget de gerenciamento de clientes
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QTextEdit
)
from PyQt5.QtCore import Qt
from database.models import Cliente
from utils.formatters import formatar_cpf, formatar_telefone
from utils.validators import validar_cpf, validar_telefone, validar_email


class ClienteDialog(QDialog):
    """Dialog para cadastro/edição de cliente"""
    
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.cliente = cliente
        self.setWindowTitle("✏️ Editar Cliente" if cliente else "➕ Novo Cliente")
        self.setMinimumWidth(500)
        self._init_ui()
        
        if cliente:
            self._carregar_dados()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome completo")
        form_layout.addRow("Nome:*", self.input_nome)
        
        self.input_cpf = QLineEdit()
        self.input_cpf.setPlaceholderText("000.000.000-00")
        self.input_cpf.setMaxLength(14)
        form_layout.addRow("CPF:", self.input_cpf)
        
        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("(00) 00000-0000")
        self.input_telefone.setMaxLength(15)
        form_layout.addRow("Telefone:*", self.input_telefone)
        
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("email@exemplo.com")
        form_layout.addRow("E-mail:", self.input_email)
        
        self.input_endereco = QTextEdit()
        self.input_endereco.setMaximumHeight(80)
        self.input_endereco.setPlaceholderText("Endereço completo...")
        form_layout.addRow("Endereço:", self.input_endereco)
        
        layout.addLayout(form_layout)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def _carregar_dados(self):
        """Carrega dados do cliente no formulário"""
        self.input_nome.setText(self.cliente.nome)
        if self.cliente.cpf:
            self.input_cpf.setText(formatar_cpf(self.cliente.cpf))
        if self.cliente.telefone:
            self.input_telefone.setText(formatar_telefone(self.cliente.telefone))
        if self.cliente.email:
            self.input_email.setText(self.cliente.email)
        if self.cliente.endereco:
            self.input_endereco.setPlainText(self.cliente.endereco)
    
    def get_dados(self):
        """Retorna os dados do formulário"""
        return Cliente(
            id=self.cliente.id if self.cliente else None,
            nome=self.input_nome.text().strip(),
            cpf=self.input_cpf.text().strip(),
            telefone=self.input_telefone.text().strip(),
            email=self.input_email.text().strip(),
            endereco=self.input_endereco.toPlainText().strip()
        )


class ClienteWidget(QWidget):
    """Widget de gerenciamento de clientes"""
    
    def __init__(self, cliente_service):
        super().__init__()
        self.cliente_service = cliente_service
        self._init_ui()
        self.atualizar_lista()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        titulo = QLabel("👥 GERENCIAMENTO DE CLIENTES")
        titulo.setProperty("class", "title")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        btn_novo = QPushButton("➕ Novo Cliente")
        btn_novo.setProperty("class", "success")
        btn_novo.clicked.connect(self._novo_cliente)
        header_layout.addWidget(btn_novo)
        
        layout.addLayout(header_layout)
        
        # Filtro de busca
        filtro_layout = QHBoxLayout()
        
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("🔍 Buscar por nome, CPF, telefone...")
        self.input_busca.textChanged.connect(self.atualizar_lista)
        filtro_layout.addWidget(self.input_busca)
        
        layout.addLayout(filtro_layout)
        
        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "CPF", "Telefone", "E-mail"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.doubleClicked.connect(self._editar_cliente)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        btn_editar = QPushButton("✏️ Editar")
        btn_editar.clicked.connect(self._editar_cliente)
        btn_layout.addWidget(btn_editar)
        
        btn_deletar = QPushButton("🗑️ Desativar")
        btn_deletar.setProperty("class", "danger")
        btn_deletar.clicked.connect(self._deletar_cliente)
        btn_layout.addWidget(btn_deletar)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def atualizar_lista(self):
        """Atualiza a lista de clientes"""
        clientes = self.cliente_service.listar_clientes()
        
        # Filtrar por busca
        busca = self.input_busca.text().lower()
        if busca:
            clientes = [c for c in clientes if 
                       busca in c.nome.lower() or 
                       busca in (c.cpf or '') or 
                       busca in (c.telefone or '')]
        
        self.tabela.setRowCount(0)
        
        for cliente in clientes:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            self.tabela.setItem(row, 0, QTableWidgetItem(str(cliente.id)))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente.nome))
            self.tabela.setItem(row, 2, QTableWidgetItem(
                formatar_cpf(cliente.cpf) if cliente.cpf else "-"
            ))
            self.tabela.setItem(row, 3, QTableWidgetItem(
                formatar_telefone(cliente.telefone) if cliente.telefone else "-"
            ))
            self.tabela.setItem(row, 4, QTableWidgetItem(cliente.email or "-"))
    
    def _novo_cliente(self):
        """Abre dialog para novo cliente"""
        dialog = ClienteDialog(self)
        if dialog.exec_():
            cliente = dialog.get_dados()
            sucesso, mensagem, _ = self.cliente_service.cadastrar_cliente(cliente)
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.atualizar_lista()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
    
    def _editar_cliente(self):
        """Edita o cliente selecionado"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente!")
            return
        
        cliente_id = int(self.tabela.item(row, 0).text())
        cliente = self.cliente_service.buscar_cliente(cliente_id)
        
        if not cliente:
            QMessageBox.critical(self, "Erro", "Cliente não encontrado!")
            return
        
        dialog = ClienteDialog(self, cliente)
        if dialog.exec_():
            dados = dialog.get_dados()
            sucesso, mensagem = self.cliente_service.atualizar_cliente(
                cliente_id,
                nome=dados.nome,
                cpf=dados.cpf,
                telefone=dados.telefone,
                email=dados.email,
                endereco=dados.endereco
            )
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.atualizar_lista()
            else:
                QMessageBox.warning(self, "Erro", mensagem)
    
    def _deletar_cliente(self):
        """Desativa o cliente selecionado"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente!")
            return
        
        cliente_id = int(self.tabela.item(row, 0).text())
        cliente = self.cliente_service.buscar_cliente(cliente_id)
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"Deseja realmente desativar o cliente '{cliente.nome}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            sucesso, mensagem = self.cliente_service.deletar_cliente(cliente_id)
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.atualizar_lista()
            else:
                QMessageBox.warning(self, "Erro", mensagem)