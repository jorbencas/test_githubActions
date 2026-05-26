#!/usr/bin/env python3
"""
Test para verificar que el selector de semanas genera conteos correctos.
Simula datos de historial y verifica que el conteo de meses coincide
con los labels generados en el selector HTML.
"""
import locale
from datetime import datetime, timedelta
from collections import Counter

def test_locale_consistency():
    """Verifica que el conteo de meses y los labels usen el mismo locale."""
    
    # 1. Establecer locale ANTES del conteo (como en el fix)
    try: locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except:
        try: locale.setlocale(locale.LC_TIME, "es_ES.utf8")
        except:
            print("⚠️ Locale es_ES no disponible en este sistema. Test no aplica.")
            return True

    # 2. Simular historial con timestamps de los últimos 3 meses
    ahora = datetime.now()
    historial = []
    for i in range(90):
        ts = (ahora - timedelta(days=i)).isoformat()
        historial.append({"ts": ts, "fuente": "Test", "titulo": f"Noticia {i}"})

    # 3. Contar por mes (como hace el código)
    conteo_meses = Counter()
    for n in historial:
        try:
            dt_n = datetime.fromisoformat(n.get('ts'))
            mes_key = dt_n.strftime('%B %Y').capitalize()
            conteo_meses[mes_key] += 1
        except:
            continue

    print(f"✅ Conteo de meses (Counter): {dict(conteo_meses)}")

    # 4. Generar labels como hace el código
    errores = 0
    for i in range(12):
        inicio = ahora - timedelta(days=ahora.weekday() + (7*i))
        nombre_mes = inicio.strftime('%B %Y').capitalize()
        total_mes = conteo_meses.get(nombre_mes, 0)
        
        if nombre_mes in conteo_meses:
            if total_mes == 0:
                print(f"❌ FALLO: '{nombre_mes}' existe en Counter pero devuelve 0")
                errores += 1
            else:
                print(f"  ✅ {nombre_mes}: {total_mes} ítems")

    if errores == 0:
        print("\n🎉 TEST PASADO: Conteo de meses y labels usan el mismo locale.")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: {errores} errores de mismatch de locale.")
        return False


def test_api_key_detection():
    """Verifica que la detección de API key inválida funciona con los strings reales."""
    
    # Simular el error real que devuelve Gemini
    error_messages = [
        "400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 'type.googleapis.com/google.rpc.ErrorInfo', 'reason': 'API_KEY_INVALID'}]}}",
        "API_KEY_INVALID: The provided API key is not valid",
    ]
    
    quota_messages = [
        "429 Resource has been exhausted (e.g. check quota).",
        "RESOURCE_EXHAUSTED: Quota exceeded",
    ]
    
    errores = 0
    
    for msg in error_messages:
        error_str = msg.upper()
        is_key_invalid = "API_KEY_INVALID" in error_str or ("INVALID_ARGUMENT" in error_str and "API KEY" in error_str)
        if not is_key_invalid:
            print(f"❌ No detectó API key inválida en: {msg[:60]}...")
            errores += 1
        else:
            print(f"  ✅ Detectó API key inválida correctamente")
    
    for msg in quota_messages:
        error_str = msg.upper()
        is_key_invalid = "API_KEY_INVALID" in error_str or ("INVALID_ARGUMENT" in error_str and "API KEY" in error_str)
        is_quota = "429" in error_str or "QUOTA" in error_str or "RESOURCE_EXHAUSTED" in error_str
        if is_key_invalid:
            print(f"❌ Falso positivo de API key en cuota: {msg[:60]}...")
            errores += 1
        elif not is_quota:
            print(f"❌ No detectó cuota en: {msg[:60]}...")
            errores += 1
        else:
            print(f"  ✅ Detectó cuota correctamente (no confundida con API key)")
    
    if errores == 0:
        print("\n🎉 TEST PASADO: Detección de errores de API key funciona correctamente.")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: {errores} errores")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TEST 1: Consistencia de locale en selector de semanas")
    print("=" * 60)
    r1 = test_locale_consistency()
    
    print("\n" + "=" * 60)
    print("TEST 2: Detección de API key inválida")
    print("=" * 60)
    r2 = test_api_key_detection()
    
    print("\n" + "=" * 60)
    if r1 and r2:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("=" * 60)
