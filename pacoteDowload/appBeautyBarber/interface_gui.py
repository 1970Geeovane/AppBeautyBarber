import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Label, Entry, Button, filedialog
from PIL import Image, ImageTk

# Importa as funções de lógica de negócio do outro arquivo
import appBB

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BeautyBarber - Sistema de Gestão")
        self.root.geometry("800x600")

        # --- Frame Principal ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Frame de Botões (Menu Lateral) ---
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(button_frame, text="Cadastros", font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Button(button_frame, text="Cadastrar Administrador", command=self.abrir_janela_admin).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Cadastrar Gerente", command=self.abrir_janela_gerente).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Cadastrar Profissional", command=self.abrir_janela_profissional).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Cadastrar Cliente", command=self.abrir_janela_cliente).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Cadastrar Serviço", command=self.abrir_janela_servico).pack(fill=tk.X, pady=5)

        ttk.Separator(button_frame, orient='horizontal').pack(fill='x', pady=20)

        ttk.Label(button_frame, text="Visualizar", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.tipos_cadastro = ['Todos', 'Administrador', 'Gerente', 'Profissional', 'Clientes', 'Serviços', 'Produtos']
        self.tipo_selecionado = tk.StringVar(value=self.tipos_cadastro[0])
        
        ttk.Label(button_frame, text="Tipo de Cadastro:").pack(fill=tk.X, pady=(0, 2))
        self.combo_tipos = ttk.Combobox(button_frame, textvariable=self.tipo_selecionado, values=self.tipos_cadastro, state="readonly")
        self.combo_tipos.pack(fill=tk.X, pady=(0, 5))
        self.combo_tipos.bind("<<ComboboxSelected>>", self.listar_cadastros)

        ttk.Label(button_frame, text="Ações", font=("Arial", 14, "bold")).pack(pady=(15, 10))
        ttk.Button(button_frame, text="Excluir Selecionado", command=self.excluir_item_selecionado).pack(fill=tk.X, pady=5)
        
        ttk.Separator(button_frame, orient='horizontal').pack(fill='x', pady=20)
        
        ttk.Label(button_frame, text="Customização", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Button(button_frame, text="Carregar Logo", command=self.carregar_logo).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Definir Fundo", command=self.definir_imagem_fundo).pack(fill=tk.X, pady=5)

        # --- Frame de Conteúdo (Área de Exibição) ---
        content_frame = ttk.Frame(main_frame, padding="10")
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Usar um Canvas permite colocar uma imagem de fundo
        self.canvas = tk.Canvas(content_frame, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Label para exibir a logo
        self.logo_label = ttk.Label(content_frame)

        # Tabela (Treeview) para exibir os cadastros
        columns = ('id', 'nome', 'tipo', 'detalhes')
        self.tree = ttk.Treeview(self.canvas, columns=columns, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='Nome')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('detalhes', text='Detalhes')
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('tipo', width=100, anchor='center')

        # Scrollbar para a tabela
        scrollbar = ttk.Scrollbar(self.canvas, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        # Adiciona os widgets ao canvas
        self.canvas.create_window(5, 5, window=self.logo_label, anchor="nw")
        self.canvas.create_window(5, 120, window=self.tree, anchor="nw")
        self.canvas.create_window(0, 0, window=scrollbar, anchor="ne") # Posição inicial, será ajustada

        # Ajusta o tamanho dos widgets quando a janela é redimensionada
        def on_resize(event):
            self.canvas.itemconfig(2, width=event.width - 25, height=event.height - 125) # Ajusta a Treeview
            self.canvas.coords(3, event.width, 120) # Move a scrollbar
            self.canvas.itemconfigure(3, height=event.height - 125) # Ajusta altura da scrollbar
        self.canvas.bind("<Configure>", on_resize)

    def definir_imagem_fundo(self):
        """Abre um diálogo para selecionar uma imagem e a define como fundo do canvas."""
        filepath = filedialog.askopenfilename(title="Selecione uma imagem de fundo", filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not filepath: return
        
        image = Image.open(filepath)
        self.background_image = ImageTk.PhotoImage(image) # Guardar referência
        self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")

    def carregar_logo(self):
        """Abre um diálogo para selecionar uma imagem e a exibe no label."""
        filepath = filedialog.askopenfilename(title="Selecione um arquivo de imagem", filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if not filepath:
            return

        # Abrir a imagem com o Pillow, redimensionar e converter para o Tkinter
        image = Image.open(filepath)
        image.thumbnail((200, 100)) # Redimensiona mantendo a proporção (max 200x100)
        
        # Guardar referência da imagem para evitar que seja coletada pelo garbage collector
        self.logo_image = ImageTk.PhotoImage(image)
        
        self.logo_label.config(image=self.logo_image)

    def listar_cadastros(self, event=None):
        """Busca os dados e os exibe na tabela (Treeview)."""
        # Limpa a tabela antes de preencher
        for i in self.tree.get_children():
            self.tree.delete(i)

        tipo_a_listar = self.tipo_selecionado.get().lower()

        # Busca os dados estruturados
        todos_cadastros = appBB.get_all_cadastros()

        for tipo, cadastros in todos_cadastros.items():
            # Se não for 'todos', filtra pelo tipo selecionado
            if tipo_a_listar != 'todos':
                # Converte o tipo singular do menu para o plural do banco de dados
                if tipo_a_listar == 'administrador':
                    tipo_db = 'administradores'
                elif tipo_a_listar == 'profissional':
                    tipo_db = 'profissionais'
                else:
                    tipo_db = f"{tipo_a_listar}s" if not tipo_a_listar.endswith('s') else tipo_a_listar
                if tipo != tipo_db:
                    continue

            # Remove o 's' final para singularizar (ex: 'clientes' -> 'cliente')
            if tipo == 'profissionais':
                tipo_singular = 'profissional' # Caso especial
            elif tipo == 'administradores':
                tipo_singular = tipo[:-2]
            elif tipo.endswith('s'):
                tipo_singular = tipo[:-1]
            else:
                tipo_singular = tipo
            
            if cadastros:
                for id_obj, obj in cadastros.items():
                    detalhes = ""
                    if hasattr(obj, 'email'):
                        detalhes += f"Email: {obj.email}"
                    if hasattr(obj, 'comissao_percentual'):
                        detalhes += f" | Comissão: {obj.comissao_percentual}%"
                    if hasattr(obj, 'preco'):
                        detalhes = f"Preço: R$ {obj.preco:.2f}"
                    
                    self.tree.insert('', tk.END, values=(obj.id, obj.nome, tipo_singular.capitalize(), detalhes))

    def excluir_item_selecionado(self):
        """Exclui o item selecionado na tabela."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um item na lista para excluir.")
            return

        item_details = self.tree.item(selected_item)
        item_id = item_details['values'][0]
        item_nome = item_details['values'][1]
        item_tipo = item_details['values'][2].lower()

        # Confirmação
        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir '{item_nome}' (ID: {item_id})?"
        )

        if confirmar:
            resultado = appBB.excluir_cadastro(item_tipo, item_id)
            messagebox.showinfo("Resultado da Exclusão", resultado)
            # Atualiza a lista após a exclusão
            self.listar_cadastros()

    # --- PÁGINAS DE CADASTRO INDIVIDUAIS ---

    def _criar_janela_base(self, titulo):
        """Cria uma janela Toplevel padrão para os formulários."""
        janela = Toplevel(self.root)
        janela.title(titulo)
        janela.transient(self.root)
        janela.grab_set()
        return janela

    def abrir_janela_cliente(self):
        janela = self._criar_janela_base("Cadastro de Cliente")

        # Campos
        Label(janela, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        nome_entry = Entry(janela)
        nome_entry.grid(row=0, column=1, padx=10, pady=5)

        Label(janela, text="Telefone:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tel_entry = Entry(janela)
        tel_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(janela, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        email_entry = Entry(janela)
        email_entry.grid(row=2, column=1, padx=10, pady=5)

        def salvar():
            resultado = appBB.cadastrar_cliente(nome_entry.get(), tel_entry.get(), email_entry.get())
            messagebox.showinfo("Resultado", resultado, parent=janela)
            janela.destroy()
            self.listar_cadastros()

        Button(janela, text="Salvar", command=salvar).grid(row=3, column=0, columnspan=2, pady=10)

    def abrir_janela_servico(self):
        janela = self._criar_janela_base("Cadastro de Serviço")

        # Campos
        Label(janela, text="Nome do Serviço:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        nome_entry = Entry(janela)
        nome_entry.grid(row=0, column=1, padx=10, pady=5)

        Label(janela, text="Preço (R$):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        preco_entry = Entry(janela)
        preco_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(janela, text="Comissão Padrão (%):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        comissao_entry = Entry(janela)
        comissao_entry.grid(row=2, column=1, padx=10, pady=5)

        def salvar():
            resultado = appBB.cadastrar_servico(nome_entry.get(), preco_entry.get(), comissao_entry.get())
            messagebox.showinfo("Resultado", resultado, parent=janela)
            janela.destroy()
            self.listar_cadastros()

        Button(janela, text="Salvar", command=salvar).grid(row=3, column=0, columnspan=2, pady=10)

    def _abrir_janela_usuario(self, tipo):
        """Função auxiliar para criar janelas de Admin, Gerente e Profissional."""
        titulo = f"Cadastro de {tipo.capitalize()}"
        janela = self._criar_janela_base(titulo)
        comissao_entry = None # Inicializa a variável

        # Campos comuns de usuário
        Label(janela, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        nome_entry = Entry(janela)
        nome_entry.grid(row=0, column=1, padx=10, pady=5)

        Label(janela, text="Telefone:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tel_entry = Entry(janela)
        tel_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(janela, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        email_entry = Entry(janela)
        email_entry.grid(row=2, column=1, padx=10, pady=5)

        Label(janela, text="Login:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        login_entry = Entry(janela)
        login_entry.grid(row=3, column=1, padx=10, pady=5)

        Label(janela, text="Senha:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        senha_entry = Entry(janela, show="*")
        senha_entry.grid(row=4, column=1, padx=10, pady=5)

        # Campo específico de profissional
        if tipo == 'profissional':
            Label(janela, text="Comissão (%):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
            comissao_entry = Entry(janela)
            comissao_entry.grid(row=5, column=1, padx=10, pady=5)
            row_final = 6
        else:
            row_final = 5

        def salvar():
            resultado = ""
            if tipo == 'admin':
                resultado = appBB.cadastrar_administrador(nome_entry.get(), tel_entry.get(), email_entry.get(), login_entry.get(), senha_entry.get())
            elif tipo == 'gerente':
                resultado = appBB.cadastrar_gerente(nome_entry.get(), tel_entry.get(), email_entry.get(), login_entry.get(), senha_entry.get())
            elif tipo == 'profissional':
                resultado = appBB.cadastrar_profissional(nome_entry.get(), tel_entry.get(), email_entry.get(), login_entry.get(), senha_entry.get(), comissao_entry.get())
            
            messagebox.showinfo("Resultado", resultado, parent=janela)
            janela.destroy()
            self.listar_cadastros()

        Button(janela, text="Salvar", command=salvar).grid(row=row_final, column=0, columnspan=2, pady=10)

    def abrir_janela_admin(self):
        self._abrir_janela_usuario('admin')

    def abrir_janela_gerente(self):
        self._abrir_janela_usuario('gerente')

    def abrir_janela_profissional(self):
        self._abrir_janela_usuario('profissional')

def main():
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()