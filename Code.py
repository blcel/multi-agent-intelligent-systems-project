import tkinter as tk
from tkinter import messagebox
import random
import heapq
import csv
import os
import time

GRID_SIZE = 8
CELL_SIZE = 40
NUM_DANGER = 12

class GridWorld(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("مقایسه سه عامل روی گرید")
        self.geometry(f"{GRID_SIZE*CELL_SIZE+400}x{GRID_SIZE*CELL_SIZE+60}")
        self.resizable(False, False)

        self.grid_data, self.start, self.goal = self.create_grid()
        self.canvas = tk.Canvas(self, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg="white")
        self.canvas.pack(side="left")
        self.draw_grid()

        control_frame = tk.Frame(self)
        control_frame.pack(side="right", fill="y", padx=10, pady=10)

        self.agent_var = tk.StringVar(value="Simple Reflex")
        tk.Label(control_frame, text="انتخاب عامل", font=("B Nazanin", 16)).pack(pady=10)
        agents = ["Simple Reflex", "Goal-Based (A*)", "Model-Based"]
        for agent in agents:
            tk.Radiobutton(control_frame, text=agent, variable=self.agent_var, value=agent, font=("B Nazanin", 12)).pack(anchor="w")

        tk.Button(control_frame, text="اجرای عامل", command=self.run_agent, font=("B Nazanin", 12), bg="#f57c00", fg="white").pack(pady=5)
        tk.Button(control_frame, text="اجرای همه و مقایسه", command=self.run_all_agents, font=("B Nazanin", 12), bg="#fbc02d").pack(pady=5)
        tk.Button(control_frame, text="ساخت گرید جدید", command=self.new_grid, font=("B Nazanin", 12), bg="#388e3c", fg="white").pack(pady=5)

        self.result_text = tk.Text(control_frame, width=40, height=15, font=("B Nazanin", 12))
        self.result_text.pack()

    def create_grid(self):
        grid = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        start = (0, 0)
        grid[start[0]][start[1]] = 'S'
        while True:
            goal = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if goal != start:
                grid[goal[0]][goal[1]] = 'G'
                break
        danger_set = set()
        while len(danger_set) < NUM_DANGER:
            pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if pos != start and pos != goal and pos not in danger_set:
                danger_set.add(pos)
                grid[pos[0]][pos[1]] = 'D'
        return grid, start, goal

    def draw_grid(self, path=None):
        self.canvas.delete("all")
        colors = {
            '.': '#fff9c4',
            'S': '#fb8c00',
            'G': '#43a047',
            'D': '#e53935'
        }
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1 = j*CELL_SIZE
                y1 = i*CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                cell_val = self.grid_data[i][j]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[cell_val], outline='black')

        if path:
            for (x, y) in path:
                x1 = y*CELL_SIZE + CELL_SIZE//4
                y1 = x*CELL_SIZE + CELL_SIZE//4
                x2 = x1 + CELL_SIZE//2
                y2 = y1 + CELL_SIZE//2
                self.canvas.create_oval(x1, y1, x2, y2, fill='#ffa726', outline='')

    def simple_reflex(self):
        path = [self.start]
        visited = set()
        pos = self.start
        directions = [(0,1),(1,0),(0,-1),(-1,0)]
        while True:
            visited.add(pos)
            for dx, dy in directions:
                nx, ny = pos[0]+dx, pos[1]+dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if self.grid_data[nx][ny] != 'D' and (nx, ny) not in visited:
                        pos = (nx, ny)
                        path.append(pos)
                        if self.grid_data[nx][ny] == 'G':
                            return path, False, True
                        break
            else:
                return path, False, False

    def heuristic(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def a_star(self):
        start = self.start
        goal = self.goal
        heap = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        while heap:
            _, current = heapq.heappop(heap)
            if current == goal:
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path, False, True
            for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                nx, ny = current[0]+dx, current[1]+dy
                neighbor = (nx, ny)
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if self.grid_data[nx][ny] == 'D':
                        continue
                    new_cost = cost_so_far[current] + 1
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        priority = new_cost + self.heuristic(goal, neighbor)
                        heapq.heappush(heap, (priority, neighbor))
                        came_from[neighbor] = current
        return [], False, False

    def model_based(self):
        path = []
        visited = set()
        pos = self.start
        goal = self.goal
        def safe_neighbors(x, y):
            neighbors = []
            for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if self.grid_data[nx][ny] != 'D' and (nx, ny) not in visited:
                        neighbors.append((nx, ny))
            return neighbors
        def dfs(pos):
            if pos == goal:
                path.append(pos)
                return True
            visited.add(pos)
            path.append(pos)
            for neighbor in sorted(safe_neighbors(*pos), key=lambda n: self.heuristic(n, goal)):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
            path.pop()
            return False
        reached = dfs(pos)
        return path, False, reached

    def save_to_csv(self, agent_name, steps, success, elapsed_time):
        data = {
            "Agent": agent_name,
            "Steps": steps,
            "Reached Goal": "Yes" if success else "No",
            "Time Taken (s)": round(elapsed_time, 4)
        }
        file_name = "experimental_data.csv"
        file_exists = os.path.isfile(file_name)

        with open(file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def run_agent(self):
        agent = self.agent_var.get()
        start_time = time.time()

        if agent == "Simple Reflex":
            path, danger, success = self.simple_reflex()
        elif agent == "Goal-Based (A*)":
            path, danger, success = self.a_star()
        else:
            path, danger, success = self.model_based()

        elapsed_time = time.time() - start_time
        self.draw_grid(path)

        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, f"عامل انتخاب شده: {agent}\n")
        self.result_text.insert(tk.END, f"تعداد قدم‌ها: {len(path)}\n")
        self.result_text.insert(tk.END, f"رسیدن به هدف: {'بله' if success else 'خیر'}\n")

        self.save_to_csv(agent, len(path), success, elapsed_time)

    def run_all_agents(self):
        agents = [("Simple Reflex", self.simple_reflex),
                  ("Goal-Based (A*)", self.a_star),
                  ("Model-Based", self.model_based)]
        self.result_text.delete('1.0', tk.END)

        results = []
        goal_path_len = None

        for name, func in agents:
            start_time = time.time()
            path, danger, success = func()
            elapsed_time = time.time() - start_time
            self.save_to_csv(name, len(path), success, elapsed_time)

            if name == "Goal-Based (A*)":
                goal_path_len = len(path) if success else None
                results.append((name, len(path), success, None))
                continue

            if goal_path_len and success:
                optimal = (len(path) == goal_path_len)
            else:
                optimal = False
            results.append((name, len(path), success, optimal))

        results = [r for r in results if r[0] == "Goal-Based (A*)"] + [r for r in results if r[0] != "Goal-Based (A*)"]

        self.result_text.tag_configure("header", background="#ffd3b6", foreground="black", font=("B Nazanin", 12, "bold"))
        self.result_text.tag_configure("ok", background="#a8e6cf", foreground="black")
        self.result_text.tag_configure("notok", background="#ff9aa2", foreground="black")
        self.result_text.tag_configure("normal", background="#fff3e0")

        header = f"{'بهینه بودن':<15}{'رسیدن به هدف':<15}{'زمان طی شده':<15}{'نام عامل انتخابی':<15}\n"
        self.result_text.insert(tk.END, header, "header")
        for r in results:
            name, steps, success, optimal = r
            line = f"{name:<15}        {steps:<15}{'     بله' if success else '     خیر':<15}"
            if optimal is None:
                line += f"{'     -':<15}\n"
            else:
                line += f"{'     بله' if optimal else '     خیر':<15}\n"
            tag = "ok" if success else "notok"
            self.result_text.insert(tk.END, line, tag)

    def new_grid(self):
        self.grid_data, self.start, self.goal = self.create_grid()
        self.draw_grid()
        self.result_text.delete('1.0', tk.END)

if __name__ == "__main__":
    app = GridWorld()
    app.mainloop()
