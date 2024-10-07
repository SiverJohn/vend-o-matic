import psycopg
from os import getenv

def generateConnection(autocommit: bool=False) -> psycopg.Connection:
    keys = [x.lower()+"="+getenv(x) for x in ['HOST','USER','PASSWORD','DBNAME'] if getenv(x)]
    connectionString = " ".join(keys)
    connection = psycopg.connect(connectionString,autocommit=autocommit)
    return connection

def createDB(name: str,dropIfExists: bool=False) -> None:
    conn = generateConnection(True)
    cursor = conn.cursor()
    cursor.execute("select exists(SELECT datname FROM pg_catalog.pg_database WHERE datname=%s);",[name])
    dataBaseExists = cursor.fetchone()[0]
    if dataBaseExists and dropIfExists:
        cursor.execute(psycopg.sql.SQL("DROP DATABASE {};").format(psycopg.sql.SQL(name)))
        cursor.execute(psycopg.sql.SQL("CREATE DATABASE {};").format(psycopg.sql.SQL(name)))
    else:
        cursor.execute(psycopg.sql.SQL("CREATE DATABASE {};").format(psycopg.sql.SQL(name)))

def dropDB(name: str):
    conn = generateConnection(True)
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_catalog.pg_database WHERE datname=%s;",[name])
    dataBaseExists = cursor.fetchall()
    if dataBaseExists:
        cursor.execute(psycopg.sql.SQL("DROP DATABASE {};").format(psycopg.sql.SQL(name)))


def setupDB() -> None:
    conn = generateConnection(True)
    cursor = conn.cursor()
    cursor.execute("select exists(SELECT 1 FROM pg_tables WHERE tablename='inventory');")
    inventoryTableExists = cursor.fetchone()[0]
    if not inventoryTableExists:
        cursor.execute("""
            CREATE TABLE inventory (
                id integer PRIMARY KEY,
                name text,
                sold integer,
                cost float,
                stock integer
                );
            """)
        initInventoryTable()
    cursor.execute("select exists(SELECT 1 FROM pg_tables WHERE tablename='cash');")
    cashTableExists = cursor.fetchone()[0]
    if not cashTableExists:
        cursor.execute("""
            CREATE TABLE cash (
                id text PRIMARY KEY,
                banked integer,
                available integer,
                denomination float
                );
            """)
        initCashTable()
    conn.close()
    cursor.close()

def dropTables() -> None:
    conn = generateConnection(autocommit=True)
    cursor = conn.cursor()
    cursor.execute("select exists(SELECT 1 FROM pg_tables WHERE tablename='inventory');")
    inventoryTableExists = cursor.fetchone()[0]
    if inventoryTableExists:
        cursor.execute("DROP TABLE inventory;")
    cursor.execute("select exists(SELECT 1 FROM pg_tables WHERE tablename='cash');")
    cashTableExists = cursor.fetchone()[0]
    if cashTableExists:
        cursor.execute("DROP TABLE cash;")


def initInventoryTable() -> None:
    conn = generateConnection()
    cursor = conn.cursor()
    inventory = [(i, x, 0, 0.50, 5) for i, x in enumerate(["Milk Tea 500mL", "Green Tea 500mL", "Boba Tea 500mL"])]

    with conn.transaction():
        with cursor.copy("COPY inventory (id, name, sold, cost, stock) FROM STDIN;") as copy:
            for item in inventory:
                copy.write_row(item)
    cursor.close()
    conn.close()

def initCashTable() -> None:
    conn = generateConnection()
    cursor = conn.cursor()

    with conn.transaction():
        cursor.execute("""
                       INSERT INTO cash (id, banked, available, denomination)
                       VALUES ('quarter_usd',0,0,0.25);""")

    cursor.close()
    conn.close()

def resetTables() -> None:
    conn = generateConnection()
    cursor = conn.cursor()

    cursor.execute("UPDATE inventory set stock=5;")
    cursor.execute("UPDATE cash set available=0;")
    conn.commit()

    conn.close()

def currentUsableCoins(denomination: str="quarter_usd") -> int:

    conn = generateConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT available FROM cash WHERE id=%s;",[denomination])
    
    coins = cursor.fetchone()[0]
    conn.close()
    return coins

def attempToInputCoin(inputJSON: any, denomination: str="quarter_usd")-> bool:
    coins = currentUsableCoins(denomination)

    if "coin" in inputJSON.keys():
        if inputJSON["coin"]>=1:
            conn = generateConnection()
            cursor = conn.cursor()
            coins +=1
            cursor.execute("UPDATE cash set available=%s WHERE id=%s;", (coins,denomination))
            conn.commit()
            conn.close()
            out = (True,coins)
        else:
            out = (False,None)
    else:
        out = (False,None)

    return out

def returnStoredCoins(paymentCoins: int=0, denomination: str="quarter_usd") -> int:
    coins = currentUsableCoins(denomination)

    conn = generateConnection()
    cursor = conn.cursor()

    if paymentCoins > 0:
        cursor.execute("UPDATE cash set banked=banked+%s;",[paymentCoins])
        cursor.execute("UPDATE cash set available=0;")
        coins -= paymentCoins
    else:
        cursor.execute("UPDATE cash set available=0;")

    conn.commit()
    conn.close()
    return coins

def getInventoryStocks() -> list[int]:
    conn = generateConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM inventory;")
    stock = cursor.fetchall()
    flattenedStock = [x for y in stock for x in y]
    conn.close()
    return flattenedStock

def getItemStock(itemID: int)-> int:
    conn = generateConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM inventory WHERE id=%s;",[itemID])
    stock = cursor.fetchone()
    if stock is None:
        return 0
    conn.close()
    return stock[0]

def updateItemStock(itemID: int, newStock: int) -> None:
    conn = generateConnection()
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET stock=%s WHERE id=%s;",[newStock,itemID])
    conn.commit()
    conn.close()
