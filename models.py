# models.py
import sqlite3

def crear_base():
    conn = sqlite3.connect("farmacia.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tipos_medicamento (
        id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_tipo TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS presentaciones (
        id_presentacion INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_presentacion TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicamentos (
        id_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_barras TEXT UNIQUE,
        nombre_comercial TEXT,
        id_tipo INTEGER,
        id_presentacion INTEGER,
        precio REAL,
        FOREIGN KEY (id_tipo) REFERENCES tipos_medicamento(id_tipo),
        FOREIGN KEY (id_presentacion) REFERENCES presentaciones(id_presentacion)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sustancias (
        id_sustancia INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_sustancia TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicamento_sustancia (
        id_medicamento INTEGER,
        id_sustancia INTEGER,
        concentracion TEXT,
        PRIMARY KEY (id_medicamento, id_sustancia),
        FOREIGN KEY (id_medicamento) REFERENCES medicamentos(id_medicamento),
        FOREIGN KEY (id_sustancia) REFERENCES sustancias(id_sustancia)
    )''')

    cursor.execute("SELECT COUNT(*) FROM tipos_medicamento")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO tipos_medicamento (nombre_tipo) VALUES (?)", [('Antibiótico',), ('Genérico',), ('Patente',)])

    cursor.execute("SELECT COUNT(*) FROM presentaciones")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO presentaciones (nombre_presentacion) VALUES (?)", [('Tableta',), ('Cápsula',), ('Suspensión',), ('Inyectable',)])

    conn.commit()
    conn.close()

crear_base()
