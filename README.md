# Squib-Box: DMX Theater Control System

A **Raspberry Pi Pico + MAX485** DMX receiver for firing theater effects from any standard DMX controller.

## What It Does

- Receives DMX512 signals from your lighting desk
- Controls 16 independent GPIO outputs
- DMX Channel 3: Level control (GPIO 2, HIGH/LOW)
- DMX Channels 4-18: 250ms pulse triggers (GPIO 3-4, 6-18)
- 3-frame debouncing for reliability

## Hardware

- Raspberry Pi Pico W
- MAX485 RS485 transceiver
- Any DMX controller with XLR output (Enttec, Chauvet, ETC, QLC+, etc.)
- Relay modules for load switching

## Quick Start

1. Flash MicroPython to Pico: `RPI_PICO2-20241129-v1.24.1.uf2`
2. Upload `main.py` to Pico
3. Wire MAX485 module (see diagram)
4. Connect DMX controller to MAX485
5. Unplug/replug Pico – script autorun on boot

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
- GPIO 2: DMX Channel 3 (level control)
- GPIO 3-4, 6-18: DMX Channels 4-18 (pulse triggers)

**Complete DMX Channel to GPIO Mapping:**

| DMX Channel | GPIO | Behavior |
|-------------|------|----------|
| 3 | 2 | Level control (HIGH > 100, LOW ≤ 100) |
| 4 | 3 | Pulse on rising edge |
| 5 | 4 | Pulse on rising edge |
| 6 | 6 | Pulse on rising edge |
| 7 | 7 | Pulse on rising edge |
| 8 | 8 | Pulse on rising edge |
| 9 | 9 | Pulse on rising edge |
| 10 | 10 | Pulse on rising edge |
| 11 | 11 | Pulse on rising edge |
| 12 | 12 | Pulse on rising edge |
| 13 | 13 | Pulse on rising edge |
| 14 | 14 | Pulse on rising edge |
| 15 | 15 | Pulse on rising edge |
| 16 | 16 | Pulse on rising edge |
| 17 | 17 | Pulse on rising edge |
| 18 | 18 | Pulse on rising edge |

⚠️ **A/B Polarity**: If all channels read 0, swap the A/B wires at MAX485.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No data | Check MAX485 wiring and A/B polarity |
| No triggers | Move DMX faders above 100 |
| Intermittent | Add capacitor to MAX485 power pin |

## Files

- `main.py` – Main receiver script (auto-runs on Pico boot)
- `.instructions.md` – Detailed technical docs
- `RPI_PICO2-*.uf2` – MicroPython firmware

**For detailed setup and technical deep-dive, see `.instructions.md`**