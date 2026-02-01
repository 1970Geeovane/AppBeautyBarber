# --- SIMULAÇÃO DE BANCO DE DADOS EM MEMÓRIA ---
database = {
    'administradores': {}, # {id: Admin_obj}
    'gerentes': {},
    'profissionais': {},
    'clientes': {},
    'produtos': {},
    'servicos': {},
    'transacoes': {},
}

# ID Sequencial Simples
next_id = 1

def get_next_id():
    global next_id
    current_id = next_id
    next_id += 1
    return current_id

# --- CLASSES MODELO ---

class Pessoa:
    def __init__(self, nome, telefone, email):
        self.id = get_next_id()
        self.nome = nome
        self.telefone = telefone
        self.email = email

class Usuario(Pessoa):
    def __init__(self, nome, telefone, email, login, senha, nivel_acesso):
        super().__init__(nome, telefone, email)
        self.login = login
        self.senha = senha  # Em um sistema real, use hashing de senhas!
        self.nivel_acesso = nivel_acesso # 'Admin', 'Gerente', 'Profissional'

class Administrador(Usuario):
    def __init__(self, nome, telefone, email, login, senha):
        # Nível 3 (Máximo)
        super().__init__(nome, telefone, email, login, senha, 'Admin')
        
        # O sistema só permite até 3 Administradores
        if len(database['administradores']) >= 3:
             raise Exception("Limite de 3 administradores atingido.")
        database['administradores'][self.id] = self

class Gerente(Usuario):
    def __init__(self, nome, telefone, email, login, senha):
        # Nível 2
        super().__init__(nome, telefone, email, login, senha, 'Gerente')
        self.permissoes = {} # Ex: {'cadastrar_cliente': True, 'visualizar_caixa': False}
        database['gerentes'][self.id] = self

class Profissional(Usuario):
    def __init__(self, nome, telefone, email, login, senha, comissao_percentual):
        # Nível 1
        super().__init__(nome, telefone, email, login, senha, 'Profissional')
        self.comissao_percentual = comissao_percentual
        database['profissionais'][self.id] = self

class Cliente(Pessoa):
    def __init__(self, nome, telefone, email):
        super().__init__(nome, telefone, email)
        self.historico_servicos = []
        database['clientes'][self.id] = self

class Servico:
    def __init__(self, nome, preco, comissao_padrao):
        self.id = get_next_id()
        self.nome = nome
        self.preco = preco
        self.comissao_padrao = comissao_padrao # %
        database['servicos'][self.id] = self

# --- CLASSE CAIXA E TRANSAÇÕES ---
class Caixa:
    def __init__(self):
        self.saldo_dinheiro = 0.0
        self.saldo_cartao = 0.0
        self.saldo_pix = 0.0
        self.historico_transacoes = database['transacoes']

    def registrar_venda(self, servico_id, profissional_id, forma_pagamento):
        servico = database['servicos'].get(servico_id)
        profissional = database['profissionais'].get(profissional_id)
        
        if not servico or not profissional:
            return "Erro: Serviço ou Profissional não encontrado."

        valor = servico.preco
        
        # 1. Atualizar Saldo do Caixa
        if forma_pagamento == 'Dinheiro':
            self.saldo_dinheiro += valor
        elif forma_pagamento == 'Cartao':
            self.saldo_cartao += valor
        elif forma_pagamento == 'Pix':
            self.saldo_pix += valor
        else:
            return "Forma de pagamento inválida."
            
        # 2. Registrar Transação
        transacao_id = get_next_id()
        database['transacoes'][transacao_id] = {
            'id': transacao_id,
            'data': '2025-10-10', # Usar datetime.now() em um sistema real
            'tipo': 'Serviço',
            'valor_bruto': valor,
            'forma_pagamento': forma_pagamento,
            'profissional_id': profissional_id,
            'comissao': valor * (profissional.comissao_percentual / 100.0)
        }
        
        return f"Venda de R$ {valor:.2f} registrada com sucesso. Comissão: R$ {database['transacoes'][transacao_id]['comissao']:.2f}"

# --- CLASSE DE GERENCIAMENTO DE PERMISSÕES (ADMIN) ---
class SistemaPermissoes:
    
    def liberar_permissao_gerente(self, admin_id, gerente_id, permissao, status):
        """Permite que um Admin libere ou restrinja uma permissão para um Gerente."""
        if admin_id not in database['administradores']:
            return "Somente administradores podem alterar permissões."

        gerente = database['gerentes'].get(gerente_id)
        if not gerente:
            return "Gerente não encontrado."
            
        # Lista de permissões possíveis (exemplo)
        permissoes_validas = ['cadastrar_cliente', 'visualizar_relatorios', 'gerenciar_estoque']
        if permissao not in permissoes_validas:
             return "Permissão inválida."

        gerente.permissoes[permissao] = status # True/False
        return f"Permissão '{permissao}' definida para {gerente.nome}: {status}"
        
