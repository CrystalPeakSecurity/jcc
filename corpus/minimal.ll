; ModuleID = 'main.c'
source_filename = "main.c"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-n32:64-S128-ni:1:10:20"
target triple = "wasm32-unknown-unknown"

@counter = hidden local_unnamed_addr global i16 0, align 2, !dbg !0

; Function Attrs: nounwind
define hidden void @process(ptr noundef %0, i16 noundef signext %1) local_unnamed_addr #0 !dbg !15 {
    #dbg_value(ptr %0, !21, !DIExpression(), !26)
    #dbg_value(i16 %1, !22, !DIExpression(), !26)
  %3 = tail call ptr @jc_APDU_getBuffer(ptr noundef %0) #2, !dbg !27
    #dbg_value(ptr %3, !23, !DIExpression(), !26)
  %4 = getelementptr inbounds i8, ptr %3, i32 1, !dbg !28
  %5 = load i8, ptr %4, align 1, !dbg !28, !tbaa !29
    #dbg_value(i8 %5, !25, !DIExpression(), !26)
  switch i8 %5, label %21 [
    i8 1, label %6
    i8 2, label %14
    i8 3, label %15
  ], !dbg !32

6:                                                ; preds = %2
  %7 = load i16, ptr @counter, align 2, !dbg !33, !tbaa !35
  %8 = add i16 %7, 1, !dbg !37
  store i16 %8, ptr @counter, align 2, !dbg !38, !tbaa !35
  %9 = lshr i16 %8, 8, !dbg !39
  %10 = trunc nuw i16 %9 to i8, !dbg !40
  store i8 %10, ptr %3, align 1, !dbg !41, !tbaa !29
  %11 = load i16, ptr @counter, align 2, !dbg !42, !tbaa !35
  %12 = trunc i16 %11 to i8, !dbg !43
  store i8 %12, ptr %4, align 1, !dbg !44, !tbaa !29
  %13 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #2, !dbg !45
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #2, !dbg !46
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #2, !dbg !47
  br label %22, !dbg !48

14:                                               ; preds = %2
  store i16 0, ptr @counter, align 2, !dbg !49, !tbaa !35
  br label %22, !dbg !50

15:                                               ; preds = %2
  %16 = getelementptr inbounds i8, ptr %3, i32 2, !dbg !51
  %17 = load i8, ptr %16, align 1, !dbg !51, !tbaa !29
  store i8 %17, ptr %3, align 1, !dbg !52, !tbaa !29
  %18 = getelementptr inbounds i8, ptr %3, i32 3, !dbg !53
  %19 = load i8, ptr %18, align 1, !dbg !53, !tbaa !29
  store i8 %19, ptr %4, align 1, !dbg !54, !tbaa !29
  %20 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #2, !dbg !55
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #2, !dbg !56
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #2, !dbg !57
  br label %22, !dbg !58

21:                                               ; preds = %2
  tail call void @jc_ISOException_throwIt(i16 noundef signext 27904) #2, !dbg !59
  br label %22, !dbg !60

22:                                               ; preds = %21, %15, %14, %6
  ret void, !dbg !61
}

declare !dbg !62 ptr @jc_APDU_getBuffer(ptr noundef) local_unnamed_addr #1

declare !dbg !65 signext i16 @jc_APDU_setOutgoing(ptr noundef) local_unnamed_addr #1

declare !dbg !68 void @jc_APDU_setOutgoingLength(ptr noundef, i16 noundef signext) local_unnamed_addr #1

declare !dbg !69 void @jc_APDU_sendBytes(ptr noundef, i16 noundef signext, i16 noundef signext) local_unnamed_addr #1

declare !dbg !72 void @jc_ISOException_throwIt(i16 noundef signext) local_unnamed_addr #1

