"""
Cliente de Inventario de Equipos de Laboratorio
Permite conectarse al servidor y realizar operaciones sobre el inventario
"""

import socket
import json
import sys


class ClienteInventario:
    def __init__(self, host='localhost', puerto=5555):
        self.host = host
        self.puerto = puerto
        self.socket = None

    def conectar(self):
        """Establece conexión con el servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.puerto))
            return True
        except ConnectionRefusedError:
            print(
                f"\n❌ Error: No se pudo conectar al servidor en {self.host}:{self.puerto}")
            print("Verifica que el servidor esté ejecutándose.")
            return False
        except Exception as e:
            print(f"\n❌ Error al conectar: {e}")
            return False

    def desconectar(self):
        """Cierra la conexión con el servidor"""
        if self.socket:
            self.socket.close()

    def enviar_solicitud(self, solicitud):
        """Envía una solicitud al servidor y recibe la respuesta"""
        try:
            # Enviar solicitud
            mensaje_json = json.dumps(solicitud, ensure_ascii=False)
            self.socket.sendall(mensaje_json.encode('utf-8'))

            # Recibir respuesta
            data = self.socket.recv(4096)
            respuesta = json.loads(data.decode('utf-8'))

            return respuesta

        except Exception as e:
            print(f"\n❌ Error en la comunicación: {e}")
            return None

    def registrar_equipo(self):
        """Captura datos y registra un nuevo equipo"""
        print("\n" + "="*60)
        print("REGISTRAR NUEVO EQUIPO")
        print("="*60)

        codigo = input("Código del equipo: ").strip()
        nombre = input("Nombre del equipo: ").strip()
        tipo = input("Tipo de equipo: ").strip()

        print("\nEstados disponibles:")
        print("1. Disponible")
        print("2. En uso")
        print("3. En mantenimiento")
        print("4. Fuera de servicio")

        estados = {
            '1': 'disponible',
            '2': 'en uso',
            '3': 'en mantenimiento',
            '4': 'fuera de servicio'
        }

        opcion_estado = input("Selecciona el estado (1-4): ").strip()
        estado = estados.get(opcion_estado, 'disponible')

        # Crear solicitud
        solicitud = {
            'accion': 'registrar',
            'codigo': codigo,
            'nombre': nombre,
            'tipo': tipo,
            'estado': estado
        }

        # Enviar solicitud
        respuesta = self.enviar_solicitud(solicitud)

        # Mostrar respuesta
        if respuesta:
            if respuesta['resultado'] == 'ok':
                print(f"\n✅ {respuesta['mensaje']}")
                if 'equipo' in respuesta:
                    self.mostrar_equipo(respuesta['equipo'])
            else:
                print(f"\n❌ Error: {respuesta['mensaje']}")

    def consultar_equipos(self):
        """Consulta y muestra todos los equipos"""
        print("\n" + "="*60)
        print("LISTA DE EQUIPOS")
        print("="*60)

        # Crear solicitud
        solicitud = {'accion': 'consultar'}

        # Enviar solicitud
        respuesta = self.enviar_solicitud(solicitud)

        # Mostrar respuesta
        if respuesta:
            if respuesta['resultado'] == 'ok':
                equipos = respuesta.get('equipos', [])

                if not equipos:
                    print("\n📋 No hay equipos registrados en el inventario.")
                else:
                    print(f"\n📋 {respuesta['mensaje']}\n")
                    for i, equipo in enumerate(equipos, 1):
                        print(f"\n--- Equipo #{i} ---")
                        self.mostrar_equipo(equipo)
            else:
                print(f"\n❌ Error: {respuesta['mensaje']}")

    def buscar_equipo(self):
        """Busca un equipo por código"""
        print("\n" + "="*60)
        print("BUSCAR EQUIPO")
        print("="*60)

        codigo = input("Ingresa el código del equipo: ").strip()

        # Crear solicitud
        solicitud = {
            'accion': 'buscar',
            'codigo': codigo
        }

        # Enviar solicitud
        respuesta = self.enviar_solicitud(solicitud)

        # Mostrar respuesta
        if respuesta:
            if respuesta['resultado'] == 'ok':
                print(f"\n✅ {respuesta['mensaje']}\n")
                self.mostrar_equipo(respuesta['equipo'])
            else:
                print(f"\n❌ {respuesta['mensaje']}")

    def actualizar_estado(self):
        """Actualiza el estado de un equipo"""
        print("\n" + "="*60)
        print("ACTUALIZAR ESTADO DE EQUIPO")
        print("="*60)

        codigo = input("Código del equipo: ").strip()

        print("\nNuevos estados disponibles:")
        print("1. Disponible")
        print("2. En uso")
        print("3. En mantenimiento")
        print("4. Fuera de servicio")

        estados = {
            '1': 'disponible',
            '2': 'en uso',
            '3': 'en mantenimiento',
            '4': 'fuera de servicio'
        }

        opcion_estado = input("Selecciona el nuevo estado (1-4): ").strip()
        estado = estados.get(opcion_estado, 'disponible')

        # Crear solicitud
        solicitud = {
            'accion': 'actualizar',
            'codigo': codigo,
            'estado': estado
        }

        # Enviar solicitud
        respuesta = self.enviar_solicitud(solicitud)

        # Mostrar respuesta
        if respuesta:
            if respuesta['resultado'] == 'ok':
                print(f"\n✅ {respuesta['mensaje']}")
                if 'equipo' in respuesta:
                    self.mostrar_equipo(respuesta['equipo'])
            else:
                print(f"\n❌ Error: {respuesta['mensaje']}")

    def mostrar_equipo(self, equipo):
        """Muestra la información de un equipo"""
        print(f"  Código: {equipo['codigo']}")
        print(f"  Nombre: {equipo['nombre']}")
        print(f"  Tipo: {equipo['tipo']}")
        print(f"  Estado: {equipo['estado'].upper()}")
        if 'fecha_registro' in equipo:
            print(f"  Fecha de registro: {equipo['fecha_registro']}")
        if 'ultima_actualizacion' in equipo:
            print(f"  Última actualización: {equipo['ultima_actualizacion']}")

    def mostrar_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*60)
        print("SISTEMA DE INVENTARIO DE EQUIPOS DE LABORATORIO")
        print("="*60)
        print("1. Registrar nuevo equipo")
        print("2. Consultar todos los equipos")
        print("3. Buscar equipo por código")
        print("4. Actualizar estado de equipo")
        print("5. Salir")
        print("="*60)

    def ejecutar(self):
        """Ejecuta el cliente"""
        print("\n" + "="*60)
        print("CLIENTE DE INVENTARIO DE EQUIPOS")
        print("="*60)
        print(f"Conectando a {self.host}:{self.puerto}...")

        if not self.conectar():
            return

        print(f"✅ Conectado exitosamente al servidor\n")

        try:
            while True:
                self.mostrar_menu()
                opcion = input("\nSelecciona una opción: ").strip()

                if opcion == '1':
                    self.registrar_equipo()
                elif opcion == '2':
                    self.consultar_equipos()
                elif opcion == '3':
                    self.buscar_equipo()
                elif opcion == '4':
                    self.actualizar_estado()
                elif opcion == '5':
                    print("\n👋 Cerrando conexión con el servidor...")
                    break
                else:
                    print(
                        "\n⚠️  Opción no válida. Por favor, selecciona una opción del 1 al 5.")

                input("\nPresiona Enter para continuar...")

        except KeyboardInterrupt:
            print("\n\n👋 Conexión interrumpida por el usuario.")

        finally:
            self.desconectar()
            print("Desconectado del servidor.\n")


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("CONFIGURACIÓN DEL CLIENTE")
    print("="*60)

    # Solicitar configuración
    host = input(
        "Ingresa la IP del servidor (Enter para 'localhost'): ").strip()
    if not host:
        host = 'localhost'

    puerto_str = input(
        "Ingresa el puerto del servidor (Enter para '5555'): ").strip()
    if not puerto_str:
        puerto = 5555
    else:
        try:
            puerto = int(puerto_str)
        except ValueError:
            print("⚠️  Puerto inválido. Usando puerto 5555 por defecto.")
            puerto = 5555

    # Crear y ejecutar cliente
    cliente = ClienteInventario(host=host, puerto=puerto)
    cliente.ejecutar()


if __name__ == "__main__":
    main()
