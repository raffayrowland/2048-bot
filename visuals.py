import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MOVE_CODE_TO_NAME = {
    0: "left",
    1: "right",
    2: "down",
    3: "up",
    "a": "left",
    "d": "right",
    "w": "up",
    "s": "down",
    "left": "left",
    "right": "right",
    "up": "up",
    "down": "down",
}

# Colors from the original 2048 visual style.
TILE_COLORS = {
    0: "#cdc1b4",
    2: "#eee4da",
    4: "#ede0c8",
    8: "#f2b179",
    16: "#f59563",
    32: "#f67c5f",
    64: "#f65e3b",
    128: "#edcf72",
    256: "#edcc61",
    512: "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
}

TEXT_COLORS = {
    "dark": "#776e65",
    "light": "#f9f6f2",
}


@dataclass
class GameRecorder:
    path: Path
    data: dict[str, Any]

    def append_step(self, move: int | str, board: list[int], score: int) -> None:
        self.data["steps"].append(
            {
                "move": normalize_move(move),
                "board": list(board),
                "score": int(score),
            }
        )

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)


# -------------------- Recording API --------------------
def start_game_record(path: str | Path, initial_board: list[int], initial_score: int = 0) -> GameRecorder:
    recorder = GameRecorder(
        path=Path(path),
        data={
            "version": 1,
            "initial_board": list(initial_board),
            "initial_score": int(initial_score),
            "steps": [],
        },
    )
    recorder.save()
    return recorder


def record_game_step(recorder: GameRecorder, move: int | str, board_after_spawn: list[int], score: int) -> None:
    recorder.append_step(move, list(board_after_spawn), int(score))
    recorder.save()


def finish_game_record(recorder: GameRecorder) -> None:
    recorder.save()


