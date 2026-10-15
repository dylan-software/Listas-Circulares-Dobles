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
    the dial number that follows it (next) and the one that precedes it
    (previous)."""

    def __init__(self, value):
        self.value = value
        self.next = None
        self.previous = None


class SafeDial:
    """Circular doubly linked list of dial numbers.

    The indicator always points to the dial number that is currently
    aligned with the safe's fixed marker. Turning clockwise moves the
    indicator to the next dial number; turning counterclockwise moves it
    to the previous one. Because the list is circular, turning past the
    last number lands on the first one, and the other way around.
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


WINDOW_BACKGROUND = "#1C1F22"
DOOR_PANEL = "#30363B"
TEXT_COLOR = "#E6E8EA"
MUTED = "#8A9298"
GOLD = "#C9A24B"
SUCCESS = "#3DDC84"
WARNING = "#E07856"
LED_OFF = "#3A2A2A"
LED_ERROR = "#FF5A4A"
BUTTON_COLOR = "#2F3438"
BUTTON_ACTIVE = "#3B4249"


class SafeDialInterface:
    """Graphical interface for the SafeDial circular doubly linked list.

    The black dial face turns underneath a fixed red marker, like a real
    safe. Numbers grow counterclockwise on the face, so turning the knob
    clockwise always brings the next number under the marker.

    Controls:
      - Keyboard: Left / Right arrows turn the dial one step,
        Shift + Left / Right turn it five steps, Enter confirms the number.
      - Mouse: grab the knob and turn it, use the mouse wheel, or use
        the buttons.
    """

    CANVAS_WIDTH = 450
    CANVAS_HEIGHT = 490
    CENTER_X = 225
    CENTER_Y = 225
    PLATE_RADIUS = 214

    def __init__(self, root):
        self.dial = SafeDial()
        self.drag_angle = None
        self.drag_remainder = 0.0

        self.root = root
        self.root.title("Safe Dial")
        self.root.configure(bg=WINDOW_BACKGROUND)
        self.root.resizable(False, False)

        title_label = tk.Label(
            root, text="SAFE DIAL", font=("Georgia", 18, "bold"),
            bg=WINDOW_BACKGROUND, fg=TEXT_COLOR,
        )
        title_label.pack(pady=(14, 0))

        subtitle_label = tk.Label(
            root, text="Circular doubly linked list — turn it either way, it never ends",
            font=("Segoe UI", 9), bg=WINDOW_BACKGROUND, fg=MUTED,
        )
        subtitle_label.pack(pady=(0, 10))

        self.canvas = tk.Canvas(
            root, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT,
            bg=DOOR_PANEL, highlightthickness=0, cursor="hand2",
        )
        self.canvas.pack(padx=10)
        self.draw_door()
        self.draw_knob()
        self.draw_marker()
        self.draw_leds()

        self.direction_label = tk.Label(
            root, text="", font=("Segoe UI", 10), bg=WINDOW_BACKGROUND, fg=MUTED,
        )
        self.direction_label.pack(pady=(10, 0))

        self.status_label = tk.Label(
            root, text="Turn the dial and press Confirm on each number.",
            font=("Segoe UI", 10, "bold"), bg=WINDOW_BACKGROUND, fg=MUTED,
        )
        self.status_label.pack(pady=(2, 10))

        turn_frame = tk.Frame(root, bg=WINDOW_BACKGROUND)
        turn_frame.pack(padx=24, fill="x")

        left_button = tk.Button(
            turn_frame, text="← Turn left", font=("Segoe UI", 10),
            bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_ACTIVE,
            activeforeground=TEXT_COLOR, relief="flat", pady=6, takefocus=0,
            command=lambda: self.turn(COUNTERCLOCKWISE, 1),
        )
        left_button.pack(side="left", fill="x", expand=True)

        right_button = tk.Button(
            turn_frame, text="Turn right →", font=("Segoe UI", 10),
            bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_ACTIVE,
            activeforeground=TEXT_COLOR, relief="flat", pady=6, takefocus=0,
            command=lambda: self.turn(CLOCKWISE, 1),
        )
        right_button.pack(side="left", fill="x", expand=True, padx=(8, 0))

        action_frame = tk.Frame(root, bg=WINDOW_BACKGROUND)
        action_frame.pack(padx=24, pady=(8, 0), fill="x")

        confirm_button = tk.Button(
            action_frame, text="Confirm number (Enter)", font=("Segoe UI", 10, "bold"),
            bg=GOLD, fg="#1C1F22", activebackground="#D9B45E",
            activeforeground="#1C1F22", relief="flat", pady=7, takefocus=0,
            command=self.confirm,
        )
        confirm_button.pack(side="left", fill="x", expand=True)

        reset_button = tk.Button(
            action_frame, text="Reset", font=("Segoe UI", 10),
            bg="#A85C2E", fg="white", activebackground="#BC6B38",
            activeforeground="white", relief="flat", padx=16, pady=7, takefocus=0,
            command=self.reset,
        )
        reset_button.pack(side="left", padx=(8, 0))

        self.hint_visible = tk.BooleanVar(value=False)
        hint_check = tk.Checkbutton(
            root, text="Show combination", variable=self.hint_visible,
            command=self.update_hint, bg=WINDOW_BACKGROUND, fg=MUTED,
            activebackground=WINDOW_BACKGROUND, activeforeground=TEXT_COLOR,
            selectcolor=BUTTON_COLOR, font=("Segoe UI", 9), takefocus=0,
        )
        hint_check.pack(pady=(10, 0))

        self.hint_label = tk.Label(
            root, text="", font=("Segoe UI", 9), bg=WINDOW_BACKGROUND, fg=MUTED,
            wraplength=400, justify="center",
        )
        self.hint_label.pack()

        help_label = tk.Label(
            root,
            text="Keys: ← → turn 1  ·  Shift + ← → turn 5  ·  Enter confirm\n"
                 "Mouse: grab the knob and turn it, or use the wheel",
            font=("Segoe UI", 9), bg=WINDOW_BACKGROUND, fg=MUTED, justify="center",
        )
        help_label.pack(pady=(8, 16))

        self.bind_controls()
        self.root.focus_set()
        self.refresh()

    def polar_point(self, radius, angle):
        """Point at a distance from the dial center. The angle goes
        clockwise from the top of the dial, in radians."""
        return (
            self.CENTER_X + radius * math.sin(angle),
            self.CENTER_Y - radius * math.cos(angle),
        )

    def draw_circle(self, radius, fill, tags=()):
        return self.canvas.create_oval(
            self.CENTER_X - radius, self.CENTER_Y - radius,
            self.CENTER_X + radius, self.CENTER_Y + radius,
            fill=fill, outline="", tags=tags,
        )

    def draw_door(self):
        # Four screws holding the steel plate to the safe door.
        for screw_x in (22, self.CANVAS_WIDTH - 22):
            for screw_y in (22, self.CANVAS_HEIGHT - 22):
                self.canvas.create_oval(
                    screw_x - 9, screw_y - 9, screw_x + 9, screw_y + 9,
                    fill="#5C646A", outline="#1F2326", width=2,
                )
                self.canvas.create_line(
                    screw_x - 5, screw_y - 4, screw_x + 5, screw_y + 4,
                    fill="#1F2326", width=2,
                )

        # Beveled steel rings around the dial face.
        self.draw_circle(self.PLATE_RADIUS, "#22262A")
        self.draw_circle(210, "#6E767C")
        self.draw_circle(204, "#A9B1B7")
        self.draw_circle(198, "#838B91")
        self.glow_ring = self.draw_circle(192, "#4C5359")

        # Black dial face. The numbers and ticks are drawn on top of it.
        self.draw_circle(186, "#101214")

    def draw_knob(self):
        # Knob built from concentric rings to look like brushed metal.
        self.draw_circle(100, "#22262A", tags="knob_static")
        self.draw_circle(96, "#D3D8DC", tags="knob_static")
        self.draw_circle(92, "#8F979D", tags="knob_static")
        self.draw_circle(80, "#B7BEC4", tags="knob_static")
        self.draw_circle(70, "#868E95", tags="knob_static")
        self.draw_circle(44, "#2A2F33", tags="knob_static")
        self.draw_circle(40, "#15181A", tags="knob_static")

        self.readout_item = self.canvas.create_text(
            self.CENTER_X, self.CENTER_Y, text="00",
            font=("Consolas", 22, "bold"), fill=GOLD,
        )

    def draw_marker(self):
        # Fixed red marker above the dial: the number under it is the
        # one the safe reads.
        tip_x, tip_y = self.polar_point(190, 0)
        self.canvas.create_polygon(
            tip_x, tip_y, tip_x - 11, tip_y - 22, tip_x + 11, tip_y - 22,
            fill="#D64533", outline="#F2F2F2", width=2,
        )

    def draw_leds(self):
        led_count = len(self.dial.combination)
        for led_index in range(led_count):
            led_x = self.CENTER_X + (led_index - (led_count - 1) / 2) * 38
            led_y = self.CANVAS_HEIGHT - 24
            self.canvas.create_oval(
                led_x - 8, led_y - 8, led_x + 8, led_y + 8,
                fill=LED_OFF, outline="#5A4646", width=2, tags=f"led_{led_index}",
            )

    def draw_marks(self):
        """Redraw the turning parts: the ticks and numbers of the dial face
        and the notches of the knob. The face is drawn by walking the
        circular list from the indicator, so the number under the marker
        is always the indicator and the following numbers (next) are laid
        out counterclockwise."""
        self.canvas.delete("face_marks")
        self.canvas.delete("knob_marks")
        step_angle = 2 * math.pi / self.dial.size

        dial_number = self.dial.indicator
        for offset in range(self.dial.size):
            angle = -offset * step_angle
            is_major = dial_number.value % 5 == 0

            tick_start_x, tick_start_y = self.polar_point(180, angle)
            tick_end_x, tick_end_y = self.polar_point(164 if is_major else 172, angle)
            self.canvas.create_line(
                tick_start_x, tick_start_y, tick_end_x, tick_end_y,
                fill="#ECE9E1" if is_major else "#9A9A94",
                width=2 if is_major else 1, tags="face_marks",
            )

            if is_major:
                label_x, label_y = self.polar_point(146, angle)
                self.canvas.create_text(
                    label_x, label_y, text=str(dial_number.value),
                    font=("Segoe UI", 10, "bold"),
                    fill=GOLD if dial_number.value == 0 else "#ECE9E1",
                    tags="face_marks",
                )
            dial_number = dial_number.next

        # Knurled edge and grip line of the knob: they turn with the dial.
        knob_angle = self.dial.indicator.value * step_angle
        notch_count = 48
        for notch in range(notch_count):
            angle = knob_angle + notch * 2 * math.pi / notch_count
            start_x, start_y = self.polar_point(84, angle)
            end_x, end_y = self.polar_point(93, angle)
            self.canvas.create_line(
                start_x, start_y, end_x, end_y,
                fill="#4A5157", width=2, tags="knob_marks",
            )
        grip_start_x, grip_start_y = self.polar_point(50, knob_angle)
        grip_end_x, grip_end_y = self.polar_point(68, knob_angle)
        self.canvas.create_line(
            grip_start_x, grip_start_y, grip_end_x, grip_end_y,
            fill=GOLD, width=4, capstyle=tk.ROUND, tags="knob_marks",
        )

        # Keep the layers in order: face marks go under the knob.
        self.canvas.tag_lower("face_marks", "knob_static")

    def bind_controls(self):
        self.root.bind("<Right>", lambda event: self.turn(CLOCKWISE, 1))
        self.root.bind("<Left>", lambda event: self.turn(COUNTERCLOCKWISE, 1))
        self.root.bind("<Shift-Right>", lambda event: self.turn(CLOCKWISE, 5))
        self.root.bind("<Shift-Left>", lambda event: self.turn(COUNTERCLOCKWISE, 5))
        self.root.bind("<Return>", lambda event: self.confirm())
        self.root.bind("<KP_Enter>", lambda event: self.confirm())

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)

    def angle_from_mouse(self, event):
        """Angle of the mouse around the dial center, in degrees going
        clockwise from the top. None if the mouse is too close to the
        center to give a stable angle."""
        delta_x = event.x - self.CENTER_X
        delta_y = event.y - self.CENTER_Y
        if math.hypot(delta_x, delta_y) < 20:
            return None
        return math.degrees(math.atan2(delta_x, -delta_y)) % 360

    def on_mouse_press(self, event):
        self.drag_angle = self.angle_from_mouse(event)
        self.drag_remainder = 0.0

    def on_mouse_drag(self, event):
        if self.dial.unlocked or self.drag_angle is None:
            return
        angle = self.angle_from_mouse(event)
        if angle is None:
            return

        # Turn the dial by as many steps as the mouse moved around the
        # center, keeping the leftover fraction for the next movement.
        moved = (angle - self.drag_angle + 180) % 360 - 180
        self.drag_angle = angle
        self.drag_remainder += moved

        step_degrees = 360 / self.dial.size
        steps = int(self.drag_remainder / step_degrees)
        if steps > 0:
            self.dial.rotate_clockwise(steps)
        elif steps < 0:
            self.dial.rotate_counterclockwise(-steps)
        self.drag_remainder -= steps * step_degrees
        if steps != 0:
            self.refresh()

    def on_mouse_release(self, event):
        self.drag_angle = None
        self.drag_remainder = 0.0

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
            self.set_status("Click! The safe is open.", SUCCESS)
        elif result == "correct":
            self.set_status("Click! Number accepted. Keep going.", SUCCESS)
        else:
            self.set_status("Wrong number or direction. The lock reset.", WARNING)
        self.refresh()
        if result == "wrong":
            self.update_leds(show_error=True)
            self.root.after(450, self.update_leds)

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

    def update_leds(self, show_error=False):
        for led_index in range(len(self.dial.combination)):
            if show_error:
                color = LED_ERROR
            elif self.dial.unlocked or led_index < self.dial.current_step:
                color = SUCCESS
            else:
                color = LED_OFF
            self.canvas.itemconfig(f"led_{led_index}", fill=color)

    def refresh(self):
        self.draw_marks()
        value = self.dial.indicator.value
        self.canvas.itemconfig(self.readout_item, text=f"{value:02d}")

        if self.dial.last_direction is None:
            self.direction_label.config(text="Last turn: none")
        else:
            self.direction_label.config(text=f"Last turn: {self.dial.last_direction}")

        self.update_leds()
        self.canvas.itemconfig(
            self.glow_ring, fill=SUCCESS if self.dial.unlocked else "#4C5359",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SafeDialInterface(root)
    root.mainloop()