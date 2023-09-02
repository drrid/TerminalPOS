from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Date, and_, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv
import os
from math import floor


load_dotenv()
password = os.getenv('DB_PASSWORD')
uri = os.getenv('URI')


engine = create_engine(f'mysql+pymysql://root:{password}@{uri}', pool_recycle=3600)

# engine = create_engine('sqlite:///database.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)



# Textile Class -----------------------------------------------------------------------------------------------------------
class Textile(Base):

    __tablename__ = 'textile'
    textile_id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(50))
    length = Column(Float())
    width = Column(Float())
    weight = Column(Float())
    cost = Column(Float())
    price = Column(Float())
    notes = Column(String(200))
    added_time = Column(DateTime, default=func.now())
    # stored_cost_per_meter = Column(Float())

    transactions = relationship('TransactionItem', back_populates='textile')

    def calculate_price(self, quantity):
        if quantity >= 5:
            return self.price * 0.9
        elif quantity >= 3:
            return self.price * 0.95
        else:
            return self.price
        
    # def compute_and_set_cost_per_meter(self):
    #     self.stored_cost_per_meter = self.cost_per_meter

    @property
    def cost_per_meter(self):
        if self.length and self.weight and self.cost:  # checking if these values are not None
            return round((self.cost * self.weight) / self.length)
        else:
            return None

    def __repr__(self):
        return f'{self.textile_id},{self.name},{self.length},{self.width},{self.weight},{self.cost},{self.price},{self.added_time},{self.notes},{self.cost_per_meter}'
#---------------------------------------------------------------------------------------------------------------------------

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer(), primary_key=True, autoincrement=True)
    transaction_date = Column(DateTime, default=func.now())
    total = Column(Float())
    
    # Relationship to TransactionItem
    items = relationship('TransactionItem', back_populates='transaction')


class TransactionItem(Base):
    __tablename__ = 'transaction_items'
    item_id = Column(Integer(), primary_key=True, autoincrement=True)
    transaction_id = Column(Integer(), ForeignKey('transactions.transaction_id'))
    textile_id = Column(Integer(), ForeignKey('textile.textile_id'))
    quantity = Column(Float())
    subtotal = Column(Float())

    transaction = relationship('Transaction', back_populates='items')
    textile = relationship('Textile', back_populates='transactions')


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine


def calculate_quantity_left(textile_id):
    with Session() as session:
        try:
            # Get all TransactionItems for the given textile_id
            transaction_items = session.query(TransactionItem).filter_by(textile_id=textile_id).all()

            # Calculate the total quantity sold
            total_quantity_sold = sum(item.quantity for item in transaction_items)

            # Get the initial quantity of the textile
            textile = session.query(Textile).filter_by(textile_id=textile_id).first()
            initial_quantity = textile.length  # Assuming you have a 'quantity' attribute in the Textile class

            # Calculate the quantity left
            quantity_left = initial_quantity - total_quantity_sold
            return quantity_left
        except Exception as e:
            print(e)
    

# def round_total_amount(total_amount):
#     rounding_rules = [
#         {'threshold': x, 'limit': x + 40, 'round_to': 40} for x in range(1000, 4000, 500)
#     ] + [
#         {'threshold': x, 'limit': x + 50, 'round_to': 50} for x in range(2000, 4000, 500)
#     ] + [
#         {'threshold': x, 'limit': x + 100, 'round_to': 100} for x in range(4000, 7000, 500)
#     ] + [
#         {'threshold': x, 'limit': x + 200, 'round_to': 200} for x in range(7000, 10000, 500)
#     ] + [
#         {'threshold': x, 'limit': x + 300, 'round_to': 300} for x in range(10000, 15000, 500)
#     ] + [
#         {'threshold': x, 'limit': x + 500, 'round_to': 500} for x in range(15000, 50001, 1000)
#     ]

#     for rule in rounding_rules:
#         if rule['threshold'] <= total_amount < rule['limit']:
#             return rule['threshold']

#     return total_amount


