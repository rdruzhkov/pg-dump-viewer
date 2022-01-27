from tkinter import *
import tkinter as ttk
from tkinter import filedialog
import logging

from dump import Dump

PADDING_X = 3
PADDING_Y = 3


class MainFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.__dump_file_name = None
        self.__dump = None
        self.__tables = None

        self.__tables_list_box = Listbox(self, height=20)
        self.__tables_list_box.grid(column=0, row=1, padx=PADDING_X, pady=PADDING_Y)

    def button_open_dump_file_handler(self):
        logging.debug('__button_open_dump_file_handler was called')

        self.__dump_file_name = filedialog.askopenfilename()

        logging.debug(f'\tFile name = {self.__dump_file_name}')

        self.__dump = Dump(self.__dump_file_name)
        self.__tables = self.__dump.get_tables()

        self.__update_tables_list_box()

    def __update_tables_list_box(self):
        self.__tables_list_box.delete(0, len(self.__tables) - 1)
        for table in self.__tables:
            self.__tables_list_box.insert(0, f"{table['namespace']}:{table['name']}")


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s]: %(message)s',
        level=logging.DEBUG)

    root = ttk.Tk()
    root.title('Postgres Dump Viewer')
    root.option_add('*tearOff', FALSE)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    main_frame = MainFrame(root)
    main_frame.grid(column=0, row=0, sticky='NWES')

    menubar = Menu(root)
    root['menu'] = menubar

    menu_file = Menu(menubar)
    menubar.add_cascade(menu=menu_file, label='Файл')
    menu_file.add_command(label='Открыть', command=main_frame.button_open_dump_file_handler)

    root.mainloop()
