# JCC - C-to-JavaCard Compiler

Write JavaCard applets in C. Compiles a restricted C subset to JavaCard bytecode (JCA).

## Prerequisites

`jcc` uses `just` for running commands - installation instructions are [here](https://github.com/casey/just?tab=readme-ov-file#installation)

## Quick Start

```bash
git clone <repo>
cd jcc
just setup      # Install dependencies (see below for manual steps)
just test-fast  # Verify installation
```

## Requirements

- Python 3.14+ and [uv](https://docs.astral.sh/uv/)
- Java 17+
- [Oracle JavaCard SDK](https://www.oracle.com/java/technologies/javacard-downloads.html) - extract to `etc/jcdk/`
- [Oracle JavaCard Simulator](https://www.oracle.com/java/technologies/javacard-downloads.html) (optional) - extract to `etc/jcdk-sim/`

Run `just setup` for platform-specific instructions.

## Usage

```bash
# Compile C to JavaCard
just compile examples/minimal/main.c

# Test on simulator
just run examples/minimal/main.c

# Deploy to real card
just card-install examples/minimal/main.c
```

## Example

```c
#include "jcc.h"

short count;

void process(APDU apdu, short len) {
    byte* buffer = apduGetBuffer(apdu);
    if (buffer[APDU_INS] == 0x01) {
        count++;
        buffer[0] = (byte)(count >> 8);
        buffer[1] = (byte)count;
        apduSetOutgoing(apdu);
        apduSetOutgoingLength(apdu, 2);
        apduSendBytes(apdu, 0, 2);
    }
}
```

## Examples

```bash
just demo-sim doom        # DOOM on simulator
just demo-sim 2048        # 2048 game
just demo-sim flappy      # Flappy Bird
just demo-sim synth       # Music synthesizer
just demo-sim apple       # Bad Apple
just demo-sim musicvideo  # A music video
```

## Project Structure

- `src/jcc/` - Compiler source
- `examples/` - Example applets
- `include/jcc.h` - C header with APDU functions
- `etc/` - External tools (SDK, simulator, GlobalPlatformPro)

## License

MIT
