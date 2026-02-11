# Test Corpus

LLVM IR files for testing the jcc compiler. These are compiled examples.

## Files

| File | Source | Description |
|------|--------|-------------|
| `minimal.ll` | C | Minimal applet with APDU handling |
| `minimal_loop.ll` | C | Minimal with loop constructs |
| `debug.ll` | C | Debug/test applet |
| `stats.ll` | C | Statistics example |
| `apple.ll` | C | Apple II emulator game |
| `flappy.ll` | C | Flappy Bird game |
| `2048.ll` | C | 2048 puzzle game |
| `correctness.ll` | C | Comprehensive correctness tests |
| `rusty.ll` | Rust | Rust-compiled example |

## Regenerating

To regenerate from the JCC project:

```bash
# From jcc directory
just build examples/minimal/main.c
just build examples/2048/main.c
# etc.

# Then copy
cp examples/*/build/main.ll corpus/<name>.ll
```
