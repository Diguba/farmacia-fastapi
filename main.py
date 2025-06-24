# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_connection():
    return sqlite3.connect("farmacia.db")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT m.id_medicamento, m.nombre_comercial, m.codigo_barras, m.precio, 
           t.nombre_tipo, p.nombre_presentacion,
           (SELECT GROUP_CONCAT(s.nombre_sustancia || ' (' || ms.concentracion || ')', ', ')
            FROM medicamento_sustancia ms
            JOIN sustancias s ON ms.id_sustancia = s.id_sustancia
            WHERE ms.id_medicamento = m.id_medicamento)
    FROM medicamentos m
    JOIN tipos_medicamento t ON m.id_tipo = t.id_tipo
    JOIN presentaciones p ON m.id_presentacion = p.id_presentacion
    ORDER BY 
        CASE t.nombre_tipo
            WHEN 'Antibiótico' THEN 1
            WHEN 'Genérico' THEN 2
            WHEN 'Patente' THEN 3
            ELSE 4
        END,
        m.nombre_comercial ASC
    ''')
    medicamentos = cursor.fetchall()

    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "medicamentos": medicamentos})

@app.post("/agregar")
def agregar(
    id_medicamento: int = Form(None),
    nombre: str = Form(...),
    codigo: str = Form(...),
    tipo: int = Form(...),
    presentacion: int = Form(...),
    precio: float = Form(...),
    sustancia1: str = Form(...),
    concentracion1: str = Form(...),
    sustancia2: str = Form(None),
    concentracion2: str = Form(None),
):
    conn = get_connection()
    cursor = conn.cursor()

    if id_medicamento:
        # Actualizar medicamento
        cursor.execute("UPDATE medicamentos SET nombre_comercial=?, codigo_barras=?, id_tipo=?, id_presentacion=?, precio=? WHERE id_medicamento=?",
                       (nombre, codigo, tipo, presentacion, precio, id_medicamento))
        cursor.execute("DELETE FROM medicamento_sustancia WHERE id_medicamento=?", (id_medicamento,))
    else:
        cursor.execute("INSERT INTO medicamentos (nombre_comercial, codigo_barras, id_tipo, id_presentacion, precio) VALUES (?, ?, ?, ?, ?)",
                       (nombre, codigo, tipo, presentacion, precio))
        id_medicamento = cursor.lastrowid

    for sustancia, concentracion in [(sustancia1, concentracion1), (sustancia2, concentracion2)]:
        if sustancia and concentracion:
            cursor.execute("SELECT id_sustancia FROM sustancias WHERE nombre_sustancia = ?", (sustancia,))
            result = cursor.fetchone()
            if result:
                id_sustancia = result[0]
            else:
                cursor.execute("INSERT INTO sustancias (nombre_sustancia) VALUES (?)", (sustancia,))
                id_sustancia = cursor.lastrowid
            cursor.execute("INSERT INTO medicamento_sustancia (id_medicamento, id_sustancia, concentracion) VALUES (?, ?, ?)",
                           (id_medicamento, id_sustancia, concentracion))

    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)

@app.get("/borrar/{id_medicamento}")
def borrar(id_medicamento: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicamento_sustancia WHERE id_medicamento=?", (id_medicamento,))
    cursor.execute("DELETE FROM medicamentos WHERE id_medicamento=?", (id_medicamento,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)
@app.get("/api/medicamento/{id}")
def obtener_medicamento(id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id_medicamento, m.nombre_comercial, m.codigo_barras, m.precio,
               m.id_tipo, m.id_presentacion,
               group_concat(s.nombre_sustancia, '|'),
               group_concat(ms.concentracion, '|')
        FROM medicamentos m
        LEFT JOIN medicamento_sustancia ms ON m.id_medicamento = ms.id_medicamento
        LEFT JOIN sustancias s ON ms.id_sustancia = s.id_sustancia
        WHERE m.id_medicamento = ?
        GROUP BY m.id_medicamento
    """, (id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        sustancias = row[6].split('|') if row[6] else []
        concentraciones = row[7].split('|') if row[7] else []
        return {
            "id": row[0],
            "nombre": row[1],
            "codigo": row[2],
            "precio": row[3],
            "tipo": row[4],
            "presentacion": row[5],
            "sustancias": sustancias,
            "concentraciones": concentraciones
        }
    return {"error": "No encontrado"}
from difflib import get_close_matches

@app.get("/api/sugerencias")
def sugerencias(q: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_comercial FROM medicamentos")
    todos = [row[0] for row in cursor.fetchall()]
    conn.close()

    q_lower = q.lower()
    sugeridos = [n for n in todos if q_lower in n.lower()]
    
    respuesta = {
        "coincidencias": sugeridos
    }

    if not sugeridos:
        cercanos = get_close_matches(q, todos, n=1, cutoff=0.5)
        if cercanos:
            respuesta["sugerencia"] = f"¿Quisiste decir: {cercanos[0]}?"
    return respuesta
