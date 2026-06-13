import streamlit as st
import pandas as pd
import os

# Configuración de la página con el título de JOMACO
st.set_page_config(page_title="Registro de citaciones JOMACO", page_icon="📝", layout="wide")
st.title("📝 Registro de citaciones JOMACO")

LISTA_OFICIAL_CSV = "estudiantes.csv"
ARCHIVO_SALIDA_EXCEL = "datos_citaciones.xlsx"

@st.cache_data
def cargar_estudiantes():
    if os.path.exists(LISTA_OFICIAL_CSV):
        return pd.read_csv(LISTA_OFICIAL_CSV, encoding='utf-8', sep=';')
    return None

df_estudiantes = cargar_estudiantes()

if 'lista_estudiantes' not in st.session_state:
    st.session_state.lista_estudiantes = []
if 'contador_limpieza' not in st.session_state:
    st.session_state.contador_limpieza = 0

# --- DISEÑO EN DOS GRANDES COLUMNAS ---
col_formulario, col_revision = st.columns([1.2, 1])

with col_formulario:
    st.subheader("1. Llenar Datos de Citación")
    
    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        if df_estudiantes is not None:
            lista_grupos = sorted(df_estudiantes['Grupo'].unique().astype(str))
            grupo = st.selectbox("Grupo:", ["--"] + lista_grupos, key="sel_grupo")
        else:
            st.error("⚠️ No se encontró 'estudiantes.csv'")
            grupo = st.text_input("Grupo:")
            
    with st.form("formulario_citacion", clear_on_submit=False):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nombre_docente = st.text_input("Nombre del Docente:", key="txt_docente")
        with col_f2:
            asignatura = st.text_input("Asignatura:")
            
        motivo = st.selectbox("Motivo principal:", ["Bajo Rendimiento Académico", "Comportamiento / Disciplinario", "Académico y Disciplinario"])

        st.markdown("**2. Selección de Alumnos**")
        if df_estudiantes is not None and grupo != "--":
            estudiantes_filtrados = df_estudiantes[df_estudiantes['Grupo'].astype(str) == grupo]['Nombre'].tolist()
            estudiantes_seleccionados = st.multiselect(
                f"Alumnos de {grupo}:", 
                sorted(estudiantes_filtrados),
                key=f"items_estudiantes_{st.session_state.contador_limpieza}"
            )
        else:
            st.info("💡 Seleccione un grupo arriba para activar este listado.")
            estudiantes_seleccionados = []

        boton_agregar = st.form_submit_button("➕ Agregar a la Lista Inferior", use_container_width=True)

        if boton_agregar:
            if nombre_docente and grupo != "--" and asignatura and estudiantes_seleccionados:
                for estudiante in estudiantes_seleccionados:
                    nuevo_registro = {
                        "Docente": nombre_docente,
                        "Grupo": grupo,
                        "Asignatura": asignatura,
                        "Estudiante": estudiante,
                        "Motivo": motivo
                    }
                    st.session_state.lista_estudiantes.append(nuevo_registro)
                
                st.toast(f"✅ Se agregaron {len(estudiantes_seleccionados)} estudiantes.")
                st.session_state.contador_limpieza += 1
                st.rerun()
            else:
                st.error("Por favor, rellene todos los campos del formulario.")

# --- COLUMNA DERECHA: REVISIÓN Y DESCARGA ---
with col_revision:
    st.subheader("2. Estudiantes en Espera")
    
    if st.session_state.lista_estudiantes:
        df_temporal = pd.DataFrame(st.session_state.lista_estudiantes)
        st.dataframe(df_temporal[["Grupo", "Estudiante", "Motivo"]], use_container_width=True, hide_index=True)
        
        c_b1, c_b2 = st.columns(2)
        with c_b1:
            if st.button("🗑️ Limpiar Todo", use_container_width=True):
                st.session_state.lista_estudiantes = []
                st.rerun()
        with c_b2:
            btn_guardar = st.button("💾 Guardar en Excel", type="primary", use_container_width=True)
            
        if btn_guardar:
            df_nuevos = pd.DataFrame(st.session_state.lista_estudiantes)
            if os.path.exists(ARCHIVO_SALIDA_EXCEL):
                df_existente = pd.read_excel(ARCHIVO_SALIDA_EXCEL)
                df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
            else:
                df_final = df_nuevos
            df_final.to_excel(ARCHIVO_SALIDA_EXCEL, index=False)
            st.success("🎉 ¡Registros guardados con éxito!")
            st.balloons()
            st.session_state.lista_estudiantes = []
            st.rerun()
    else:
        st.info("No hay estudiantes pendientes por guardar en este bloque.")

    # --- NUEVA ZONA DE DESCARGA SEGURA (Se ve abajo a la derecha) ---
    if os.path.exists(ARCHIVO_SALIDA_EXCEL):
        st.markdown("---")
        st.markdown("### 📥 Zona de Administración (Descargas)")
        try:
            with open(ARCHIVO_SALIDA_EXCEL, "rb") as f:
                st.download_button(
                    label="📊 Descargar Archivo Excel Consolidado",
                    data=f,
                    file_name="citaciones_JOMACO_consolidado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        except Exception as e:
            st.warning("El archivo se está actualizando, espere un momento.")