#!/usr/bin/env python3
"""Comprehensive JCVM instruction benchmark driver.

Measures per-iteration cost of every JCVM instruction we emit.
All benchmarks use identical loop structure; only the body varies.
Bodies are stack-neutral (net 0 stack effect). The NOP baseline
measures pure loop overhead; subtracting it gives the body cost.
Generates results.html with isolated per-instruction cost visualization.
"""

import json
import sys
import time
from pathlib import Path

from jcc.driver import BaseDriver

BENCHMARKS = [
    # (name, description, body_insns)
    # INS byte = 0x10 + index in this list (0x10..0x4D)
    # body_insns = number of instructions in the body (excluding loop overhead)

    # 0x10  Constants
    ("nop",             "nop",                                  1),  # 0
    ("sconst",          "sconst_5; pop",                       2),  # 1
    ("bspush",          "bspush 5; pop",                       2),  # 2
    ("sspush",          "sspush 5; pop",                       2),  # 3
    # 0x14  Local variable access
    ("sload",           "sload_3; pop",                        2),  # 4
    ("sstore_sload",    "sconst_5; sstore_3",                  2),  # 5
    ("iload_i2s",       "iload 3; pop2",                      2),  # 6
    ("istore_iload",    "iconst_5; istore",                    2),  # 7
    ("sinc_sload",      "sinc 3 1",                            1),  # 8
    # 0x19  Short arithmetic
    ("sadd",            "sconst_5; sconst_3; sadd; pop",      4),  # 9
    ("ssub",            "sconst_5; sconst_3; ssub; pop",      4),  # 10
    ("smul",            "sconst_5; sconst_3; smul; pop",      4),  # 11
    ("sdiv",            "sconst_5; sconst_3; sdiv; pop",      4),  # 12
    ("srem",            "sconst_5; sconst_3; srem; pop",      4),  # 13
    ("sneg",            "sconst_5; sneg; pop",                 3),  # 14
    ("sand",            "sconst_5; sconst_3; sand; pop",      4),  # 15
    ("sor",             "sconst_5; sconst_3; sor; pop",       4),  # 16
    ("sxor",            "sconst_5; sconst_3; sxor; pop",      4),  # 17
    ("sshl",            "sconst_5; sconst_3; sshl; pop",      4),  # 18
    ("sshr",            "sconst_5; sconst_3; sshr; pop",      4),  # 19
    ("sushr",           "sconst_5; sconst_3; sushr; pop",     4),  # 20
    # 0x25  Type conversions & stack ops
    ("s2b",             "sconst_5; s2b; pop",                  3),  # 21
    ("s2i_i2s",         "iconst_5; i2s; pop",                  3),  # 22
    ("dup",             "sconst_5; dup; pop; pop",             4),  # 23
    ("pop",             "sconst_5; sconst_3; pop; pop",       4),  # 24
    ("if_scmplt",       "sconst_3; sconst_5; if_scmplt L; L:", 3), # 25
    ("ifeq",            "sconst_5; ifeq L; L:",               2),  # 26
    # 0x2A  Array access
    ("baload",          "getstatic_a; sconst_0; baload; pop", 4),  # 27
    ("saload",          "getstatic_a; sconst_1; saload; pop", 4),  # 28
    ("ba_roundtrip",    "bastore + baload round-trip; pop",    8),  # 29
    ("sa_roundtrip",    "sastore + saload round-trip; pop",    8),  # 30
    ("getstatic_a",     "getstatic_a; pop",                   2),  # 31
    # 0x2F  Method invocation
    ("invokestatic",    "invokestatic bench_empty; pop",       4),  # 32
    ("invoke_void",     "invokestatic bench_empty_void",       2),  # 33
    # 0x31  Int arithmetic
    ("iadd",            "iconst_5; iconst_3; iadd; pop2",     4),  # 34
    ("isub",            "iconst_5; iconst_3; isub; pop2",     4),  # 35
    ("imul",            "iconst_5; iconst_3; imul; pop2",     4),  # 36
    ("idiv",            "iconst_5; iconst_3; idiv; pop2",     4),  # 37
    ("irem",            "iconst_5; iconst_3; irem; pop2",     4),  # 38
    ("ineg",            "iconst_5; ineg; pop2",                3),  # 39
    ("iand",            "iconst_5; iconst_3; iand; pop2",     4),  # 40
    ("ior",             "iconst_5; iconst_3; ior; pop2",      4),  # 41
    ("ixor",            "iconst_5; iconst_3; ixor; pop2",     4),  # 42
    ("ishl",            "iconst_5; iconst_3; ishl; pop2",     4),  # 43
    ("ishr",            "iconst_5; iconst_3; ishr; pop2",     4),  # 44
    ("iushr",           "iconst_5; iconst_3; iushr; pop2",    4),  # 45
    # 0x3D  Int constants
    ("iconst",          "iconst_5; pop2",                      2),  # 46
    ("bipush_int",      "bipush 5; pop2",                      2),  # 47
    ("sipush_int",      "sipush 5; pop2",                      2),  # 48
    ("iipush",          "iipush 5; pop2",                      2),  # 49
    # 0x41  More conversions
    ("i2b",             "iconst_5; i2b; pop",                  3),  # 50
    ("icmp",            "iconst_5; iconst_3; icmp; pop",       4),  # 51
    # 0x43  Int locals
    ("iinc",            "iinc 3 1",                            1),  # 52
    # 0x44  Stack
    ("pop2",            "iconst_5; pop2",                      2),  # 53
    # 0x45  More branches
    ("ifne",            "sconst_5; ifne L; L:",               2),  # 54
    ("if_scmpeq",       "sconst_5; sconst_5; if_scmpeq L; L:", 3), # 55
    # 0x47  Reference locals
    ("aload",           "aload_3; pop",                       2),  # 56
    # 0x48  Control flow
    ("goto_w",          "goto_w L; L:",                       1),  # 57
    # 0x49  More invocation
    ("ireturn",         "invokestatic bench_iret; pop2",      4),  # 58
    ("pop2_baseline",   "sconst_5; sconst_3; pop2",            3),  # 59
    # 0x4B  Switch
    ("slookupswitch",   "sconst; slookupswitch; L:",          2),  # 60
    ("stableswitch",    "sconst; stableswitch; L:",           2),  # 61
    # 0x4E  Baseline
    ("empty",            "(empty body, baseline)",              0),  # 62
    # 0x4F  Exception calibration
    ("exc_baseline",     "aconst_null; athrow (exc calib)",    3),  # 63
    ("exc_sconst",       "sconst_5; aconst_null; athrow",     4),  # 64
    ("exc_iconst",       "iconst_5; aconst_null; athrow",     4),  # 65
    ("exc_sload",        "sload_3; aconst_null; athrow",      4),  # 66
    # 0x53  Baselines
    ("int_baseline",     "iconst_5; iconst_3; pop2; pop2",    4),  # 67
    ("arr_baseline",     "getstatic_a; sconst_0; pop; pop",   4),  # 68
    # 0x55  Instance field access
    ("getfield_a_this",  "getfield_a_this; pop",               2),  # 69
    # 0x56  Array stores
    ("bastore",          "getstatic_a; sconst_0; sconst_5; bastore", 4),  # 70
    ("sastore",          "getstatic_a; sconst_1; sconst_5; sastore", 4),  # 71
    # 0x58  Array baseline (pop2)
    ("arr_baseline2",    "getstatic_a; sconst_0; pop2",        3),  # 72
    # 0x59  EEPROM array access
    ("eeprom_baload",    "getstatic_a EEPROM; sconst_0; baload; pop", 4),  # 73
    ("eeprom_bastore",   "getstatic_a EEPROM; sconst_0; sconst_5; bastore", 4),  # 74
    ("empty_eeprom",      "(empty body, 1-iter baseline)",             0),  # 75
    # 0x5C  Linear array access (index = loop counter, 1000 bytes)
    ("linear_baseline",   "getstatic_a; sload_0; sconst_5; pop2; pop", 5),  # 76
    ("ram_linear_read",   "getstatic_a RAM; sload_0; baload; pop",     4),  # 77
    ("eeprom_linear_read", "getstatic_a EEPROM; sload_0; baload; pop", 4),  # 78
    ("ram_linear_write",  "getstatic_a RAM; sload_0; sconst_5; bastore", 4),  # 79
    ("eeprom_linear_write", "getstatic_a EEPROM; sload_0; sconst_5; bastore", 4),  # 80
    # 0x61  Direct static field access (vs array pattern)
    ("getstatic_b",      "getstatic_b; pop",                    2),  # 81
    ("putstatic_b",      "sconst_5; putstatic_b",               2),  # 82
    ("getstatic_s",      "getstatic_s; pop",                    2),  # 83
    ("putstatic_s",      "sconst_5; putstatic_s",               2),  # 84
]

