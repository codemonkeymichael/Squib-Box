# Squib-Box: DMX Theater Control System

A **Raspberry Pi Pico + MAX485** DMX receiver for firing theater effects from any standard DMX controller.

## What It Does

- Receives DMX512 signals from your lighting desk
- Controls 16 independent GPIO outputs
- Channel 1: Level control (HIGH/LOW)
- Channels 2-16: 250ms pulse triggers
- 3-frame debouncing for reliability

## Hardware

- Raspberry Pi Pico W
- MAX485 RS485 transceiver
- Any DMX controller with XLR output (Enttec, Chauvet, ETC, QLC+, etc.)
- Relay modules for load switching

## Quick Start

1. Flash MicroPython to Pico: `RPI_PICO2-20241129-v1.24.1.uf2`
2. Upload `dmx_receiver.py` to Pico
3. Wire MAX485 module (see diagram)
4. Connect DMX controller to MAX485
5. Power on

## Wiring

**MAX485 to Pico:**
| MAX485 | Pico |
|--------|------|
| VCC | 3.3V |
| GND | GND |
| RO | GPIO 5 |
| DE, RE | GND |
| A, B | DMX XLR 3, 2 |

**GPIO Outputs:**
- GPIO 2: Channel 1 (level control)
- GPIO 3-4, 6-18: Channels 2-16 (pulse triggers)

⚠️ **A/B Polarity**: If all channels read 0, swap the A/B wires at MAX485.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No data | Check MAX485 wiring and A/B polarity |
| No triggers | Move DMX faders above 100 |
| Intermittent | Add capacitor to MAX485 power pin |

## Files

- `dmx_receiver.py` – Main receiver script
- `.instructions.md` – Detailed technical docs
- `RPI_PICO2-*.uf2` – MicroPython firmware

**For detailed setup and technical deep-dive, see `.instructions.md`**