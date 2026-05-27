import streamlit as st
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard SEN - Chile", layout="wide")
st.title("⚡ Matriz Energética: Sistema Eléctrico Nacional (SEN)")
st.markdown("Análisis interactivo de la infraestructura de generación eléctrica en Chile, basado en datos de la Comisión Nacional de Energía.")

@st.cache_data
def obtener_datos_energia():
    url_base = "https://datos.gob.cl/api/3/action/datastore_search"
    
    parametros = {
        "resource_id": "379f068d-5539-47c0-bc36-2b8ba522a77f",
        "limit": 1000
    }
    
    try:
        response = requests.get(url_base, params=parametros)
        response.raise_for_status() 
        
        datos_json = response.json()
        registros = datos_json['result']['records']
        df = pd.DataFrame(registros)
        return df
        
    except Exception as e:
        st.error(f"Error de conexión con la API: {e}")
        return pd.DataFrame()


df = obtener_datos_energia()


if not df.empty:
    
    columnas_disponibles = [col.lower() for col in df.columns]
    df.columns = columnas_disponibles

    
    st.sidebar.header("⚙️ Panel de Control")
    st.sidebar.write("Filtra los componentes de la red:")
    
    if 'tecnologia' in df.columns:
        opciones_tec = ["Todas"] + list(df['tecnologia'].unique())
        tec_seleccionada = st.sidebar.selectbox("Tipo de Tecnología:", opciones_tec)
        
        if tec_seleccionada != "Todas":
            df = df[df['tecnologia'] == tec_seleccionada]
            
    if 'region' in df.columns:
        opciones_reg = ["Todas"] + list(df['region'].unique())
        reg_seleccionada = st.sidebar.selectbox("Macro Zona / Región:", opciones_reg)
        
        if reg_seleccionada != "Todas":
            df = df[df['region'] == reg_seleccionada]

    st.subheader("Resumen de Infraestructura")
    if 'potencia_neta_mw' in df.columns:
        df['potencia_neta_mw'] = pd.to_numeric(df['potencia_neta_mw'], errors='coerce')
        capacidad_total = df['potencia_neta_mw'].sum()
        total_centrales = len(df)
        
        col1, col2 = st.columns(2)
        col1.metric("Total Centrales Operativas", total_centrales)
        col2.metric("Capacidad Neta Instalada (MW)", f"{capacidad_total:,.2f}")

    col_tabla, col_grafico = st.columns(2)
    
    with col_tabla:
        st.write("**Datos Crudos (DataFrame)**")
        st.dataframe(df.head(15), use_container_width=True)
        
    with col_grafico:
        st.write("**Distribución por Tecnología**")
        if 'tecnologia' in df.columns and 'potencia_neta_mw' in df.columns:
            
            datos_grafico = df.groupby('tecnologia')['potencia_neta_mw'].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            datos_grafico.plot(kind='bar', color='#4CAF50', ax=ax)
            ax.set_title("Potencia por Tecnología (MW)")
            ax.set_ylabel("MW")
            ax.set_xlabel("Tecnología")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
        else:
            st.info("No se encontraron las columnas necesarias para el gráfico.")
            
else:
    st.warning("Esperando conexión con la API de datos.gob.cl...")