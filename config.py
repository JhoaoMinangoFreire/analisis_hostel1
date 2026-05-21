"""
Configuraciones globales de la aplicación
"""

# Configuración de la app
APP_NAME = "Analizador de Desempeño"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Analiza archivos Excel y genera informes de desempeño"

# Tipos de archivo permitidos
ALLOWED_EXTENSIONS = ['xlsx', 'xls']

# Configuración de gráficos
CHART_COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ffbb78'
}

# Configuración de exportación
EXPORT_FORMATS = ['Excel', 'PDF', 'CSV']

# Mensajes
MESSAGES = {
    'no_file': '❌ Por favor, carga un archivo Excel',
    'no_data': '⚠️ No se encontraron datos para analizar',
    'success': '✅ Análisis completado exitosamente',
    'error': '❌ Ocurrió un error durante el análisis'
}