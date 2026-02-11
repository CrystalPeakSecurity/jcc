; ModuleID = 'main.c'
source_filename = "main.c"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-n32:64-S128-ni:1:10:20"
target triple = "wasm32-unknown-unknown"

; Function Attrs: nounwind
define hidden void @sendResult(ptr noundef %0, ptr nocapture noundef writeonly %1, i16 noundef signext %2) local_unnamed_addr #0 !dbg !11 {
    #dbg_value(ptr %0, !19, !DIExpression(), !22)
    #dbg_value(ptr %1, !20, !DIExpression(), !22)
    #dbg_value(i16 %2, !21, !DIExpression(), !22)
  %4 = lshr i16 %2, 8, !dbg !23
  %5 = trunc nuw i16 %4 to i8, !dbg !24
  store i8 %5, ptr %1, align 1, !dbg !25, !tbaa !26
  %6 = trunc i16 %2 to i8, !dbg !29
  %7 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !30
  store i8 %6, ptr %7, align 1, !dbg !31, !tbaa !26
  %8 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #2, !dbg !32
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #2, !dbg !33
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #2, !dbg !34
  ret void, !dbg !35
}

declare !dbg !36 signext i16 @jc_APDU_setOutgoing(ptr noundef) local_unnamed_addr #1

declare !dbg !39 void @jc_APDU_setOutgoingLength(ptr noundef, i16 noundef signext) local_unnamed_addr #1

declare !dbg !42 void @jc_APDU_sendBytes(ptr noundef, i16 noundef signext, i16 noundef signext) local_unnamed_addr #1

; Function Attrs: nounwind
define hidden void @test_loops(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !45 {
    #dbg_value(ptr %0, !49, !DIExpression(), !57)
    #dbg_value(ptr %1, !50, !DIExpression(), !57)
    #dbg_value(i8 %2, !51, !DIExpression(), !57)
  switch i8 %2, label %21 [
    i8 0, label %29
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %10
    i8 8, label %11
    i8 9, label %12
    i8 10, label %13
    i8 11, label %20
  ], !dbg !58

4:                                                ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i32 poison, !52, !DIExpression(), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !59)
    #dbg_value(ptr %1, !20, !DIExpression(), !59)
    #dbg_value(i16 1, !21, !DIExpression(), !59)
  br label %29, !dbg !63

5:                                                ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !64)
    #dbg_value(ptr %1, !20, !DIExpression(), !64)
    #dbg_value(i16 55, !21, !DIExpression(), !64)
  br label %29, !dbg !68

6:                                                ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !69)
    #dbg_value(ptr %1, !20, !DIExpression(), !69)
    #dbg_value(i16 20, !21, !DIExpression(), !69)
  br label %29, !dbg !73

7:                                                ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !74)
    #dbg_value(ptr %1, !20, !DIExpression(), !74)
    #dbg_value(i16 15, !21, !DIExpression(), !74)
  br label %29, !dbg !78

8:                                                ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 undef, !52, !DIExpression(), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !79)
    #dbg_value(ptr %1, !20, !DIExpression(), !79)
    #dbg_value(i16 10, !21, !DIExpression(), !79)
  br label %29, !dbg !83

9:                                                ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
    #dbg_value(i32 10, !53, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !84)
    #dbg_value(ptr %1, !20, !DIExpression(), !84)
    #dbg_value(i32 10, !21, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !84)
  br label %29, !dbg !88

10:                                               ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !54, !DIExpression(), !89)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !90)
    #dbg_value(ptr %1, !20, !DIExpression(), !90)
    #dbg_value(i16 12, !21, !DIExpression(), !90)
  br label %29

11:                                               ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !92)
    #dbg_value(ptr %1, !20, !DIExpression(), !92)
    #dbg_value(i16 7, !21, !DIExpression(), !92)
  br label %29, !dbg !96

12:                                               ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !97)
    #dbg_value(ptr %1, !20, !DIExpression(), !97)
    #dbg_value(i16 9, !21, !DIExpression(), !97)
  br label %29, !dbg !101

