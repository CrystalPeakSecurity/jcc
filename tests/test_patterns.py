"""Unit tests for IR string patterns parsing."""

from jcc.ir import patterns


class TestBlockLabelExtraction:
    """Test extraction of numeric block labels from function IR."""

    def test_single_block_no_label(self) -> None:
        """Single block with no explicit label defaults to 0."""
        ir = """define void @test() {
  ret void
}"""
        labels = patterns.extract_function_block_labels(ir)
        assert labels == ["0"]

    def test_numeric_labels_from_preds(self) -> None:
        """Entry block label found from preds comment."""
        ir = """define i32 @test(i1 %cond) {
  br i1 %cond, label %1, label %2

1:                                                ; preds = %0
  ret i32 10

2:                                                ; preds = %0
  ret i32 20
}"""
        labels = patterns.extract_function_block_labels(ir)
        assert labels == ["0", "1", "2"]

    def test_numeric_labels_multiple_preds(self) -> None:
        """Entry block found when multiple blocks reference it."""
        ir = """define i32 @test(i1 %cond) {
  br i1 %cond, label %1, label %2

1:                                                ; preds = %0
  br label %3

2:                                                ; preds = %0
  br label %3

3:                                                ; preds = %2, %1
  ret i32 0
}"""
        labels = patterns.extract_function_block_labels(ir)
        assert labels == ["0", "1", "2", "3"]

    def test_non_sequential_labels(self) -> None:
        """Handles non-sequential block numbers from SSA numbering."""
        # Real compiler output has gaps in block numbers due to SSA values
        ir = """define i32 @test(i1 %cond) {
  br i1 %cond, label %5, label %8

5:                                                ; preds = %0
  ret i32 10

8:                                                ; preds = %0
  ret i32 20
}"""
        labels = patterns.extract_function_block_labels(ir)
        # Entry block is 0 (found via preds = %0), explicit labels are 5 and 8
        assert labels == ["0", "5", "8"]

    def test_no_blocks_returns_default(self) -> None:
        """Pathological case: declaration-like text returns default."""
        ir = """declare void @test()"""
        labels = patterns.extract_function_block_labels(ir)
        assert labels == ["0"]


class TestPhiIncomingParsing:
    """Test balanced parsing of phi incoming values."""

    def test_simple_phi(self) -> None:
        """Parse simple phi with constants."""
        instr = "%result = phi i32 [ 1, %then ], [ 2, %else ]"
        incoming = patterns.parse_phi_incoming(instr)
        assert len(incoming) == 2
        assert incoming[0].value_str == "1"
        assert incoming[0].label == "then"
        assert incoming[1].value_str == "2"
        assert incoming[1].label == "else"

    def test_phi_with_nested_gep(self) -> None:
        """Parse phi with complex nested GEP expression."""
        instr = "%p = phi ptr [ getelementptr inbounds (i8, ptr @arr, i32 0), %bb ]"
        incoming = patterns.parse_phi_incoming(instr)
        assert len(incoming) == 1
        assert "getelementptr" in incoming[0].value_str
        assert incoming[0].label == "bb"

    def test_phi_with_ssa_refs(self) -> None:
        """Parse phi with SSA references."""
        instr = "%i = phi i32 [ 0, %entry ], [ %next, %loop ]"
        incoming = patterns.parse_phi_incoming(instr)
        assert len(incoming) == 2
        assert incoming[0].value_str == "0"
        assert incoming[0].label == "entry"
        assert incoming[1].value_str == "%next"
        assert incoming[1].label == "loop"

    def test_phi_with_numeric_labels(self) -> None:
        """Parse phi with numeric block labels."""
        instr = "%result = phi i32 [ 10, %1 ], [ 20, %2 ]"
        incoming = patterns.parse_phi_incoming(instr)
        assert len(incoming) == 2
        assert incoming[0].label == "1"
        assert incoming[1].label == "2"


class TestGEPParsing:
    """Test GEP-related pattern extraction."""

    def test_gep_source_type(self) -> None:
        """Extract source type from GEP instruction."""
        instr = "%ptr = getelementptr inbounds [100 x i16], ptr @arr, i64 0, i64 %idx"
        source_type = patterns.parse_gep_source_type(instr)
        assert "[100 x i16]" in source_type

    def test_gep_with_nuw_nusw(self) -> None:
        """Handle LLVM 17+ nuw/nusw modifiers."""
        instr = "%ptr = getelementptr inbounds nuw i8, ptr %p, i64 8"
        source_type = patterns.parse_gep_source_type(instr)
        assert "i8" in source_type


class TestConstExprDetection:
    """Test constant expression detection."""

    def test_ptrtoint_detected(self) -> None:
        """ptrtoint is detected as unsupported."""
        s = "ptrtoint (ptr @global to i64)"
        result = patterns.contains_unsupported_const_expr(s)
        assert result == "ptrtoint"

    def test_inttoptr_detected(self) -> None:
        """inttoptr is detected as unsupported."""
        s = "inttoptr (i64 12345 to ptr)"
        result = patterns.contains_unsupported_const_expr(s)
        assert result == "inttoptr"

    def test_bitcast_detected(self) -> None:
        """bitcast is detected as unsupported."""
        s = "bitcast (ptr @foo to ptr)"
        result = patterns.contains_unsupported_const_expr(s)
        assert result == "bitcast"

    def test_gep_not_unsupported(self) -> None:
        """GEP constant expressions are supported (handled separately)."""
        s = "getelementptr inbounds (i8, ptr @arr, i32 0)"
        result = patterns.contains_unsupported_const_expr(s)
        assert result is None

    def test_plain_value_not_unsupported(self) -> None:
        """Plain values are not unsupported expressions."""
        result = patterns.contains_unsupported_const_expr("%x")
        assert result is None
