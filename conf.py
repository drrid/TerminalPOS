from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Date, and_, func
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


    def __repr__(self):
        return f'{self.textile_id},{self.name},{self.length},{self.width},{self.weight},{self.cost},{self.price},{self.added_time}'
#---------------------------------------------------------------------------------------------------------------------------


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine


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


init_db()
