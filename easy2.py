import customtkinter as ctk
import json
import re
from tkinter import filedialog, messagebox
import threading
import time
from PIL import Image
import pyautogui
import sys
from werkzeug.security import check_password_hash
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import ast
import datetime
import os

class TestPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.width, self.height = pyautogui.size()
        self.title('Easy2')
        self.state('zoomed')
        self.overrideredirect(True)
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(width=False, height=False)

        self.questions = []
        self.entries = []
        self.checkboxes = []
        self.tab_buttons = []
        self.score = 0
        self.correct_counter = 0
        self.questions_counter = 0
        self.passed_flag = False

        self.canvas = ctk.CTkCanvas(self, height=32)
        self.canvas.config(bg='#2b2b2b', highlightbackground='#2b2b2b')
        self.canvas.pack(side='top', fill='x')

        self.tab_frame = ctk.CTkFrame(self.canvas)
        
        self.canvas.create_window((0, 0), window=self.tab_frame, anchor='nw')

        self.scrollbar = ctk.CTkScrollbar(self, orientation='horizontal', command=self.on_scroll)
        self.scrollbar.pack(side='top', fill='x')

        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.tab_frame.bind('<Configure>', self.on_frame_configure)

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(side='top', fill='both', expand=True)
        
        self.load_button = ctk.CTkButton(self, text='Загрузить тест', command=self.load_test)
        self.load_button.place(relx=0.45, rely=0.5)

        self.exit_button = ctk.CTkButton(self, text='Выйти', command=sys.exit)
        self.exit_button.place(relx=0.45, rely=0.55)

        self.timer_label = ctk.CTkLabel(master=self, text='00:00:00', font=('Arial', 36, 'bold'), fg_color='#2b2b2b')
        self.timer_label.place(relx=0.1, rely=0.9)

        self.fio = ctk.CTkInputDialog(title='Easy2', text='Фамилия И.О.').get_input()
        
        if not self.fio:
            sys.exit()

        self.bad_guy_check = threading.Thread(target=self.bad_guy_alert)
        self.timer = threading.Thread(target=self.timer_function)

        messagebox.showwarning(title='Внимание', message=('Программа отслеживает любую попытку свернуть тест или открыть что-то в фоне. ' 
                                                          'Будьте осторожны! Даже случайное нажатие на "Пуск"' 
                                                          'будет расценено как попытка списать.'))
    def timer_function(self):
        self.timer_label.configure(text=time.strftime('%H:%M:%S', time.gmtime(self.time)))

        while(True):
            time.sleep(1)
            if self.passed_flag:
                break
            self.time -= 1
            self.timer_label.configure(text=time.strftime('%H:%M:%S', time.gmtime(self.time)))
            if self.time == 0:
                for widget in self.tab_frame.winfo_children():
                    widget.destroy()

                for widget in self.content_frame.winfo_children():
                    widget.destroy()

                self.passed_label = ctk.CTkLabel(master=self.content_frame, text=f'Время вышло\n Результат: {self.score} из {len(self.questions)}', font=('Arial', 72, 'bold'))
                self.passed_label.pack(side='top', pady=100)
                self.passed_flag = True
                break

    def bad_guy_alert(self):
        time.sleep(1)
        coordinates_pool_x = []
        coordinates_pool_x.append(self.width - 60)
        coordinates_pool_x.append(int(self.width*0.8))
        coordinates_pool_y = []
        coordinates_pool_y.append(self.height - 20)
        coordinates_pool_y.append(int(self.height*0.5))

        while(not self.passed_flag):
            time.sleep(0.1)
            screenshot = pyautogui.screenshot()
            for check in range(2):
                if screenshot.getpixel((coordinates_pool_x[check], coordinates_pool_y[check])) != (43,43,43):
                    for widget in self.tab_frame.winfo_children():
                        widget.destroy()

                    for widget in self.content_frame.winfo_children():
                        widget.destroy()

                    ctk.set_appearance_mode('light')
                    self.timer_label.configure(fg_color='#dbdbdb')
                    self.canvas.config(bg='#dbdbdb', highlightbackground='#dbdbdb')
                    self.passed_fio = ctk.CTkLabel(master=self.content_frame, text=self.fio, font=('Arial', 72, 'bold'), text_color='red')
                    self.passed_fio.pack(side='top', pady=100)
                    self.passed_label = ctk.CTkLabel(master=self.content_frame, text='ПОЙМАН НА ОШИБКЕ', font=('Arial', 72, 'bold'), text_color='red')
                    self.passed_label.pack(side='top', pady=100)
                    self.content_frame.configure(fg_color='#dbdbdb', border_color='dbdbdb')
                    self.variant_label.configure(bg_color='#dbdbdb')
                    self.passed_flag = True
    
        self.exit_button.configure(state=ctk.DISABLED)
        self.exit_button.place(relx=0.46, rely=0.8)
        time.sleep(3)
        self.exit_button.configure(state=ctk.ACTIVE)

    def on_scroll(self, *args):
        self.canvas.xview(*args)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def generate_key(self, key):
        key_bytes = key.encode('utf-8')
        return hashlib.sha256(key_bytes).digest()
    
    def decryption_func(self, key_str, encrypted_data):
        decrypted_dict = {}
        attribute_list = ['question', 'answers', 'correct']
        key = self.generate_key(key_str)
        iv = key[:16]
        key = key[16:]

        for attribute in attribute_list:
            encrypted_bytes = base64.b64decode(encrypted_data[attribute])
            aes_cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).decryptor()
            unpadded_data = aes_cipher.update(encrypted_bytes) + aes_cipher.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            unpadded_data = unpadder.update(unpadded_data) + unpadder.finalize()
            if attribute == 'answers' or attribute == 'correct':
                decrypted_dict[attribute] = ast.literal_eval(unpadded_data.decode('utf-8'))
            else:
                decrypted_dict[attribute] = unpadded_data.decode('utf-8')
    
        return decrypted_dict
    
    def decrypt_time(self, key_str, encrypted_data):
        key = self.generate_key(key_str)
        iv = key[:16]  # Initialization vector (IV)
        key = key[16:]  # Use next 32 bytes for AES-256
        aes_cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()).decryptor()

        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = aes_cipher.update(encrypted_bytes) + aes_cipher.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted) + unpadder.finalize()

        return unpadded_data.decode('utf-8')
    
    def load_test(self):
        try:
            file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if not file:
                raise RuntimeError
            self.variant_label = ctk.CTkLabel(master=self, text=os.path.basename(file), font=('Arial', 42, 'bold'), bg_color='#2b2b2b')
            self.variant_label.place(relx=0.85, rely=0.9)
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for question in data:
                    question['question']
                    question['answers']
                    question['correct']
                    question['id']
                
                self.questions = data
                key = self.questions[-1]['password']
                password = ctk.CTkInputDialog(title='Авторизация', text='Введите пароль').get_input()

                if check_password_hash(str(key), str(password)):
                    counter = 0
                    for question in self.questions:
                        update = self.decryption_func(str(password), question)
                        self.questions[counter].update(update)
                        counter += 1

                    self.time = int(self.decrypt_time(key_str=password, encrypted_data=self.questions[-1]['time']))
                    
                    if not str(self.time).isnumeric():
                        raise KeyError
                    
                    self.create_questions(len(self.questions))
                    self.load_button.destroy()
                    self.exit_button.place_forget()
                    self.bad_guy_check.start()
                    self.timer.start()
                else:
                    messagebox.showerror(title='Ошибка авторизации', message='Неверный пароль')
                    raise RuntimeError

        except KeyError as e:
            messagebox.showerror(title='Файл повреждён', message=f'Не найден ключ: {e}')
        except RuntimeError:
            pass
        except Exception as e:
            messagebox.showerror(title='Файл повреждён', message=f'{e}')

    def create_questions(self, n):
        for i in range(n):
            button = ctk.CTkButton(master=self.tab_frame, text=f"Вопрос {i+1}", command=lambda i=i: self.update_content(i+1))
            button.pack(side='left', padx=5, pady=5)
            self.tab_buttons.append(button)

    def create_widgets(self, id):
        self.textbox_question = ctk.CTkTextbox(master=self.content_frame, width=900)
        self.textbox_question.pack(side='top', padx=20, pady=10)
        self.textbox_question.insert('0.0', str(self.questions[id-1]['question']))
        self.textbox_question.configure(state=ctk.DISABLED)

        for i in range(len(self.questions[id-1]['answers'])):
                var = ctk.BooleanVar()
                answer_checkbox = ctk.CTkCheckBox(master=self.content_frame, text='', variable=var)
                answer_checkbox.place(rely=0.4 + i * 0.03, relx=0.27)
                self.checkboxes.append(answer_checkbox)

                answer_entry = ctk.CTkEntry(master=self.content_frame, width=850)
                answer_entry.place(rely=0.4 + i * 0.03, relx=0.29)
                answer_entry.insert(ctk.END, str(self.questions[id-1]['answers'][i]))
                answer_entry.configure(state=ctk.DISABLED)
                self.entries.append(answer_entry)

        self.button_answer = ctk.CTkButton(master=self.content_frame, text='Ответить', command=self.answer)
        self.button_answer.place(relx=0.7, rely=0.8)

            
    def update_content(self, tab_index):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.checkboxes.clear()
        self.entries.clear()

        self.current_question = tab_index
        self.create_widgets(self.questions[tab_index-1]['id'])

    def answer(self):
            answers = []
            correct_answers = []
            approved = True
            for i, entry in enumerate(self.entries):
                if self.checkboxes[i].get():
                    if entry.get() not in self.questions[self.current_question - 1]['correct']:
                        approved = False
                    else:
                        self.correct_counter += 1
            if self.correct_counter != len(self.questions[self.current_question -1 ]['correct']):
                approved = False

            self.correct_counter = 0
            self.questions_counter += 1
            if approved:
                self.score += 1

            if self.questions_counter == len(self.questions):
                for widget in self.tab_frame.winfo_children():
                    widget.destroy()

                for widget in self.content_frame.winfo_children():
                    widget.destroy()

                self.passed_flag = True
                self.passed_fio = ctk.CTkLabel(master=self.content_frame, text=self.fio, font=('Arial', 52, 'bold'))
                self.passed_fio.pack(side='top', pady=100)

                self.passed_label = ctk.CTkLabel(master=self.content_frame, text=f'Результат: {self.score} из {len(self.questions)}', font=('Arial', 82, 'bold'))
                self.passed_label.pack(side='top', pady=100)

                self.passed_time = ctk.CTkLabel(master=self.content_frame, text=f'{datetime.datetime.now().strftime('%H:%M | %d.%m.%Y')}', font=('Arial', 52, 'bold'))
                self.passed_time.pack(side='top', pady=100)
            else:
                self.tab_buttons[self.current_question - 1].configure(state=ctk.DISABLED)
                self.answered_label = ctk.CTkLabel(master=self.content_frame, text='Ответ записан', font=('Arial', 32, 'bold'), text_color='green')
                self.answered_label.place(relx=0.7, rely=0.85)
                self.button_answer.configure(state=ctk.DISABLED)
                for checkbox in self.checkboxes:
                    checkbox.configure(state=ctk.DISABLED)

if __name__ == '__main__':
    app = TestPlayer()
    app.mainloop()
