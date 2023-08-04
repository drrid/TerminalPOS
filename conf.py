from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Date, and_, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()
password = os.getenv('DB_PASSWORD')
uri = os.getenv('URI')


engine = create_engine(f'mysql+pymysql://root:{password}@{uri}', pool_recycle=3600)

# engine = create_engine('sqlite:///database.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)



# Patient Class -----------------------------------------------------------------------------------------------------------
class Textile(Base):

    __tablename__ = 'textile'
    textile_id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(50))
    length = Column(Float())
    width = Column(Float())
    weight = Column(Float())
    cost = Column(Float())
    price = Column(Float())
    added_time = Column(DateTime, default=func.now())

    transactions = relationship('TransactionItem', back_populates='textile')

    def __repr__(self):
        return f'{self.textile_id},{self.name},{self.length},{self.width},{self.weight},{self.cost},{self.price},{self.added_time}'
#---------------------------------------------------------------------------------------------------------------------------

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer(), primary_key=True, autoincrement=True)
    transaction_date = Column(DateTime, default=func.now())
    
    # Relationship to TransactionItem
    items = relationship('TransactionItem', back_populates='transaction')


class TransactionItem(Base):
    __tablename__ = 'transaction_items'
    item_id = Column(Integer(), primary_key=True, autoincrement=True)
    transaction_id = Column(Integer(), ForeignKey('transactions.transaction_id'))
    textile_id = Column(Integer(), ForeignKey('textile.textile_id'))
    quantity = Column(Integer())
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
    


def create_transaction_with_textiles(textiles_and_quantities):
    """Create a new transaction with multiple textiles and quantities."""
    with Session() as session:
        try:
            new_transaction = Transaction()
            session.add(new_transaction)
            session.commit()

            for textile_id, quantity in textiles_and_quantities:
                textile = session.query(Textile).filter_by(textile_id=textile_id).first()
                if textile:
                    subtotal = quantity * textile.price
                    new_item = TransactionItem(transaction_id=new_transaction.transaction_id,
                                               textile_id=textile_id,
                                               quantity=quantity,
                                               subtotal=subtotal)
                    session.add(new_item)
                    # textile.quantity_left -= quantity
            
            session.commit()
            return new_transaction.transaction_id
        except Exception as e:
            session.rollback()
            print(f"Error creating transaction: {e}")
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


def select_all_starts_with(**kwargs):
    with Session() as session:
        try:
            filters = [getattr(Textile, key).startswith(value) for key, value in kwargs.items()]
            return [(str(r.textile_id), str(r.name), str(r.length), str(r.width), 
                     str(r.weight), str(r.cost), str(r.price),  str(r.added_time)) 
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
    


def select_textile_by_details(textile_name, textile_length, textile_width, textile_weight_of_roll, textile_cost_of_roll, textile_price_per_meter):
    with Session() as session:
        try:
            textile = session.query(Textile).filter(Textile.name == textile_name,
                                                    Textile.length == textile_length,
                                                    Textile.width == textile_width,
                                                    Textile.weight == textile_weight_of_roll,
                                                    Textile.cost == textile_cost_of_roll,
                                                    Textile.price == textile_price_per_meter).first()
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


textiles_and_quantities = [(3, 3), (4, 1)]
transaction_id = create_transaction_with_textiles(textiles_and_quantities)
print(calculate_quantity_left(4))