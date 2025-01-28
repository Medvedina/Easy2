import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class TestReader:
    def __init__(self, master):
        self.master = master
        self.master.title("Читатель тестов")

        self.questions = []
        self.current_question = 0

        self.create_widgets()

        self.load_quiz()

    def create_widgets(self):
        # Текст вопроса
        self.question_label = tk.Label(self.master, font=("Arial", 16), wraplength=600)
        self.question_label.pack()

        # Варианты ответов
        self.options_frame = tk.Frame(self.master)
        self.options_frame.pack()

        # Правильный ответ
        self.correct_label = tk.Label(self.master, text="Правильный ответ:")
        self.correct_label.pack()

        # Боковое меню
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side=tk.BOTTOM)

        self.previous_button = tk.Button(self.button_frame, text="Предыдущий вопрос", command=self.previous_question)
        self.previous_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.button_frame, text="Следующий вопрос", command=self.next_question)
        self.next_button.pack(side=tk.LEFT)

    def load_quiz(self):
        try:
            with open(os.path.join('tests', 'quiz.json'), 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
        except FileNotFoundError:
            messagebox.showwarning("Ошибка", "Нет теста для чтения.")
            return

        if self.questions:
            self.show_question()

    def show_question(self):
        if self.current_question < len(self.questions):
            self.question_label['text'] = self.questions[self.current_question]['question']
            for widget in self.options_frame.winfo_children():
                widget.destroy()

            correct_answer = self.questions[self.current_question]['correct']
            for option in self.questions[self.current_question]['options']:
                var = tk.IntVar()
                radio_button = ttk.Radiobutton(self.options_frame, text=option, variable=var)
                radio_button.pack(fill='x')
                if option == correct_answer:
                    var.set(1)

            self.correct_label['text'] = f"Правильный ответ: {correct_answer}"
        else:
            self.question_label['text'] = "Тест окончен!"

    def previous_question(self):
        self.current_question = max(0, self.current_question - 1)
        self.show_question()

    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_question()

if __name__ == "__main__":
    root = tk.Tk()
    test_reader = TestReader(root)
    root.mainloop()