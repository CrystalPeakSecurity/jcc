# JCC - LLVM IR to JavaCard Compiler

Compiles LLVM IR to JavaCard bytecode (CAP files). Any language with an LLVM frontend (C, Rust, etc.) can target JavaCard smart cards.

## Prerequisites

`jcc` uses `just` for running commands - installation instructions are [here](https://github.com/casey/just?tab=readme-ov-file#installation)

## Quick Start

```bash
git clone <repo>
cd jcc
just setup      # Guided setup (installs deps, downloads SDKs)
just check      # Run type checker and tests
```

## Usage

```bash
# Build a project (compiles C → LLVM IR → CAP)
just build examples/minimal

# Load onto simulator and run interactively
just load examples/doom
just run examples/doom
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
just build examples/doom        # DOOM
just build examples/2048        # 2048 game
just build examples/flappy      # Flappy Bird
just build examples/synth       # Music synthesizer
just build examples/apple       # Bad Apple
just build examples/musicvideo  # A music video
just build examples/wolf3d      # Wolfenstein 3D
```

## Project Structure

- `src/jcc/` - Compiler source (LLVM IR parser, analysis, codegen, output)
- `examples/` - Example applets
- `include/jcc.h` - C header with APDU functions
- `tools/` - CAP file analysis utilities
- `corpus/` - LLVM IR test fixtures


## License

MIT
