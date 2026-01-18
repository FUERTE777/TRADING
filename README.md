# 📜 ESTRATEGIA DE TRADING ALGORÍTMICO: S&P 500 (PROYECTO TRADING500)

Este repositorio contiene la lógica y el motor de ejecución para un sistema de trading cuantitativo basado en el índice S&P 500, gestionado por IA y ejecutado mediante Python en conexión con MetaTrader 5 y Supabase.

## 1. Perfil del Activo y Ejecución
*   **Activo:** S&P 500 (US500 / SPX500).
*   **Plataforma de Operación:** MetaTrader 5 (MT5).
*   **Entorno de Ejecución:** Python 3.x (Corriendo 24/7 en la nube - Render/Fly.io).
*   **Base de Datos (Memoria Permanente):** Supabase (Tablas segmentadas por temporalidad).

## 2. Gestión de Riesgo Dinámica (Regla de Oro)
*   **Capital Base:** $1,000 USD.
*   **Riesgo Estándar:** $37 USD por operación.
*   **Riesgo Potenciado (Cruce Medias 50/200 en NY 9:00 - 10:30 AM):**
    *   Gráfica 5 min: **$55 USD**.
    *   Gráfica 1 hora: **$70 USD**.
*   **Escalabilidad:** 
    *   Si el capital es < $1,000: El riesgo se mantiene fijo ($37, $55, $70).
    *   Si el capital es > $1,000: El riesgo se recalcula proporcionalmente por cada $1,000 de balance (Interés compuesto).

## 3. Protocolo de Análisis Multi-Temporal
El sistema realiza cálculos y anotaciones en Supabase cada 5 minutos en las siguientes temporalidades:
*   **5 min:** Ejecución y precisión.
*   **15 min / 1h:** Confirmación de tendencia.
*   **2h / 4h / 1D:** Estructura de mercado inter-día y sesgo macro.

## 4. Jerarquía de Decisión (IA)
1.  **Volumen y Precio (85% - 90%):** El análisis de VPA (Volume Price Analysis), VWAP y Delta tiene la máxima prioridad.
2.  **Noticias (10% - 15%):** Peso máximo de 1.5/10. Se analizan a las 2:00 AM (Londres) y 9:00 AM (NY) solo como contexto. Si el volumen contradice la noticia, se sigue al volumen.

## 5. Estrategia de Salida "Invisible" (Stealth Mode)
*   **Sin SL/TP en MT5:** Las órdenes se envían sin niveles visibles para el broker para evitar manipulación.
*   **Gestión por Python:** El script monitorea el precio cada segundo.
*   **Cierre IA:** No se cierra por miedo. Se cierra si:
    1. Se alcanza el riesgo máximo monetario.
    2. La IA determina que la tesis original se invalidó (cambio real de tendencia/volumen).
    3. **Basura Técnica:** Cualquier operación detectada que no cumpla los parámetros profesionales se cierra inmediatamente.

## 6. Protocolo de Recuperación y Adopción
*   **Re-conexión:** Al reiniciar, el script lee `active_trades` en Supabase para retomar el control.
*   **Adopción de Huérfanas:** Si detecta una operación en MT5 no registrada, la IA la analiza. Si es técnicamente válida, le asigna un SL y la gestiona; si es "basura técnica", la cierra de inmediato.

## 7. Stack Técnico Recomendado
*   **Data:** MT5 (Gratis inicial) -> CME Real Volume (Pago futuro).
*   **IA:** Gemini API / Procesamiento de sentimiento y técnico.
*   **DB:** Supabase (PostgreSQL).
*   **Hosting:** Render / Fly.io / Heroku.
