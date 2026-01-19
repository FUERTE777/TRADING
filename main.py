import MetaTrader5 as mt5
import time
import json
import google.generativeai as genai
from supabase import create_client, Client
from datetime import datetime

# --- CREDENCIALES REGISTRADAS (IA TRADING) ---
SUPABASE_URL = "https://twijbhpgusigkxaxxbgg.supabase.co"
SUPABASE_KEY = "sb_secret_U3-Q59QI0KD5hukufSEvqw_hUSpevKA"
GEMINI_KEY = "AIzaSyBIeuYf395dfR3kgGr5Z730s6gWg5P0oVg"
ALPHA_VANTAGE_KEY = "6R265KOP1EBX9LLK"

# Configuración de Clientes
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PARÁMETROS ESTRATEGIA FUERTE777 ---
SIMBOLO = "US500"
CAPITAL_INICIAL = 15.0
stats_diarias = {"fecha": datetime.now().date(), "trades_5m": 0, "trades_1h": 0}

# --- GESTIÓN FINANCIERA (High-Water Mark) ---
def actualizar_estado_cuenta():
    account_info = mt5.account_info()
    if account_info is None: return 15.0
    
    balance_actual = account_info.balance
    # Obtener el balance de referencia de Supabase
    res = supabase.table("estado_cuenta").select("*").order("fecha_actualizacion", desc=True).limit(1).execute()
    balance_referencia = res.data[0]['balance_referencia'] if res.data else 15.0
    
    # Si ganamos, subimos la marca de agua
    if balance_actual > balance_referencia:
        balance_referencia = balance_actual
        supabase.table("estado_cuenta").insert({
            "balance_actual": balance_actual,
            "balance_referencia": balance_referencia,
            "nota": "Nueva marca de agua alcanzada"
        }).execute()
    
    return balance_referencia

# --- CEREBRO IA (Análisis VSA + Institutional Score) ---
def consultar_ia_profesional(velas_data, temporalidad):
    prompt = f"""
    Analiza como Trader Institucional S&P 500 ({temporalidad}).
    VELAS: {velas_data}
    TAREA:
    1. Calcula el 'Institutional Score' (0-55).
    2. Busca Cruce Medias 50/200 (SMA vs EMA).
    3. Analiza 'Esfuerzo vs Resultado' (VSA).
    4. Determina SL Técnico.
    RESPONDE SOLO JSON:
    {{"decision": "COMPRA/VENTA/NADA", "score": 55, "sl": 0.0, "vsa": "texto", "probabilidad": 0}}
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('```', ''))
    except:
        return {"decision": "NADA"}

# --- EJECUCIÓN CON ÑAPA DEL 10% ---
def ejecutar_trade(decision, sl_tecnico, tf):
    global stats_diarias
    precio_entrada = mt5.symbol_info_tick(SIMBOLO).ask if decision == "COMPRA" else mt5.symbol_info_tick(SIMBOLO).bid
    
    # Cálculo de la Ñapa del 10%
    distancia_puntos = abs(precio_entrada - sl_tecnico)
    sl_final = precio_entrada - (distancia_puntos * 1.10) if decision == "COMPRA" else precio_entrada + (distancia_puntos * 1.10)
    
    lotaje = 0.02 if (9 <= datetime.now().hour <= 10) else 0.01
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SIMBOLO,
        "volume": lotaje,
        "type": mt5.ORDER_TYPE_BUY if decision == "COMPRA" else mt5.ORDER_TYPE_SELL,
        "price": precio_entrada,
        "sl": sl_final,
        "magic": 777,
        "comment": f"FUERTE777 {tf}",
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    res = mt5.order_send(request)
    if res.retcode == mt5.TRADE_RETCODE_DONE:
        if tf == "5m": stats_diarias["trades_5m"] += 1
        else: stats_diarias["trades_1h"] += 1
        return res.order, sl_final
    return None, None

# --- MODO CENTINELA (NO DUERME) ---
def modo_centinela(ticket, sl_aplicado):
    max_p = 0
    min_dist_sl = 999999
    while True:
        pos = mt5.positions_get(ticket=ticket)
        if not pos: break
        
        curr = pos[0].price_current
        dist = abs(curr - sl_aplicado)
        if curr > max_p: max_p = curr
        if dist < min_dist_sl: min_dist_sl = dist
        
        supabase.table("operaciones").update({
            "precio_max": max_p,
            "min_distancia_al_sl": min_dist_sl
        }).eq("ticket_id", str(ticket)).execute()
        time.sleep(1)

# --- BUCLE PRINCIPAL ---
def main():
    if not mt5.initialize(): return
    print("FUERTE777 ACTIVO - OPERANDO DESDE LONDRES HASTA NY")
    
    while True:
        balance_ref = actualizar_estado_cuenta()
        
        for tf_str, tf_mt5 in [("5m", mt5.TIMEFRAME_M5), ("1h", mt5.TIMEFRAME_H1)]:
            # Verificar límites diarios y si hay posiciones abiertas
            if (tf_str == "5m" and stats_diarias["trades_5m"] < 1) or (tf_str == "1h" and stats_diarias["trades_1h"] < 1):
                if len(mt5.positions_get(symbol=SIMBOLO)) < 2:
                    
                    # 1. Obtener Velas y Medias
                    rates = mt5.copy_rates_from_pos(SIMBOLO, tf_mt5, 0, 200)
                    # (Aquí se calcularían SMAs y EMAs para pasar a la IA)
                    
                    # 2. Consultar Cerebro Gemini
                    ia = consultar_ia_profesional(str(rates[-5:]), tf_str)
                    
                    # 3. Ejecutar y Activar Centinela
                    if ia['decision'] != "NADA" and ia['probabilidad'] > 70:
                        order_id, sl_final = ejecutar_trade(ia['decision'], ia['sl'], tf_str)
                        if order_id:
                            modo_centinela(order_id, sl_final)
                            
        time.sleep(300)

if __name__ == "__main__":
    main()
