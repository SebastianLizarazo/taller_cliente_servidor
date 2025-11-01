"""
Script de prueba automática para el sistema de inventario
Ejecuta pruebas unitarias de las funciones del servidor
"""

from servidor import ServidorInventario
import json
import sys
import os

# Agregar el directorio actual al path para importar el servidor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def prueba_validacion():
    """Prueba la validación de equipos"""
    print("\n=== PRUEBA 1: Validación de Equipos ===")

    servidor = ServidorInventario(
        puerto=5556, archivo_datos='test_inventario.json')

    # Prueba 1: Equipo válido
    equipo_valido = {
        'codigo': 'TEST01',
        'nombre': 'Equipo de Prueba',
        'tipo': 'Tipo de Prueba',
        'estado': 'disponible'
    }
    es_valido, mensaje = servidor.validar_equipo(equipo_valido)
    print(f"✓ Equipo válido: {es_valido} - {mensaje}")
    assert es_valido == True

    # Prueba 2: Equipo sin código
    equipo_sin_codigo = {
        'nombre': 'Equipo de Prueba',
        'tipo': 'Tipo de Prueba',
        'estado': 'disponible'
    }
    es_valido, mensaje = servidor.validar_equipo(equipo_sin_codigo)
    print(f"✓ Equipo sin código: {es_valido} - {mensaje}")
    assert es_valido == False

    # Prueba 3: Estado inválido
    equipo_estado_invalido = {
        'codigo': 'TEST02',
        'nombre': 'Equipo de Prueba',
        'tipo': 'Tipo de Prueba',
        'estado': 'estado_invalido'
    }
    es_valido, mensaje = servidor.validar_equipo(equipo_estado_invalido)
    print(f"✓ Estado inválido: {es_valido} - {mensaje}")
    assert es_valido == False

    print("✅ Todas las pruebas de validación pasaron\n")

    # Limpiar archivo de prueba
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')


