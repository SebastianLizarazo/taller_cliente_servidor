# Diagramas del Sistema de Inventario

## 1. Arquitectura General del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SISTEMA CLIENTE-SERVIDOR                      │
│                     Inventario de Equipos de Laboratorio            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│   CAPA CLIENTE      │         │   CAPA SERVIDOR     │
│                     │         │                     │
│  ┌───────────────┐  │         │  ┌───────────────┐  │
│  │ Interfaz UI   │  │         │  │ Socket Server │  │
│  │   (consola)   │  │         │  │  (Threading)  │  │
│  └───────┬───────┘  │         │  └───────┬───────┘  │
│          │          │         │          │          │
│  ┌───────▼───────┐  │         │  ┌───────▼───────┐  │
│  │ Validación    │  │         │  │ Procesamiento │  │
│  │   Cliente     │  │         │  │   Solicitudes │  │
│  └───────┬───────┘  │         │  └───────┬───────┘  │
│          │          │         │          │          │
│  ┌───────▼───────┐  │  JSON   │  ┌───────▼───────┐  │
│  │ Comunicación  ├──┼────────►│  │ Validación    │  │
│  │   Socket      │◄─┼─────────┤  │   Servidor    │  │
│  └───────────────┘  │         │  └───────┬───────┘  │
│                     │         │          │          │
└─────────────────────┘         │  ┌───────▼───────┐  │
                                │  │ Sincronización│  │
                                │  │    (Locks)    │  │
                                │  └───────┬───────┘  │
                                │          │          │
                                │  ┌───────▼───────┐  │
                                │  │  Persistencia │  │
                                │  │     (JSON)    │  │
                                │  └───────────────┘  │
                                └─────────────────────┘
```

## 2. Flujo de Comunicación - Registrar Equipo

```
CLIENTE                     RED                      SERVIDOR
   │                         │                          │
   │  1. Usuario ingresa     │                          │
   │     datos del equipo    │                          │
   │                         │                          │
   │  2. Validar datos       │                          │
   │     localmente          │                          │
   │                         │                          │
   │  3. Crear JSON          │                          │
   │     de solicitud        │                          │
   │                         │                          │
   │  4. Enviar por socket   │                          │
   ├────────────────────────►│                          │
   │                         │  5. Recibir solicitud    │
   │                         ├─────────────────────────►│
   │                         │                          │
   │                         │  6. Parsear JSON         │
   │                         │                          │
   │                         │  7. Validar datos        │
   │                         │                          │
   │                         │  8. Verificar duplicados │
   │                         │     (con lock)           │
   │                         │                          │
   │                         │  9. Agregar a inventario │
   │                         │                          │
   │                         │  10. Guardar en archivo  │
   │                         │      inventario.json     │
   │                         │                          │
   │                         │  11. Crear respuesta     │
   │                         │      JSON                │
   │                         │                          │
   │                         │  12. Enviar respuesta    │
   │                         ◄─────────────────────────┤
   │  13. Recibir respuesta  │                          │
   ◄─────────────────────────┤                          │
   │                         │                          │
   │  14. Mostrar resultado  │                          │
   │      al usuario         │                          │
   │                         │                          │
```

## 3. Flujo Multi-Cliente Concurrente

```
┌──────────────┐         ┌──────────────────────────────┐
│  CLIENTE 1   │         │         SERVIDOR             │
│192.168.0.11  │         │       192.168.0.10:5555      │
└──────┬───────┘         │                              │
       │                 │  ┌─────────────────────────┐ │
       │ Solicitud 1     │  │   Thread Principal      │ │
       ├────────────────►│  │  (Listener)             │ │
       │                 │  └────────┬────────────────┘ │
┌──────────────┐         │           │                  │
│  CLIENTE 2   │         │           │ accept()         │
│192.168.0.12  │         │           ▼                  │
└──────┬───────┘         │  ┌────────────────┐          │
       │                 │  │ Thread Cliente1│          │
       │ Solicitud 2     │  │ (Procesa Req 1)│          │
       ├────────────────►│  └────────┬───────┘          │
       │                 │           │                  │
