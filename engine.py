import sqlite3
from tkinter import ttk
import tkinter
from datetime import date, timedelta
from models import Item, Record

class Engine:
    def __init__(self, db):
        self._db = db

        self._selected_date = date.today()
        self._root = None
        self._tab1 = None
        self._tab2 = None


    @staticmethod
    def _calculate_macros(item: Item, amount: float) -> tuple[float, float]:
        calorie_calc = (amount / item.serving_size) * item.calories
        protein_calc = (amount / item.serving_size) * item.protein

        return calorie_calc, protein_calc


    @staticmethod
    def _list_to_item(item_list) -> Item:
        return Item(name=item_list[0],
                    serving_size=item_list[1],
                    calories=item_list[2],
                    protein=item_list[3],)


    def start(self):
        self._root = tkinter.Tk()
        self._root.title('Macrotracker')

        self._render_content()

        self._root.mainloop()


    def _render_content(self):
        tab_control = ttk.Notebook(self._root)

        self._tab1 = tkinter.Frame(tab_control)
        self._tab2 = tkinter.Frame(tab_control)
        self._tab3 = tkinter.Frame(tab_control)

        tab_control.add(self._tab3, text='Tracker')
        tab_control.add(self._tab1, text='Items')
        tab_control.add(self._tab2, text='Calculate')
        tab_control.pack(expand=1, fill='both')

        self._render_tab3()
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
                item = self._list_to_item(selected_item_list[0])
                calorie_calc, protein_calc = self._calculate_macros(item, amount)

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


    def _render_tab3(self):
        for widget in self._tab3.winfo_children():
            widget.destroy()

        if not self._db.has_items():
            placeholder_label = tkinter.Label(self._tab3, text='Enter a food item in the "Items" tab to start tracking!')
            placeholder_label.grid(column=0, row=0, pady=10)
            return

        time_str = self._selected_date.strftime('%A, %B %d, %Y')
        title_label = tkinter.Label(self._tab3, text=f'Totals for {time_str}', font=(None, 16))
        title_label.grid(column=0, row=0, columnspan=2, pady=20)

        # Date picker frame start code block
        date_picker_frame = tkinter.Frame(self._tab3)
        date_picker_frame.grid(column=0, row=1, columnspan=2, pady=(0, 10))

        # Right button disabled?
        next_disabled = tkinter.DISABLED if self._selected_date == date.today() else tkinter.NORMAL

        def _prev_btn_command():
            self._selected_date -= timedelta(days=1)
            self._render_tab3()

        def _next_btn_command():
            self._selected_date += timedelta(days=1)
            self._render_tab3()

        prev_btn = tkinter.Button(date_picker_frame, text='<', width=1, command=_prev_btn_command)
        date_label = tkinter.Label(date_picker_frame, text=self._selected_date.strftime('%a, %B %d, %Y'), width=30, background='white')
        next_btn = tkinter.Button(date_picker_frame, text='>', width=1, state=next_disabled, command=_next_btn_command)

        prev_btn.grid(column=0, row=0)
        date_label.grid(column=1, row=0)
        next_btn.grid(column=2, row=0)
        # Date picker frame end code block

        cal_label = tkinter.Label(self._tab3, text='0 calories', font=(None, 12))
        prot_label = tkinter.Label(self._tab3, text='0 g protein', font=(None, 12))

        cal_label.grid(column=0, row=2)
        prot_label.grid(column=1, row=2)

        add_record_btn = tkinter.Button(self._tab3, text='Add record for this day', command=self._handle_add_record)
        add_record_btn.grid(column=0, row=3, pady=20)

        tkinter.Label(self._tab3, text='*Double click on an entry to modify it.', font=(None, 11, "italic"), foreground='red').grid(column=1, row=3)

        # Food record table start code block
        record_frame = tkinter.Frame(self._tab3, width=100, height=100)
        record_frame.grid(column=0, row=4, columnspan=2)

        tkinter.Label(record_frame, text='Food item', width=40, background='lightblue').grid(column=0, row=0)
        tkinter.Label(record_frame, text='Amount', width=10, background='lightblue').grid(column=1, row=0)
        tkinter.Label(record_frame, text='Calories', width=10, background='lightblue').grid(column=2, row=0)
        tkinter.Label(record_frame, text='Protein', width=10, background='lightblue').grid(column=3, row=0)

        records = self._db.get_joined_records(self._selected_date)

        calorie_total = 0
        protein_total = 0

        for idx, record in enumerate(records):
            item = self._list_to_item(record[3:])
            amount = record[2]
            calorie_calc, protein_calc = self._calculate_macros(item, amount)

            calorie_total += calorie_calc
            protein_total += protein_calc

            bg_color = 'white' if idx % 2 else 'lightgray'

            food_item_data = tkinter.Label(record_frame, text=item.name, width=40, background=bg_color)
            food_item_data.grid(column=0, row=idx+1)

            amount_data = tkinter.Label(record_frame, text=f'{amount} g', width=10, background=bg_color)
            amount_data.grid(column=1, row=idx+1)

            cal_data = tkinter.Label(record_frame, text=round(calorie_calc, 2), width=10, background=bg_color)
            cal_data.grid(column=2, row=idx+1)

            prot_data = tkinter.Label(record_frame, text=f'{round(protein_calc, 2)} g', width=10, background=bg_color)
            prot_data.grid(column=3, row=idx+1)

            def _on_row_click(event, rid=record[0], name_d=item.name, amount_d=amount):
                modify_window = tkinter.Toplevel(self._tab3)
                modify_window.title('Modify food record')

                def _on_delete_record():
                    self._db.delete_record(rid)
                    modify_window.destroy()
                    self._render_tab3()

                modify_label = tkinter.Label(modify_window,
                                             text=f'You are viewing a record for {amount_d} g of {name_d}.',
                                             pady=10)
                del_btn = tkinter.Button(modify_window, text='Delete food record', command=_on_delete_record)
                cancel_btn = tkinter.Button(modify_window, text='Cancel', command=lambda: modify_window.destroy())

                modify_label.grid(column=0, row=0, columnspan=2)
                del_btn.grid(column=0, row=1)
                cancel_btn.grid(column=1, row=1)

            food_item_data.bind('<Double-Button-1>', _on_row_click)
            amount_data.bind('<Double-Button-1>', _on_row_click)
            cal_data.bind('<Double-Button-1>', _on_row_click)
            prot_data.bind('<Double-Button-1>', _on_row_click)

        cal_label.config(text=f'{round(calorie_total, 2)} calories')
        prot_label.config(text=f'{round(protein_total, 2)} g protein')
        # Food record table end code block


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
                self._render_tab3()

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
            self._render_tab3()

        tkinter.Button(delete_window, text='Delete', command=_remove_entry).grid(column=0, row=5, pady=10)
        tkinter.Button(delete_window, text='Cancel', command=lambda: delete_window.destroy()).grid(column=1, row=5, pady=10)


    def _handle_add_record(self):
        new_window = tkinter.Toplevel(self._root)
        new_window.title('Add new record')

        var_item = tkinter.StringVar()
        var_amount = tkinter.StringVar()

        var_item.set('Select a food item to record')

        amount_label = tkinter.Label(new_window, text='Enter the food item and amount (in grams) you wish to record')
        amount_label.grid(column=0, row=0, columnspan=2, pady=10)

        items = [x[0] for x in self._db.get_items()]
        option_menu = tkinter.OptionMenu(new_window, var_item, *items)
        option_menu.grid(column=0, row=1)

        entry_frame = tkinter.Frame(new_window)
        entry_frame.grid(column=1, row=1)

        amount_entry = tkinter.Entry(entry_frame, textvariable=var_amount, width=10)
        amount_entry.grid(column=0, row=0)

        tkinter.Label(entry_frame, text='g').grid(column=1, row=0, padx=(10, 0))

        def add_record():
            err_label = tkinter.Label(new_window, text='', fg='red')
            err_label.grid(column=0, row=6, columnspan=2)

            try:
                item, amt = var_item.get(), float(var_amount.get())

                if item not in items or amt <= 0:
                    raise ValueError('Serving size must be greater than 0.')

                record = Record(date=self._selected_date, food=item, amt=amt)

                self._db.insert_record(record)

                new_window.destroy()

                self._render_tab3()

            except ValueError as e:
                err_label.config(text='Please select a food item and enter a valid amount.')

        submit_btn = tkinter.Button(new_window, text='Add new record', command=add_record)
        cancel_btn = tkinter.Button(new_window, text='Cancel', command=lambda: new_window.destroy())

        submit_btn.grid(column=0, row=2, pady=10)
        cancel_btn.grid(column=1, row=2, pady=10)

