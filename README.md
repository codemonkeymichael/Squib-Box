# Squib-Box: DMX Theater Control System

A **Raspberry Pi Pico + MAX485** DMX receiver for firing theater effects (squibs, lights, motors, etc.) from QLC+ lighting software.

## Features

✅ **16 independent GPIO triggers** – one per DMX channel  
✅ **3-frame debouncing** – theater-grade reliability (~70ms response)  
✅ **Edge detection** – Channel 1 fires on falling edge (OFF), Channels 2-16 on rising edge (ON)  
✅ **DMX break detection** – proper frame synchronization  
✅ **250ms GPIO pulse** – clean relay/mosfet activation  
✅ **Real-time monitoring** – prints channel values for debugging  

## Hardware Requirements

- **Raspberry Pi Pico** (RP2040)
- **MAX485 TTL-to-RS485 module** (~$2-3)
- **Enttec DMX USB Pro** or compatible DMX controller
- **Relay modules** or mosfet drivers for load switching
- **Standard DMX XLR cables** (3-pin)

## Quick Start

1. Flash MicroPython to Pico
2. Upload `main2026.py` as `main.py` to Pico
3. Wire MAX485 module (see Wiring section)
4. Connect DMX cable from Enttec to MAX485
5. Wire GPIO outputs to relay modules
6. Power on – DMX receiver starts automatically

## Wiring

### MAX485 Module to Pico

| MAX485 Pin | Pico Pin | Purpose |
|-----------|----------|---------|
| VCC | 3.3V | Power |
| GND | GND | Ground |
| RO | GPIO 5 | DMX data (UART1 RX) |
| DE, RE | GND | Receive mode only |
| A, B | DMX XLR 3, 2 | RS485 signal |

### GPIO Trigger Outputs to Relays

| Channel | GPIO | Trigger |
|---------|------|---------|
| 1 | GPIO 2 | Falling edge (OFF) |
| 2-16 | GPIO 3-4, 6-18 | Rising edge (ON) |

## QLC+ Usage

1. Set Channel 1 HIGH (>100) – turn LOW to fire main trigger
2. Set Channels 2-16 LOW (≤100) – turn ON to fire effects
3. Each channel transition triggers a 250ms GPIO pulse

## How It Works

- **DMX break detection** syncs to frame start
- **3-frame debouncing** ensures reliability
- **Edge detection** monitors channel transitions
- **GPIO pulse** fires relay/mosfet on state change
- **Continuous loop** ready for next cue

## Relay Wiring Example

```
GPIO pin (3.3V)
    ↓
[470Ω resistor]
    ↓
[Transistor / Relay coil]
    ↓
[1N4007 diode to GND]  ← Protection
    ↓
[Relay contacts → Load]
```

## Troubleshooting

**No data:** Check MAX485 wiring and A/B polarity  
**No triggers:** Verify GPIO wiring and QLC+ channel values >100  
**Intermittent:** Add flyback diodes, check solder joints  

See `.instructions.md` for detailed technical notes.

## Files

- `main2026.py` – DMX receiver + 16-channel triggers (production)
- `.instructions.md` – Technical deep-dive and project history
- `RPI_PICO2-*.uf2` – MicroPython firmware

## Author Notes

Built for reliable theater shows. Tested with Enttec DMX USB Pro + QLC+ 4.13.1. Response time ~70-75ms (acceptable for mechanical effects).

---

*For detailed setup and troubleshooting, see `.instructions.md`*