"""
Serviço de lógica de negócio para Clientes
"""
from typing import List, Optional, Tuple
from database import DatabaseManager, Cliente
from utils.validators import validar_cpf, validar_telefone, validar_email
from utils.formatters import limpar_cpf, limpar_telefone

class ClienteService:
    """Gerencia a lógica de negócio relacionada a clientes"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def _validar_cliente(self, cliente: Cliente, validar_cpf_obrigatorio: bool = True) -> Tuple[bool, str]:
        """Valida todos os campos de um cliente"""
        
        # Validar nome
        if not cliente.nome or len(cliente.nome.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        # Validar CPF (se fornecido ou obrigatório)
        if cliente.cpf:
            cpf_limpo = limpar_cpf(cliente.cpf)
            if cpf_limpo and not validar_cpf(cpf_limpo):
                return False, "CPF inválido"
            cliente.cpf = cpf_limpo
        elif validar_cpf_obrigatorio:
            return False, "CPF é obrigatório"
        
        # Validar telefone
        if not cliente.telefone:
            return False, "Telefone é obrigatório"
        
        telefone_limpo = limpar_telefone(cliente.telefone)
        if not validar_telefone(telefone_limpo):
            return False, "Telefone inválido"
        cliente.telefone = telefone_limpo
        
        # Validar email (se fornecido)
        if cliente.email and not validar_email(cliente.email):
            return False, "E-mail inválido"
        
        return True, ""
    
    def cadastrar_cliente(self, cliente: Cliente, cpf_obrigatorio: bool = False) -> Tuple[bool, str, Optional[int]]:
        """
        Cadastra um novo cliente
        Retorna: (sucesso, mensagem, id_cliente)
        """
        # Validar dados
        valido, mensagem = self._validar_cliente(cliente, cpf_obrigatorio)
        if not valido:
            return False, mensagem, None
        
        # Verificar se CPF já existe (se fornecido)
        if cliente.cpf:
            cliente_existente = self.db.buscar_cliente_por_cpf(cliente.cpf)
            if cliente_existente:
                return False, f"CPF já cadastrado para o cliente '{cliente_existente.nome}'", None
        
        # Criar cliente no banco
        cliente_id = self.db.criar_cliente(cliente)
        
        if cliente_id:
            return True, f"Cliente '{cliente.nome}' cadastrado com sucesso!", cliente_id
        else:
            return False, "Erro ao cadastrar cliente no banco de dados", None
    
    def buscar_cliente(self, cliente_id: int) -> Optional[Cliente]:
        """Busca um cliente pelo ID"""
        return self.db.buscar_cliente(cliente_id)
    
    def buscar_cliente_por_cpf(self, cpf: str) -> Optional[Cliente]:
        """Busca um cliente pelo CPF"""
        cpf_limpo = limpar_cpf(cpf)
        return self.db.buscar_cliente_por_cpf(cpf_limpo)
    
    def listar_clientes(self, apenas_ativos: bool = True) -> List[Cliente]:
        """Lista todos os clientes"""
        return self.db.listar_clientes(apenas_ativos)
    
    def atualizar_cliente(self, cliente_id: int, **kwargs) -> Tuple[bool, str]:
        """
        Atualiza um cliente existente
        Retorna: (sucesso, mensagem)
        """
        # Verificar se cliente existe
        cliente = self.db.buscar_cliente(cliente_id)
        if not cliente:
            return False, f"Cliente ID {cliente_id} não encontrado"
        
        # Validar campos se fornecidos
        if 'cpf' in kwargs and kwargs['cpf']:
            cpf_limpo = limpar_cpf(kwargs['cpf'])
            if not validar_cpf(cpf_limpo):
                return False, "CPF inválido"
            
            # Verificar se CPF já existe para outro cliente
            cliente_existente = self.db.buscar_cliente_por_cpf(cpf_limpo)
            if cliente_existente and cliente_existente.id != cliente_id:
                return False, f"CPF já cadastrado para outro cliente"
            
            kwargs['cpf'] = cpf_limpo
        
        if 'telefone' in kwargs:
            telefone_limpo = limpar_telefone(kwargs['telefone'])
            if not validar_telefone(telefone_limpo):
                return False, "Telefone inválido"
            kwargs['telefone'] = telefone_limpo
        
        if 'email' in kwargs and kwargs['email']:
            if not validar_email(kwargs['email']):
                return False, "E-mail inválido"
        
        # Atualizar no banco
        if self.db.atualizar_cliente(cliente_id, **kwargs):
            return True, "Cliente atualizado com sucesso!"
        else:
            return False, "Erro ao atualizar cliente"
    
    def deletar_cliente(self, cliente_id: int) -> Tuple[bool, str]:
        """
        Desativa um cliente (soft delete)
        Retorna: (sucesso, mensagem)
        """
        cliente = self.db.buscar_cliente(cliente_id)
        if not cliente:
            return False, f"Cliente ID {cliente_id} não encontrado"
        
        if self.db.deletar_cliente(cliente_id):
            return True, f"Cliente '{cliente.nome}' desativado com sucesso!"
        else:
            return False, "Erro ao desativar cliente"
    
    def obter_estatisticas(self) -> dict:
        """Retorna estatísticas gerais dos clientes"""
        clientes = self.db.listar_clientes(apenas_ativos=True)
        
        total_clientes = len(clientes)
        clientes_com_cpf = len([c for c in clientes if c.cpf])
        clientes_com_email = len([c for c in clientes if c.email])
        
        return {
            'total_clientes': total_clientes,
            'clientes_com_cpf': clientes_com_cpf,
            'clientes_com_email': clientes_com_email
        }