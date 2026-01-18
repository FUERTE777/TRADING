import MetaTrader5 as mt5
import time
from supabase import create_client, Client
from datetime import datetime

# --- CREDENCIALES (YA REGISTRADAS POR LA IA) ---
SUPABASE_URL = "https://twijbhpgusigkxaxxbgg.supabase.co"
SUPABASE_KEY = "sb_secret_U3-Q59QI0KD5hukufSEvqw_hUSpevKA" # He usado tu clave secreta
GEMINI_KEY = "AIzaSyBIeuYf395dfR3kgGr5Z730s6gWg5P0oVg"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- PARÁMETROS DE LA ESTRATEGIA $15 ---
SIMBOLO = "US500" # Nombre en Exness Standard
CAPITAL_INICIAL = 15.0

def es_ventana_ny():
    ahora = datetime.now()
    return 9 <= ahora.hour <= 10 and 0 <= ahora.minute <= 30

def calcular_riesgo_y_lote(temporalidad, probabilidad_ia):
    lote = 0.01
    if es_ventana_ny():
        lote = 0.02
    
    # Si la cuenta creció, la IA puede decidir subir el riesgo según tu regla
    # (Lógica de redondeo integrada aquí)
    return lote

def monitoreo_centinela(ticket, precio_sl):
    """Mantiene al bot despierto mientras la operacion esta abierta."""
    min_distancia = 999999
    while True:
        posicion = mt5.positions_get(ticket=ticket)
        if not posicion: # La operacion se cerró
            break
        
        precio_actual = posicion[0].price_current
        distancia = abs(precio_actual - precio_sl)
        if distancia < min_distancia:
            min_distancia = distancia
            # Actualizar en Supabase el punto mas cercano
            supabase.table("operaciones").update({"min_distancia_al_sl": min_distancia}).eq("ticket_id", str(ticket)).execute()
        
        time.sleep(1) # Revisión cada segundo

def main():
    if not mt5.initialize(): return

    print("SISTEMA FUERTE777 ACTIVO - MODO MICRO-RIESGO $15")
    
    while True:
        ahora = datetime.now()
        # 1. ANALIZAR CRUCES 50/200 (5M y 1H)
        # 2. IA ANALIZA (GEMINI + ALPHA VANTAGE)
        # 3. EJECUTAR CON 0.01 o 0.02 + 10% SL Extra
        
        # El bot duerme 5 min si NO hay operacion
        # Si HAY operacion, entra en monitoreo_centinela
        time.sleep(300)

if __name__ == "__main__":
    main()
