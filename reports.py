"""
Generación de informes Excel con las tablas del dashboard
"""
import pandas as pd
from datetime import datetime
import io

def generate_excel(tables, filters=None):
    """
    Genera un archivo Excel a partir de las mismas tablas mostradas en la app.
    'tables' debe ser un diccionario con:
        - 'indicadores': DataFrame de indicadores generales
        - 'ranking': DataFrame de ranking de usuarios
        - 'descripciones': DataFrame de descripciones más frecuentes (con Total D+C)
        - 'evolucion': DataFrame de evolución diaria (periodo, debito, credito, Total)
        - 'detalle': pivote usuario x descripción (opcional)
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        money_fmt = workbook.add_format({'num_format': '$#,##0.00'})
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white'})

        # 1. Hoja de Indicadores Generales
        indicadores = tables.get('indicadores')
        if indicadores is not None:
            indicadores.to_excel(writer, sheet_name='Indicadores Generales', index=False)
            ws = writer.sheets['Indicadores Generales']
            ws.set_column('A:A', 25)
            ws.set_column('B:B', 15)
            # Formatear filas de dinero (primeras 3)
            for i, val in enumerate(indicadores['Valor']):
                if i < 3:
                    ws.write(i+1, 1, val, money_fmt)

        # 2. Ranking de Usuarios
        ranking = tables.get('ranking')
        if ranking is not None:
            ranking.to_excel(writer, sheet_name='Ranking Usuarios', index=False)
            ws = writer.sheets['Ranking Usuarios']
            ws.set_column('A:A', 20)
            ws.set_column('B:B', 15)
            for row in range(1, len(ranking)+1):
                ws.write(row, 1, ranking.iloc[row-1]['debito'], money_fmt)

        # 3. Descripciones más frecuentes
        desc = tables.get('descripciones')
        if desc is not None:
            desc.to_excel(writer, sheet_name='Descripciones', index=False)
            ws = writer.sheets['Descripciones']
            ws.set_column('A:A', 30)
            ws.set_column('B:B', 12)
            ws.set_column('C:C', 15)
            # Columna 'Total (D+C)' es la tercera
            for row in range(1, len(desc)+1):
                ws.write(row, 2, desc.iloc[row-1]['Total (D+C)'], money_fmt)

        # 4. Evolución Diaria
        evol = tables.get('evolucion')
        if evol is not None:
            evol.to_excel(writer, sheet_name='Evolución Diaria', index=False)
            ws = writer.sheets['Evolución Diaria']
            ws.set_column('A:A', 12)
            ws.set_column('B:D', 15)
            for row in range(1, len(evol)+1):
                ws.write(row, 1, evol.iloc[row-1]['debito'], money_fmt)
                ws.write(row, 2, evol.iloc[row-1]['credito'], money_fmt)
                if 'Total (D+C)' in evol.columns:
                    ws.write(row, 3, evol.iloc[row-1]['Total (D+C)'], money_fmt)

        # 5. Detalle Usuario x Descripción (opcional)
        detalle = tables.get('detalle')
        if detalle is not None:
            detalle.to_excel(writer, sheet_name='Detalle Usuario x Desc')
            ws = writer.sheets['Detalle Usuario x Desc']
            ws.set_column('A:A', 20)
            # El resto de columnas (descripciones) pueden ser muchas, dar formato
            for col in range(1, len(detalle.columns)+1):
                ws.set_column(col, col, 15)  # ancho base
            # Aplicar formato de dinero a todas las celdas de datos
            for row in range(1, len(detalle)+1):
                for col in range(1, len(detalle.columns)+1):
                    ws.write(row, col, detalle.iloc[row-1, col-1], money_fmt)

        # 6. Filtros aplicados (si existen)
        if filters:
            filtros_df = pd.DataFrame(list(filters.items()), columns=['Filtro', 'Valor'])
            filtros_df.to_excel(writer, sheet_name='Filtros', index=False)

    output.seek(0)
    return output.getvalue()