"""
Servidor de Inventario de Equipos de Laboratorio
Maneja múltiples clientes concurrentes y mantiene persistencia en JSON
"""

import socket
import threading
import json
import os
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('servidor.log'),
        logging.StreamHandler()
    ]
)


class ServidorInventario:
    def __init__(self, host='0.0.0.0', puerto=5555, archivo_datos='inventario.json'):
        self.host = host
        self.puerto = puerto
        self.archivo_datos = archivo_datos
        self.inventario = []
        self.lock = threading.Lock()  # Para sincronización de hilos
        self.cargar_inventario()

    def cargar_inventario(self):
        """Carga el inventario desde el archivo JSON"""
        try:
            if os.path.exists(self.archivo_datos):
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    self.inventario = json.load(f)
                logging.info(
                    f"Inventario cargado: {len(self.inventario)} equipos")
            else:
                self.inventario = []
                logging.info(
                    "Archivo de inventario no existe. Iniciando con inventario vacío.")
        except Exception as e:
            logging.error(f"Error al cargar inventario: {e}")
            self.inventario = []

    def guardar_inventario(self):
        """Guarda el inventario en el archivo JSON"""
        try:
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(self.inventario, f, indent=4, ensure_ascii=False)
            logging.info("Inventario guardado correctamente")
        except Exception as e:
            logging.error(f"Error al guardar inventario: {e}")

    def validar_equipo(self, equipo):
        """Valida que los campos del equipo sean correctos"""
        campos_requeridos = ['codigo', 'nombre', 'tipo', 'estado']
        estados_validos = ['disponible', 'en uso',
                           'en mantenimiento', 'fuera de servicio']

        for campo in campos_requeridos:
            if campo not in equipo or not equipo[campo]:
                return False, f"Campo '{campo}' es requerido"

        if equipo['estado'].lower() not in estados_validos:
            return False, f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"

        return True, "Válido"

    def registrar_equipo(self, datos):
        """Registra un nuevo equipo en el inventario"""
        try:
            # Validar datos
            es_valido, mensaje = self.validar_equipo(datos)
            if not es_valido:
                return {"resultado": "error", "mensaje": mensaje}

            # Verificar si el código ya existe
            with self.lock:
                for equipo in self.inventario:
                    if equipo['codigo'].upper() == datos['codigo'].upper():
                        return {"resultado": "error", "mensaje": "El código ya existe en el inventario"}

                # Agregar equipo
                nuevo_equipo = {
                    'codigo': datos['codigo'].upper(),
                    'nombre': datos['nombre'],
                    'tipo': datos['tipo'],
                    'estado': datos['estado'].lower(),
                    'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.inventario.append(nuevo_equipo)
                self.guardar_inventario()

            logging.info(f"Equipo registrado: {nuevo_equipo['codigo']}")
            return {"resultado": "ok", "mensaje": "Equipo registrado correctamente", "equipo": nuevo_equipo}

        except Exception as e:
            logging.error(f"Error al registrar equipo: {e}")
            return {"resultado": "error", "mensaje": f"Error interno: {str(e)}"}

    def consultar_equipos(self):
        """Devuelve la lista completa de equipos"""
        try:
            with self.lock:
                return {
                    "resultado": "ok",
                    "mensaje": f"Total de equipos: {len(self.inventario)}",
                    "equipos": self.inventario.copy()
                }
        except Exception as e:
            logging.error(f"Error al consultar equipos: {e}")
            return {"resultado": "error", "mensaje": f"Error interno: {str(e)}"}

    def buscar_equipo(self, codigo):
        """Busca un equipo por su código"""
        try:
            with self.lock:
                for equipo in self.inventario:
                    if equipo['codigo'].upper() == codigo.upper():
                        return {
                            "resultado": "ok",
                            "mensaje": "Equipo encontrado",
                            "equipo": equipo
                        }

                return {"resultado": "error", "mensaje": "Equipo no encontrado"}

        except Exception as e:
            logging.error(f"Error al buscar equipo: {e}")
            return {"resultado": "error", "mensaje": f"Error interno: {str(e)}"}

    def actualizar_estado(self, codigo, nuevo_estado):
        """Actualiza el estado de un equipo"""
        try:
            estados_validos = ['disponible', 'en uso',
                               'en mantenimiento', 'fuera de servicio']

            if nuevo_estado.lower() not in estados_validos:
                return {
                    "resultado": "error",
                    "mensaje": f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
                }

            with self.lock:
                for equipo in self.inventario:
                    if equipo['codigo'].upper() == codigo.upper():
                        estado_anterior = equipo['estado']
                        equipo['estado'] = nuevo_estado.lower()
                        equipo['ultima_actualizacion'] = datetime.now().strftime(
                            '%Y-%m-%d %H:%M:%S')
                        self.guardar_inventario()

                        logging.info(
                            f"Estado actualizado para {codigo}: {estado_anterior} -> {nuevo_estado}")
                        return {
                            "resultado": "ok",
                            "mensaje": f"Estado actualizado de '{estado_anterior}' a '{nuevo_estado}'",
                            "equipo": equipo
                        }

                return {"resultado": "error", "mensaje": "Equipo no encontrado"}

        except Exception as e:
            logging.error(f"Error al actualizar estado: {e}")
            return {"resultado": "error", "mensaje": f"Error interno: {str(e)}"}

    def procesar_solicitud(self, mensaje):
        """Procesa la solicitud del cliente y devuelve la respuesta"""
        try:
            # Parsear el mensaje JSON
            solicitud = json.loads(mensaje)
            accion = solicitud.get('accion', '').lower()

            # Procesar según la acción
            if accion == 'registrar':
                return self.registrar_equipo(solicitud)

            elif accion == 'consultar':
                return self.consultar_equipos()

            elif accion == 'buscar':
                codigo = solicitud.get('codigo', '')
                if not codigo:
                    return {"resultado": "error", "mensaje": "Código no proporcionado"}
                return self.buscar_equipo(codigo)

            elif accion == 'actualizar':
                codigo = solicitud.get('codigo', '')
                estado = solicitud.get('estado', '')
                if not codigo or not estado:
                    return {"resultado": "error", "mensaje": "Código o estado no proporcionado"}
                return self.actualizar_estado(codigo, estado)

            else:
                return {"resultado": "error", "mensaje": f"Acción '{accion}' no reconocida"}

        except json.JSONDecodeError:
            return {"resultado": "error", "mensaje": "Mensaje JSON inválido"}
        except Exception as e:
            logging.error(f"Error al procesar solicitud: {e}")
            return {"resultado": "error", "mensaje": f"Error interno: {str(e)}"}

    def manejar_cliente(self, conn, addr):
        """Maneja la conexión de un cliente"""
        logging.info(f"Nueva conexión desde {addr}")

        try:
            while True:
                # Recibir datos del cliente
                data = conn.recv(4096)
                if not data:
                    break

                mensaje = data.decode('utf-8')
                logging.info(f"Solicitud de {addr}: {mensaje[:100]}...")

                # Procesar solicitud
                respuesta = self.procesar_solicitud(mensaje)

                # Enviar respuesta
                respuesta_json = json.dumps(respuesta, ensure_ascii=False)
                conn.sendall(respuesta_json.encode('utf-8'))
                logging.info(f"Respuesta enviada a {addr}")

        except Exception as e:
            logging.error(f"Error manejando cliente {addr}: {e}")

        finally:
            conn.close()
            logging.info(f"Conexión cerrada con {addr}")

    def iniciar(self):
        """Inicia el servidor"""
        try:
            # Crear socket
            servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            servidor_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Enlazar al puerto
            servidor_socket.bind((self.host, self.puerto))

            # Escuchar conexiones
            servidor_socket.listen(5)
            logging.info(f"Servidor escuchando en {self.host}:{self.puerto}")
            print(f"\n{'='*60}")
            print(f"SERVIDOR DE INVENTARIO DE EQUIPOS")
            print(f"{'='*60}")
            print(f"Escuchando en: {self.host}:{self.puerto}")
            print(f"Archivo de datos: {self.archivo_datos}")
            print(f"Equipos en inventario: {len(self.inventario)}")
            print(f"{'='*60}\n")

            while True:
                # Aceptar conexión
                conn, addr = servidor_socket.accept()

                # Crear hilo para manejar cliente
                cliente_thread = threading.Thread(
                    target=self.manejar_cliente,
                    args=(conn, addr)
                )
                cliente_thread.daemon = True
                cliente_thread.start()

        except KeyboardInterrupt:
            logging.info("Servidor detenido por el usuario")
            print("\n\nServidor detenido.")

        except Exception as e:
            logging.error(f"Error en el servidor: {e}")
            print(f"\nError: {e}")

        finally:
            servidor_socket.close()


if __name__ == "__main__":
    # Configuración del servidor
    HOST = '0.0.0.0'  # Escuchar en todas las interfaces
    PUERTO = 5555      # Puerto del servidor

    # Crear e iniciar servidor
    servidor = ServidorInventario(host=HOST, puerto=PUERTO)
    servidor.iniciar()
