import tkinter as tk
from tkinter import messagebox
import json
import os

class QuizEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Редактор тестов")

        self.questions = []

        self.create_widgets()

        self.load_quiz()

    def create_widgets(self):
        # Ввод вопроса
        self.question_label = tk.Label(self.master, text="Вопрос:")
        self.question_label.pack()
        self.question_entry = tk.Entry(self.master, width=50)
        self.question_entry.pack()

        # Ввод вариантов ответов
        self.options_label = tk.Label(self.master, text="Варианты ответов (через запятую):")
        self.options_label.pack()
        self.options_entry = tk.Entry(self.master, width=50)
        self.options_entry.pack()

        # Ввод правильного ответа
        self.correct_answer_label = tk.Label(self.master, text="Правильный ответ:")
        self.correct_answer_label.pack()
        self.correct_answer_entry = tk.Entry(self.master, width=50)
        self.correct_answer_entry.pack()

        # Добавить вопрос
        self.add_button = tk.Button(self.master, text="Добавить вопрос", command=self.add_question)
        self.add_button.pack()

        # Сохранить тест
        self.save_button = tk.Button(self.master, text="Сохранить тест", command=self.save_quiz)
        self.save_button.pack()

    def add_question(self):
        question_text = self.question_entry.get()
        options_text = self.options_entry.get()
        correct_answer = self.correct_answer_entry.get()

        if not question_text or not options_text or not correct_answer:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля.")
            return

        options = [opt.strip() for opt in options_text.split(",")]
        if correct_answer not in options:
            messagebox.showwarning("Ошибка", "Правильный ответ должен быть среди вариантов.")
            return

        self.questions.append({
            "question": question_text,
            "options": options,
            "correct": correct_answer
        })

        # Очистить поля ввода
        self.question_entry.delete(0, tk.END)
        self.options_entry.delete(0, tk.END)
        self.correct_answer_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", "Вопрос добавлен!")

    def save_quiz(self):
        if not self.questions:
            messagebox.showwarning("Ошибка", "Нет вопросов для сохранения.")
            return

        save_path = os.path.join('created', 'quiz.json')
        with open(save_path, 'w') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=4)
        
        messagebox.showinfo("Успех", f"Тест сохранен в {save_path}!")
        self.questions.clear()

    def load_quiz(self):
        try:
            with open(os.path.join('tests', 'quiz.json'), 'r') as f:
                self.questions = json.load(f)
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    quiz_editor = QuizEditor(root)
    root.mainloop()