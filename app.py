import os
import base64
import platform
import traceback
import streamlit as st
from PIL import Image
from openai import OpenAI

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y DISEÑO NUTRICIONAL
# ==========================================
st.set_page_config(
    page_title="NutriVision AI | Análisis Nutricional Inteligente",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS orientados a un entorno saludable, limpio y moderno (Tonos verdes y blancos)
st.markdown("""
<style>
    .main { padding: 1.5rem 2.5rem; }
    
    .nutri-banner {
        background: linear-gradient(135deg, #064E3B 0%, #065F46 50%, #047857 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: #FFFFFF;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(6, 95, 70, 0.2);
    }
    
    .nutri-banner h1 {
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.4rem;
    }
    
    .nutri-banner p {
        color: #D1FAE5;
        font-size: 1.05rem;
        margin: 0;
    }

    .stButton>button {
        background: linear-gradient(90deg, #059669 0%, #10B981 100%);
        color: white !important;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        border: none;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        opacity: 0.95;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }
</style>
""", unsafe_allow_html=True)

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# ==========================================
# BARRA LATERAL: CONTROL Y CREDENCIALES
# ==========================================
with st.sidebar:
    st.markdown("## 🥗 NutriVision AI")
    st.caption("Asistente experto en análisis de etiquetas nutricionales, platos preparados y conteo calórico visual.")
    
    st.markdown("---")

    st.subheader("🔑 Paso 1: Autenticación")
    ke = st.text_input(
        "Clave API de OpenAI", 
        type="password",
        placeholder="sk-...",
        help="Tu API Key es requerida para el análisis visual de alimentos y etiquetas."
    )
    
    if ke:
        os.environ['OPENAI_API_KEY'] = ke
        st.success("API Key vinculada correctamente")
    else:
        st.warning("Ingresa tu API Key para habilitar la plataforma.")

    st.markdown("---")
    st.caption(f"Entorno: Python v{platform.python_version()} | GPT-4o Vision Engine")

# ==========================================
# ENCABEZADO Y PASOS CONDUCTUALES
# ==========================================
st.markdown("""
<div class="nutri-banner">
    <h1>Análisis Nutricional & Etiquetas por Imagen 🥗</h1>
    <p>Sube la foto de un plato de comida o la tabla nutricional de un producto para evaluar calorías, macros, alérgenos y calidad de ingredientes.</p>
</div>
""", unsafe_allow_html=True)

api_key = os.environ.get('OPENAI_API_KEY', '')

col_upload, col_analysis = st.columns([1, 1.2])

with col_upload:
    st.subheader("📸 Paso 2: Cargar Foto de Alimento / Etiqueta")
    uploaded_file = st.file_uploader(
        "Sube un archivo de imagen (PNG, JPG, JPEG)",
        type=["jpg", "png", "jpeg"],
        help="Sube la foto del plato o etiqueta nutricional que deseas analizar."
    )

    if uploaded_file:
        with st.expander("👁️ Previsualización de la Imagen", expanded=True):
            st.image(uploaded_file, caption=f"Archivo: {uploaded_file.name}", width=350)

with col_analysis:
    st.subheader("💬 Paso 3: Definir Enfoque Nutricional")
    
    if "preset_query" not in st.session_state:
        st.session_state.preset_query = ""

    st.write("*Atajos Rápidos:*")
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("⚖️ Conteo de Macros y Calorías"):
            st.session_state.preset_query = "Estima las calorías aproximadas, proteínas, carbohidratos y grasas saludables de este plato o producto."
        if st.button("🚨 Alérgenos e Ingredientes Ocultos"):
            st.session_state.preset_query = "Analiza los ingredientes o la etiqueta en busca de azúcares añadidos, ultraprocesados o alérgenos comunes."

    with btn_col2:
        if st.button("💪 Apto para Dieta Fitness"):
            st.session_state.preset_query = "Evalúa si este alimento es adecuado para una dieta orientada a ganancia muscular o pérdida de grasa."
        if st.button("📋 Calidad Nutricional General"):
            st.session_state.preset_query = "¿Qué tan saludable es este producto o preparación y qué alternativas o mejoras sugieres?"

    with st.form(key="nutri_vision_form"):
        user_query = st.text_area(
            "Pregunta o instrucción nutricional:",
            value=st.session_state.preset_query,
            placeholder="Ejemplo: Analiza la etiqueta de este producto y dime si es saludable para consumo diario...",
            height=110
        )
        
        submit_button = st.form_submit_button(label="🚀 Ejecutar Análisis Nutricional")

# ==========================================
# PROCESAMIENTO Y EJECUCIÓN VISION
# ==========================================
if submit_button:
    if not api_key:
        st.error("⚠️ Por favor ingresa tu API Key de OpenAI en el panel lateral antes de continuar.")
    elif not uploaded_file:
        st.error("⚠️ Por favor carga una imagen en el Paso 2 antes de iniciar el análisis.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            with st.spinner("Analizando composición nutricional y calidad de ingredientes..."):
                base64_image = encode_image(uploaded_file)
                
                prompt_instrucciones = (
                    "Eres un nutricionista clínico y experto en seguridad alimentaria. "
                    "Analiza la siguiente imagen de comida o etiqueta nutricional en español. "
                    "Proporciona respuestas claras, estructuradas con viñetas y orientadas al bienestar y salud del usuario.\n\n"
                )
                
                if user_query.strip():
                    prompt_instrucciones += f"Consulta específica del usuario:\n{user_query}"
                else:
                    prompt_instrucciones += "Realiza una evaluación nutricional general analizando: Estimación calórica/macros principales, calidad de ingredientes y recomendaciones de consumo."

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_instrucciones},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ],
                    }
                ]

                st.markdown("---")
                st.subheader("📋 Reporte Nutricional Inteligente")
                
                message_placeholder = st.empty()
                full_response = ""

                for completion in client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=1000,
                    stream=True
                ):
                    if completion.choices[0].delta.content is not None:
                        full_response += completion.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.info(full_response)

        except Exception as e:
            st.error("Ocurrió un inconveniente al procesar la imagen.")
            with st.expander("Ver detalle técnico del error"):
                st.code(traceback.format_exc())
