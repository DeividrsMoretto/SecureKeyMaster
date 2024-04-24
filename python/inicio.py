import sys
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
        for row in rows:
            print(row)

if __name__ == "__main__":
    pm = PasswordManager(dbname='Inicio', user='moretto', password='incorreta')

    while True:
        print("\nMenu:")
        print("1. Adicionar ou atualizar usuário e senha")
        print("2. Verificar senha")
        print("3. Listar senhas")
        print("4. Sair")

        choice = input("Escolha uma opção: ")

        if choice == "1":
            username = input("Digite o nome de usuário: ")
            password = input("Digite a senha: ")
            pm.add_or_update_password(username, password)
            print(f"Usuário '{username}' adicionado/atualizado com sucesso!")
        elif choice == "2":
            username = input("Digite o nome de usuário: ")
            password = input("Digite a senha: ")
            if pm.verify_password(username, password):
                print("Senha correta!")
            else:
                print("Senha incorreta!")
        elif choice == "3":
            print("Listando senhas no banco de dados:")
            pm.list_passwords()
        elif choice == "4":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Por favor, escolha novamente.")