# Benchmarks with a fixed iteration count (overrides --iters).
FIXED_ITERS: dict[str, int] = {
}

# Benchmarks skipped unless --eeprom is passed.
EEPROM_BENCHMARKS = {
    "eeprom_baload", "eeprom_bastore", "empty_eeprom",
    "linear_baseline", "ram_linear_read", "eeprom_linear_read",
    "ram_linear_write", "eeprom_linear_write",
}


def _get(results, name):
    """Get avg_ms for a benchmark by name, or None."""
    for n, _, _, avg in results:
        if n == name:
            return avg
    return None


def _adj(results, name, nop):
    """Get adjusted ms (above NOP baseline) for a benchmark, or 0."""
    v = _get(results, name)
    return (v - nop) if v is not None else 0.0


def _save_results(results, iterations, runs, suites, output_path):
    """Save raw benchmark results to JSON."""
    data = {
        "iterations": iterations,
        "runs": runs,
        "suites": suites,
        "benchmarks": [
            {"name": name, "desc": desc, "body_insns": body_insns, "avg_ms": avg}
            for name, desc, body_insns, avg in results
        ],
    }
    output_path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Wrote {output_path}")


def _load_results(input_path):
    """Load benchmark results from JSON. Returns (results, iterations, runs, suites)."""
    data = json.loads(input_path.read_text())
    results = [
        (b["name"], b["desc"], b["body_insns"], b["avg_ms"])
        for b in data["benchmarks"]
    ]
    return results, data["iterations"], data["runs"], data["suites"]


