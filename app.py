import streamlit as st
import numpy as np
import pandas as pd
import sqlite3

# 🔌 Conexión a la base de datos SQLite
def create_connection():
    return sqlite3.connect("numpystreamlit.db")

# 🧱 Inicializar tablas si no existen
def initialize_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vectores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jovenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombres TEXT,
            apellidos TEXT,
            edad INTEGER,
            notas REAL,
            materias TEXT
        )
    """)
    conn.commit()
    conn.close()

initialize_database()

# 🧠 CRUD para vectores
def insert_vector(val):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vectores (valor) VALUES (?)", (float(val),))
    conn.commit()
    conn.close()

# 🧠 CRUD para jóvenes
def insert_joven(nombre, apellido, edad, nota, materia):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO jovenes (nombres, apellidos, edad, notas, materias) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(query, (nombre, apellido, edad, nota, materia))
    conn.commit()
    conn.close()

def get_jovenes():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM jovenes", conn)
    conn.close()
    return df

def update_joven(id, nombre, apellido, edad, nota, materia):
    conn = create_connection()
    cursor = conn.cursor()
    query = "UPDATE jovenes SET nombres=?, apellidos=?, edad=?, notas=?, materias=? WHERE id=?"
    cursor.execute(query, (nombre, apellido, edad, nota, materia, id))
    conn.commit()
    conn.close()

def delete_joven(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jovenes WHERE id=?", (id,))
    conn.commit()
    conn.close()

# 🧮 Título principal
st.title("🧠 Proyecto Educativo con NumPy, Streamlit y SQLite")

# 📌 Ejercicio 1
st.header("Ejercicio 1: Estadísticas de un array del 1 al 100")
array = np.arange(1, 101)
st.write("Array:", array)
st.write("Media:", np.mean(array))
st.write("Mediana:", np.median(array))
st.write("Varianza:", np.var(array))
st.write("Percentil 90:", np.percentile(array, 90))

# 📌 Ejercicio 2
st.header("Ejercicio 2: Matriz aleatoria 5x5")
matriz = np.random.randn(5, 5)
st.write("Matriz generada:", matriz)
st.write("Determinante:", np.linalg.det(matriz))
st.write("Traza:", np.trace(matriz))

# 📌 Ejercicio 3
st.header("Ejercicio 3: Frecuencias de números aleatorios")
datos = np.random.randint(0, 11, 1000)
frecuencias = pd.Series(datos).value_counts().sort_index()
st.write("Tabla de frecuencias:", frecuencias)
st.bar_chart(frecuencias)

# 📌 Ejercicio 4
st.header("Ejercicio 4: Normalización de vector")
modo = st.radio("Selecciona cómo generar el vector:", ["Manual", "Aleatorio"])
if modo == "Manual":
    entrada = st.text_input("Ingresa números separados por coma (ej. 1,2,3,4)")
    if entrada:
        try:
            vector = np.array([float(x) for x in entrada.split(",")])
        except:
            st.error("Formato inválido. Usa solo números separados por coma.")
else:
    vector = np.random.randint(1, 100, 10)
    st.write("Vector generado:", vector)

if 'vector' in locals():
    normalizado = (vector - np.mean(vector)) / np.std(vector)
    st.write("Vector normalizado:", normalizado)

    if st.button("Guardar vector en base de datos"):
        for val in vector:
            insert_vector(val)
        st.success("Vector guardado correctamente.")

# 📋 Sección editable de jóvenes
st.header("📋 Registro de jóvenes del ciclo")

with st.form("form_joven"):
    nombre = st.text_input("Nombre")
    apellido = st.text_input("Apellido")
    edad = st.number_input("Edad", min_value=0, max_value=120)
    nota = st.number_input("Nota", min_value=0.0, max_value=10.0)
    materia = st.text_input("Materia")
    submitted = st.form_submit_button("Insertar")
    if submitted:
        insert_joven(nombre, apellido, edad, nota, materia)
        st.success("Joven insertado correctamente.")

df_jovenes = get_jovenes()
st.subheader("📄 Tabla de jóvenes")
st.dataframe(df_jovenes)

# 🔄 Actualizar o eliminar
st.subheader("✏️ Modificar o eliminar joven")
id_mod = st.number_input("ID del joven", min_value=1)
if st.button("Eliminar"):
    delete_joven(id_mod)
    st.success("Joven eliminado.")

with st.form("form_update"):
    nombre_u = st.text_input("Nuevo nombre")
    apellido_u = st.text_input("Nuevo apellido")
    edad_u = st.number_input("Nueva edad", min_value=0, max_value=120)
    nota_u = st.number_input("Nueva nota", min_value=0.0, max_value=10.0)
    materia_u = st.text_input("Nueva materia")
    actualizar = st.form_submit_button("Actualizar")
    if actualizar:
        update_joven(id_mod, nombre_u, apellido_u, edad_u, nota_u, materia_u)
        st.success("Joven actualizado.")

# 📊 Visualización extra
st.subheader("📊 Gráfico de notas por materia")
if not df_jovenes.empty:
    st.bar_chart(df_jovenes.groupby("materias")["notas"].mean())

st.subheader("📈 Histograma de edades")
if not df_jovenes.empty:
    st.bar_chart(df_jovenes["edad"].value_counts().sort_index())

# 📥 Descargar CSV
csv = df_jovenes.to_csv(index=False).encode('utf-8')
st.download_button("Descargar CSV", data=csv, file_name="registro_jovenes.csv", mime="text/csv")
