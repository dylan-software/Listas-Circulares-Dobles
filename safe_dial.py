"""
Workshop: Circular Doubly Linked Lists applied to a case study
Case: safe dial. The dial numbers (0-99) form a circle: every dial number
knows the one after it (next) and the one before it (previous), and the
last one connects back to the first one. The user turns the dial with the
keyboard arrows or the mouse and must enter the secret combination,
respecting the turning direction of every step.
"""

import math
import tkinter as tk

CLOCKWISE = "clockwise"
COUNTERCLOCKWISE = "counterclockwise"

DEFAULT_COMBINATION = (
    (CLOCKWISE, 25),
    (COUNTERCLOCKWISE, 70),
    (CLOCKWISE, 42),
)


class DialNumber:
    """One number printed on the dial. Stores its value and a reference to
    the dial number on its right (next) and on its left (previous)."""

    def __init__(self, value):
        self.value = value
        self.next = None
        self.previous = None


class SafeDial:
    """Circular doubly linked list of dial numbers.

    The indicator always points to the dial number that is currently
    aligned with the safe's marker. Turning clockwise moves the indicator
    to the next dial number; turning counterclockwise moves it to the
    previous one. Because the list is circular, turning past the last
    number lands on the first one, and the other way around.
    """

    def __init__(self, total_numbers=100, combination=DEFAULT_COMBINATION):
        self.first_number = None
        self.last_number = None
        self.indicator = None
        self.size = 0
        self.last_direction = None
        self.combination = combination
        self.current_step = 0
        self.unlocked = False

        for value in range(total_numbers):
            self.add_number(value)
        self.indicator = self.first_number

    def add_number(self, value):
        new_number = DialNumber(value)
        if self.first_number is None:
            self.first_number = new_number
            self.last_number = new_number
            new_number.next = new_number
            new_number.previous = new_number
        else:
            new_number.previous = self.last_number
            new_number.next = self.first_number
            self.last_number.next = new_number
            self.first_number.previous = new_number
            self.last_number = new_number
        self.size += 1

    def rotate_clockwise(self, steps=1):
        for _ in range(steps):
            self.indicator = self.indicator.next
        if steps > 0:
            self.last_direction = CLOCKWISE

    def rotate_counterclockwise(self, steps=1):
        for _ in range(steps):
            self.indicator = self.indicator.previous
        if steps > 0:
            self.last_direction = COUNTERCLOCKWISE

    def rotate_to(self, target_value):
        """Move the indicator to a value using the shortest way around the
        circle. Values must go from 0 to size - 1."""
        clockwise_distance = (target_value - self.indicator.value) % self.size
        counterclockwise_distance = self.size - clockwise_distance
        if clockwise_distance == 0:
            return
        if clockwise_distance <= counterclockwise_distance:
            self.rotate_clockwise(clockwise_distance)
        else:
            self.rotate_counterclockwise(counterclockwise_distance)

    def confirm_number(self):
        """Lock in the number under the indicator for the current step.
        Returns "unlocked", "correct" or "wrong"."""
        if self.unlocked:
            return "unlocked"
        expected_direction, expected_value = self.combination[self.current_step]
        if (self.last_direction == expected_direction
                and self.indicator.value == expected_value):
            self.current_step += 1
            if self.current_step == len(self.combination):
                self.unlocked = True
                return "unlocked"
            return "correct"
        self.reset_attempt()
        return "wrong"

    def reset_attempt(self):
        self.current_step = 0
        self.last_direction = None

    def lock_again(self):
        self.unlocked = False
        self.reset_attempt()


BACKGROUND = "#F4F6F5"
INK = "#1C2624"
MUTED = "#5B6660"
ACCENT = "#2F6F5E"
WARNING = "#A85C2E"


