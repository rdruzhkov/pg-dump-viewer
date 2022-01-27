import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import logging

from dump import Dump

PADDING_X = 3
PADDING_Y = 3


class MainWindow:
    def __init__(self):
        self.__dump_file_name = None
        self.__dump = None
        self.__tables = None

        self.__root = tkinter.Tk()
        self.__root.geometry('900x520')
        self.__root.title('Postgres Dump Viewer')
        self.__root.option_add('*tearOff', FALSE)

        self.__tables_list_box = Listbox(self.__root, height=30)
        self.__tables_list_box.grid(column=0, row=0, rowspan=2, padx=PADDING_X, pady=PADDING_Y)
        self.__tables_list_box.bind(
            '<<ListboxSelect>>',
            lambda evt: self.__list_box_select_handler(evt)
        )

        self.__tree_view = None

        menubar = Menu(self.__root)
        self.__root['menu'] = menubar

        menu_file = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='Файл')
        menu_file.add_command(label='Открыть', command=self.__button_open_dump_file_handler)

    def __list_box_select_handler(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        logging.debug(f'Listbox selected value {value}')

        self.__update_tree_view(self.__tables[index]['name'], self.__tables[index]['namespace'])

    def __button_open_dump_file_handler(self):
        logging.debug('__button_open_dump_file_handler was called')

        self.__dump_file_name = filedialog.askopenfilename()

        logging.debug(f'\tFile name = {self.__dump_file_name}')

        self.__dump = Dump(self.__dump_file_name)
        self.__tables = self.__dump.get_tables()

        self.__update_tables_list_box()

        if self.__tree_view is not None:
            self.__remove_tree_view()

    def __remove_tree_view(self):
        if self.__tree_view is not None:
            self.__tree_view.destroy()
            self.__tree_view = None

        else:
            logging.error('__remove_tree_view was called when tree view is None')

    def __update_tree_view(self, selected_table_name: str, selected_table_namespace: str):
        if self.__tree_view is not None:
            self.__remove_tree_view()

        for table in self.__tables:
            if table['name'] == selected_table_name and table['namespace'] == selected_table_namespace:
                self.__tree_view = ttk.Treeview(
                    self.__root,
                    columns=[column['name'] for column in table['columns']],
                    show='headings',
                    height=25
                )
                self.__tree_view.grid(column=1, row=1, columnspan=2, padx=PADDING_X, pady=PADDING_Y)

                for column in table['columns']:
                    self.__tree_view.heading(column['name'], text=column['name'] + ' : ' + column['data_type'])

                table_data = self.__dump.get_table_data(selected_table_name, selected_table_namespace)
                for row_data in table_data:
                    self.__tree_view.insert('', tkinter.END, values=row_data)

                break

        else:
            logging.error('__update_tree_view can\'t find specified table')

    def __update_tables_list_box(self):
        self.__tables_list_box.delete(0, len(self.__tables) - 1)
        for table in self.__tables:
            self.__tables_list_box.insert(0, f"{table['namespace']} : {table['name']}")

    def main_loop(self):
        self.__root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s]: %(message)s',
        level=logging.DEBUG)

    main_windows = MainWindow()
    main_windows.main_loop()
