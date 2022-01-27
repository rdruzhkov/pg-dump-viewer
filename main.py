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
        self.__filter_string = None
        self.__selected_table_name = None
        self.__selected_table_namespace = None

        self.__root = tkinter.Tk()
        self.__root.minsize(900, 520)
        self.__root.title('Postgres Dump Viewer')
        self.__root.option_add('*tearOff', FALSE)
        self.__root.columnconfigure(3, weight=1)
        self.__root.rowconfigure(1, weight=1)

        self.__tables_list_box = Listbox(self.__root)
        self.__tables_list_box.grid(column=0, row=0, rowspan=2, padx=PADDING_X, pady=PADDING_Y, sticky="nsew")
        self.__tables_list_box.bind(
            '<<ListboxSelect>>',
            lambda evt: self.__list_box_select_handler(evt)
        )

        self.__tree_view = ttk.Treeview(
            self.__root,
            show='headings',
            height=25
        )
        self.__tree_view.grid(column=1, row=1, columnspan=3, padx=PADDING_X, pady=PADDING_Y, sticky="nsew")

        self.__reset_filter_button = Button(
            self.__root,
            text='Reset filter',
            command=lambda: self.__button_reset_filter_handler()
        )
        self.__reset_filter_button.grid(column=1, row=0)
        self.__apply_filter_button = Button(
            self.__root,
            text='Apply filter',
            command=lambda: self.__button_apply_filter_handler()
        )
        self.__apply_filter_button.grid(column=2, row=0)

        self.__filter_entry = Entry(self.__root)
        self.__filter_entry.grid(column=3, row=0, sticky="nsew")

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

        self.__selected_table_name = self.__tables[index]['name']
        self.__selected_table_namespace = self.__tables[index]['namespace']
        self.__update_tree_view()

    def __button_open_dump_file_handler(self):
        logging.debug('__button_open_dump_file_handler was called')

        self.__dump_file_name = filedialog.askopenfilename()

        logging.debug(f'\tFile name = {self.__dump_file_name}')

        self.__dump = Dump(self.__dump_file_name)
        self.__tables = self.__dump.get_tables()

        self.__update_tables_list_box()

        self.__clear_tree_view()

    def __button_apply_filter_handler(self):
        self.__filter_string = self.__filter_entry.get()
        if self.__selected_table_name is not None:
            self.__update_tree_view()

    def __button_reset_filter_handler(self):
        self.__filter_string = None
        if self.__selected_table_name is not None:
            self.__update_tree_view()

    def __remove_tree_view(self):
        if self.__tree_view is not None:
            self.__tree_view.destroy()
            self.__tree_view = None

        else:
            logging.error('__remove_tree_view was called when tree view is None')

    def __clear_tree_view(self):
        self.__tree_view.destroy()
        self.__tree_view = ttk.Treeview(
            self.__root,
            show='headings',
            height=25
        )
        self.__tree_view.grid(column=1, row=1, columnspan=3, padx=PADDING_X, pady=PADDING_Y, sticky="nsew")

    def __update_tree_view(self):
        self.__clear_tree_view()

        for table in self.__tables:
            if table['name'] == self.__selected_table_name and table['namespace'] == self.__selected_table_namespace:
                self.__tree_view = ttk.Treeview(
                    self.__root,
                    columns=[column['name'] for column in table['columns']],
                    show='headings',
                    height=25
                )
                self.__tree_view.grid(column=1, row=1, columnspan=3, padx=PADDING_X, pady=PADDING_Y, sticky="nsew")

                for column in table['columns']:
                    self.__tree_view.heading(column['name'], text=column['name'] + ' : ' + column['data_type'])

                table_data = self.__dump.get_table_data(self.__selected_table_name, self.__selected_table_namespace)
                for row_data in table_data:
                    if self.__filter_string is not None:
                        for value in row_data:
                            if self.__filter_string in value:
                                self.__tree_view.insert('', tkinter.END, values=row_data)
                                break

                    else:
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
