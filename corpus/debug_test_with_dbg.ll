; ModuleID = 'debug_test.c'
source_filename = "debug_test.c"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-n32:64-S128-ni:1:10:20"
target triple = "wasm32"

%struct.Point = type { i16, i16, i8 }

@points = hidden global [10 x %struct.Point] zeroinitializer, align 16, !dbg !0
@values = hidden global [8 x i16] zeroinitializer, align 16, !dbg !5
@counter = hidden global i32 0, align 4, !dbg !11

; Function Attrs: noinline nounwind optnone
define hidden void @test() #0 !dbg !27 {
  store i16 1, ptr @points, align 16, !dbg !30
  store i16 2, ptr @values, align 16, !dbg !31
  store i32 3, ptr @counter, align 4, !dbg !32
  ret void, !dbg !33
}

attributes #0 = { noinline nounwind optnone "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!23, !24, !25}
!llvm.ident = !{!26}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "points", scope: !2, file: !3, line: 10, type: !14, isLocal: false, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C11, file: !3, producer: "Apple clang version 17.0.0 (clang-1700.6.3.2)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, globals: !4, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "debug_test.c", directory: "/home/user/jcc/corpus")
!4 = !{!0, !5, !11}
!5 = !DIGlobalVariableExpression(var: !6, expr: !DIExpression())
!6 = distinct !DIGlobalVariable(name: "values", scope: !2, file: !3, line: 11, type: !7, isLocal: false, isDefinition: true)
!7 = !DICompositeType(tag: DW_TAG_array_type, baseType: !8, size: 128, elements: !9)
!8 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!9 = !{!10}
!10 = !DISubrange(count: 8)
!11 = !DIGlobalVariableExpression(var: !12, expr: !DIExpression())
!12 = distinct !DIGlobalVariable(name: "counter", scope: !2, file: !3, line: 12, type: !13, isLocal: false, isDefinition: true)
!13 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!14 = !DICompositeType(tag: DW_TAG_array_type, baseType: !15, size: 480, elements: !21)
!15 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "Point", file: !3, line: 4, size: 48, elements: !16)
!16 = !{!17, !18, !19}
!17 = !DIDerivedType(tag: DW_TAG_member, name: "x", scope: !15, file: !3, line: 5, baseType: !8, size: 16)
!18 = !DIDerivedType(tag: DW_TAG_member, name: "y", scope: !15, file: !3, line: 6, baseType: !8, size: 16, offset: 16)
!19 = !DIDerivedType(tag: DW_TAG_member, name: "flags", scope: !15, file: !3, line: 7, baseType: !20, size: 8, offset: 32)
!20 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!21 = !{!22}
!22 = !DISubrange(count: 10)
!23 = !{i32 7, !"Dwarf Version", i32 4}
!24 = !{i32 2, !"Debug Info Version", i32 3}
!25 = !{i32 1, !"wchar_size", i32 4}
!26 = !{!"Apple clang version 17.0.0 (clang-1700.6.3.2)"}
!27 = distinct !DISubprogram(name: "test", scope: !3, file: !3, line: 14, type: !28, scopeLine: 14, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !2)
!28 = !DISubroutineType(types: !29)
!29 = !{null}
!30 = !DILocation(line: 15, column: 17, scope: !27)
!31 = !DILocation(line: 16, column: 15, scope: !27)
!32 = !DILocation(line: 17, column: 13, scope: !27)
!33 = !DILocation(line: 18, column: 1, scope: !27)