def round_total_amount(total_amount):
    # Initialize rounding thresholds and corresponding rounding values
    rounding_rules = [
        {'threshold': 1000, 'limit': 1040, 'round_to': 40},
        {'threshold': 1500, 'limit': 1540, 'round_to': 40},
        {'threshold': 2000, 'limit': 2050, 'round_to': 50},
        {'threshold': 2500, 'limit': 2550, 'round_to': 50},
        {'threshold': 3000, 'limit': 3050, 'round_to': 50},
        {'threshold': 3500, 'limit': 3550, 'round_to': 50},
        {'threshold': 4000, 'limit': 4100, 'round_to': 100},
        {'threshold': 4500, 'limit': 4600, 'round_to': 100},
        {'threshold': 5000, 'limit': 5100, 'round_to': 100},
        {'threshold': 5500, 'limit': 5600, 'round_to': 100},
        {'threshold': 6000, 'limit': 6100, 'round_to': 100},
        {'threshold': 6500, 'limit': 6600, 'round_to': 100},
        {'threshold': 7000, 'limit': 7200, 'round_to': 200},
        {'threshold': 7500, 'limit': 7700, 'round_to': 200},
        {'threshold': 8000, 'limit': 8200, 'round_to': 200},
        {'threshold': 8500, 'limit': 8700, 'round_to': 200},
        {'threshold': 9000, 'limit': 9200, 'round_to': 200},
        {'threshold': 9500, 'limit': 9700, 'round_to': 200},
        {'threshold': 10000, 'limit': 10300, 'round_to': 300},
        {'threshold': 10500, 'limit': 10800, 'round_to': 300},
        {'threshold': 11000, 'limit': 11300, 'round_to': 300},
        {'threshold': 11500, 'limit': 11800, 'round_to': 300},
        {'threshold': 12500, 'limit': 12800, 'round_to': 300},
        {'threshold': 13000, 'limit': 13300, 'round_to': 300},
        {'threshold': 13500, 'limit': 13800, 'round_to': 300},
        {'threshold': 14000, 'limit': 14300, 'round_to': 300},
        {'threshold': 14500, 'limit': 14800, 'round_to': 300},
        {'threshold': 15000, 'limit': 15300, 'round_to': 300},
        {'threshold': 15500, 'limit': 15800, 'round_to': 300},
        {'threshold': 16000, 'limit': 16300, 'round_to': 300},
        {'threshold': 16500, 'limit': 16800, 'round_to': 300},
        {'threshold': 17000, 'limit': 17300, 'round_to': 300},
        {'threshold': 17500, 'limit': 17800, 'round_to': 300},
        {'threshold': 18000, 'limit': 18300, 'round_to': 300},
        {'threshold': 18500, 'limit': 18800, 'round_to': 300},
        {'threshold': 19000, 'limit': 19300, 'round_to': 300},
        {'threshold': 19500, 'limit': 19800, 'round_to': 300},
        {'threshold': 20000, 'limit': 20300, 'round_to': 300},
        {'threshold': 20500, 'limit': 20800, 'round_to': 300},
        {'threshold': 21000, 'limit': 21300, 'round_to': 300},
        {'threshold': 21500, 'limit': 21800, 'round_to': 300},
        {'threshold': 22000, 'limit': 22300, 'round_to': 300},
        {'threshold': 22500, 'limit': 22800, 'round_to': 300},
        {'threshold': 23000, 'limit': 23300, 'round_to': 300},
        {'threshold': 23500, 'limit': 23800, 'round_to': 300},
        {'threshold': 24000, 'limit': 24300, 'round_to': 300},
        {'threshold': 24500, 'limit': 24800, 'round_to': 300},
        {'threshold': 25000, 'limit': 25300, 'round_to': 300},
        {'threshold': 25500, 'limit': 25800, 'round_to': 300},
        {'threshold': 26000, 'limit': 26300, 'round_to': 300},
        {'threshold': 26500, 'limit': 26800, 'round_to': 300},
        {'threshold': 27000, 'limit': 27300, 'round_to': 300},
        {'threshold': 27500, 'limit': 27800, 'round_to': 300},
        {'threshold': 28000, 'limit': 28300, 'round_to': 300},
        {'threshold': 28500, 'limit': 28800, 'round_to': 300},
        {'threshold': 29000, 'limit': 29300, 'round_to': 300},
        {'threshold': 29500, 'limit': 29800, 'round_to': 300},
        {'threshold': 30000, 'limit': 30300, 'round_to': 300},
        {'threshold': 30500, 'limit': 30800, 'round_to': 300},
        {'threshold': 31000, 'limit': 31300, 'round_to': 300},
        {'threshold': 31500, 'limit': 31800, 'round_to': 300},
        {'threshold': 32000, 'limit': 32300, 'round_to': 300},
        {'threshold': 32500, 'limit': 32800, 'round_to': 300},
        {'threshold': 33000, 'limit': 33300, 'round_to': 300},
        {'threshold': 33500, 'limit': 33800, 'round_to': 300},
        {'threshold': 34000, 'limit': 34300, 'round_to': 300}
    ]

    for rule in rounding_rules:
        if rule['threshold'] <= total_amount < rule['limit']:
            return rule['threshold']

    return total_amount

def create_transaction_with_textiles(textiles_and_quantities):
    """Create a new transaction with multiple textiles and quantities."""
    with Session() as session:
        try:
            new_transaction = Transaction()
            session.add(new_transaction)

            total_amount = 0.0  # Variable to hold the total amount for the transaction

            for textile_id, quantity in textiles_and_quantities:
                textile = session.query(Textile).filter_by(textile_id=textile_id).first()
                if textile:
                    subtotal = floor(quantity * textile.calculate_price(quantity) / 10) * 10
                    total_amount += subtotal  # Add the subtotal to the total amount

                    new_item = TransactionItem(transaction_id=new_transaction.transaction_id,
                                               textile_id=textile_id,
                                               quantity=quantity,
                                               subtotal=subtotal)
                    session.add(new_item)

            # Apply rounding rules to total_amount
            rounded_total = round_total_amount(total_amount)

            new_transaction.total = rounded_total  # Update the transaction's total column
            
            session.commit()
            return new_transaction.transaction_id
        except Exception as e:
            session.rollback()
            print(f"Error creating transaction: {e}")
            return None


