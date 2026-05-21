"""
Módulo de análisis para servicios de hotel (nuevo formato)
"""
import pandas as pd
import numpy as np

class HotelAnalyzer:
    def __init__(self, df):
        self.df = df

    def total_debito(self):
        return self.df['debito'].sum()

    def ranking_usuarios_por_debito(self, n=10):
        """Top n usuarios por suma de débito"""
        ranking = self.df.groupby('usuario')['debito'].sum().sort_values(ascending=False).head(n)
        return ranking.reset_index()  # DataFrame con columnas 'usuario' y 'debito'

    def conceptos_mas_frecuentes(self, n=10):
        """Top n descripciones por cantidad de registros (frecuencia)"""
        freq = self.df['descripcion'].value_counts().head(n)
        return freq.reset_index()
        # columnas: 'index' (descripcion), 'descripcion' (count)

    def debito_por_concepto(self):
        """Suma de débito por descripción"""
        return self.df.groupby('descripcion')['debito'].sum().sort_values(ascending=False)

    def debito_por_usuario_y_concepto(self, usuarios=None, conceptos=None):
        """Tabla pivote usuarios x descripción, filtrada opcionalmente"""
        df_f = self.df.copy()
        if usuarios:
            df_f = df_f[df_f['usuario'].isin(usuarios)]
        if conceptos:
            df_f = df_f[df_f['descripcion'].isin(conceptos)]
        pivot = df_f.pivot_table(values='debito', index='usuario', columns='descripcion', aggfunc='sum', fill_value=0)
        return pivot

    def debito_por_tiempo(self, columna_fecha='fecha del servicio', freq='D'):
        """
        Agrupa el débito por período (D=día, W=semana, M=mes)
        Retorna DataFrame con columnas: periodo (fecha) y debito
        """
        df_time = self.df.copy()
        if columna_fecha not in df_time.columns:
            if 'fecha y hora' in df_time.columns:
                columna_fecha = 'fecha y hora'
            else:
                return None
        df_time[columna_fecha] = pd.to_datetime(df_time[columna_fecha])
        grupo = df_time.set_index(columna_fecha).resample(freq)['debito'].sum().reset_index()
        grupo.columns = ['periodo', 'debito']
        return grupo

    def debito_por_tiempo_agrupado(self, columna_fecha='fecha del servicio', freq='D', grupo='usuario'):
        """
        Débito agrupado por tiempo y por una categoría (usuario o descripción).
        Retorna DataFrame con columnas: periodo, grupo, debito
        """
        df_time = self.df.copy()
        if columna_fecha not in df_time.columns:
            if 'fecha y hora' in df_time.columns:
                columna_fecha = 'fecha y hora'
            else:
                return None
        df_time[columna_fecha] = pd.to_datetime(df_time[columna_fecha])
        grupo_df = df_time.groupby([pd.Grouper(key=columna_fecha, freq=freq), grupo])['debito'].sum().reset_index()
        grupo_df.columns = ['periodo', 'grupo', 'debito']
        return grupo_df

    def resumen_usuario(self, usuario):
        """Estadísticas básicas para un usuario específico"""
        u_data = self.df[self.df['usuario'] == usuario]
        return {
            'total_debito': u_data['debito'].sum(),
            'num_servicios': len(u_data),
            'conceptos_unicos': u_data['descripcion'].nunique(),
            'concepto_top': u_data.groupby('descripcion')['debito'].sum().idxmax() if len(u_data)>0 else None
        }

    def credito_por_tiempo(self, columna_fecha='fecha del servicio', freq='D'):
        """Agrupa el crédito por período (D=día, W=semana, M=mes)"""
        df_time = self.df.copy()
        if columna_fecha not in df_time.columns:
            if 'fecha y hora' in df_time.columns:
                columna_fecha = 'fecha y hora'
            else:
                return None
        df_time[columna_fecha] = pd.to_datetime(df_time[columna_fecha])
        grupo = df_time.set_index(columna_fecha).resample(freq)['credito'].sum().reset_index()
        grupo.columns = ['periodo', 'credito']
        return grupo

    def neto_por_tiempo(self, columna_fecha='fecha del servicio', freq='D'):
        """Agrupa el neto (débito - crédito) por período"""
        df_time = self.df.copy()
        if columna_fecha not in df_time.columns:
            if 'fecha y hora' in df_time.columns:
                columna_fecha = 'fecha y hora'
            else:
                return None
        df_time[columna_fecha] = pd.to_datetime(df_time[columna_fecha])
        grupo = df_time.set_index(columna_fecha).resample(freq)['neto'].sum().reset_index()
        grupo.columns = ['periodo', 'neto']
        return grupo

    def total_por_tiempo(self, columna_fecha='fecha del servicio', freq='D'):
        """Agrupa la suma de débito + crédito (ambos positivos) por período"""
        df_time = self.df.copy()
        # Determinar la columna de fecha a usar
        if columna_fecha not in df_time.columns:
            if 'fecha y hora' in df_time.columns:
                columna_fecha = 'fecha y hora'
            else:
                return None
        df_time[columna_fecha] = pd.to_datetime(df_time[columna_fecha])
        df_time['total'] = df_time['debito'] + df_time['credito']
        grupo = df_time.set_index(columna_fecha).resample(freq)['total'].sum().reset_index()
        grupo.columns = ['periodo', 'total']
        return grupo

    def total_por_tiempo_usuario(self, freq='D'):
        """
        Agrupa el total (débito + crédito) por período y por usuario.
        Retorna DataFrame con columnas: periodo, usuario, total
        """
        df_time = self.df.copy()
        columna_fecha = 'fecha del servicio'
        if columna_fecha not in df_time.columns:
            if 'fecha y hora' in df_time.columns:
                columna_fecha = 'fecha y hora'
            else:
                return None
        df_time[columna_fecha] = pd.to_datetime(df_time[columna_fecha])
        # Sumar débito y crédito por grupo
        grupo = df_time.groupby([pd.Grouper(key=columna_fecha, freq=freq), 'usuario']).apply(
            lambda x: x['debito'].sum() + x['credito'].sum()
        ).reset_index(name='total')
        # Renombrar la columna de fecha a 'periodo' para consistencia
        grupo.rename(columns={columna_fecha: 'periodo'}, inplace=True)
        return grupo