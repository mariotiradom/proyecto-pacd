# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 22:59:02 2025

@author: user
"""

import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import gmean

# === Cargar bases ===
def load_data(file_path):
    try:
        data = pd.read_excel(file_path, header=3)
        return data
    except Exception as e:
        print(f"Error al cargar la data de {file_path}: {e}")
        return None

# Cargar los datasets
siniestros_path = r"D:\PROGRA AVANZADA\PROYECTO FINAL\Base de datos original\BBDD ONSV - SINIESTROS 2021-2023.xlsx"  # modificar segÃºn sea necesario
vehiculos_path = r"D:\PROGRA AVANZADA\PROYECTO FINAL\Base de datos original\BBDD ONSV - VEHICULOS 2021-2023.xlsx"  # modificar segÃºn sea necesario

siniestros = load_data(siniestros_path)
vehiculos = load_data(vehiculos_path)

# === Limpiar y unir ===
siniestros = siniestros[['CÓDIGO SINIESTRO', 'CLASE SINIESTRO', 'SUPERFICIE DE CALZADA', 'DEPARTAMENTO']]
vehiculos = vehiculos[['CÓDIGO SINIESTRO', 'AÑO']]
vehiculos_siniestros = pd.merge(siniestros, vehiculos, on='CÓDIGO SINIESTRO', how='inner')







# === AGRUPACIÓN de categorías poco frecuentes ===

def limpiar_categorias(df):
    # Agrupar superficies poco frecuentes
    superficies_a_agrupar = ['CASCAJO/RIPIO', 'CONCRETO']
    df['SUPERFICIE DE CALZADA'] = df['SUPERFICIE DE CALZADA'].replace(superficies_a_agrupar, 'OTROS')

    # Agrupar tipos de siniestro poco frecuentes
    siniestros_a_agrupar = ['ESPECIAL', 'VOLCADURA']
    df['CLASE SINIESTRO'] = df['CLASE SINIESTRO'].replace(siniestros_a_agrupar, 'OTROS')

    return df

# Aplicar la función tanto a siniestros como a la base unificada
siniestros = limpiar_categorias(siniestros)
vehiculos_siniestros = limpiar_categorias(vehiculos_siniestros)






# === MAPA DE CALOR POR DEPARTAMENTO ===
def mapa_calor(departamento, nombre_html):
    df = siniestros[siniestros['DEPARTAMENTO'].str.upper() == departamento.upper()]

    #Agrupacion solo para Lima
    if departamento.upper() == 'LIMA':
        df['SUPERFICIE DE CALZADA'] = df['SUPERFICIE DE CALZADA'].replace(['CASCAJO/RIPIO', 'CONCRETO', 'EMPEDRADO'], 'OTROS')
        df['CLASE SINIESTRO'] = df['CLASE SINIESTRO'].replace(['ESPECIAL', 'VOLCADURA', 'INCENDIO'], 'OTROS')
    else:
        df['SUPERFICIE DE CALZADA'] = df['SUPERFICIE DE CALZADA'].replace(['CASCAJO/RIPIO', 'CONCRETO'], 'OTROS')
        df['CLASE SINIESTRO'] = df['CLASE SINIESTRO'].replace(['ESPECIAL', 'VOLCADURA'], 'OTROS')





    tabla = pd.crosstab(df['SUPERFICIE DE CALZADA'], df['CLASE SINIESTRO'])

    fig = px.imshow(tabla,
                    labels=dict(x="Tipo de Siniestro", y="Superficie de Calzada", color="Cantidad"),
                    x=tabla.columns,
                    y=tabla.index,
                    title=f"Mapa de Calor: Tipo de Siniestro vs Superficie de Calzada en {departamento.title()}",
                    text_auto=True,
                    color_continuous_scale='YlOrRd')
    fig.update_layout(title_x=0.5)
    fig.write_html(nombre_html)
    fig.show()

mapa_calor("LIMA", "mapa_calor_lima.html")
mapa_calor("LA LIBERTAD", "mapa_calor_lalibertad.html")

# === FUNCIONES DE PROYECCIÓN ===
def tasa_promedio(serie):
    if len(serie) < 3:
        return 0
    tasas = [serie[i] / serie[i-1] for i in range(1, len(serie))]
    media_geom = gmean(tasas)
    return (media_geom - 1) * 100

def valor_final(valor_inicial, tasa_percent, n):
    tasa_decimal = tasa_percent / 100
    return valor_inicial * (1 + tasa_decimal) ** n

def valores_proyecciones(serie):
    tasa = tasa_promedio(serie)
    val_2024 = int(valor_final(serie[-1], tasa, 1))
    val_2025 = int(valor_final(val_2024, tasa, 1))
    val_2026 = int(valor_final(val_2025, tasa, 1))
    return list(serie) + [val_2024, val_2025, val_2026]

# === GRÁFICO DE LÍNEAS INTERACTIVO CON PROYECCIONES ===
def grafico_lineas(departamento, df, nombre_html):
    df = df[df['DEPARTAMENTO'].str.upper() == departamento.upper()]
    df = df.groupby(['CLASE SINIESTRO', 'AÑO']).size().reset_index(name='cantidad')
    
    # Top 2 siniestros
    top_2 = df.groupby('CLASE SINIESTRO')['cantidad'].sum().sort_values(ascending=False).head(2).index.tolist()
    
    serie1 = df[df['CLASE SINIESTRO'] == top_2[0]].sort_values('AÑO')['cantidad'].values
    serie2 = df[df['CLASE SINIESTRO'] == top_2[1]].sort_values('AÑO')['cantidad'].values
    
    eje_y_1 = valores_proyecciones(serie1)
    eje_y_2 = valores_proyecciones(serie2)
    años = ["2021", "2022", "2023", "2024", "2025", "2026"]

    df_proy = pd.DataFrame({
        'Año': años * 2,
        'Cantidad': eje_y_1 + eje_y_2,
        'Tipo': [top_2[0]] * 6 + [top_2[1]] * 6
    })

    fig = px.line(df_proy, x='Año', y='Cantidad', color='Tipo',
                  title=f"Proyección: Tipos de siniestro más frecuentes en {departamento.title()}",
                  markers=True,
                  color_discrete_sequence=['#FF5733', '#1F77B4'])

    fig.update_layout(title_x=0.5, hovermode='x unified')
    fig.write_html(nombre_html)
    fig.show()

grafico_lineas("LIMA", vehiculos_siniestros, "proyeccion_lima.html")
grafico_lineas("LA LIBERTAD", vehiculos_siniestros, "proyeccion_lalibertad.html")
