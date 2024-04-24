import tkinter as tk
from tkinter import messagebox, simpledialog  # Importe simpledialog
import hashlib
import psycopg2

class PasswordManager:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS passwords
                            (username TEXT PRIMARY KEY, hashed_password TEXT)''')
        self.conn.commit()

    def add_or_update_password(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM passwords WHERE username = %s)", (username,))
        exists = self.cur.fetchone()[0]
        if exists:
            self.cur.execute("UPDATE passwords SET hashed_password = %s WHERE username = %s", (hashed_password, username))
        else:
            self.cur.execute("INSERT INTO passwords VALUES (%s, %s)", (username, hashed_password))
        self.conn.commit()

    def verify_password(self, username, password):
        self.cur.execute("SELECT hashed_password FROM passwords WHERE username=%s", (username,))
        result = self.cur.fetchone()
        if result:
            hashed_password = result[0]
            input_hashed_password = hashlib.sha256(password.encode()).hexdigest()
            return hashed_password == input_hashed_password
        else:
            return False

    def list_passwords(self):
        self.cur.execute("SELECT * FROM passwords")
        rows = self.cur.fetchall()
        return [(row[0], row[1]) for row in rows]

    def delete_user(self, username):
        self.cur.execute("DELETE FROM passwords WHERE username=%s", (username,))
        self.conn.commit()

class PasswordManagerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Password Manager")

        # Crie uma instância da classe PasswordManager
        self.pm = PasswordManager(dbname='Inicio', user='moretto', password='incorreta')

        self.label = tk.Label(master, text="Menu:")
        self.label.pack()

        self.add_button = tk.Button(master, text="Adicionar ou atualizar usuário e senha", command=self.add_or_update_password)
        self.add_button.pack()

        self.delete_button = tk.Button(master, text="Excluir usuário", command=self.delete_user)
        self.delete_button.pack()

        self.verify_button = tk.Button(master, text="Verificar senha", command=self.verify_password)
        self.verify_button.pack()

        self.list_button = tk.Button(master, text="Listar senhas", command=self.list_passwords)
        self.list_button.pack()

        self.user_listbox = tk.Listbox(master)
        self.user_listbox.pack()

        self.quit_button = tk.Button(master, text="Sair", command=master.quit)
        self.quit_button.pack()

        # Preencher a lista de usuários inicialmente
        self.update_user_list()

    def add_or_update_password(self):
        # Cria uma nova janela para inserir o nome de usuário e senha
        add_window = tk.Toplevel(self.master)
        add_window.title("Adicionar ou Atualizar Usuário e Senha")

        # Label e Entry para o nome de usuário
        username_label = tk.Label(add_window, text="Nome de Usuário:")
        username_label.grid(row=0, column=0, padx=5, pady=5)
        username_entry = tk.Entry(add_window)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        # Label e Entry para a senha
        password_label = tk.Label(add_window, text="Senha:")
        password_label.grid(row=1, column=0, padx=5, pady=5)
        password_entry = tk.Entry(add_window, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Função para adicionar ou atualizar a senha
        def add_update():
            username = username_entry.get()
            password = password_entry.get()
            self.pm.add_or_update_password(username, password)
            messagebox.showinfo("Sucesso", f"Usuário '{username}' adicionado/atualizado com sucesso!")
            add_window.destroy()
            self.update_user_list()

        # Botão para adicionar ou atualizar
        add_button = tk.Button(add_window, text="Adicionar/Atualizar", command=add_update)
        add_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def delete_user(self):
        # Verifica se algum usuário está selecionado na lista
        selected_user = self.user_listbox.curselection()
        if selected_user:
            # Pega o nome do usuário selecionado
            username = self.user_listbox.get(selected_user)
            # Pede a senha para confirmar a exclusão
            confirm_password = simpledialog.askstring("Confirmação de Senha", f"Digite a senha para confirmar a exclusão do usuário '{username}':", show='*')
            if confirm_password:
                # Verifica se a senha está correta e exclui o usuário
                if self.pm.verify_password(username, confirm_password):
                    self.pm.delete_user(username)
                    messagebox.showinfo("Sucesso", f"Usuário '{username}' excluído com sucesso!")
                    self.update_user_list()
                else:
                    messagebox.showerror("Erro", "Senha incorreta.")
            else:
                messagebox.showerror("Erro", "Senha não digitada.")
        else:
            messagebox.showerror("Erro", "Nenhum usuário selecionado.")

    def verify_password(self):
        username = input("Digite o nome de usuário: ")
        password = input("Digite a senha: ")
        if self.pm.verify_password(username, password):
            messagebox.showinfo("Verificação de Senha", "Senha correta!")
        else:
            messagebox.showerror("Verificação de Senha", "Senha incorreta!")

    def list_passwords(self):
        passwords = self.pm.list_passwords()
        messagebox.showinfo("Senhas", "\n".join(f"Usuário: {user[0]}, Senha: {user[1]}" for user in passwords))

    def update_user_list(self):
        # Limpa a lista de usuários
        self.user_listbox.delete(0, tk.END)
        # Preenche a lista com os usuários presentes no banco de dados
        users = self.pm.list_passwords()
        for user in users:
            self.user_listbox.insert(tk.END, f"Usuário: {user[0]}, Senha: {user[1]}")

if __name__ == "__main__":
    root = tk.Tk()
    pm_gui = PasswordManagerGUI(root)
    root.mainloop()