# -------------------- Replay GUI --------------------
def replay_recording(path: str | Path, anim_ms: int = 150, pause_ms: int = 80, size: int = 520) -> None:
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)

    initial_board = data["initial_board"]
    initial_score = int(data.get("initial_score", 0))
    steps = data.get("steps", [])

    root = tk.Tk()
    root.title("2048 Replay")
    root.configure(bg="#faf8ef")

    board_px = int(size)
    pad = 12
    gap = 12
    tile_px = (board_px - pad * 2 - gap * 3) / 4

    score_var = tk.StringVar(value=f"Score: {initial_score}")
    score_label = tk.Label(
        root,
        textvariable=score_var,
        font=("Verdana", 20, "bold"),
        bg="#faf8ef",
        fg="#776e65",
    )
    score_label.pack(pady=(16, 8))

    canvas = tk.Canvas(root, width=board_px, height=board_px, bg="#bbada0", highlightthickness=0)
    canvas.pack(padx=16, pady=(0, 16))

    def cell_xy(idx: int) -> tuple[float, float]:
        r = idx // 4
        c = idx % 4
        x = pad + c * (tile_px + gap)
        y = pad + r * (tile_px + gap)
        return x, y

    def tile_style(value: int) -> tuple[str, str]:
        bg = TILE_COLORS.get(value, "#3c3a32")
        fg = TEXT_COLORS["dark"] if value <= 4 else TEXT_COLORS["light"]
        return bg, fg

    def draw_static_grid() -> None:
        for idx in range(16):
            x, y = cell_xy(idx)
            canvas.create_rectangle(x, y, x + tile_px, y + tile_px, fill="#cdc1b4", width=0)

    def draw_board_state(board: list[int], spawn_idx: int | None = None, spawn_scale: float = 1.0) -> None:
        canvas.delete("all")
        draw_static_grid()
        for idx, value in enumerate(board):
            if value == 0:
                continue
            x, y = cell_xy(idx)
            w = tile_px
            h = tile_px
            if idx == spawn_idx:
                shrink_w = w * (1.0 - spawn_scale) / 2.0
                shrink_h = h * (1.0 - spawn_scale) / 2.0
                x += shrink_w
                y += shrink_h
                w *= spawn_scale
                h *= spawn_scale
            bg, fg = tile_style(value)
            canvas.create_rectangle(x, y, x + w, y + h, fill=bg, width=0)
            font_size = 34 if value < 100 else 30 if value < 1000 else 24
            canvas.create_text(
                x + w / 2,
                y + h / 2,
                text=str(value),
                font=("Verdana", font_size, "bold"),
                fill=fg,
            )

    def line_indices(move_name: str, line: int) -> list[int]:
        if move_name == "left":
            return [line * 4 + c for c in range(4)]
        if move_name == "right":
            return [line * 4 + c for c in range(3, -1, -1)]
        if move_name == "up":
            return [line + 4 * r for r in range(4)]
        return [line + 4 * r for r in range(3, -1, -1)]

    def transitions_for_line(values: list[int]) -> tuple[list[tuple[int, int, int]], list[int]]:
        # Returns (source_pos, target_pos, tile_value_before_move) and final values.
        non_zero = [(i, v) for i, v in enumerate(values) if v != 0]
        moves: list[tuple[int, int, int]] = []
        out = [0, 0, 0, 0]

        i = 0
        target = 0
        while i < len(non_zero):
            src_i, val = non_zero[i]
            if i + 1 < len(non_zero) and non_zero[i + 1][1] == val:
                src_j, _ = non_zero[i + 1]
                moves.append((src_i, target, val))
                moves.append((src_j, target, val))
                out[target] = val * 2
                i += 2
            else:
                moves.append((src_i, target, val))
                out[target] = val
                i += 1
            target += 1

        return moves, out

    def simulate_move_and_transitions(board: list[int], move_name: str) -> tuple[list[int], list[tuple[int, int, int]]]:
        transitions: list[tuple[int, int, int]] = []
        result = board.copy()

        for line in range(4):
            idxs = line_indices(move_name, line)
            vals = [board[i] for i in idxs]
            line_moves, out = transitions_for_line(vals)
            for src_pos, dst_pos, val in line_moves:
                transitions.append((idxs[src_pos], idxs[dst_pos], val))
            for pos, board_idx in enumerate(idxs):
                result[board_idx] = out[pos]

        return result, transitions

    def spawn_index(before_spawn: list[int], after_spawn: list[int]) -> int | None:
        for i in range(16):
            if before_spawn[i] == 0 and after_spawn[i] in (2, 4):
                return i
        return None

    draw_board_state(initial_board)

    def run_replay(step_index: int, current_board: list[int], current_score: int) -> None:
        if step_index >= len(steps):
            score_var.set(f"Score: {current_score} (Replay complete)")
            return

        step = steps[step_index]
        move_name = normalize_move(step["move"])
        next_board = list(step["board"])
        next_score = int(step.get("score", current_score))

        shifted, movements = simulate_move_and_transitions(current_board, move_name)
        tile_items = []

        canvas.delete("all")
        draw_static_grid()

        # Draw moving tiles using pre-move tile values.
        for src_idx, _, value in movements:
            x, y = cell_xy(src_idx)
            bg, fg = tile_style(value)
            rect = canvas.create_rectangle(x, y, x + tile_px, y + tile_px, fill=bg, width=0)
            font_size = 34 if value < 100 else 30 if value < 1000 else 24
            text = canvas.create_text(
                x + tile_px / 2,
                y + tile_px / 2,
                text=str(value),
                font=("Verdana", font_size, "bold"),
                fill=fg,
            )
            tile_items.append((rect, text))

        frames = max(6, anim_ms // 16)

        def animate_frame(frame: int) -> None:
            t = frame / frames
            eased = 1 - (1 - t) * (1 - t)

            for i, (src_idx, dst_idx, _) in enumerate(movements):
                x0, y0 = cell_xy(src_idx)
                x1, y1 = cell_xy(dst_idx)
                x = x0 + (x1 - x0) * eased
                y = y0 + (y1 - y0) * eased

                rect, text = tile_items[i]
                canvas.coords(rect, x, y, x + tile_px, y + tile_px)
                canvas.coords(text, x + tile_px / 2, y + tile_px / 2)

            if frame < frames:
                root.after(max(1, anim_ms // frames), lambda: animate_frame(frame + 1))
            else:
                # Snap to board after movement (before spawn), then show spawn pop.
                s_idx = spawn_index(shifted, next_board)
                if s_idx is None:
                    draw_board_state(next_board)
                    score_var.set(f"Score: {next_score}")
                    root.after(pause_ms, lambda: run_replay(step_index + 1, next_board, next_score))
                    return

                pop_frames = 5

                def animate_spawn_pop(pop_frame: int) -> None:
                    scale = 0.65 + 0.35 * (pop_frame / pop_frames)
                    draw_board_state(next_board, spawn_idx=s_idx, spawn_scale=scale)
                    if pop_frame < pop_frames:
                        root.after(16, lambda: animate_spawn_pop(pop_frame + 1))
                    else:
                        score_var.set(f"Score: {next_score}")
                        root.after(pause_ms, lambda: run_replay(step_index + 1, next_board, next_score))

                animate_spawn_pop(0)

        animate_frame(0)

    root.after(100, lambda: run_replay(0, list(initial_board), initial_score))
    root.mainloop()


def normalize_move(move: int | str) -> str:
    if move in MOVE_CODE_TO_NAME:
        return MOVE_CODE_TO_NAME[move]

    if isinstance(move, str):
        lowered = move.strip().lower()
        if lowered in MOVE_CODE_TO_NAME:
            return MOVE_CODE_TO_NAME[lowered]

    raise ValueError(f"Unsupported move representation: {move!r}")
