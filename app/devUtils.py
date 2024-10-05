import sqlalchemy as sql
from sqlalchemy_utils import database_exists, create_database, drop_database

from config import *
from schema import *

def _deleteDB(engine):
    drop_database(engine.url)

def _createDB(engine):
    create_database(engine.url)

def _createTables(baseClass,engine):
    baseClass.metadata.create_all(engine)

def initializeDB(session: sql.orm.Session) -> None:
    itemGen = lambda idx, name, sold, cost, inventory: { 'id':idx, 'name':name, 'sold':sold, 'cost':cost, 'inventory':inventory }
    items = [itemGen(i,x,0,0.50,5) for i,x in enumerate(['Milk Tea 500mL','Green Tea 500mL','Boba Tea 500mL'])]
    stmt = sql.insert(Items).values(items)
    session.execute(stmt)
    quarter = Cash(id='quarter_usd',banked=0,number=0,denomination=0.25)
    session.add(quarter)
    session.commit()

def createSQLAlcURL(config=None):
    if config is None:
        url_object = sql.URL.create(
                "postgresql",
                username=DBUSER,
                password=DBPASS,
                host=DBURL,
                database=DBNAME
        )
    else:
        url_object = sql.URL.create(
                "postgresql",
                username=config['DBUSER'],
                password=config['DBPASS'],
                host=config['DBURL'],
                database=config['DBNAME']
        )
    return url_object

def createUserEngine(config = None):
    url_object = createSQLAlcURL(config)
    engine = sql.create_engine(url_object)
    return engine

def setupDB(config=None):
    engine = createUserEngine(config)
    if not database_exists(engine.url):
        _createDB(engine)

def destroyDB(config=None):
    engine = createUserEngine(config)
    _deleteDB(engine)

if __name__ == '__main__':
    engine = createUserEngine()
    if not database_exists(engine.url):
        _createDB(engine)
