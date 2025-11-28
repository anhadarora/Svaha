import os
import sys
import time
from subprocess import Popen

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class AppRestartHandler(FileSystemEventHandler):
    def __init__(self, script, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.script = script
        self.process = None
        self.start_process()

    def start_process(self):
        self.process = Popen([sys.executable, self.script])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"Restarting due to: {event.src_path}")
            self.process.terminate()
            self.process.wait()
            self.start_process()


if __name__ == "__main__":
    path = "."
    script_to_run = "main.py"

    event_handler = AppRestartHandler(script_to_run)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print(f"Watching for changes in '{path}' to reload '{script_to_run}'")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