# def create_transaction_with_textiles(textiles_and_quantities):
#     """Create a new transaction with multiple textiles and quantities."""
#     with Session() as session:
#         try:
#             new_transaction = Transaction()
#             session.add(new_transaction)
#             session.commit()

#             for textile_id, quantity in textiles_and_quantities:
#                 textile = session.query(Textile).filter_by(textile_id=textile_id).first()
#                 if textile:
#                     # if quantity >= 3 and quantity < 5:
#                     #     subtotal = quantity * textile.price * 0.95
#                     # if quantity >= 5:
#                     #     subtotal = quantity * textile.price * 0.9
#                     # else:
#                         # subtotal = quantity * textile.price
#                     subtotal = floor(quantity * textile.calculate_price(quantity) / 10) * 10

#                     new_item = TransactionItem(transaction_id=new_transaction.transaction_id,
#                                                textile_id=textile_id,
#                                                quantity=quantity,
#                                                subtotal=subtotal)
#                     session.add(new_item)
#                     # textile.quantity_left -= quantity
            
#             session.commit()
#             return new_transaction.transaction_id
#         except Exception as e:
#             session.rollback()
#             print(f"Error creating transaction: {e}")
#             return None
        
def calculate_total_for_transaction(transaction_id):
    """Calculate the total amount of transaction items for a given transaction id."""
    with Session() as session:
        try:
            # Get all TransactionItems for the given transaction_id
            transaction_items = session.query(TransactionItem).filter_by(transaction_id=transaction_id).all()

            # Calculate the total amount
            total = sum(item.subtotal for item in transaction_items)
            
            return total
        except Exception as e:
            print(f"Error calculating total for transaction: {e}")
            return None


def update_textile(textile_id, **kwargs):
    """Update the textile with the given ID using the provided keyword arguments."""
    with Session() as session:
        try:
            textile_to_update = session.query(Textile).filter(Textile.textile_id == textile_id).one()

            for key, value in kwargs.items():
                setattr(textile_to_update, key, value)

            session.commit()
        except Exception as e:
            print(e)
            session.rollback()


def save_to_db(record):
    """Save the given record to the database."""
    with Session() as session:
        try:
            session.add(record)
            session.commit()
            generated_id = record.textile_id
            return generated_id
        except Exception as e:
            session.rollback()
            print(e)

# def save_to_db(record):
#     """Save the given record to the database."""
#     with Session() as session:
#         try:
#             # if isinstance(record, Textile):
#             record.compute_and_set_cost_per_meter()

#             session.add(record)
#             session.commit()
#             generated_id = record.textile_id
#             return generated_id
#         except Exception as e:
#             session.rollback()
#             print(e)


def select_all_starts_with(**kwargs):
    with Session() as session:
        try:
            filters = [getattr(Textile, key).startswith(value) for key, value in kwargs.items()]
            return [(str(r.textile_id), str(r.name), str(r.length), str(r.width), 
                     str(r.weight), str(r.cost), str(r.price),  str(r.added_time), str(r.notes), str(r.cost_per_meter)) 
                    for r in session.query(Textile).filter(*filters)]
        except Exception as e:
            print(e)


        
def select_all_textiles():
    with Session() as session:
        try:
            textiles = session.query(Textile).all()
            return textiles
        except Exception as e:
            print(f"Error selecting textiles: {e}")
            return None
    


def select_textile_by_details(name, length, width, weight, cost, price):
    with Session() as session:
        try:
            textile = session.query(Textile).filter(Textile.name == name,
                                                    Textile.length == length,
                                                    Textile.width == width,
                                                    Textile.weight == weight,
                                                    Textile.cost == cost,
                                                    Textile.price == price).first()
            return textile
        except Exception as e:
            print(f"Error selecting Textile by details: {e}")
            return None



def select_textile_by_id(textile_id):
    with Session() as session:
        try:
            textile = session.query(Textile).filter(Textile.textile_id == textile_id).first()
            return textile
        except Exception as e:
            print(f"Error selecting textile by details: {e}")
            return None
        

def select_transaction_by_id(transaction_id):
    with Session() as session:
        try:
            transaction = session.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
            return transaction
        except Exception as e:
            print(f"Error selecting transaction by details: {e}")
            return None


# def select_textile_by_id(textile_id):
#     with Session() as session:
#         try:
#             r = session.query(Textile).filter(Textile.textile_id == textile_id).first()
#             return [(str(r.textile_id), str(r.name), str(r.length), str(r.width), 
#                      str(r.weight), str(r.cost), str(r.price),  str(r.added_time)) 
#                     for r in session.query(Textile).filter(*filters)]
#         except Exception as e:
#             print(f"Error selecting textile by details: {e}")
#             return None

init_db()


print(round_total_amount(33530))
# print(select_all_textiles())
# textiles_and_quantities = [(3, 3), (4, 1)]
# transaction_id = create_transaction_with_textiles(textiles_and_quantities)
# print(calculate_quantity_left(4))