from textual.app import App
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, DataTable, RichLog, Static
from textual.coordinate import Coordinate
from textual.containers import Container, Horizontal, Vertical
import conf
import datetime as dt
from escpos.printer import Network
import socketio
from math import floor


# Pos Screen --------------------------------------------------------------------------------------------------------------------------------------------------
class Pos(Screen):

    def compose(self):
        self.textile_widget = DataTable(id='pt_table', zebra_stripes=True, fixed_columns=1)
        self.textile_widget.cursor_type = 'row'

        self.inputs_container = Vertical(Horizontal(
            Input('', placeholder='Textile', id='textile', classes='inputs'), id='inputs'),
            Static('', id='total', classes='inputs'),
            id='upper_cnt')
        self.tables_container = Vertical(
            self.textile_widget, RichLog(id='feedback', highlight=True, markup=True, wrap=True),
            id='lower_cnt')

        self.footer_widget = Footer()
        self.footer_widget.styles.background = '#11696b'

        yield Header()
        yield Container(self.inputs_container, self.tables_container, id='app_grid')
        yield self.footer_widget

    def on_mount(self):
        PT_CLMN = [['ID', 7], ['Textile Name', 30], ['price', 20], ['quantity', 20], ['quantity left', 20], ['subtotal', 20]]
        for c in PT_CLMN:
            self.textile_widget.add_column(f'{c[0]}', width=c[1])
        self.query_one('#textile').focus()

        try:
            self.sio = socketio.Client()
            self.sio.connect('http://192.168.5.133:5555')
            self.sio.emit('clear')
        except socketio.exceptions.ConnectionError as e:
            self.log_error(f"Connection error: {e}")


    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def on_input_submitted(self, event: Input.Submitted):
        try:
            textiles = conf.select_all_textiles()
            qr_code_ids = [f'{textile.textile_id} {textile.name}' for textile in textiles]

            if event.value in qr_code_ids:
                # if self.is_float(event.value):
                id = int(event.value.split(' ')[0])
                textile = conf.select_textile_by_id(id)
                if str(id) in self.textile_widget.rows.keys():
                    row = self.textile_widget.get_row_index(str(id))
                    self.textile_widget.move_cursor(row=row)
                else:
                    quantity_left = conf.calculate_quantity_left(textile.textile_id)
                    self.textile_widget.add_row(*[textile.textile_id, textile.name, textile.calculate_price(0), 0, quantity_left, 0], key=str(id))
                    row = self.textile_widget.get_row_index(str(id))
                    self.textile_widget.move_cursor(row=row)

            elif self.is_float(event.value):
                current_row = self.textile_widget.cursor_row
                quantity = self.textile_widget.get_cell_at(Coordinate(row=current_row, column=3))
                # price = self.textile_widget.get_cell_at(Coordinate(row=current_row, column=3))

                new_value = quantity + float(event.value)

                price = conf.select_textile_by_id(int(self.textile_widget.get_row_at(current_row)[0])).calculate_price(new_value)
                self.textile_widget.update_cell_at(Coordinate(row=current_row, column=3), new_value)
                self.textile_widget.update_cell_at(Coordinate(row=current_row, column=2), price)
                self.textile_widget.update_cell_at(Coordinate(row=current_row, column=5), floor(price*new_value / 10) * 10)
                
                total = sum(float(self.textile_widget.get_row(r)[5]) for r in self.textile_widget.rows)
                self.query_one('#total').update(f'Total : {total} DA')


            elif event.value == 'confirm':
                rows = []
                for i, row in enumerate(self.textile_widget.rows):
                    rows.append(self.textile_widget.get_row_at(i))


                    # self.log_feedback([str(key) for key in self.textile_widget.rows.keys()])
                textiles_and_quantities = [(value[0], value[3]) for value in rows]
                transaction_id = conf.create_transaction_with_textiles(textiles_and_quantities)

                self.print_receipt(transaction_id, rows)
                self.clear_table()

            elif event.value == 'clear':
                self.clear_table()

            elif event.value == 'deleteqnt':
                current_row = self.textile_widget.cursor_row
                quantity = self.textile_widget.get_cell_at(Coordinate(row=current_row, column=3))
                # price = self.textile_widget.get_cell_at(Coordinate(row=current_row, column=3))
                new_value = 0
                price = conf.select_textile_by_id(int(self.textile_widget.get_row_at(current_row)[0])).calculate_price(new_value)
                self.textile_widget.update_cell_at(Coordinate(row=current_row, column=3), new_value)
                self.textile_widget.update_cell_at(Coordinate(row=current_row, column=2), price)
                self.textile_widget.update_cell_at(Coordinate(row=current_row, column=5), floor(price*new_value / 10) * 10)


            elif event.value == 'deleterow':
                current_row = self.textile_widget.get_row_at(self.textile_widget.cursor_row)
                id = str(current_row[0])
                # self.textile_widget.get_row_index
                self.textile_widget.remove_row(id)


            
            
            self.sio.emit('clear')
            for i, row in enumerate(self.textile_widget.rows):
                    data = self.textile_widget.get_row_at(i)
                  # Emitting the update event to the server with the data as JSON
                    self.sio.emit('update', {
                        'id': data[0],
                        'name': data[1],
                        'price': data[2],
                        'quantity': data[3],
                        'quantity_left': data[4],
                        'subtotal': data[5]
                    })

            self.query_one('#textile').value = ''
            self.query_one('#textile').focus()
        except Exception as e:
            self.log_error(e)
        finally:
            self.query_one('#textile').value = ''
            self.query_one('#textile').focus()


    def clear_table(self):
        self.textile_widget.clear()

    def print_receipt(self, transaction_id, rows):
        try:
            receipt = Network("192.168.5.79") #Printer IP Address
            receipt.text(f"{transaction_id}\n")
            receipt.text(f"id -- Textile Name   --  Price --    Quantity\n")
            for r in rows:
                receipt.text(f"{r[0]}--{r[1]}--{r[2]}--{r[3]}\n")
                receipt.text(f"    \n")
            receipt.text(f'total : *** {conf.calculate_total_for_transaction(transaction_id)} ***')
            receipt.barcode("{B" + f'{transaction_id}', "CODE128", function_type="B")
            receipt.cut()
        except Exception as e:
            self.log_error(e)


    def log_error(self, msg):
        timestamp = dt.datetime.now()
        self.query_one('#feedback').write(f'{timestamp}---[bold red]{str(msg)}')

    def log_feedback(self, msg):
        timestamp = dt.datetime.now()
        self.query_one('#feedback').write(f'{timestamp}---[bold #11696b]{str(msg)}')

  
# ------------------------------------------------------------------------Main App-----------------------------------------------------------------------------------------
class PosApp(App):

    CSS_PATH = 'styling.css'
    TITLE = 'TerminalPOS'
    SUB_TITLE = 'by Dr.Abdennebi Tarek'
    SCREENS = {"pos": Pos()}

    def on_mount(self):
        self.push_screen(self.SCREENS.get('pos'))


if __name__ == "__main__":
    app = PosApp()
    app.run()
 