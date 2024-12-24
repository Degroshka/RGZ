import tkinter as tk
from tkinter import ttk, messagebox

class Task:
    def __init__(self, name, execution_time):
        self.name = name
        self.remaining_time = execution_time

class OSDispatcherEmulator:
    def __init__(self):
        self.tasks = []
        self.completed_tasks = []
        self.task_progress_bars = {}
        self.is_executing = False  # Flag for task execution state
        self.current_task_index = -1  # Track current task for asynchronous execution

        self.root = tk.Tk()
        self.root.title("Эмулятор диспетчера ОС (Linux)")
        self.root.geometry("800x500")

        self.setup_ui()
        self.root.mainloop()

    def setup_ui(self):
        # Input Fields
        input_frame = tk.Frame(self.root, padx=10, pady=10)
        input_frame.grid(row=0, column=0, sticky="nw")

        tk.Label(input_frame, text="Имя задачи").grid(row=0, column=0, sticky="w")
        self.task_name_entry = tk.Entry(input_frame, width=20)
        self.task_name_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Время выполнения").grid(row=1, column=0, sticky="w")
        self.execution_time_entry = tk.Entry(input_frame, width=20)
        self.execution_time_entry.grid(row=1, column=1, padx=5)

        tk.Button(input_frame, text="Добавить задачу", command=self.add_task).grid(row=2, column=0, columnspan=2, pady=5)

        # Task List
        task_frame = tk.Frame(self.root, padx=10, pady=10)
        task_frame.grid(row=0, column=1, sticky="nsew")

        tk.Label(task_frame, text="Список задач").pack(anchor="w")
        self.task_listbox = tk.Listbox(task_frame, height=10, width=30)
        self.task_listbox.pack(fill="both", expand=True)

        # Progress Bars
        progress_frame = tk.Frame(self.root, padx=10, pady=10)
        progress_frame.grid(row=0, column=2, sticky="nsew")

        tk.Label(progress_frame, text="Прогресс выполнения задач").pack(anchor="w")
        self.progress_canvas = tk.Canvas(progress_frame)
        self.progress_canvas.pack(fill="both", expand=True)
        self.progress_frame = tk.Frame(self.progress_canvas)
        self.progress_canvas.create_window((0, 0), window=self.progress_frame, anchor="nw")
        self.progress_frame.bind("<Configure>", self.update_scroll_region)

        # Scrollbar for Progress Bars
        self.scrollbar = ttk.Scrollbar(progress_frame, orient="vertical", command=self.progress_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.progress_canvas.config(yscrollcommand=self.scrollbar.set)

        # Completed Tasks
        completed_frame = tk.Frame(self.root, padx=10, pady=10)
        completed_frame.grid(row=0, column=3, sticky="nsew")

        tk.Label(completed_frame, text="Список выполненных задач").pack(anchor="w")
        self.completed_listbox = tk.Listbox(completed_frame, height=10, width=30)
        self.completed_listbox.pack(fill="both", expand=True)

        # Control Buttons
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.grid(row=1, column=0, columnspan=4, sticky="ew")

        tk.Label(control_frame, text="Квант времени").grid(row=0, column=0, padx=5)
        self.time_quantum_entry = tk.Entry(control_frame, width=10)
        self.time_quantum_entry.grid(row=0, column=1, padx=5)
        self.time_quantum_entry.insert(0, "10")

        tk.Button(control_frame, text="Выполнять", command=self.start_execution).grid(row=0, column=2, padx=10)
        tk.Button(control_frame, text="Очистить", command=self.clear_all).grid(row=0, column=3, padx=10)

    def update_scroll_region(self, event=None):
        self.progress_canvas.config(scrollregion=self.progress_canvas.bbox("all"))

    def add_task(self):
        name = self.task_name_entry.get()
        try:
            execution_time = int(self.execution_time_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Время выполнения должно быть числом")
            return

        if not name or execution_time <= 0:
            messagebox.showerror("Ошибка", "Введите корректные данные для задачи")
            return

        task = Task(name, execution_time)
        self.tasks.append(task)

        # Create and display a progress bar with a label for the new task
        frame = tk.Frame(self.progress_frame)
        frame.pack(fill="x", pady=2)

        tk.Label(frame, text=task.name, width=20, anchor="w").pack(side="left", padx=5)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=execution_time)
        progress_bar.pack(side="left", fill="x", expand=True)
        self.task_progress_bars[task.name] = (progress_var, progress_bar, frame)

        self.update_task_list()

    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, f"{task.name}: {task.remaining_time}")

    def start_execution(self):
        if self.is_executing:
            messagebox.showinfo("Внимание", "Задачи уже выполняются!")
            return
        self.is_executing = True
        self.current_task_index = 0
        self.execute_tasks_async()

    def execute_tasks_async(self):
        if not self.is_executing or self.current_task_index >= len(self.tasks):
            self.is_executing = False
            return

        task = self.tasks[self.current_task_index]
        time_quantum = int(self.time_quantum_entry.get())
        progress_var = self.task_progress_bars[task.name][0]

        if task.remaining_time > 0:
            task.remaining_time -= 1
            progress_var.set(progress_var.get() + 1)
            self.root.update_idletasks()
            self.root.after(50, self.execute_tasks_async)
        else:
            self.completed_tasks.append(task)
            self.completed_listbox.insert(tk.END, f"{task.name}: Завершено")
            self.task_progress_bars[task.name][2].destroy()
            del self.task_progress_bars[task.name]
            self.tasks.pop(self.current_task_index)

            self.execute_tasks_async()

    def clear_all(self):
        self.is_executing = False  # Stop ongoing task execution safely
        self.tasks.clear()
        self.completed_tasks.clear()
        self.task_listbox.delete(0, tk.END)
        self.completed_listbox.delete(0, tk.END)

        # Clear progress bars
        for _, (_, _, bar) in list(self.task_progress_bars.values()):
            bar.destroy()
        self.task_progress_bars.clear()

if __name__ == "__main__":
    OSDispatcherEmulator()
