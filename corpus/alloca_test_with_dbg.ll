; ModuleID = 'alloca_test.c'
source_filename = "alloca_test.c"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-n32:64-S128-ni:1:10:20"
target triple = "wasm32"

%struct.Point = type { i16, i16, i8 }

; Function Attrs: noinline nounwind optnone
define hidden void @test() #0 !dbg !6 {
  %1 = alloca %struct.Point, align 2
  %2 = alloca [5 x i16], align 2
  %3 = alloca i32, align 4
    #dbg_declare(ptr %1, !10, !DIExpression(), !18)
    #dbg_declare(ptr %2, !19, !DIExpression(), !23)
    #dbg_declare(ptr %3, !24, !DIExpression(), !26)
  %4 = getelementptr inbounds %struct.Point, ptr %1, i32 0, i32 0, !dbg !27
  store i16 1, ptr %4, align 2, !dbg !28
  %5 = getelementptr inbounds %struct.Point, ptr %1, i32 0, i32 1, !dbg !29
  store i16 2, ptr %5, align 2, !dbg !30
  %6 = getelementptr inbounds %struct.Point, ptr %1, i32 0, i32 2, !dbg !31
  store i8 3, ptr %6, align 2, !dbg !32
  %7 = getelementptr inbounds [5 x i16], ptr %2, i32 0, i32 0, !dbg !33
  store i16 10, ptr %7, align 2, !dbg !34
  %8 = getelementptr inbounds [5 x i16], ptr %2, i32 0, i32 4, !dbg !35
  store i16 50, ptr %8, align 2, !dbg !36
  store i32 100, ptr %3, align 4, !dbg !37
  ret void, !dbg !38
}

attributes #0 = { noinline nounwind optnone "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4}
!llvm.ident = !{!5}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "Apple clang version 17.0.0 (clang-1700.6.3.2)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "alloca_test.c", directory: "/home/user/jcc/corpus")
!2 = !{i32 7, !"Dwarf Version", i32 4}
!3 = !{i32 2, !"Debug Info Version", i32 3}
!4 = !{i32 1, !"wchar_size", i32 4}
!5 = !{!"Apple clang version 17.0.0 (clang-1700.6.3.2)"}
!6 = distinct !DISubprogram(name: "test", scope: !1, file: !1, line: 10, type: !7, scopeLine: 10, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !9)
!7 = !DISubroutineType(types: !8)
!8 = !{null}
!9 = !{}
!10 = !DILocalVariable(name: "local_point", scope: !6, file: !1, line: 11, type: !11)
!11 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "Point", file: !1, line: 4, size: 48, elements: !12)
!12 = !{!13, !15, !16}
!13 = !DIDerivedType(tag: DW_TAG_member, name: "x", scope: !11, file: !1, line: 5, baseType: !14, size: 16)
!14 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!15 = !DIDerivedType(tag: DW_TAG_member, name: "y", scope: !11, file: !1, line: 6, baseType: !14, size: 16, offset: 16)
!16 = !DIDerivedType(tag: DW_TAG_member, name: "flags", scope: !11, file: !1, line: 7, baseType: !17, size: 8, offset: 32)
!17 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!18 = !DILocation(line: 11, column: 18, scope: !6)
!19 = !DILocalVariable(name: "local_array", scope: !6, file: !1, line: 12, type: !20)
!20 = !DICompositeType(tag: DW_TAG_array_type, baseType: !14, size: 80, elements: !21)
!21 = !{!22}
!22 = !DISubrange(count: 5)
!23 = !DILocation(line: 12, column: 11, scope: !6)
!24 = !DILocalVariable(name: "local_scalar", scope: !6, file: !1, line: 13, type: !25)
!25 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!26 = !DILocation(line: 13, column: 9, scope: !6)
!27 = !DILocation(line: 15, column: 17, scope: !6)
!28 = !DILocation(line: 15, column: 19, scope: !6)
!29 = !DILocation(line: 16, column: 17, scope: !6)
!30 = !DILocation(line: 16, column: 19, scope: !6)
!31 = !DILocation(line: 17, column: 17, scope: !6)
!32 = !DILocation(line: 17, column: 23, scope: !6)
!33 = !DILocation(line: 19, column: 5, scope: !6)
!34 = !DILocation(line: 19, column: 20, scope: !6)
!35 = !DILocation(line: 20, column: 5, scope: !6)
!36 = !DILocation(line: 20, column: 20, scope: !6)
!37 = !DILocation(line: 22, column: 18, scope: !6)
!38 = !DILocation(line: 23, column: 1, scope: !6)