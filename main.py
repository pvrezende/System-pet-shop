"""
Ponto de entrada da aplicação Pet Shop
"""
import sys
import os

# Garantir que o diretório atual está no path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from PyQt5.QtWidgets import QApplication
    print("✅ PyQt5 importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar PyQt5: {e}")
    sys.exit(1)

try:
    from gui.main_window import MainWindow
    print("✅ MainWindow importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar MainWindow: {e}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Conteúdo da pasta gui:")
    if os.path.exists('gui'):
        print(os.listdir('gui'))
    sys.exit(1)


def main():
    """Função principal"""
    print("🚀 Iniciando aplicação Pet Shop...")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    print("✅ Janela aberta com sucesso!")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()