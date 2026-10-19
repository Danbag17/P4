# Laboratorio de P4: redes programables con BMv2 y Mininet

Soluciones a las prácticas del **P4 Lab** de la asignatura *Advanced Networking (ANET)* de la University of Twente (2026).
Cada práctica programa el plano de datos de un switch en **P4₁₆** (arquitectura v1model) y, en las últimas, también el plano de control con **P4Runtime** en Python.

![P4](https://img.shields.io/badge/lenguaje-P4%E2%82%81%E2%82%86-blue)
![Python](https://img.shields.io/badge/control-Python%203-yellow)
![BMv2](https://img.shields.io/badge/switch-BMv2-lightgrey)
![Mininet](https://img.shields.io/badge/emulador-Mininet-green)

## Prácticas

| # | Práctica | Qué hace | Archivos principales |
|---|----------|----------|----------------------|
| 1 | [Reenvío básico](./assignments/basic) | Router IPv4 con tabla LPM: reescribe las MAC, decrementa el TTL y elige el puerto de salida. | `basic.p4` |
| 1 | [Túnel básico](./assignments/basic_tunnel) | Cabecera propia `myTunnel` (EtherType `0x1212`) que encamina por identificador de destino en vez de por IP. | `basic.p4` |
| 2 | [P4Runtime](./assignments/p4runtime) | Un controlador en Python instala las reglas de entrada, tránsito y salida del túnel y lee contadores por túnel. | `basic.p4`, `mycontroller.py` |
| 3 | [Firewall](./assignments/firewall) | Firewall con estado basado en un *Bloom filter* de dos registros: solo deja entrar el tráfico TCP de conexiones iniciadas desde la red interna. | `firewall.p4` |
| 4 | [Balanceo de carga](./assignments/load_balance) | ECMP: un hash sobre la 5-tupla reparte los flujos UDP entre dos caminos. | `load_balance.p4` |
| 4 | [Balanceo de carga controlado](./assignments/controlled_load_balance) | El controlador lee contadores de bytes por enlace y reajusta cada 2 s las 100 entradas de la tabla de siguiente salto para equilibrar la carga. | `load_balance.p4`, `balance_controller.py` |

Cada carpeta tiene un README con un resumen de la solución al principio, seguido del enunciado original.

## Estructura del repositorio

```
.
├── assignments/     # Prácticas resueltas (una carpeta por práctica)
├── base_code/       # Esqueleto basic.p4 del que parten las prácticas
├── utils/           # Scripts para lanzar Mininet, BMv2 y la librería p4runtime_lib
├── P4_Lab_Slides_2026.pdf   # Diapositivas de la clase introductoria
├── P4_tutorial.pdf          # Tutorial de p4.org
└── p4-cheat-sheet.pdf       # Chuleta de sintaxis de P4
```

## Cómo ejecutarlo

Las prácticas se ejecutan en la máquina virtual del curso, que trae instalados `p4c`, BMv2, Mininet y P4Runtime (usuario `p4`, contraseña `p4`).

```bash
git clone https://github.com/Danbag17/P4.git
cd P4/assignments/basic
make run        # compila el programa P4 y arranca la topología en Mininet
```

Dentro de Mininet:

```bash
mininet> pingall
mininet> exit
```

Para parar y limpiar:

```bash
make stop       # para Mininet
make clean      # además borra build/, logs/ y pcaps/
```

En las prácticas con controlador (`p4runtime`, `controlled_load_balance`), el controlador se lanza en otra terminal mientras Mininet está en marcha:

```bash
python3 mycontroller.py            # práctica p4runtime
python3 balance_controller.py      # práctica controlled_load_balance
```

## Documentación de referencia

- [BMv2 simple_switch](https://github.com/p4lang/behavioral-model/blob/main/docs/simple_switch.md): descripción de la arquitectura v1model.
- [`v1model.p4`](https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4): definición comentada de la arquitectura.
- [Especificación de P4₁₆](https://p4.org/specs/)

## Créditos

Los enunciados, el código base, las utilidades y las diapositivas son material del curso ANET de la University of Twente, basado en los [tutoriales oficiales de P4](https://github.com/p4lang/tutorials).
Las soluciones de las carpetas `assignments/` son mías.

Licencia: [Apache 2.0](./LICENSE).