def prueba_registro():
    """Prueba el registro de equipos"""
    print("=== PRUEBA 2: Registro de Equipos ===")

    # Limpiar archivo de prueba si existe
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')

    servidor = ServidorInventario(
        puerto=5556, archivo_datos='test_inventario.json')

    # Prueba 1: Registrar equipo nuevo
    datos = {
        'codigo': 'MM01',
        'nombre': 'Multímetro Digital',
        'tipo': 'Instrumento de medición',
        'estado': 'disponible'
    }
    respuesta = servidor.registrar_equipo(datos)
    print(
        f"✓ Registro nuevo: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'ok'
    assert len(servidor.inventario) == 1

    # Prueba 2: Registrar equipo con código duplicado
    respuesta = servidor.registrar_equipo(datos)
    print(
        f"✓ Código duplicado: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'error'
    assert len(servidor.inventario) == 1

    # Prueba 3: Registrar otro equipo
    datos2 = {
        'codigo': 'OSC01',
        'nombre': 'Osciloscopio',
        'tipo': 'Instrumento de medición',
        'estado': 'en uso'
    }
    respuesta = servidor.registrar_equipo(datos2)
    print(
        f"✓ Segundo registro: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'ok'
    assert len(servidor.inventario) == 2

    print("✅ Todas las pruebas de registro pasaron\n")

    # Limpiar archivo de prueba
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')


def prueba_busqueda():
    """Prueba la búsqueda de equipos"""
    print("=== PRUEBA 3: Búsqueda de Equipos ===")

    # Limpiar archivo de prueba si existe
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')

    servidor = ServidorInventario(
        puerto=5556, archivo_datos='test_inventario.json')

    # Registrar equipos de prueba
    servidor.registrar_equipo({
        'codigo': 'PC01',
        'nombre': 'Computador Dell',
        'tipo': 'Equipo de cómputo',
        'estado': 'disponible'
    })

    # Prueba 1: Buscar equipo existente
    respuesta = servidor.buscar_equipo('PC01')
    print(
        f"✓ Búsqueda exitosa: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'ok'
    assert respuesta['equipo']['codigo'] == 'PC01'

    # Prueba 2: Buscar equipo inexistente
    respuesta = servidor.buscar_equipo('NOEXISTE')
    print(
        f"✓ Equipo no encontrado: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'error'

    # Prueba 3: Búsqueda case-insensitive
    respuesta = servidor.buscar_equipo('pc01')
    print(
        f"✓ Búsqueda case-insensitive: {respuesta['resultado']} - {respuesta['equipo']['codigo']}")
    assert respuesta['resultado'] == 'ok'

    print("✅ Todas las pruebas de búsqueda pasaron\n")

    # Limpiar archivo de prueba
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')


def prueba_actualizacion():
    """Prueba la actualización de estado"""
    print("=== PRUEBA 4: Actualización de Estado ===")

    # Limpiar archivo de prueba si existe
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')

    servidor = ServidorInventario(
        puerto=5556, archivo_datos='test_inventario.json')

    # Registrar equipo de prueba
    servidor.registrar_equipo({
        'codigo': 'SENS01',
        'nombre': 'Sensor de Temperatura',
        'tipo': 'Sensor',
        'estado': 'disponible'
    })

    # Prueba 1: Actualizar a estado válido
    respuesta = servidor.actualizar_estado('SENS01', 'en uso')
    print(
        f"✓ Actualización exitosa: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'ok'
    assert respuesta['equipo']['estado'] == 'en uso'

    # Prueba 2: Actualizar a estado inválido
    respuesta = servidor.actualizar_estado('SENS01', 'estado_invalido')
    print(
        f"✓ Estado inválido: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'error'

    # Prueba 3: Actualizar equipo inexistente
    respuesta = servidor.actualizar_estado('NOEXISTE', 'disponible')
    print(
        f"✓ Equipo no encontrado: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'error'

    print("✅ Todas las pruebas de actualización pasaron\n")

    # Limpiar archivo de prueba
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')


def prueba_persistencia():
    """Prueba la persistencia de datos"""
    print("=== PRUEBA 5: Persistencia de Datos ===")

    # Limpiar archivo de prueba si existe
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')

    # Crear servidor y registrar equipos
    servidor1 = ServidorInventario(
        puerto=5556, archivo_datos='test_inventario.json')
    servidor1.registrar_equipo({
        'codigo': 'PERS01',
        'nombre': 'Equipo de Persistencia',
        'tipo': 'Prueba',
        'estado': 'disponible'
    })
    print(
        f"✓ Equipo registrado, inventario tiene {len(servidor1.inventario)} equipos")

    # Crear nuevo servidor (simula reinicio)
    servidor2 = ServidorInventario(
        puerto=5557, archivo_datos='test_inventario.json')
    print(
        f"✓ Servidor reiniciado, inventario cargado con {len(servidor2.inventario)} equipos")
    assert len(servidor2.inventario) == 1
    assert servidor2.inventario[0]['codigo'] == 'PERS01'

    print("✅ Prueba de persistencia pasó\n")

    # Limpiar archivo de prueba
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')


def prueba_protocolo():
    """Prueba el procesamiento de mensajes JSON"""
    print("=== PRUEBA 6: Protocolo de Comunicación ===")

    # Limpiar archivo de prueba si existe
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')

    servidor = ServidorInventario(
        puerto=5556, archivo_datos='test_inventario.json')

    # Prueba 1: Mensaje de registro
    mensaje_registro = json.dumps({
        'accion': 'registrar',
        'codigo': 'PROT01',
        'nombre': 'Equipo Protocolo',
        'tipo': 'Prueba',
        'estado': 'disponible'
    })
    respuesta = servidor.procesar_solicitud(mensaje_registro)
    print(f"✓ Protocolo registro: {respuesta['resultado']}")
    assert respuesta['resultado'] == 'ok'

    # Prueba 2: Mensaje de consulta
    mensaje_consulta = json.dumps({'accion': 'consultar'})
    respuesta = servidor.procesar_solicitud(mensaje_consulta)
    print(
        f"✓ Protocolo consulta: {respuesta['resultado']}, {len(respuesta['equipos'])} equipos")
    assert respuesta['resultado'] == 'ok'
    assert len(respuesta['equipos']) == 1

    # Prueba 3: Mensaje inválido
    mensaje_invalido = "esto no es json"
    respuesta = servidor.procesar_solicitud(mensaje_invalido)
    print(
        f"✓ Mensaje inválido: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'error'

    # Prueba 4: Acción no reconocida
    mensaje_accion_invalida = json.dumps({'accion': 'accion_inexistente'})
    respuesta = servidor.procesar_solicitud(mensaje_accion_invalida)
    print(
        f"✓ Acción inválida: {respuesta['resultado']} - {respuesta['mensaje']}")
    assert respuesta['resultado'] == 'error'

    print("✅ Todas las pruebas de protocolo pasaron\n")

    # Limpiar archivo de prueba
    if os.path.exists('test_inventario.json'):
        os.remove('test_inventario.json')


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("SUITE DE PRUEBAS DEL SISTEMA DE INVENTARIO")
    print("="*60)

    try:
        prueba_validacion()
        prueba_registro()
        prueba_busqueda()
        prueba_actualizacion()
        prueba_persistencia()
        prueba_protocolo()

        print("="*60)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("="*60 + "\n")

    except AssertionError as e:
        print(f"\n❌ PRUEBA FALLÓ: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
