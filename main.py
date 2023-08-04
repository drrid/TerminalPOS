from textual.app import App
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, DataTable, Button, TextLog
from textual.coordinate import Coordinate
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual import work
import conf
import datetime as dt
from dateutil import parser
import os
from textual.worker import Worker, get_current_worker


# Calendar Screen --------------------------------------------------------------------------------------------------------------------------------------------------
class Calendar(Screen):

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
                                    Input('', placeholder='price', id='price', classes='inputs'),
                                    Button('Add', id='addtextile', classes='inputs'),Button('Update', id='updatetextile', classes='inputs'), id='inputs'),
                                id='upper_cnt')
        self.tables_container = Vertical(
                            self.textile_widget, TextLog(id='feedback', highlight=True, markup=True),
                            id='lower_cnt')
        
        self.footer_widget = Footer()
        self.footer_widget.styles.background = '#11696b'

        yield Header()
        yield Container(self.inputs_container, self.tables_container, id='app_grid')
        yield self.footer_widget    
    

    def on_mount(self):

        PT_CLMN = [['ID', 3], ['Textile Name', 13], ['length', 13], ['width', 12], ['weight', 10], ['cost', 10], ['price', 10], ['added time', 30]]
        for c in PT_CLMN:
            self.textile_widget.add_column(f'{c[0]}', width=c[1])
        self.show_textiles()


    def on_input_changed(self, event: Input.Changed):
        if event.input.id != 'notes':
            try:
                name = self.query_one('#name').value
                length = self.query_one('#length').value
                width = self.query_one('#width').value
                weight = self.query_one('#weight').value
                cost = self.query_one('#cost').value
                price = self.query_one('#price').value
                # if phone.isdigit():
                #     phone = int(phone)
                # else:
                #     self.query_one('#phone').value = ''

                textiles = conf.select_all_starts_with(name=name, length=length, width=width, weight=weight, cost=cost, price=price)
                if len(textiles) != 0:
                    textile_id = textiles[0][0]
                    row_index = self.row_index_id.get(textile_id)
                    self.textile_widget.move_cursor(row=row_index)

            except Exception as e:
                self.log_error(e)


    def on_button_pressed(self, event: Button.Pressed):
        # try:
        #     cursor = self.textile_widget.cursor_coordinate
        #     # textile_id = self.textile_widget.get_cell_at(Coordinate(cursor.row, 0))
        # except Exception as e:
        #     self.log_error("Error occurred while fetching textile ID: " + str(e))
        #     return

        try:
            name = self.query_one('#name').value
            length = self.query_one('#length').value
            width = self.query_one('#width').value
            weight = self.query_one('#weight').value
            cost = self.query_one('#cost').value
            price = self.query_one('#price').value
        except Exception as e:
            self.log_error("Error occurred while fetching input values: " + str(e))
            return

        # # Validate the input values
        # if not name or not length or not phone or not date_of_birth:
        #     self.log_error("Please fill in all fields.")
        #     return

        # try:
        #     parsed_phone = int(phone)
        # except ValueError:
        #     self.log_error("Invalid phone number. Please enter a valid integer.")
        #     return

        # Check for textile duplication
        try:
            existing_textile = conf.select_textile_by_details(name, length, width, weight, cost, price)
            if existing_textile:
                self.log_error("Textile with the same details already exists.")
                return
        except Exception as e:
            self.log_error("Error occurred while checking for existing textile: " + str(e))
            return

        try:
            if event.control.id == 'addtextile':
                self.add_textile(name, length, width, weight, cost, price)
            elif event.control.id == 'updatetextile':
                self.update_textile(name, length, width, weight, cost, price)
            else:
                self.log_error("Invalid button event.")
                return
        except Exception as e:
            self.log_error("Error occurred while performing textile action: " + str(e))
            return




    # def action_modify_patient(self):
    #     try:
    #         cursor = self.textile_widget.cursor_coordinate
    #         # patient_id = self.patient_widget.get_cell_at(Coordinate(cursor.row, 0))
    #         inputs = ['fname', 'lname', 'dob', 'phone']
    #         self.query_one('#fname').focus()

    #         if self.modify_pt == False:

    #             for i, inp in enumerate(inputs):
    #                 self.query_one(f'#{inp}').value = self.textile_widget.get_cell_at(Coordinate(cursor.row, i+1))
    #                 self.query_one(f'#{inp}').styles.background = 'teal'
    #                 if i==4:
    #                     self.query_one(f'#{inp}').value = int(self.textile_widget.get_cell_at(Coordinate(cursor.row, i+1)))
    #             self.modify_pt = True
    #             pass

    #         else :
    #             for i, inp in enumerate(inputs):
    #                 self.query_one(f'#{inp}').value = ''
    #                 self.query_one(f'#{inp}').styles.background = self.styles.background
    #             self.modify_pt = False
    #     except Exception as e:
    #         self.log_error(f"Error in modify_patient: {e}")
            


    def add_textile(self, name, length, width, weight, cost, price):
        if self.modify_pt == False:
            try:
                textile = conf.Textile(name=name, length=length, width=width, weight=weight, cost=cost, price=price)
                textile_id = conf.save_to_db(textile)
                self.show_textiles()
                self.log_feedback("Textile added successfully.")
                # self.show_patients()
                # row_index = self.row_index_id.get(str(textile_id))
                # self.textile_widget.move_cursor(row=row_index)
                

            except Exception as e:
                self.log_error(f"Error adding textile: {e}")


    def update_textile(self, patient_id, first_name, last_name, phone, date_of_birth):
        try:
            self.action_modify_patient()
            old_patient = conf.select_patient_by_id(patient_id)
            conf.update_patient(patient_id=patient_id, first_name=first_name, last_name=last_name, phone=phone, date_of_birth=date_of_birth)
            self.log_feedback("textile updated successfully.")
            self.show_textiles()
            row_index = self.row_index_id.get(str(patient_id))
            self.textile_widget.move_cursor(row=row_index)

            old_foldername = f"Z:\\patients\\{patient_id} {old_patient.first_name} {old_patient.last_name}"
            new_foldername = f"Z:\\patients\\{patient_id} {first_name} {last_name}"
            isExist = os.path.exists(f'Z:\\patients\\{old_foldername}')
            if isExist:
                os.rename(old_foldername, new_foldername)
            else:
                os.makedirs(new_foldername)

        except Exception as e:
            self.log_error(f"Error updating patient: {e}")


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





    def on_data_table_cell_selected(self, message: DataTable.CellSelected):
        try:
            if message.control.id == 'enc_table':
                self.query_one('#notes').focus()
                self.query_one('#notes').value = ''
            if message.control.id == 'cal_table':
                self.selected_calendar()
                self.selected_calendar()
                # self.update_tooltip()
        except Exception as e:
            self.log_error(e)


    # def on_data_table_cell_highlighted(self, message: DataTable.CellHighlighted):
    #     if message.control.id == 'cal_table':
    #         self.update_tooltip()

    

    def on_data_table_row_selected(self, message: DataTable.RowSelected):
        try:
            if message.control.id == 'pt_table':
                if self.modify_pt == True:
                    self.action_modify_patient()
                self.encounter_widget.cursor_type = 'row'
                cursor = self.calendar_widget.cursor_coordinate
                cursor_value = self.calendar_widget.get_cell_at(cursor)
                if '_' not in cursor_value:
                    self.calendar_widget.move_cursor(row=0, column=0)
                self.show_encounters()
            elif message.control.id == 'enc_table':
                self.encounter_widget.cursor_type = 'cell'
                self.calendar_widget.move_cursor(row=0, column=0)
        except Exception as e:
            self.log_error(e)
            

    
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

 