┌──────────────┐         │           │ accept()         │
│  CLIENTE 3   │         │           ▼                  │
│192.168.0.13  │         │  ┌────────────────┐          │
└──────┬───────┘         │  │ Thread Cliente2│          │
       │                 │  │ (Procesa Req 2)│          │
       │ Solicitud 3     │  └────────┬───────┘          │
       ├────────────────►│           │                  │
       │                 │           │ accept()         │
       │                 │           ▼                  │
       │                 │  ┌────────────────┐          │
       │                 │  │ Thread Cliente3│          │
       │                 │  │ (Procesa Req 3)│          │
       │                 │  └────────┬───────┘          │
       │                 │           │                  │
       │                 │           ▼                  │
       │                 │  ┌─────────────────────────┐ │
       │                 │  │   LOCK (Sincronización) │ │
       │                 │  │   Acceso a inventario   │ │
       │                 │  └────────┬────────────────┘ │
       │                 │           │                  │
       │                 │           ▼                  │
       │                 │  ┌─────────────────────────┐ │
       │                 │  │   inventario.json       │ │
       │                 │  └─────────────────────────┘ │
       │                 └──────────────────────────────┘
       │
```

## 4. Estructura de Datos - Equipo

```
┌─────────────────────────────────────────────┐
│              EQUIPO                         │
├─────────────────────────────────────────────┤
│ codigo: String (PK, único, mayúsculas)      │
│ nombre: String                              │
│ tipo: String                                │
│ estado: Enum [disponible, en uso,           │
│              en mantenimiento,              │
│              fuera de servicio]             │
│ fecha_registro: DateTime (auto)             │
│ ultima_actualizacion: DateTime (opcional)   │
└─────────────────────────────────────────────┘
```

## 5. Diagrama de Estados de un Equipo

```
                    [Registro]
                        │
                        ▼
              ┌──────────────────┐
              │   DISPONIBLE     │◄──────────┐
              └────┬─────────────┘           │
                   │                         │
          [Usar]   │                         │ [Liberar]
                   │                         │
                   ▼                         │
              ┌──────────────────┐           │
              │     EN USO       ├───────────┘
              └────┬─────────────┘
                   │
      [Reportar]   │                    [Reparar]
        [Falla]    │                         │
                   ▼                         │
              ┌──────────────────┐           │
              │ EN MANTENIMIENTO │───────────┤
              └────┬─────────────┘           │
                   │                         │
    [Declarar]     │                         │
   [Irreparable]   │                         │
                   ▼                         │
              ┌──────────────────┐           │
              │ FUERA DE SERVICIO│           │
              └──────────────────┘           │
                   │                         │
                   │   [Reparación]          │
                   │   [Exitosa]             │
                   └─────────────────────────┘
