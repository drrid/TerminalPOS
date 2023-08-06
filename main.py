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
import requests


# Calendar Screen --------------------------------------------------------------------------------------------------------------------------------------------------
class PosBunker(Screen):
    BINDINGS = [
            ("f2", "modify_textile", "Modify Textile"),
            ("f5", "clear_inputs", "Clear"),
            ("f10", "request_export", "Export")]
    
    week_index = reactive(0)
    row_index_id = {}
    row_index_enc_id = {}
    modify_pt = False


    def compose(self):
        self.textile_widget = DataTable(id='pt_table', zebra_stripes=True, fixed_columns=1)
        self.textile_widget.cursor_type = 'row'

        self.inputs_container = Vertical(Horizontal(
                                    Input('', placeholder='Textile Name', id='name', classes='inputs'),Input('', placeholder='Length', id='length', classes='inputs'),
                                    Input('', placeholder='width', id='width', classes='inputs'),
                                    Input('', placeholder='weight', id='weight', classes='inputs'),Input('', placeholder='cost', id='cost', classes='inputs'),
                                    Input('', placeholder='price', id='price', classes='inputs'),Input('', placeholder='notes-t', id='notes-t', classes='inputs'),
                                    Button('Add', id='addtextile', classes='inputs'),Button('Update', id='updatetextile', classes='inputs'), id='inputs'),
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

        PT_CLMN = [['ID', 3], ['Textile Name', 13], ['length', 13], ['width', 12], ['weight', 10], ['cost', 10], ['price', 10], 
                   ['added time', 30], ['notes', 50], ['cost per meter', 30]]
        for c in PT_CLMN:
            self.textile_widget.add_column(f'{c[0]}', width=c[1])
        self.show_textiles()

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def on_input_changed(self, event: Input.Changed):
        try:
            if event.input.id in ['name', 'notes-t']:
                pass
            else:
                if self.is_float(event.input.value):
                        pass
                else:
                    self.query_one(f'#{event.input.id}').value = ''

            inp = self.query(Input)
            textiles = conf.select_all_starts_with(name=inp[0].value, length=inp[1].value, width=inp[2].value, weight=inp[3].value, cost=inp[4].value, price=inp[5].value)
            if len(textiles) != 0:
                textile_id = textiles[0][0]
                row_index = self.row_index_id.get(textile_id)
                self.textile_widget.move_cursor(row=row_index)

        except Exception as e:
            self.log_error(e)


    def on_button_pressed(self, event: Button.Pressed):
        try:
            inp = self.query(Input)
            existing_textile = conf.select_textile_by_details(name=inp[0].value, length=inp[1].value, width=inp[2].value, weight=inp[3].value, cost=inp[4].value, price=inp[5].value)
            
            for i in inp:
                if i.value == '':
                    # self.log_error("Textile with the same details already exists.")
                    return
            
            if event.control.id == 'addtextile':
                if existing_textile is not None:
                    self.log_error("Textile with the same details already exists.")
                    return
                else:
                    self.add_textile(name=inp[0].value, length=inp[1].value, width=inp[2].value, weight=inp[3].value, cost=inp[4].value, price=inp[5].value, notes=inp[6].value)
            elif event.control.id == 'updatetextile':
                self.update_textile(name=inp[0].value, length=inp[1].value, width=inp[2].value, 
                                    weight=inp[3].value, cost=inp[4].value, price=inp[5].value, notes=inp[6].value)

        except Exception as e:
            self.log_error("Error occurred while performing textile action: " + str(e))
            return


    def action_modify_textile(self):
        try:
            cursor = self.textile_widget.cursor_coordinate
            # inputs = ['fname', 'lname', 'dob', 'phone']
            self.query_one('#name').focus()

            if self.modify_pt == False:

                for i, inp in enumerate(self.query(Input)):
                    inp.value = self.textile_widget.get_cell_at(Coordinate(cursor.row, i+1))
                    inp.styles.background = 'teal'
                    if inp.id == 'notes-t':
                        self.query_one('#notes-t').value = self.textile_widget.get_cell_at(Coordinate(cursor.row, 8))    
                        # self.log_feedback(self.textile_widget.get_cell_at(Coordinate(cursor.row, 8)))               
                    
                self.modify_pt = True
                pass

            else :
                for i, inp in enumerate(self.query(Input)):
                    inp.value = ''
                    inp.styles.background = self.styles.background
                self.modify_pt = False
        except Exception as e:
            self.log_error(f"Error in modify_patient: {e}")
            


    def add_textile(self, name, length, width, weight, cost, price, notes):
        if self.modify_pt == False:
            try:
                textile = conf.Textile(name=name, length=length, width=width, weight=weight, cost=cost, price=price, notes=notes)
                textile_id = conf.save_to_db(textile)
                self.show_textiles()
                self.log_feedback("Textile added successfully.")
                # self.show_patients()
                # row_index = self.row_index_id.get(str(textile_id))
                # self.textile_widget.move_cursor(row=row_index)
                

            except Exception as e:
                self.log_error(f"Error adding textile: {e}")


    def update_textile(self, name, length, width, weight, cost, price, notes):
        try:
            self.action_modify_textile()
            cursor = self.textile_widget.cursor_coordinate
            inp = self.textile_widget.get_row_at(cursor.row)
            
            # existing_textile = conf.select_textile_by_details(name=inp[1], length=inp[2], width=inp[3], weight=inp[4], cost=inp[5], price=inp[6])

            # old_textile = conf.select_textile_by_id(inp[0])
            conf.update_textile(textile_id=inp[0], name=name, length=length, width=width, weight=weight, cost=cost, price=price, notes=notes)
            self.log_feedback("textile updated successfully.")
            self.show_textiles()
            row_index = self.textile_widget.get_row_index(inp[0])
            # self.log_feedback(row_index)
            self.textile_widget.move_cursor(row=int(row_index))


        except Exception as e:
            self.log_error(f"Error updating textile: {e}")


    def log_error(self, msg):
        timestamp = dt.datetime.now()
        self.query_one('#feedback').write(f'{timestamp}---[bold red]{str(msg)}')


    def log_feedback(self, msg):
        timestamp = dt.datetime.now()
        self.query_one('#feedback').write(f'{timestamp}---[bold #11696b]{str(msg)}')


    def show_textiles(self):
        try:
            current_row = self.textile_widget.cursor_row
            current_column = self.textile_widget.cursor_column
            self.textile_widget.clear()
            textiles = iter(conf.select_all_starts_with())
            self.row_index_id = {}
            for index, textile in enumerate(textiles):
                textile_id = textile[0]
                self.textile_widget.add_row(*textile, key=textile_id)
                self.row_index_id.update({textile_id: index})
                # self.log_feedback()
            self.textile_widget.move_cursor(row=current_row, column=current_column)
        except Exception as e:
            self.log_error("Error occurred in show_textiles: " + str(e))


    def action_request_export(self):
        url = "http://192.168.5.133:5000/generate_qr_custom"
        row = self.textile_widget.cursor_row
        data = self.textile_widget.get_row_at(row)
        qr_code = f'{data[0]} {data[1]}'
        # self.log_feedback(qr_code)
        params = {"field1": qr_code}
        
        response = requests.get(url, params=params)

        if response.status_code == 200:
            self.log_feedback("Request was successful!")
            return response.text
        else:
            self.log_error("Request failed!")
            return None



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
class PosBunkerApp(App):
    BINDINGS = [
            ("f2", "modify_textile", "Modify Textile"),
            ("f5", "clear_inputs", "Clear"),
            ("f10", "request_export", "Export")]
    
    CSS_PATH = 'styling.css'
    TITLE = 'TerminalPOS-Bunker'
    # SUB_TITLE = 'by Dr.Abdennebi Tarek'
    SCREENS = {"PosBunker": PosBunker()}

    def on_mount(self):
        self.push_screen(self.SCREENS.get('PosBunker'))


if __name__ == "__main__":
    app = PosBunkerApp()
    app.run()

 