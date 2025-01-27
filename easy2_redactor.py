import customtkinter as ctk
import json
import re
from tkinter import filedialog, messagebox

class Redactor(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
    
        self.title('Easy2-redactor')
        self.state('zoomed')
        #self.overrideredirect(True)
        self.geometry("960x960")
        self.resizable(width=False, height=False)

        self.id = 1
        self.current_question = 1
        self.answer_checkboxes = []
        self.answer_entries = []
        self.questions = []

        self.canvas = ctk.CTkCanvas(self, height=32)
        self.canvas.config(bg='#242424', highlightbackground='#242424')
        self.canvas.pack(side='top', fill='x')

        self.tab_frame = ctk.CTkFrame(self.canvas)
        
        self.canvas.create_window((0, 0), window=self.tab_frame, anchor='nw')

        self.scrollbar = ctk.CTkScrollbar(self, orientation='horizontal', command=self.on_scroll)
        self.scrollbar.pack(side='top', fill='x')

        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.tab_frame.bind('<Configure>', self.on_frame_configure)

        self.add_tabs()

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(side='top', fill='both', expand=True)

        self.create_question_widgets()
        self.create_answers()

    def add_tabs(self, n=None):
        if n:
            for i in range(n-1):
                button = ctk.CTkButton(master=self.tab_frame, text=f"Вопрос {i+2}", command=lambda:self.update_content(int(re.findall(r'\b\d+\b', button.cget('text'))[0])))
                button.pack(side='left', padx=5, pady=5)
        else:
            button = ctk.CTkButton(master=self.tab_frame, text=f"Вопрос {self.id}", command=lambda:self.update_content(int(re.findall(r'\b\d+\b', button.cget('text'))[0])))
            button.pack(side='left', padx=5, pady=5)

    def on_scroll(self, *args):
        self.canvas.xview(*args)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def forget_widgets(self, forgotten):
        for i in forgotten:
            i.destroy()
        forgotten.clear()

    def create_answers(self, n=4, index=None):
        self.answer_checkboxes.clear()
        self.answer_entries.clear()
        try:
            if self.questions[index]:
                for i in range(n):
                    var = ctk.BooleanVar()
                    answer_checkbox = ctk.CTkCheckBox(master=self.content_frame, text='', variable=var)
                    answer_checkbox.place(rely=0.4 + i * 0.03, relx=0.24)

                    answer_entry = ctk.CTkEntry(master=self.content_frame, width=450)
                    answer_entry.place(rely=0.4 + i * 0.03, relx=0.28)
                    answer_entry.insert(ctk.END, f'{self.questions[index]['answers'][i]}')
                    
                    if self.questions[index]['answers'][i] in self.questions[index]['correct']:
                        answer_checkbox.select()

                    self.answer_checkboxes.append(answer_checkbox)
                    self.answer_entries.append(answer_entry)
                    self.number_button.configure(text=f'Кол-во ответов: {n}')

        except TypeError:
            for i in range(n):
                var = ctk.BooleanVar()
                answer_checkbox = ctk.CTkCheckBox(master=self.content_frame, text='', variable = var)
                answer_checkbox.place(rely=0.4 + i * 0.03, relx=0.24)

                answer_entry = ctk.CTkEntry(master=self.content_frame, width=450)
                answer_entry.place(rely=0.4 + i * 0.03, relx=0.28)

                self.answer_checkboxes.append(answer_checkbox)
                self.answer_entries.append(answer_entry)
            

    def create_question_widgets(self, change_flag=False):
        self.label_question = ctk.CTkLabel(master=self.content_frame, text='Введите вопрос', font=('Arial', 20, 'bold'))
        self.label_question.pack(side='top', pady=10)

        self.textbox_question = ctk.CTkTextbox(master=self.content_frame, width=900)
        self.textbox_question.pack(side='top', padx=20, pady=10)

        self.label_question = ctk.CTkLabel(master=self.content_frame, text='Введите ответы', font=('Arial', 20, 'bold'))
        self.label_question.pack(side='top', pady=40)

        self.question_save_button = ctk.CTkButton(master=self.content_frame, text='Записать вопрос', command=self.record_question)
        self.update_button = ctk.CTkButton(master=self.content_frame, text='Сохранить изменения', command=lambda:self.update_question(self.current_question))

        if not change_flag:
            self.question_save_button.place(relx=0.3, rely=0.8)
        else:
            self.update_button.place(relx=0.3, rely=0.8)
            pass

        self.record_test_button = ctk.CTkButton(master=self.content_frame, text='Сохранить тест', command=self.save_test)
        self.record_test_button.place(relx=0.55, rely=0.8)

        self.number_button = ctk.CTkButton(master=self.content_frame, text=f'Кол-во ответов: 4', command=self.change_answer_count)
        self.number_button.place(relx=0.03, rely=0.4)

        self.open_button = ctk.CTkButton(master=self.content_frame, text='Открыть тест', command=self.open_file)
        self.open_button.place(relx=0.03, rely=0.45)

    def change_answer_count(self):
        self.dialog = ctk.CTkInputDialog(text='Введите кол-во ответов для текущего вопроса (не больше 12)', title='Выберите кол-во ответов')
        n = int(self.dialog.get_input())

        while(n > 12):
            self.dialog = ctk.CTkInputDialog(text='Введите кол-во ответов для текущего вопроса (не больше 12)', title='Выберите кол-во ответов')
            n = int(self.dialog.get_input())

        self.forget_widgets(self.answer_entries)
        self.forget_widgets(self.answer_checkboxes)

        self.answer_checkboxes.clear()
        self.answer_entries.clear()

        self.create_answers(n)
        self.number_button.configure(text=f'Кол-во ответов: {n}')

    def update_content(self, tab_index):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.current_question = tab_index

        try:
            self.questions[tab_index-1]['answers']
            self.create_question_widgets(True)
            self.create_answers(len(self.questions[tab_index-1]['answers']), tab_index-1)
            self.textbox_question.insert('0.0', f'{self.questions[tab_index-1]['question']}')

        except IndexError:
            self.create_question_widgets(False)
            self.create_answers()

    def record_question(self):
        question_text = self.textbox_question.get('0.0', 'end')
        answers = []
        correct_answers = []
        
        for i, entry in enumerate(self.answer_entries):
            answers.append(entry.get())
            if self.answer_checkboxes[i].get():
                correct_answers.append(entry.get())
        
        self.questions.append({
            "question": question_text,
            "answers": answers,
            "correct": correct_answers,
            "id": self.id
        })
        self.id += 1
        self.add_tabs()
        self.question_save_button.destroy()
        self.update_button.place(relx=0.3, rely=0.8)
        self.label_success_record = ctk.CTkLabel(master=self.content_frame, text='Вопрос записан в память', font=('Arial', 12, 'bold'), text_color='green')
        self.label_success_record.place(relx=0.3, rely=0.85)

    def update_question(self, index):
        question_text = self.textbox_question.get('0.0', 'end')
        answers = []
        correct_answers = []
        
        for i, entry in enumerate(self.answer_entries):
            answers.append(entry.get())
            if self.answer_checkboxes[i].get():
                correct_answers.append(entry.get())
        
        self.questions[index-1]= {
            "question": question_text,
            "answers": answers,
            "correct": correct_answers,
            "id": index
        }
        self.label_success_record.destroy()
        self.label_success_edit = ctk.CTkLabel(master=self.content_frame, text='Изменения сохранены', font=('Arial', 12, 'bold'), text_color='green')
        self.label_success_edit.place(relx=0.3, rely=0.85)

    def save_test(self):
        if not self.questions:
            return

        save_path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[("JSON files", "*.json")])
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=4)
        messagebox.showinfo(title='Сохранение', message=f'Файл сохранён как {save_path}')
    
    def open_file(self):
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        with open(file, 'r', encoding='utf-8') as f:
            self.id = 1
            self.current_question = 1
            self.answer_checkboxes = []
            self.answer_entries = []
            for widget in self.tab_frame.winfo_children():
                widget.destroy()
            self.add_tabs()
            data = json.load(f)
            self.add_tabs(len(data))
            self.questions = data
            self.id = len(data) + 1
        self.add_tabs()
        self.update_content(1)
        messagebox.showinfo(title='Загрузка', message=f'Успешно загружен файл {file}')

if __name__ == '__main__':
    app = Redactor()
    app.mainloop()
