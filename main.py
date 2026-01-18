import MetaTrader5 as mt5
import time
import google.generativeai as genai
from supabase import create_client, Client
from datetime import datetime

# --- CREDENCIALES REGISTRADAS POR LA IA ---
SUPABASE_URL = "https://twijbhpgusigkxaxxbgg.supabase.co"
SUPABASE_KEY = "sb_secret_U3-Q59QI0KD5hukufSEvqw_hUSpevKA"
GEMINI_KEY = "AIzaSyBIeuYf395dfR3kgGr5Z730s6gWg5P0oVg"
ALPHA_VANTAGE_KEY = "6R265KOP1EBX9LLK"

# Configuración de Clientes
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PARÁMETROS ---
SIMBOLO = "US500"
CAPITAL_PRUEBA = 15.0

# Rastreo diario para cumplir tus límites
stats_diarias = {"fecha": datetime.now().date(), "trades_5m": 0, "trades_1h": 0}

def es_ventana_ny():
    ahora = datetime.now()
    return 9 <= ahora.hour <= 10 and 0 <= ahora.minute <= 30

def puede_operar(temporalidad):
    """Verifica límites de 1 trade al día y no más de 1 corto/1 largo."""
    global stats_diarias
    hoy = datetime.now().date()
    
    # Reiniciar contador si es un nuevo día
    if hoy != stats_diarias["fecha"]:
        stats_diarias = {"fecha": hoy, "trades_5m": 0, "trades_1h": 0}

    # Verificar límite diario (a menos que IA vea oportunidad suprema, se controla en el análisis)
    if temporalidad == "5m" and stats_diarias["trades_5m"] >= 1: return False
    if temporalidad == "1h" and stats_diarias["trades_1h"] >= 1: return False

    # Verificar que no haya más de 1 compra y 1 venta abiertas
    posiciones = mt5.positions_get(symbol=SIMBOLO)
    compras = len([p for p in posiciones if p.type == mt5.POSITION_TYPE_BUY])
    ventas = len([p for p in posiciones if p.type == mt5.POSITION_TYPE_SELL])
    
    return compras < 1 and ventas < 1

def consultar_ia_decididora(datos_mercado):
    """Gemini analiza y decide la entrada."""
    prompt = f"Analiza estos datos del S&P 500: {datos_mercado}. Decide: COMPRA, VENTA o NADA. Da el SL técnico. Responde en JSON."
    try:
        response = model.generate_content(prompt)
        return response.text # Aquí procesaríamos el JSON
    except:
        return None

def ejecutar_operacion(tipo, precio_entrada, sl_tecnico, temporalidad):
    """Ejecuta con 0.01 o 0.02 y suma 10% al SL."""
    global stats_diarias
    
    # Calcular 10% extra de margen en el SL
    distancia_original = abs(precio_entrada - sl_tecnico)
    distancia_con_ñapa = distancia_original * 1.10
    
    if tipo == "COMPRA":
        nuevo_sl = precio_entrada - distancia_con_ñapa
        order_type = mt5.ORDER_TYPE_BUY
    else:
        nuevo_sl = precio_entrada + distancia_con_ñapa
        order_type = mt5.ORDER_TYPE_SELL

    lotaje = 0.02 if es_ventana_ny() else 0.01
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SIMBOLO,
        "volume": lotaje,
        "type": order_type,
        "price": precio_entrada,
        "sl": nuevo_sl,
        "magic": 777,
        "comment": f"IA {temporalidad}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    resultado = mt5.order_send(request)
    if resultado.retcode == mt5.TRADE_RETCODE_DONE:
        if temporalidad == "5m": stats_diarias["trades_5m"] += 1
        else: stats_diarias["trades_1h"] += 1
        return resultado.order
    return None

def monitoreo_centinela(ticket, sl_aplicado):
    """Software 'No Duerme': Monitorea precio máximo, mínimo y cercanía al SL."""
    max_precio = 0
    min_distancia_sl = 999999
    
    while True:
        pos = mt5.positions_get(ticket=ticket)
        if not pos: break # Operación cerrada
        
        actual = pos[0].price_current
        distancia = abs(actual - sl_aplicado)
        
        if actual > max_precio: max_precio = actual
        if distancia < min_distancia_sl: min_distancia_sl = distancia
        
        # Anotar en Supabase cada cambio relevante
        supabase.table("operaciones").update({
            "precio_max": max_precio,
            "min_distancia_al_sl": min_distancia_sl
        }).eq("ticket_id", str(ticket)).execute()
        
        time.sleep(1) # Monitoreo en vivo (1 segundo)

def main():
    if not mt5.initialize():
        print("Error inicializando MT5")
        return

    print(">>> FUERTE777 INICIADO: PROTECCIÓN DE $15 ACTIVA <<<")
    
    while True:
        for tf in ["5m", "1h"]:
            if puede_operar(tf):
                # 1. Obtener velas de MT5
                # 2. Consultar IA Gemini
                # 3. Si decide entrar: ticket = ejecutar_operacion(...)
                # 4. Si ticket: monitoreo_centinela(ticket, nuevo_sl)
                pass
        
        time.sleep(300) # Revisa cada 5 minutos si no hay nada abierto

if __name__ == "__main__":
    main()
