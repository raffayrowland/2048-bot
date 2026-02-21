import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path

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
    initial_board: list[int]
    initial_score: int = 0
    _file: object | None = None
    _has_steps: bool = False
    _closed: bool = False
    _tail: str = "]}\n"

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8")
        self._file.write('{"version":1,"initial_board":')
        self._file.write(json.dumps(list(self.initial_board), separators=(",", ":")))
        self._file.write(f',"initial_score":{int(self.initial_score)},"steps":[')
        self._file.write(self._tail)
        self._file.flush()

    def append_step(self, move: int | str, board: list[int], score: int) -> None:
        if self._closed or self._file is None:
            raise RuntimeError("Cannot append step to a closed recorder.")

        # Overwrite the closing tail, append the new step, then restore the tail.
        self._file.seek(0, 2)
        end = self._file.tell()
        self._file.seek(end - len(self._tail))

        if self._has_steps:
            self._file.write(",")

        self._file.write(
            json.dumps(
                {
                    "move": normalize_move(move),
                    "board": list(board),
                    "score": int(score),
                },
                separators=(",", ":"),
            )
        )
        self._file.write(self._tail)
        self._has_steps = True
        self._file.flush()

    def finish(self) -> None:
        if self._closed or self._file is None:
            return
        self._file.close()
        self._closed = True


# -------------------- Recording API --------------------
def start_game_record(path: str | Path, initial_board: list[int], initial_score: int = 0) -> GameRecorder:
    return GameRecorder(
        path=Path(path),
        initial_board=list(initial_board),
        initial_score=int(initial_score),
    )


def record_game_step(recorder: GameRecorder, move: int | str, board_after_spawn: list[int], score: int) -> None:
    recorder.append_step(move, board_after_spawn, score)


def finish_game_record(recorder: GameRecorder) -> None:
    recorder.finish()


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

    states: list[tuple[list[int], int]] = [(list(initial_board), initial_score)]
    for step in steps:
        prev_score = states[-1][1]
        states.append((list(step["board"]), int(step.get("score", prev_score))))

    current_step = 0  # Index of the board currently shown in `states`.
    paused = False
    animating = False
    queued_after: str | None = None

    def cancel_queued() -> None:
        nonlocal queued_after
        if queued_after is not None:
            root.after_cancel(queued_after)
            queued_after = None

    def set_status_text() -> None:
        score = states[current_step][1]
        if current_step >= len(steps):
            suffix = " (Replay complete)"
        elif paused:
            suffix = " (Paused)"
        else:
            suffix = ""
        score_var.set(f"Score: {score}{suffix}")

    def show_current_board() -> None:
        board, _ = states[current_step]
        draw_board_state(board)
        set_status_text()

    def maybe_schedule_next() -> None:
        nonlocal queued_after
        cancel_queued()
        if paused or animating or current_step >= len(steps):
            return
        queued_after = root.after(pause_ms, lambda: play_step(current_step, keep_paused=False))

    def play_step(step_index: int, keep_paused: bool) -> None:
        nonlocal current_step, animating, paused, queued_after
        if animating or step_index >= len(steps):
            return

        cancel_queued()
        animating = True

        current_board, _ = states[step_index]
        step = steps[step_index]
        move_name = normalize_move(step["move"])
        next_board, _ = states[step_index + 1]

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

        def finalize_step() -> None:
            nonlocal current_step, animating, paused
            current_step = step_index + 1
            animating = False
            if keep_paused:
                paused = True
            show_current_board()
            maybe_schedule_next()

        def animate_frame(frame: int) -> None:
            nonlocal queued_after
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
                queued_after = root.after(max(1, anim_ms // frames), lambda: animate_frame(frame + 1))
                return

            s_idx = spawn_index(shifted, next_board)
            if s_idx is None:
                finalize_step()
                return

            pop_frames = 5

            def animate_spawn_pop(pop_frame: int) -> None:
                nonlocal queued_after
                scale = 0.65 + 0.35 * (pop_frame / pop_frames)
                draw_board_state(next_board, spawn_idx=s_idx, spawn_scale=scale)
                if pop_frame < pop_frames:
                    queued_after = root.after(16, lambda: animate_spawn_pop(pop_frame + 1))
                else:
                    finalize_step()

            animate_spawn_pop(0)

        animate_frame(0)

    def on_key(event: tk.Event) -> None:
        nonlocal paused, current_step
        key = event.keysym

        if key == "space":
            paused = not paused
            set_status_text()
            if not paused:
                maybe_schedule_next()
            return

        if key == "Left":
            if paused and not animating and current_step > 0:
                cancel_queued()
                current_step -= 1
                show_current_board()
            return

        if key == "Right":
            if paused and not animating and current_step < len(steps):
                play_step(current_step, keep_paused=True)

    draw_board_state(initial_board)
    set_status_text()
    root.bind("<KeyPress>", on_key)
    root.after(100, maybe_schedule_next)
    root.mainloop()


def normalize_move(move: int | str) -> str:
    if move in MOVE_CODE_TO_NAME:
        return MOVE_CODE_TO_NAME[move]

    if isinstance(move, str):
        lowered = move.strip().lower()
        if lowered in MOVE_CODE_TO_NAME:
            return MOVE_CODE_TO_NAME[lowered]

    raise ValueError(f"Unsupported move representation: {move!r}")
