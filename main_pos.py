from textual.app import App
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, DataTable, Button, RichLog
from textual.coordinate import Coordinate
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual import work
import conf
import datetime as dt
from dateutil import parser
import os
from textual.worker import Worker, get_current_worker
from escpos.printer import Network


# Calendar Screen --------------------------------------------------------------------------------------------------------------------------------------------------
class Calendar(Screen):


    def compose(self):
        self.textile_widget = DataTable(id='pt_table', zebra_stripes=True, fixed_columns=1)
        self.textile_widget.cursor_type = 'row'

        self.inputs_container = Vertical(Horizontal(
                                    Input('', placeholder='Textile', id='textile', classes='inputs'), id='inputs'),
                                id='upper_cnt')
        self.tables_container = Vertical(
                            self.textile_widget, RichLog(id='feedback', highlight=True, markup=True),
                            id='lower_cnt')
        
        self.footer_widget = Footer()
        self.footer_widget.styles.background = '#11696b'

        yield Header()
        yield Container(self.inputs_container, self.tables_container, id='app_grid')
        yield self.footer_widget    
    

    def on_mount(self):

        PT_CLMN = [['ID', 3], ['Textile Name', 13], ['price', 13], ['quantity', 12], ['quantity left', 10]]
        for c in PT_CLMN:
            self.textile_widget.add_column(f'{c[0]}', width=c[1])
        # self.show_textiles()


    def on_input_submitted(self, event: Input.Submitted):
        try:
            if '-' in event.value:
                id = int(event.value.split('-')[0])
                textile = conf.select_textile_by_id(id)
                if str(id) in self.textile_widget.rows.keys():
                    row = self.textile_widget.get_row_index(str(id))
                    self.textile_widget.move_cursor(row=row)
                    return
                else:
                    quantity_left = conf.calculate_quantity_left(textile.textile_id)
                    self.textile_widget.add_row(*[textile.textile_id, textile.name, textile.price, 0, quantity_left], key=str(id))
                    row = self.textile_widget.get_row_index(str(id))
                    self.textile_widget.move_cursor(row=row)

            elif event.value == 'add1':
                current_row = self.textile_widget.cursor_row
                old_value = self.textile_widget.get_cell_at(Coordinate(row=current_row, column=3))
                new_value = old_value + 1
                self.textile_widget.update_cell_at(Coordinate(row=current_row, column=3), new_value)
            elif event.value == 'confirm':
                rows = []
                for i, row in enumerate(self.textile_widget.rows):
                    rows.append(self.textile_widget.get_row_at(i))


                    # self.log_feedback([str(key) for key in self.textile_widget.rows.keys()])
                textiles_and_quantities = [(value[0], value[3]) for value in rows]
                transaction_id = conf.create_transaction_with_textiles(textiles_and_quantities)

                receipt = Network("192.168.5.79") #Printer IP Address
                receipt.text(f"{transaction_id}\n")
                receipt.text(f"id -- Textile Name   --  Price --    Quantity\n")
                for r in rows:
                    receipt.text(f"{r[0]}--{r[1]}--{r[2]}--{r[3]}\n")
                receipt.barcode("{B" + f'{transaction_id}', "CODE128", function_type="B")
                receipt.cut()


            self.query_one('#textile').value = ''
        except Exception as e:
            self.log_error(e)


    def log_error(self, msg):
        timestamp = dt.datetime.now()
        self.query_one('#feedback').write(f'{timestamp}---[bold red]{str(msg)}')


    def log_feedback(self, msg):
        timestamp = dt.datetime.now()
        self.query_one('#feedback').write(f'{timestamp}---[bold #11696b]{str(msg)}')



    # def on_data_table_cell_selected(self, message: DataTable.CellSelected):
    #     try:
    #         if message.control.id == 'enc_table':
    #             self.query_one('#notes').focus()
    #             self.query_one('#notes').value = ''
    #         if message.control.id == 'cal_table':
    #             self.selected_calendar()
    #             self.selected_calendar()
    #             # self.update_tooltip()
    #     except Exception as e:
    #         self.log_error(e)


    # def on_data_table_cell_highlighted(self, message: DataTable.CellHighlighted):
    #     if message.control.id == 'cal_table':
    #         self.update_tooltip()

    
    # def on_data_table_row_selected(self, message: DataTable.RowSelected):
    #     try:
    #         if message.control.id == 'pt_table':
    #             if self.modify_pt == True:
    #                 self.action_modify_patient()
    #             self.encounter_widget.cursor_type = 'row'
    #             cursor = self.calendar_widget.cursor_coordinate
    #             cursor_value = self.calendar_widget.get_cell_at(cursor)
    #             if '_' not in cursor_value:
    #                 self.calendar_widget.move_cursor(row=0, column=0)
    #             self.show_encounters()
    #         elif message.control.id == 'enc_table':
    #             self.encounter_widget.cursor_type = 'cell'
    #             self.calendar_widget.move_cursor(row=0, column=0)
    #     except Exception as e:
    #         self.log_error(e)
            

    
# ------------------------------------------------------------------------Main App-----------------------------------------------------------------------------------------
class PMSApp(App):
    BINDINGS = [("ctrl+left", "previous_week", "Previous Week"),
            ("ctrl+right", "next_week", "Next Week"),
            ("f1", "add_encounter", "Add Encounter"),
            ("f2", "modify_patient", "Modify Patient"),
            ("ctrl+delete", "delete_encounter", "Delete Encounter"),
            ("f5", "clear_inputs", "Clear"),
            ("f10", "request_export", "Export")]
    
    CSS_PATH = 'styling.css'
    TITLE = 'TerminalPMS'
    SUB_TITLE = 'by Dr.Abdennebi Tarek'
    SCREENS = {"calendar": Calendar()}

    def on_mount(self):
        self.push_screen(self.SCREENS.get('calendar'))


if __name__ == "__main__":
    app = PMSApp()
    app.run()

 