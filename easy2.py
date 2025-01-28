import customtkinter as ctk
import json
import re
from tkinter import filedialog, messagebox
import threading
import time
from PIL import Image
import pyautogui

class TestPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.width, self.height = pyautogui.size()
        self.title('Easy2-redactor')
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

        self.bad_guy_check = threading.Thread(target=self.bad_guy_alert)

    def bad_guy_alert(self):
        time.sleep(1)
        coordinates_pool_x = []
        coordinates_pool_x.append(self.width - 60)
        coordinates_pool_x.append(int(self.width*0.8))
        coordinates_pool_y = []
        coordinates_pool_y.append(self.height - 20)
        coordinates_pool_y.append(int(self.height*0.5))
        while(True):
            time.sleep(0.1)
            screenshot = pyautogui.screenshot()
            for check in range(2):
                if screenshot.getpixel((coordinates_pool_x[check], coordinates_pool_y[check])) != (43,43,43):
                    for widget in self.tab_frame.winfo_children():
                        widget.destroy()

                    for widget in self.content_frame.winfo_children():
                        widget.destroy()

                    self.passed_label = ctk.CTkLabel(master=self.content_frame, text=f'ПОПАЛСЯ, ПИДОРАС', font=('Arial', 72, 'bold'), text_color='red')
                    self.passed_label.pack(side='top', pady=100)
        
    def on_scroll(self, *args):
        self.canvas.xview(*args)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def load_test(self):
        try:
            file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])

            if not file:
                raise RuntimeError
            
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for question in data:
                    question['question']
                    question['answers']
                    question['correct']
                    question['id']

                self.questions = data
                self.create_questions(len(self.questions))
                self.load_button.destroy()
            self.bad_guy_check.start()

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
        self.textbox_question.insert('0.0', f'{self.questions[id-1]['question']}')
        self.textbox_question.configure(state=ctk.DISABLED)

        for i in range(len(self.questions[id-1]['answers'])):
                var = ctk.BooleanVar()
                answer_checkbox = ctk.CTkCheckBox(master=self.content_frame, text='', variable=var)
                answer_checkbox.place(rely=0.4 + i * 0.03, relx=0.27)
                self.checkboxes.append(answer_checkbox)

                answer_entry = ctk.CTkEntry(master=self.content_frame, width=850)
                answer_entry.place(rely=0.4 + i * 0.03, relx=0.29)
                answer_entry.insert(ctk.END, f'{self.questions[id-1]['answers'][i]}')
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
            self.correct_counter = 0
            for i, entry in enumerate(self.entries):
                if self.checkboxes[i].get():
                    if entry.get() not in self.questions[self.current_question - 1]['correct']:
                        approved = False
                    else:
                        self.correct_counter += 1
            if self.correct_counter != len(self.questions[self.current_question -1 ]['correct']):
                approved = False

            self.correct_counter = 0

            if approved:
                self.score += 1

            self.tab_buttons[self.current_question - 1].configure(state=ctk.DISABLED)

            if self.current_question + 1 > len(self.questions):
                for widget in self.tab_frame.winfo_children():
                    widget.destroy()

                for widget in self.content_frame.winfo_children():
                    widget.destroy()

                self.passed_label = ctk.CTkLabel(master=self.content_frame, text=f'Результат: {self.score} из {len(self.questions)}', font=('Arial', 72, 'bold'))
                self.passed_label.pack(side='top', pady=100)
            else:
                self.update_content(self.current_question + 1)


if __name__ == '__main__':
    app = TestPlayer()
    app.mainloop()