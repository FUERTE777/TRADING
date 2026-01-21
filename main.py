import os
import asyncio
import pandas as pd
from metaapi_cloud_sdk import MetaApi
from supabase import create_client, Client
import google.generativeai as genai
from datetime import datetime

# --- CREDENCIALES (Anotadas en Memoria Científica) ---
SUPABASE_URL = "https://twijbhpgusigkxaxxbgg.supabase.co"
SUPABASE_KEY = "sb_secret_U3-Q59QI0KD5hukufSEvqw_hUSpevKA"
GEMINI_KEY = "AIzaSyBIeuYf395dfR3kgGr5Z730s6gWg5P0oVg"

# Estas variables deben estar configuradas en Fly.io
META_API_TOKEN = os.getenv("META_API_TOKEN") 
ACCOUNT_ID = os.getenv("META_ACCOUNT_ID")

# Inicialización de Clientes
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SIMBOLO = "US500"
LOTE_ESTANDAR = 0.03 # Regla fija acordada [cite: 2026-01-19]

# --- MODULO DE MEMORIA (PARA NO PERDER EL HILO) ---

def leer_memoria_ia():
    """Lee lo último que hablamos para que la IA sepa dónde está parada [cite: 2026-01-21]"""
    try:
        res = supabase.table("memoria_conversacion").select("*").order("fecha_hora", desc=True).limit(1).execute()
        if res.data:
            print(f"--- MEMORIA RECUPERADA ---")
            print(f"Última instrucción: {res.data[0]['detalle_instruccion']}")
            return res.data[0]
    except Exception as e:
        print(f"Error leyendo memoria: {e}")
    return None

def guardar_charla_ia(categoria, instruccion):
    """Escribe en Supabase para que no se me olvide nada al cerrar sesión [cite: 2026-01-21]"""
    data = {
        "categoria": categoria,
        "detalle_instruccion": instruccion,
        "estado_estrategia": "Riesgo Max 30% | US500 | Lote 0.03"
    }
    supabase.table("memoria_conversacion").insert(data).execute()
    print(f"✅ Registro guardado: {categoria} - Memoria blindada.")

# --- MONITOREO Y EJECUCIÓN ---

def obtener_analisis_vsa_realtime():
    """Monitoreo segundo a segundo de Diamantes y Esfuerzo Oculto [cite: 2026-01-19]"""
    res = supabase.table("monitoreo_diamante_pro").select("*").order("timestamp", desc=True).limit(1).execute()
    if not res.data: return None
    
    dato = res.data[0]
    es_diamante = dato['volumen_dic_institutional'] > 500 
    es_trampa = dato['volumen_esfuerzo_oculto'] > 1000 and abs(dato['precio_ia_master'] - dato['precio_massive']) < 0.01
    
    return {
        "es_diamante": es_diamante,
        "es_trampa": es_trampa,
        "delta": dato['delta_fuerza_neta'],
        "precio": dato['precio_ia_master']
    }

async def ejecutar_trade_virtual(api, decision, sl_tecnico, analisis_vsa):
    """Ejecución en la nube compatible con Fly.io (Linux) [cite: 2026-01-20]"""
    account = await api.metatrader_account_api.get_account(ACCOUNT_ID)
    connection = account.get_streaming_connection()
    await connection.connect()
    
    # Gestión de riesgo según señales Diamante [cite: 2026-01-19, 2026-01-21]
    riesgo = 0.05 
    if analisis_vsa['es_diamante']:
        riesgo = 0.10 
        if analisis_vsa['delta'] > 1000: # Excepción de Oro (20%) [cite: 2026-01-19]
            riesgo = 0.20
            guardar_charla_ia("EJECUCIÓN", "Activada Excepción de Oro al 20%")

    try:
        # Aquí usamos MetaApi para enviar la orden sin interfaz visual
        if decision == "COMPRA":
            await connection.create_market_buy_order(SIMBOLO, LOTE_ESTANDAR, sl_tecnico, 0)
        else:
            await connection.create_market_sell_order(SIMBOLO, LOTE_ESTANDAR, sl_tecnico, 0)
        
        guardar_charla_ia("TRADE", f"Abierta {decision} con riesgo {riesgo*100}%")
    except Exception as e:
        print(f"Error en trade: {e}")

# --- BUCLE PRINCIPAL ---

async def main():
    api = MetaApi(META_API_TOKEN)
    print("🚀 FUERTE777: Sistema Diamante Virtual Iniciado")
    
    # 1. Recuperar contexto de lo que hablamos
    memoria = leer_memoria_ia()
    
    # 2. Registrar el inicio de sesión de hoy
    guardar_charla_ia("SISTEMA", "Bot iniciado en Fly.io. Monitoreando US500.")

    while True:
        vsa = obtener_analisis_vsa_realtime()
        
        if vsa and not vsa['es_trampa']:
            # Aquí la IA procesa la entrada según las reglas de volumen [cite: 2026-01-19]
            # await ejecutar_trade_virtual(api, "COMPRA", sl_calculado, vsa)
            pass
            
        await asyncio.sleep(1) 

if __name__ == "__main__":
    asyncio.run(main())