def _generate_html(results, iterations, runs, suites, output_path):
    """Generate results.html with raw measured benchmark costs.

    Shows honest measured data grouped by stack profile (push/pop count).
    No decomposition — push and pop costs cannot be separated from
    stack-neutral benchmarks, so we don't try.
    """
    baseline = _get(results, "empty") or 0.0
    baseline_1iter = _get(results, "empty_eeprom") or 0.0

    def m(name):
        """Adjusted microseconds per iteration for a benchmark."""
        v = _get(results, name)
        if v is None:
            return 0.0
        actual_iters = FIXED_ITERS.get(name, iterations)
        if actual_iters != iterations and baseline_1iter > 0:
            bl = baseline_1iter
        else:
            bl = baseline
        adj = v - bl
        return max(0.0, (adj * 1000) / actual_iters if actual_iters > 0 else 0.0)

    # Each entry: (cat, label, us_value, insns, scaffold)
    # label includes push/pop counts inline: "[pushN popM] instruction"
    # Grouped by stack profile so within-group comparisons are exact.
    S5 = "sconst 5"
    S3 = "sconst 3"
    I5 = "iconst 5"
    I3 = "iconst 3"

    # Lookup: benchmark name -> body_insns
    _insns = {name: bi for name, _, bi in BENCHMARKS}

    def mi(name):
        return _insns.get(name, 0)

    # Scaffold: number of *const / pop / pop2 instructions in each body.
    # Weight classification subtracts these (at ~2.8us each) to isolate
    # the cost of the "interesting" instructions.
    _scaffold = {
        "nop": 0, "sconst": 2, "bspush": 1, "sspush": 1,
        "sload": 1, "sstore_sload": 1, "iload_i2s": 1, "istore_iload": 1,
        "sinc_sload": 0,
        "sadd": 3, "ssub": 3, "smul": 3, "sdiv": 3, "srem": 3,
        "sneg": 2, "sand": 3, "sor": 3, "sxor": 3,
        "sshl": 3, "sshr": 3, "sushr": 3,
        "s2b": 2, "s2i_i2s": 2, "dup": 3, "pop": 4,
        "if_scmplt": 2, "ifeq": 1,
        "baload": 2, "saload": 2, "ba_roundtrip": 3, "sa_roundtrip": 3,
        "getstatic_a": 1,
        # invokestatic: caller pop + callee sconst = 2
        "invokestatic": 2,
        # invoke_void: no scaffold (caller: invokestatic, callee: return)
        "invoke_void": 0,
        "iadd": 3, "isub": 3, "imul": 3, "idiv": 3, "irem": 3,
        "ineg": 2, "iand": 3, "ior": 3, "ixor": 3,
        "ishl": 3, "ishr": 3, "iushr": 3,
        "iconst": 2, "bipush_int": 1, "sipush_int": 1, "iipush": 1,
        "i2b": 2, "icmp": 3,
        "iinc": 0, "pop2": 2,
        "ifne": 1, "if_scmpeq": 2,
        "aload": 1, "goto_w": 0,
        # ireturn: caller pop2 + callee iconst = 2
        "ireturn": 2,
        "pop2_baseline": 3,
        "slookupswitch": 1, "stableswitch": 1,
        "empty": 0,
        "exc_baseline": 2, "exc_sconst": 3, "exc_iconst": 3, "exc_sload": 2,
        "int_baseline": 4, "arr_baseline": 3,
        "getfield_a_this": 1,
        "bastore": 2, "sastore": 2,
        "arr_baseline2": 2,
        "eeprom_baload": 2, "eeprom_bastore": 2, "empty_eeprom": 0,
        "linear_baseline": 3,
        "ram_linear_read": 1, "eeprom_linear_read": 1,
        "ram_linear_write": 1, "eeprom_linear_write": 1,
        "getstatic_b": 1, "putstatic_b": 1,
        "getstatic_s": 1, "putstatic_s": 1,
    }

    def sc(name):
        return _scaffold.get(name, 0)

    def _i(bench, **kw):
        """Build an item dict with insns and scaffold looked up by benchmark name."""
        return {"insns": mi(bench), "scaffold": sc(bench), **kw}

    data = [
        {"section": "0 Push, 0 Pop", "items": [
            _i("goto_w",     cat="cf",    name="goto_w L; L:",            us=m("goto_w")),
            _i("sinc_sload", cat="short", name="sinc 3 1",                us=m("sinc_sload"), gap=True),
            _i("iinc",       cat="int",   name="iinc 3 1",                us=m("iinc"), tight=True),
            _i("nop",        cat="nop",   name="nop",                     us=m("nop"), gap=True),
            _i("invoke_void",cat="inv",   name="invokestatic (void)",     us=m("invoke_void"), gap=True),
        ]},
        {"section": "1 Push, 1 Pop (short)", "baseline": m("sconst"), "items": [
            _i("sconst",     cat="short", name=f"{S5}; pop",              us=m("sconst")),
            _i("bspush",     cat="short", name="bspush 5; pop",           us=m("bspush"), tight=True),
            _i("sspush",     cat="short", name="sspush 5; pop",           us=m("sspush"), tight=True),
            _i("sload",      cat="short", name="sload; pop",              us=m("sload"), gap=True),
            _i("aload",      cat="ref",   name="aload; pop",              us=m("aload"), tight=True),
            _i("getstatic_a",cat="ref",   name="getstatic_a; pop",        us=m("getstatic_a"), tight=True),
            _i("getfield_a_this", cat="ref", name="getfield_a_this; pop", us=m("getfield_a_this"), tight=True),
            _i("sstore_sload", cat="short", name=f"{S5}; sstore",         us=m("sstore_sload"), gap=True),
            _i("sneg",       cat="conv",  name=f"{S5}; sneg; pop",        us=m("sneg"), gap=True),
            _i("s2b",        cat="conv",  name=f"{S5}; s2b; pop",         us=m("s2b"), tight=True),
            _i("ifeq",       cat="cf",    name=f"{S5}; ifeq L; L:",       us=m("ifeq"), gap=True),
            _i("ifne",       cat="cf",    name=f"{S5}; ifne L; L:",       us=m("ifne"), tight=True),
            _i("slookupswitch", cat="cf",  name="sconst 1; slookupswitch L; L:", us=m("slookupswitch"), gap=True),
            _i("stableswitch",  cat="cf",  name="sconst 0; stableswitch L; L:",  us=m("stableswitch"), tight=True),
            _i("invokestatic",  cat="inv", name="invokestatic (short); pop", us=m("invokestatic"), gap=True),
        ]},
        {"section": "1 Push, 1 Pop (int)", "baseline": m("iconst"), "items": [
            _i("iconst",     cat="int",  name=f"{I5}; pop2",              us=m("iconst")),
            _i("bipush_int", cat="int",  name="bipush 5; pop2",           us=m("bipush_int"), tight=True),
            _i("sipush_int", cat="int",  name="sipush 5; pop2",           us=m("sipush_int"), tight=True),
            _i("iipush",     cat="int",  name="iipush 5; pop2",           us=m("iipush"), tight=True),
            _i("iload_i2s",  cat="int",  name="iload; pop2",              us=m("iload_i2s"), gap=True),
            _i("istore_iload", cat="int", name=f"{I5}; istore",           us=m("istore_iload"), gap=True),
            _i("s2i_i2s",    cat="conv", name=f"{I5}; i2s; pop",          us=m("s2i_i2s"), gap=True),
            _i("i2b",        cat="conv", name=f"{I5}; i2b; pop",          us=m("i2b"), tight=True),
            _i("ineg",       cat="int",  name=f"{I5}; ineg; pop2",        us=m("ineg"), gap=True),
            _i("ireturn",    cat="inv",  name="invokestatic (int); pop2", us=m("ireturn"), gap=True),
        ]},
        {"section": "2 Push, 2 Pop (short)", "baseline": m("pop2_baseline"), "items": [
            _i("pop2_baseline", cat="conv", name=f"{S5}; {S3}; pop2",       us=m("pop2_baseline")),
            _i("pop",        cat="conv",  name=f"{S5}; {S3}; pop; pop",   us=m("pop"), tight=True),
            _i("dup",        cat="conv",  name=f"{S5}; dup; pop; pop",    us=m("dup"), tight=True),
            _i("sadd",       cat="short", name=f"{S5}; {S3}; sadd; pop",  us=m("sadd"), gap=True),
            _i("ssub",       cat="short", name=f"{S5}; {S3}; ssub; pop",  us=m("ssub"), tight=True),
            _i("smul",       cat="short", name=f"{S5}; {S3}; smul; pop",  us=m("smul"), tight=True),
            _i("sdiv",       cat="short", name=f"{S5}; {S3}; sdiv; pop",  us=m("sdiv"), gap=True),
            _i("srem",       cat="short", name=f"{S5}; {S3}; srem; pop",  us=m("srem"), tight=True),
            _i("sand",       cat="short", name=f"{S5}; {S3}; sand; pop",  us=m("sand"), gap=True),
            _i("sor",        cat="short", name=f"{S5}; {S3}; sor; pop",   us=m("sor"), tight=True),
            _i("sxor",       cat="short", name=f"{S5}; {S3}; sxor; pop",  us=m("sxor"), tight=True),
            _i("sshl",       cat="short", name=f"{S5}; {S3}; sshl; pop",  us=m("sshl"), gap=True),
            _i("sshr",       cat="short", name=f"{S5}; {S3}; sshr; pop",  us=m("sshr"), tight=True),
            _i("sushr",      cat="short", name=f"{S5}; {S3}; sushr; pop", us=m("sushr"), tight=True),
            _i("if_scmplt",  cat="cf",    name=f"{S3}; {S5}; if_scmplt L; L:", us=m("if_scmplt"), gap=True),
            _i("if_scmpeq",  cat="cf",    name=f"{S5}; {S5}; if_scmpeq L; L:", us=m("if_scmpeq"), tight=True),
        ]},
        {"section": "2 Push, 2 Pop (int)", "baseline": m("int_baseline"), "items": [
            _i("int_baseline", cat="int", name=f"{I5}; {I3}; pop2; pop2", us=m("int_baseline")),
            _i("iadd",       cat="int", name=f"{I5}; {I3}; iadd; pop2",   us=m("iadd"), gap=True),
            _i("isub",       cat="int", name=f"{I5}; {I3}; isub; pop2",   us=m("isub"), tight=True),
            _i("imul",       cat="int", name=f"{I5}; {I3}; imul; pop2",   us=m("imul"), tight=True),
            _i("idiv",       cat="int", name=f"{I5}; {I3}; idiv; pop2",   us=m("idiv"), gap=True),
            _i("irem",       cat="int", name=f"{I5}; {I3}; irem; pop2",   us=m("irem"), tight=True),
            _i("iand",       cat="int", name=f"{I5}; {I3}; iand; pop2",   us=m("iand"), gap=True),
            _i("ior",        cat="int", name=f"{I5}; {I3}; ior; pop2",    us=m("ior"), tight=True),
            _i("ixor",       cat="int", name=f"{I5}; {I3}; ixor; pop2",   us=m("ixor"), tight=True),
            _i("ishl",       cat="int", name=f"{I5}; {I3}; ishl; pop2",   us=m("ishl"), gap=True),
            _i("ishr",       cat="int", name=f"{I5}; {I3}; ishr; pop2",   us=m("ishr"), tight=True),
            _i("iushr",      cat="int", name=f"{I5}; {I3}; iushr; pop2",  us=m("iushr"), tight=True),
            _i("icmp",       cat="int", name=f"{I5}; {I3}; icmp; pop",    us=m("icmp"), gap=True),
        ]},
        {"section": "Array Access", "baseline": m("arr_baseline2"), "items": [
            _i("arr_baseline2", cat="ref", name="getstatic_a; sconst 0; pop2",     us=m("arr_baseline2")),
            _i("arr_baseline",  cat="ref", name="getstatic_a; sconst 0; pop; pop", us=m("arr_baseline"), tight=True),
            _i("getstatic_b",cat="byte",  name="getstatic_b; pop (direct field)",              us=m("getstatic_b"), gap=True),
            _i("baload",     cat="byte",  name="getstatic_a; sconst 0; baload; pop (array)", us=m("baload"), tight=True),
            _i("getstatic_s",cat="short", name="getstatic_s; pop (direct field)",             us=m("getstatic_s"), gap=True),
            _i("saload",     cat="short", name="getstatic_a; sconst 1; saload; pop (array)",  us=m("saload"), tight=True),
            _i("putstatic_b",cat="byte",  name="sconst 5; putstatic_b (direct field)",        us=m("putstatic_b"), gap=True),
            _i("bastore",    cat="byte",  name="getstatic_a; sconst 0; sconst 5; bastore (array)", us=m("bastore"), tight=True),
            _i("putstatic_s",cat="short", name="sconst 5; putstatic_s (direct field)",        us=m("putstatic_s"), gap=True),
            _i("sastore",    cat="short", name="getstatic_a; sconst 1; sconst 5; sastore (array)", us=m("sastore"), tight=True),
            _i("ba_roundtrip", cat="byte", name="getstatic_a; sconst 0; sconst 5; bastore; baload; pop", us=m("ba_roundtrip"), gap=True),
            _i("sa_roundtrip", cat="short", name="getstatic_a; sconst 1; sconst 5; sastore; saload; pop", us=m("sa_roundtrip"), tight=True),
        ]},
        {"section": "Exceptions", "baseline": m("exc_baseline"), "items": [
            _i("exc_baseline", cat="nop",  name="aconst_null; athrow (baseline)", us=m("exc_baseline")),
            _i("exc_sconst", cat="short", name="sconst 5; aconst_null; athrow",  us=m("exc_sconst"), gap=True),
            _i("exc_iconst", cat="int",   name="iconst 5; aconst_null; athrow",  us=m("exc_iconst"), tight=True),
            _i("exc_sload",  cat="short", name="sload 3; aconst_null; athrow",   us=m("exc_sload"), tight=True),
        ]},
        {"section": "Linear Array Access (1000 bytes)", "baseline": m("linear_baseline"), "items": [
            _i("linear_baseline", cat="nop", name="getstatic_a; sload i; sconst 5; pop2; pop (baseline)", us=m("linear_baseline")),
            _i("ram_linear_read",    cat="byte", name="getstatic_a RAM; sload i; baload; pop",          us=m("ram_linear_read"), gap=True),
            _i("eeprom_linear_read", cat="byte", name="getstatic_a EEPROM; sload i; baload; pop",       us=m("eeprom_linear_read"), tight=True),
            _i("ram_linear_write",   cat="byte", name="getstatic_a RAM; sload i; sconst 5; bastore",    us=m("ram_linear_write"), gap=True),
            _i("eeprom_linear_write",cat="byte", name="getstatic_a EEPROM; sload i; sconst 5; bastore", us=m("eeprom_linear_write"), tight=True),
        ]},
    ]

    print(f"  {len([i for s in data for i in s['items']])} chart entries from raw measurements")

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>JCVM Instruction Benchmark</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'SF Mono', 'Menlo', 'Consolas', monospace; background: #0d1117; color: #c9d1d9; padding: 32px; max-width: 1200px; margin: 0 auto; }}
h1 {{ font-size: 20px; font-weight: 600; color: #f0f6fc; margin-bottom: 4px; }}
.subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 24px; }}
.section {{ margin-bottom: 20px; }}
.section-title {{
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px;
  color: #8b949e; margin-bottom: 6px; padding-bottom: 4px;
  border-bottom: 1px solid #21262d; cursor: pointer; user-select: none;
}}
.section-title:hover {{ color: #c9d1d9; }}
.section-title::before {{ content: '\\25BE '; font-size: 10px; }}
.section.collapsed .section-title::before {{ content: '\\25B8 '; }}
.section.collapsed .row {{ display: none; }}
.row {{
  display: grid; grid-template-columns: 420px 1fr 64px 58px 72px; align-items: center;
  height: 26px; gap: 0 6px;
}}
.row.gap {{ margin-top: 0px; }}
.row.tight {{ margin-top: -8px; }}
.label {{ font-size: 12px; color: #c9d1d9; padding-left: 4px; white-space: nowrap; }}
.bar-bg {{ height: 14px; background: #161b22; border-radius: 3px; position: relative; }}
.bar {{ height: 100%; border-radius: 3px; min-width: 2px; }}
.baseline-mark {{ position: absolute; top: -1px; bottom: -1px; width: 2px; background: rgba(255,255,255,0.6); z-index: 1; }}
.value {{ font-size: 12px; text-align: right; font-variant-numeric: tabular-nums; color: #8b949e; }}
.delta {{ font-size: 12px; display: flex; justify-content: space-between; font-variant-numeric: tabular-nums; color: #c9d1d9; padding: 0 10px 0 12px; }}
.weight {{ font-size: 10px; text-align: center; border-radius: 3px; padding: 1px 6px; font-weight: 600; white-space: nowrap; }}
.weight.w-light   {{ background: #1a3a2a; color: #3fb950; }}
.weight.w-moderate {{ background: #3a3520; color: #d29922; }}
.weight.w-heavy   {{ background: #3a2a1a; color: #e87b3a; }}
.weight.w-turtle  {{ background: #3a1a1a; color: #ee4f4f; }}
.weight.w-glacial {{ background: #2a1a3a; color: #bc8cff; }}
.weight.w-danger  {{ background: #000; color: #BBB; border: 1px solid #BBB; }}
.cat-byte .bar  {{ background: linear-gradient(90deg, #c98a1d, #e3b341); }}
.cat-short .bar {{ background: linear-gradient(90deg, #cc6228, #e87b3a); }}
.cat-int .bar   {{ background: linear-gradient(90deg, #cc3838, #ee4f4f); }}
.cat-conv .bar  {{ background: linear-gradient(90deg, #2ea8a1, #39d2c0); }}
.cat-cf .bar    {{ background: linear-gradient(90deg, #388bfd, #58a6ff); }}
.cat-inv .bar   {{ background: linear-gradient(90deg, #db61a2, #f778ba); }}
.cat-ref .bar   {{ background: linear-gradient(90deg, #a371f7, #bc8cff); }}
.cat-nop .bar   {{ background: linear-gradient(90deg, #6e7681, #8b949e); }}
.legend {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }}
.legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 11px; color: #8b949e; }}
.legend-dot {{ width: 10px; height: 10px; border-radius: 2px; }}
.note {{
  font-size: 11px; color: #8b949e; margin-top: 20px; padding: 12px;
  background: #161b22; border-radius: 6px; border: 1px solid #21262d; line-height: 1.7;
}}
.note strong {{ color: #c9d1d9; }}
.note code {{ color: #58a6ff; font-size: 11px; }}
</style>
</head>
<body>
<h1>JCVM Instruction Cost (Raw Measurements)</h1>
<div class="subtitle">J3R180 &mdash; {iterations} iters &times; {runs} runs &times; {suites} suites (drop hi/lo) &mdash; empty-loop baseline subtracted</div>
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#e3b341"></div>Byte</div>
  <div class="legend-item"><div class="legend-dot" style="background:#e87b3a"></div>Short</div>
  <div class="legend-item"><div class="legend-dot" style="background:#ee4f4f"></div>Int</div>
  <div class="legend-item"><div class="legend-dot" style="background:#39d2c0"></div>Conversion / Stack</div>
  <div class="legend-item"><div class="legend-dot" style="background:#58a6ff"></div>Control Flow</div>
  <div class="legend-item"><div class="legend-dot" style="background:#f778ba"></div>Invocation</div>
  <div class="legend-item"><div class="legend-dot" style="background:#bc8cff"></div>Reference</div>
  <div class="legend-item"><div class="legend-dot" style="background:#8b949e"></div>Other</div>
</div>
<div id="chart"></div>
<div class="note">
  <strong>Methodology:</strong> Each bar shows the raw measured cost of a complete stack-neutral instruction sequence,
  with the empty-loop baseline subtracted. Benchmarks are grouped by stack profile (push/pop count) so that
  comparisons <em>within</em> a group are exact. Comparisons across groups with different push/pop counts include
  an ambiguous push/pop overhead that cannot be separated from stack-neutral measurements.
</div>
<script>
const data = {json.dumps(data)};
const chart = document.getElementById('chart');
const sections = [];
data.forEach(section => {{
  const div = document.createElement('div');
  div.className = 'section';
  const title = document.createElement('div');
  title.className = 'section-title';
  title.textContent = section.section;
  title.addEventListener('click', () => {{
    div.classList.toggle('collapsed');
    rescale();
  }});
  div.appendChild(title);
  const rows = [];
  const bl = section.baseline || 0;
  section.items.forEach((item, idx) => {{
    const us = Math.max(0, item.us);
    const row = document.createElement('div');
    let cls = `row cat-${{item.cat}}`;
    if (item.gap) cls += ' gap';
    if (item.tight) cls += ' tight';
    row.className = cls;
    const delta = bl > 0 ? us - bl : 0;
    const isBaseline = bl > 0 && idx === 0;
    const deltaSign = (bl > 0 && !isBaseline) ? (delta >= 0 ? '+' : '\u2212') : '';
    const deltaNum = (bl > 0 && !isBaseline) ? Math.abs(delta).toFixed(1) : '';
    const insns = item.insns || 0;
    const scaff = item.scaffold || 0;
    const adjInsns = insns - scaff;
    const adjUs = us - scaff * 2.8;
    const BASELINE = 2.8;
    let wLabel = '', wCls = '';
    if (insns > 0) {{
      let uspi;
      if (adjInsns <= 0) {{ uspi = BASELINE; }}
      else {{ uspi = adjUs / adjInsns; }}
      const mult = uspi / BASELINE;
      if (mult < 1.4)       {{ wCls = 'w-light'; }}
      else if (mult < 1.6)  {{ wCls = 'w-moderate'; }}
      else if (mult < 2.25) {{ wCls = 'w-heavy'; }}
      else if (mult < 3.2)  {{ wCls = 'w-turtle'; }}
      else if (mult < 5.7)  {{ wCls = 'w-glacial'; }}
      else                   {{ wCls = 'w-danger'; }}
      wLabel = mult.toFixed(1) + 'x';
    }}
    const weightHtml = wLabel ? `<div class="weight ${{wCls}}">${{wLabel}}</div>` : `<div class="weight"></div>`;
    row.innerHTML = `
      <div class="label">${{item.name}}</div>
      <div class="bar-bg"><div class="bar"></div></div>
      <div class="value">${{us.toFixed(1)}} us</div>
      <div class="delta"><span>${{deltaSign}}</span><span>${{deltaNum}}</span></div>
      ${{weightHtml}}`;
    div.appendChild(row);
    rows.push({{ el: row, us }});
  }});
  sections.push({{ el: div, rows, bl }});
  chart.appendChild(div);
}});
function rescale() {{
  let maxUs = 0;
  sections.forEach(s => {{
    if (!s.el.classList.contains('collapsed'))
      s.rows.forEach(r => {{ if (r.us > maxUs) maxUs = r.us; }});
  }});
  maxUs = maxUs || 5;
  sections.forEach(s => {{
    s.rows.forEach(r => {{
      const pct = Math.min(100, (r.us / maxUs) * 100);
      r.el.querySelector('.bar').style.width = pct + '%';
      const bg = r.el.querySelector('.bar-bg');
      let mark = bg.querySelector('.baseline-mark');
      if (s.bl > 0) {{
        if (!mark) {{ mark = document.createElement('div'); mark.className = 'baseline-mark'; bg.appendChild(mark); }}
        mark.style.left = Math.min(100, (s.bl / maxUs) * 100) + '%';
      }} else if (mark) {{ mark.remove(); }}
    }});
  }});
}}
rescale();
</script>
</body>
</html>"""

    output_path.write_text(html)
    print(f"  Wrote {output_path}")

    # Also generate markdown
    md_path = output_path.with_suffix(".md")
    _generate_md(data, iterations, runs, suites, md_path)


def _generate_md(data, iterations, runs, suites, output_path):
    BASELINE_US = 2.8
    SCAFF_COST = 2.8
    lines = [
        "# JCVM Instruction Cost (Raw Measurements)",
        "",
        f"**Card:** J3R180 — {iterations} iters × {runs} runs × {suites} suites (drop hi/lo) — empty-loop baseline subtracted",
        "",
    ]
    for section in data:
        bl = section.get("baseline", 0)
        lines.append(f"## {section['section']}")
        lines.append("")
        if bl > 0:
            lines.append("| Instruction | us | Δ baseline | cost |")
            lines.append("|---|--:|--:|--:|")
        else:
            lines.append("| Instruction | us | cost |")
            lines.append("|---|--:|--:|")
        for item in section["items"]:
            us = max(0, item["us"])
            name = item["name"]
            insns = item.get("insns", 0)
            scaff = item.get("scaffold", 0)
            adj_insns = insns - scaff
            adj_us = us - scaff * SCAFF_COST
            if insns > 0:
                uspi = BASELINE_US if adj_insns <= 0 else adj_us / adj_insns
                mult = f"{uspi / BASELINE_US:.1f}x"
            else:
                mult = ""
            if bl > 0:
                delta = us - bl
                sign = "+" if delta >= 0 else ""
                lines.append(f"| `{name}` | {us:.1f} | {sign}{delta:.1f} | {mult} |")
            else:
                lines.append(f"| `{name}` | {us:.1f} | {mult} |")
        lines.append("")
    output_path.write_text("\n".join(lines))
    print(f"  Wrote {output_path}")


class BenchDriver(BaseDriver):

    def add_commands(self, subparsers):
        bench_parser = subparsers.add_parser("bench", help="Run benchmarks")
        bench_parser.add_argument("--iters", type=int, default=1000, help="Iterations per benchmark")
        bench_parser.add_argument("--runs", type=int, default=5, help="Runs per benchmark")
        bench_parser.add_argument("--suites", type=int, default=7, help="Suite passes (drop hi/lo)")
        bench_parser.add_argument("--card", action="store_true", help="Use real card")
        bench_parser.add_argument("--eeprom", action="store_true", help="Include EEPROM benchmarks (skipped by default)")

        subparsers.add_parser("html", help="Regenerate HTML from results.json")

    def handle_command(self, args):
        if args.command == "bench":
            backend = "card" if args.card else None
            self.cmd_bench(backend, args.iters, args.runs, args.suites,
                           eeprom=args.eeprom)
        elif args.command == "html":
            self.cmd_html()

    def cmd_html(self):
        json_path = self.demo_dir / "results.json"
        if not json_path.exists():
            sys.exit(f"No results.json found at {json_path}. Run bench first.")
        results, iterations, runs, suites = _load_results(json_path)
        html_path = self.demo_dir / "results.html"
        _generate_html(results, iterations, runs, suites, html_path)

    def cmd_play(self, backend=None):
        self.cmd_bench(backend, 1000, 5, 7)

    def cmd_bench(self, backend=None, iterations=1000, runs=5, suites=7,
                  eeprom=False):
        skip = set() if eeprom else EEPROM_BENCHMARKS
        print(f"Iterations: {iterations}, Runs: {runs}, Suites: {suites}")
        if skip:
            print(f"Skipping: {', '.join(sorted(skip))}")
        print()

        iter_hi = (iterations >> 8) & 0xFF
        iter_lo = iterations & 0xFF

        def _apdu(bi, name):
            iters = FIXED_ITERS.get(name, iterations)
            hi = (iters >> 8) & 0xFF
            lo = iters & 0xFF
            return f"80{0x10 + bi:02X}000002{hi:02X}{lo:02X}"

        # suite_avgs[bench_index] = list of per-suite averages
        suite_avgs = [[] for _ in BENCHMARKS]

        with self.get_session(backend) as session:
            # Warmup
            print("  warmup...", end=" ", flush=True)
            for bi, (name, _, _) in enumerate(BENCHMARKS):
                if name in skip:
                    continue
                session.send(_apdu(bi, name))
            print("done\n")

            for si in range(suites):
                print(f"  Suite {si + 1}/{suites}:")
                for bi, (name, desc, body_insns) in enumerate(BENCHMARKS):
                    if name in skip:
                        continue
                    ins = 0x10 + bi
                    print(f"    {name}...", end=" ", flush=True)
                    apdu = _apdu(bi, name)

                    times = []
                    for _ in range(runs):
                        start = time.perf_counter()
                        data, sw = session.send(apdu)
                        elapsed = time.perf_counter() - start
                        if sw != 0x9000:
                            print(f"SW={sw:04X}", end=" ")
                        times.append(elapsed * 1000)

                    avg = sum(times) / len(times)
                    print(f"{avg:.2f} ms")
                    suite_avgs[bi].append(avg)
                print()

        # For each benchmark: drop highest and lowest suite avg, average the rest
        baseline_ms = 0.0
        baseline_1iter_ms = 0.0
        results = []
        for bi, (name, desc, body_insns) in enumerate(BENCHMARKS):
            if name in skip:
                results.append((name, desc, body_insns, 0.0))
                continue
            avgs = sorted(suite_avgs[bi])
            trimmed = avgs[1:-1] if len(avgs) >= 3 else avgs  # drop lowest and highest
            final_avg = sum(trimmed) / len(trimmed)

            if name == "empty":
                baseline_ms = final_avg
            elif name == "empty_eeprom":
                baseline_1iter_ms = final_avg
            results.append((name, desc, body_insns, final_avg))

        # --- Raw results table ---
        print()
        print(f"{'Benchmark':<20} {'Avg ms':>8} {'Adj ms':>8} {'us/op':>8} {'Body':>5}  Description")
        print("-" * 96)

        for name, desc, body_insns, avg in results:
            if name in skip:
                print(f"{name:<20} {'skip':>8} {'skip':>8} {'skip':>8} {body_insns:>5}  {desc}")
                continue
            actual_iters = FIXED_ITERS.get(name, iterations)
            if actual_iters != iterations and baseline_1iter_ms > 0:
                bl = baseline_1iter_ms
            else:
                bl = baseline_ms
            adj = max(0, avg - bl)
            us_per_op = (adj * 1000) / actual_iters if actual_iters > 0 else 0
            marker = " *" if name == "empty" else ""
            print(f"{name:<20} {avg:>8.2f} {adj:>8.2f} {us_per_op:>8.2f} {body_insns:>5}  {desc}{marker}")

        print(f"\nBaseline (empty loop): {baseline_ms:.2f} ms for {iterations} iterations")
        print(f"  = {baseline_ms * 1000 / iterations:.2f} us/iter (loop overhead only)")

        # --- Save results JSON ---
        json_path = self.demo_dir / "results.json"
        _save_results(results, iterations, runs, suites, json_path)

        # --- Generate HTML ---
        html_path = self.demo_dir / "results.html"
        _generate_html(results, iterations, runs, suites, html_path)


if __name__ == "__main__":
    BenchDriver(Path(__file__).parent.parent).run(sys.argv[1:])
