# ESTRATEGIA MAESTRA: ORO (XAUUSD)
**Estado:** Activa
**Última actualización:** 2026-01-25

## 1. REGLAS DE GESTIÓN DE RIESGO
- **Riesgo Estándar:** 10% del capital por operación en gráficas de 5m, 15m, 1h, 2h y 4h.
- **Operación Diamante:** Riesgo del 10% del capital de inmediato.
- **Excepción de Oro (Dos Diamantes):** Si aparecen dos señales simultáneas, subir riesgo al 20% y CERRAR cualquier operación estándar abierta.
- **Riesgo Máximo Total:** Nunca exceder el 30% de la cuenta, sin excepciones.
- **Stop Loss (SL):** Obligatorio en todas las operaciones. El tamaño de la posición se ajusta según el SL (IA + 10%).

## 2. PROTOCOLO DE EJECUCIÓN
- **Consulta Obligatoria:** Antes de cada operación, GIME debe consultar la tabla `ia_estrategia_oro`.
- **Análisis de Volumen:** Calcular el volumen de internet y sumar al puntaje total.
- **Cierre de Vela:** Al concluir cada vela, revisar si la puntuación requiere un cambio de instrucción.

## 3. GESTIÓN DE BENEFICIOS (Trailing Stop)
- Si la ganancia es mayor al SL establecido: Subir el SL para asegurar ganancias (Break Even+).
- Si la ganancia es positiva pero menor al SL: Cerrar operación por completo y tomar ganancia si el precio muestra debilidad.

## 4. INSTRUCCIÓN AUTOMÁTICA DE MENSAJE
GIME siempre debe incluir: "Jime, el precio actual es [Precio]. Consultando tabla `ia_estrategia_oro`, puntuación y volumen... La instrucción a ejecutar es: [X]".
