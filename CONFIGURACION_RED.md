# Guía de Configuración de Red Local (LAN)

Esta guía proporciona instrucciones paso a paso para configurar el sistema en una red local del laboratorio.

## Escenario de Prueba Recomendado

### Equipos Necesarios

- 1 PC para el servidor
- 2-3 PCs para clientes
- Todos conectados a la misma red LAN (switch/router)

## Paso 1: Preparar el Servidor

### 1.1 Identificar la IP del Servidor

En Windows PowerShell:

```powershell
ipconfig
```

Buscar la línea "Dirección IPv4" en la sección del adaptador activo. Ejemplo:

```
Dirección IPv4. . . . . . . . . . . . . . : 192.168.0.10
```

### 1.2 Configurar el Firewall

**Opción A: Crear regla específica (Recomendado)**

En PowerShell como Administrador:

```powershell
New-NetFirewallRule -DisplayName "Servidor Inventario" -Direction Inbound -LocalPort 5555 -Protocol TCP -Action Allow
```

**Opción B: Desactivar temporalmente el firewall (Solo para pruebas)**

```powershell
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
```

⚠️ **Importante**: Recuerda reactivar el firewall después de las pruebas:

```powershell
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

### 1.3 Verificar que el puerto está libre

```powershell
netstat -an | findstr :5555
```

Si el comando no devuelve nada, el puerto está libre.

### 1.4 Iniciar el Servidor

```powershell
python servidor.py
```

Deberías ver:

```
============================================================
SERVIDOR DE INVENTARIO DE EQUIPOS
============================================================
Escuchando en: 0.0.0.0:5555
```

## Paso 2: Configurar los Clientes

### 2.1 Verificar Conectividad

Desde cada PC cliente, hacer ping al servidor:

```powershell
ping 192.168.0.10
```

Deberías ver respuestas como:

```
Respuesta desde 192.168.0.10: bytes=32 tiempo<1ms TTL=128
```

### 2.2 Verificar que el Puerto está Accesible

```powershell
Test-NetConnection -ComputerName 192.168.0.10 -Port 5555
```

Si la conexión es exitosa, verás:

```
TcpTestSucceeded : True
```

### 2.3 Iniciar el Cliente

```powershell
python cliente.py
```

Cuando se solicite:

```
Ingresa la IP del servidor: 192.168.0.10
Ingresa el puerto del servidor: 5555
```

## Paso 3: Realizar Pruebas

### Prueba 1: Registro desde Múltiples Clientes

**Cliente 1:**

```
Selecciona opción: 1
Código: MM01
Nombre: Multímetro Fluke 87V
Tipo: Instrumento de medición
Estado: 1 (Disponible)
```

**Cliente 2:**

```
Selecciona opción: 1
Código: OSC01
Nombre: Osciloscopio Tektronix
Tipo: Instrumento de medición
Estado: 1 (Disponible)
```

### Prueba 2: Verificar Sincronización

En ambos clientes, seleccionar opción 2 (Consultar todos los equipos).

Ambos deberían ver los 2 equipos registrados.

### Prueba 3: Actualización Simultánea

**Cliente 1:**

```
Selecciona opción: 4
Código: MM01
Nuevo estado: 2 (En uso)
```

**Cliente 2:**
Inmediatamente después, buscar el equipo:

```
Selecciona opción: 3
Código: MM01
```

Debería mostrar el estado actualizado "EN USO".

### Prueba 4: Manejo de Errores

**Desde cualquier cliente:**

```
Selecciona opción: 1
Código: MM01  (código que ya existe)
```

Debería mostrar: "❌ Error: El código ya existe en el inventario"

## Paso 4: Monitorear el Servidor

Mientras los clientes se conectan y envían solicitudes, el servidor mostrará logs en tiempo real:

```
2025-11-01 10:30:45 - INFO - Nueva conexión desde ('192.168.0.11', 54321)
2025-11-01 10:30:46 - INFO - Solicitud de ('192.168.0.11', 54321): {"accion": "registrar", "codigo": "MM01"...
2025-11-01 10:30:46 - INFO - Equipo registrado: MM01
```

También puedes revisar el archivo `servidor.log` para ver el historial completo.

## Solución de Problemas Comunes

### Problema: "No se pudo conectar al servidor"

**Verificar:**

1. ✅ El servidor está ejecutándose
2. ✅ La IP es correcta
3. ✅ Ambos equipos están en la misma red
4. ✅ El firewall permite conexiones en el puerto 5555

**Comandos de diagnóstico:**

```powershell
# Verificar IP del servidor
ping 192.168.0.10

# Verificar conectividad del puerto
Test-NetConnection -ComputerName 192.168.0.10 -Port 5555

# Ver reglas de firewall
Get-NetFirewallRule -DisplayName "Servidor Inventario"
```

### Problema: "Address already in use"

El puerto 5555 ya está siendo usado.

**Solución:**

1. Cerrar cualquier instancia anterior del servidor
2. Esperar 30 segundos
3. Reiniciar el servidor

O verificar qué proceso está usando el puerto:

```powershell
netstat -ano | findstr :5555
```

### Problema: Firewall bloqueando conexiones

**Verificar estado del firewall:**

```powershell
Get-NetFirewallProfile | Select Name, Enabled
```

**Ver si hay reglas bloqueando:**

```powershell
Get-NetFirewallRule | Where-Object {$_.LocalPort -eq 5555}
```

### Problema: Clientes no se sincronizan

**Verificar:**

1. ✅ Todos los clientes están conectados al mismo servidor
2. ✅ El archivo `inventario.json` se está actualizando (ver fecha de modificación)
3. ✅ No hay errores en `servidor.log`

## Configuración de Red Avanzada

### Usar una IP Estática para el Servidor

1. Abrir "Configuración de red"
2. Clic en "Cambiar opciones del adaptador"
3. Clic derecho en el adaptador → Propiedades
4. Seleccionar "Protocolo de Internet versión 4 (TCP/IPv4)"
5. Seleccionar "Usar la siguiente dirección IP"
6. Ingresar:
   - Dirección IP: `192.168.0.10`
   - Máscara de subred: `255.255.255.0`
   - Puerta de enlace: `192.168.0.1` (o la IP del router)

### Cambiar el Puerto del Servidor

Si el puerto 5555 está en uso, modificar en `servidor.py`:

```python
# Línea al final del archivo
PUERTO = 5556  # Cambiar a un puerto diferente
```

Y en cada cliente conectarse al nuevo puerto.

## Lista de Verificación Pre-Prueba

Antes de iniciar las pruebas en el laboratorio:

- [ ] Python 3.7+ instalado en todos los equipos
- [ ] Archivos `servidor.py` y `cliente.py` copiados en todos los equipos
- [ ] Todos los equipos conectados a la misma red LAN
- [ ] IP del servidor identificada y anotada
- [ ] Firewall configurado en el servidor
- [ ] Conectividad verificada con `ping` y `Test-NetConnection`
- [ ] Servidor iniciado y escuchando
- [ ] Al menos 2 clientes listos para conectarse

## Arquitectura de Red Visual

```
┌─────────────────────────────────────────────────────────┐
│                  RED LOCAL (LAN)                         │
│                192.168.0.0/24                            │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  │  SERVIDOR    │    │  CLIENTE 1   │    │  CLIENTE 2   │
│  │              │    │              │    │              │
│  │ 192.168.0.10 │    │ 192.168.0.11 │    │ 192.168.0.12 │
│  │ Puerto: 5555 │◄───┤ Python       │◄───┤ Python       │
│  │              │    │ cliente.py   │    │ cliente.py   │
│  │ servidor.py  │    │              │    │              │
│  └──────────────┘    └──────────────┘    └──────────────┘
│         │                                                │
│         ▼                                                │
│  inventario.json                                         │
│  servidor.log                                            │
└─────────────────────────────────────────────────────────┘
```

## Conclusión

Siguiendo estos pasos, deberías poder:

1. ✅ Configurar el servidor en una máquina
2. ✅ Conectar múltiples clientes desde otras máquinas
3. ✅ Realizar operaciones simultáneas
4. ✅ Verificar la sincronización de datos
5. ✅ Resolver problemas comunes de conectividad

Para más información, consultar [DOCUMENTACION.md](DOCUMENTACION.md).
