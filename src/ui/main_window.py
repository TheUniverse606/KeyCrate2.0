import customtkinter as ctk
from tkinter import messagebox
import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import Database
from utils.encryption import Encryption

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class KeyCrateGUI:
    SUCCESS_TITLE = "Éxito"
    ERROR_TITLE = "Error"
    ACCESS_DENIED_TITLE = "Acceso Denegado"
    LOGIN_TAB_TITLE = "Iniciar Sesión"
    REGISTER_TAB_TITLE = "Registrarse"
    PASSWORD_LABEL_TEXT = "Contraseña"
    RETURN_KEY = '<Return>'

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("KeyCrate")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.current_user_id = None
        self.current_user_email = None
        self.current_user_password = None
        
        self.center_window()
        
        self.db = Database()
        self.encryption = Encryption()
        
        self.setup_ui()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        title_label = ctk.CTkLabel(main_frame, 
                                  text="KeyCrate", 
                                  font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=(30, 40))
        
        self.tabview = ctk.CTkTabview(main_frame, width=500, height=350)
        self.tabview.pack(expand=True, pady=10)
        
        self.tabview.add(self.LOGIN_TAB_TITLE)
        self.tabview.add(self.REGISTER_TAB_TITLE)
        
        self.setup_login_tab()
        self.setup_register_tab()

    def setup_login_tab(self):
        login_frame = self.tabview.tab(self.LOGIN_TAB_TITLE)
        
        login_container = ctk.CTkFrame(login_frame)
        login_container.pack(expand=True, fill="both", padx=40, pady=40)
        
        ctk.CTkLabel(login_container, 
                    text="Iniciar Sesión",
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 30))
        
        ctk.CTkLabel(login_container, text="Correo Electrónico").pack(pady=(10, 5))
        self.login_email = ctk.CTkEntry(login_container, width=280, height=35)
        self.login_email.pack(pady=(0, 10))
        
        ctk.CTkLabel(login_container, text=self.PASSWORD_LABEL_TEXT).pack(pady=(0, 5))
        self.login_password = ctk.CTkEntry(login_container, width=280, height=35, show="*")
        self.login_password.pack(pady=(0, 20))
        
        login_btn = ctk.CTkButton(login_container, 
                                 text="Iniciar Sesión", 
                                 command=self.login,
                                 width=280, height=35)
        login_btn.pack(pady=(5, 20))
        
        self.login_email.bind(self.RETURN_KEY, lambda e: self.login_password.focus())
        self.login_password.bind(self.RETURN_KEY, lambda e: self.login())

    def setup_register_tab(self):
        register_frame = self.tabview.tab(self.REGISTER_TAB_TITLE)
        
        register_container = ctk.CTkFrame(register_frame)
        register_container.pack(expand=True, fill="both", padx=40, pady=40)
        
        ctk.CTkLabel(register_container, 
                    text="Crear Cuenta",
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 30))
        
        ctk.CTkLabel(register_container, text="Correo Electrónico").pack(pady=(10, 5))
        self.register_email = ctk.CTkEntry(register_container, width=280, height=35)
        self.register_email.pack(pady=(0, 10))
        
        ctk.CTkLabel(register_container, text=self.PASSWORD_LABEL_TEXT).pack(pady=(0, 5))
        self.register_password = ctk.CTkEntry(register_container, width=280, height=35, show="*")
        self.register_password.pack(pady=(0, 10))
        
        ctk.CTkLabel(register_container, text="Confirmar Contraseña").pack(pady=(0, 5))
        self.register_confirm = ctk.CTkEntry(register_container, width=280, height=35, show="*")
        self.register_confirm.pack(pady=(0, 20))
        
        register_btn = ctk.CTkButton(register_container, 
                                    text="Crear Cuenta", 
                                    command=self.register,
                                    width=300, height=40)
        register_btn.pack(pady=(10, 30))
        
        self.register_email.bind(self.RETURN_KEY, lambda e: self.register_password.focus())
        self.register_password.bind(self.RETURN_KEY, lambda e: self.register_confirm.focus())
        self.register_confirm.bind(self.RETURN_KEY, lambda e: self.register())

    def login(self):
        email = self.login_email.get()
        password = self.login_password.get()
        
        if not email or not password:
            messagebox.showerror("Error de Validación", 
                               "Por favor complete todos los campos requeridos")
            return
        
        self.db.connect()
        cursor = self.db.cursor
        cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result:
            stored_password = result[1]
            
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            if self.encryption.verify_master_password(password, stored_password):
                self.current_user_id = result[0]
                self.current_user_email = email
                self.current_user_password = password
                self.show_password_manager()
                messagebox.showinfo(self.SUCCESS_TITLE, 
                                  "Inicio de sesión exitoso")
            else:
                messagebox.showerror(self.ACCESS_DENIED_TITLE, 
                                   "Las credenciales proporcionadas son incorrectas")
        else:
            messagebox.showerror(self.ACCESS_DENIED_TITLE, 
                               "No se encontró una cuenta con ese email")
        
        self.db.disconnect()

    def register(self):
        email = self.register_email.get()
        password = self.register_password.get()
        confirm = self.register_confirm.get()
        
        if not email or not password or not confirm:
            messagebox.showerror("Error de Validación", 
                               "Todos los campos son obligatorios")
            return
        
        if len(password) < 8:
            messagebox.showerror("Contraseña Débil", 
                               "La contraseña debe tener al menos 8 caracteres")
            return
        
        if password != confirm:
            messagebox.showerror("Error de Confirmación", 
                               "Las contraseñas no coinciden")
            return
        
        self.db.connect()
        cursor = self.db.cursor
        
        try:
            hashed_password = self.encryption.hash_master_password(password)
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", 
                         (email, hashed_password))
            self.db.connection.commit()
            
            messagebox.showinfo(self.SUCCESS_TITLE, 
                              "Cuenta creada exitosamente")
            
            self.register_email.delete(0, "end")
            self.register_password.delete(0, "end")
            self.register_confirm.delete(0, "end")
            self.tabview.set(self.LOGIN_TAB_TITLE)
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Usuario Existente", 
                               "Ya existe una cuenta con este correo electrónico")
        finally:
            self.db.disconnect()

    def verify_master_password_for_view(self, action_description="realizar esta acción"):
        verify_window = ctk.CTkToplevel(self.root)
        verify_window.title("Verificación de Seguridad")
        verify_window.geometry("400x300")
        verify_window.resizable(False, False)
        verify_window.transient(self.root)
        verify_window.grab_set()
        
        verify_window.update_idletasks()
        x = (verify_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (verify_window.winfo_screenheight() // 2) - (300 // 2)
        verify_window.geometry(f'400x300+{x}+{y}')
        
        main_frame = ctk.CTkFrame(verify_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, 
                    text="Verificación de Identidad",
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(30, 20))
        
        ctk.CTkLabel(main_frame,
                    text=f"Confirma tu identidad para {action_description}",
                    wraplength=300).pack(pady=(0, 30))
        
        ctk.CTkLabel(main_frame, text="Contraseña Maestra").pack(pady=(0, 5))
        
        password_entry = ctk.CTkEntry(main_frame, show="*", width=250, height=40)
        password_entry.pack(pady=(0, 30))
        password_entry.focus()
        
        result = {"verified": False}
        
        def verify_password():
            entered_password = password_entry.get()
            if entered_password == self.current_user_password:
                result["verified"] = True
                verify_window.destroy()
            else:
                messagebox.showerror(self.ACCESS_DENIED_TITLE, "Contraseña incorrecta")
                password_entry.delete(0, "end")
                password_entry.focus()
        
        def cancel_verification():
            result["verified"] = False
            verify_window.destroy()
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 20))
        
        verify_btn = ctk.CTkButton(button_frame, 
                                  text="Verificar", 
                                  command=verify_password,
                                  width=100)
        verify_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(button_frame, 
                                  text="Cancelar", 
                                  command=cancel_verification,
                                  width=100)
        cancel_btn.pack(side="right")
        
        password_entry.bind(self.RETURN_KEY, lambda e: verify_password())
        
        verify_window.wait_window()
        
        return result["verified"]

    def show_password_manager(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.setup_password_manager_ui()

    def setup_password_manager_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(header_frame, 
                                  text=f"KeyCrate - {self.current_user_email}",
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(side="left", padx=20, pady=20)
        
        logout_btn = ctk.CTkButton(header_frame, 
                                  text="Cerrar Sesión", 
                                  command=self.logout,
                                  width=120)
        logout_btn.pack(side="right", padx=20, pady=20)
        
        self.manager_tabview = ctk.CTkTabview(main_frame)
        self.manager_tabview.pack(fill="both", expand=True, pady=(0, 20))
        
        self.manager_tabview.add("Mis Contraseñas")
        self.manager_tabview.add("Agregar")
        self.manager_tabview.add("Buscar")
        self.manager_tabview.add("Generar")
        
        self.setup_passwords_tab()
        self.setup_add_tab()
        self.setup_search_tab()
        self.setup_generate_tab()

    def setup_passwords_tab(self):
        passwords_frame = self.manager_tabview.tab("Mis Contraseñas")
        
        header_frame = ctk.CTkFrame(passwords_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, 
                    text="Contraseñas Guardadas",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=20, pady=10)
        
        refresh_btn = ctk.CTkButton(header_frame, 
                                   text="Actualizar", 
                                   command=self.load_passwords,
                                   width=100)
        refresh_btn.pack(side="right", padx=20, pady=10)
        
        self.password_list_frame = ctk.CTkScrollableFrame(passwords_frame)
        self.password_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.load_passwords()

    def setup_add_tab(self):
        add_frame = self.manager_tabview.tab("Agregar")
        
        content_frame = ctk.CTkFrame(add_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content_frame, 
                    text="Agregar Nueva Contraseña",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 30))
        
        ctk.CTkLabel(content_frame, text="Nombre de la cuenta").pack(pady=(0, 5))
        self.add_account_entry = ctk.CTkEntry(content_frame, width=400, height=35)
        self.add_account_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(content_frame, text="URL").pack(pady=(0, 5))
        self.add_url_entry = ctk.CTkEntry(content_frame, width=400, height=35)
        self.add_url_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(content_frame, text="Contraseña").pack(pady=(0, 5))
        password_frame = ctk.CTkFrame(content_frame)
        password_frame.pack(pady=(0, 15))
        
        self.add_password_entry = ctk.CTkEntry(password_frame, width=300, height=35, show="*")
        self.add_password_entry.pack(side="left", padx=(10, 5), pady=10)
        
        generate_quick_btn = ctk.CTkButton(password_frame, 
                                          text="Generar", 
                                          command=self.generate_password_for_add,
                                          width=80)
        generate_quick_btn.pack(side="right", padx=(5, 10), pady=10)
        
        ctk.CTkLabel(content_frame, text="Notas").pack(pady=(0, 5))
        self.add_notes_entry = ctk.CTkTextbox(content_frame, width=400, height=100)
        self.add_notes_entry.pack(pady=(0, 30))
        
        save_btn = ctk.CTkButton(content_frame, 
                                text="Guardar Contraseña", 
                                command=self.save_new_password,
                                width=400, height=40)
        save_btn.pack(pady=(0, 20))

    def setup_search_tab(self):
        search_frame = self.manager_tabview.tab("Buscar")
        
        content_frame = ctk.CTkFrame(search_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content_frame, 
                    text="Buscar Contraseñas",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 30))
        
        search_input_frame = ctk.CTkFrame(content_frame)
        search_input_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(search_input_frame, text="Buscar por nombre o URL").pack(pady=(10, 5))
        
        search_entry_frame = ctk.CTkFrame(search_input_frame)
        search_entry_frame.pack(pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(search_entry_frame, width=300, height=35)
        self.search_entry.pack(side="left", padx=(10, 5), pady=10)
        
        search_btn = ctk.CTkButton(search_entry_frame, 
                                  text="Buscar", 
                                  command=self.perform_search,
                                  width=80)
        search_btn.pack(side="right", padx=(5, 10), pady=10)
        
        self.search_results_frame = ctk.CTkScrollableFrame(content_frame)
        self.search_results_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.search_entry.bind(self.RETURN_KEY, lambda e: self.perform_search())

    def setup_generate_tab(self):
        generate_frame = self.manager_tabview.tab("Generar")
        
        content_frame = ctk.CTkFrame(generate_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content_frame, 
                    text="Generar Contraseña Segura",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 30))
        
        ctk.CTkLabel(content_frame, text="Longitud de la contraseña").pack(pady=(0, 5))
        self.length_var = ctk.StringVar(value="16")
        length_entry = ctk.CTkEntry(content_frame, width=100, height=35, textvariable=self.length_var)
        length_entry.pack(pady=(0, 20))
        
        generate_btn = ctk.CTkButton(content_frame, 
                                    text="Generar Nueva Contraseña", 
                                    command=self.generate_new_password,
                                    width=300, height=40)
        generate_btn.pack(pady=(0, 20))
        
        ctk.CTkLabel(content_frame, text="Contraseña generada:").pack(pady=(0, 5))
        self.generated_password_entry = ctk.CTkEntry(content_frame, width=400, height=40)
        self.generated_password_entry.pack(pady=(0, 20))
        
        copy_btn = ctk.CTkButton(content_frame, 
                                text="Copiar al Portapapeles", 
                                command=self.copy_generated_password,
                                width=300, height=35)
        copy_btn.pack(pady=(0, 20))

    def generate_password_for_add(self):
        password = self.encryption.generate_secure_password(16)
        self.add_password_entry.delete(0, "end")
        self.add_password_entry.insert(0, password)

    def save_new_password(self):
        account = self.add_account_entry.get()
        url = self.add_url_entry.get()
        password = self.add_password_entry.get()
        notes = self.add_notes_entry.get("1.0", "end-1c")
        
        if not account or not password:
            messagebox.showerror(self.ERROR_TITLE, "Nombre de cuenta y contraseña son obligatorios")
            return
        
        encrypted_password = self.encryption.encrypt_password(password)
        
        self.db.connect()
        try:
            self.db.cursor.execute("""
                INSERT INTO passwords (user_id, account_name, password, url, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (self.current_user_id, account, encrypted_password, url, notes))
            self.db.connection.commit()
            
            self.add_account_entry.delete(0, "end")
            self.add_url_entry.delete(0, "end")
            self.add_password_entry.delete(0, "end")
            self.add_notes_entry.delete("1.0", "end")
            
            self.load_passwords()
            messagebox.showinfo(self.SUCCESS_TITLE, "Contraseña guardada correctamente")
            self.manager_tabview.set("Mis Contraseñas")
        finally:
            self.db.disconnect()

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        if not search_term:
            return
        
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()
        
        self.db.connect()
        try:
            self.db.cursor.execute("""
                SELECT id, account_name, url FROM passwords
                WHERE user_id = ? AND (
                    LOWER(account_name) LIKE ? OR 
                    LOWER(url) LIKE ?
                )
            """, (self.current_user_id, f"%{search_term}%", f"%{search_term}%"))
            
            results = self.db.cursor.fetchall()
            
            if not results:
                ctk.CTkLabel(self.search_results_frame, 
                            text="No se encontraron resultados",
                            font=ctk.CTkFont(size=16)).pack(pady=20)
            else:
                for password_data in results:
                    self.create_search_result_item(password_data)
                    
        finally:
            self.db.disconnect()

    def create_search_result_item(self, password_data):
        password_id, account_name, url = password_data
        
        item_frame = ctk.CTkFrame(self.search_results_frame)
        item_frame.pack(fill="x", padx=10, pady=5)
        
        info_frame = ctk.CTkFrame(item_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        account_label = ctk.CTkLabel(info_frame, 
                                    text=account_name,
                                    font=ctk.CTkFont(size=14, weight="bold"))
        account_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        url_label = ctk.CTkLabel(info_frame, 
                                text=url if url else "Sin URL",
                                font=ctk.CTkFont(size=12))
        url_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        button_frame = ctk.CTkFrame(item_frame)
        button_frame.pack(side="right", padx=10, pady=10)
        
        view_btn = ctk.CTkButton(button_frame, 
                                text="Ver", 
                                command=lambda: self.show_password_details_inline(password_id),
                                width=60)
        view_btn.pack(side="left", padx=5)
        
        copy_btn = ctk.CTkButton(button_frame, 
                                text="Copiar", 
                                command=lambda: self.copy_password_by_id(password_id),
                                width=60)
        copy_btn.pack(side="left", padx=5)

    def generate_new_password(self):
        try:
            length = int(self.length_var.get())
            if length < 4:
                length = 4
            elif length > 50:
                length = 50
        except ValueError:
            length = 16
            self.length_var.set("16")
        
        password = self.encryption.generate_secure_password(length)
        self.generated_password_entry.delete(0, "end")
        self.generated_password_entry.insert(0, password)

    def copy_generated_password(self):
        password = self.generated_password_entry.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo(self.SUCCESS_TITLE, "Contraseña copiada al portapapeles")
        else:
            messagebox.showwarning("Advertencia", "Primero genera una contraseña")

    def show_password_details_inline(self, password_id):
        if not self.verify_master_password_for_view("ver los detalles de esta contraseña"):
            return
            
        self.db.connect()
        try:
            self.db.cursor.execute("""
                SELECT account_name, password, url, notes FROM passwords
                WHERE id = ? AND user_id = ?
            """, (password_id, self.current_user_id))
            
            result = self.db.cursor.fetchone()
            if result:
                account_name, encrypted_password, url, notes = result
                decrypted_password = self.encryption.decrypt_password(encrypted_password)
                
                details_text = f"Cuenta: {account_name}\n"
                details_text += f"Contraseña: {decrypted_password}\n"
                details_text += f"URL: {url if url else 'Sin URL'}\n"
                details_text += f"Notas: {notes if notes else 'Sin notas'}"
                
                messagebox.showinfo(f"Detalles de {account_name}", details_text)
        finally:
            self.db.disconnect()

    def load_passwords(self):
        for widget in self.password_list_frame.winfo_children():
            widget.destroy()
        
        self.db.connect()
        try:
            self.db.cursor.execute("""
                SELECT id, account_name, url FROM passwords
                WHERE user_id = ?
                ORDER BY account_name
            """, (self.current_user_id,))
            
            passwords = self.db.cursor.fetchall()
            
            if not passwords:
                no_passwords_label = ctk.CTkLabel(self.password_list_frame,
                                                 text="No hay contraseñas guardadas",
                                                 font=ctk.CTkFont(size=16))
                no_passwords_label.pack(pady=50)
            else:
                for password_data in passwords:
                    self.create_password_item(password_data)
                    
        finally:
            self.db.disconnect()

    def create_password_item(self, password_data):
        password_id, account_name, url = password_data
        
        item_frame = ctk.CTkFrame(self.password_list_frame)
        item_frame.pack(fill="x", padx=10, pady=5)
        
        info_frame = ctk.CTkFrame(item_frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        account_label = ctk.CTkLabel(info_frame, 
                                    text=account_name,
                                    font=ctk.CTkFont(size=14, weight="bold"))
        account_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        url_label = ctk.CTkLabel(info_frame, 
                                text=url if url else "Sin URL",
                                font=ctk.CTkFont(size=12))
        url_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        button_frame = ctk.CTkFrame(item_frame)
        button_frame.pack(side="right", padx=10, pady=10)
        
        view_btn = ctk.CTkButton(button_frame, 
                                text="Ver", 
                                command=lambda: self.show_password_details_inline(password_id),
                                width=60)
        view_btn.pack(side="left", padx=5)
        
        copy_btn = ctk.CTkButton(button_frame, 
                                text="Copiar", 
                                command=lambda: self.copy_password_by_id(password_id),
                                width=60)
        copy_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(button_frame, 
                                  text="Eliminar", 
                                  command=lambda: self.delete_password_by_id(password_id),
                                  width=60,
                                  fg_color="red")
        delete_btn.pack(side="left", padx=5)

    def show_add_password_dialog(self):
        self.manager_tabview.set("Agregar")

    def show_all_passwords(self):
        self.manager_tabview.set("Mis Contraseñas")

    def show_search_dialog(self):
        self.manager_tabview.set("Buscar")

    def generate_password(self):
        self.manager_tabview.set("Generar")

    def show_password_details_by_id(self, password_id):
        self.show_password_details_inline(password_id)

    def copy_password_by_id(self, password_id):
        if not self.verify_master_password_for_view("copiar esta contraseña"):
            return
            
        self.db.connect()
        try:
            self.db.cursor.execute("""
                SELECT account_name, password FROM passwords
                WHERE id = ? AND user_id = ?
            """, (password_id, self.current_user_id))
            result = self.db.cursor.fetchone()
            if result:
                decrypted_password = self.encryption.decrypt_password(result[1])
                self.root.clipboard_clear()
                self.root.clipboard_append(decrypted_password)
                messagebox.showinfo("Copiado", f"Contraseña de {result[0]} copiada")
        finally:
            self.db.disconnect()

    def delete_password_by_id(self, password_id):
        self.db.connect()
        try:
            self.db.cursor.execute("""
                SELECT account_name FROM passwords
                WHERE id = ? AND user_id = ?
            """, (password_id, self.current_user_id))
            result = self.db.cursor.fetchone()
            if result:
                account_name = result[0]
                response = messagebox.askyesno("Confirmar eliminación", 
                                             f"¿Eliminar la contraseña de {account_name}?")
                if response:
                    self.db.cursor.execute("DELETE FROM passwords WHERE id = ? AND user_id = ?", 
                                         (password_id, self.current_user_id))
                    self.db.connection.commit()
                    self.load_passwords()
                    messagebox.showinfo(self.SUCCESS_TITLE, "Contraseña eliminada")
        finally:
            self.db.disconnect()

    def logout(self):
        self.current_user_id = None
        self.current_user_email = None
        self.current_user_password = None
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.setup_ui()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KeyCrateGUI()
    app.run()