attributes #0 = { nounwind "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #1 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #2 = { nounwind }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!10, !11, !12, !13}
!llvm.ident = !{!14}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "counter", scope: !2, file: !3, line: 5, type: !9, isLocal: false, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C11, file: !3, producer: "Apple clang version 17.0.0 (clang-1700.6.3.2)", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !4, globals: !8, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "main.c", directory: "/home/user/jcc/examples/minimal")
!4 = !{!5}
!5 = !DIDerivedType(tag: DW_TAG_typedef, name: "byte", file: !6, line: 7, baseType: !7)
!6 = !DIFile(filename: "include/jcc.h", directory: "/home/user/jcc")
!7 = !DIBasicType(name: "signed char", size: 8, encoding: DW_ATE_signed_char)
!8 = !{!0}
!9 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!10 = !{i32 7, !"Dwarf Version", i32 4}
!11 = !{i32 2, !"Debug Info Version", i32 3}
!12 = !{i32 1, !"wchar_size", i32 4}
!13 = !{i32 7, !"debug-info-assignment-tracking", i1 true}
!14 = !{!"Apple clang version 17.0.0 (clang-1700.6.3.2)"}
!15 = distinct !DISubprogram(name: "process", scope: !3, file: !3, line: 7, type: !16, scopeLine: 7, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !20)
!16 = !DISubroutineType(types: !17)
!17 = !{null, !18, !9}
!18 = !DIDerivedType(tag: DW_TAG_typedef, name: "APDU", file: !6, line: 11, baseType: !19)
!19 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 32)
!20 = !{!21, !22, !23, !25}
!21 = !DILocalVariable(name: "apdu", arg: 1, scope: !15, file: !3, line: 7, type: !18)
!22 = !DILocalVariable(name: "len", arg: 2, scope: !15, file: !3, line: 7, type: !9)
!23 = !DILocalVariable(name: "buffer", scope: !15, file: !3, line: 8, type: !24)
!24 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !5, size: 32)
!25 = !DILocalVariable(name: "ins", scope: !15, file: !3, line: 9, type: !5)
!26 = !DILocation(line: 0, scope: !15)
!27 = !DILocation(line: 8, column: 20, scope: !15)
!28 = !DILocation(line: 9, column: 16, scope: !15)
!29 = !{!30, !30, i64 0}
!30 = !{!"omnipotent char", !31, i64 0}
!31 = !{!"Simple C/C++ TBAA"}
!32 = !DILocation(line: 11, column: 5, scope: !15)
!33 = !DILocation(line: 13, column: 19, scope: !34)
!34 = distinct !DILexicalBlock(scope: !15, file: !3, line: 11, column: 18)
!35 = !{!36, !36, i64 0}
!36 = !{!"short", !30, i64 0}
!37 = !DILocation(line: 13, column: 27, scope: !34)
!38 = !DILocation(line: 13, column: 17, scope: !34)
!39 = !DILocation(line: 14, column: 36, scope: !34)
!40 = !DILocation(line: 14, column: 21, scope: !34)
!41 = !DILocation(line: 14, column: 19, scope: !34)
!42 = !DILocation(line: 15, column: 27, scope: !34)
!43 = !DILocation(line: 15, column: 21, scope: !34)
!44 = !DILocation(line: 15, column: 19, scope: !34)
!45 = !DILocation(line: 16, column: 9, scope: !34)
!46 = !DILocation(line: 17, column: 9, scope: !34)
!47 = !DILocation(line: 18, column: 9, scope: !34)
!48 = !DILocation(line: 19, column: 9, scope: !34)
!49 = !DILocation(line: 22, column: 17, scope: !34)
!50 = !DILocation(line: 23, column: 9, scope: !34)
!51 = !DILocation(line: 26, column: 21, scope: !34)
!52 = !DILocation(line: 26, column: 19, scope: !34)
!53 = !DILocation(line: 27, column: 21, scope: !34)
!54 = !DILocation(line: 27, column: 19, scope: !34)
!55 = !DILocation(line: 28, column: 9, scope: !34)
!56 = !DILocation(line: 29, column: 9, scope: !34)
!57 = !DILocation(line: 30, column: 9, scope: !34)
!58 = !DILocation(line: 31, column: 9, scope: !34)
!59 = !DILocation(line: 34, column: 9, scope: !34)
!60 = !DILocation(line: 35, column: 5, scope: !34)
!61 = !DILocation(line: 36, column: 1, scope: !15)
!62 = !DISubprogram(name: "jc_APDU_getBuffer", scope: !6, file: !6, line: 94, type: !63, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!63 = !DISubroutineType(types: !64)
!64 = !{!24, !18}
!65 = !DISubprogram(name: "jc_APDU_setOutgoing", scope: !6, file: !6, line: 96, type: !66, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!66 = !DISubroutineType(types: !67)
!67 = !{!9, !18}
!68 = !DISubprogram(name: "jc_APDU_setOutgoingLength", scope: !6, file: !6, line: 97, type: !16, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!69 = !DISubprogram(name: "jc_APDU_sendBytes", scope: !6, file: !6, line: 98, type: !70, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!70 = !DISubroutineType(types: !71)
!71 = !{null, !18, !9, !9}
!72 = !DISubprogram(name: "jc_ISOException_throwIt", scope: !6, file: !6, line: 120, type: !73, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!73 = !DISubroutineType(types: !74)
!74 = !{null, !9}
