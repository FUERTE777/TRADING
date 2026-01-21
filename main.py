importar sistema operativo
importar asyncio
import pandas as pd # Importante para cálculos de Medias Móviles
importar numpy como np
desde metaapi_cloud_sdk importar MetaApi
desde supabase importar create_client, Cliente
importar google.generativeai como genes
desde datetime importar datetime

# --- CREDENCIALES REGISTRADAS EN MEMORIA [cite: 2026-01-21] ---
SUPABASE_URL = " https://twijbhpgusigkxaxxbgg.supabase.co "
SUPABASE_KEY = "sb_secret_U3- Q59QI0KD5hukufSEvqw_hUSpevKA"
CLAVE_GEMINI = " AIzaSyBIeuYf395dfR3kgGr5Z730s6 gWg5P0oVg"
ACCOUNT_ID = "074b666f-ded6-49aa-a349- 0fa7e8ac4757" # Tu ID Real [cita: 2026-01-21]

supabase: Cliente = crear_cliente(SUPABASE_URL, SUPABASE_KEY)
genai.configure(clave_api= CLAVE_GEMINI)
modelo = genai.GenerativeModel('gemini- 1.5-flash')

SÍMBOLO = "US500"
LOTE_ESTANDAR = 0.03 # Regla fija acordada [cite: 2026-01-19]

# --- MODULO DE MEMORIA Y LOGS ---
def guardar_charla_ia(categoria, instruccion):
    """Escribe en Supabase para que no se me olvide nada [cite: 2026-01-21]"""
    datos = {
        "categoría": categoría,
        "detalle_instruccion": instruccion,
        "estado_estrategia": "Riesgo Max 30% | US500 | Lote 0.03"
    }
    supabase.table("memoria_conversacion").insert(data).execute()

# --- GESTIÓN DE CONEXIÓN (ENCENDER/APAGAR) [cite: 2026-01-20] ---
async def gestionar_conexion(api, encender=True):
    cuenta = await api.metatrader_account_api.get_account (ID_CUENTA)
    if encender:
        esperar cuenta.deploy()
        esperar cuenta.wait_connected()
    demás:
        esperar cuenta.undeploy()

# --- ANÁLISIS VSA Y CÁLCULOS TÉCNICOS ---
def obtener_analisis_vsa_realtime():
    """Analiza volumen y esfuerzo oculto segundo a segundo [cite: 2026-01-19]"""
    res = supabase.table("monitoreo_diamante_pro ").select("*"). order("timestamp", desc=True).limit(100).execute( )
    si no res.data: devuelve Ninguno
    
    df = pd.DataFrame(res.data) # Aquí usamos Pandas para la potencia de cálculo
    último = df.iloc[0]
    
    # Detección de Diamante e Instancias de Oro [cite: 2026-01-19]
    es_diamante = ultimo['volumen_dic_institutional'] > 500 
    es_trampa = ultimo['volumen_esfuerzo_oculto'] > 1000 and abs(ultimo['precio_ia_master'] - ultimo['precio_massive']) < 0.01
    
    # Cálculo de Medias Móviles Virtuales (Sin MT5 visual)
    ma50 = df['precio_ia_master']. rolling(ventana=50).mean(). iloc[0]
    ma200 = df['precio_ia_master']. rolling(ventana=200).mean(). iloc[0]
    
    devolver {
        "es_diamante": es_diamante, "es_trampa": es_trampa,
        "delta": ultimo['delta_fuerza_neta'], "precio": ultimo['precio_ia_master'],
        "ma50": ma50, "ma200": ma200
    }

# --- EJECUCIÓN VIRTUAL ---
async def ejecutar_trade_pro(api, decision, sl_tecnico, vsa):
    """Prende MetaApi, opera según riesgo y apaga [cite: 2026-01-20, 2026-01-21]"""
    intentar:
        await gestionar_conexion(api, encender=True)
        cuenta = await api.metatrader_account_api.get_account (ID_CUENTA)
        conexión = cuenta.get_streaming_connection ()
        esperar conexión.connect()
        esperar conexión.wait_synchronized()

        # Riesgo según Diamantes [cite: 2026-01-19, 2026-01-21]
        riesgo = 0.10 if vsa['es_diamante'] else 0.05
        if vsa['es_diamante'] and vsa['delta'] > 1000: riesgo = 0.20 # Excepción de Oro
            
        if decision == "COMPRA":
            esperar conexión.create_market_buy_order (SÍMBOLO, LOTE_ESTANDAR, sl_tecnico, 0)
        demás:
            esperar conexión.create_market_sell_order (SIMBOLO, LOTE_ESTANDAR, sl_tecnico, 0)
        
        guardar_charla_ia("EJECUCIÓN", f"Orden {decision} enviada. Riesgo: {riesgo*100}%")
        await gestionar_conexion(api, encender=False)
        
    excepto Excepción como e:
        imprimir(f"Error: {e}")
        await gestionar_conexion(api, encender=False)

# --- BUCLE PRINCIPAL ---
definición asíncrona principal():
    api = MetaApi(os.getenv("META_API_TOKEN "))
    print("🚀 FUERTE777: Sistema Diamante Pro (Pandas + Memoria) Activo")
    guardar_charla_ia("SISTEMA", "Bot iniciado con soporte Pandas para Medias Móviles.")

    mientras sea verdadero:
        vsa = obtener_analisis_vsa_realtime()
        
        si vsa y no vsa['es_trampa']:
            # Lógica de Medias Móviles: Precio por encima de MA200 es alcista [cite: 2026-01-19]
            si vsa['precio'] > vsa['ma200'] y vsa['es_diamante']:
                # Aquí llamamos a ejecutar_trade_pro...
                aprobar
            
        esperar asyncio.sleep(1)

si __nombre__ == "__principal__":
    asyncio.run(principal())
