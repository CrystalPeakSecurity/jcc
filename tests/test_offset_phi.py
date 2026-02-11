"""Tests for analysis/offset_phi.py - Offset phi detection.

Tests both constant-offset (GlobalRef/InlineGEP) and dynamic-offset (SSARef→GEP)
offset phi detection.
"""

from jcc.analysis.globals import AllocationResult, GlobalInfo, MemArray
from jcc.analysis.offset_phi import detect_offset_phis
from jcc.analysis.phi import PhiInfo, PhiSource
from jcc.ir.instructions import GEPInst
from jcc.ir.types import BlockLabel, GlobalName, LLVMType, SSAName
from jcc.ir.values import GlobalRef, SSARef


def _make_allocation(*globals_list: tuple[str, int]) -> AllocationResult:
    """Create a simple AllocationResult for testing.

    Args:
        globals_list: (name, mem_offset) pairs for byte-array globals.
    """
    alloc: dict[GlobalName, GlobalInfo] = {}
    for name, offset in globals_list:
        alloc[GlobalName(name)] = GlobalInfo(
            name=GlobalName(name),
            mem_array=MemArray.MEM_B,
            mem_offset=offset,
            count=256,
        )
    return AllocationResult(globals=alloc, structs={}, mem_sizes={}, const_values={})


class TestDynamicGepPhiDetection:
    """Test offset phi detection for dynamic-index GEPs (SSARef sources)."""

    def test_dynamic_gep_same_global_detected(self) -> None:
        """Phi with SSARef sources pointing to GEPs on the same global → offset phi."""
        #   %gep1 = gep i8, ptr @BUF, i32 %idx1
        #   %gep2 = gep i8, ptr @BUF, i32 %idx2
        #   %phi = phi ptr [%gep1, bb1], [%gep2, bb2]

        allocation = _make_allocation(("@BUF", 0))

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%gep1")),
                        from_block=BlockLabel("bb1"),
                    ),
                    PhiSource(
                        value=SSARef(name=SSAName("%gep2")),
                        from_block=BlockLabel("bb2"),
                    ),
                ),
            }
        )

        # Define GEP instructions
        def_map = {
            SSAName("%gep1"): GEPInst(
                result=SSAName("%gep1"),
                base=GlobalRef(name=GlobalName("@BUF")),
                indices=(SSARef(name=SSAName("%idx1")),),
                source_type=LLVMType("i8"),
                inbounds=True,
            ),
            SSAName("%gep2"): GEPInst(
                result=SSAName("%gep2"),
                base=GlobalRef(name=GlobalName("@BUF")),
                indices=(SSARef(name=SSAName("%idx2")),),
                source_type=LLVMType("i8"),
                inbounds=True,
            ),
        }

        result = detect_offset_phis(phi_info, allocation, def_map)

        assert result.is_offset_phi(SSAName("%phi"))
        assert result.get_base_global(SSAName("%phi")) == GlobalName("@BUF")
        # Dynamic offsets: SSA names of the GEP index operands
        assert result.get_offset(SSAName("%phi"), BlockLabel("bb1")) == SSAName("%idx1")
        assert result.get_offset(SSAName("%phi"), BlockLabel("bb2")) == SSAName("%idx2")

    def test_dynamic_gep_different_globals_rejected(self) -> None:
        """Phi with GEPs on different globals → NOT an offset phi."""
        allocation = _make_allocation(("@BUF1", 0), ("@BUF2", 256))

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%gep1")),
                        from_block=BlockLabel("bb1"),
                    ),
                    PhiSource(
                        value=SSARef(name=SSAName("%gep2")),
                        from_block=BlockLabel("bb2"),
                    ),
                ),
            }
        )

        def_map = {
            SSAName("%gep1"): GEPInst(
                result=SSAName("%gep1"),
                base=GlobalRef(name=GlobalName("@BUF1")),
                indices=(SSARef(name=SSAName("%idx1")),),
                source_type=LLVMType("i8"),
                inbounds=True,
            ),
            SSAName("%gep2"): GEPInst(
                result=SSAName("%gep2"),
                base=GlobalRef(name=GlobalName("@BUF2")),
                indices=(SSARef(name=SSAName("%idx2")),),
                source_type=LLVMType("i8"),
                inbounds=True,
            ),
        }

        result = detect_offset_phis(phi_info, allocation, def_map)

        assert not result.is_offset_phi(SSAName("%phi"))

    def test_mixed_constant_and_dynamic_not_detected(self) -> None:
        """Phi with mix of GlobalRef and SSARef GEP → not detected.

        GlobalRef resolves to constant offset, SSARef to dynamic.
        Both need same base global, but mixing source types is OK.
        """
        allocation = _make_allocation(("@BUF", 0))

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=GlobalRef(name=GlobalName("@BUF")),
                        from_block=BlockLabel("bb1"),
                    ),
                    PhiSource(
                        value=SSARef(name=SSAName("%gep2")),
                        from_block=BlockLabel("bb2"),
                    ),
                ),
            }
        )

        def_map = {
            SSAName("%gep2"): GEPInst(
                result=SSAName("%gep2"),
                base=GlobalRef(name=GlobalName("@BUF")),
                indices=(SSARef(name=SSAName("%idx2")),),
                source_type=LLVMType("i8"),
                inbounds=True,
            ),
        }

        result = detect_offset_phis(phi_info, allocation, def_map)

        # This SHOULD be detected: GlobalRef = constant offset 0, SSARef = dynamic
        assert result.is_offset_phi(SSAName("%phi"))
        assert result.get_offset(SSAName("%phi"), BlockLabel("bb1")) == 0  # constant
        assert result.get_offset(SSAName("%phi"), BlockLabel("bb2")) == SSAName("%idx2")  # dynamic

    def test_no_def_map_skips_ssa_sources(self) -> None:
        """Without def_map, SSARef sources cannot be resolved."""
        allocation = _make_allocation(("@BUF", 0))

        phi_info = PhiInfo(
            phi_sources={
                SSAName("%phi"): (
                    PhiSource(
                        value=SSARef(name=SSAName("%gep1")),
                        from_block=BlockLabel("bb1"),
                    ),
                ),
            }
        )

        # No def_map
        result = detect_offset_phis(phi_info, allocation, def_map=None)

        assert not result.is_offset_phi(SSAName("%phi"))