13:                                               ; preds = %3, %16
  %14 = phi i32 [ %18, %16 ], [ 0, %3 ]
  %15 = phi i16 [ %17, %16 ], [ 0, %3 ]
    #dbg_value(i16 %15, !53, !DIExpression(), !57)
  switch i32 %14, label %16 [
    i32 327680, label %22
    i32 196608, label %22
  ], !dbg !102

16:                                               ; preds = %13
  %17 = add nuw nsw i16 %15, 1, !dbg !106
    #dbg_value(i16 %17, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
  %18 = add nuw nsw i32 %14, 65536, !dbg !109
  %19 = icmp ugt i32 %14, 524288, !dbg !110
  br i1 %19, label %26, label %13, !dbg !102, !llvm.loop !111

20:                                               ; preds = %3
    #dbg_value(i16 poison, !53, !DIExpression(), !57)
    #dbg_value(i16 poison, !52, !DIExpression(), !57)
    #dbg_value(i32 10, !53, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !57)
    #dbg_value(ptr %0, !19, !DIExpression(), !115)
    #dbg_value(ptr %1, !20, !DIExpression(), !115)
    #dbg_value(i32 10, !21, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !115)
  br label %29, !dbg !119

21:                                               ; preds = %3
    #dbg_value(ptr %0, !19, !DIExpression(), !120)
    #dbg_value(ptr %1, !20, !DIExpression(), !120)
    #dbg_value(i16 -1, !21, !DIExpression(), !120)
  br label %29, !dbg !122

22:                                               ; preds = %13, %13
  %23 = trunc i16 %15 to i8
  %24 = lshr i16 %15, 8
  %25 = trunc nuw nsw i16 %24 to i8
  br label %29, !dbg !123

26:                                               ; preds = %16
  %27 = lshr i16 %17, 8
  %28 = trunc nuw nsw i16 %27 to i8
  br label %29, !dbg !123

29:                                               ; preds = %22, %26, %3, %21, %20, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %30 = phi i8 [ -1, %21 ], [ 0, %20 ], [ 0, %12 ], [ 0, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ], [ %25, %22 ], [ %28, %26 ]
  %31 = phi i8 [ -1, %21 ], [ 10, %20 ], [ %2, %12 ], [ 7, %11 ], [ 12, %10 ], [ 10, %9 ], [ 10, %8 ], [ 15, %7 ], [ 20, %6 ], [ 55, %5 ], [ %2, %4 ], [ %2, %3 ], [ %23, %22 ], [ 10, %26 ]
  store i8 %30, ptr %1, align 1, !dbg !123, !tbaa !26
  %32 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !124
  store i8 %31, ptr %32, align 1, !dbg !125, !tbaa !26
  %33 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #2, !dbg !126
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #2, !dbg !127
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #2, !dbg !128
  ret void, !dbg !122
}

; Function Attrs: nounwind
define hidden void @process(ptr noundef %0, i16 noundef signext %1) local_unnamed_addr #0 !dbg !129 {
    #dbg_value(ptr %0, !131, !DIExpression(), !134)
    #dbg_value(i16 %1, !132, !DIExpression(), !134)
  %3 = tail call ptr @jc_APDU_getBuffer(ptr noundef %0) #2, !dbg !135
    #dbg_value(ptr %3, !133, !DIExpression(), !134)
  %4 = getelementptr inbounds i8, ptr %3, i32 1, !dbg !136
  %5 = load i8, ptr %4, align 1, !dbg !136, !tbaa !26
  %6 = icmp eq i8 %5, 16, !dbg !138
  br i1 %6, label %7, label %10, !dbg !139

7:                                                ; preds = %2
  %8 = getelementptr inbounds i8, ptr %3, i32 2, !dbg !140
  %9 = load i8, ptr %8, align 1, !dbg !140, !tbaa !26
  tail call void @test_loops(ptr noundef %0, ptr noundef %3, i8 noundef signext %9), !dbg !142
  br label %11, !dbg !143

10:                                               ; preds = %2
  tail call void @jc_ISOException_throwIt(i16 noundef signext 27904) #2, !dbg !144
  br label %11, !dbg !145

11:                                               ; preds = %10, %7
  ret void, !dbg !145
}

declare !dbg !146 ptr @jc_APDU_getBuffer(ptr noundef) local_unnamed_addr #1

