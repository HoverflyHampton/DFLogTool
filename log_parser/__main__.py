import os
import sys
from kivy.resources import resource_add_path
from log_parser.log_parse_gui import Editor


def main():
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    app = Editor()
    app.run()

if __name__ == '__main__':
    main()
