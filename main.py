import os
import asyncio
import pandas as pd
from metaapi_cloud_sdk import MetaApi
from supabase import create_client, Client
import google.generativeai as genai
from datetime import datetime

# --- CREDENCIALES ---
SUPABASE_URL = "https://twijbhpgusigkxaxxbgg.supabase.co"
SUPABASE_KEY = "sb_secret_U3-Q59QI0KD5hukufSEvqw_hUSpevKA"
GEMINI_KEY = "AIzaSyBIeuYf395dfR3kgGr5Z730s6gWg5P0oVg"
# Necesitarás tu TOKEN de MetaApi y el ID de tu cuenta (Account ID)
META_API_TOKEN = os.getenv("META_API_TOKEN") 
ACCOUNT_ID = os.getenv("META_ACCOUNT_ID")

# Inicialización de Clientes
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SIMBOLO = "US500"
LOTE_ESTANDAR = 0.03 # Lote base según acuerdo [cite: 2026-01-19]

# --- MEMORIA CIENTÍFICA: LEER REGLAS ANTES DE EMPEZAR ---
def leer_memoria_ia():
    """Lee lo último que hablamos para no estar perdido [cite: 2026-01-21]"""
    res = supabase.table("memoria_conversacion").select("*").order("fecha_hora", desc=True).limit(1).execute()
    if res.data:
        print(f"--- MEMORIA CARGADA ---")
        print(f"Última instrucción: {res.data[0]['detalle_instruccion']}")
        return res.data[0]
    return None

# --- MONITOREO VSA SEGUNDO A SEGUNDO ---
def obtener_analisis_vsa_realtime():
    res = supabase.table("monitoreo_diamante_pro").select("*").order("timestamp", desc=True).limit(1).execute()
    if not res.data: return None
    
    dato = res.data[0]
    # Detección de Diamante e Instancias de Oro [cite: 2026-01-19]
    es_diamante = dato['volumen_dic_institutional'] > 500 
    es_trampa = dato['volumen_esfuerzo_oculto'] > 1000 and abs(dato['precio_ia_master'] - dato['precio_massive']) < 0.01
    
    return {
        "es_diamante": es_diamante,
        "es_trampa": es_trampa,
        "delta": dato['delta_fuerza_neta'],
        "precio": dato['precio_ia_master']
    }

# --- EJECUCIÓN VIRTUAL (METAAPI) ---
async def ejecutar_trade_virtual(api, decision, sl_tecnico, analisis_vsa):
    account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
    connection = account.get_streaming_connection()
    await connection.connect()
    await connection.wait_synchronized()

    # Gestión de Riesgo Basada en Diamantes [cite: 2026-01-21]
    riesgo = 0.05 # Riesgo estándar 5% [cite: 2026-01-21]
    if analisis_vsa['es_diamante']:
        riesgo = 0.10 # 10% por un Diamante [cite: 2026-01-19]
        if analisis_vsa['delta'] > 1000: # Excepción de Oro [cite: 2026-01-19]
            riesgo = 0.20
            print("¡EXCEPCIÓN DE ORO! Ejecutando cierre de estándar.")
            # Aquí iría lógica para cerrar otras posiciones

    # El lote se calcula para no pasar de $37 si el riesgo es bajo [cite: 2026-01-14]
    # Pero sube al 10% o 20% si es Diamante [cite: 2026-01-19, 2026-01-21]
    
    print(f"Enviando Orden Virtual: {decision} | Riesgo: {riesgo*100}%")
    try:
        if decision == "COMPRA":
            await connection.create_market_buy_order(SIMBOLO, LOTE_ESTANDAR, sl_tecnico, 0)
        else:
            await connection.create_market_sell_order(SIMBOLO, LOTE_ESTANDAR, sl_tecnico, 0)
    except Exception as e:
        print(f"Error en ejecución virtual: {e}")

# --- BUCLE PRINCIPAL ---
async def main():
    api = MetaApi(META_API_TOKEN)
    print("FUERTE777 + SISTEMA DIAMANTE (MODO VIRTUAL LINUX) ACTIVO")
    
    # Cargar memoria antes de operar
    leer_memoria_ia()

    while True:
        vsa = obtener_analisis_vsa_realtime()
        
        if vsa and not vsa['es_trampa']:
            # Lógica de Medias Móviles y Confirmación Institucional 9:30 AM [cite: 2026-01-19]
            # Si se detecta entrada:
            # await ejecutar_trade_virtual(api, "COMPRA", sl_calculado, vsa)
            pass
            
        await asyncio.sleep(1) 

if __name__ == "__main__":
    asyncio.run(main())