declare !dbg !149 void @jc_ISOException_throwIt(i16 noundef signext) local_unnamed_addr #1

attributes #0 = { nounwind "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #1 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #2 = { nounwind }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!6, !7, !8, !9}
!llvm.ident = !{!10}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "Apple clang version 17.0.0 (clang-1700.6.3.2)", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !2, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "main.c", directory: "/home/user/jcc/examples/minimal_loop")
!2 = !{!3}
!3 = !DIDerivedType(tag: DW_TAG_typedef, name: "byte", file: !4, line: 7, baseType: !5)
!4 = !DIFile(filename: "include/jcc.h", directory: "/home/user/jcc")
!5 = !DIBasicType(name: "signed char", size: 8, encoding: DW_ATE_signed_char)
!6 = !{i32 7, !"Dwarf Version", i32 4}
!7 = !{i32 2, !"Debug Info Version", i32 3}
!8 = !{i32 1, !"wchar_size", i32 4}
!9 = !{i32 7, !"debug-info-assignment-tracking", i1 true}
!10 = !{!"Apple clang version 17.0.0 (clang-1700.6.3.2)"}
!11 = distinct !DISubprogram(name: "sendResult", scope: !1, file: !1, line: 5, type: !12, scopeLine: 5, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0, retainedNodes: !18)
!12 = !DISubroutineType(types: !13)
!13 = !{null, !14, !16, !17}
!14 = !DIDerivedType(tag: DW_TAG_typedef, name: "APDU", file: !4, line: 11, baseType: !15)
!15 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 32)
!16 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !3, size: 32)
!17 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!18 = !{!19, !20, !21}
!19 = !DILocalVariable(name: "apdu", arg: 1, scope: !11, file: !1, line: 5, type: !14)
!20 = !DILocalVariable(name: "buffer", arg: 2, scope: !11, file: !1, line: 5, type: !16)
!21 = !DILocalVariable(name: "result", arg: 3, scope: !11, file: !1, line: 5, type: !17)
!22 = !DILocation(line: 0, scope: !11)
!23 = !DILocation(line: 6, column: 31, scope: !11)
!24 = !DILocation(line: 6, column: 17, scope: !11)
!25 = !DILocation(line: 6, column: 15, scope: !11)
!26 = !{!27, !27, i64 0}
!27 = !{!"omnipotent char", !28, i64 0}
!28 = !{!"Simple C/C++ TBAA"}
!29 = !DILocation(line: 7, column: 17, scope: !11)
!30 = !DILocation(line: 7, column: 5, scope: !11)
!31 = !DILocation(line: 7, column: 15, scope: !11)
!32 = !DILocation(line: 8, column: 5, scope: !11)
!33 = !DILocation(line: 9, column: 5, scope: !11)
!34 = !DILocation(line: 10, column: 5, scope: !11)
!35 = !DILocation(line: 11, column: 1, scope: !11)
!36 = !DISubprogram(name: "jc_APDU_setOutgoing", scope: !4, file: !4, line: 96, type: !37, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!37 = !DISubroutineType(types: !38)
!38 = !{!17, !14}
!39 = !DISubprogram(name: "jc_APDU_setOutgoingLength", scope: !4, file: !4, line: 97, type: !40, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!40 = !DISubroutineType(types: !41)
!41 = !{null, !14, !17}
!42 = !DISubprogram(name: "jc_APDU_sendBytes", scope: !4, file: !4, line: 98, type: !43, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!43 = !DISubroutineType(types: !44)
!44 = !{null, !14, !17, !17}
!45 = distinct !DISubprogram(name: "test_loops", scope: !1, file: !1, line: 13, type: !46, scopeLine: 13, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0, retainedNodes: !48)
!46 = !DISubroutineType(types: !47)
!47 = !{null, !14, !16, !3}
!48 = !{!49, !50, !51, !52, !53, !54}
!49 = !DILocalVariable(name: "apdu", arg: 1, scope: !45, file: !1, line: 13, type: !14)
!50 = !DILocalVariable(name: "buffer", arg: 2, scope: !45, file: !1, line: 13, type: !16)
!51 = !DILocalVariable(name: "p1", arg: 3, scope: !45, file: !1, line: 13, type: !3)
!52 = !DILocalVariable(name: "i", scope: !45, file: !1, line: 14, type: !17)
!53 = !DILocalVariable(name: "sum", scope: !45, file: !1, line: 14, type: !17)
!54 = !DILocalVariable(name: "j", scope: !55, file: !1, line: 23, type: !17)
!55 = distinct !DILexicalBlock(scope: !56, file: !1, line: 23, column: 18)
!56 = distinct !DILexicalBlock(scope: !45, file: !1, line: 23, column: 9)
!57 = !DILocation(line: 0, scope: !45)
!58 = !DILocation(line: 16, column: 9, scope: !45)
!59 = !DILocation(line: 0, scope: !11, inlinedAt: !60)
!60 = distinct !DILocation(line: 17, column: 78, scope: !61)
!61 = distinct !DILexicalBlock(scope: !62, file: !1, line: 17, column: 18)
!62 = distinct !DILexicalBlock(scope: !45, file: !1, line: 17, column: 9)
!63 = !DILocation(line: 17, column: 109, scope: !61)
!64 = !DILocation(line: 0, scope: !11, inlinedAt: !65)
!65 = distinct !DILocation(line: 18, column: 79, scope: !66)
!66 = distinct !DILexicalBlock(scope: !67, file: !1, line: 18, column: 18)
!67 = distinct !DILexicalBlock(scope: !45, file: !1, line: 18, column: 9)
!68 = !DILocation(line: 18, column: 110, scope: !66)
!69 = !DILocation(line: 0, scope: !11, inlinedAt: !70)
!70 = distinct !DILocation(line: 19, column: 79, scope: !71)
!71 = distinct !DILexicalBlock(scope: !72, file: !1, line: 19, column: 18)
!72 = distinct !DILexicalBlock(scope: !45, file: !1, line: 19, column: 9)
!73 = !DILocation(line: 19, column: 110, scope: !71)
!74 = !DILocation(line: 0, scope: !11, inlinedAt: !75)
!75 = distinct !DILocation(line: 20, column: 71, scope: !76)
!76 = distinct !DILexicalBlock(scope: !77, file: !1, line: 20, column: 18)
!77 = distinct !DILexicalBlock(scope: !45, file: !1, line: 20, column: 9)
!78 = !DILocation(line: 20, column: 102, scope: !76)
!79 = !DILocation(line: 0, scope: !11, inlinedAt: !80)
!80 = distinct !DILocation(line: 21, column: 71, scope: !81)
!81 = distinct !DILexicalBlock(scope: !82, file: !1, line: 21, column: 18)
!82 = distinct !DILexicalBlock(scope: !45, file: !1, line: 21, column: 9)
!83 = !DILocation(line: 21, column: 102, scope: !81)
!84 = !DILocation(line: 0, scope: !11, inlinedAt: !85)
!85 = distinct !DILocation(line: 22, column: 84, scope: !86)
!86 = distinct !DILexicalBlock(scope: !87, file: !1, line: 22, column: 18)
!87 = distinct !DILexicalBlock(scope: !45, file: !1, line: 22, column: 9)
!88 = !DILocation(line: 22, column: 115, scope: !86)
!89 = !DILocation(line: 0, scope: !55)
!90 = !DILocation(line: 0, scope: !11, inlinedAt: !91)
!91 = distinct !DILocation(line: 23, column: 121, scope: !55)
!92 = !DILocation(line: 0, scope: !11, inlinedAt: !93)
!93 = distinct !DILocation(line: 24, column: 99, scope: !94)
!94 = distinct !DILexicalBlock(scope: !95, file: !1, line: 24, column: 18)
!95 = distinct !DILexicalBlock(scope: !45, file: !1, line: 24, column: 9)
!96 = !DILocation(line: 24, column: 130, scope: !94)
!97 = !DILocation(line: 0, scope: !11, inlinedAt: !98)
!98 = distinct !DILocation(line: 25, column: 101, scope: !99)
!99 = distinct !DILexicalBlock(scope: !100, file: !1, line: 25, column: 18)
!100 = distinct !DILexicalBlock(scope: !45, file: !1, line: 25, column: 9)
!101 = !DILocation(line: 25, column: 132, scope: !99)
!102 = !DILocation(line: 26, column: 30, scope: !103)
!103 = distinct !DILexicalBlock(scope: !104, file: !1, line: 26, column: 30)
!104 = distinct !DILexicalBlock(scope: !105, file: !1, line: 26, column: 19)
!105 = distinct !DILexicalBlock(scope: !45, file: !1, line: 26, column: 9)
!106 = !DILocation(line: 26, column: 111, scope: !107)
!107 = distinct !DILexicalBlock(scope: !108, file: !1, line: 26, column: 61)
!108 = distinct !DILexicalBlock(scope: !103, file: !1, line: 26, column: 30)
!109 = !DILocation(line: 26, column: 42, scope: !108)
!110 = !DILocation(line: 26, column: 44, scope: !108)
!111 = distinct !{!111, !102, !112, !113, !114}
!112 = !DILocation(line: 26, column: 116, scope: !103)
!113 = !{!"llvm.loop.mustprogress"}
!114 = !{!"llvm.loop.unroll.disable"}
!115 = !DILocation(line: 0, scope: !11, inlinedAt: !116)
!116 = distinct !DILocation(line: 27, column: 97, scope: !117)
!117 = distinct !DILexicalBlock(scope: !118, file: !1, line: 27, column: 19)
!118 = distinct !DILexicalBlock(scope: !45, file: !1, line: 27, column: 9)
!119 = !DILocation(line: 27, column: 128, scope: !117)
!120 = !DILocation(line: 0, scope: !11, inlinedAt: !121)
!121 = distinct !DILocation(line: 28, column: 5, scope: !45)
!122 = !DILocation(line: 29, column: 1, scope: !45)
!123 = !DILocation(line: 6, column: 15, scope: !11, inlinedAt: !57)
!124 = !DILocation(line: 7, column: 5, scope: !11, inlinedAt: !57)
!125 = !DILocation(line: 7, column: 15, scope: !11, inlinedAt: !57)
!126 = !DILocation(line: 8, column: 5, scope: !11, inlinedAt: !57)
!127 = !DILocation(line: 9, column: 5, scope: !11, inlinedAt: !57)
!128 = !DILocation(line: 10, column: 5, scope: !11, inlinedAt: !57)
!129 = distinct !DISubprogram(name: "process", scope: !1, file: !1, line: 31, type: !40, scopeLine: 31, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0, retainedNodes: !130)
!130 = !{!131, !132, !133}
!131 = !DILocalVariable(name: "apdu", arg: 1, scope: !129, file: !1, line: 31, type: !14)
!132 = !DILocalVariable(name: "len", arg: 2, scope: !129, file: !1, line: 31, type: !17)
!133 = !DILocalVariable(name: "buffer", scope: !129, file: !1, line: 32, type: !16)
!134 = !DILocation(line: 0, scope: !129)
!135 = !DILocation(line: 32, column: 20, scope: !129)
!136 = !DILocation(line: 33, column: 9, scope: !137)
!137 = distinct !DILexicalBlock(scope: !129, file: !1, line: 33, column: 9)
!138 = !DILocation(line: 33, column: 26, scope: !137)
!139 = !DILocation(line: 33, column: 9, scope: !129)
!140 = !DILocation(line: 33, column: 62, scope: !141)
!141 = distinct !DILexicalBlock(scope: !137, file: !1, line: 33, column: 35)
!142 = !DILocation(line: 33, column: 37, scope: !141)
!143 = !DILocation(line: 33, column: 80, scope: !141)
!144 = !DILocation(line: 34, column: 5, scope: !129)
!145 = !DILocation(line: 35, column: 1, scope: !129)
!146 = !DISubprogram(name: "jc_APDU_getBuffer", scope: !4, file: !4, line: 94, type: !147, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!147 = !DISubroutineType(types: !148)
!148 = !{!16, !14}
!149 = !DISubprogram(name: "jc_ISOException_throwIt", scope: !4, file: !4, line: 120, type: !150, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!150 = !DISubroutineType(types: !151)
!151 = !{null, !17}
