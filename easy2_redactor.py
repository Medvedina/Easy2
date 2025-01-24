import customtkinter as ctk
import json
import os
from tkinter import messagebox

class Redactor(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.title('Easy2-redactor')
        self.state('zoomed')
        #self.overrideredirect(True)
        self.geometry("960x960")
        self.resizable(width=False, height=False)
        self.tabview = ctk.CTkTabview(master=self, height=940, anchor='nw')

        self.id = 1

        self.create_question_widgets()

        self.answer_checkboxes = []
        self.answer_entries = []
        self.questions = []

        self.create_answers()

    def forget_widgets(self, forgotten):
        for i in forgotten:
            i.destroy()
        forgotten.clear()

    def create_answers(self, n=4):
        self.answer_checkboxes.clear()
        self.answer_entries.clear()
        for i in range(n):
            var = ctk.BooleanVar()
            answer_checkbox = ctk.CTkCheckBox(master=self.tabview.tab(f'{self.id}'), text='', variable = var)
            answer_checkbox.place(rely=0.4 + i * 0.03, relx=0.24)

            answer_entry = ctk.CTkEntry(master=self.tabview.tab(f'{self.id}'), width=450)
            answer_entry.place(rely=0.4 + i * 0.03, relx=0.28)

            self.answer_checkboxes.append(answer_checkbox)
            self.answer_entries.append(answer_entry)

    def create_question_widgets(self):
        self.tabview.grid(row=0, column=0, sticky='n')
        self.tabview.add(f'{self.id}')
        
        self.label_question = ctk.CTkLabel(master=self.tabview.tab(f'{self.id}'), text='Введите вопрос', font=('Arial', 20, 'bold'))
        self.label_question.pack(side='top', pady=10)

        self.textbox_question = ctk.CTkTextbox(master=self.tabview.tab(f'{self.id}'), width=900)
        self.textbox_question.pack(side='top', padx=20, pady=10)

        self.label_question = ctk.CTkLabel(master=self.tabview.tab(f'{self.id}'), text='Введите ответы', font=('Arial', 20, 'bold'))
        self.label_question.pack(side='top', pady=40)

        self.question_save_button = ctk.CTkButton(master=self.tabview.tab(f'{self.id}'), text='Записать вопрос', command=self.record_question)
        self.question_save_button.place(relx=0.35, rely=0.8)

        self.record_test_button = ctk.CTkButton(master=self.tabview.tab(f'{self.id}'), text='Сохранить тест', command=self.save_test)
        self.record_test_button.place(relx=0.55, rely=0.8)

        self.number_button = ctk.CTkButton(master=self.tabview.tab(f'{self.id}'), text=f'Кол-во ответов: 4', command=self.change_answer_count)
        self.number_button.place(relx=0.03, rely=0.4)
    
    def change_answer_count(self):
        self.dialog = ctk.CTkInputDialog(text='Введите кол-во ответов для текущего вопроса (не больше 12)', title='Выберите кол-во ответов')
        n = int(self.dialog.get_input())
        self.forget_widgets(self.answer_entries)
        self.forget_widgets(self.answer_checkboxes)
        self.create_answers(n)
        self.number_button.configure(text=f'Кол-во ответов: {n}')

    def record_question(self):
        if self.id > 32:
            self.tabview.delete(f'{self.id-32}')
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
        self.create_question_widgets()
        self.create_answers()

    def save_test(self):
        if not self.questions:
            return

        save_path = os.path.join('created', 'test.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    app = Redactor()
    app.mainloop()