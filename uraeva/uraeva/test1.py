import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
from pymorphy3 import MorphAnalyzer
import os

class LetterGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Puzzle")
        
        # Theme configurations
        self.themes = {
            'Dark': {
                'bg': '#2e2e2e',
                'fg': 'white',
                'button_bg': '#3e3e3e',
                'active_bg': '#4a4a4a',
                'highlight': '#4a9dff',
                'listbox_bg': '#3e3e3e',
                'entry_bg': '#3e3e3e',
                'text_wrap': 15
            },
            'Light': {
                'bg': '#f0f0f0',
                'fg': 'black',
                'button_bg': '#e0e0e0',
                'active_bg': '#d0d0d0',
                'highlight': '#0078d7',
                'listbox_bg': '#ffffff',
                'entry_bg': '#ffffff',
                'text_wrap': 15
            }
        }
        self.current_theme = 'Dark'
        self.open_windows = []

        self.grid_size = 5
        self.letters = [
            ['А', 'Б', 'В', 'Г', 'Д', 'Е'],
            ['Ж', 'З', 'И', 'Й', 'К', 'Л'],
            ['М', 'Н', 'О', 'П', 'Р', 'С'],
            ['Т', 'У', 'Ф', 'Х', 'Ц', 'Ч'],
            ['Ш', 'Щ', 'Ы', 'Э', 'Ю', 'Я']
        ]

        self.selected_letters = []
        self.start_time = None
        self.timer_running = False
        self.elapsed_time = 0
        self.user_name = None
        self.score = 0
        self.checked_words = []
        self.grid_buttons = []

        self.dictionary_file = "словарь.txt"
        self.create_dictionary_file()
        self.morph = MorphAnalyzer()

        self.create_ui()
        self.configure_styles()
        self.update_theme("Dark")

    def create_dictionary_file(self):
        if not os.path.exists(self.dictionary_file):
            with open(self.dictionary_file, 'w', encoding='utf-8') as f:
                f.write("")

    def configure_styles(self):
        theme = self.themes[self.current_theme]
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Base styles
        self.style.configure('.', 
                           background=theme['bg'], 
                           foreground=theme['fg'])
        
        # Button styles
        self.style.configure('TButton', 
                           background=theme['button_bg'],
                           foreground=theme['fg'], 
                           borderwidth=0)
        self.style.map('TButton', 
                      background=[('active', theme['active_bg']), 
                                  ('pressed', theme['highlight'])],
                      foreground=[('active', theme['fg'])])

        # Treeview styles
        self.style.configure("Treeview",
                            background=theme['button_bg'],
                            foreground=theme['fg'],
                            fieldbackground=theme['button_bg'],
                            borderwidth=0)
        self.style.configure("Treeview.Heading",
                            background=theme['active_bg'],
                            foreground=theme['fg'],
                            relief="flat")
        self.style.map("Treeview",
                      background=[('selected', theme['highlight'])],
                      foreground=[('selected', theme['fg'])])

    def update_theme(self, new_theme):
        self.current_theme = new_theme
        theme = self.themes[new_theme]
        
        # Reconfigure base styles
        self.configure_styles()
        
        # Update root and main containers
        self.root.config(bg=theme['bg'])
        
        # Update all tracked widgets
        self.update_widget_colors(theme)
        
        # Update grid buttons
        for row in self.grid_buttons:
            for btn in row:
                btn.config(bg=theme['button_bg'],
                        fg=theme['fg'],
                        activebackground=theme['active_bg'])
        
        # Update listbox
        self.words_listbox.config(bg=theme['listbox_bg'],
                                fg=theme['fg'],
                                selectbackground=theme['highlight'])
        
        # Update all open windows
        for window in self.open_windows:
            if window.winfo_exists():
                self.update_window_theme(window, theme)

    def update_widget_colors(self, theme):
        # Update frame backgrounds
        for frame in [self.top_frame, self.word_frame, self.grid_frame]:
            frame.config(bg=theme['bg'])
        
        # Update labels
        for label in [self.current_word_label, self.score_label, self.time_label]:
            label.config(bg=theme['bg'], fg=theme['fg'])
        
        # Update buttons
        for btn in [self.user_button, self.help_button, 
                self.leaderboard_button, self.check_button,
                self.start_button]:
            btn.config(bg=theme['button_bg'],
                    fg=theme['fg'],
                    activebackground=theme['active_bg'])
        
        # Update mode menu
        self.mode_menu.config(bg=theme['button_bg'],
                            fg=theme['fg'],
                            activebackground=theme['active_bg'])
        self.mode_menu['menu'].config(bg=theme['button_bg'],
                                    fg=theme['fg'],
                                    activebackground=theme['active_bg'])

    def update_window_theme(self, window, theme):
        window.config(bg=theme['bg'])
        for child in window.winfo_children():
            try:
                if isinstance(child, tk.Frame):
                    child.config(bg=theme['bg'])
                elif isinstance(child, tk.Label):
                    child.config(bg=theme['bg'], fg=theme['fg'])
                elif isinstance(child, tk.Button):
                    child.config(bg=theme['button_bg'],
                                fg=theme['fg'],
                                activebackground=theme['active_bg'])
                elif isinstance(child, tk.Entry):
                    child.config(bg=theme['entry_bg'],
                            fg=theme['fg'],
                            insertbackground=theme['fg'])
                elif isinstance(child, tk.Listbox):
                    child.config(bg=theme['listbox_bg'],
                            fg=theme['fg'],
                            selectbackground=theme['highlight'])
                self.update_window_theme(child, theme)
            except:
                continue

    def create_ui(self):
        theme = self.themes[self.current_theme]
        
        # Top frame
        self.top_frame = tk.Frame(self.root, bg=theme['bg'])
        self.top_frame.pack(pady=10, fill=tk.X)

        # Theme switcher
        theme_menu = ttk.OptionMenu(
            self.top_frame, 
            tk.StringVar(value=self.current_theme),
            self.current_theme,
            *self.themes.keys(), 
            command=lambda t: self.update_theme(t)
        )
        theme_menu.grid(row=0, column=4, padx=5, sticky="ew")

        # User button
        self.user_button = tk.Button(
            self.top_frame, 
            text="Пользователь", 
            command=self.show_user_window,
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['active_bg'],
            borderwidth=0
        )
        self.user_button.grid(row=0, column=0, padx=5, sticky="ew")

        # Mode menu
        self.modes = ['Обучение', 'Одиночный режим']
        self.selected_mode = tk.StringVar(value=self.modes[0])
        self.mode_menu = tk.OptionMenu(
            self.top_frame, 
            self.selected_mode, 
            *self.modes
        )
        self.mode_menu.config(
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['active_bg'],
            borderwidth=0
        )
        self.mode_menu['menu'].config(
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['active_bg']
        )
        self.mode_menu.grid(row=0, column=1, padx=5, sticky="ew")

        # Help button
        self.help_button = tk.Button(
            self.top_frame, 
            text="Помощь", 
            command=self.show_help_window,
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['active_bg'],
            borderwidth=0
        )
        self.help_button.grid(row=0, column=2, padx=5, sticky="ew")

        # Leaderboard button
        self.leaderboard_button = tk.Button(
            self.top_frame, 
            text="Таблица лидеров", 
            command=self.show_leaderboard,
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['active_bg'],
            borderwidth=0
        )
        self.leaderboard_button.grid(row=0, column=3, padx=5, sticky="ew")

        # Configure grid columns
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(2, weight=1)
        self.top_frame.grid_columnconfigure(3, weight=1)

        # Word frame
        self.word_frame = tk.Frame(self.root, bg=theme['bg'])
        self.word_frame.pack(pady=10, fill=tk.X)

        # Current word label
        self.current_word_label = tk.Label(
            self.word_frame, 
            text="Текущее слово: ", 
            font=("Helvetica", 14),
            bg=theme['bg'],
            fg=theme['fg'],
            anchor="w"
        )
        self.current_word_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Check button
        self.check_button = tk.Button(
            self.word_frame, 
            text="Проверить слово", 
            command=self.check_word,
            state=tk.DISABLED,
            width=15,
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['active_bg'],
            borderwidth=0
        )
        self.check_button.pack(side=tk.RIGHT, padx=10)

        # Score label
        self.score_label = tk.Label(
            self.root,
            text=f"Очки: {self.score}",
            font=("Helvetica", 14),
            pady=10,
            bg=theme['bg'],
            fg=theme['fg']
        )
        self.score_label.pack()

        # Words listbox
        self.words_listbox = tk.Listbox(
            self.root,
            width=30,
            height=5,
            font=("Helvetica", 12),
            bg=theme['listbox_bg'],
            fg=theme['fg'],
            selectbackground=theme['highlight']
        )
        self.words_listbox.pack(pady=10)

        # Grid frame
        self.grid_frame = tk.Frame(self.root, bg=theme['bg'])
        self.grid_frame.pack(pady=20)
        self.create_grid(self.grid_frame)

        # Start button
        self.start_button = tk.Button(
            self.root, 
            text="Начать игру", 
            command=self.start_game,
            bg=theme['button_bg'],
            fg=theme['fg'],
            activebackground=theme['active_bg'],
            borderwidth=0
        )
        self.start_button.pack(pady=10)

        # Time label
        self.time_label = tk.Label(
            self.root, 
            text="Время: 0 секунд", 
            font=("Helvetica", 12),
            bg=theme['bg'],
            fg=theme['fg']
        )
        self.time_label.pack(pady=10)

    def add_to_dictionary(self, word):
        """Добавляет слово в файл словаря без дубликатов"""
        with open(self.dictionary_file, 'r+', encoding='utf-8') as f:
            existing_words = [line.strip().lower() for line in f.readlines()]
            if word not in existing_words:
                f.write(f"{word}\n")

    def check_word(self):
        if not self.selected_letters:
            messagebox.showwarning("Пусто", "Выберите буквы!")
            return
            
        word = "".join(self.selected_letters).lower()
        is_valid = self.pymorphy_check(word)
        
        if is_valid:
            self.add_to_dictionary(word)
            points = len(word)
            self.score += points
            self.score_label.config(text=f"Очки: {self.score}")
            self.checked_words.append(word)
            self.words_listbox.insert(tk.END, word)
            messagebox.showinfo("Успех!", f"Слово принято! +{points} очков")
        else:
            messagebox.showwarning("Ошибка", "Такого слова не существует!")
        
        self.selected_letters = []
        self.highlight_word()
        self.current_word_label.config(text="Текущее слово: ")

    def pymorphy_check(self, word):
        parsed = self.morph.parse(word)
        return parsed[0].score >= 0.5 and parsed[0].tag.POS is not None

    def create_grid(self, frame):
        theme = self.themes[self.current_theme]
        self.grid_buttons = []
        for i in range(self.grid_size):
            row_buttons = []
            for j in range(6):
                letter = self.letters[i][j]
                button = tk.Button(
                    frame, 
                    text=letter, 
                    width=5, 
                    height=2,
                    command=lambda i=i, j=j: self.on_click(i, j),
                    bg=theme['button_bg'],
                    fg=theme['fg'],
                    activebackground=theme['active_bg'],
                    borderwidth=0
                )
                button.grid(row=i, column=j, padx=5, pady=5)
                row_buttons.append(button)
            self.grid_buttons.append(row_buttons)

    def on_click(self, i, j):
        letter = self.letters[i][j]
        if letter not in self.selected_letters:
            self.selected_letters.append(letter)
            self.highlight_word()
            current_word = ' '.join(self.selected_letters)
            wrapped_word = '\n'.join([
                current_word[i:i + self.themes[self.current_theme]['text_wrap']]
                for i in range(0, len(current_word), self.themes[self.current_theme]['text_wrap'])
            ])
            self.current_word_label.config(text=f"Текущее слово: {wrapped_word}")
            self.check_button.config(state=tk.NORMAL)

    def highlight_word(self):
        theme = self.themes[self.current_theme]
        for i in range(self.grid_size):
            for j in range(6):
                self.grid_buttons[i][j].config(bg=theme['button_bg'])
        
        for letter in self.selected_letters:
            for i in range(self.grid_size):
                for j in range(6):
                    if self.letters[i][j] == letter:
                        self.grid_buttons[i][j].config(bg=theme['highlight'])
                        break

    def start_game(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.elapsed_time = 0
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time = time.time() - self.start_time
            self.time_label.config(text=f"Время: {int(self.elapsed_time)} секунд")
            self.root.after(1000, self.update_timer)

    def show_user_window(self):
        # Fix for duplicate windows
        if hasattr(self, '_user_window_open') and self._user_window_open:
            return
            
        self._user_window_open = True
        theme = self.themes[self.current_theme]
        
        user_window = tk.Toplevel(self.root)
        user_window.title("Вход / Регистрация")
        user_window.geometry("350x400")
        user_window.configure(bg=theme['bg'])
        self.open_windows.append(user_window)
        
        user_window.protocol("WM_DELETE_WINDOW", lambda: self.on_user_window_close(user_window))

        # Welcome label
        welcome_label = tk.Label(user_window, 
                               text="Добро пожаловать", 
                               font=("Helvetica", 16),
                               bg=theme['bg'],
                               fg=theme['fg'])
        welcome_label.pack(pady=10)

        # Email entry
        email_label = tk.Label(user_window, 
                             text="E-mail", 
                             bg=theme['bg'],
                             fg=theme['fg'])
        email_label.pack(pady=5)
        self.email_entry = tk.Entry(user_window, 
                                  width=30,
                                  bg=theme['entry_bg'],
                                  fg=theme['fg'],
                                  insertbackground=theme['fg'])
        self.email_entry.pack(pady=5)

        # Password entry
        password_label = tk.Label(user_window, 
                                text="Пароль", 
                                bg=theme['bg'],
                                fg=theme['fg'])
        password_label.pack(pady=5)
        self.password_entry = tk.Entry(user_window, 
                                     width=30, 
                                     show="*",
                                     bg=theme['entry_bg'],
                                     fg=theme['fg'],
                                     insertbackground=theme['fg'])
        self.password_entry.pack(pady=5)

        # Buttons frame
        button_frame = tk.Frame(user_window, bg=theme['bg'])
        button_frame.pack(pady=10)

        login_button = tk.Button(button_frame, 
                               text="Войти", 
                               command=self.login,
                               bg=theme['button_bg'],
                               fg=theme['fg'],
                               activebackground=theme['active_bg'],
                               borderwidth=0)
        login_button.grid(row=0, column=0, padx=5)

        register_button = tk.Button(button_frame, 
                                  text="Зарегистрироваться", 
                                  command=self.register,
                                  bg=theme['button_bg'],
                                  fg=theme['fg'],
                                  activebackground=theme['active_bg'],
                                  borderwidth=0)
        register_button.grid(row=0, column=1, padx=5)

        # Social buttons
        social_frame = tk.Frame(user_window, bg=theme['bg'])
        social_frame.pack(pady=10)


    
        telegram_button = tk.Button(social_frame, 
                                  text="Телеграмм", 
                                  command=self.open_telegram,
                                  bg=theme['button_bg'],
                                  fg=theme['fg'],
                                  activebackground=theme['active_bg'],
                                  borderwidth=0)
        telegram_button.grid(row=0, column=0, padx=5)

        vk_button = tk.Button(social_frame, 
                            text="ВКонтакте", 
                            command=self.open_vk,
                            bg=theme['button_bg'],
                            fg=theme['fg'],
                            activebackground=theme['active_bg'],
                            borderwidth=0)
        vk_button.grid(row=0, column=1, padx=5)

        email_button = tk.Button(social_frame, 
                               text="E-mail", 
                               command=self.send_email,
                               bg=theme['button_bg'],
                               fg=theme['fg'],
                               activebackground=theme['active_bg'],
                               borderwidth=0)
        email_button.grid(row=0, column=2, padx=5)

        # Forgot password
        forgot_password_button = tk.Button(user_window, 
                                        text="Забыли пароль?", 
                                        command=self.forgot_password,
                                        bg=theme['bg'],
                                        fg=theme['fg'],
                                        activebackground=theme['active_bg'],
                                        borderwidth=0)
        forgot_password_button.pack(pady=10)

    def on_user_window_close(self, window):
        self._user_window_open = False
        self.open_windows.remove(window)
        window.destroy()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if email and password:
            messagebox.showinfo("Вход", f"Добро пожаловать, {email}!")
        else:
            messagebox.showwarning("Ошибка", "Введите все данные!")

    def register(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if email and password:
            messagebox.showinfo("Регистрация", f"Вы успешно зарегистрированы, {email}!")
        else:
            messagebox.showwarning("Ошибка", "Введите все данные!")

    def open_telegram(self):
        messagebox.showinfo("Телеграмм", "Открытие Телеграмм...")

    def open_vk(self):
        messagebox.showinfo("ВКонтакте", "Открытие ВКонтакте...")

    def send_email(self):
        messagebox.showinfo("E-mail", "Отправка письма...")

    def forgot_password(self):
        messagebox.showinfo("Забыли пароль?", "Восстановление пароля...")

    def show_help_window(self):
        theme = self.themes[self.current_theme]
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Помощь")
        help_window.geometry("400x400")
        help_window.configure(bg=theme['bg'])
        self.open_windows.append(help_window)

        help_title = tk.Label(help_window, 
                            text="Помощь", 
                            font=("Helvetica", 16),
                            bg=theme['bg'],
                            fg=theme['fg'])
        help_title.pack(pady=10)

        self.hints_enabled = tk.BooleanVar(value=False)
        hints_switch = tk.Checkbutton(help_window, 
                                   text="Включить подсказки",
                                   variable=self.hints_enabled,
                                   bg=theme['bg'],
                                   fg=theme['fg'],
                                   activebackground=theme['bg'],
                                   activeforeground=theme['fg'],
                                   selectcolor=theme['button_bg'])
        hints_switch.pack(pady=10)

        dictionary_button = tk.Button(help_window, 
                                    text="Таблица (словарь)", 
                                    command=self.show_dictionary,
                                    bg=theme['button_bg'],
                                    fg=theme['fg'],
                                    activebackground=theme['active_bg'],
                                    borderwidth=0)
        dictionary_button.pack(pady=10)

        rules_button = tk.Button(help_window, 
                              text="Гайд (Правила игры)", 
                              command=self.show_rules,
                              bg=theme['button_bg'],
                              fg=theme['fg'],
                              activebackground=theme['active_bg'],
                              borderwidth=0)
        rules_button.pack(pady=10)

    def show_dictionary(self):
        theme = self.themes[self.current_theme]
        
        dictionary_window = tk.Toplevel(self.root)
        dictionary_window.title("Таблица (словарь)")
        dictionary_window.geometry("400x300")
        dictionary_window.configure(bg=theme['bg'])
        self.open_windows.append(dictionary_window)

        scrollbar = tk.Scrollbar(dictionary_window, bg=theme['button_bg'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(
            dictionary_window, 
            yscrollcommand=scrollbar.set,
            font=("Helvetica", 12),
            width=40,
            bg=theme['listbox_bg'],
            fg=theme['fg'],
            selectbackground=theme['highlight']
        )
        listbox.pack(fill=tk.BOTH, expand=True)

        try:
            with open(self.dictionary_file, 'r', encoding='utf-8') as f:
                words = sorted([line.strip() for line in f.readlines() if line.strip()])
                for word in words:
                    listbox.insert(tk.END, word.capitalize())
        except FileNotFoundError:
            listbox.insert(tk.END, "Словарь пуст")

        scrollbar.config(command=listbox.yview)

    def show_rules(self):
        theme = self.themes[self.current_theme]
        
        rules_window = tk.Toplevel(self.root)
        rules_window.title("Правила игры")
        rules_window.geometry("400x300")
        rules_window.configure(bg=theme['bg'])
        self.open_windows.append(rules_window)

        rules_text = """1. Выберите буквы из сетки.
2. Составьте слова, используя выбранные буквы.
3. Если слово правильно, оно засчитывается.
4. Для получения подсказок, включите переключатель.
5. Попробуйте составить как можно больше слов за ограниченное время."""
        rules_label = tk.Label(rules_window, 
                             text=rules_text, 
                             font=("Helvetica", 12), 
                             justify="left",
                             bg=theme['bg'],
                             fg=theme['fg'])
        rules_label.pack(pady=10)

    def show_leaderboard(self):
        theme = self.themes[self.current_theme]
        
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Таблица лидеров")
        leaderboard_window.geometry("400x300")
        leaderboard_window.configure(bg=theme['bg'])
        self.open_windows.append(leaderboard_window)

        leaderboard_title = tk.Label(leaderboard_window, 
                                   text="Таблица лидеров", 
                                   font=("Helvetica", 16),
                                   bg=theme['bg'],
                                   fg=theme['fg'])
        leaderboard_title.pack(pady=10)

        columns = ("Никнейм", "Очки")
        tree = ttk.Treeview(leaderboard_window, columns=columns, show="headings")
        tree.pack(fill=tk.BOTH, expand=True)

        tree.heading("Никнейм", text="Никнейм")
        tree.heading("Очки", text="Очки")

        tree.insert("", "end", values=("Игрок1", 100))
        tree.insert("", "end", values=("Игрок2", 90))
        tree.insert("", "end", values=("Игрок3", 80))

if __name__ == "__main__":
    root = tk.Tk()
    app = LetterGridApp(root)
    root.mainloop()