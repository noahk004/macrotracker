import sqlite3
from tkinter import ttk
import tkinter
from db import Item

class Engine:
    def __init__(self, db):
        self._db = db

        self._root = None
        self._tab1 = None
        self._tab2 = None


    def start(self):
        self._root = tkinter.Tk()
        self._root.title('Macrotracker')

        self._render_content()

        self._root.mainloop()


    def _render_content(self):
        tab_control = ttk.Notebook(self._root)

        self._tab1 = tkinter.Frame(tab_control)
        self._tab2 = tkinter.Frame(tab_control)

        tab_control.add(self._tab1, text='Items')
        tab_control.add(self._tab2, text='Calculate')
        tab_control.pack(expand=1, fill='both')

        self._render_tab1()
        self._render_tab2()


    def _render_tab1(self):
        for widget in self._tab1.winfo_children():
            widget.destroy()

        item_data = self._db.get_items()

        tkinter.Button(self._tab1, text='Add food item', command=self._handle_insert_item).grid(column=0, row=0, pady=10)
        tkinter.Button(self._tab1, text='Remove food item', command=self._handle_delete_item).grid(column=1, row=0, pady=10)
        tkinter.Label(self._tab1, text='Showing all items:').grid(column=0, row=1, pady=10)

        for idx, col_name in enumerate(['Name', 'Serving Size', 'Calories', 'Protein']):
            width = 40 if idx == 0 else 20
            tkinter.Label(self._tab1, text=col_name, width=width, background='lightblue').grid(column=idx, row=2)

        for i, item in enumerate(item_data):
            for j, col in enumerate(item):
                bg_color = 'white' if i % 2 else 'lightgray'
                text = f'{col} g' if j == 1 or j == 3 else str(col)
                width = 40 if j == 0 else 20
                tkinter.Label(self._tab1, text=text, width=width, background=bg_color).grid(column=j, row=i+3)


    def _render_tab2(self):
        for widget in self._tab2.winfo_children():
            widget.destroy()

        item_data = self._db.get_items()

        if not item_data:
            placeholder_label = tkinter.Label(self._tab2,
                          text='Enter a food item in the "Items" tab to calculate macros!')
            placeholder_label.grid(column=0, row=0, columnspan=2, pady=10)
            return

        hint_label = tkinter.Label(self._tab2,
                  text='Calculate macros for your food items here by selecting a\nfood item and entering the amount of the food in grams.')
        hint_label.grid(column=0, row=0, columnspan=2, pady=10)

        options = [item[0] for item in item_data]

        var_dropdown = tkinter.StringVar()
        var_amount = tkinter.StringVar()

        if not var_dropdown.get():
            var_dropdown.set('Select a food item')

        calc_label = None
        cal_label = None
        prot_label = None


        def _update_calculation():
            amount = float(var_amount.get()) if var_amount.get() else 0
            selection = var_dropdown.get()
            selected_item_list = list(filter(lambda x: x[0] == selection, item_data))
            calc_label.config(text=f'Showing macros for {amount} g of {selection}:')

            calorie_calc = 0
            protein_calc = 0

            if selected_item_list:
                item = selected_item_list[0]
                calorie_calc = (amount / item[1]) * item[2]
                protein_calc = (amount / item[1]) * item[3]

            cal_label.config(text=f'{round(calorie_calc, 2)} calories')
            prot_label.config(text=f'{round(protein_calc, 2)} g protein')

        def on_entry_change(*args):
            _update_calculation()

        var_amount.trace_add('write', on_entry_change)

        def on_dropdown_change(x):
            _update_calculation()

        dropdown = tkinter.OptionMenu(self._tab2, var_dropdown, *options, command=on_dropdown_change)
        e_amount = tkinter.Entry(self._tab2, textvariable=var_amount)

        dropdown.grid(column=0, row=1)
        e_amount.grid(column=1, row=1)

        calc_label = tkinter.Label(self._tab2, text='')
        calc_label.grid(column=0, row=2, columnspan=2, pady=10)

        cal_label = tkinter.Label(self._tab2, text='')
        cal_label.grid(column=0, row=3)
        prot_label = tkinter.Label(self._tab2, text='')
        prot_label.grid(column=1, row=3)



    def _handle_insert_item(self):
        insert_window = tkinter.Toplevel(self._root)
        insert_window.title('Add new food item')

        var_name = tkinter.StringVar()
        var_ss = tkinter.StringVar()
        var_cal = tkinter.StringVar()
        var_prot = tkinter.StringVar()

        e_name = tkinter.Entry(insert_window, textvariable=var_name)
        e_ss = tkinter.Entry(insert_window, textvariable=var_ss)
        e_cal = tkinter.Entry(insert_window, textvariable=var_cal)
        e_prot = tkinter.Entry(insert_window, textvariable=var_prot)
        
        tkinter.Label(insert_window, text='Name of food item').grid(column=0,row=0)
        tkinter.Label(insert_window, text='Serving size (g)').grid(column=0,row=1)
        tkinter.Label(insert_window, text='Calories').grid(column=0,row=2)
        tkinter.Label(insert_window, text='Protein (g)').grid(column=0,row=3)

        e_name.grid(column=1, row=0)
        e_ss.grid(column=1, row=1)
        e_cal.grid(column=1, row=2)
        e_prot.grid(column=1, row=3)

        def _add_entry():
            err_label = tkinter.Label(insert_window, text='', fg='red')
            err_label.grid(column=0, row=6, columnspan=2)

            try:
                name, ss, cal, prot = var_name.get(), float(var_ss.get()), float(var_cal.get()), float(var_prot.get())

                if ss <= 0 or cal < 0 or prot < 0:
                    raise ValueError('Serving size must be greater than 0.')

                item = Item(name=name, serving_size=ss, calories=cal, protein=prot)

                self._db.insert_item(item)

                insert_window.destroy()

                self._render_tab1()
                self._render_tab2()

            except ValueError:
                err_label.config(text='One or more of the fields are empty or invalid.')

            except sqlite3.IntegrityError:
                err_label.config(text='The name of this food item is already taken.')

        tkinter.Button(insert_window, text='Add', command=_add_entry).grid(column=0, row=5, pady=10)
        tkinter.Button(insert_window, text='Cancel', command=lambda: insert_window.destroy()).grid(column=1, row=5, pady=10)


    def _handle_delete_item(self):
        delete_window = tkinter.Toplevel(self._root)
        delete_window.title('Remove existing food item')

        listbox = tkinter.Listbox(delete_window, selectmode=tkinter.EXTENDED, width=50)
        listbox.grid(column=0, columnspan=2)

        items = self._db.get_items()
        for item in items:
            listbox.insert(tkinter.END, item[0])

        def _remove_entry():
            selections = listbox.curselection()

            item_names = [listbox.get(idx) for idx in selections]

            self._db.remove_items(item_names)

            delete_window.destroy()

            self._render_tab1()
            self._render_tab2()

        tkinter.Button(delete_window, text='Delete', command=_remove_entry).grid(column=0, row=5, pady=10)
        tkinter.Button(delete_window, text='Cancel', command=lambda: delete_window.destroy()).grid(column=1, row=5, pady=10)
