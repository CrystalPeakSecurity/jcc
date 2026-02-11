"""Analysis phases for jcc.

Each analysis phase:
- Takes typed inputs from previous phases
- Produces an immutable, validated output
- Is independently testable

Module-level analyses:
- build_call_graph (callgraph.py): Call graph with cycle detection and topological order
- allocate_globals (globals.py): Allocate globals into MEM_* arrays using debug info

Per-function analyses:
- analyze_phis (phi.py): Phi sources, webs, and coalescing
- analyze_narrowing (narrowing.py): i32 -> i16 narrowing opportunities
- analyze_escapes (escape.py): Which values need local slots
"""
