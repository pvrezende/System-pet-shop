"""
Janela principal do sistema Pet Shop
"""
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QMessageBox, 
    QWidget, QVBoxLayout, QMenuBar, QMenu, QAction
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from datetime import datetime

from database import DatabaseManager
from business import ProdutoService, ClienteService, VendaService, EstoqueService
from config.settings import APP_CONFIG
from .widgets.dashboard_widget import DashboardWidget
from .widgets.produto_widget import ProdutoWidget
from .widgets.cliente_widget import ClienteWidget
from .widgets.venda_widget import VendaWidget


class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self):
        super().__init__()
        
        # Inicializar banco de dados e serviços
        self.db = DatabaseManager()
        self.produto_service = ProdutoService(self.db)
        self.cliente_service = ClienteService(self.db)
        self.venda_service = VendaService(self.db)
        self.estoque_service = EstoqueService(self.db)
        
        self._init_ui()
        self._carregar_estilos()
        self._criar_menu()
        self._atualizar_status_bar()
        
        # Timer para atualizar statusbar a cada 60 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self._atualizar_status_bar)
        self.timer.start(60000)  # 60 segundos
    
    def _init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle(APP_CONFIG['window_title'])
        self.setMinimumSize(APP_CONFIG['min_width'], APP_CONFIG['min_height'])
        
        # Widget central com tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Criar widgets das abas
        self.dashboard_widget = DashboardWidget(
            self.produto_service,
            self.venda_service,
            self.estoque_service,
            self.cliente_service
        )
        self.produto_widget = ProdutoWidget(self.produto_service, self.estoque_service)
        self.cliente_widget = ClienteWidget(self.cliente_service)
        self.venda_widget = VendaWidget(
            self.venda_service,
            self.produto_service,
            self.cliente_service
        )
        
        # Adicionar abas
        self.tabs.addTab(self.dashboard_widget, "🏠 Dashboard")
        self.tabs.addTab(self.venda_widget, "💰 Vendas")
        self.tabs.addTab(self.produto_widget, "📦 Produtos")
        self.tabs.addTab(self.cliente_widget, "👥 Clientes")
        
        # Conectar sinal de mudança de aba
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def _carregar_estilos(self):
        """Carrega o arquivo de estilos CSS"""
        try:
            from pathlib import Path
            style_path = Path(__file__).parent / 'styles' / 'styles.qss'
            
            if style_path.exists():
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            else:
                print(f"⚠️ Arquivo de estilos não encontrado: {style_path}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar estilos: {e}")
    
    def _criar_menu(self):
        """Cria o menu da aplicação"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        menu_arquivo = menubar.addMenu("&Arquivo")
        
        action_backup = QAction("💾 Fazer Backup", self)
        action_backup.setShortcut("Ctrl+B")
        action_backup.triggered.connect(self._fazer_backup)
        menu_arquivo.addAction(action_backup)
        
        menu_arquivo.addSeparator()
        
        action_sair = QAction("🚪 Sair", self)
        action_sair.setShortcut("Ctrl+Q")
        action_sair.triggered.connect(self.close)
        menu_arquivo.addAction(action_sair)
        
        # Menu Relatórios
        menu_relatorios = menubar.addMenu("&Relatórios")
        
        action_rel_produtos = QAction("📊 Relatório de Produtos", self)
        action_rel_produtos.triggered.connect(self._gerar_relatorio_produtos)
        menu_relatorios.addAction(action_rel_produtos)
        
        action_rel_vendas = QAction("💰 Relatório de Vendas", self)
        action_rel_vendas.triggered.connect(self._gerar_relatorio_vendas)
        menu_relatorios.addAction(action_rel_vendas)
        
        action_rel_estoque = QAction("📦 Relatório de Estoque", self)
        action_rel_estoque.triggered.connect(self._gerar_relatorio_estoque)
        menu_relatorios.addAction(action_rel_estoque)
        
        # Menu Ajuda
        menu_ajuda = menubar.addMenu("&Ajuda")
        
        action_sobre = QAction("ℹ️ Sobre", self)
        action_sobre.triggered.connect(self._mostrar_sobre)
        menu_ajuda.addAction(action_sobre)
    
    def _atualizar_status_bar(self):
        """Atualiza a barra de status com informações do sistema"""
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Verificar alertas de estoque
        alertas = self.estoque_service.produtos_alertas()
        total_alertas = len(alertas['sem_estoque']) + len(alertas['critico']) + len(alertas['baixo'])
        
        if total_alertas > 0:
            status_text = f"⚠️ {total_alertas} alertas de estoque  |  "
        else:
            status_text = "✅ Estoque OK  |  "
        
        status_text += f"🕐 {agora}  |  📍 {APP_CONFIG['company']}"
        
        self.status_bar.showMessage(status_text)
    
    def _on_tab_changed(self, index):
        """Callback quando a aba é alterada"""
        # Atualizar dashboard quando voltar para ele
        if index == 0:  # Dashboard
            self.dashboard_widget.atualizar_dados()
        elif index == 1:  # Vendas
            self.venda_widget.atualizar_dados()
        elif index == 2:  # Produtos
            self.produto_widget.atualizar_lista()
        elif index == 3:  # Clientes
            self.cliente_widget.atualizar_lista()
        
        self._atualizar_status_bar()
    
    def _fazer_backup(self):
        """Faz backup do banco de dados"""
        if self.db.criar_backup():
            QMessageBox.information(
                self,
                "Backup",
                "✅ Backup criado com sucesso!\n\nO arquivo foi salvo na pasta 'backups'."
            )
        else:
            QMessageBox.critical(
                self,
                "Erro",
                "❌ Erro ao criar backup do banco de dados."
            )
    
    def _gerar_relatorio_produtos(self):
        """Gera relatório de produtos"""
        QMessageBox.information(
            self,
            "Relatório",
            "📊 Funcionalidade de relatório de produtos será implementada em breve!"
        )
    
    def _gerar_relatorio_vendas(self):
        """Gera relatório de vendas"""
        QMessageBox.information(
            self,
            "Relatório",
            "💰 Funcionalidade de relatório de vendas será implementada em breve!"
        )
    
    def _gerar_relatorio_estoque(self):
        """Gera relatório de estoque"""
        QMessageBox.information(
            self,
            "Relatório",
            "📦 Funcionalidade de relatório de estoque será implementada em breve!"
        )
    
    def _mostrar_sobre(self):
        """Mostra informações sobre o sistema"""
        QMessageBox.about(
            self,
            "Sobre",
            f"""
            <h2>{APP_CONFIG['name']}</h2>
            <p><b>Versão:</b> {APP_CONFIG['version']}</p>
            <p><b>Desenvolvido por:</b> {APP_CONFIG['company']}</p>
            <br>
            <p>Sistema completo de gerenciamento para Pet Shops</p>
            <p>Inclui controle de produtos, vendas, clientes e estoque.</p>
            <br>
            <p><i>© 2024 - Todos os direitos reservados</i></p>
            """
        )
    
    def closeEvent(self, event):
        """Evento de fechamento da janela"""
        reply = QMessageBox.question(
            self,
            'Sair',
            '🚪 Deseja realmente sair do sistema?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()