"""
Utilidades para análisis de servicios de hotel
"""
import pandas as pd
import os
import unicodedata
import re
from datetime import datetime

def normalizar_texto(texto):
    """
    Convierte a minúsculas, quita espacios extremos, elimina tildes y caracteres especiales.
    Ej: 'Habitación' -> 'habitacion', 'Núm. de reserva' -> 'num de reserva'
    """
    texto = texto.strip().lower()
    # Eliminar tildes y diéresis, conservando ñ (luego cambiamos ñ -> n)
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    # Quitar caracteres no alfanuméricos (excepto espacios y letras) -> reemplazar puntos, etc.
    texto = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in texto)
    # Reemplazar múltiples espacios por uno solo
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# Columnas esperadas en el formato original (antes de normalizar se aplicará la normalización)
COLUMNAS_ESPERADAS_ORIGINAL = [
    'usuario', 'fecha y hora', 'fecha del servicio',
    'habitacion', 'nombre', 'apellido', 'num de reserva',
    'codigo', 'codigo de la transaccion', 'descripcion',
    'check-in', 'check-out', 'estado', 'nota', 'cant.', 'debito', 'credito'
]

# Normalizamos la lista una sola vez
COLUMNAS_ESPERADAS = [normalizar_texto(c) for c in COLUMNAS_ESPERADAS_ORIGINAL]

def load_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        # Aplicar normalización a los nombres de columna
        df.columns = [normalizar_texto(col) for col in df.columns]
        return df, None
    except Exception as e:
        return None, str(e)

def validate_dataset(df):
    """Verifica que todas las columnas esperadas existan después de normalizadas"""
    columnas_df = [normalizar_texto(c) for c in df.columns]
    faltantes = [c for c in COLUMNAS_ESPERADAS if c not in columnas_df]
    if faltantes:
        return False, f"Faltan columnas: {', '.join(faltantes)}"
    return True, "OK"

def prepare_data(df):
    """Asegura tipos de datos y agrega columna 'neto' (débito - crédito)"""
    # Convertir débito y crédito a numérico, llenar vacíos con 0
    df['debito'] = pd.to_numeric(df['debito'], errors='coerce').fillna(0)
    df['credito'] = pd.to_numeric(df['credito'], errors='coerce').fillna(0)
    df['neto'] = df['debito'] - df['credito']
    
    # Convertir fechas especificando dayfirst=True para formato dd/mm/yyyy
    columnas_fecha = ['fecha y hora', 'fecha del servicio', 'check-in', 'check-out']
    for col in columnas_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
    
    # Crear columna 'huesped' combinando nombre y apellido
    if 'nombre' in df.columns and 'apellido' in df.columns:
        df['huesped'] = df['nombre'].fillna('') + ' ' + df['apellido'].fillna('')
        df['huesped'] = df['huesped'].str.strip()
    
    return df

def get_column_types(df):
    """Devuelve diccionario con listas de columnas numéricas, texto y fechas"""
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    return {'numericas': num_cols, 'texto': text_cols, 'fechas': date_cols}

def format_currency(value):
    """Formatea un número como moneda"""
    return f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)
