"""簡單的貪食蛇小遊戲（Tkinter 版）

執行方式：
    python3 snake_game.py

操作方式：
    方向鍵：控制移動
    R：遊戲結束後重新開始
    Q：離開
"""

from __future__ import annotations

import random
import tkinter as tk


CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
INITIAL_SPEED_MS = 120
SPEEDUP_EVERY_FOOD = 5
MIN_SPEED_MS = 70


class SnakeGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Snake Game")
        self.canvas = tk.Canvas(
            root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="#1f1f1f",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.info_var = tk.StringVar()
        self.info_label = tk.Label(
            root,
            textvariable=self.info_var,
            font=("Arial", 12),
            pady=8,
        )
        self.info_label.pack()

        self.root.bind("<Up>", lambda _: self.set_direction((0, -1)))
        self.root.bind("<Down>", lambda _: self.set_direction((0, 1)))
        self.root.bind("<Left>", lambda _: self.set_direction((-1, 0)))
        self.root.bind("<Right>", lambda _: self.set_direction((1, 0)))
        self.root.bind("r", lambda _: self.reset())
        self.root.bind("R", lambda _: self.reset())
        self.root.bind("q", lambda _: self.root.destroy())
        self.root.bind("Q", lambda _: self.root.destroy())

        self.after_id: str | None = None
        self.reset()

    def reset(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.random_empty_cell()
        self.score = 0
        self.speed_ms = INITIAL_SPEED_MS
        self.game_over = False

        self.draw()
        self.schedule_next_tick()

    def random_empty_cell(self) -> tuple[int, int]:
        occupied = set(self.snake)
        empty_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        return random.choice(empty_cells)

    def set_direction(self, new_direction: tuple[int, int]) -> None:
        if self.game_over:
            return

        dx, dy = self.direction
        ndx, ndy = new_direction
        if (dx, dy) == (-ndx, -ndy):
            return
        self.next_direction = new_direction

    def schedule_next_tick(self) -> None:
        self.after_id = self.root.after(self.speed_ms, self.tick)

    def tick(self) -> None:
        if self.game_over:
            return

        self.direction = self.next_direction
        dx, dy = self.direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        nx, ny = new_head
        hit_wall = nx < 0 or nx >= GRID_WIDTH or ny < 0 or ny >= GRID_HEIGHT
        hit_self = new_head in self.snake
        if hit_wall or hit_self:
            self.game_over = True
            self.draw()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            if self.score % SPEEDUP_EVERY_FOOD == 0:
                self.speed_ms = max(MIN_SPEED_MS, self.speed_ms - 10)
            self.food = self.random_empty_cell()
        else:
            self.snake.pop()

        self.draw()
        self.schedule_next_tick()

    def draw(self) -> None:
        self.canvas.delete("all")

        for i, (x, y) in enumerate(self.snake):
            color = "#7CFC00" if i == 0 else "#3CB371"
            self.draw_cell(x, y, color)

        fx, fy = self.food
        self.draw_cell(fx, fy, "#FF6347")

        if self.game_over:
            self.info_var.set(f"遊戲結束！分數：{self.score}（按 R 重新開始，Q 離開）")
        else:
            self.info_var.set(f"分數：{self.score} | 方向鍵移動 | R 重開 | Q 離開")

    def draw_cell(self, x: int, y: int, color: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#101010")


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
