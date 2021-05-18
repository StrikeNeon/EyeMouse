from pynput.mouse import Listener
from pynput.mouse import Button, Controller
import win32gui
import win32process
import psutil


class mouse_controller():
    def __init__(self):
        self.mouse = Controller()
        self.x = self.mouse.position[0]
        self.y = self.mouse.position[1]

    def set_cursor(self, x: int, y: int):
        self.x = x
        self.y = y
        self.mouse.position(self.x, self.y)

    def move_cursor(self, x: int, y: int):
        self.mouse.move(x, y)

    def press_button(self, button: int):
        self.mouse.press(Button.left if button == 1 else Button.right)

    def release_button(self, button: int):
        self.mouse.release(Button.left if button == 1 else Button.right)

    def click_button(self, button: int, double: bool):
        self.mouse.click(Button.left if button == 1 else Button.right,
                         2 if double else 1)

    def scroll(self, steps: int):
        self.mouse.scroll(0, steps)


class mouse_listener():

    def __init__(self):
        # Collect events until released
        self.x = None
        self.y = None
        self.dx = None
        self.dy = None
        self.button = None
        self.pressed = None
        self.process_name = self.active_window_process_name()
        self.listener = Listener(on_move=self.on_move,
                                 on_click=self.on_click,
                                 on_scroll=self.on_scroll)
        self.listener.start()

    def active_window_process_name(self):
        try:
            pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
            return(psutil.Process(pid[-1]).name())
        except Exception as ex:
            print(ex)

    def on_move(self, x, y):
        self.x = x
        self.y = y

    def on_click(self, x, y, button, pressed):
        self.x = x
        self.y = y
        self.button = button
        self.pressed = pressed
        self.process_name = self.active_window_process_name()

    def on_scroll(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def stop(self):
        self.listener.stop()
