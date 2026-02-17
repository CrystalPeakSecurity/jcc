# JCC - LLVM IR to JavaCard Compiler

Compiles LLVM IR to JavaCard bytecode (CAP files). Any language with an LLVM frontend (C, Rust, etc.) can target JavaCard smart cards.

## Quick Start

```bash
git clone https://github.com/CrystalPeakSecurity/jcc.git
cd jcc
just setup              # guided setup (downloads JCDK, simulator)
just check              # type checker + tests
just sim examples/2048  # load a project in the simulator
just run examples/2048  # runs a project's driver
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
jcc examples/minimal     # A minimal example
jcc examples/2048        # The game 2048
jcc examples/flappy      # Flappy Bird
jcc examples/rusty       # Flappy Bird - in rust!
jcc examples/apple       # Bad Apple
jcc examples/musicvideo  # A music video
jcc examples/doom        # DOOM renderer
jcc examples/wolf3d      # Wolfenstein 3D renderer
```

Additional examples and tests are in the `examples/` directory.

## Project Structure

- `src/jcc/` - Compiler (LLVM IR parser, analysis, codegen, output)
- `src/jcc/cli/` - CLI (`jcc`, `jcc run-sim`, `jcc run-verify`, `jcc run-setup`)
- `src/jcc/cap/` - CAP file bytecode verifier
- `src/jcc/driver/` - Simulator/card session management
- `examples/` - Example applets with drivers
- `tools/` - Development utilities

## License

MIT
