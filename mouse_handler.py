from pynput.mouse import Listener
import win32gui
import win32process
import psutil


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
        print(self.button, self.pressed)
        self.process_name = self.active_window_process_name()
        print(self.process_name)

    def on_scroll(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def stop(self):
        self.listener.stop()
