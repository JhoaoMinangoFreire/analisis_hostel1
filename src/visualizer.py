"""
Visualizaciones para el análisis hotelero
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class HotelCharts:
    def __init__(self, df):
        self.df = df

    def ranking_barras(self, data, x, y, title="Ranking"):
        """Gráfico de barras horizontales para rankings"""
        fig = px.bar(data, x=x, y=y, orientation='h', title=title,
                     color_discrete_sequence=['#1f77b4'])
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
        return fig

    def barras_conceptos(self, data, x, y, title="Débito por Descripción"):
        fig = px.bar(data, x=x, y=y, title=title, color_discrete_sequence=['#2ca02c'])
        fig.update_layout(xaxis_tickangle=-45, height=400)
        return fig

    def pie_conceptos(self, names, values, title="Distribución de Débito"):
        """Gráfico de torta usando listas/arrays, sin depender de self.df"""
        temp_df = pd.DataFrame({'names': names, 'values': values})
        fig = px.pie(temp_df, names='names', values='values', title=title)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        return fig

    def linea_tiempo(self, data, x, y, title="Evolución del Débito"):
        """Gráfico de línea para series temporales"""
        fig = px.line(data, x=x, y=y, markers=True, title=title,
                      line_shape='linear', color_discrete_sequence=['#1f77b4'])
        fig.update_traces(marker=dict(size=8))
        fig.update_layout(
            xaxis_title='Fecha',
            yaxis_title='Débito ($)',
            hovermode='x unified'
        )
        return fig

    def lineas_multiples(self, data, x, y, color, title="Evolución por Grupo"):
        """Gráfico de líneas múltiples coloreado por grupo"""
        fig = px.line(data, x=x, y=y, color=color, markers=True, title=title,
                      color_discrete_sequence=px.colors.qualitative.Set1)
        fig.update_traces(marker=dict(size=6))
        fig.update_layout(
            xaxis_title='Fecha',
            yaxis_title='Débito ($)',
            hovermode='x unified'
        )
        return fig