class SafeDialInterface:
    """Graphical interface for the SafeDial circular doubly linked list.

    Controls:
      - Keyboard: Left / Right arrows turn the dial one step,
        Shift + Left / Right turn it five steps, Enter confirms the number.
      - Mouse: drag over the dial, use the mouse wheel, or use the buttons.
    """

    CANVAS_SIZE = 400
    CENTER = 200
    RING_RADIUS = 170
    POINTER_LENGTH = 118

    def __init__(self, root):
        self.dial = SafeDial()

        self.root = root
        self.root.title("Safe Dial")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)

        title_label = tk.Label(
            root, text="Safe Dial", font=("Segoe UI", 18, "bold"),
            bg=BACKGROUND, fg=INK,
        )
        title_label.pack(pady=(16, 2))

        subtitle_label = tk.Label(
            root, text="Circular doubly linked list — turn it either way, it never ends",
            font=("Segoe UI", 9), bg=BACKGROUND, fg=MUTED,
        )
        subtitle_label.pack(pady=(0, 8))

        self.canvas = tk.Canvas(
            root, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE,
            bg=BACKGROUND, highlightthickness=0,
        )
        self.canvas.pack()
        self.draw_dial()

        self.value_label = tk.Label(
            root, text="00", font=("Consolas", 30, "bold"), bg=BACKGROUND, fg=INK,
        )
        self.value_label.pack(pady=(4, 0))

        self.direction_label = tk.Label(
            root, text="", font=("Segoe UI", 10), bg=BACKGROUND, fg=MUTED,
        )
        self.direction_label.pack()

        self.progress_label = tk.Label(
            root, text="", font=("Segoe UI", 14), bg=BACKGROUND, fg=ACCENT,
        )
        self.progress_label.pack(pady=(4, 0))

        self.status_label = tk.Label(
            root, text="Turn the dial and press Confirm on each number.",
            font=("Segoe UI", 10, "bold"), bg=BACKGROUND, fg=MUTED,
        )
        self.status_label.pack(pady=(2, 8))

        turn_frame = tk.Frame(root, bg=BACKGROUND)
        turn_frame.pack(padx=20, fill="x")

        left_button = tk.Button(
            turn_frame, text="← Turn left", font=("Segoe UI", 10),
            bg="#FFFFFF", fg=INK, relief="solid", borderwidth=1, pady=5,
            takefocus=0, command=lambda: self.turn(COUNTERCLOCKWISE, 1),
        )
        left_button.pack(side="left", fill="x", expand=True)

        right_button = tk.Button(
            turn_frame, text="Turn right →", font=("Segoe UI", 10),
            bg="#FFFFFF", fg=INK, relief="solid", borderwidth=1, pady=5,
            takefocus=0, command=lambda: self.turn(CLOCKWISE, 1),
        )
        right_button.pack(side="left", fill="x", expand=True, padx=(8, 0))

        action_frame = tk.Frame(root, bg=BACKGROUND)
        action_frame.pack(padx=20, pady=(8, 0), fill="x")

        confirm_button = tk.Button(
            action_frame, text="Confirm number (Enter)", font=("Segoe UI", 10, "bold"),
            bg=ACCENT, fg="white", relief="flat", pady=6,
            takefocus=0, command=self.confirm,
        )
        confirm_button.pack(side="left", fill="x", expand=True)

        reset_button = tk.Button(
            action_frame, text="Reset", font=("Segoe UI", 10),
            bg=WARNING, fg="white", relief="flat", padx=14, pady=6,
            takefocus=0, command=self.reset,
        )
        reset_button.pack(side="left", padx=(8, 0))

        self.hint_visible = tk.BooleanVar(value=False)
        hint_check = tk.Checkbutton(
            root, text="Show combination", variable=self.hint_visible,
            command=self.update_hint, bg=BACKGROUND, fg=MUTED,
            activebackground=BACKGROUND, font=("Segoe UI", 9), takefocus=0,
        )
        hint_check.pack(pady=(10, 0))

        self.hint_label = tk.Label(
            root, text="", font=("Segoe UI", 9), bg=BACKGROUND, fg=MUTED,
            wraplength=370, justify="center",
        )
        self.hint_label.pack()

        help_label = tk.Label(
            root,
            text="Keys: ← → turn 1  ·  Shift + ← → turn 5  ·  Enter confirm\n"
                 "Mouse: drag over the dial or use the wheel",
            font=("Segoe UI", 9), bg=BACKGROUND, fg=MUTED, justify="center",
        )
        help_label.pack(pady=(8, 16))

        self.bind_controls()
        self.root.focus_set()
        self.refresh()

    def draw_dial(self):
        center = self.CENTER
        radius = self.RING_RADIUS

        self.dial_outline = self.canvas.create_oval(
            center - radius - 12, center - radius - 12,
            center + radius + 12, center + radius + 12,
            outline=INK, width=3, fill="#FFFFFF",
        )

        # Walk the whole circle once, from the first dial number to the
        # last one, drawing a tick (and a label every ten numbers) for each.
        dial_number = self.dial.first_number
        for _ in range(self.dial.size):
            angle = dial_number.value * 2 * math.pi / self.dial.size
            is_major = dial_number.value % 5 == 0
            inner_radius = radius - (22 if is_major else 12)
            self.canvas.create_line(
                center + radius * math.sin(angle), center - radius * math.cos(angle),
                center + inner_radius * math.sin(angle), center - inner_radius * math.cos(angle),
                fill=INK if is_major else MUTED, width=2 if is_major else 1,
            )
            if dial_number.value % 10 == 0:
                label_radius = radius - 38
                self.canvas.create_text(
                    center + label_radius * math.sin(angle),
                    center - label_radius * math.cos(angle),
                    text=str(dial_number.value), font=("Segoe UI", 10, "bold"), fill=INK,
                )
            dial_number = dial_number.next

        self.pointer_line = self.canvas.create_line(
            center, center, center, center - self.POINTER_LENGTH,
            width=5, fill=ACCENT, capstyle=tk.ROUND,
        )
        self.knob = self.canvas.create_oval(
            center - 16, center - 16, center + 16, center + 16,
            fill=ACCENT, outline="",
        )

    def bind_controls(self):
        self.root.bind("<Right>", lambda event: self.turn(CLOCKWISE, 1))
        self.root.bind("<Left>", lambda event: self.turn(COUNTERCLOCKWISE, 1))
        self.root.bind("<Shift-Right>", lambda event: self.turn(CLOCKWISE, 5))
        self.root.bind("<Shift-Left>", lambda event: self.turn(COUNTERCLOCKWISE, 5))
        self.root.bind("<Return>", lambda event: self.confirm())
        self.root.bind("<KP_Enter>", lambda event: self.confirm())

        self.canvas.bind("<Button-1>", self.on_mouse_drag)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)

    def value_from_mouse(self, event):
        delta_x = event.x - self.CENTER
        delta_y = event.y - self.CENTER
        if math.hypot(delta_x, delta_y) < 25:
            return None
        angle = math.degrees(math.atan2(delta_x, -delta_y)) % 360
        return round(angle / (360 / self.dial.size)) % self.dial.size

    def on_mouse_drag(self, event):
        if self.dial.unlocked:
            return
        target_value = self.value_from_mouse(event)
        if target_value is not None:
            self.dial.rotate_to(target_value)
            self.refresh()

    def on_mouse_wheel(self, event):
        if event.num == 4 or getattr(event, "delta", 0) > 0:
            self.turn(CLOCKWISE, 1)
        elif event.num == 5 or getattr(event, "delta", 0) < 0:
            self.turn(COUNTERCLOCKWISE, 1)

    def turn(self, direction, steps):
        if self.dial.unlocked:
            return
        if direction == CLOCKWISE:
            self.dial.rotate_clockwise(steps)
        else:
            self.dial.rotate_counterclockwise(steps)
        self.refresh()

    def confirm(self):
        result = self.dial.confirm_number()
        if result == "unlocked":
            self.set_status("Click! The safe is open.", ACCENT)
        elif result == "correct":
            self.set_status("Click! Number accepted. Keep going.", ACCENT)
        else:
            self.set_status("Wrong number or direction. The lock reset.", WARNING)
        self.refresh()

    def reset(self):
        self.dial.lock_again()
        self.set_status("Safe locked again. Turn the dial to start over.", MUTED)
        self.refresh()

    def set_status(self, text, color):
        self.status_label.config(text=text, fg=color)

    def update_hint(self):
        if not self.hint_visible.get():
            self.hint_label.config(text="")
            return
        text = ""
        for direction, value in self.dial.combination:
            if text != "":
                text += "  →  "
            text += f"{direction} to {value}"
        self.hint_label.config(text=text)

    def refresh(self):
        value = self.dial.indicator.value
        angle = value * 2 * math.pi / self.dial.size
        end_x = self.CENTER + self.POINTER_LENGTH * math.sin(angle)
        end_y = self.CENTER - self.POINTER_LENGTH * math.cos(angle)
        self.canvas.coords(self.pointer_line, self.CENTER, self.CENTER, end_x, end_y)

        self.value_label.config(text=f"{value:02d}")

        if self.dial.last_direction is None:
            self.direction_label.config(text="Last turn: none")
        else:
            self.direction_label.config(text=f"Last turn: {self.dial.last_direction}")

        progress = ""
        for step_index in range(len(self.dial.combination)):
            progress += "●" if step_index < self.dial.current_step else "○"
            progress += " "
        self.progress_label.config(text=progress.strip())

        if self.dial.unlocked:
            self.canvas.itemconfig(self.dial_outline, outline=ACCENT, width=6)
        else:
            self.canvas.itemconfig(self.dial_outline, outline=INK, width=3)


if __name__ == "__main__":
    root = tk.Tk()
    app = SafeDialInterface(root)
    root.mainloop()