# --- CLASSE DE FOLHA DE PAGAMENTO ---
class FolhaPagamento:
    
    def calcular_pagamentos(self):
        pagamentos_a_fazer = {}
        
        # 1. Pagamento Mensal (Outros Colaboradores/Gerentes/Admin)
        # O valor mensal e a lista de colaboradores que recebem fixo deveriam estar cadastrados
        
        # 2. Pagamento por Comissão (Profissionais)
        comissoes = {}
        for transacao in database['transacoes'].values():
            p_id = transacao['profissional_id']
            comissao = transacao['comissao']
            
            comissoes[p_id] = comissoes.get(p_id, 0.0) + comissao
            
        # Simula o registro na Folha de Pagamento
        for p_id, valor in comissoes.items():
            pagamentos_a_fazer[database['profissionais'][p_id].nome] = f"Comissão: R$ {valor:.2f}"
            # Em um sistema real, isso geraria um débito do caixa
            
        return pagamentos_a_fazer

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO (Adaptadas para não usar input) ---

def cadastrar_administrador(nome, telefone, email, login, senha):
    try:
        admin = Administrador(nome, telefone, email, login, senha)
        return f"Administrador '{admin.nome}' cadastrado com sucesso! ID: {admin.id}"
    except Exception as e:
        return f"Erro ao cadastrar: {e}"

def cadastrar_gerente(nome, telefone, email, login, senha):
    try:
        gerente = Gerente(nome, telefone, email, login, senha)
        return f"Gerente '{gerente.nome}' cadastrado com sucesso! ID: {gerente.id}"
    except Exception as e:
        return f"Erro ao cadastrar: {e}"

def cadastrar_profissional(nome, telefone, email, login, senha, comissao):
    try:
        prof = Profissional(nome, telefone, email, login, senha, float(comissao))
        return f"Profissional '{prof.nome}' cadastrado com sucesso! ID: {prof.id}"
    except Exception as e:
        return f"Erro ao cadastrar: {e}"

def cadastrar_cliente(nome, telefone, email):
    try:
        cliente = Cliente(nome, telefone, email)
        return f"Cliente '{cliente.nome}' cadastrado com sucesso! ID: {cliente.id}"
    except Exception as e:
        return f"Erro ao cadastrar: {e}"

def cadastrar_servico(nome, preco, comissao):
    try:
        servico = Servico(nome, float(preco), float(comissao))
        return f"Serviço '{servico.nome}' cadastrado com sucesso! ID: {servico.id}"
    except Exception as e:
        return f"Erro ao cadastrar: {e}"

def excluir_cadastro(tipo_cadastro, item_id):
    """Exclui um item de um tipo de cadastro específico pelo ID."""
    # Converte o tipo de singular para plural, se necessário (ex: 'admin' -> 'administradores')
    tipo_db = f"{tipo_cadastro}s" if not tipo_cadastro.endswith('s') else tipo_cadastro
    
    if tipo_db not in database or tipo_db == 'transacoes':
        return f"Erro: Tipo de cadastro '{tipo_cadastro}' inválido."

    try:
        item_id_int = int(item_id)
        if item_id_int in database[tipo_db]:
            item_removido = database[tipo_db].pop(item_id_int)
            return f"{tipo_cadastro.capitalize()} '{item_removido.nome}' (ID: {item_id_int}) foi excluído com sucesso."
        else:
            return f"Erro: Item com ID {item_id_int} não encontrado em {tipo_db}."
    except (ValueError, KeyError) as e:
        return f"Erro ao processar a exclusão: {e}"

def listar_cadastros_formatado():
    """Retorna uma string formatada com a lista de todos os cadastros."""
    output = "--- LISTA DE CADASTRADOS ---\n"
    for tipo, cadastros in database.items():
        if tipo == 'transacoes': continue
        output += f"\n# {tipo.upper()}:\n"
        if not cadastros:
            output += "  Nenhum cadastro.\n"
        else:
            for id, obj in cadastros.items():
                output += f"  ID: {id}, Nome: {obj.nome}\n"
    output += "\n----------------------------\n"
    return output

def get_all_cadastros():
    """Retorna o dicionário de banco de dados de forma estruturada, exceto transações."""
    cadastros = {k: v for k, v in database.items() if k != 'transacoes'}
    return cadastros