"""簡單的貪食蛇小遊戲（Tkinter 版）

執行方式：
    python3 snake_game.py

操作方式：
    方向鍵：控制移動
    R：遊戲結束後重新開始
    Q：離開
"""

from __future__ import annotations

from pathlib import Path
import random
import tkinter as tk


CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
INITIAL_SPEED_MS = 120
SPEEDUP_EVERY_FOOD = 5
MIN_SPEED_MS = 70
HIGH_SCORE_FILE = Path(__file__).with_name(".snake_high_score")


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
        self.high_score = self.load_high_score()
        self.blink_phase = 0
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
        self.blink_phase = 0

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
            self.update_high_score()
            self.draw()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.update_high_score()
            if self.score % SPEEDUP_EVERY_FOOD == 0:
                self.speed_ms = max(MIN_SPEED_MS, self.speed_ms - 10)
            self.food = self.random_empty_cell()
        else:
            self.snake.pop()

        self.draw()
        self.blink_phase += 1
        self.schedule_next_tick()

    def load_high_score(self) -> int:
        try:
            return max(0, int(HIGH_SCORE_FILE.read_text(encoding="utf-8").strip()))
        except (FileNotFoundError, ValueError):
            return 0

    def update_high_score(self) -> None:
        if self.score <= self.high_score:
            return
        self.high_score = self.score
        HIGH_SCORE_FILE.write_text(str(self.high_score), encoding="utf-8")

    def draw(self) -> None:
        self.canvas.delete("all")

        snake_len = max(1, len(self.snake) - 1)
        for i, (x, y) in enumerate(self.snake):
            color = self.get_snake_color(i, snake_len)
            self.draw_cell(x, y, color, rounded=True, with_shadow=True)

        fx, fy = self.food
        self.draw_food(fx, fy)
        self.draw_high_score()

        if self.game_over:
            self.info_var.set(f"遊戲結束！分數：{self.score}（按 R 重新開始，Q 離開）")
        else:
            self.info_var.set(f"分數：{self.score} | 方向鍵移動 | R 重開 | Q 離開")

    def draw_food(self, x: int, y: int) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        inset = 3 if self.blink_phase % 2 == 0 else 2
        glow_color = "#ff8f8f" if self.blink_phase % 2 == 0 else "#ff4c4c"

        self.canvas.create_oval(
            x1 + inset,
            y1 + inset,
            x2 - inset,
            y2 - inset,
            fill="#e53935",
            outline=glow_color,
            width=2,
        )
        self.canvas.create_oval(
            x1 + 6,
            y1 + 6,
            x1 + 10,
            y1 + 10,
            fill="#ffc1c1",
            outline="",
        )
        self.canvas.create_rectangle(
            x1 + 9,
            y1 + 2,
            x1 + 11,
            y1 + 6,
            fill="#6d4c41",
            outline="",
        )

    def draw_high_score(self) -> None:
        width = GRID_WIDTH * CELL_SIZE
        self.canvas.create_text(
            width - 12,
            10,
            text=f"High Score: {self.high_score}",
            fill="#f5f5f5",
            font=("Arial", 12, "bold"),
            anchor="ne",
        )

    def get_snake_color(self, index: int, snake_len: int) -> str:
        ratio = min(1.0, index / snake_len)
        head_rgb = (26, 105, 52)
        tail_rgb = (127, 255, 163)
        red = int(head_rgb[0] + (tail_rgb[0] - head_rgb[0]) * ratio)
        green = int(head_rgb[1] + (tail_rgb[1] - head_rgb[1]) * ratio)
        blue = int(head_rgb[2] + (tail_rgb[2] - head_rgb[2]) * ratio)
        return f"#{red:02x}{green:02x}{blue:02x}"

    def draw_cell(
        self,
        x: int,
        y: int,
        color: str,
        rounded: bool = False,
        with_shadow: bool = False,
    ) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        if not rounded:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#101010")
            return

        pad = 1
        radius = 5
        if with_shadow:
            self.draw_rounded_rect(
                x1 + pad + 1,
                y1 + pad + 1,
                x2 - pad + 1,
                y2 - pad + 1,
                radius,
                fill="#000000",
                outline="",
                stipple="gray25",
            )

        self.draw_rounded_rect(
            x1 + pad,
            y1 + pad,
            x2 - pad,
            y2 - pad,
            radius,
            fill=color,
            outline="#1b1b1b",
        )

    def draw_rounded_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        radius: int,
        **kwargs: object,
    ) -> None:
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        self.canvas.create_polygon(points, smooth=True, **kwargs)


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
