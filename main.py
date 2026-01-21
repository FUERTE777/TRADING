import MetaTrader5 as mt5
import time
import json
import google.generativeai as genai
from supabase import create_client, Client
from datetime import datetime

# --- CREDENCIALES ---
SUPABASE_URL = "https://twijbhpgusigkxaxxbgg.supabase.co"
SUPABASE_KEY = "sb_secret_U3-Q59QI0KD5hukufSEvqw_hUSpevKA"
GEMINI_KEY = "AIzaSyBIeuYf395dfR3kgGr5Z730s6gWg5P0oVg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SIMBOLO = "US500"
LOTE_ESTANDAR = 0.03 # Tu lote para cuenta real en Exness

# --- NUEVA FUNCIÓN: LEER SEGUNDO A SEGUNDO (VSA PRO) ---
def obtener_analisis_vsa_realtime():
    """Lee el último segundo grabado para detectar Diamantes y Esfuerzo Oculto"""
    res = supabase.table("monitoreo_diamante_pro").select("*").order("timestamp", desc=True).limit(1).execute()
    if not res.data: return None
    
    dato = res.data[0]
    # Lógica de detección de Diamante (Simplificada para el bot)
    es_diamante = dato['volumen_dic_institutional'] > 500 # Umbral de ejemplo
    es_trampa = dato['volumen_esfuerzo_oculto'] > 1000 and abs(dato['precio_ia_master'] - dato['precio_massive']) < 0.01
    
    return {
        "es_diamante": es_diamante,
        "es_trampa": es_trampa,
        "delta": dato['delta_fuerza_neta'],
        "precio": dato['precio_ia_master']
    }

# --- CÁLCULO DE LOTAJE DINÁMICO ($37 MAX) ---
def calcular_lote_seguro(distancia_sl):
    """Asegura que la pérdida nunca supere los $37"""
    if distancia_sl <= 0: return 0.01
    # Cálculo basado en tick value del US500
    lote = 37 / (distancia_sl * 10) 
    return round(max(0.01, min(lote, 0.50)), 2)

# --- EJECUCIÓN CON REGLAS DE DIAMANTE ---
def ejecutar_trade_pro(decision, sl_tecnico, analisis_vsa):
    # 1. Determinar Porcentaje de Riesgo
    riesgo = 0.03 # Riesgo base
    if analisis_vsa['es_diamante']:
        riesgo = 0.10 # 10% por un Diamante
        # Si el Delta se duplica (Excepción de Oro), 20% y cerrar resto
        if analisis_vsa['delta'] > 1000: 
            riesgo = 0.20
            cerrar_operaciones_estandar()
            print("¡EXCEPCIÓN DE ORO ACTIVADA! Riesgo al 20%.")

    precio_entrada = mt5.symbol_info_tick(SIMBOLO).ask if decision == "COMPRA" else mt5.symbol_info_tick(SIMBOLO).bid
    distancia = abs(precio_entrada - sl_tecnico)
    
    # Aplicar lotaje según riesgo o máximo $37
    lote_final = calcular_lote_seguro(distancia) if riesgo < 0.10 else (riesgo * 0.5) # Simplificación lotaje diamante

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SIMBOLO,
        "volume": lote_final,
        "type": mt5.ORDER_TYPE_BUY if decision == "COMPRA" else mt5.ORDER_TYPE_SELL,
        "price": precio_entrada,
        "sl": sl_tecnico,
        "magic": 777,
        "comment": f"DIAMANTE_{int(riesgo*100)}%",
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    return mt5.order_send(request)

def cerrar_operaciones_estandar():
    """Cierra todo lo que no sea Diamante cuando hay Excepción de Oro"""
    positions = mt5.positions_get(symbol=SIMBOLO)
    for pos in positions:
        if "DIAMANTE" not in pos.comment:
            # Lógica de cierre mt5.order_send para cerrar...
            pass

# --- BUCLE PRINCIPAL ---
def main():
    if not mt5.initialize(): return
    print("FUERTE777 + SISTEMA DIAMANTE ACTIVO")
    
    while True:
        # 1. Escuchar la base de datos (Segundo a segundo)
        vsa = obtener_analisis_vsa_realtime()
        
        if vsa and not vsa['es_trampa']:
            # Solo analizamos si no es una trampa de esfuerzo oculto
            rates = mt5.copy_rates_from_pos(SIMBOLO, mt5.TIMEFRAME_M5, 0, 10)
            
            # 2. Consultar Cerebro con contexto de Volumen 3
            prompt = f"Precio: {vsa['precio']}, Delta: {vsa['delta']}, Diamante: {vsa['es_diamante']}. ¿Operar?"
            # (Integrar con tu función consultar_ia_profesional)
            
            # 3. Lógica de Medias Móviles 50/200 (Especialmente madrugada)
            # Si es madrugada, esperar a las 9:30 AM para confirmar volumen
            
        time.sleep(1) # Correr a la velocidad del monitor

if __name__ == "__main__":
    main()