```

## 6. Protocolo de Mensajes JSON

```
┌─────────────────────────────────────────────────────────┐
│                    SOLICITUD                            │
├─────────────────────────────────────────────────────────┤
│  {                                                      │
│    "accion": "registrar" | "consultar" |               │
│              "buscar" | "actualizar",                   │
│    "codigo": "string",        // requerido si aplica   │
│    "nombre": "string",        // para registrar        │
│    "tipo": "string",          // para registrar        │
│    "estado": "string"         // para registrar/actual │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    [SERVIDOR]
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    RESPUESTA                            │
├─────────────────────────────────────────────────────────┤
│  {                                                      │
│    "resultado": "ok" | "error",                         │
│    "mensaje": "string",                                 │
│    "equipo": { objeto },      // si aplica             │
│    "equipos": [ array ]       // para consultar        │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
```

## 7. Diagrama de Despliegue en Red LAN

```
┌────────────────────────────────────────────────────────────┐
│                   LABORATORIO - RED LAN                    │
│                      192.168.0.0/24                        │
│                                                            │
│   ┌──────────────────────────────────────────────────┐    │
│   │              SWITCH / ROUTER                     │    │
│   │             192.168.0.1                          │    │
│   └──┬──────────┬──────────┬──────────┬─────────────┘    │
│      │          │          │          │                   │
│ ┌────▼────┐ ┌──▼────┐ ┌───▼────┐ ┌───▼────┐             │
│ │ PC-01   │ │ PC-02 │ │ PC-03  │ │ PC-04  │             │
│ │SERVIDOR │ │CLIENT │ │CLIENT  │ │CLIENT  │             │
│ │.0.10    │ │.0.11  │ │.0.12   │ │.0.13   │             │
│ │         │ │       │ │        │ │        │             │
│ │servidor │ │cliente│ │cliente │ │cliente │             │
│ │.py      │ │.py    │ │.py     │ │.py     │             │
│ │:5555    │ │       │ │        │ │        │             │
│ │         │ │       │ │        │ │        │             │
│ │┌───────┐│ └───────┘ └────────┘ └────────┘             │
│ ││invent.││                                               │
│ ││json   ││                                               │
│ │└───────┘│                                               │
│ └─────────┘                                               │
│                                                            │
│  Firewall abierto en puerto 5555                          │
│  Protocolo: TCP                                           │
│  Formato: JSON sobre sockets                              │
└────────────────────────────────────────────────────────────┘
```

## 8. Flujo de Manejo de Errores

```
┌─────────────────────────────────────────────────────┐
│              SOLICITUD DEL CLIENTE                  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ ¿JSON válido?        │
          └──────┬───────────────┘
                 │
         ┌───────┴───────┐
         │ NO            │ SÍ
         ▼               ▼
    ┌────────┐   ┌──────────────────┐
    │ Error: │   │ ¿Acción válida?  │
    │ JSON   │   └───┬──────────────┘
    │inválido│       │
    └────┬───┘   ┌───┴───────┐
         │       │ NO        │ SÍ
         │       ▼           ▼
         │  ┌────────┐  ┌──────────────────┐
         │  │ Error: │  │ ¿Datos completos?│
         │  │Acción  │  └───┬──────────────┘
         │  │inválida│      │
         │  └───┬────┘  ┌───┴───────┐
         │      │       │ NO        │ SÍ
         │      │       ▼           ▼
         │      │  ┌────────┐  ┌──────────────────┐
         │      │  │ Error: │  │ ¿Validación OK?  │
         │      │  │Datos   │  └───┬──────────────┘
         │      │  │incompl.│      │
         │      │  └───┬────┘  ┌───┴───────┐
         │      │      │       │ NO        │ SÍ
         │      │      │       ▼           ▼
         │      │      │  ┌────────┐  ┌──────────┐
         │      │      │  │ Error: │  │ Procesar │
         │      │      │  │Validac.│  │ Solicitud│
         │      │      │  └───┬────┘  └────┬─────┘
         │      │      │      │            │
         └──────┴──────┴──────┴────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Respuesta JSON   │
                    │ al Cliente       │
                    └──────────────────┘
```

## 9. Diagrama de Clases Simplificado

```
┌───────────────────────────────┐
│   ServidorInventario          │
├───────────────────────────────┤
│ - host: str                   │
│ - puerto: int                 │
│ - archivo_datos: str          │
│ - inventario: list            │
│ - lock: Lock                  │
├───────────────────────────────┤
│ + __init__(host, puerto)      │
│ + cargar_inventario()         │
│ + guardar_inventario()        │
│ + validar_equipo(equipo)      │
│ + registrar_equipo(datos)     │
│ + consultar_equipos()         │
│ + buscar_equipo(codigo)       │
│ + actualizar_estado(...)      │
│ + procesar_solicitud(mensaje) │
│ + manejar_cliente(conn, addr) │
│ + iniciar()                   │
└───────────────────────────────┘
         △
         │ usa
         │
┌───────────────────────────────┐
│   ClienteInventario           │
├───────────────────────────────┤
│ - host: str                   │
│ - puerto: int                 │
│ - socket: Socket              │
├───────────────────────────────┤
│ + __init__(host, puerto)      │
│ + conectar()                  │
│ + desconectar()               │
│ + enviar_solicitud(solicitud) │
│ + registrar_equipo()          │
│ + consultar_equipos()         │
│ + buscar_equipo()             │
│ + actualizar_estado()         │
│ + mostrar_menu()              │
│ + ejecutar()                  │
└───────────────────────────────┘
```

## 10. Timeline de una Sesión Completa

```
TIEMPO  CLIENTE                 SERVIDOR                ARCHIVO

00:00   [Inicio]
        python cliente.py       [Ya ejecutándose]       inventario.json
                                                        [vacío o con datos]
00:01   Conectar()
        ────────────────────►   accept()
                                crear_thread()

00:02   [Usuario registra]
        Solicitud JSON
        ────────────────────►   recibir()
                                validar()
                                lock.acquire()
                                inventario.append()     guardar() ──►
                                lock.release()
        ◄────────────────────   respuesta JSON
        [Mostrar éxito]

00:03   [Usuario consulta]
        Solicitud JSON
        ────────────────────►   recibir()
                                lock.acquire()
                                copiar inventario       leer() ────►
                                lock.release()
        ◄────────────────────   respuesta JSON
        [Mostrar lista]

00:04   [Usuario sale]
        Desconectar()
        ────────────────────►   cerrar conexión
        [Fin]                   thread finaliza
```
