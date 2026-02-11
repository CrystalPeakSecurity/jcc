; ModuleID = 'main.c'
source_filename = "main.c"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-n32:64-S128-ni:1:10:20"
target triple = "wasm32-unknown-unknown"

@framebuffer = hidden global [2048 x i8] zeroinitializer, align 16, !dbg !0
@rng_state = hidden local_unnamed_addr global i16 0, align 2, !dbg !38
@tiles = hidden local_unnamed_addr global [16 x i8] zeroinitializer, align 16, !dbg !24
@work = hidden local_unnamed_addr global [4 x i8] zeroinitializer, align 4, !dbg !40
@score = hidden local_unnamed_addr global i16 0, align 2, !dbg !36
@tiles_prev = hidden local_unnamed_addr global [16 x i8] zeroinitializer, align 16, !dbg !30
@game_over = hidden local_unnamed_addr global i8 0, align 1, !dbg !32
@needs_full_redraw = hidden local_unnamed_addr global i8 0, align 1, !dbg !34
@DIGIT_FONT = hidden local_unnamed_addr constant [50 x i8] c"\07\05\05\05\07\02\06\02\02\07\07\01\07\04\07\07\01\07\01\07\05\05\07\01\01\07\04\07\01\07\07\04\07\05\07\07\01\01\01\01\07\05\07\05\07\07\05\07\01\07", align 16, !dbg !10
@TILE_DIGITS = hidden local_unnamed_addr constant [60 x i8] c"\00\00\00\00\00\01\00\00\00\02\01\00\00\00\04\01\00\00\00\08\02\00\00\01\06\02\00\00\03\02\02\00\00\06\04\03\00\01\02\08\03\00\02\05\06\03\00\05\01\02\04\01\00\02\04\04\02\00\04\08", align 16, !dbg !17
@_score_digits = hidden local_unnamed_addr global [4 x i8] zeroinitializer, align 1, !dbg !45
@game_initialized = hidden local_unnamed_addr global i8 0, align 1, !dbg !22

; Function Attrs: nounwind
define hidden void @clearFB(i8 noundef signext %0) local_unnamed_addr #0 !dbg !56 {
    #dbg_value(i8 %0, !60, !DIExpression(), !62)
  %2 = and i8 %0, 15, !dbg !63
  %3 = shl i8 %0, 4, !dbg !64
  %4 = or disjoint i8 %3, %2, !dbg !65
    #dbg_value(i8 %4, !61, !DIExpression(), !62)
  %5 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext 0, i16 noundef signext 2048, i8 noundef signext %4) #14, !dbg !66
  ret void, !dbg !67
}

declare !dbg !68 signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef, i16 noundef signext, i16 noundef signext, i8 noundef signext) local_unnamed_addr #1

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden void @setPixel(i16 noundef signext %0, i16 noundef signext %1, i8 noundef signext %2) local_unnamed_addr #2 !dbg !72 {
    #dbg_value(i16 %0, !76, !DIExpression(), !82)
    #dbg_value(i16 %1, !77, !DIExpression(), !82)
    #dbg_value(i8 %2, !78, !DIExpression(), !82)
  %4 = or i16 %1, %0, !dbg !83
  %5 = icmp ult i16 %4, 64, !dbg !83
  br i1 %5, label %6, label %25, !dbg !83

6:                                                ; preds = %3
  %7 = shl nuw nsw i16 %1, 5, !dbg !85
  %8 = lshr i16 %0, 1, !dbg !86
  %9 = or disjoint i16 %7, %8, !dbg !87
    #dbg_value(i16 %9, !79, !DIExpression(), !82)
  %10 = and i16 %0, 1, !dbg !88
  %11 = icmp eq i16 %10, 0, !dbg !88
  %12 = zext nneg i16 %9 to i32, !dbg !90
  %13 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %12, !dbg !90
  %14 = load i8, ptr %13, align 1, !dbg !90, !tbaa !91
  br i1 %11, label %19, label %15, !dbg !94

15:                                               ; preds = %6
  %16 = and i8 %14, -16, !dbg !95
  %17 = and i8 %2, 15, !dbg !97
  %18 = or disjoint i8 %16, %17, !dbg !98
  br label %23, !dbg !99

19:                                               ; preds = %6
  %20 = and i8 %14, 15, !dbg !100
  %21 = shl i8 %2, 4, !dbg !102
  %22 = or disjoint i8 %20, %21, !dbg !103
  br label %23

23:                                               ; preds = %19, %15
  %24 = phi i8 [ %18, %15 ], [ %22, %19 ]
  store i8 %24, ptr %13, align 1, !dbg !90, !tbaa !91
  br label %25, !dbg !104

25:                                               ; preds = %23, %3
  ret void, !dbg !104
}

; Function Attrs: nounwind
define hidden void @fillTile(i16 noundef signext %0, i16 noundef signext %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !105 {
    #dbg_value(i16 %0, !107, !DIExpression(), !112)
    #dbg_value(i16 %1, !108, !DIExpression(), !112)
    #dbg_value(i8 %2, !109, !DIExpression(), !112)
  %4 = shl i16 %1, 9, !dbg !113
  %5 = shl i16 %0, 3, !dbg !114
  %6 = add i16 %4, %5, !dbg !115
    #dbg_value(i16 %6, !110, !DIExpression(), !112)
  %7 = and i8 %2, 15, !dbg !116
  %8 = shl i8 %2, 4, !dbg !117
  %9 = or disjoint i8 %8, %7, !dbg !118
    #dbg_value(i8 %9, !111, !DIExpression(), !112)
  %10 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %6, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !119
  %11 = add i16 %6, 32, !dbg !120
  %12 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %11, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !120
  %13 = add i16 %6, 64, !dbg !121
  %14 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %13, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !121
  %15 = add i16 %6, 96, !dbg !122
  %16 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %15, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !122
  %17 = add i16 %6, 128, !dbg !123
  %18 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %17, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !123
  %19 = add i16 %6, 160, !dbg !124
  %20 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %19, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !124
  %21 = add i16 %6, 192, !dbg !125
  %22 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %21, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !125
  %23 = add i16 %6, 224, !dbg !126
  %24 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %23, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !126
  %25 = add i16 %6, 256, !dbg !127
  %26 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %25, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !127
  %27 = add i16 %6, 288, !dbg !128
  %28 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %27, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !128
  %29 = add i16 %6, 320, !dbg !129
  %30 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %29, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !129
  %31 = add i16 %6, 352, !dbg !130
  %32 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %31, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !130
  %33 = add i16 %6, 384, !dbg !131
  %34 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %33, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !131
  %35 = add i16 %6, 416, !dbg !132
  %36 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %35, i16 noundef signext 7, i8 noundef signext %9) #14, !dbg !132
  ret void, !dbg !133
}

; Function Attrs: nounwind
define hidden void @hline(i16 noundef signext %0, i16 noundef signext %1, i16 noundef signext %2, i8 noundef signext %3) local_unnamed_addr #0 !dbg !134 {
    #dbg_value(i16 %0, !138, !DIExpression(), !147)
    #dbg_value(i16 %1, !139, !DIExpression(), !147)
    #dbg_value(i16 %2, !140, !DIExpression(), !147)
    #dbg_value(i8 %3, !141, !DIExpression(), !147)
  %5 = icmp ugt i16 %2, 63, !dbg !148
  br i1 %5, label %65, label %6, !dbg !148

6:                                                ; preds = %4
  %7 = tail call i16 @llvm.smax.i16(i16 %0, i16 0), !dbg !150
    #dbg_value(i16 %7, !138, !DIExpression(), !147)
  %8 = tail call i16 @llvm.smin.i16(i16 %1, i16 63), !dbg !151
    #dbg_value(i16 %8, !139, !DIExpression(), !147)
  %9 = icmp sgt i16 %7, %8, !dbg !152
  br i1 %9, label %65, label %10, !dbg !154

10:                                               ; preds = %6
  %11 = and i8 %3, 15, !dbg !155
  %12 = shl i8 %3, 4, !dbg !156
  %13 = or disjoint i8 %12, %11, !dbg !157
    #dbg_value(i8 %13, !146, !DIExpression(), !147)
  %14 = shl nuw nsw i16 %2, 5, !dbg !158
    #dbg_value(i16 %14, !143, !DIExpression(), !147)
    #dbg_value(i16 %7, !142, !DIExpression(), !147)
  %15 = and i16 %7, 1, !dbg !159
  %16 = icmp eq i16 %15, 0, !dbg !159
  br i1 %16, label %30, label %17, !dbg !161

17:                                               ; preds = %10
    #dbg_value(i16 %7, !76, !DIExpression(), !162)
    #dbg_value(i16 %2, !77, !DIExpression(), !162)
    #dbg_value(i8 %3, !78, !DIExpression(), !162)
  %18 = or i16 %7, %2, !dbg !165
  %19 = icmp ult i16 %18, 64, !dbg !165
  br i1 %19, label %20, label %28, !dbg !165

20:                                               ; preds = %17
  %21 = lshr i16 %7, 1, !dbg !166
  %22 = or disjoint i16 %14, %21, !dbg !167
    #dbg_value(i16 %22, !79, !DIExpression(), !162)
  %23 = zext nneg i16 %22 to i32, !dbg !168
  %24 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %23, !dbg !168
  %25 = load i8, ptr %24, align 1, !dbg !168, !tbaa !91
  %26 = and i8 %25, -16, !dbg !169
  %27 = or disjoint i8 %26, %11, !dbg !170
  store i8 %27, ptr %24, align 1, !dbg !171, !tbaa !91
  br label %28, !dbg !172

28:                                               ; preds = %17, %20
  %29 = add nuw i16 %7, 1, !dbg !173
    #dbg_value(i16 %29, !142, !DIExpression(), !147)
  br label %30, !dbg !174

30:                                               ; preds = %28, %10
  %31 = phi i16 [ %29, %28 ], [ %7, %10 ], !dbg !147
    #dbg_value(i16 %31, !142, !DIExpression(), !147)
  %32 = sext i16 %31 to i32, !dbg !175
  %33 = add nsw i16 %8, 1, !dbg !176
  %34 = sext i16 %33 to i32, !dbg !176
  %35 = sub nsw i32 %34, %32, !dbg !177
  %36 = lshr i32 %35, 1, !dbg !178
    #dbg_value(i32 %36, !145, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !147)
  %37 = shl i32 %36, 16, !dbg !179
  %38 = icmp sgt i32 %37, 0, !dbg !181
  br i1 %38, label %39, label %47, !dbg !182

39:                                               ; preds = %30
  %40 = trunc i32 %36 to i16, !dbg !183
    #dbg_value(i16 %40, !145, !DIExpression(), !147)
  %41 = ashr i16 %31, 1, !dbg !184
  %42 = add nsw i16 %41, %14, !dbg !186
    #dbg_value(i16 %42, !144, !DIExpression(), !147)
  %43 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %42, i16 noundef signext %40, i8 noundef signext %13) #14, !dbg !187
  %44 = lshr exact i32 %37, 15, !dbg !188
  %45 = trunc nuw i32 %44 to i16, !dbg !189
  %46 = add i16 %31, %45, !dbg !189
    #dbg_value(i16 %46, !142, !DIExpression(), !147)
  br label %47, !dbg !190

47:                                               ; preds = %39, %30
  %48 = phi i16 [ %46, %39 ], [ %31, %30 ], !dbg !147
    #dbg_value(i16 %48, !142, !DIExpression(), !147)
  %49 = icmp sle i16 %48, %8, !dbg !191
    #dbg_value(i16 %48, !76, !DIExpression(), !193)
    #dbg_value(i16 %2, !77, !DIExpression(), !193)
    #dbg_value(i8 %3, !78, !DIExpression(), !193)
  %50 = or i16 %48, %2
  %51 = icmp ult i16 %50, 64
  %52 = and i1 %49, %51, !dbg !196
  br i1 %52, label %53, label %65, !dbg !196

53:                                               ; preds = %47
  %54 = lshr i16 %48, 1, !dbg !197
  %55 = or disjoint i16 %54, %14, !dbg !198
    #dbg_value(i16 %55, !79, !DIExpression(), !193)
  %56 = and i16 %48, 1, !dbg !199
  %57 = icmp eq i16 %56, 0, !dbg !199
  %58 = zext nneg i16 %55 to i32, !dbg !200
  %59 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %58, !dbg !200
  %60 = load i8, ptr %59, align 1, !dbg !200, !tbaa !91
  %61 = select i1 %57, i8 15, i8 -16
  %62 = select i1 %57, i8 %12, i8 %11
  %63 = and i8 %60, %61, !dbg !200
  %64 = or disjoint i8 %63, %62, !dbg !200
  store i8 %64, ptr %59, align 1, !dbg !200, !tbaa !91
  br label %65, !dbg !201

65:                                               ; preds = %53, %47, %6, %4
  ret void, !dbg !201
}

; Function Attrs: nounwind
define hidden void @fillRect(i16 noundef signext %0, i16 noundef signext %1, i16 noundef signext %2, i16 noundef signext %3, i8 noundef signext %4) local_unnamed_addr #0 !dbg !202 {
    #dbg_value(i16 %0, !206, !DIExpression(), !218)
    #dbg_value(i16 %1, !207, !DIExpression(), !218)
    #dbg_value(i16 %2, !208, !DIExpression(), !218)
    #dbg_value(i16 %3, !209, !DIExpression(), !218)
    #dbg_value(i8 %4, !210, !DIExpression(), !218)
  %6 = tail call i16 @llvm.smax.i16(i16 %0, i16 0), !dbg !219
    #dbg_value(i16 %6, !206, !DIExpression(), !218)
  %7 = tail call i16 @llvm.smax.i16(i16 %1, i16 0), !dbg !220
    #dbg_value(i16 %7, !207, !DIExpression(), !218)
  %8 = tail call i16 @llvm.smin.i16(i16 %2, i16 63), !dbg !221
    #dbg_value(i16 %8, !208, !DIExpression(), !218)
    #dbg_value(i16 poison, !209, !DIExpression(), !218)
  %9 = icmp sgt i16 %6, %8, !dbg !222
  br i1 %9, label %82, label %10, !dbg !224

10:                                               ; preds = %5
  %11 = tail call i16 @llvm.smin.i16(i16 %3, i16 63), !dbg !225
    #dbg_value(i16 %11, !209, !DIExpression(), !218)
  %12 = icmp sgt i16 %7, %11, !dbg !226
  br i1 %12, label %82, label %13, !dbg !227

13:                                               ; preds = %10
  %14 = and i8 %4, 15, !dbg !228
  %15 = shl i8 %4, 4, !dbg !229
  %16 = or disjoint i8 %15, %14, !dbg !230
    #dbg_value(i8 %16, !217, !DIExpression(), !218)
  %17 = icmp slt i16 %0, 1, !dbg !231
  %18 = icmp sgt i16 %2, 62
  %19 = and i1 %17, %18, !dbg !233
  br i1 %19, label %27, label %20, !dbg !233

20:                                               ; preds = %13
    #dbg_value(i16 %7, !211, !DIExpression(), !218)
  %21 = and i16 %6, 1
  %22 = icmp eq i16 %21, 0
  %23 = lshr i16 %6, 1
  %24 = add nuw i16 %6, 1
  %25 = add nsw i16 %8, 1
  %26 = sext i16 %25 to i32
  br label %33, !dbg !234

27:                                               ; preds = %13
  %28 = shl i16 %7, 5, !dbg !236
    #dbg_value(i16 %28, !214, !DIExpression(), !218)
  %29 = sub i16 %11, %7, !dbg !238
  %30 = shl i16 %29, 5, !dbg !239
  %31 = add i16 %30, 32, !dbg !239
    #dbg_value(i16 %31, !216, !DIExpression(), !218)
  %32 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %28, i16 noundef signext %31, i8 noundef signext %16) #14, !dbg !240
  br label %82, !dbg !241

33:                                               ; preds = %20, %79
  %34 = phi i16 [ %7, %20 ], [ %80, %79 ]
    #dbg_value(i16 %34, !211, !DIExpression(), !218)
  %35 = shl i16 %34, 5, !dbg !242
    #dbg_value(i16 %35, !213, !DIExpression(), !218)
    #dbg_value(i16 %6, !212, !DIExpression(), !218)
  br i1 %22, label %46, label %36, !dbg !245

36:                                               ; preds = %33
    #dbg_value(i16 %6, !76, !DIExpression(), !246)
    #dbg_value(i16 %34, !77, !DIExpression(), !246)
    #dbg_value(i8 %4, !78, !DIExpression(), !246)
  %37 = or i16 %34, %6, !dbg !250
  %38 = icmp ult i16 %37, 64, !dbg !250
  br i1 %38, label %39, label %46, !dbg !250

39:                                               ; preds = %36
  %40 = or disjoint i16 %35, %23, !dbg !251
    #dbg_value(i16 %40, !79, !DIExpression(), !246)
  %41 = zext nneg i16 %40 to i32, !dbg !252
  %42 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %41, !dbg !252
  %43 = load i8, ptr %42, align 1, !dbg !252, !tbaa !91
  %44 = and i8 %43, -16, !dbg !253
  %45 = or disjoint i8 %44, %14, !dbg !254
  store i8 %45, ptr %42, align 1, !dbg !255, !tbaa !91
  br label %46, !dbg !256

46:                                               ; preds = %39, %36, %33
  %47 = phi i16 [ %6, %33 ], [ %24, %36 ], [ %24, %39 ], !dbg !257
    #dbg_value(i16 %47, !212, !DIExpression(), !218)
  %48 = sext i16 %47 to i32, !dbg !258
  %49 = sub nsw i32 %26, %48, !dbg !259
  %50 = lshr i32 %49, 1, !dbg !260
    #dbg_value(i32 %50, !215, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !218)
  %51 = shl i32 %50, 16, !dbg !261
  %52 = icmp sgt i32 %51, 0, !dbg !263
  br i1 %52, label %53, label %61, !dbg !264

53:                                               ; preds = %46
  %54 = trunc i32 %50 to i16, !dbg !265
    #dbg_value(i16 %54, !215, !DIExpression(), !218)
  %55 = ashr i16 %47, 1, !dbg !266
  %56 = add i16 %55, %35, !dbg !268
    #dbg_value(i16 %56, !214, !DIExpression(), !218)
  %57 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %56, i16 noundef signext %54, i8 noundef signext %16) #14, !dbg !269
  %58 = lshr exact i32 %51, 15, !dbg !270
  %59 = trunc nuw i32 %58 to i16, !dbg !271
  %60 = add i16 %47, %59, !dbg !271
    #dbg_value(i16 %60, !212, !DIExpression(), !218)
  br label %61, !dbg !272

61:                                               ; preds = %53, %46
  %62 = phi i16 [ %60, %53 ], [ %47, %46 ], !dbg !257
    #dbg_value(i16 %62, !212, !DIExpression(), !218)
  %63 = icmp sle i16 %62, %8, !dbg !273
    #dbg_value(i16 %62, !76, !DIExpression(), !275)
    #dbg_value(i16 %34, !77, !DIExpression(), !275)
    #dbg_value(i8 %4, !78, !DIExpression(), !275)
  %64 = or i16 %62, %34
  %65 = icmp ult i16 %64, 64
  %66 = and i1 %63, %65, !dbg !278
  br i1 %66, label %67, label %79, !dbg !278

67:                                               ; preds = %61
  %68 = lshr i16 %62, 1, !dbg !279
  %69 = or disjoint i16 %68, %35, !dbg !280
    #dbg_value(i16 %69, !79, !DIExpression(), !275)
  %70 = and i16 %62, 1, !dbg !281
  %71 = icmp eq i16 %70, 0, !dbg !281
  %72 = zext nneg i16 %69 to i32, !dbg !282
  %73 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %72, !dbg !282
  %74 = load i8, ptr %73, align 1, !dbg !282, !tbaa !91
  %75 = select i1 %71, i8 15, i8 -16
  %76 = select i1 %71, i8 %15, i8 %14
  %77 = and i8 %74, %75, !dbg !282
  %78 = or disjoint i8 %77, %76, !dbg !282
  store i8 %78, ptr %73, align 1, !dbg !282, !tbaa !91
  br label %79, !dbg !283

79:                                               ; preds = %67, %61
  %80 = add nuw nsw i16 %34, 1, !dbg !283
    #dbg_value(i16 %80, !211, !DIExpression(), !218)
  %81 = icmp slt i16 %34, %11, !dbg !284
  br i1 %81, label %33, label %82, !dbg !234, !llvm.loop !285

82:                                               ; preds = %79, %5, %10, %27
  ret void, !dbg !289
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden signext range(i16 0, -32768) i16 @random_short() local_unnamed_addr #2 !dbg !290 {
  %1 = load i16, ptr @rng_state, align 2, !dbg !293, !tbaa !294
  %2 = mul i16 %1, 25173, !dbg !296
  %3 = add i16 %2, 13849, !dbg !297
  %4 = and i16 %3, 32767, !dbg !298
  store i16 %4, ptr @rng_state, align 2, !dbg !299, !tbaa !294
  ret i16 %4, !dbg !300
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(read, argmem: none, inaccessiblemem: none)
define hidden signext i8 @get_tile(i16 noundef signext %0, i16 noundef signext %1) local_unnamed_addr #3 !dbg !301 {
    #dbg_value(i16 %0, !305, !DIExpression(), !307)
    #dbg_value(i16 %1, !306, !DIExpression(), !307)
  %3 = sext i16 %1 to i32, !dbg !308
  %4 = shl nsw i32 %3, 2, !dbg !309
  %5 = sext i16 %0 to i32, !dbg !310
  %6 = add nsw i32 %4, %5, !dbg !311
  %7 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %6, !dbg !312
  %8 = load i8, ptr %7, align 1, !dbg !312, !tbaa !91
  ret i8 %8, !dbg !313
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(write, argmem: none, inaccessiblemem: none)
define hidden void @set_tile(i16 noundef signext %0, i16 noundef signext %1, i8 noundef signext %2) local_unnamed_addr #4 !dbg !314 {
    #dbg_value(i16 %0, !316, !DIExpression(), !319)
    #dbg_value(i16 %1, !317, !DIExpression(), !319)
    #dbg_value(i8 %2, !318, !DIExpression(), !319)
  %4 = sext i16 %1 to i32, !dbg !320
  %5 = shl nsw i32 %4, 2, !dbg !321
  %6 = sext i16 %0 to i32, !dbg !322
  %7 = add nsw i32 %5, %6, !dbg !323
  %8 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %7, !dbg !324
  store i8 %2, ptr %8, align 1, !dbg !325, !tbaa !91
  ret void, !dbg !326
}

; Function Attrs: nofree norecurse nosync nounwind memory(read, argmem: none, inaccessiblemem: none)
define hidden signext i16 @count_empty() local_unnamed_addr #5 !dbg !327 {
    #dbg_value(i16 0, !330, !DIExpression(), !331)
    #dbg_value(i16 0, !329, !DIExpression(), !331)
  br label %1, !dbg !332

1:                                                ; preds = %0, %1
  %2 = phi i32 [ 0, %0 ], [ %9, %1 ]
  %3 = phi i16 [ 0, %0 ], [ %8, %1 ]
    #dbg_value(i16 %3, !330, !DIExpression(), !331)
    #dbg_value(i32 %2, !329, !DIExpression(), !331)
  %4 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %2, !dbg !334
  %5 = load i8, ptr %4, align 1, !dbg !334, !tbaa !91
  %6 = icmp eq i8 %5, 0, !dbg !338
  %7 = zext i1 %6 to i16, !dbg !339
  %8 = add i16 %3, %7, !dbg !339
    #dbg_value(i16 %8, !330, !DIExpression(), !331)
  %9 = add nuw nsw i32 %2, 1, !dbg !340
    #dbg_value(i32 %9, !329, !DIExpression(), !331)
  %10 = icmp eq i32 %9, 16, !dbg !341
  br i1 %10, label %11, label %1, !dbg !332, !llvm.loop !342

11:                                               ; preds = %1
  ret i16 %8, !dbg !344
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden void @spawn_tile() local_unnamed_addr #6 !dbg !345 {
    #dbg_value(i16 0, !330, !DIExpression(), !354)
    #dbg_value(i16 0, !329, !DIExpression(), !354)
  br label %1, !dbg !356

1:                                                ; preds = %1, %0
  %2 = phi i32 [ 0, %0 ], [ %9, %1 ]
  %3 = phi i16 [ 0, %0 ], [ %8, %1 ]
    #dbg_value(i16 %3, !330, !DIExpression(), !354)
    #dbg_value(i32 %2, !329, !DIExpression(), !354)
  %4 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %2, !dbg !357
  %5 = load i8, ptr %4, align 1, !dbg !357, !tbaa !91
  %6 = icmp eq i8 %5, 0, !dbg !358
  %7 = zext i1 %6 to i16, !dbg !359
  %8 = add i16 %3, %7, !dbg !359
    #dbg_value(i16 %8, !330, !DIExpression(), !354)
  %9 = add nuw nsw i32 %2, 1, !dbg !360
    #dbg_value(i32 %9, !329, !DIExpression(), !354)
  %10 = icmp eq i32 %9, 16, !dbg !361
  br i1 %10, label %11, label %1, !dbg !356, !llvm.loop !362

11:                                               ; preds = %1
    #dbg_value(i16 %8, !349, !DIExpression(), !364)
  %12 = icmp eq i16 %8, 0, !dbg !365
  br i1 %12, label %43, label %13, !dbg !367

13:                                               ; preds = %11
  %14 = sext i16 %8 to i32, !dbg !368
  %15 = load i16, ptr @rng_state, align 2, !dbg !369, !tbaa !294
  %16 = mul i16 %15, 25173, !dbg !371
  %17 = add i16 %16, 13849, !dbg !372
  %18 = and i16 %17, 32767, !dbg !373
  %19 = zext nneg i16 %18 to i32, !dbg !374
  %20 = srem i32 %19, %14, !dbg !375
    #dbg_value(i32 %20, !352, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !364)
  %21 = mul i16 %17, 25173, !dbg !376
  %22 = add i16 %21, 13849, !dbg !378
  %23 = and i16 %22, 32767, !dbg !379
  store i16 %23, ptr @rng_state, align 2, !dbg !380, !tbaa !294
  %24 = urem i16 %23, 10, !dbg !381
  %25 = icmp ult i16 %24, 9, !dbg !382
  %26 = select i1 %25, i8 1, i8 2, !dbg !383
    #dbg_value(i8 %26, !353, !DIExpression(), !364)
    #dbg_value(i16 0, !350, !DIExpression(), !364)
    #dbg_value(i16 0, !351, !DIExpression(), !364)
  br label %27, !dbg !384

27:                                               ; preds = %13, %39
  %28 = phi i32 [ 0, %13 ], [ %41, %39 ]
  %29 = phi i16 [ 0, %13 ], [ %40, %39 ]
    #dbg_value(i16 %29, !350, !DIExpression(), !364)
    #dbg_value(i32 %28, !351, !DIExpression(), !364)
  %30 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %28, !dbg !386
  %31 = load i8, ptr %30, align 1, !dbg !386, !tbaa !91
  %32 = icmp eq i8 %31, 0, !dbg !390
  br i1 %32, label %33, label %39, !dbg !391

33:                                               ; preds = %27
  %34 = sext i16 %29 to i32, !dbg !392
  %35 = icmp eq i32 %20, %34, !dbg !395
  br i1 %35, label %36, label %37, !dbg !396

36:                                               ; preds = %33
  store i8 %26, ptr %30, align 1, !dbg !397, !tbaa !91
  br label %43, !dbg !399

37:                                               ; preds = %33
  %38 = add i16 %29, 1, !dbg !400
    #dbg_value(i16 %38, !350, !DIExpression(), !364)
  br label %39, !dbg !401

39:                                               ; preds = %27, %37
  %40 = phi i16 [ %38, %37 ], [ %29, %27 ], !dbg !364
    #dbg_value(i16 %40, !350, !DIExpression(), !364)
  %41 = add nuw nsw i32 %28, 1, !dbg !402
    #dbg_value(i32 %41, !351, !DIExpression(), !364)
  %42 = icmp eq i32 %41, 16, !dbg !403
  br i1 %42, label %43, label %27, !dbg !384, !llvm.loop !404

43:                                               ; preds = %39, %11, %36
  ret void, !dbg !406
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden signext range(i8 0, 2) i8 @slide_line() local_unnamed_addr #6 !dbg !407 {
    #dbg_value(i8 0, !413, !DIExpression(), !414)
    #dbg_value(i16 0, !412, !DIExpression(), !414)
    #dbg_value(i16 0, !411, !DIExpression(), !414)
  br label %3, !dbg !415

1:                                                ; preds = %19
  %2 = load i16, ptr @score, align 2, !tbaa !294
    #dbg_value(i8 %21, !413, !DIExpression(), !414)
    #dbg_value(i16 0, !411, !DIExpression(), !414)
  br label %24, !dbg !417

3:                                                ; preds = %0, %19
  %4 = phi i32 [ 0, %0 ], [ %22, %19 ]
  %5 = phi i8 [ 0, %0 ], [ %21, %19 ]
  %6 = phi i16 [ 0, %0 ], [ %20, %19 ]
    #dbg_value(i8 %5, !413, !DIExpression(), !414)
    #dbg_value(i16 %6, !412, !DIExpression(), !414)
    #dbg_value(i32 %4, !411, !DIExpression(), !414)
  %7 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %4, !dbg !419
  %8 = load i8, ptr %7, align 1, !dbg !419, !tbaa !91
  %9 = icmp eq i8 %8, 0, !dbg !423
  br i1 %9, label %19, label %10, !dbg !424

10:                                               ; preds = %3
  %11 = zext i16 %6 to i32, !dbg !425
  %12 = icmp eq i32 %4, %11, !dbg !425
  br i1 %12, label %16, label %13, !dbg !428

13:                                               ; preds = %10
  %14 = sext i16 %6 to i32, !dbg !429
  %15 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %14, !dbg !430
  store i8 %8, ptr %15, align 1, !dbg !432, !tbaa !91
  store i8 0, ptr %7, align 1, !dbg !433, !tbaa !91
    #dbg_value(i8 1, !413, !DIExpression(), !414)
  br label %16, !dbg !434

16:                                               ; preds = %13, %10
  %17 = phi i8 [ 1, %13 ], [ %5, %10 ], !dbg !414
    #dbg_value(i8 %17, !413, !DIExpression(), !414)
  %18 = add i16 %6, 1, !dbg !435
    #dbg_value(i16 %18, !412, !DIExpression(), !414)
  br label %19, !dbg !436

19:                                               ; preds = %3, %16
  %20 = phi i16 [ %18, %16 ], [ %6, %3 ], !dbg !414
  %21 = phi i8 [ %17, %16 ], [ %5, %3 ], !dbg !414
    #dbg_value(i8 %21, !413, !DIExpression(), !414)
    #dbg_value(i16 %20, !412, !DIExpression(), !414)
  %22 = add nuw nsw i32 %4, 1, !dbg !437
    #dbg_value(i32 %22, !411, !DIExpression(), !414)
  %23 = icmp eq i32 %22, 4, !dbg !438
  br i1 %23, label %1, label %3, !dbg !415, !llvm.loop !439

24:                                               ; preds = %1, %42
  %25 = phi i32 [ 0, %1 ], [ %45, %42 ]
  %26 = phi i8 [ %21, %1 ], [ %44, %42 ]
  %27 = phi i16 [ %2, %1 ], [ %43, %42 ]
    #dbg_value(i8 %26, !413, !DIExpression(), !414)
    #dbg_value(i32 %25, !411, !DIExpression(), !414)
  %28 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %25, !dbg !441
  %29 = load i8, ptr %28, align 1, !dbg !441, !tbaa !91
  %30 = icmp eq i8 %29, 0, !dbg !445
  br i1 %30, label %42, label %31, !dbg !446

31:                                               ; preds = %24
  %32 = add nuw nsw i32 %25, 1, !dbg !447
  %33 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %32, !dbg !448
  %34 = load i8, ptr %33, align 1, !dbg !448, !tbaa !91
  %35 = icmp eq i8 %29, %34, !dbg !449
  br i1 %35, label %36, label %42, !dbg !450

36:                                               ; preds = %31
  %37 = add i8 %29, 1, !dbg !451
  store i8 %37, ptr %28, align 1, !dbg !453, !tbaa !91
  %38 = zext nneg i8 %37 to i32, !dbg !454
  %39 = shl nuw i32 1, %38, !dbg !454
  %40 = trunc i32 %39 to i16, !dbg !455
  %41 = add i16 %27, %40, !dbg !455
  store i16 %41, ptr @score, align 2, !dbg !456, !tbaa !294
  store i8 0, ptr %33, align 1, !dbg !457, !tbaa !91
    #dbg_value(i8 1, !413, !DIExpression(), !414)
  br label %42, !dbg !458

42:                                               ; preds = %24, %31, %36
  %43 = phi i16 [ %41, %36 ], [ %27, %31 ], [ %27, %24 ]
  %44 = phi i8 [ 1, %36 ], [ %26, %31 ], [ %26, %24 ], !dbg !414
    #dbg_value(i8 %44, !413, !DIExpression(), !414)
  %45 = add nuw nsw i32 %25, 1, !dbg !459
    #dbg_value(i32 %45, !411, !DIExpression(), !414)
  %46 = icmp eq i32 %45, 3, !dbg !460
  br i1 %46, label %47, label %24, !dbg !417, !llvm.loop !461

47:                                               ; preds = %42, %61
  %48 = phi i32 [ %63, %61 ], [ 0, %42 ]
  %49 = phi i16 [ %62, %61 ], [ 0, %42 ]
    #dbg_value(i16 %49, !412, !DIExpression(), !414)
    #dbg_value(i32 %48, !411, !DIExpression(), !414)
  %50 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %48, !dbg !463
  %51 = load i8, ptr %50, align 1, !dbg !463, !tbaa !91
  %52 = icmp eq i8 %51, 0, !dbg !468
  br i1 %52, label %61, label %53, !dbg !469

53:                                               ; preds = %47
  %54 = zext i16 %49 to i32, !dbg !470
  %55 = icmp eq i32 %48, %54, !dbg !470
  br i1 %55, label %59, label %56, !dbg !473

56:                                               ; preds = %53
  %57 = sext i16 %49 to i32, !dbg !474
  %58 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %57, !dbg !475
  store i8 %51, ptr %58, align 1, !dbg !477, !tbaa !91
  store i8 0, ptr %50, align 1, !dbg !478, !tbaa !91
  br label %59, !dbg !479

59:                                               ; preds = %56, %53
  %60 = add i16 %49, 1, !dbg !480
    #dbg_value(i16 %60, !412, !DIExpression(), !414)
  br label %61, !dbg !481

61:                                               ; preds = %47, %59
  %62 = phi i16 [ %60, %59 ], [ %49, %47 ], !dbg !414
    #dbg_value(i16 %62, !412, !DIExpression(), !414)
  %63 = add nuw nsw i32 %48, 1, !dbg !482
    #dbg_value(i32 %63, !411, !DIExpression(), !414)
  %64 = icmp eq i32 %63, 4, !dbg !483
  br i1 %64, label %65, label %47, !dbg !484, !llvm.loop !485

65:                                               ; preds = %61
  ret i8 %44, !dbg !487
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define hidden signext range(i8 0, 2) i8 @move_tiles(i8 noundef signext %0) local_unnamed_addr #7 !dbg !488 {
    #dbg_value(i8 %0, !492, !DIExpression(), !497)
    #dbg_value(i8 0, !496, !DIExpression(), !497)
  %2 = icmp eq i8 %0, 3, !dbg !498
  br i1 %2, label %3, label %17, !dbg !500

3:                                                ; preds = %1, %13
  %4 = phi i32 [ %15, %13 ], [ 0, %1 ]
  %5 = phi i8 [ %14, %13 ], [ 0, %1 ]
  %6 = shl nuw nsw i32 %4, 2
  %7 = getelementptr i8, ptr @tiles, i32 %6
    #dbg_value(i8 %5, !496, !DIExpression(), !497)
    #dbg_value(i16 poison, !493, !DIExpression(), !497)
    #dbg_value(i16 0, !495, !DIExpression(), !497)
  %8 = load i32, ptr %7, align 4, !dbg !501, !tbaa !91
  store i32 %8, ptr @work, align 4, !dbg !501, !tbaa !91
    #dbg_value(i32 poison, !495, !DIExpression(), !497)
    #dbg_value(i32 poison, !305, !DIExpression(), !508)
    #dbg_value(i16 poison, !306, !DIExpression(), !508)
  %9 = tail call signext i8 @slide_line(), !dbg !510
  %10 = icmp eq i8 %9, 0, !dbg !510
  br i1 %10, label %13, label %11, !dbg !512

11:                                               ; preds = %3
    #dbg_value(i16 0, !495, !DIExpression(), !497)
  %12 = load i32, ptr @work, align 4, !dbg !513, !tbaa !91
  store i32 %12, ptr %7, align 4, !dbg !513, !tbaa !91
    #dbg_value(i32 poison, !495, !DIExpression(), !497)
    #dbg_value(i32 poison, !316, !DIExpression(), !518)
    #dbg_value(i16 poison, !317, !DIExpression(), !518)
    #dbg_value(i8 poison, !318, !DIExpression(), !518)
  br label %13, !dbg !519

13:                                               ; preds = %11, %3
  %14 = phi i8 [ %5, %3 ], [ 1, %11 ], !dbg !497
    #dbg_value(i8 %14, !496, !DIExpression(), !497)
    #dbg_value(i16 poison, !493, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !497)
  %15 = add nuw nsw i32 %4, 1, !dbg !520
  %16 = icmp eq i32 %15, 4, !dbg !521
  br i1 %16, label %17, label %3, !dbg !520, !llvm.loop !522

17:                                               ; preds = %13, %1
  %18 = phi i8 [ 0, %1 ], [ %14, %13 ], !dbg !524
    #dbg_value(i8 %18, !496, !DIExpression(), !497)
  %19 = icmp eq i8 %0, 4, !dbg !525
  br i1 %19, label %20, label %49, !dbg !527

20:                                               ; preds = %17, %45
  %21 = phi i32 [ %47, %45 ], [ 0, %17 ]
  %22 = phi i8 [ %46, %45 ], [ %18, %17 ]
    #dbg_value(i8 %22, !496, !DIExpression(), !497)
    #dbg_value(i32 %21, !493, !DIExpression(), !497)
  %23 = shl nsw i32 %21, 2
    #dbg_value(i16 0, !495, !DIExpression(), !497)
  br label %24, !dbg !528

24:                                               ; preds = %20, %24
  %25 = phi i32 [ 0, %20 ], [ %31, %24 ]
    #dbg_value(i32 %25, !495, !DIExpression(), !497)
    #dbg_value(!DIArgList(i32 3, i32 %25), !305, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !534)
    #dbg_value(i32 %21, !306, !DIExpression(), !534)
  %26 = sub nsw i32 %23, %25, !dbg !537
  %27 = add i32 %26, 3, !dbg !537
  %28 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %27, !dbg !538
  %29 = load i8, ptr %28, align 1, !dbg !538, !tbaa !91
  %30 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %25, !dbg !539
  store i8 %29, ptr %30, align 1, !dbg !540, !tbaa !91
  %31 = add nuw nsw i32 %25, 1, !dbg !541
    #dbg_value(i32 %31, !495, !DIExpression(), !497)
  %32 = icmp eq i32 %31, 4, !dbg !542
  br i1 %32, label %33, label %24, !dbg !528, !llvm.loop !543

33:                                               ; preds = %24
  %34 = tail call signext i8 @slide_line(), !dbg !545
  %35 = icmp eq i8 %34, 0, !dbg !545
  br i1 %35, label %45, label %36, !dbg !547

36:                                               ; preds = %33, %36
  %37 = phi i32 [ %43, %36 ], [ 0, %33 ]
    #dbg_value(i32 %37, !495, !DIExpression(), !497)
  %38 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %37, !dbg !548
  %39 = load i8, ptr %38, align 1, !dbg !548, !tbaa !91
    #dbg_value(!DIArgList(i32 3, i32 %37), !316, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !552)
    #dbg_value(i32 %21, !317, !DIExpression(), !552)
    #dbg_value(i8 %39, !318, !DIExpression(), !552)
  %40 = sub nsw i32 %23, %37, !dbg !554
  %41 = add i32 %40, 3, !dbg !554
  %42 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %41, !dbg !555
  store i8 %39, ptr %42, align 1, !dbg !556, !tbaa !91
  %43 = add nuw nsw i32 %37, 1, !dbg !557
    #dbg_value(i32 %43, !495, !DIExpression(), !497)
  %44 = icmp eq i32 %43, 4, !dbg !558
  br i1 %44, label %45, label %36, !dbg !559, !llvm.loop !560

45:                                               ; preds = %36, %33
  %46 = phi i8 [ %22, %33 ], [ 1, %36 ], !dbg !497
    #dbg_value(i8 %46, !496, !DIExpression(), !497)
  %47 = add nuw nsw i32 %21, 1, !dbg !562
    #dbg_value(i32 %47, !493, !DIExpression(), !497)
  %48 = icmp eq i32 %47, 4, !dbg !563
  br i1 %48, label %49, label %20, !dbg !564, !llvm.loop !565

49:                                               ; preds = %45, %17
  %50 = phi i8 [ %18, %17 ], [ %46, %45 ], !dbg !524
    #dbg_value(i8 %50, !496, !DIExpression(), !497)
  %51 = icmp eq i8 %0, 1, !dbg !567
  br i1 %51, label %52, label %80, !dbg !569

52:                                               ; preds = %49, %76
  %53 = phi i32 [ %78, %76 ], [ 0, %49 ]
  %54 = phi i8 [ %77, %76 ], [ %50, %49 ]
    #dbg_value(i8 %54, !496, !DIExpression(), !497)
    #dbg_value(i32 %53, !494, !DIExpression(), !497)
    #dbg_value(i16 0, !495, !DIExpression(), !497)
  br label %55, !dbg !570

55:                                               ; preds = %52, %55
  %56 = phi i32 [ 0, %52 ], [ %62, %55 ]
    #dbg_value(i32 %56, !495, !DIExpression(), !497)
    #dbg_value(i32 %53, !305, !DIExpression(), !576)
    #dbg_value(i32 %56, !306, !DIExpression(), !576)
  %57 = shl nsw i32 %56, 2, !dbg !579
  %58 = add nuw nsw i32 %57, %53, !dbg !580
  %59 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %58, !dbg !581
  %60 = load i8, ptr %59, align 1, !dbg !581, !tbaa !91
  %61 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %56, !dbg !582
  store i8 %60, ptr %61, align 1, !dbg !583, !tbaa !91
  %62 = add nuw nsw i32 %56, 1, !dbg !584
    #dbg_value(i32 %62, !495, !DIExpression(), !497)
  %63 = icmp eq i32 %62, 4, !dbg !585
  br i1 %63, label %64, label %55, !dbg !570, !llvm.loop !586

64:                                               ; preds = %55
  %65 = tail call signext i8 @slide_line(), !dbg !588
  %66 = icmp eq i8 %65, 0, !dbg !588
  br i1 %66, label %76, label %67, !dbg !590

67:                                               ; preds = %64, %67
  %68 = phi i32 [ %74, %67 ], [ 0, %64 ]
    #dbg_value(i32 %68, !495, !DIExpression(), !497)
  %69 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %68, !dbg !591
  %70 = load i8, ptr %69, align 1, !dbg !591, !tbaa !91
    #dbg_value(i32 %53, !316, !DIExpression(), !595)
    #dbg_value(i32 %68, !317, !DIExpression(), !595)
    #dbg_value(i8 %70, !318, !DIExpression(), !595)
  %71 = shl nsw i32 %68, 2, !dbg !597
  %72 = add nuw nsw i32 %71, %53, !dbg !598
  %73 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %72, !dbg !599
  store i8 %70, ptr %73, align 1, !dbg !600, !tbaa !91
  %74 = add nuw nsw i32 %68, 1, !dbg !601
    #dbg_value(i32 %74, !495, !DIExpression(), !497)
  %75 = icmp eq i32 %74, 4, !dbg !602
  br i1 %75, label %76, label %67, !dbg !603, !llvm.loop !604

76:                                               ; preds = %67, %64
  %77 = phi i8 [ %54, %64 ], [ 1, %67 ], !dbg !497
    #dbg_value(i8 %77, !496, !DIExpression(), !497)
  %78 = add nuw nsw i32 %53, 1, !dbg !606
    #dbg_value(i32 %78, !494, !DIExpression(), !497)
  %79 = icmp eq i32 %78, 4, !dbg !607
  br i1 %79, label %80, label %52, !dbg !608, !llvm.loop !609

80:                                               ; preds = %76, %49
  %81 = phi i8 [ %50, %49 ], [ %77, %76 ], !dbg !524
    #dbg_value(i8 %81, !496, !DIExpression(), !497)
  %82 = icmp eq i8 %0, 2, !dbg !611
  br i1 %82, label %83, label %113, !dbg !613

83:                                               ; preds = %80, %109
  %84 = phi i32 [ %111, %109 ], [ 0, %80 ]
  %85 = phi i8 [ %110, %109 ], [ %81, %80 ]
    #dbg_value(i8 %85, !496, !DIExpression(), !497)
    #dbg_value(i32 %84, !494, !DIExpression(), !497)
    #dbg_value(i16 0, !495, !DIExpression(), !497)
  br label %86, !dbg !614

86:                                               ; preds = %83, %86
  %87 = phi i32 [ 0, %83 ], [ %94, %86 ]
    #dbg_value(i32 %87, !495, !DIExpression(), !497)
    #dbg_value(i32 %84, !305, !DIExpression(), !620)
    #dbg_value(!DIArgList(i32 3, i32 %87), !306, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !620)
  %88 = shl i32 %87, 2, !dbg !623
  %89 = sub i32 %84, %88, !dbg !624
  %90 = add i32 %89, 12, !dbg !624
  %91 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %90, !dbg !625
  %92 = load i8, ptr %91, align 1, !dbg !625, !tbaa !91
  %93 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %87, !dbg !626
  store i8 %92, ptr %93, align 1, !dbg !627, !tbaa !91
  %94 = add nuw nsw i32 %87, 1, !dbg !628
    #dbg_value(i32 %94, !495, !DIExpression(), !497)
  %95 = icmp eq i32 %94, 4, !dbg !629
  br i1 %95, label %96, label %86, !dbg !614, !llvm.loop !630

96:                                               ; preds = %86
  %97 = tail call signext i8 @slide_line(), !dbg !632
  %98 = icmp eq i8 %97, 0, !dbg !632
  br i1 %98, label %109, label %99, !dbg !634

99:                                               ; preds = %96, %99
  %100 = phi i32 [ %107, %99 ], [ 0, %96 ]
    #dbg_value(i32 %100, !495, !DIExpression(), !497)
  %101 = getelementptr inbounds [4 x i8], ptr @work, i32 0, i32 %100, !dbg !635
  %102 = load i8, ptr %101, align 1, !dbg !635, !tbaa !91
    #dbg_value(i32 %84, !316, !DIExpression(), !639)
    #dbg_value(!DIArgList(i32 3, i32 %100), !317, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !639)
    #dbg_value(i8 %102, !318, !DIExpression(), !639)
  %103 = shl i32 %100, 2, !dbg !641
  %104 = sub i32 %84, %103, !dbg !642
  %105 = add i32 %104, 12, !dbg !642
  %106 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %105, !dbg !643
  store i8 %102, ptr %106, align 1, !dbg !644, !tbaa !91
  %107 = add nuw nsw i32 %100, 1, !dbg !645
    #dbg_value(i32 %107, !495, !DIExpression(), !497)
  %108 = icmp eq i32 %107, 4, !dbg !646
  br i1 %108, label %109, label %99, !dbg !647, !llvm.loop !648

109:                                              ; preds = %99, %96
  %110 = phi i8 [ %85, %96 ], [ 1, %99 ], !dbg !497
    #dbg_value(i8 %110, !496, !DIExpression(), !497)
  %111 = add nuw nsw i32 %84, 1, !dbg !650
    #dbg_value(i32 %111, !494, !DIExpression(), !497)
  %112 = icmp eq i32 %111, 4, !dbg !651
  br i1 %112, label %113, label %83, !dbg !652, !llvm.loop !653

113:                                              ; preds = %109, %80
  %114 = phi i8 [ %81, %80 ], [ %110, %109 ], !dbg !524
    #dbg_value(i8 %114, !496, !DIExpression(), !497)
  ret i8 %114, !dbg !655
}

; Function Attrs: nofree norecurse nosync nounwind memory(read, argmem: none, inaccessiblemem: none)
define hidden signext range(i8 0, 2) i8 @can_move() local_unnamed_addr #5 !dbg !656 {
    #dbg_value(i16 0, !330, !DIExpression(), !661)
    #dbg_value(i16 0, !329, !DIExpression(), !661)
  br label %1, !dbg !664

1:                                                ; preds = %1, %0
  %2 = phi i32 [ 0, %0 ], [ %9, %1 ]
  %3 = phi i16 [ 0, %0 ], [ %8, %1 ]
    #dbg_value(i16 %3, !330, !DIExpression(), !661)
    #dbg_value(i32 %2, !329, !DIExpression(), !661)
  %4 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %2, !dbg !665
  %5 = load i8, ptr %4, align 1, !dbg !665, !tbaa !91
  %6 = icmp eq i8 %5, 0, !dbg !666
  %7 = zext i1 %6 to i16, !dbg !667
  %8 = add i16 %3, %7, !dbg !667
    #dbg_value(i16 %8, !330, !DIExpression(), !661)
  %9 = add nuw nsw i32 %2, 1, !dbg !668
    #dbg_value(i32 %9, !329, !DIExpression(), !661)
  %10 = icmp eq i32 %9, 16, !dbg !669
  br i1 %10, label %11, label %1, !dbg !664, !llvm.loop !670

11:                                               ; preds = %1
  %12 = icmp sgt i16 %8, 0, !dbg !672
  br i1 %12, label %42, label %13, !dbg !673

13:                                               ; preds = %11, %40
  %14 = phi i32 [ %17, %40 ], [ 0, %11 ]
    #dbg_value(i32 %14, !658, !DIExpression(), !674)
  %15 = shl nsw i32 %14, 2
    #dbg_value(i16 0, !659, !DIExpression(), !674)
  %16 = icmp eq i32 %14, 3
  %17 = add nuw nsw i32 %14, 1, !dbg !675
  %18 = shl nsw i32 %17, 2
  br label %19, !dbg !678

19:                                               ; preds = %13, %37
  %20 = phi i32 [ 0, %13 ], [ %38, %37 ]
    #dbg_value(i32 %20, !659, !DIExpression(), !674)
    #dbg_value(i32 %20, !305, !DIExpression(), !681)
    #dbg_value(i32 %14, !306, !DIExpression(), !681)
  %21 = add nuw nsw i32 %15, %20, !dbg !685
  %22 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %21, !dbg !686
  %23 = load i8, ptr %22, align 1, !dbg !686, !tbaa !91
    #dbg_value(i8 %23, !660, !DIExpression(), !674)
  %24 = icmp eq i32 %20, 3, !dbg !687
  br i1 %24, label %31, label %25, !dbg !689

25:                                               ; preds = %19
  %26 = add nuw nsw i32 %20, 1, !dbg !690
    #dbg_value(i32 %26, !305, !DIExpression(), !691)
    #dbg_value(i32 %14, !306, !DIExpression(), !691)
  %27 = add nuw nsw i32 %15, %26, !dbg !693
  %28 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %27, !dbg !694
  %29 = load i8, ptr %28, align 1, !dbg !694, !tbaa !91
  %30 = icmp eq i8 %29, %23, !dbg !695
  br i1 %30, label %42, label %31, !dbg !696

31:                                               ; preds = %25, %19
  br i1 %16, label %37, label %32, !dbg !697

32:                                               ; preds = %31
    #dbg_value(i32 %20, !305, !DIExpression(), !699)
    #dbg_value(i32 %17, !306, !DIExpression(), !699)
  %33 = add nuw nsw i32 %18, %20, !dbg !701
  %34 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %33, !dbg !702
  %35 = load i8, ptr %34, align 1, !dbg !702, !tbaa !91
  %36 = icmp eq i8 %35, %23, !dbg !703
  br i1 %36, label %42, label %37, !dbg !704

37:                                               ; preds = %31, %32
  %38 = add nuw nsw i32 %20, 1, !dbg !705
    #dbg_value(i32 %38, !659, !DIExpression(), !674)
  %39 = icmp eq i32 %38, 4, !dbg !706
  br i1 %39, label %40, label %19, !dbg !678, !llvm.loop !707

40:                                               ; preds = %37
    #dbg_value(i32 %17, !658, !DIExpression(), !674)
  %41 = icmp eq i32 %17, 4, !dbg !709
  br i1 %41, label %42, label %13, !dbg !710, !llvm.loop !711

42:                                               ; preds = %40, %32, %25, %11
  %43 = phi i8 [ 1, %11 ], [ 1, %25 ], [ 1, %32 ], [ 0, %40 ], !dbg !674
  ret i8 %43, !dbg !713
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden void @reset_game() local_unnamed_addr #6 !dbg !714 {
    #dbg_value(i16 0, !716, !DIExpression(), !717)
  tail call void @llvm.memset.p0.i32(ptr noundef nonnull align 16 dereferenceable(16) @tiles, i8 0, i32 16, i1 false), !dbg !718, !tbaa !91
  tail call void @llvm.memset.p0.i32(ptr noundef nonnull align 16 dereferenceable(16) @tiles_prev, i8 -1, i32 16, i1 false), !dbg !722, !tbaa !91
    #dbg_value(i32 poison, !716, !DIExpression(), !717)
  store i8 0, ptr @game_over, align 1, !dbg !723, !tbaa !91
  store i8 1, ptr @needs_full_redraw, align 1, !dbg !724, !tbaa !91
  store i16 0, ptr @score, align 2, !dbg !725, !tbaa !294
  store i16 12345, ptr @rng_state, align 2, !dbg !726, !tbaa !294
    #dbg_value(i16 0, !330, !DIExpression(), !727)
    #dbg_value(i16 0, !329, !DIExpression(), !727)
  br label %1, !dbg !730

1:                                                ; preds = %1, %0
  %2 = phi i32 [ 0, %0 ], [ %9, %1 ]
  %3 = phi i16 [ 0, %0 ], [ %8, %1 ]
    #dbg_value(i16 %3, !330, !DIExpression(), !727)
    #dbg_value(i32 %2, !329, !DIExpression(), !727)
  %4 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %2, !dbg !731
  %5 = load i8, ptr %4, align 1, !dbg !731, !tbaa !91
  %6 = icmp eq i8 %5, 0, !dbg !732
  %7 = zext i1 %6 to i16, !dbg !733
  %8 = add i16 %3, %7, !dbg !733
    #dbg_value(i16 %8, !330, !DIExpression(), !727)
  %9 = add nuw nsw i32 %2, 1, !dbg !734
    #dbg_value(i32 %9, !329, !DIExpression(), !727)
  %10 = icmp eq i32 %9, 16, !dbg !735
  br i1 %10, label %11, label %1, !dbg !730, !llvm.loop !736

11:                                               ; preds = %1
    #dbg_value(i16 %8, !349, !DIExpression(), !738)
  %12 = icmp eq i16 %8, 0, !dbg !739
  br i1 %12, label %32, label %13, !dbg !740

13:                                               ; preds = %11
  %14 = sext i16 %8 to i32, !dbg !741
  %15 = srem i32 2822, %14, !dbg !742
    #dbg_value(i32 %15, !352, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !738)
  store i16 11031, ptr @rng_state, align 2, !dbg !743, !tbaa !294
    #dbg_value(i8 1, !353, !DIExpression(), !738)
    #dbg_value(i16 0, !350, !DIExpression(), !738)
    #dbg_value(i16 0, !351, !DIExpression(), !738)
  br label %16, !dbg !745

16:                                               ; preds = %28, %13
  %17 = phi i32 [ 0, %13 ], [ %30, %28 ]
  %18 = phi i16 [ 0, %13 ], [ %29, %28 ]
    #dbg_value(i16 %18, !350, !DIExpression(), !738)
    #dbg_value(i32 %17, !351, !DIExpression(), !738)
  %19 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %17, !dbg !746
  %20 = load i8, ptr %19, align 1, !dbg !746, !tbaa !91
  %21 = icmp eq i8 %20, 0, !dbg !747
  br i1 %21, label %22, label %28, !dbg !748

22:                                               ; preds = %16
  %23 = sext i16 %18 to i32, !dbg !749
  %24 = icmp eq i32 %15, %23, !dbg !750
  br i1 %24, label %25, label %26, !dbg !751

25:                                               ; preds = %22
  store i8 1, ptr %19, align 1, !dbg !752, !tbaa !91
  br label %32, !dbg !753

26:                                               ; preds = %22
  %27 = add i16 %18, 1, !dbg !754
    #dbg_value(i16 %27, !350, !DIExpression(), !738)
  br label %28, !dbg !755

28:                                               ; preds = %26, %16
  %29 = phi i16 [ %27, %26 ], [ %18, %16 ], !dbg !738
    #dbg_value(i16 %29, !350, !DIExpression(), !738)
  %30 = add nuw nsw i32 %17, 1, !dbg !756
    #dbg_value(i32 %30, !351, !DIExpression(), !738)
  %31 = icmp eq i32 %30, 16, !dbg !757
  br i1 %31, label %32, label %16, !dbg !745, !llvm.loop !758

32:                                               ; preds = %28, %11, %25
  br label %33, !dbg !760

33:                                               ; preds = %32, %33
  %34 = phi i32 [ %41, %33 ], [ 0, %32 ]
  %35 = phi i16 [ %40, %33 ], [ 0, %32 ]
    #dbg_value(i16 %35, !330, !DIExpression(), !763)
    #dbg_value(i32 %34, !329, !DIExpression(), !763)
  %36 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %34, !dbg !764
  %37 = load i8, ptr %36, align 1, !dbg !764, !tbaa !91
  %38 = icmp eq i8 %37, 0, !dbg !765
  %39 = zext i1 %38 to i16, !dbg !766
  %40 = add i16 %35, %39, !dbg !766
    #dbg_value(i16 %40, !330, !DIExpression(), !763)
  %41 = add nuw nsw i32 %34, 1, !dbg !767
    #dbg_value(i32 %41, !329, !DIExpression(), !763)
  %42 = icmp eq i32 %41, 16, !dbg !768
  br i1 %42, label %43, label %33, !dbg !760, !llvm.loop !769

43:                                               ; preds = %33
    #dbg_value(i16 %40, !349, !DIExpression(), !771)
  %44 = icmp eq i16 %40, 0, !dbg !772
  br i1 %44, label %75, label %45, !dbg !773

45:                                               ; preds = %43
  %46 = sext i16 %40 to i32, !dbg !774
  %47 = load i16, ptr @rng_state, align 2, !dbg !775, !tbaa !294
  %48 = mul i16 %47, 25173, !dbg !777
  %49 = add i16 %48, 13849, !dbg !778
  %50 = and i16 %49, 32767, !dbg !779
  %51 = zext nneg i16 %50 to i32, !dbg !780
  %52 = srem i32 %51, %46, !dbg !781
    #dbg_value(i32 %52, !352, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !771)
  %53 = mul i16 %49, 25173, !dbg !782
  %54 = add i16 %53, 13849, !dbg !784
  %55 = and i16 %54, 32767, !dbg !785
  store i16 %55, ptr @rng_state, align 2, !dbg !786, !tbaa !294
  %56 = urem i16 %55, 10, !dbg !787
  %57 = icmp ult i16 %56, 9, !dbg !788
  %58 = select i1 %57, i8 1, i8 2, !dbg !789
    #dbg_value(i8 %58, !353, !DIExpression(), !771)
    #dbg_value(i16 0, !350, !DIExpression(), !771)
    #dbg_value(i16 0, !351, !DIExpression(), !771)
  br label %59, !dbg !790

59:                                               ; preds = %71, %45
  %60 = phi i32 [ 0, %45 ], [ %73, %71 ]
  %61 = phi i16 [ 0, %45 ], [ %72, %71 ]
    #dbg_value(i16 %61, !350, !DIExpression(), !771)
    #dbg_value(i32 %60, !351, !DIExpression(), !771)
  %62 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %60, !dbg !791
  %63 = load i8, ptr %62, align 1, !dbg !791, !tbaa !91
  %64 = icmp eq i8 %63, 0, !dbg !792
  br i1 %64, label %65, label %71, !dbg !793

65:                                               ; preds = %59
  %66 = sext i16 %61 to i32, !dbg !794
  %67 = icmp eq i32 %52, %66, !dbg !795
  br i1 %67, label %68, label %69, !dbg !796

68:                                               ; preds = %65
  store i8 %58, ptr %62, align 1, !dbg !797, !tbaa !91
  br label %75, !dbg !798

69:                                               ; preds = %65
  %70 = add i16 %61, 1, !dbg !799
    #dbg_value(i16 %70, !350, !DIExpression(), !771)
  br label %71, !dbg !800

71:                                               ; preds = %69, %59
  %72 = phi i16 [ %70, %69 ], [ %61, %59 ], !dbg !771
    #dbg_value(i16 %72, !350, !DIExpression(), !771)
  %73 = add nuw nsw i32 %60, 1, !dbg !801
    #dbg_value(i32 %73, !351, !DIExpression(), !771)
  %74 = icmp eq i32 %73, 16, !dbg !802
  br i1 %74, label %75, label %59, !dbg !790, !llvm.loop !803

75:                                               ; preds = %71, %43, %68
  ret void, !dbg !805
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(read, argmem: none, inaccessiblemem: none)
define hidden signext range(i8 0, 2) i8 @tile_dirty(i16 noundef signext %0) local_unnamed_addr #3 !dbg !806 {
    #dbg_value(i16 %0, !809, !DIExpression(), !810)
  %2 = sext i16 %0 to i32, !dbg !811
  %3 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %2, !dbg !811
  %4 = load i8, ptr %3, align 1, !dbg !811, !tbaa !91
  %5 = getelementptr inbounds [16 x i8], ptr @tiles_prev, i32 0, i32 %2, !dbg !812
  %6 = load i8, ptr %5, align 1, !dbg !812, !tbaa !91
  %7 = icmp ne i8 %4, %6, !dbg !813
  %8 = zext i1 %7 to i8, !dbg !811
  ret i8 %8, !dbg !814
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden void @mark_tiles_clean() local_unnamed_addr #2 !dbg !815 {
    #dbg_value(i16 0, !817, !DIExpression(), !818)
  tail call void @llvm.memcpy.p0.p0.i32(ptr noundef nonnull align 16 dereferenceable(16) @tiles_prev, ptr noundef nonnull align 16 dereferenceable(16) @tiles, i32 16, i1 false), !dbg !819, !tbaa !91
    #dbg_value(i32 poison, !817, !DIExpression(), !818)
  store i8 0, ptr @needs_full_redraw, align 1, !dbg !823, !tbaa !91
  ret void, !dbg !824
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define hidden void @game_tick(i8 noundef signext %0) local_unnamed_addr #7 !dbg !825 {
    #dbg_value(i8 %0, !827, !DIExpression(), !828)
  %2 = load i8, ptr @game_over, align 1, !dbg !829, !tbaa !91
  %3 = icmp eq i8 %2, 0, !dbg !829
  %4 = icmp eq i8 %0, 0, !dbg !828
  br i1 %3, label %7, label %5, !dbg !831

5:                                                ; preds = %1
  br i1 %4, label %96, label %6, !dbg !832

6:                                                ; preds = %5
  tail call void @reset_game(), !dbg !834
  br label %96, !dbg !837

7:                                                ; preds = %1
  br i1 %4, label %96, label %8, !dbg !838

8:                                                ; preds = %7
  %9 = tail call signext i8 @move_tiles(i8 noundef signext %0), !dbg !839
  %10 = icmp eq i8 %9, 0, !dbg !839
  br i1 %10, label %96, label %11, !dbg !843

11:                                               ; preds = %8, %11
  %12 = phi i32 [ %19, %11 ], [ 0, %8 ]
  %13 = phi i16 [ %18, %11 ], [ 0, %8 ]
    #dbg_value(i16 %13, !330, !DIExpression(), !844)
    #dbg_value(i32 %12, !329, !DIExpression(), !844)
  %14 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %12, !dbg !848
  %15 = load i8, ptr %14, align 1, !dbg !848, !tbaa !91
  %16 = icmp eq i8 %15, 0, !dbg !849
  %17 = zext i1 %16 to i16, !dbg !850
  %18 = add i16 %13, %17, !dbg !850
    #dbg_value(i16 %18, !330, !DIExpression(), !844)
  %19 = add nuw nsw i32 %12, 1, !dbg !851
    #dbg_value(i32 %19, !329, !DIExpression(), !844)
  %20 = icmp eq i32 %19, 16, !dbg !852
  br i1 %20, label %21, label %11, !dbg !853, !llvm.loop !854

21:                                               ; preds = %11
    #dbg_value(i16 %18, !349, !DIExpression(), !856)
  %22 = icmp eq i16 %18, 0, !dbg !857
  br i1 %22, label %53, label %23, !dbg !858

23:                                               ; preds = %21
  %24 = sext i16 %18 to i32, !dbg !859
  %25 = load i16, ptr @rng_state, align 2, !dbg !860, !tbaa !294
  %26 = mul i16 %25, 25173, !dbg !862
  %27 = add i16 %26, 13849, !dbg !863
  %28 = and i16 %27, 32767, !dbg !864
  %29 = zext nneg i16 %28 to i32, !dbg !865
  %30 = srem i32 %29, %24, !dbg !866
    #dbg_value(i32 %30, !352, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !856)
  %31 = mul i16 %27, 25173, !dbg !867
  %32 = add i16 %31, 13849, !dbg !869
  %33 = and i16 %32, 32767, !dbg !870
  store i16 %33, ptr @rng_state, align 2, !dbg !871, !tbaa !294
  %34 = urem i16 %33, 10, !dbg !872
  %35 = icmp ult i16 %34, 9, !dbg !873
  %36 = select i1 %35, i8 1, i8 2, !dbg !874
    #dbg_value(i8 %36, !353, !DIExpression(), !856)
    #dbg_value(i16 0, !350, !DIExpression(), !856)
    #dbg_value(i16 0, !351, !DIExpression(), !856)
  br label %37, !dbg !875

37:                                               ; preds = %49, %23
  %38 = phi i32 [ 0, %23 ], [ %51, %49 ]
  %39 = phi i16 [ 0, %23 ], [ %50, %49 ]
    #dbg_value(i16 %39, !350, !DIExpression(), !856)
    #dbg_value(i32 %38, !351, !DIExpression(), !856)
  %40 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %38, !dbg !876
  %41 = load i8, ptr %40, align 1, !dbg !876, !tbaa !91
  %42 = icmp eq i8 %41, 0, !dbg !877
  br i1 %42, label %43, label %49, !dbg !878

43:                                               ; preds = %37
  %44 = sext i16 %39 to i32, !dbg !879
  %45 = icmp eq i32 %30, %44, !dbg !880
  br i1 %45, label %46, label %47, !dbg !881

46:                                               ; preds = %43
  store i8 %36, ptr %40, align 1, !dbg !882, !tbaa !91
  br label %53, !dbg !883

47:                                               ; preds = %43
  %48 = add i16 %39, 1, !dbg !884
    #dbg_value(i16 %48, !350, !DIExpression(), !856)
  br label %49, !dbg !885

49:                                               ; preds = %47, %37
  %50 = phi i16 [ %48, %47 ], [ %39, %37 ], !dbg !856
    #dbg_value(i16 %50, !350, !DIExpression(), !856)
  %51 = add nuw nsw i32 %38, 1, !dbg !886
    #dbg_value(i32 %51, !351, !DIExpression(), !856)
  %52 = icmp eq i32 %51, 16, !dbg !887
  br i1 %52, label %53, label %37, !dbg !875, !llvm.loop !888

53:                                               ; preds = %49, %21, %46
  br label %54, !dbg !890

54:                                               ; preds = %53, %54
  %55 = phi i32 [ %62, %54 ], [ 0, %53 ]
  %56 = phi i16 [ %61, %54 ], [ 0, %53 ]
    #dbg_value(i16 %56, !330, !DIExpression(), !894)
    #dbg_value(i32 %55, !329, !DIExpression(), !894)
  %57 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %55, !dbg !895
  %58 = load i8, ptr %57, align 1, !dbg !895, !tbaa !91
  %59 = icmp eq i8 %58, 0, !dbg !896
  %60 = zext i1 %59 to i16, !dbg !897
  %61 = add i16 %56, %60, !dbg !897
    #dbg_value(i16 %61, !330, !DIExpression(), !894)
  %62 = add nuw nsw i32 %55, 1, !dbg !898
    #dbg_value(i32 %62, !329, !DIExpression(), !894)
  %63 = icmp eq i32 %62, 16, !dbg !899
  br i1 %63, label %64, label %54, !dbg !890, !llvm.loop !900

64:                                               ; preds = %54
  %65 = icmp sgt i16 %61, 0, !dbg !902
  br i1 %65, label %96, label %66, !dbg !903

66:                                               ; preds = %64, %93
  %67 = phi i32 [ %70, %93 ], [ 0, %64 ]
    #dbg_value(i32 %67, !658, !DIExpression(), !904)
  %68 = shl nsw i32 %67, 2
    #dbg_value(i16 0, !659, !DIExpression(), !904)
  %69 = icmp eq i32 %67, 3
  %70 = add nuw nsw i32 %67, 1, !dbg !905
  %71 = shl nsw i32 %70, 2
  %72 = or disjoint i32 %68, 1
  br label %73, !dbg !906

73:                                               ; preds = %90, %66
  %74 = phi i32 [ 0, %66 ], [ %91, %90 ]
    #dbg_value(i32 %74, !659, !DIExpression(), !904)
    #dbg_value(i32 %74, !305, !DIExpression(), !907)
    #dbg_value(i32 %67, !306, !DIExpression(), !907)
  %75 = add nuw nsw i32 %74, %68, !dbg !909
  %76 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %75, !dbg !910
  %77 = load i8, ptr %76, align 1, !dbg !910, !tbaa !91
    #dbg_value(i8 %77, !660, !DIExpression(), !904)
  %78 = icmp eq i32 %74, 3, !dbg !911
  br i1 %78, label %84, label %79, !dbg !912

79:                                               ; preds = %73
    #dbg_value(i32 poison, !305, !DIExpression(), !913)
    #dbg_value(i32 %67, !306, !DIExpression(), !913)
  %80 = add nuw nsw i32 %72, %74, !dbg !915
  %81 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %80, !dbg !916
  %82 = load i8, ptr %81, align 1, !dbg !916, !tbaa !91
  %83 = icmp eq i8 %82, %77, !dbg !917
  br i1 %83, label %96, label %84, !dbg !918

84:                                               ; preds = %79, %73
  br i1 %69, label %90, label %85, !dbg !919

85:                                               ; preds = %84
    #dbg_value(i32 %74, !305, !DIExpression(), !920)
    #dbg_value(i32 %70, !306, !DIExpression(), !920)
  %86 = add nuw nsw i32 %74, %71, !dbg !922
  %87 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %86, !dbg !923
  %88 = load i8, ptr %87, align 1, !dbg !923, !tbaa !91
  %89 = icmp eq i8 %88, %77, !dbg !924
  br i1 %89, label %96, label %90, !dbg !925

90:                                               ; preds = %85, %84
  %91 = add nuw nsw i32 %74, 1, !dbg !926
    #dbg_value(i32 %91, !659, !DIExpression(), !904)
  %92 = icmp eq i32 %91, 4, !dbg !927
  br i1 %92, label %93, label %73, !dbg !906, !llvm.loop !928

93:                                               ; preds = %90
    #dbg_value(i32 %70, !658, !DIExpression(), !904)
  %94 = icmp eq i32 %70, 4, !dbg !930
  br i1 %94, label %95, label %66, !dbg !931, !llvm.loop !932

95:                                               ; preds = %93
  store i8 1, ptr @game_over, align 1, !dbg !934, !tbaa !91
  br label %96, !dbg !936

96:                                               ; preds = %79, %85, %64, %8, %95, %5, %6, %7
  ret void, !dbg !937
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(write, argmem: none, inaccessiblemem: none)
define hidden void @drawDigitFast(i16 noundef signext %0, i16 noundef signext %1, i16 noundef signext %2, i8 noundef signext %3, i8 noundef signext %4) local_unnamed_addr #4 !dbg !938 {
    #dbg_value(i16 %0, !942, !DIExpression(), !953)
    #dbg_value(i16 %1, !943, !DIExpression(), !953)
    #dbg_value(i16 %2, !944, !DIExpression(), !953)
    #dbg_value(i8 %3, !945, !DIExpression(), !953)
    #dbg_value(i8 %4, !946, !DIExpression(), !953)
  %6 = icmp ugt i16 %2, 9, !dbg !954
  br i1 %6, label %117, label %7, !dbg !954

7:                                                ; preds = %5
  %8 = mul nuw nsw i16 %2, 5, !dbg !956
    #dbg_value(i16 %8, !948, !DIExpression(), !953)
  %9 = shl i16 %1, 5, !dbg !957
  %10 = ashr i16 %0, 1, !dbg !958
  %11 = add i16 %9, %10, !dbg !959
    #dbg_value(i16 %11, !949, !DIExpression(), !953)
  %12 = zext nneg i16 %8 to i32, !dbg !960
  %13 = getelementptr inbounds [50 x i8], ptr @DIGIT_FONT, i32 0, i32 %12, !dbg !960
  %14 = load i8, ptr %13, align 1, !dbg !960, !tbaa !91
    #dbg_value(i8 %14, !947, !DIExpression(), !953)
  %15 = zext i8 %14 to i32, !dbg !961
  %16 = and i32 %15, 4, !dbg !962
  %17 = icmp eq i32 %16, 0, !dbg !962
  %18 = select i1 %17, i8 %4, i8 %3, !dbg !963
    #dbg_value(i8 %18, !950, !DIExpression(), !953)
  %19 = and i32 %15, 2, !dbg !964
  %20 = icmp eq i32 %19, 0, !dbg !964
  %21 = select i1 %20, i8 %4, i8 %3, !dbg !965
    #dbg_value(i8 %21, !951, !DIExpression(), !953)
  %22 = and i32 %15, 1, !dbg !966
  %23 = icmp eq i32 %22, 0, !dbg !966
  %24 = select i1 %23, i8 %4, i8 %3, !dbg !967
    #dbg_value(i8 %24, !952, !DIExpression(), !953)
  %25 = shl i8 %18, 4, !dbg !968
  %26 = or i8 %25, %21, !dbg !969
  %27 = sext i16 %11 to i32, !dbg !970
  %28 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %27, !dbg !970
  store i8 %26, ptr %28, align 1, !dbg !971, !tbaa !91
  %29 = shl i8 %24, 4, !dbg !972
  %30 = or i8 %29, %4, !dbg !973
  %31 = add nsw i32 %27, 1, !dbg !974
  %32 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %31, !dbg !975
  store i8 %30, ptr %32, align 1, !dbg !976, !tbaa !91
  %33 = add nuw nsw i32 %12, 1, !dbg !977
  %34 = getelementptr inbounds [50 x i8], ptr @DIGIT_FONT, i32 0, i32 %33, !dbg !978
  %35 = load i8, ptr %34, align 1, !dbg !978, !tbaa !91
    #dbg_value(i8 %35, !947, !DIExpression(), !953)
  %36 = zext i8 %35 to i32, !dbg !979
  %37 = and i32 %36, 4, !dbg !980
  %38 = icmp eq i32 %37, 0, !dbg !980
  %39 = select i1 %38, i8 %4, i8 %3, !dbg !981
    #dbg_value(i8 %39, !950, !DIExpression(), !953)
  %40 = and i32 %36, 2, !dbg !982
  %41 = icmp eq i32 %40, 0, !dbg !982
  %42 = select i1 %41, i8 %4, i8 %3, !dbg !983
    #dbg_value(i8 %42, !951, !DIExpression(), !953)
  %43 = and i32 %36, 1, !dbg !984
  %44 = icmp eq i32 %43, 0, !dbg !984
  %45 = select i1 %44, i8 %4, i8 %3, !dbg !985
    #dbg_value(i8 %45, !952, !DIExpression(), !953)
  %46 = shl i8 %39, 4, !dbg !986
  %47 = or i8 %46, %42, !dbg !987
  %48 = add nsw i32 %27, 32, !dbg !988
  %49 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %48, !dbg !989
  store i8 %47, ptr %49, align 1, !dbg !990, !tbaa !91
  %50 = shl i8 %45, 4, !dbg !991
  %51 = or i8 %50, %4, !dbg !992
  %52 = add nsw i32 %27, 33, !dbg !993
  %53 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %52, !dbg !994
  store i8 %51, ptr %53, align 1, !dbg !995, !tbaa !91
  %54 = add nuw nsw i32 %12, 2, !dbg !996
  %55 = getelementptr inbounds [50 x i8], ptr @DIGIT_FONT, i32 0, i32 %54, !dbg !997
  %56 = load i8, ptr %55, align 1, !dbg !997, !tbaa !91
    #dbg_value(i8 %56, !947, !DIExpression(), !953)
  %57 = zext i8 %56 to i32, !dbg !998
  %58 = and i32 %57, 4, !dbg !999
  %59 = icmp eq i32 %58, 0, !dbg !999
  %60 = select i1 %59, i8 %4, i8 %3, !dbg !1000
    #dbg_value(i8 %60, !950, !DIExpression(), !953)
  %61 = and i32 %57, 2, !dbg !1001
  %62 = icmp eq i32 %61, 0, !dbg !1001
  %63 = select i1 %62, i8 %4, i8 %3, !dbg !1002
    #dbg_value(i8 %63, !951, !DIExpression(), !953)
  %64 = and i32 %57, 1, !dbg !1003
  %65 = icmp eq i32 %64, 0, !dbg !1003
  %66 = select i1 %65, i8 %4, i8 %3, !dbg !1004
    #dbg_value(i8 %66, !952, !DIExpression(), !953)
  %67 = shl i8 %60, 4, !dbg !1005
  %68 = or i8 %67, %63, !dbg !1006
  %69 = add nsw i32 %27, 64, !dbg !1007
  %70 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %69, !dbg !1008
  store i8 %68, ptr %70, align 1, !dbg !1009, !tbaa !91
  %71 = shl i8 %66, 4, !dbg !1010
  %72 = or i8 %71, %4, !dbg !1011
  %73 = add nsw i32 %27, 65, !dbg !1012
  %74 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %73, !dbg !1013
  store i8 %72, ptr %74, align 1, !dbg !1014, !tbaa !91
  %75 = add nuw nsw i32 %12, 3, !dbg !1015
  %76 = getelementptr inbounds [50 x i8], ptr @DIGIT_FONT, i32 0, i32 %75, !dbg !1016
  %77 = load i8, ptr %76, align 1, !dbg !1016, !tbaa !91
    #dbg_value(i8 %77, !947, !DIExpression(), !953)
  %78 = zext i8 %77 to i32, !dbg !1017
  %79 = and i32 %78, 4, !dbg !1018
  %80 = icmp eq i32 %79, 0, !dbg !1018
  %81 = select i1 %80, i8 %4, i8 %3, !dbg !1019
    #dbg_value(i8 %81, !950, !DIExpression(), !953)
  %82 = and i32 %78, 2, !dbg !1020
  %83 = icmp eq i32 %82, 0, !dbg !1020
  %84 = select i1 %83, i8 %4, i8 %3, !dbg !1021
    #dbg_value(i8 %84, !951, !DIExpression(), !953)
  %85 = and i32 %78, 1, !dbg !1022
  %86 = icmp eq i32 %85, 0, !dbg !1022
  %87 = select i1 %86, i8 %4, i8 %3, !dbg !1023
    #dbg_value(i8 %87, !952, !DIExpression(), !953)
  %88 = shl i8 %81, 4, !dbg !1024
  %89 = or i8 %88, %84, !dbg !1025
  %90 = add nsw i32 %27, 96, !dbg !1026
  %91 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %90, !dbg !1027
  store i8 %89, ptr %91, align 1, !dbg !1028, !tbaa !91
  %92 = shl i8 %87, 4, !dbg !1029
  %93 = or i8 %92, %4, !dbg !1030
  %94 = add nsw i32 %27, 97, !dbg !1031
  %95 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %94, !dbg !1032
  store i8 %93, ptr %95, align 1, !dbg !1033, !tbaa !91
  %96 = add nuw nsw i32 %12, 4, !dbg !1034
  %97 = getelementptr inbounds [50 x i8], ptr @DIGIT_FONT, i32 0, i32 %96, !dbg !1035
  %98 = load i8, ptr %97, align 1, !dbg !1035, !tbaa !91
    #dbg_value(i8 %98, !947, !DIExpression(), !953)
  %99 = zext i8 %98 to i32, !dbg !1036
  %100 = and i32 %99, 4, !dbg !1037
  %101 = icmp eq i32 %100, 0, !dbg !1037
  %102 = select i1 %101, i8 %4, i8 %3, !dbg !1038
    #dbg_value(i8 %102, !950, !DIExpression(), !953)
  %103 = and i32 %99, 2, !dbg !1039
  %104 = icmp eq i32 %103, 0, !dbg !1039
  %105 = select i1 %104, i8 %4, i8 %3, !dbg !1040
    #dbg_value(i8 %105, !951, !DIExpression(), !953)
  %106 = and i32 %99, 1, !dbg !1041
  %107 = icmp eq i32 %106, 0, !dbg !1041
  %108 = select i1 %107, i8 %4, i8 %3, !dbg !1042
    #dbg_value(i8 %108, !952, !DIExpression(), !953)
  %109 = shl i8 %102, 4, !dbg !1043
  %110 = or i8 %109, %105, !dbg !1044
  %111 = add nsw i32 %27, 128, !dbg !1045
  %112 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %111, !dbg !1046
  store i8 %110, ptr %112, align 1, !dbg !1047, !tbaa !91
  %113 = shl i8 %108, 4, !dbg !1048
  %114 = or i8 %113, %4, !dbg !1049
  %115 = add nsw i32 %27, 129, !dbg !1050
  %116 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %115, !dbg !1051
  store i8 %114, ptr %116, align 1, !dbg !1052, !tbaa !91
  br label %117, !dbg !1053

117:                                              ; preds = %5, %7
  ret void, !dbg !1053
}

; Function Attrs: nofree norecurse nosync nounwind memory(write, inaccessiblemem: none)
define hidden void @drawNumberInTile(i16 noundef signext %0, i16 noundef signext %1, i8 noundef signext %2, i8 noundef signext %3, i8 noundef signext %4) local_unnamed_addr #8 !dbg !1054 {
    #dbg_value(i16 %0, !1058, !DIExpression(), !1068)
    #dbg_value(i16 %1, !1059, !DIExpression(), !1068)
    #dbg_value(i8 %2, !1060, !DIExpression(), !1068)
    #dbg_value(i8 %3, !1061, !DIExpression(), !1068)
    #dbg_value(i8 %4, !1062, !DIExpression(), !1068)
  %6 = icmp eq i8 %2, 0, !dbg !1069
  %7 = icmp sgt i8 %2, 11
  %8 = or i1 %6, %7, !dbg !1071
  br i1 %8, label %50, label %9, !dbg !1071

9:                                                ; preds = %5
  %10 = sext i8 %2 to i32, !dbg !1072
  %11 = mul nsw i32 %10, 5, !dbg !1073
    #dbg_value(i8 %2, !1063, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_constu, 5, DW_OP_mul, DW_OP_stack_value), !1068)
    #dbg_value(i8 poison, !1064, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 32, DW_ATE_signed, DW_OP_stack_value), !1068)
  %12 = zext nneg i32 %11 to i64, !dbg !1074
  %13 = lshr i64 2533412237771808, %12, !dbg !1074
  %14 = and i64 %13, 1, !dbg !1074
  %15 = icmp eq i64 %14, 0, !dbg !1074
  br i1 %15, label %23, label %16, !dbg !1076

16:                                               ; preds = %9
  %17 = add i16 %0, -1, !dbg !1077
  %18 = add i16 %1, -2, !dbg !1079
  %19 = add nsw i32 %11, 4, !dbg !1080
  %20 = getelementptr inbounds [60 x i8], ptr @TILE_DIGITS, i32 0, i32 %19, !dbg !1081
  %21 = load i8, ptr %20, align 1, !dbg !1081, !tbaa !91
  %22 = sext i8 %21 to i16, !dbg !1081
  tail call void @drawDigitFast(i16 noundef signext %17, i16 noundef signext %18, i16 noundef signext %22, i8 noundef signext %3, i8 noundef signext %4), !dbg !1082
  br label %50, !dbg !1083

23:                                               ; preds = %9
    #dbg_value(i8 poison, !1064, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 32, DW_ATE_signed, DW_OP_stack_value), !1068)
    #dbg_value(i8 poison, !1064, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 32, DW_ATE_signed, DW_OP_stack_value), !1068)
    #dbg_value(i8 poison, !1065, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_stack_value), !1068)
    #dbg_value(!DIArgList(i16 poison, i8 poison), !1066, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1068)
    #dbg_value(!DIArgList(i16 poison, i8 poison), !1067, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_minus, DW_OP_stack_value), !1068)
    #dbg_value(!DIArgList(i16 poison, i8 poison), !1066, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1068)
  %24 = lshr i64 1004230073766168096, %12, !dbg !1084
  %25 = and i64 %24, 1, !dbg !1084
  %26 = icmp eq i64 %25, 0, !dbg !1084
  br i1 %26, label %50, label %27, !dbg !1087

27:                                               ; preds = %23
  %28 = getelementptr inbounds [60 x i8], ptr @TILE_DIGITS, i32 0, i32 %11, !dbg !1088
  %29 = load i8, ptr %28, align 1, !dbg !1088, !tbaa !91
    #dbg_value(!DIArgList(i16 4, i8 %29), !1067, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_minus, DW_OP_stack_value), !1068)
    #dbg_value(!DIArgList(i16 %0, i8 %29), !1066, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1068)
    #dbg_value(i8 %29, !1065, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_stack_value), !1068)
    #dbg_value(i8 %29, !1064, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 32, DW_ATE_signed, DW_OP_stack_value), !1068)
  %30 = sext i8 %29 to i16, !dbg !1089
    #dbg_value(!DIArgList(i16 4, i16 %30), !1067, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !1068)
    #dbg_value(!DIArgList(i16 %0, i16 %30), !1066, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1068)
    #dbg_value(!DIArgList(i16 4, i16 %30), !1067, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !1068)
  %31 = shl nsw i16 %30, 2, !dbg !1090
    #dbg_value(!DIArgList(i16 %0, i16 %31), !1066, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1068)
  %32 = add nsw i16 %31, 255, !dbg !1090
    #dbg_value(!DIArgList(i16 %0, i16 %32), !1066, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1068)
  %33 = lshr i16 %32, 1, !dbg !1091
    #dbg_value(!DIArgList(i16 %0, i16 %33), !1066, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1068)
  %34 = and i16 %33, 127, !dbg !1091
    #dbg_value(!DIArgList(i16 %0, i16 %34), !1066, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !1068)
  %35 = sub i16 %0, %34, !dbg !1091
    #dbg_value(i16 %35, !1066, !DIExpression(), !1068)
  %36 = add i16 %1, -2
  %37 = add nsw i32 %11, 1
  %38 = sub nsw i16 4, %30, !dbg !1087
  %39 = sext i16 %38 to i32, !dbg !1087
  br label %40, !dbg !1087

40:                                               ; preds = %27, %40
  %41 = phi i32 [ %39, %27 ], [ %48, %40 ]
  %42 = phi i16 [ %35, %27 ], [ %47, %40 ]
    #dbg_value(i32 %41, !1067, !DIExpression(), !1068)
    #dbg_value(i16 %42, !1066, !DIExpression(), !1068)
  %43 = add nsw i32 %37, %41, !dbg !1092
  %44 = getelementptr inbounds [60 x i8], ptr @TILE_DIGITS, i32 0, i32 %43, !dbg !1094
  %45 = load i8, ptr %44, align 1, !dbg !1094, !tbaa !91
  %46 = sext i8 %45 to i16, !dbg !1094
  tail call void @drawDigitFast(i16 noundef signext %42, i16 noundef signext %36, i16 noundef signext %46, i8 noundef signext %3, i8 noundef signext %4), !dbg !1095
  %47 = add i16 %42, 4, !dbg !1096
    #dbg_value(i16 %47, !1066, !DIExpression(), !1068)
  %48 = add nsw i32 %41, 1, !dbg !1097
    #dbg_value(i32 %48, !1067, !DIExpression(), !1068)
  %49 = icmp slt i32 %41, 3, !dbg !1084
  br i1 %49, label %40, label %50, !dbg !1087, !llvm.loop !1098

50:                                               ; preds = %40, %23, %5, %16
  ret void, !dbg !1100
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define hidden signext range(i8 -127, 13) i8 @tile_color(i8 noundef signext %0) local_unnamed_addr #9 !dbg !1101 {
    #dbg_value(i8 %0, !1103, !DIExpression(), !1104)
  %2 = icmp slt i8 %0, 12, !dbg !1105
  %3 = add i8 %0, 1, !dbg !1105
  %4 = select i1 %2, i8 %3, i8 12, !dbg !1105
  ret i8 %4, !dbg !1106
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define hidden noundef signext range(i8 13, 15) i8 @text_color(i8 noundef signext %0) local_unnamed_addr #9 !dbg !1107 {
    #dbg_value(i8 %0, !1109, !DIExpression(), !1110)
  %2 = icmp slt i8 %0, 3, !dbg !1111
  %3 = select i1 %2, i8 13, i8 14, !dbg !1110
  ret i8 %3, !dbg !1113
}

; Function Attrs: nounwind
define hidden void @drawTile(i16 noundef signext %0, i16 noundef signext %1) local_unnamed_addr #0 !dbg !1114 {
    #dbg_value(i16 %0, !1118, !DIExpression(), !1125)
    #dbg_value(i16 %1, !1119, !DIExpression(), !1125)
    #dbg_value(i16 %0, !305, !DIExpression(), !1126)
    #dbg_value(i16 %1, !306, !DIExpression(), !1126)
  %3 = sext i16 %1 to i32, !dbg !1128
  %4 = shl nsw i32 %3, 2, !dbg !1129
  %5 = sext i16 %0 to i32, !dbg !1130
  %6 = add nsw i32 %4, %5, !dbg !1131
  %7 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %6, !dbg !1132
  %8 = load i8, ptr %7, align 1, !dbg !1132, !tbaa !91
    #dbg_value(i8 %8, !1120, !DIExpression(), !1125)
    #dbg_value(i8 %8, !1103, !DIExpression(), !1133)
  %9 = icmp slt i8 %8, 12, !dbg !1135
  %10 = add i8 %8, 1, !dbg !1135
  %11 = select i1 %9, i8 %10, i8 12, !dbg !1135
    #dbg_value(i8 %11, !1121, !DIExpression(), !1125)
  tail call void @fillTile(i16 noundef signext %0, i16 noundef signext %1, i8 noundef signext %11), !dbg !1136
  %12 = icmp eq i8 %8, 0, !dbg !1137
  br i1 %12, label %20, label %13, !dbg !1139

13:                                               ; preds = %2
    #dbg_value(i8 %8, !1109, !DIExpression(), !1140)
  %14 = icmp slt i8 %8, 3, !dbg !1142
  %15 = select i1 %14, i8 13, i8 14, !dbg !1140
    #dbg_value(i8 %15, !1122, !DIExpression(), !1125)
  %16 = shl i16 %0, 4, !dbg !1143
    #dbg_value(i16 %16, !1123, !DIExpression(), !1125)
  %17 = shl i16 %1, 4, !dbg !1144
    #dbg_value(i16 %17, !1124, !DIExpression(), !1125)
  %18 = or disjoint i16 %16, 7, !dbg !1145
  %19 = or disjoint i16 %17, 7, !dbg !1146
  tail call void @drawNumberInTile(i16 noundef signext %18, i16 noundef signext %19, i8 noundef signext %8, i8 noundef signext %15, i8 noundef signext %11), !dbg !1147
  br label %20, !dbg !1148

20:                                               ; preds = %2, %13
  ret void, !dbg !1148
}

; Function Attrs: nounwind
define hidden void @draw_board() local_unnamed_addr #0 !dbg !1149 {
    #dbg_value(i16 0, !1153, !DIExpression(), !1154)
    #dbg_value(i16 0, !1151, !DIExpression(), !1154)
  br label %1, !dbg !1155

1:                                                ; preds = %0, %38
  %2 = phi i32 [ 0, %0 ], [ %40, %38 ]
  %3 = phi i16 [ 0, %0 ], [ %39, %38 ]
    #dbg_value(i16 %3, !1153, !DIExpression(), !1154)
    #dbg_value(i32 %2, !1151, !DIExpression(), !1154)
    #dbg_value(i16 %3, !1153, !DIExpression(), !1154)
    #dbg_value(i16 0, !1152, !DIExpression(), !1154)
  %4 = shl nsw i32 %2, 2
  %5 = trunc nuw nsw i32 %2 to i16
  %6 = shl i16 %5, 4
  %7 = or disjoint i16 %6, 7
  br label %8, !dbg !1157

8:                                                ; preds = %1, %34
  %9 = phi i32 [ 0, %1 ], [ %36, %34 ]
  %10 = phi i16 [ %3, %1 ], [ %35, %34 ]
    #dbg_value(i16 %10, !1153, !DIExpression(), !1154)
    #dbg_value(i32 %9, !1152, !DIExpression(), !1154)
  %11 = load i8, ptr @needs_full_redraw, align 1, !dbg !1161, !tbaa !91
  %12 = icmp eq i8 %11, 0, !dbg !1161
  br i1 %12, label %13, label %20, !dbg !1165

13:                                               ; preds = %8
    #dbg_value(i16 %10, !809, !DIExpression(), !1166)
  %14 = sext i16 %10 to i32, !dbg !1168
  %15 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %14, !dbg !1168
  %16 = load i8, ptr %15, align 1, !dbg !1168, !tbaa !91
  %17 = getelementptr inbounds [16 x i8], ptr @tiles_prev, i32 0, i32 %14, !dbg !1169
  %18 = load i8, ptr %17, align 1, !dbg !1169, !tbaa !91
  %19 = icmp eq i8 %16, %18, !dbg !1170
  br i1 %19, label %34, label %20, !dbg !1171

20:                                               ; preds = %13, %8
    #dbg_value(i32 %9, !1118, !DIExpression(), !1172)
    #dbg_value(i32 %2, !1119, !DIExpression(), !1172)
    #dbg_value(i32 %9, !305, !DIExpression(), !1175)
    #dbg_value(i32 %2, !306, !DIExpression(), !1175)
  %21 = add nuw nsw i32 %4, %9, !dbg !1177
  %22 = getelementptr inbounds [16 x i8], ptr @tiles, i32 0, i32 %21, !dbg !1178
  %23 = load i8, ptr %22, align 1, !dbg !1178, !tbaa !91
    #dbg_value(i8 %23, !1120, !DIExpression(), !1172)
    #dbg_value(i8 %23, !1103, !DIExpression(), !1179)
  %24 = icmp slt i8 %23, 12, !dbg !1181
  %25 = add i8 %23, 1, !dbg !1181
  %26 = select i1 %24, i8 %25, i8 12, !dbg !1181
    #dbg_value(i8 %26, !1121, !DIExpression(), !1172)
  %27 = trunc nuw nsw i32 %9 to i16, !dbg !1182
  tail call void @fillTile(i16 noundef signext %27, i16 noundef signext %5, i8 noundef signext %26), !dbg !1182
  %28 = icmp eq i8 %23, 0, !dbg !1183
  br i1 %28, label %34, label %29, !dbg !1184

29:                                               ; preds = %20
    #dbg_value(i8 %23, !1109, !DIExpression(), !1185)
  %30 = icmp slt i8 %23, 3, !dbg !1187
  %31 = select i1 %30, i8 13, i8 14, !dbg !1185
    #dbg_value(i8 %31, !1122, !DIExpression(), !1172)
    #dbg_value(i32 %9, !1123, !DIExpression(DW_OP_constu, 4, DW_OP_shl, DW_OP_stack_value), !1172)
    #dbg_value(i32 %2, !1124, !DIExpression(DW_OP_constu, 4, DW_OP_shl, DW_OP_stack_value), !1172)
  %32 = shl i16 %27, 4, !dbg !1188
  %33 = or disjoint i16 %32, 7, !dbg !1188
  tail call void @drawNumberInTile(i16 noundef signext %33, i16 noundef signext %7, i8 noundef signext %23, i8 noundef signext %31, i8 noundef signext %26), !dbg !1188
  br label %34, !dbg !1189

34:                                               ; preds = %29, %20, %13
  %35 = add i16 %10, 1, !dbg !1190
    #dbg_value(i16 %35, !1153, !DIExpression(), !1154)
  %36 = add nuw nsw i32 %9, 1, !dbg !1191
    #dbg_value(i32 %36, !1152, !DIExpression(), !1154)
  %37 = icmp eq i32 %36, 4, !dbg !1192
  br i1 %37, label %38, label %8, !dbg !1157, !llvm.loop !1193

38:                                               ; preds = %34
  %39 = add nuw nsw i16 %3, 4, !dbg !1157
  %40 = add nuw nsw i32 %2, 1, !dbg !1195
    #dbg_value(i16 %39, !1153, !DIExpression(), !1154)
    #dbg_value(i32 %40, !1151, !DIExpression(), !1154)
  %41 = icmp eq i32 %40, 4, !dbg !1196
  br i1 %41, label %42, label %1, !dbg !1155, !llvm.loop !1197

42:                                               ; preds = %38
  ret void, !dbg !1199
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, argmem: write, inaccessiblemem: none)
define hidden void @drawScore(i16 noundef signext %0, i16 noundef signext %1, i16 noundef signext %2, i8 noundef signext %3, i8 noundef signext %4) local_unnamed_addr #10 !dbg !1200 {
    #dbg_value(i16 %0, !1202, !DIExpression(), !1212)
    #dbg_value(i16 %1, !1203, !DIExpression(), !1212)
    #dbg_value(i16 %2, !1204, !DIExpression(), !1212)
    #dbg_value(i8 %3, !1205, !DIExpression(), !1212)
    #dbg_value(i8 %4, !1206, !DIExpression(), !1212)
  %6 = icmp slt i16 %2, 1, !dbg !1213
  br i1 %6, label %7, label %10, !dbg !1215

7:                                                ; preds = %5
  %8 = add i16 %0, -1, !dbg !1216
  %9 = add i16 %1, -2, !dbg !1218
  tail call void @drawDigitFast(i16 noundef signext %8, i16 noundef signext %9, i16 noundef signext 0, i8 noundef signext %3, i8 noundef signext %4), !dbg !1219
  br label %43, !dbg !1220

10:                                               ; preds = %5, %10
  %11 = phi i32 [ %20, %10 ], [ 0, %5 ]
  %12 = phi i16 [ %19, %10 ], [ %2, %5 ]
    #dbg_value(i32 poison, !1207, !DIExpression(), !1212)
    #dbg_value(i16 %12, !1208, !DIExpression(), !1212)
  %13 = zext nneg i16 %12 to i32, !dbg !1221
  %14 = udiv i32 %13, 10, !dbg !1222
  %15 = mul nuw nsw i32 %14, 246, !dbg !1224
  %16 = add nuw nsw i32 %15, %13, !dbg !1225
  %17 = trunc i32 %16 to i8, !dbg !1226
  %18 = getelementptr inbounds [4 x i8], ptr @_score_digits, i32 0, i32 %11, !dbg !1227
  store i8 %17, ptr %18, align 1, !dbg !1228, !tbaa !91
  %19 = trunc nuw nsw i32 %14 to i16, !dbg !1229
    #dbg_value(i16 %19, !1208, !DIExpression(), !1212)
  %20 = add nuw nsw i32 %11, 1, !dbg !1230
    #dbg_value(i32 %20, !1207, !DIExpression(), !1212)
  %21 = icmp ugt i16 %12, 9, !dbg !1231
  %22 = icmp ult i32 %11, 3, !dbg !1232
  %23 = and i1 %21, %22, !dbg !1232
  br i1 %23, label %10, label %24, !dbg !1233, !llvm.loop !1234

24:                                               ; preds = %10
    #dbg_value(i32 %20, !1209, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_stack_value), !1212)
    #dbg_value(!DIArgList(i16 %0, i32 %20), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1212)
    #dbg_value(i32 %20, !1211, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 1, DW_OP_minus, DW_OP_stack_value), !1212)
  %25 = trunc nuw nsw i32 %11 to i16, !dbg !1236
  %26 = trunc nuw nsw i32 %20 to i16, !dbg !1236
    #dbg_value(!DIArgList(i16 %0, i16 %26), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1212)
    #dbg_value(i16 %26, !1209, !DIExpression(DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_stack_value), !1212)
    #dbg_value(i16 %26, !1211, !DIExpression(DW_OP_constu, 1, DW_OP_minus, DW_OP_stack_value), !1212)
  %27 = shl i16 %26, 2, !dbg !1239
    #dbg_value(!DIArgList(i16 %0, i16 %27), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1212)
    #dbg_value(i16 %27, !1209, !DIExpression(DW_OP_plus_uconst, 255, DW_OP_stack_value), !1212)
  %28 = add i16 %27, 255, !dbg !1240
    #dbg_value(!DIArgList(i16 %0, i16 %28), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1212)
  %29 = lshr i16 %28, 1, !dbg !1241
    #dbg_value(!DIArgList(i16 %0, i16 %29), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1212)
  %30 = and i16 %29, 127, !dbg !1241
    #dbg_value(!DIArgList(i16 %0, i16 %30), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !1212)
  %31 = sub i16 %0, %30, !dbg !1242
    #dbg_value(i16 %31, !1210, !DIExpression(), !1212)
  %32 = add i16 %1, -2
  br label %33, !dbg !1243

33:                                               ; preds = %24, %33
  %34 = phi i16 [ %25, %24 ], [ %41, %33 ]
  %35 = phi i16 [ %31, %24 ], [ %40, %33 ]
    #dbg_value(i16 %35, !1210, !DIExpression(), !1212)
  %36 = zext nneg i16 %34 to i32, !dbg !1244
  %37 = getelementptr inbounds [4 x i8], ptr @_score_digits, i32 0, i32 %36, !dbg !1245
  %38 = load i8, ptr %37, align 1, !dbg !1245, !tbaa !91
  %39 = sext i8 %38 to i16, !dbg !1245
  tail call void @drawDigitFast(i16 noundef signext %35, i16 noundef signext %32, i16 noundef signext %39, i8 noundef signext %3, i8 noundef signext %4), !dbg !1247
  %40 = add i16 %35, 4, !dbg !1248
    #dbg_value(i16 %40, !1210, !DIExpression(), !1212)
    #dbg_value(i16 %34, !1211, !DIExpression(DW_OP_constu, 1, DW_OP_minus, DW_OP_stack_value), !1212)
  %41 = add nsw i16 %34, -1, !dbg !1249
    #dbg_value(i16 %41, !1211, !DIExpression(), !1212)
  %42 = icmp sgt i16 %34, 0, !dbg !1236
  br i1 %42, label %33, label %43, !dbg !1243, !llvm.loop !1250

43:                                               ; preds = %33, %7
  ret void, !dbg !1252
}

; Function Attrs: nounwind
define hidden void @draw_game_over() local_unnamed_addr #0 !dbg !1253 {
    #dbg_value(i16 32, !1255, !DIExpression(), !1262)
    #dbg_value(i16 32, !1256, !DIExpression(), !1262)
    #dbg_value(i16 12, !206, !DIExpression(), !1263)
    #dbg_value(i16 24, !207, !DIExpression(), !1263)
    #dbg_value(i16 51, !208, !DIExpression(), !1263)
    #dbg_value(i16 39, !209, !DIExpression(), !1263)
    #dbg_value(i8 13, !210, !DIExpression(), !1263)
    #dbg_value(i16 12, !206, !DIExpression(), !1263)
    #dbg_value(i16 24, !207, !DIExpression(), !1263)
    #dbg_value(i16 51, !208, !DIExpression(), !1263)
    #dbg_value(i16 poison, !209, !DIExpression(), !1263)
    #dbg_value(i16 39, !209, !DIExpression(), !1263)
    #dbg_value(i8 -35, !217, !DIExpression(), !1263)
    #dbg_value(i16 24, !211, !DIExpression(), !1263)
  br label %1, !dbg !1265

1:                                                ; preds = %1, %0
  %2 = phi i16 [ 24, %0 ], [ %6, %1 ]
    #dbg_value(i16 %2, !211, !DIExpression(), !1263)
  %3 = shl i16 %2, 5, !dbg !1266
    #dbg_value(i16 %3, !213, !DIExpression(), !1263)
    #dbg_value(i16 12, !212, !DIExpression(), !1263)
    #dbg_value(i16 12, !212, !DIExpression(), !1263)
    #dbg_value(i32 20, !215, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1263)
    #dbg_value(i16 20, !215, !DIExpression(), !1263)
  %4 = or disjoint i16 %3, 6, !dbg !1267
    #dbg_value(i16 %4, !214, !DIExpression(), !1263)
  %5 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext %4, i16 noundef signext 20, i8 noundef signext -35) #14, !dbg !1268
    #dbg_value(i16 52, !212, !DIExpression(), !1263)
    #dbg_value(i16 52, !212, !DIExpression(), !1263)
    #dbg_value(i16 52, !76, !DIExpression(), !1269)
    #dbg_value(i16 %2, !77, !DIExpression(), !1269)
    #dbg_value(i8 13, !78, !DIExpression(), !1269)
  %6 = add nuw nsw i16 %2, 1, !dbg !1271
    #dbg_value(i16 %6, !211, !DIExpression(), !1263)
  %7 = icmp ult i16 %2, 39, !dbg !1272
  br i1 %7, label %1, label %8, !dbg !1265, !llvm.loop !1273

8:                                                ; preds = %1
    #dbg_value(i16 12, !1257, !DIExpression(), !1262)
    #dbg_value(i16 24, !1258, !DIExpression(), !1262)
    #dbg_value(i16 51, !1259, !DIExpression(), !1262)
    #dbg_value(i16 39, !1260, !DIExpression(), !1262)
    #dbg_value(i16 12, !138, !DIExpression(), !1275)
    #dbg_value(i16 51, !139, !DIExpression(), !1275)
    #dbg_value(i16 24, !140, !DIExpression(), !1275)
    #dbg_value(i8 14, !141, !DIExpression(), !1275)
    #dbg_value(i16 12, !138, !DIExpression(), !1275)
    #dbg_value(i16 51, !139, !DIExpression(), !1275)
    #dbg_value(i8 -18, !146, !DIExpression(), !1275)
    #dbg_value(i16 768, !143, !DIExpression(), !1275)
    #dbg_value(i16 12, !142, !DIExpression(), !1275)
    #dbg_value(i16 12, !142, !DIExpression(), !1275)
    #dbg_value(i32 20, !145, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1275)
    #dbg_value(i16 20, !145, !DIExpression(), !1275)
    #dbg_value(i16 774, !144, !DIExpression(), !1275)
  %9 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext 774, i16 noundef signext 20, i8 noundef signext -18) #14, !dbg !1277
    #dbg_value(i16 52, !142, !DIExpression(), !1275)
    #dbg_value(i16 52, !142, !DIExpression(), !1275)
    #dbg_value(i16 52, !76, !DIExpression(), !1278)
    #dbg_value(i16 24, !77, !DIExpression(), !1278)
    #dbg_value(i8 14, !78, !DIExpression(), !1278)
    #dbg_value(i16 12, !138, !DIExpression(), !1280)
    #dbg_value(i16 51, !139, !DIExpression(), !1280)
    #dbg_value(i16 39, !140, !DIExpression(), !1280)
    #dbg_value(i8 14, !141, !DIExpression(), !1280)
    #dbg_value(i16 12, !138, !DIExpression(), !1280)
    #dbg_value(i16 51, !139, !DIExpression(), !1280)
    #dbg_value(i8 -18, !146, !DIExpression(), !1280)
    #dbg_value(i16 1248, !143, !DIExpression(), !1280)
    #dbg_value(i16 12, !142, !DIExpression(), !1280)
    #dbg_value(i16 12, !142, !DIExpression(), !1280)
    #dbg_value(i32 20, !145, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1280)
    #dbg_value(i16 20, !145, !DIExpression(), !1280)
    #dbg_value(i16 1254, !144, !DIExpression(), !1280)
  %10 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext 1254, i16 noundef signext 20, i8 noundef signext -18) #14, !dbg !1282
    #dbg_value(i16 52, !142, !DIExpression(), !1280)
    #dbg_value(i16 52, !142, !DIExpression(), !1280)
    #dbg_value(i16 52, !76, !DIExpression(), !1283)
    #dbg_value(i16 39, !77, !DIExpression(), !1283)
    #dbg_value(i8 14, !78, !DIExpression(), !1283)
    #dbg_value(i16 24, !1261, !DIExpression(), !1262)
  br label %11, !dbg !1285

11:                                               ; preds = %8, %11
  %12 = phi i32 [ 24, %8 ], [ %24, %11 ]
    #dbg_value(i32 %12, !1261, !DIExpression(), !1262)
    #dbg_value(i16 12, !76, !DIExpression(), !1287)
    #dbg_value(i32 %12, !77, !DIExpression(), !1287)
    #dbg_value(i8 14, !78, !DIExpression(), !1287)
  %13 = shl nuw nsw i32 %12, 5, !dbg !1291
  %14 = or disjoint i32 %13, 6, !dbg !1292
    #dbg_value(i32 %14, !79, !DIExpression(), !1287)
  %15 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %14, !dbg !1293
  %16 = load i8, ptr %15, align 2, !dbg !1293, !tbaa !91
  %17 = and i8 %16, 15, !dbg !1294
  %18 = or disjoint i8 %17, -32, !dbg !1295
  store i8 %18, ptr %15, align 2, !dbg !1296, !tbaa !91
    #dbg_value(i16 51, !76, !DIExpression(), !1297)
    #dbg_value(i32 %12, !77, !DIExpression(), !1297)
    #dbg_value(i8 14, !78, !DIExpression(), !1297)
  %19 = or disjoint i32 %13, 25, !dbg !1299
    #dbg_value(i32 %19, !79, !DIExpression(), !1297)
  %20 = getelementptr inbounds [2048 x i8], ptr @framebuffer, i32 0, i32 %19, !dbg !1300
  %21 = load i8, ptr %20, align 1, !dbg !1300, !tbaa !91
  %22 = and i8 %21, -16, !dbg !1301
  %23 = or disjoint i8 %22, 14, !dbg !1302
  store i8 %23, ptr %20, align 1, !dbg !1303, !tbaa !91
  %24 = add nuw nsw i32 %12, 1, !dbg !1304
    #dbg_value(i32 %24, !1261, !DIExpression(), !1262)
  %25 = icmp eq i32 %24, 40, !dbg !1305
  br i1 %25, label %26, label %11, !dbg !1285, !llvm.loop !1306

26:                                               ; preds = %11
  %27 = load i16, ptr @score, align 2, !dbg !1308, !tbaa !294
    #dbg_value(i16 32, !1202, !DIExpression(), !1309)
    #dbg_value(i16 32, !1203, !DIExpression(), !1309)
    #dbg_value(i16 %27, !1204, !DIExpression(), !1309)
    #dbg_value(i8 14, !1205, !DIExpression(), !1309)
    #dbg_value(i8 13, !1206, !DIExpression(), !1309)
  %28 = icmp slt i16 %27, 1, !dbg !1311
  br i1 %28, label %29, label %30, !dbg !1312

29:                                               ; preds = %26
  tail call void @drawDigitFast(i16 noundef signext 31, i16 noundef signext 30, i16 noundef signext 0, i8 noundef signext 14, i8 noundef signext 13), !dbg !1313
  br label %60, !dbg !1314

30:                                               ; preds = %26, %30
  %31 = phi i32 [ %40, %30 ], [ 0, %26 ]
  %32 = phi i16 [ %39, %30 ], [ %27, %26 ]
    #dbg_value(i32 poison, !1207, !DIExpression(), !1309)
    #dbg_value(i16 %32, !1208, !DIExpression(), !1309)
  %33 = zext nneg i16 %32 to i32, !dbg !1315
  %34 = udiv i32 %33, 10, !dbg !1316
  %35 = mul nuw nsw i32 %34, 246, !dbg !1317
  %36 = add nuw nsw i32 %35, %33, !dbg !1318
  %37 = trunc i32 %36 to i8, !dbg !1319
  %38 = getelementptr inbounds [4 x i8], ptr @_score_digits, i32 0, i32 %31, !dbg !1320
  store i8 %37, ptr %38, align 1, !dbg !1321, !tbaa !91
  %39 = trunc nuw nsw i32 %34 to i16, !dbg !1322
    #dbg_value(i16 %39, !1208, !DIExpression(), !1309)
  %40 = add nuw nsw i32 %31, 1, !dbg !1323
    #dbg_value(i32 %40, !1207, !DIExpression(), !1309)
  %41 = icmp ugt i16 %32, 9, !dbg !1324
  %42 = icmp ult i32 %31, 3, !dbg !1325
  %43 = and i1 %42, %41, !dbg !1325
  br i1 %43, label %30, label %44, !dbg !1326, !llvm.loop !1327

44:                                               ; preds = %30
    #dbg_value(i32 %40, !1209, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_stack_value), !1309)
    #dbg_value(!DIArgList(i16 32, i32 %40), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1309)
    #dbg_value(i32 %40, !1211, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 1, DW_OP_minus, DW_OP_stack_value), !1309)
  %45 = trunc nuw nsw i32 %40 to i16, !dbg !1329
    #dbg_value(!DIArgList(i16 32, i16 %45), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1309)
    #dbg_value(i16 %45, !1209, !DIExpression(DW_OP_constu, 2, DW_OP_shl, DW_OP_plus_uconst, 255, DW_OP_stack_value), !1309)
    #dbg_value(i16 %45, !1211, !DIExpression(DW_OP_constu, 1, DW_OP_minus, DW_OP_stack_value), !1309)
  %46 = shl i16 %45, 2, !dbg !1330
    #dbg_value(!DIArgList(i16 32, i16 %46), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus_uconst, 255, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1309)
    #dbg_value(i16 %46, !1209, !DIExpression(DW_OP_plus_uconst, 255, DW_OP_stack_value), !1309)
  %47 = add i16 %46, 255, !dbg !1331
    #dbg_value(!DIArgList(i16 32, i16 %47), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 1, DW_OP_shr, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1309)
  %48 = lshr i16 %47, 1, !dbg !1332
    #dbg_value(!DIArgList(i16 32, i16 %48), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 127, DW_OP_and, DW_OP_minus, DW_OP_stack_value), !1309)
  %49 = and i16 %48, 127, !dbg !1332
    #dbg_value(!DIArgList(i16 32, i16 %49), !1210, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_minus, DW_OP_stack_value), !1309)
  %50 = sub nsw i16 32, %49, !dbg !1333
    #dbg_value(i16 %50, !1210, !DIExpression(), !1309)
  br label %51, !dbg !1334

51:                                               ; preds = %51, %44
  %52 = phi i32 [ %59, %51 ], [ %31, %44 ]
  %53 = phi i16 [ %57, %51 ], [ %50, %44 ]
    #dbg_value(i16 %53, !1210, !DIExpression(), !1309)
  %54 = getelementptr inbounds [4 x i8], ptr @_score_digits, i32 0, i32 %52, !dbg !1335
  %55 = load i8, ptr %54, align 1, !dbg !1335, !tbaa !91
  %56 = sext i8 %55 to i16, !dbg !1335
  tail call void @drawDigitFast(i16 noundef signext %53, i16 noundef signext 30, i16 noundef signext %56, i8 noundef signext 14, i8 noundef signext 13), !dbg !1336
  %57 = add nuw nsw i16 %53, 4, !dbg !1337
    #dbg_value(i16 %57, !1210, !DIExpression(), !1309)
    #dbg_value(i32 %52, !1211, !DIExpression(DW_OP_constu, 1, DW_OP_minus, DW_OP_stack_value), !1309)
    #dbg_value(i16 poison, !1211, !DIExpression(DW_OP_constu, 1, DW_OP_minus, DW_OP_stack_value), !1309)
  %58 = icmp sgt i32 %52, 0, !dbg !1329
  %59 = add nsw i32 %52, -1, !dbg !1338
  br i1 %58, label %51, label %60, !dbg !1334, !llvm.loop !1339

60:                                               ; preds = %51, %29
  ret void, !dbg !1341
}

; Function Attrs: nounwind
define hidden void @render_game() local_unnamed_addr #0 !dbg !1342 {
  tail call void @draw_board(), !dbg !1343
  %1 = load i8, ptr @game_over, align 1, !dbg !1344, !tbaa !91
  %2 = icmp eq i8 %1, 0, !dbg !1344
  br i1 %2, label %4, label %3, !dbg !1346

3:                                                ; preds = %0
  tail call void @draw_game_over(), !dbg !1347
  br label %4, !dbg !1349

4:                                                ; preds = %3, %0
    #dbg_value(i16 0, !817, !DIExpression(), !1350)
  tail call void @llvm.memcpy.p0.p0.i32(ptr noundef nonnull align 16 dereferenceable(16) @tiles_prev, ptr noundef nonnull align 16 dereferenceable(16) @tiles, i32 16, i1 false), !dbg !1352, !tbaa !91
    #dbg_value(i32 poison, !817, !DIExpression(), !1350)
  store i8 0, ptr @needs_full_redraw, align 1, !dbg !1353, !tbaa !91
  ret void, !dbg !1354
}

; Function Attrs: nounwind
define hidden void @process(ptr noundef %0, i16 noundef signext %1) local_unnamed_addr #0 !dbg !1355 {
    #dbg_value(ptr %0, !1361, !DIExpression(), !1368)
    #dbg_value(i16 %1, !1362, !DIExpression(), !1368)
  %3 = tail call ptr @jc_APDU_getBuffer(ptr noundef %0) #14, !dbg !1369
    #dbg_value(ptr %3, !1363, !DIExpression(), !1368)
  %4 = getelementptr inbounds i8, ptr %3, i32 1, !dbg !1370
  %5 = load i8, ptr %4, align 1, !dbg !1370, !tbaa !91
    #dbg_value(i8 %5, !1364, !DIExpression(), !1368)
  %6 = load i8, ptr @game_initialized, align 1, !dbg !1371, !tbaa !91
  %7 = icmp eq i8 %6, 0, !dbg !1371
  br i1 %7, label %8, label %9, !dbg !1373

8:                                                ; preds = %2
  tail call void @reset_game(), !dbg !1374
  store i8 1, ptr @game_initialized, align 1, !dbg !1376, !tbaa !91
  br label %9, !dbg !1377

9:                                                ; preds = %8, %2
  switch i8 %5, label %29 [
    i8 2, label %10
    i8 1, label %12
  ], !dbg !1378

10:                                               ; preds = %9
  tail call void @reset_game(), !dbg !1379
  %11 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #14, !dbg !1382
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 0) #14, !dbg !1382
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 0) #14, !dbg !1382
  br label %30, !dbg !1384

12:                                               ; preds = %9
  %13 = icmp sgt i16 %1, 0, !dbg !1385
  br i1 %13, label %14, label %17, !dbg !1386

14:                                               ; preds = %12
  %15 = getelementptr inbounds i8, ptr %3, i32 7, !dbg !1387
  %16 = load i8, ptr %15, align 1, !dbg !1387, !tbaa !91
  br label %17, !dbg !1386

17:                                               ; preds = %12, %14
  %18 = phi i8 [ %16, %14 ], [ 0, %12 ], !dbg !1386
    #dbg_value(i8 %18, !1365, !DIExpression(), !1388)
  tail call void @game_tick(i8 noundef signext %18), !dbg !1389
  %19 = load i8, ptr @needs_full_redraw, align 1, !dbg !1390, !tbaa !91
  %20 = icmp eq i8 %19, 0, !dbg !1390
  br i1 %20, label %23, label %21, !dbg !1392

21:                                               ; preds = %17
    #dbg_value(i8 0, !60, !DIExpression(), !1393)
    #dbg_value(i8 0, !61, !DIExpression(), !1393)
  %22 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @framebuffer, i16 noundef signext 0, i16 noundef signext 2048, i8 noundef signext 0) #14, !dbg !1396
  br label %23, !dbg !1397

23:                                               ; preds = %21, %17
  tail call void @draw_board(), !dbg !1398
  %24 = load i8, ptr @game_over, align 1, !dbg !1400, !tbaa !91
  %25 = icmp eq i8 %24, 0, !dbg !1400
  br i1 %25, label %27, label %26, !dbg !1401

26:                                               ; preds = %23
  tail call void @draw_game_over(), !dbg !1402
  br label %27, !dbg !1403

27:                                               ; preds = %23, %26
    #dbg_value(i16 0, !817, !DIExpression(), !1404)
  tail call void @llvm.memcpy.p0.p0.i32(ptr noundef nonnull align 16 dereferenceable(16) @tiles_prev, ptr noundef nonnull align 16 dereferenceable(16) @tiles, i32 16, i1 false), !dbg !1406, !tbaa !91
    #dbg_value(i32 poison, !817, !DIExpression(), !1404)
  store i8 0, ptr @needs_full_redraw, align 1, !dbg !1407, !tbaa !91
  %28 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #14, !dbg !1408
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2048) #14, !dbg !1409
  tail call void @jc_APDU_sendBytesLong(ptr noundef %0, ptr noundef nonnull @framebuffer, i16 noundef signext 0, i16 noundef signext 2048) #14, !dbg !1410
  br label %30

29:                                               ; preds = %9
  tail call void @jc_ISOException_throwIt(i16 noundef signext 27904) #14, !dbg !1411
  br label %30, !dbg !1412

30:                                               ; preds = %29, %27, %10
  ret void, !dbg !1412
}

declare !dbg !1413 ptr @jc_APDU_getBuffer(ptr noundef) local_unnamed_addr #1

declare !dbg !1416 signext i16 @jc_APDU_setOutgoing(ptr noundef) local_unnamed_addr #1

declare !dbg !1419 void @jc_APDU_setOutgoingLength(ptr noundef, i16 noundef signext) local_unnamed_addr #1

declare !dbg !1420 void @jc_APDU_sendBytes(ptr noundef, i16 noundef signext, i16 noundef signext) local_unnamed_addr #1

declare !dbg !1423 void @jc_APDU_sendBytesLong(ptr noundef, ptr noundef, i16 noundef signext, i16 noundef signext) local_unnamed_addr #1

declare !dbg !1426 void @jc_ISOException_throwIt(i16 noundef signext) local_unnamed_addr #1

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define hidden void @_jcsl_method_cap_fix() local_unnamed_addr #9 !dbg !1429 {
  ret void, !dbg !1430
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i16 @llvm.smax.i16(i16, i16) #11

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i16 @llvm.smin.i16(i16, i16) #11

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i32(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i32, i1 immarg) #12

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i32(ptr nocapture writeonly, i8, i32, i1 immarg) #13

attributes #0 = { nounwind "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #1 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #2 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #3 = { mustprogress nofree norecurse nosync nounwind willreturn memory(read, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #4 = { mustprogress nofree norecurse nosync nounwind willreturn memory(write, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #5 = { nofree norecurse nosync nounwind memory(read, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #6 = { nofree norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #7 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #8 = { nofree norecurse nosync nounwind memory(write, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #9 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #10 = { nofree norecurse nosync nounwind memory(readwrite, argmem: write, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #11 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #12 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #13 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #14 = { nounwind }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!51, !52, !53, !54}
!llvm.ident = !{!55}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "framebuffer", scope: !2, file: !47, line: 26, type: !48, isLocal: false, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C11, file: !3, producer: "Apple clang version 17.0.0 (clang-1700.6.3.2)", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !4, globals: !9, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "main.c", directory: "/home/user/jcc/examples/2048")
!4 = !{!5, !8}
!5 = !DIDerivedType(tag: DW_TAG_typedef, name: "byte", file: !6, line: 7, baseType: !7)
!6 = !DIFile(filename: "include/jcc.h", directory: "/home/user/jcc")
!7 = !DIBasicType(name: "signed char", size: 8, encoding: DW_ATE_signed_char)
!8 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!9 = !{!10, !17, !22, !0, !24, !30, !32, !34, !36, !38, !40, !45}
!10 = !DIGlobalVariableExpression(var: !11, expr: !DIExpression())
!11 = distinct !DIGlobalVariable(name: "DIGIT_FONT", scope: !2, file: !12, line: 9, type: !13, isLocal: false, isDefinition: true)
!12 = !DIFile(filename: "./graphics.h", directory: "/home/user/jcc/examples/2048")
!13 = !DICompositeType(tag: DW_TAG_array_type, baseType: !14, size: 400, elements: !15)
!14 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !5)
!15 = !{!16}
!16 = !DISubrange(count: 50)
!17 = !DIGlobalVariableExpression(var: !18, expr: !DIExpression())
!18 = distinct !DIGlobalVariable(name: "TILE_DIGITS", scope: !2, file: !12, line: 83, type: !19, isLocal: false, isDefinition: true)
!19 = !DICompositeType(tag: DW_TAG_array_type, baseType: !14, size: 480, elements: !20)
!20 = !{!21}
!21 = !DISubrange(count: 60)
!22 = !DIGlobalVariableExpression(var: !23, expr: !DIExpression())
!23 = distinct !DIGlobalVariable(name: "game_initialized", scope: !2, file: !3, line: 11, type: !5, isLocal: false, isDefinition: true)
!24 = !DIGlobalVariableExpression(var: !25, expr: !DIExpression())
!25 = distinct !DIGlobalVariable(name: "tiles", scope: !2, file: !26, line: 13, type: !27, isLocal: false, isDefinition: true)
!26 = !DIFile(filename: "./game.h", directory: "/home/user/jcc/examples/2048")
!27 = !DICompositeType(tag: DW_TAG_array_type, baseType: !5, size: 128, elements: !28)
!28 = !{!29}
!29 = !DISubrange(count: 16)
!30 = !DIGlobalVariableExpression(var: !31, expr: !DIExpression())
!31 = distinct !DIGlobalVariable(name: "tiles_prev", scope: !2, file: !26, line: 14, type: !27, isLocal: false, isDefinition: true)
!32 = !DIGlobalVariableExpression(var: !33, expr: !DIExpression())
!33 = distinct !DIGlobalVariable(name: "game_over", scope: !2, file: !26, line: 15, type: !5, isLocal: false, isDefinition: true)
!34 = !DIGlobalVariableExpression(var: !35, expr: !DIExpression())
!35 = distinct !DIGlobalVariable(name: "needs_full_redraw", scope: !2, file: !26, line: 16, type: !5, isLocal: false, isDefinition: true)
!36 = !DIGlobalVariableExpression(var: !37, expr: !DIExpression())
!37 = distinct !DIGlobalVariable(name: "score", scope: !2, file: !26, line: 17, type: !8, isLocal: false, isDefinition: true)
!38 = !DIGlobalVariableExpression(var: !39, expr: !DIExpression())
!39 = distinct !DIGlobalVariable(name: "rng_state", scope: !2, file: !26, line: 18, type: !8, isLocal: false, isDefinition: true)
!40 = !DIGlobalVariableExpression(var: !41, expr: !DIExpression())
!41 = distinct !DIGlobalVariable(name: "work", scope: !2, file: !26, line: 64, type: !42, isLocal: false, isDefinition: true)
!42 = !DICompositeType(tag: DW_TAG_array_type, baseType: !5, size: 32, elements: !43)
!43 = !{!44}
!44 = !DISubrange(count: 4)
!45 = !DIGlobalVariableExpression(var: !46, expr: !DIExpression())
!46 = distinct !DIGlobalVariable(name: "_score_digits", scope: !2, file: !12, line: 167, type: !42, isLocal: false, isDefinition: true)
!47 = !DIFile(filename: "./jcc_fb.h", directory: "/home/user/jcc/examples/2048")
!48 = !DICompositeType(tag: DW_TAG_array_type, baseType: !5, size: 16384, elements: !49)
!49 = !{!50}
!50 = !DISubrange(count: 2048)
!51 = !{i32 7, !"Dwarf Version", i32 4}
!52 = !{i32 2, !"Debug Info Version", i32 3}
!53 = !{i32 1, !"wchar_size", i32 4}
!54 = !{i32 7, !"debug-info-assignment-tracking", i1 true}
!55 = !{!"Apple clang version 17.0.0 (clang-1700.6.3.2)"}
!56 = distinct !DISubprogram(name: "clearFB", scope: !47, file: !47, line: 28, type: !57, scopeLine: 28, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !59)
!57 = !DISubroutineType(types: !58)
!58 = !{null, !5}
!59 = !{!60, !61}
!60 = !DILocalVariable(name: "color", arg: 1, scope: !56, file: !47, line: 28, type: !5)
!61 = !DILocalVariable(name: "fill", scope: !56, file: !47, line: 29, type: !5)
!62 = !DILocation(line: 0, scope: !56)
!63 = !DILocation(line: 29, column: 32, scope: !56)
!64 = !DILocation(line: 29, column: 40, scope: !56)
!65 = !DILocation(line: 29, column: 46, scope: !56)
!66 = !DILocation(line: 31, column: 5, scope: !56)
!67 = !DILocation(line: 32, column: 1, scope: !56)
!68 = !DISubprogram(name: "jc_Util_arrayFillNonAtomic", scope: !6, file: !6, line: 126, type: !69, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!69 = !DISubroutineType(types: !70)
!70 = !{!8, !71, !8, !8, !5}
!71 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !5, size: 32)
!72 = distinct !DISubprogram(name: "setPixel", scope: !47, file: !47, line: 34, type: !73, scopeLine: 34, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !75)
!73 = !DISubroutineType(types: !74)
!74 = !{null, !8, !8, !5}
!75 = !{!76, !77, !78, !79, !80, !81}
!76 = !DILocalVariable(name: "x", arg: 1, scope: !72, file: !47, line: 34, type: !8)
!77 = !DILocalVariable(name: "y", arg: 2, scope: !72, file: !47, line: 34, type: !8)
!78 = !DILocalVariable(name: "color", arg: 3, scope: !72, file: !47, line: 34, type: !5)
!79 = !DILocalVariable(name: "byteIdx", scope: !72, file: !47, line: 35, type: !8)
!80 = !DILocalVariable(name: "shift", scope: !72, file: !47, line: 36, type: !5)
!81 = !DILocalVariable(name: "mask", scope: !72, file: !47, line: 37, type: !5)
!82 = !DILocation(line: 0, scope: !72)
!83 = !DILocation(line: 39, column: 15, scope: !84)
!84 = distinct !DILexicalBlock(scope: !72, file: !47, line: 39, column: 9)
!85 = !DILocation(line: 43, column: 12, scope: !72)
!86 = !DILocation(line: 43, column: 23, scope: !72)
!87 = !DILocation(line: 43, column: 18, scope: !72)
!88 = !DILocation(line: 45, column: 11, scope: !89)
!89 = distinct !DILexicalBlock(scope: !72, file: !47, line: 45, column: 9)
!90 = !DILocation(line: 0, scope: !89)
!91 = !{!92, !92, i64 0}
!92 = !{!"omnipotent char", !93, i64 0}
!93 = !{!"Simple C/C++ TBAA"}
!94 = !DILocation(line: 45, column: 9, scope: !72)
!95 = !DILocation(line: 47, column: 51, scope: !96)
!96 = distinct !DILexicalBlock(scope: !89, file: !47, line: 45, column: 16)
!97 = !DILocation(line: 48, column: 27, scope: !96)
!98 = !DILocation(line: 47, column: 59, scope: !96)
!99 = !DILocation(line: 49, column: 5, scope: !96)
!100 = !DILocation(line: 51, column: 51, scope: !101)
!101 = distinct !DILexicalBlock(scope: !89, file: !47, line: 49, column: 12)
!102 = !DILocation(line: 52, column: 36, scope: !101)
!103 = !DILocation(line: 51, column: 59, scope: !101)
!104 = !DILocation(line: 54, column: 1, scope: !72)
!105 = distinct !DISubprogram(name: "fillTile", scope: !47, file: !47, line: 56, type: !73, scopeLine: 56, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !106)
!106 = !{!107, !108, !109, !110, !111}
!107 = !DILocalVariable(name: "col", arg: 1, scope: !105, file: !47, line: 56, type: !8)
!108 = !DILocalVariable(name: "row", arg: 2, scope: !105, file: !47, line: 56, type: !8)
!109 = !DILocalVariable(name: "color", arg: 3, scope: !105, file: !47, line: 56, type: !5)
!110 = !DILocalVariable(name: "baseOffset", scope: !105, file: !47, line: 57, type: !8)
!111 = !DILocalVariable(name: "fill", scope: !105, file: !47, line: 58, type: !5)
!112 = !DILocation(line: 0, scope: !105)
!113 = !DILocation(line: 57, column: 29, scope: !105)
!114 = !DILocation(line: 57, column: 42, scope: !105)
!115 = !DILocation(line: 57, column: 35, scope: !105)
!116 = !DILocation(line: 58, column: 32, scope: !105)
!117 = !DILocation(line: 58, column: 40, scope: !105)
!118 = !DILocation(line: 58, column: 46, scope: !105)
!119 = !DILocation(line: 61, column: 5, scope: !105)
!120 = !DILocation(line: 62, column: 5, scope: !105)
!121 = !DILocation(line: 63, column: 5, scope: !105)
!122 = !DILocation(line: 64, column: 5, scope: !105)
!123 = !DILocation(line: 65, column: 5, scope: !105)
!124 = !DILocation(line: 66, column: 5, scope: !105)
!125 = !DILocation(line: 67, column: 5, scope: !105)
!126 = !DILocation(line: 68, column: 5, scope: !105)
!127 = !DILocation(line: 69, column: 5, scope: !105)
!128 = !DILocation(line: 70, column: 5, scope: !105)
!129 = !DILocation(line: 71, column: 5, scope: !105)
!130 = !DILocation(line: 72, column: 5, scope: !105)
!131 = !DILocation(line: 73, column: 5, scope: !105)
!132 = !DILocation(line: 74, column: 5, scope: !105)
!133 = !DILocation(line: 75, column: 1, scope: !105)
!134 = distinct !DISubprogram(name: "hline", scope: !47, file: !47, line: 77, type: !135, scopeLine: 77, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !137)
!135 = !DISubroutineType(types: !136)
!136 = !{null, !8, !8, !8, !5}
!137 = !{!138, !139, !140, !141, !142, !143, !144, !145, !146}
!138 = !DILocalVariable(name: "x0", arg: 1, scope: !134, file: !47, line: 77, type: !8)
!139 = !DILocalVariable(name: "x1", arg: 2, scope: !134, file: !47, line: 77, type: !8)
!140 = !DILocalVariable(name: "y", arg: 3, scope: !134, file: !47, line: 77, type: !8)
!141 = !DILocalVariable(name: "color", arg: 4, scope: !134, file: !47, line: 77, type: !5)
!142 = !DILocalVariable(name: "x", scope: !134, file: !47, line: 78, type: !8)
!143 = !DILocalVariable(name: "rowBase", scope: !134, file: !47, line: 78, type: !8)
!144 = !DILocalVariable(name: "startByte", scope: !134, file: !47, line: 78, type: !8)
!145 = !DILocalVariable(name: "numBytes", scope: !134, file: !47, line: 78, type: !8)
!146 = !DILocalVariable(name: "fill", scope: !134, file: !47, line: 79, type: !5)
!147 = !DILocation(line: 0, scope: !134)
!148 = !DILocation(line: 81, column: 15, scope: !149)
!149 = distinct !DILexicalBlock(scope: !134, file: !47, line: 81, column: 9)
!150 = !DILocation(line: 83, column: 9, scope: !134)
!151 = !DILocation(line: 85, column: 9, scope: !134)
!152 = !DILocation(line: 87, column: 12, scope: !153)
!153 = distinct !DILexicalBlock(scope: !134, file: !47, line: 87, column: 9)
!154 = !DILocation(line: 87, column: 9, scope: !134)
!155 = !DILocation(line: 90, column: 27, scope: !134)
!156 = !DILocation(line: 90, column: 35, scope: !134)
!157 = !DILocation(line: 90, column: 41, scope: !134)
!158 = !DILocation(line: 91, column: 17, scope: !134)
!159 = !DILocation(line: 94, column: 11, scope: !160)
!160 = distinct !DILexicalBlock(scope: !134, file: !47, line: 94, column: 9)
!161 = !DILocation(line: 94, column: 9, scope: !134)
!162 = !DILocation(line: 0, scope: !72, inlinedAt: !163)
!163 = distinct !DILocation(line: 95, column: 9, scope: !164)
!164 = distinct !DILexicalBlock(scope: !160, file: !47, line: 94, column: 16)
!165 = !DILocation(line: 39, column: 15, scope: !84, inlinedAt: !163)
!166 = !DILocation(line: 43, column: 23, scope: !72, inlinedAt: !163)
!167 = !DILocation(line: 43, column: 18, scope: !72, inlinedAt: !163)
!168 = !DILocation(line: 47, column: 22, scope: !96, inlinedAt: !163)
!169 = !DILocation(line: 47, column: 51, scope: !96, inlinedAt: !163)
!170 = !DILocation(line: 47, column: 59, scope: !96, inlinedAt: !163)
!171 = !DILocation(line: 46, column: 30, scope: !96, inlinedAt: !163)
!172 = !DILocation(line: 49, column: 5, scope: !96, inlinedAt: !163)
!173 = !DILocation(line: 96, column: 10, scope: !164)
!174 = !DILocation(line: 97, column: 5, scope: !164)
!175 = !DILocation(line: 99, column: 22, scope: !134)
!176 = !DILocation(line: 99, column: 20, scope: !134)
!177 = !DILocation(line: 99, column: 24, scope: !134)
!178 = !DILocation(line: 99, column: 29, scope: !134)
!179 = !DILocation(line: 100, column: 9, scope: !180)
!180 = distinct !DILexicalBlock(scope: !134, file: !47, line: 100, column: 9)
!181 = !DILocation(line: 100, column: 18, scope: !180)
!182 = !DILocation(line: 100, column: 9, scope: !134)
!183 = !DILocation(line: 99, column: 16, scope: !134)
!184 = !DILocation(line: 101, column: 34, scope: !185)
!185 = distinct !DILexicalBlock(scope: !180, file: !47, line: 100, column: 23)
!186 = !DILocation(line: 101, column: 29, scope: !185)
!187 = !DILocation(line: 102, column: 9, scope: !185)
!188 = !DILocation(line: 103, column: 27, scope: !185)
!189 = !DILocation(line: 103, column: 13, scope: !185)
!190 = !DILocation(line: 104, column: 5, scope: !185)
!191 = !DILocation(line: 106, column: 11, scope: !192)
!192 = distinct !DILexicalBlock(scope: !134, file: !47, line: 106, column: 9)
!193 = !DILocation(line: 0, scope: !72, inlinedAt: !194)
!194 = distinct !DILocation(line: 107, column: 9, scope: !195)
!195 = distinct !DILexicalBlock(scope: !192, file: !47, line: 106, column: 18)
!196 = !DILocation(line: 106, column: 9, scope: !134)
!197 = !DILocation(line: 43, column: 23, scope: !72, inlinedAt: !194)
!198 = !DILocation(line: 43, column: 18, scope: !72, inlinedAt: !194)
!199 = !DILocation(line: 45, column: 11, scope: !89, inlinedAt: !194)
!200 = !DILocation(line: 0, scope: !89, inlinedAt: !194)
!201 = !DILocation(line: 109, column: 1, scope: !134)
!202 = distinct !DISubprogram(name: "fillRect", scope: !47, file: !47, line: 111, type: !203, scopeLine: 111, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !205)
!203 = !DISubroutineType(types: !204)
!204 = !{null, !8, !8, !8, !8, !5}
!205 = !{!206, !207, !208, !209, !210, !211, !212, !213, !214, !215, !216, !217}
!206 = !DILocalVariable(name: "x0", arg: 1, scope: !202, file: !47, line: 111, type: !8)
!207 = !DILocalVariable(name: "y0", arg: 2, scope: !202, file: !47, line: 111, type: !8)
!208 = !DILocalVariable(name: "x1", arg: 3, scope: !202, file: !47, line: 111, type: !8)
!209 = !DILocalVariable(name: "y1", arg: 4, scope: !202, file: !47, line: 111, type: !8)
!210 = !DILocalVariable(name: "color", arg: 5, scope: !202, file: !47, line: 111, type: !5)
!211 = !DILocalVariable(name: "y", scope: !202, file: !47, line: 112, type: !8)
!212 = !DILocalVariable(name: "x", scope: !202, file: !47, line: 112, type: !8)
!213 = !DILocalVariable(name: "rowBase", scope: !202, file: !47, line: 112, type: !8)
!214 = !DILocalVariable(name: "startByte", scope: !202, file: !47, line: 112, type: !8)
!215 = !DILocalVariable(name: "numBytes", scope: !202, file: !47, line: 112, type: !8)
!216 = !DILocalVariable(name: "totalBytes", scope: !202, file: !47, line: 112, type: !8)
!217 = !DILocalVariable(name: "fill", scope: !202, file: !47, line: 113, type: !5)
!218 = !DILocation(line: 0, scope: !202)
!219 = !DILocation(line: 115, column: 9, scope: !202)
!220 = !DILocation(line: 117, column: 9, scope: !202)
!221 = !DILocation(line: 119, column: 9, scope: !202)
!222 = !DILocation(line: 123, column: 12, scope: !223)
!223 = distinct !DILexicalBlock(scope: !202, file: !47, line: 123, column: 9)
!224 = !DILocation(line: 123, column: 17, scope: !223)
!225 = !DILocation(line: 121, column: 9, scope: !202)
!226 = !DILocation(line: 123, column: 23, scope: !223)
!227 = !DILocation(line: 123, column: 9, scope: !202)
!228 = !DILocation(line: 126, column: 27, scope: !202)
!229 = !DILocation(line: 126, column: 35, scope: !202)
!230 = !DILocation(line: 126, column: 41, scope: !202)
!231 = !DILocation(line: 129, column: 12, scope: !232)
!232 = distinct !DILexicalBlock(scope: !202, file: !47, line: 129, column: 9)
!233 = !DILocation(line: 129, column: 17, scope: !232)
!234 = !DILocation(line: 136, column: 5, scope: !235)
!235 = distinct !DILexicalBlock(scope: !202, file: !47, line: 136, column: 5)
!236 = !DILocation(line: 130, column: 24, scope: !237)
!237 = distinct !DILexicalBlock(scope: !232, file: !47, line: 129, column: 44)
!238 = !DILocation(line: 131, column: 26, scope: !237)
!239 = !DILocation(line: 131, column: 36, scope: !237)
!240 = !DILocation(line: 132, column: 9, scope: !237)
!241 = !DILocation(line: 133, column: 9, scope: !237)
!242 = !DILocation(line: 137, column: 21, scope: !243)
!243 = distinct !DILexicalBlock(scope: !244, file: !47, line: 136, column: 32)
!244 = distinct !DILexicalBlock(scope: !235, file: !47, line: 136, column: 5)
!245 = !DILocation(line: 140, column: 13, scope: !243)
!246 = !DILocation(line: 0, scope: !72, inlinedAt: !247)
!247 = distinct !DILocation(line: 141, column: 13, scope: !248)
!248 = distinct !DILexicalBlock(scope: !249, file: !47, line: 140, column: 20)
!249 = distinct !DILexicalBlock(scope: !243, file: !47, line: 140, column: 13)
!250 = !DILocation(line: 39, column: 15, scope: !84, inlinedAt: !247)
!251 = !DILocation(line: 43, column: 18, scope: !72, inlinedAt: !247)
!252 = !DILocation(line: 47, column: 22, scope: !96, inlinedAt: !247)
!253 = !DILocation(line: 47, column: 51, scope: !96, inlinedAt: !247)
!254 = !DILocation(line: 47, column: 59, scope: !96, inlinedAt: !247)
!255 = !DILocation(line: 46, column: 30, scope: !96, inlinedAt: !247)
!256 = !DILocation(line: 49, column: 5, scope: !96, inlinedAt: !247)
!257 = !DILocation(line: 0, scope: !243)
!258 = !DILocation(line: 145, column: 26, scope: !243)
!259 = !DILocation(line: 145, column: 28, scope: !243)
!260 = !DILocation(line: 145, column: 33, scope: !243)
!261 = !DILocation(line: 146, column: 13, scope: !262)
!262 = distinct !DILexicalBlock(scope: !243, file: !47, line: 146, column: 13)
!263 = !DILocation(line: 146, column: 22, scope: !262)
!264 = !DILocation(line: 146, column: 13, scope: !243)
!265 = !DILocation(line: 145, column: 20, scope: !243)
!266 = !DILocation(line: 147, column: 38, scope: !267)
!267 = distinct !DILexicalBlock(scope: !262, file: !47, line: 146, column: 27)
!268 = !DILocation(line: 147, column: 33, scope: !267)
!269 = !DILocation(line: 148, column: 13, scope: !267)
!270 = !DILocation(line: 149, column: 31, scope: !267)
!271 = !DILocation(line: 149, column: 17, scope: !267)
!272 = !DILocation(line: 150, column: 9, scope: !267)
!273 = !DILocation(line: 152, column: 15, scope: !274)
!274 = distinct !DILexicalBlock(scope: !243, file: !47, line: 152, column: 13)
!275 = !DILocation(line: 0, scope: !72, inlinedAt: !276)
!276 = distinct !DILocation(line: 153, column: 13, scope: !277)
!277 = distinct !DILexicalBlock(scope: !274, file: !47, line: 152, column: 22)
!278 = !DILocation(line: 152, column: 13, scope: !243)
!279 = !DILocation(line: 43, column: 23, scope: !72, inlinedAt: !276)
!280 = !DILocation(line: 43, column: 18, scope: !72, inlinedAt: !276)
!281 = !DILocation(line: 45, column: 11, scope: !89, inlinedAt: !276)
!282 = !DILocation(line: 0, scope: !89, inlinedAt: !276)
!283 = !DILocation(line: 136, column: 28, scope: !244)
!284 = !DILocation(line: 136, column: 20, scope: !244)
!285 = distinct !{!285, !234, !286, !287, !288}
!286 = !DILocation(line: 155, column: 5, scope: !235)
!287 = !{!"llvm.loop.mustprogress"}
!288 = !{!"llvm.loop.unroll.disable"}
!289 = !DILocation(line: 156, column: 1, scope: !202)
!290 = distinct !DISubprogram(name: "random_short", scope: !26, file: !26, line: 20, type: !291, scopeLine: 20, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!291 = !DISubroutineType(types: !292)
!292 = !{!8}
!293 = !DILocation(line: 21, column: 34, scope: !290)
!294 = !{!295, !295, i64 0}
!295 = !{!"short", !92, i64 0}
!296 = !DILocation(line: 21, column: 32, scope: !290)
!297 = !DILocation(line: 21, column: 44, scope: !290)
!298 = !DILocation(line: 21, column: 53, scope: !290)
!299 = !DILocation(line: 21, column: 15, scope: !290)
!300 = !DILocation(line: 22, column: 5, scope: !290)
!301 = distinct !DISubprogram(name: "get_tile", scope: !26, file: !26, line: 25, type: !302, scopeLine: 25, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !304)
!302 = !DISubroutineType(types: !303)
!303 = !{!5, !8, !8}
!304 = !{!305, !306}
!305 = !DILocalVariable(name: "col", arg: 1, scope: !301, file: !26, line: 25, type: !8)
!306 = !DILocalVariable(name: "row", arg: 2, scope: !301, file: !26, line: 25, type: !8)
!307 = !DILocation(line: 0, scope: !301)
!308 = !DILocation(line: 25, column: 53, scope: !301)
!309 = !DILocation(line: 25, column: 57, scope: !301)
!310 = !DILocation(line: 25, column: 65, scope: !301)
!311 = !DILocation(line: 25, column: 63, scope: !301)
!312 = !DILocation(line: 25, column: 46, scope: !301)
!313 = !DILocation(line: 25, column: 39, scope: !301)
!314 = distinct !DISubprogram(name: "set_tile", scope: !26, file: !26, line: 27, type: !73, scopeLine: 27, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !315)
!315 = !{!316, !317, !318}
!316 = !DILocalVariable(name: "col", arg: 1, scope: !314, file: !26, line: 27, type: !8)
!317 = !DILocalVariable(name: "row", arg: 2, scope: !314, file: !26, line: 27, type: !8)
!318 = !DILocalVariable(name: "val", arg: 3, scope: !314, file: !26, line: 27, type: !5)
!319 = !DILocation(line: 0, scope: !314)
!320 = !DILocation(line: 27, column: 56, scope: !314)
!321 = !DILocation(line: 27, column: 60, scope: !314)
!322 = !DILocation(line: 27, column: 68, scope: !314)
!323 = !DILocation(line: 27, column: 66, scope: !314)
!324 = !DILocation(line: 27, column: 49, scope: !314)
!325 = !DILocation(line: 27, column: 73, scope: !314)
!326 = !DILocation(line: 27, column: 80, scope: !314)
!327 = distinct !DISubprogram(name: "count_empty", scope: !26, file: !26, line: 29, type: !291, scopeLine: 29, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !328)
!328 = !{!329, !330}
!329 = !DILocalVariable(name: "i", scope: !327, file: !26, line: 30, type: !8)
!330 = !DILocalVariable(name: "count", scope: !327, file: !26, line: 31, type: !8)
!331 = !DILocation(line: 0, scope: !327)
!332 = !DILocation(line: 32, column: 5, scope: !333)
!333 = distinct !DILexicalBlock(scope: !327, file: !26, line: 32, column: 5)
!334 = !DILocation(line: 33, column: 13, scope: !335)
!335 = distinct !DILexicalBlock(scope: !336, file: !26, line: 33, column: 13)
!336 = distinct !DILexicalBlock(scope: !337, file: !26, line: 32, column: 37)
!337 = distinct !DILexicalBlock(scope: !333, file: !26, line: 32, column: 5)
!338 = !DILocation(line: 33, column: 22, scope: !335)
!339 = !DILocation(line: 33, column: 13, scope: !336)
!340 = !DILocation(line: 32, column: 33, scope: !337)
!341 = !DILocation(line: 32, column: 19, scope: !337)
!342 = distinct !{!342, !332, !343, !287, !288}
!343 = !DILocation(line: 35, column: 5, scope: !333)
!344 = !DILocation(line: 36, column: 5, scope: !327)
!345 = distinct !DISubprogram(name: "spawn_tile", scope: !26, file: !26, line: 39, type: !346, scopeLine: 39, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !348)
!346 = !DISubroutineType(types: !347)
!347 = !{null}
!348 = !{!349, !350, !351, !352, !353}
!349 = !DILocalVariable(name: "empty", scope: !345, file: !26, line: 40, type: !8)
!350 = !DILocalVariable(name: "idx", scope: !345, file: !26, line: 41, type: !8)
!351 = !DILocalVariable(name: "i", scope: !345, file: !26, line: 42, type: !8)
!352 = !DILocalVariable(name: "pos", scope: !345, file: !26, line: 43, type: !8)
!353 = !DILocalVariable(name: "val", scope: !345, file: !26, line: 44, type: !5)
!354 = !DILocation(line: 0, scope: !327, inlinedAt: !355)
!355 = distinct !DILocation(line: 40, column: 19, scope: !345)
!356 = !DILocation(line: 32, column: 5, scope: !333, inlinedAt: !355)
!357 = !DILocation(line: 33, column: 13, scope: !335, inlinedAt: !355)
!358 = !DILocation(line: 33, column: 22, scope: !335, inlinedAt: !355)
!359 = !DILocation(line: 33, column: 13, scope: !336, inlinedAt: !355)
!360 = !DILocation(line: 32, column: 33, scope: !337, inlinedAt: !355)
!361 = !DILocation(line: 32, column: 19, scope: !337, inlinedAt: !355)
!362 = distinct !{!362, !356, !363, !287, !288}
!363 = !DILocation(line: 35, column: 5, scope: !333, inlinedAt: !355)
!364 = !DILocation(line: 0, scope: !345)
!365 = !DILocation(line: 46, column: 15, scope: !366)
!366 = distinct !DILexicalBlock(scope: !345, file: !26, line: 46, column: 9)
!367 = !DILocation(line: 46, column: 9, scope: !345)
!368 = !DILocation(line: 46, column: 9, scope: !366)
!369 = !DILocation(line: 21, column: 34, scope: !290, inlinedAt: !370)
!370 = distinct !DILocation(line: 49, column: 11, scope: !345)
!371 = !DILocation(line: 21, column: 32, scope: !290, inlinedAt: !370)
!372 = !DILocation(line: 21, column: 44, scope: !290, inlinedAt: !370)
!373 = !DILocation(line: 21, column: 53, scope: !290, inlinedAt: !370)
!374 = !DILocation(line: 49, column: 11, scope: !345)
!375 = !DILocation(line: 49, column: 26, scope: !345)
!376 = !DILocation(line: 21, column: 32, scope: !290, inlinedAt: !377)
!377 = distinct !DILocation(line: 50, column: 12, scope: !345)
!378 = !DILocation(line: 21, column: 44, scope: !290, inlinedAt: !377)
!379 = !DILocation(line: 21, column: 53, scope: !290, inlinedAt: !377)
!380 = !DILocation(line: 21, column: 15, scope: !290, inlinedAt: !377)
!381 = !DILocation(line: 50, column: 27, scope: !345)
!382 = !DILocation(line: 50, column: 32, scope: !345)
!383 = !DILocation(line: 50, column: 11, scope: !345)
!384 = !DILocation(line: 53, column: 5, scope: !385)
!385 = distinct !DILexicalBlock(scope: !345, file: !26, line: 53, column: 5)
!386 = !DILocation(line: 54, column: 13, scope: !387)
!387 = distinct !DILexicalBlock(scope: !388, file: !26, line: 54, column: 13)
!388 = distinct !DILexicalBlock(scope: !389, file: !26, line: 53, column: 37)
!389 = distinct !DILexicalBlock(scope: !385, file: !26, line: 53, column: 5)
!390 = !DILocation(line: 54, column: 22, scope: !387)
!391 = !DILocation(line: 54, column: 13, scope: !388)
!392 = !DILocation(line: 55, column: 17, scope: !393)
!393 = distinct !DILexicalBlock(scope: !394, file: !26, line: 55, column: 17)
!394 = distinct !DILexicalBlock(scope: !387, file: !26, line: 54, column: 28)
!395 = !DILocation(line: 55, column: 21, scope: !393)
!396 = !DILocation(line: 55, column: 17, scope: !394)
!397 = !DILocation(line: 56, column: 26, scope: !398)
!398 = distinct !DILexicalBlock(scope: !393, file: !26, line: 55, column: 29)
!399 = !DILocation(line: 57, column: 17, scope: !398)
!400 = !DILocation(line: 59, column: 16, scope: !394)
!401 = !DILocation(line: 60, column: 9, scope: !394)
!402 = !DILocation(line: 53, column: 33, scope: !389)
!403 = !DILocation(line: 53, column: 19, scope: !389)
!404 = distinct !{!404, !384, !405, !287, !288}
!405 = !DILocation(line: 61, column: 5, scope: !385)
!406 = !DILocation(line: 62, column: 1, scope: !345)
!407 = distinct !DISubprogram(name: "slide_line", scope: !26, file: !26, line: 66, type: !408, scopeLine: 66, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !410)
!408 = !DISubroutineType(types: !409)
!409 = !{!5}
!410 = !{!411, !412, !413}
!411 = !DILocalVariable(name: "i", scope: !407, file: !26, line: 67, type: !8)
!412 = !DILocalVariable(name: "j", scope: !407, file: !26, line: 67, type: !8)
!413 = !DILocalVariable(name: "moved", scope: !407, file: !26, line: 68, type: !5)
!414 = !DILocation(line: 0, scope: !407)
!415 = !DILocation(line: 71, column: 5, scope: !416)
!416 = distinct !DILexicalBlock(scope: !407, file: !26, line: 71, column: 5)
!417 = !DILocation(line: 82, column: 5, scope: !418)
!418 = distinct !DILexicalBlock(scope: !407, file: !26, line: 82, column: 5)
!419 = !DILocation(line: 72, column: 13, scope: !420)
!420 = distinct !DILexicalBlock(scope: !421, file: !26, line: 72, column: 13)
!421 = distinct !DILexicalBlock(scope: !422, file: !26, line: 71, column: 29)
!422 = distinct !DILexicalBlock(scope: !416, file: !26, line: 71, column: 5)
!423 = !DILocation(line: 72, column: 21, scope: !420)
!424 = !DILocation(line: 72, column: 13, scope: !421)
!425 = !DILocation(line: 73, column: 19, scope: !426)
!426 = distinct !DILexicalBlock(scope: !427, file: !26, line: 73, column: 17)
!427 = distinct !DILexicalBlock(scope: !420, file: !26, line: 72, column: 27)
!428 = !DILocation(line: 73, column: 17, scope: !427)
!429 = !DILocation(line: 73, column: 17, scope: !426)
!430 = !DILocation(line: 74, column: 17, scope: !431)
!431 = distinct !DILexicalBlock(scope: !426, file: !26, line: 73, column: 25)
!432 = !DILocation(line: 74, column: 25, scope: !431)
!433 = !DILocation(line: 75, column: 25, scope: !431)
!434 = !DILocation(line: 77, column: 13, scope: !431)
!435 = !DILocation(line: 78, column: 14, scope: !427)
!436 = !DILocation(line: 79, column: 9, scope: !427)
!437 = !DILocation(line: 71, column: 25, scope: !422)
!438 = !DILocation(line: 71, column: 19, scope: !422)
!439 = distinct !{!439, !415, !440, !287, !288}
!440 = !DILocation(line: 80, column: 5, scope: !416)
!441 = !DILocation(line: 83, column: 13, scope: !442)
!442 = distinct !DILexicalBlock(scope: !443, file: !26, line: 83, column: 13)
!443 = distinct !DILexicalBlock(scope: !444, file: !26, line: 82, column: 29)
!444 = distinct !DILexicalBlock(scope: !418, file: !26, line: 82, column: 5)
!445 = !DILocation(line: 83, column: 21, scope: !442)
!446 = !DILocation(line: 83, column: 26, scope: !442)
!447 = !DILocation(line: 83, column: 47, scope: !442)
!448 = !DILocation(line: 83, column: 40, scope: !442)
!449 = !DILocation(line: 83, column: 37, scope: !442)
!450 = !DILocation(line: 83, column: 13, scope: !443)
!451 = !DILocation(line: 84, column: 31, scope: !452)
!452 = distinct !DILexicalBlock(scope: !442, file: !26, line: 83, column: 53)
!453 = !DILocation(line: 84, column: 21, scope: !452)
!454 = !DILocation(line: 85, column: 32, scope: !452)
!455 = !DILocation(line: 85, column: 21, scope: !452)
!456 = !DILocation(line: 85, column: 19, scope: !452)
!457 = !DILocation(line: 86, column: 25, scope: !452)
!458 = !DILocation(line: 88, column: 9, scope: !452)
!459 = !DILocation(line: 82, column: 25, scope: !444)
!460 = !DILocation(line: 82, column: 19, scope: !444)
!461 = distinct !{!461, !417, !462, !287, !288}
!462 = !DILocation(line: 89, column: 5, scope: !418)
!463 = !DILocation(line: 93, column: 13, scope: !464)
!464 = distinct !DILexicalBlock(scope: !465, file: !26, line: 93, column: 13)
!465 = distinct !DILexicalBlock(scope: !466, file: !26, line: 92, column: 29)
!466 = distinct !DILexicalBlock(scope: !467, file: !26, line: 92, column: 5)
!467 = distinct !DILexicalBlock(scope: !407, file: !26, line: 92, column: 5)
!468 = !DILocation(line: 93, column: 21, scope: !464)
!469 = !DILocation(line: 93, column: 13, scope: !465)
!470 = !DILocation(line: 94, column: 19, scope: !471)
!471 = distinct !DILexicalBlock(scope: !472, file: !26, line: 94, column: 17)
!472 = distinct !DILexicalBlock(scope: !464, file: !26, line: 93, column: 27)
!473 = !DILocation(line: 94, column: 17, scope: !472)
!474 = !DILocation(line: 94, column: 17, scope: !471)
!475 = !DILocation(line: 95, column: 17, scope: !476)
!476 = distinct !DILexicalBlock(scope: !471, file: !26, line: 94, column: 25)
!477 = !DILocation(line: 95, column: 25, scope: !476)
!478 = !DILocation(line: 96, column: 25, scope: !476)
!479 = !DILocation(line: 97, column: 13, scope: !476)
!480 = !DILocation(line: 98, column: 14, scope: !472)
!481 = !DILocation(line: 99, column: 9, scope: !472)
!482 = !DILocation(line: 92, column: 25, scope: !466)
!483 = !DILocation(line: 92, column: 19, scope: !466)
!484 = !DILocation(line: 92, column: 5, scope: !467)
!485 = distinct !{!485, !484, !486, !287, !288}
!486 = !DILocation(line: 100, column: 5, scope: !467)
!487 = !DILocation(line: 102, column: 5, scope: !407)
!488 = distinct !DISubprogram(name: "move_tiles", scope: !26, file: !26, line: 105, type: !489, scopeLine: 105, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !491)
!489 = !DISubroutineType(types: !490)
!490 = !{!5, !5}
!491 = !{!492, !493, !494, !495, !496}
!492 = !DILocalVariable(name: "dir", arg: 1, scope: !488, file: !26, line: 105, type: !5)
!493 = !DILocalVariable(name: "row", scope: !488, file: !26, line: 106, type: !8)
!494 = !DILocalVariable(name: "col", scope: !488, file: !26, line: 106, type: !8)
!495 = !DILocalVariable(name: "i", scope: !488, file: !26, line: 106, type: !8)
!496 = !DILocalVariable(name: "moved", scope: !488, file: !26, line: 107, type: !5)
!497 = !DILocation(line: 0, scope: !488)
!498 = !DILocation(line: 109, column: 13, scope: !499)
!499 = distinct !DILexicalBlock(scope: !488, file: !26, line: 109, column: 9)
!500 = !DILocation(line: 109, column: 9, scope: !488)
!501 = !DILocation(line: 112, column: 25, scope: !502)
!502 = distinct !DILexicalBlock(scope: !503, file: !26, line: 111, column: 13)
!503 = distinct !DILexicalBlock(scope: !504, file: !26, line: 111, column: 13)
!504 = distinct !DILexicalBlock(scope: !505, file: !26, line: 110, column: 39)
!505 = distinct !DILexicalBlock(scope: !506, file: !26, line: 110, column: 9)
!506 = distinct !DILexicalBlock(scope: !507, file: !26, line: 110, column: 9)
!507 = distinct !DILexicalBlock(scope: !499, file: !26, line: 109, column: 26)
!508 = !DILocation(line: 0, scope: !301, inlinedAt: !509)
!509 = distinct !DILocation(line: 112, column: 27, scope: !502)
!510 = !DILocation(line: 113, column: 17, scope: !511)
!511 = distinct !DILexicalBlock(scope: !504, file: !26, line: 113, column: 17)
!512 = !DILocation(line: 113, column: 17, scope: !504)
!513 = !DILocation(line: 27, column: 73, scope: !314, inlinedAt: !514)
!514 = distinct !DILocation(line: 116, column: 21, scope: !515)
!515 = distinct !DILexicalBlock(scope: !516, file: !26, line: 115, column: 17)
!516 = distinct !DILexicalBlock(scope: !517, file: !26, line: 115, column: 17)
!517 = distinct !DILexicalBlock(scope: !511, file: !26, line: 113, column: 31)
!518 = !DILocation(line: 0, scope: !314, inlinedAt: !514)
!519 = !DILocation(line: 110, column: 35, scope: !505)
!520 = !DILocation(line: 110, column: 9, scope: !506)
!521 = !DILocation(line: 110, column: 27, scope: !505)
!522 = distinct !{!522, !520, !523, !287, !288}
!523 = !DILocation(line: 118, column: 9, scope: !506)
!524 = !DILocation(line: 107, column: 10, scope: !488)
!525 = !DILocation(line: 121, column: 13, scope: !526)
!526 = distinct !DILexicalBlock(scope: !488, file: !26, line: 121, column: 9)
!527 = !DILocation(line: 121, column: 9, scope: !488)
!528 = !DILocation(line: 123, column: 13, scope: !529)
!529 = distinct !DILexicalBlock(scope: !530, file: !26, line: 123, column: 13)
!530 = distinct !DILexicalBlock(scope: !531, file: !26, line: 122, column: 39)
!531 = distinct !DILexicalBlock(scope: !532, file: !26, line: 122, column: 9)
!532 = distinct !DILexicalBlock(scope: !533, file: !26, line: 122, column: 9)
!533 = distinct !DILexicalBlock(scope: !526, file: !26, line: 121, column: 27)
!534 = !DILocation(line: 0, scope: !301, inlinedAt: !535)
!535 = distinct !DILocation(line: 124, column: 27, scope: !536)
!536 = distinct !DILexicalBlock(scope: !529, file: !26, line: 123, column: 13)
!537 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !535)
!538 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !535)
!539 = !DILocation(line: 124, column: 17, scope: !536)
!540 = !DILocation(line: 124, column: 25, scope: !536)
!541 = !DILocation(line: 123, column: 33, scope: !536)
!542 = !DILocation(line: 123, column: 27, scope: !536)
!543 = distinct !{!543, !528, !544, !287, !288}
!544 = !DILocation(line: 124, column: 46, scope: !529)
!545 = !DILocation(line: 125, column: 17, scope: !546)
!546 = distinct !DILexicalBlock(scope: !530, file: !26, line: 125, column: 17)
!547 = !DILocation(line: 125, column: 17, scope: !530)
!548 = !DILocation(line: 128, column: 42, scope: !549)
!549 = distinct !DILexicalBlock(scope: !550, file: !26, line: 127, column: 17)
!550 = distinct !DILexicalBlock(scope: !551, file: !26, line: 127, column: 17)
!551 = distinct !DILexicalBlock(scope: !546, file: !26, line: 125, column: 31)
!552 = !DILocation(line: 0, scope: !314, inlinedAt: !553)
!553 = distinct !DILocation(line: 128, column: 21, scope: !549)
!554 = !DILocation(line: 27, column: 66, scope: !314, inlinedAt: !553)
!555 = !DILocation(line: 27, column: 49, scope: !314, inlinedAt: !553)
!556 = !DILocation(line: 27, column: 73, scope: !314, inlinedAt: !553)
!557 = !DILocation(line: 127, column: 37, scope: !549)
!558 = !DILocation(line: 127, column: 31, scope: !549)
!559 = !DILocation(line: 127, column: 17, scope: !550)
!560 = distinct !{!560, !559, !561, !287, !288}
!561 = !DILocation(line: 128, column: 49, scope: !550)
!562 = !DILocation(line: 122, column: 35, scope: !531)
!563 = !DILocation(line: 122, column: 27, scope: !531)
!564 = !DILocation(line: 122, column: 9, scope: !532)
!565 = distinct !{!565, !564, !566, !287, !288}
!566 = !DILocation(line: 130, column: 9, scope: !532)
!567 = !DILocation(line: 133, column: 13, scope: !568)
!568 = distinct !DILexicalBlock(scope: !488, file: !26, line: 133, column: 9)
!569 = !DILocation(line: 133, column: 9, scope: !488)
!570 = !DILocation(line: 135, column: 13, scope: !571)
!571 = distinct !DILexicalBlock(scope: !572, file: !26, line: 135, column: 13)
!572 = distinct !DILexicalBlock(scope: !573, file: !26, line: 134, column: 39)
!573 = distinct !DILexicalBlock(scope: !574, file: !26, line: 134, column: 9)
!574 = distinct !DILexicalBlock(scope: !575, file: !26, line: 134, column: 9)
!575 = distinct !DILexicalBlock(scope: !568, file: !26, line: 133, column: 24)
!576 = !DILocation(line: 0, scope: !301, inlinedAt: !577)
!577 = distinct !DILocation(line: 136, column: 27, scope: !578)
!578 = distinct !DILexicalBlock(scope: !571, file: !26, line: 135, column: 13)
!579 = !DILocation(line: 25, column: 57, scope: !301, inlinedAt: !577)
!580 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !577)
!581 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !577)
!582 = !DILocation(line: 136, column: 17, scope: !578)
!583 = !DILocation(line: 136, column: 25, scope: !578)
!584 = !DILocation(line: 135, column: 33, scope: !578)
!585 = !DILocation(line: 135, column: 27, scope: !578)
!586 = distinct !{!586, !570, !587, !287, !288}
!587 = !DILocation(line: 136, column: 42, scope: !571)
!588 = !DILocation(line: 137, column: 17, scope: !589)
!589 = distinct !DILexicalBlock(scope: !572, file: !26, line: 137, column: 17)
!590 = !DILocation(line: 137, column: 17, scope: !572)
!591 = !DILocation(line: 140, column: 38, scope: !592)
!592 = distinct !DILexicalBlock(scope: !593, file: !26, line: 139, column: 17)
!593 = distinct !DILexicalBlock(scope: !594, file: !26, line: 139, column: 17)
!594 = distinct !DILexicalBlock(scope: !589, file: !26, line: 137, column: 31)
!595 = !DILocation(line: 0, scope: !314, inlinedAt: !596)
!596 = distinct !DILocation(line: 140, column: 21, scope: !592)
!597 = !DILocation(line: 27, column: 60, scope: !314, inlinedAt: !596)
!598 = !DILocation(line: 27, column: 66, scope: !314, inlinedAt: !596)
!599 = !DILocation(line: 27, column: 49, scope: !314, inlinedAt: !596)
!600 = !DILocation(line: 27, column: 73, scope: !314, inlinedAt: !596)
!601 = !DILocation(line: 139, column: 37, scope: !592)
!602 = !DILocation(line: 139, column: 31, scope: !592)
!603 = !DILocation(line: 139, column: 17, scope: !593)
!604 = distinct !{!604, !603, !605, !287, !288}
!605 = !DILocation(line: 140, column: 45, scope: !593)
!606 = !DILocation(line: 134, column: 35, scope: !573)
!607 = !DILocation(line: 134, column: 27, scope: !573)
!608 = !DILocation(line: 134, column: 9, scope: !574)
!609 = distinct !{!609, !608, !610, !287, !288}
!610 = !DILocation(line: 142, column: 9, scope: !574)
!611 = !DILocation(line: 145, column: 13, scope: !612)
!612 = distinct !DILexicalBlock(scope: !488, file: !26, line: 145, column: 9)
!613 = !DILocation(line: 145, column: 9, scope: !488)
!614 = !DILocation(line: 147, column: 13, scope: !615)
!615 = distinct !DILexicalBlock(scope: !616, file: !26, line: 147, column: 13)
!616 = distinct !DILexicalBlock(scope: !617, file: !26, line: 146, column: 39)
!617 = distinct !DILexicalBlock(scope: !618, file: !26, line: 146, column: 9)
!618 = distinct !DILexicalBlock(scope: !619, file: !26, line: 146, column: 9)
!619 = distinct !DILexicalBlock(scope: !612, file: !26, line: 145, column: 26)
!620 = !DILocation(line: 0, scope: !301, inlinedAt: !621)
!621 = distinct !DILocation(line: 148, column: 27, scope: !622)
!622 = distinct !DILexicalBlock(scope: !615, file: !26, line: 147, column: 13)
!623 = !DILocation(line: 25, column: 57, scope: !301, inlinedAt: !621)
!624 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !621)
!625 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !621)
!626 = !DILocation(line: 148, column: 17, scope: !622)
!627 = !DILocation(line: 148, column: 25, scope: !622)
!628 = !DILocation(line: 147, column: 33, scope: !622)
!629 = !DILocation(line: 147, column: 27, scope: !622)
!630 = distinct !{!630, !614, !631, !287, !288}
!631 = !DILocation(line: 148, column: 46, scope: !615)
!632 = !DILocation(line: 149, column: 17, scope: !633)
!633 = distinct !DILexicalBlock(scope: !616, file: !26, line: 149, column: 17)
!634 = !DILocation(line: 149, column: 17, scope: !616)
!635 = !DILocation(line: 152, column: 42, scope: !636)
!636 = distinct !DILexicalBlock(scope: !637, file: !26, line: 151, column: 17)
!637 = distinct !DILexicalBlock(scope: !638, file: !26, line: 151, column: 17)
!638 = distinct !DILexicalBlock(scope: !633, file: !26, line: 149, column: 31)
!639 = !DILocation(line: 0, scope: !314, inlinedAt: !640)
!640 = distinct !DILocation(line: 152, column: 21, scope: !636)
!641 = !DILocation(line: 27, column: 60, scope: !314, inlinedAt: !640)
!642 = !DILocation(line: 27, column: 66, scope: !314, inlinedAt: !640)
!643 = !DILocation(line: 27, column: 49, scope: !314, inlinedAt: !640)
!644 = !DILocation(line: 27, column: 73, scope: !314, inlinedAt: !640)
!645 = !DILocation(line: 151, column: 37, scope: !636)
!646 = !DILocation(line: 151, column: 31, scope: !636)
!647 = !DILocation(line: 151, column: 17, scope: !637)
!648 = distinct !{!648, !647, !649, !287, !288}
!649 = !DILocation(line: 152, column: 49, scope: !637)
!650 = !DILocation(line: 146, column: 35, scope: !617)
!651 = !DILocation(line: 146, column: 27, scope: !617)
!652 = !DILocation(line: 146, column: 9, scope: !618)
!653 = distinct !{!653, !652, !654, !287, !288}
!654 = !DILocation(line: 154, column: 9, scope: !618)
!655 = !DILocation(line: 157, column: 5, scope: !488)
!656 = distinct !DISubprogram(name: "can_move", scope: !26, file: !26, line: 160, type: !408, scopeLine: 160, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !657)
!657 = !{!658, !659, !660}
!658 = !DILocalVariable(name: "row", scope: !656, file: !26, line: 161, type: !8)
!659 = !DILocalVariable(name: "col", scope: !656, file: !26, line: 161, type: !8)
!660 = !DILocalVariable(name: "val", scope: !656, file: !26, line: 162, type: !5)
!661 = !DILocation(line: 0, scope: !327, inlinedAt: !662)
!662 = distinct !DILocation(line: 164, column: 9, scope: !663)
!663 = distinct !DILexicalBlock(scope: !656, file: !26, line: 164, column: 9)
!664 = !DILocation(line: 32, column: 5, scope: !333, inlinedAt: !662)
!665 = !DILocation(line: 33, column: 13, scope: !335, inlinedAt: !662)
!666 = !DILocation(line: 33, column: 22, scope: !335, inlinedAt: !662)
!667 = !DILocation(line: 33, column: 13, scope: !336, inlinedAt: !662)
!668 = !DILocation(line: 32, column: 33, scope: !337, inlinedAt: !662)
!669 = !DILocation(line: 32, column: 19, scope: !337, inlinedAt: !662)
!670 = distinct !{!670, !664, !671, !287, !288}
!671 = !DILocation(line: 35, column: 5, scope: !333, inlinedAt: !662)
!672 = !DILocation(line: 164, column: 23, scope: !663)
!673 = !DILocation(line: 164, column: 9, scope: !656)
!674 = !DILocation(line: 0, scope: !656)
!675 = !DILocation(line: 167, column: 31, scope: !676)
!676 = distinct !DILexicalBlock(scope: !677, file: !26, line: 167, column: 5)
!677 = distinct !DILexicalBlock(scope: !656, file: !26, line: 167, column: 5)
!678 = !DILocation(line: 168, column: 9, scope: !679)
!679 = distinct !DILexicalBlock(scope: !680, file: !26, line: 168, column: 9)
!680 = distinct !DILexicalBlock(scope: !676, file: !26, line: 167, column: 35)
!681 = !DILocation(line: 0, scope: !301, inlinedAt: !682)
!682 = distinct !DILocation(line: 169, column: 19, scope: !683)
!683 = distinct !DILexicalBlock(scope: !684, file: !26, line: 168, column: 39)
!684 = distinct !DILexicalBlock(scope: !679, file: !26, line: 168, column: 9)
!685 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !682)
!686 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !682)
!687 = !DILocation(line: 170, column: 21, scope: !688)
!688 = distinct !DILexicalBlock(scope: !683, file: !26, line: 170, column: 17)
!689 = !DILocation(line: 170, column: 25, scope: !688)
!690 = !DILocation(line: 170, column: 41, scope: !688)
!691 = !DILocation(line: 0, scope: !301, inlinedAt: !692)
!692 = distinct !DILocation(line: 170, column: 28, scope: !688)
!693 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !692)
!694 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !692)
!695 = !DILocation(line: 170, column: 51, scope: !688)
!696 = !DILocation(line: 170, column: 17, scope: !683)
!697 = !DILocation(line: 172, column: 25, scope: !698)
!698 = distinct !DILexicalBlock(scope: !683, file: !26, line: 172, column: 17)
!699 = !DILocation(line: 0, scope: !301, inlinedAt: !700)
!700 = distinct !DILocation(line: 172, column: 28, scope: !698)
!701 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !700)
!702 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !700)
!703 = !DILocation(line: 172, column: 51, scope: !698)
!704 = !DILocation(line: 172, column: 17, scope: !683)
!705 = !DILocation(line: 168, column: 35, scope: !684)
!706 = !DILocation(line: 168, column: 27, scope: !684)
!707 = distinct !{!707, !678, !708, !287, !288}
!708 = !DILocation(line: 174, column: 9, scope: !679)
!709 = !DILocation(line: 167, column: 23, scope: !676)
!710 = !DILocation(line: 167, column: 5, scope: !677)
!711 = distinct !{!711, !710, !712, !287, !288}
!712 = !DILocation(line: 175, column: 5, scope: !677)
!713 = !DILocation(line: 178, column: 1, scope: !656)
!714 = distinct !DISubprogram(name: "reset_game", scope: !26, file: !26, line: 180, type: !346, scopeLine: 180, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !715)
!715 = !{!716}
!716 = !DILocalVariable(name: "i", scope: !714, file: !26, line: 181, type: !8)
!717 = !DILocation(line: 0, scope: !714)
!718 = !DILocation(line: 184, column: 18, scope: !719)
!719 = distinct !DILexicalBlock(scope: !720, file: !26, line: 183, column: 37)
!720 = distinct !DILexicalBlock(scope: !721, file: !26, line: 183, column: 5)
!721 = distinct !DILexicalBlock(scope: !714, file: !26, line: 183, column: 5)
!722 = !DILocation(line: 185, column: 23, scope: !719)
!723 = !DILocation(line: 188, column: 15, scope: !714)
!724 = !DILocation(line: 189, column: 23, scope: !714)
!725 = !DILocation(line: 190, column: 11, scope: !714)
!726 = !DILocation(line: 191, column: 15, scope: !714)
!727 = !DILocation(line: 0, scope: !327, inlinedAt: !728)
!728 = distinct !DILocation(line: 40, column: 19, scope: !345, inlinedAt: !729)
!729 = distinct !DILocation(line: 193, column: 5, scope: !714)
!730 = !DILocation(line: 32, column: 5, scope: !333, inlinedAt: !728)
!731 = !DILocation(line: 33, column: 13, scope: !335, inlinedAt: !728)
!732 = !DILocation(line: 33, column: 22, scope: !335, inlinedAt: !728)
!733 = !DILocation(line: 33, column: 13, scope: !336, inlinedAt: !728)
!734 = !DILocation(line: 32, column: 33, scope: !337, inlinedAt: !728)
!735 = !DILocation(line: 32, column: 19, scope: !337, inlinedAt: !728)
!736 = distinct !{!736, !730, !737, !287, !288}
!737 = !DILocation(line: 35, column: 5, scope: !333, inlinedAt: !728)
!738 = !DILocation(line: 0, scope: !345, inlinedAt: !729)
!739 = !DILocation(line: 46, column: 15, scope: !366, inlinedAt: !729)
!740 = !DILocation(line: 46, column: 9, scope: !345, inlinedAt: !729)
!741 = !DILocation(line: 46, column: 9, scope: !366, inlinedAt: !729)
!742 = !DILocation(line: 49, column: 26, scope: !345, inlinedAt: !729)
!743 = !DILocation(line: 21, column: 15, scope: !290, inlinedAt: !744)
!744 = distinct !DILocation(line: 50, column: 12, scope: !345, inlinedAt: !729)
!745 = !DILocation(line: 53, column: 5, scope: !385, inlinedAt: !729)
!746 = !DILocation(line: 54, column: 13, scope: !387, inlinedAt: !729)
!747 = !DILocation(line: 54, column: 22, scope: !387, inlinedAt: !729)
!748 = !DILocation(line: 54, column: 13, scope: !388, inlinedAt: !729)
!749 = !DILocation(line: 55, column: 17, scope: !393, inlinedAt: !729)
!750 = !DILocation(line: 55, column: 21, scope: !393, inlinedAt: !729)
!751 = !DILocation(line: 55, column: 17, scope: !394, inlinedAt: !729)
!752 = !DILocation(line: 56, column: 26, scope: !398, inlinedAt: !729)
!753 = !DILocation(line: 57, column: 17, scope: !398, inlinedAt: !729)
!754 = !DILocation(line: 59, column: 16, scope: !394, inlinedAt: !729)
!755 = !DILocation(line: 60, column: 9, scope: !394, inlinedAt: !729)
!756 = !DILocation(line: 53, column: 33, scope: !389, inlinedAt: !729)
!757 = !DILocation(line: 53, column: 19, scope: !389, inlinedAt: !729)
!758 = distinct !{!758, !745, !759, !287, !288}
!759 = !DILocation(line: 61, column: 5, scope: !385, inlinedAt: !729)
!760 = !DILocation(line: 32, column: 5, scope: !333, inlinedAt: !761)
!761 = distinct !DILocation(line: 40, column: 19, scope: !345, inlinedAt: !762)
!762 = distinct !DILocation(line: 194, column: 5, scope: !714)
!763 = !DILocation(line: 0, scope: !327, inlinedAt: !761)
!764 = !DILocation(line: 33, column: 13, scope: !335, inlinedAt: !761)
!765 = !DILocation(line: 33, column: 22, scope: !335, inlinedAt: !761)
!766 = !DILocation(line: 33, column: 13, scope: !336, inlinedAt: !761)
!767 = !DILocation(line: 32, column: 33, scope: !337, inlinedAt: !761)
!768 = !DILocation(line: 32, column: 19, scope: !337, inlinedAt: !761)
!769 = distinct !{!769, !760, !770, !287, !288}
!770 = !DILocation(line: 35, column: 5, scope: !333, inlinedAt: !761)
!771 = !DILocation(line: 0, scope: !345, inlinedAt: !762)
!772 = !DILocation(line: 46, column: 15, scope: !366, inlinedAt: !762)
!773 = !DILocation(line: 46, column: 9, scope: !345, inlinedAt: !762)
!774 = !DILocation(line: 46, column: 9, scope: !366, inlinedAt: !762)
!775 = !DILocation(line: 21, column: 34, scope: !290, inlinedAt: !776)
!776 = distinct !DILocation(line: 49, column: 11, scope: !345, inlinedAt: !762)
!777 = !DILocation(line: 21, column: 32, scope: !290, inlinedAt: !776)
!778 = !DILocation(line: 21, column: 44, scope: !290, inlinedAt: !776)
!779 = !DILocation(line: 21, column: 53, scope: !290, inlinedAt: !776)
!780 = !DILocation(line: 49, column: 11, scope: !345, inlinedAt: !762)
!781 = !DILocation(line: 49, column: 26, scope: !345, inlinedAt: !762)
!782 = !DILocation(line: 21, column: 32, scope: !290, inlinedAt: !783)
!783 = distinct !DILocation(line: 50, column: 12, scope: !345, inlinedAt: !762)
!784 = !DILocation(line: 21, column: 44, scope: !290, inlinedAt: !783)
!785 = !DILocation(line: 21, column: 53, scope: !290, inlinedAt: !783)
!786 = !DILocation(line: 21, column: 15, scope: !290, inlinedAt: !783)
!787 = !DILocation(line: 50, column: 27, scope: !345, inlinedAt: !762)
!788 = !DILocation(line: 50, column: 32, scope: !345, inlinedAt: !762)
!789 = !DILocation(line: 50, column: 11, scope: !345, inlinedAt: !762)
!790 = !DILocation(line: 53, column: 5, scope: !385, inlinedAt: !762)
!791 = !DILocation(line: 54, column: 13, scope: !387, inlinedAt: !762)
!792 = !DILocation(line: 54, column: 22, scope: !387, inlinedAt: !762)
!793 = !DILocation(line: 54, column: 13, scope: !388, inlinedAt: !762)
!794 = !DILocation(line: 55, column: 17, scope: !393, inlinedAt: !762)
!795 = !DILocation(line: 55, column: 21, scope: !393, inlinedAt: !762)
!796 = !DILocation(line: 55, column: 17, scope: !394, inlinedAt: !762)
!797 = !DILocation(line: 56, column: 26, scope: !398, inlinedAt: !762)
!798 = !DILocation(line: 57, column: 17, scope: !398, inlinedAt: !762)
!799 = !DILocation(line: 59, column: 16, scope: !394, inlinedAt: !762)
!800 = !DILocation(line: 60, column: 9, scope: !394, inlinedAt: !762)
!801 = !DILocation(line: 53, column: 33, scope: !389, inlinedAt: !762)
!802 = !DILocation(line: 53, column: 19, scope: !389, inlinedAt: !762)
!803 = distinct !{!803, !790, !804, !287, !288}
!804 = !DILocation(line: 61, column: 5, scope: !385, inlinedAt: !762)
!805 = !DILocation(line: 195, column: 1, scope: !714)
!806 = distinct !DISubprogram(name: "tile_dirty", scope: !26, file: !26, line: 197, type: !807, scopeLine: 197, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !808)
!807 = !DISubroutineType(types: !4)
!808 = !{!809}
!809 = !DILocalVariable(name: "idx", arg: 1, scope: !806, file: !26, line: 197, type: !8)
!810 = !DILocation(line: 0, scope: !806)
!811 = !DILocation(line: 197, column: 37, scope: !806)
!812 = !DILocation(line: 197, column: 51, scope: !806)
!813 = !DILocation(line: 197, column: 48, scope: !806)
!814 = !DILocation(line: 197, column: 30, scope: !806)
!815 = distinct !DISubprogram(name: "mark_tiles_clean", scope: !26, file: !26, line: 199, type: !346, scopeLine: 199, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !816)
!816 = !{!817}
!817 = !DILocalVariable(name: "i", scope: !815, file: !26, line: 200, type: !8)
!818 = !DILocation(line: 0, scope: !815)
!819 = !DILocation(line: 202, column: 23, scope: !820)
!820 = distinct !DILexicalBlock(scope: !821, file: !26, line: 201, column: 37)
!821 = distinct !DILexicalBlock(scope: !822, file: !26, line: 201, column: 5)
!822 = distinct !DILexicalBlock(scope: !815, file: !26, line: 201, column: 5)
!823 = !DILocation(line: 204, column: 23, scope: !815)
!824 = !DILocation(line: 205, column: 1, scope: !815)
!825 = distinct !DISubprogram(name: "game_tick", scope: !26, file: !26, line: 207, type: !57, scopeLine: 207, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !826)
!826 = !{!827}
!827 = !DILocalVariable(name: "dir", arg: 1, scope: !825, file: !26, line: 207, type: !5)
!828 = !DILocation(line: 0, scope: !825)
!829 = !DILocation(line: 208, column: 9, scope: !830)
!830 = distinct !DILexicalBlock(scope: !825, file: !26, line: 208, column: 9)
!831 = !DILocation(line: 208, column: 9, scope: !825)
!832 = !DILocation(line: 209, column: 13, scope: !833)
!833 = distinct !DILexicalBlock(scope: !830, file: !26, line: 208, column: 20)
!834 = !DILocation(line: 210, column: 13, scope: !835)
!835 = distinct !DILexicalBlock(scope: !836, file: !26, line: 209, column: 30)
!836 = distinct !DILexicalBlock(scope: !833, file: !26, line: 209, column: 13)
!837 = !DILocation(line: 211, column: 9, scope: !835)
!838 = !DILocation(line: 215, column: 9, scope: !825)
!839 = !DILocation(line: 216, column: 13, scope: !840)
!840 = distinct !DILexicalBlock(scope: !841, file: !26, line: 216, column: 13)
!841 = distinct !DILexicalBlock(scope: !842, file: !26, line: 215, column: 26)
!842 = distinct !DILexicalBlock(scope: !825, file: !26, line: 215, column: 9)
!843 = !DILocation(line: 216, column: 13, scope: !841)
!844 = !DILocation(line: 0, scope: !327, inlinedAt: !845)
!845 = distinct !DILocation(line: 40, column: 19, scope: !345, inlinedAt: !846)
!846 = distinct !DILocation(line: 217, column: 13, scope: !847)
!847 = distinct !DILexicalBlock(scope: !840, file: !26, line: 216, column: 30)
!848 = !DILocation(line: 33, column: 13, scope: !335, inlinedAt: !845)
!849 = !DILocation(line: 33, column: 22, scope: !335, inlinedAt: !845)
!850 = !DILocation(line: 33, column: 13, scope: !336, inlinedAt: !845)
!851 = !DILocation(line: 32, column: 33, scope: !337, inlinedAt: !845)
!852 = !DILocation(line: 32, column: 19, scope: !337, inlinedAt: !845)
!853 = !DILocation(line: 32, column: 5, scope: !333, inlinedAt: !845)
!854 = distinct !{!854, !853, !855, !287, !288}
!855 = !DILocation(line: 35, column: 5, scope: !333, inlinedAt: !845)
!856 = !DILocation(line: 0, scope: !345, inlinedAt: !846)
!857 = !DILocation(line: 46, column: 15, scope: !366, inlinedAt: !846)
!858 = !DILocation(line: 46, column: 9, scope: !345, inlinedAt: !846)
!859 = !DILocation(line: 46, column: 9, scope: !366, inlinedAt: !846)
!860 = !DILocation(line: 21, column: 34, scope: !290, inlinedAt: !861)
!861 = distinct !DILocation(line: 49, column: 11, scope: !345, inlinedAt: !846)
!862 = !DILocation(line: 21, column: 32, scope: !290, inlinedAt: !861)
!863 = !DILocation(line: 21, column: 44, scope: !290, inlinedAt: !861)
!864 = !DILocation(line: 21, column: 53, scope: !290, inlinedAt: !861)
!865 = !DILocation(line: 49, column: 11, scope: !345, inlinedAt: !846)
!866 = !DILocation(line: 49, column: 26, scope: !345, inlinedAt: !846)
!867 = !DILocation(line: 21, column: 32, scope: !290, inlinedAt: !868)
!868 = distinct !DILocation(line: 50, column: 12, scope: !345, inlinedAt: !846)
!869 = !DILocation(line: 21, column: 44, scope: !290, inlinedAt: !868)
!870 = !DILocation(line: 21, column: 53, scope: !290, inlinedAt: !868)
!871 = !DILocation(line: 21, column: 15, scope: !290, inlinedAt: !868)
!872 = !DILocation(line: 50, column: 27, scope: !345, inlinedAt: !846)
!873 = !DILocation(line: 50, column: 32, scope: !345, inlinedAt: !846)
!874 = !DILocation(line: 50, column: 11, scope: !345, inlinedAt: !846)
!875 = !DILocation(line: 53, column: 5, scope: !385, inlinedAt: !846)
!876 = !DILocation(line: 54, column: 13, scope: !387, inlinedAt: !846)
!877 = !DILocation(line: 54, column: 22, scope: !387, inlinedAt: !846)
!878 = !DILocation(line: 54, column: 13, scope: !388, inlinedAt: !846)
!879 = !DILocation(line: 55, column: 17, scope: !393, inlinedAt: !846)
!880 = !DILocation(line: 55, column: 21, scope: !393, inlinedAt: !846)
!881 = !DILocation(line: 55, column: 17, scope: !394, inlinedAt: !846)
!882 = !DILocation(line: 56, column: 26, scope: !398, inlinedAt: !846)
!883 = !DILocation(line: 57, column: 17, scope: !398, inlinedAt: !846)
!884 = !DILocation(line: 59, column: 16, scope: !394, inlinedAt: !846)
!885 = !DILocation(line: 60, column: 9, scope: !394, inlinedAt: !846)
!886 = !DILocation(line: 53, column: 33, scope: !389, inlinedAt: !846)
!887 = !DILocation(line: 53, column: 19, scope: !389, inlinedAt: !846)
!888 = distinct !{!888, !875, !889, !287, !288}
!889 = !DILocation(line: 61, column: 5, scope: !385, inlinedAt: !846)
!890 = !DILocation(line: 32, column: 5, scope: !333, inlinedAt: !891)
!891 = distinct !DILocation(line: 164, column: 9, scope: !663, inlinedAt: !892)
!892 = distinct !DILocation(line: 218, column: 18, scope: !893)
!893 = distinct !DILexicalBlock(scope: !847, file: !26, line: 218, column: 17)
!894 = !DILocation(line: 0, scope: !327, inlinedAt: !891)
!895 = !DILocation(line: 33, column: 13, scope: !335, inlinedAt: !891)
!896 = !DILocation(line: 33, column: 22, scope: !335, inlinedAt: !891)
!897 = !DILocation(line: 33, column: 13, scope: !336, inlinedAt: !891)
!898 = !DILocation(line: 32, column: 33, scope: !337, inlinedAt: !891)
!899 = !DILocation(line: 32, column: 19, scope: !337, inlinedAt: !891)
!900 = distinct !{!900, !890, !901, !287, !288}
!901 = !DILocation(line: 35, column: 5, scope: !333, inlinedAt: !891)
!902 = !DILocation(line: 164, column: 23, scope: !663, inlinedAt: !892)
!903 = !DILocation(line: 164, column: 9, scope: !656, inlinedAt: !892)
!904 = !DILocation(line: 0, scope: !656, inlinedAt: !892)
!905 = !DILocation(line: 167, column: 31, scope: !676, inlinedAt: !892)
!906 = !DILocation(line: 168, column: 9, scope: !679, inlinedAt: !892)
!907 = !DILocation(line: 0, scope: !301, inlinedAt: !908)
!908 = distinct !DILocation(line: 169, column: 19, scope: !683, inlinedAt: !892)
!909 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !908)
!910 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !908)
!911 = !DILocation(line: 170, column: 21, scope: !688, inlinedAt: !892)
!912 = !DILocation(line: 170, column: 25, scope: !688, inlinedAt: !892)
!913 = !DILocation(line: 0, scope: !301, inlinedAt: !914)
!914 = distinct !DILocation(line: 170, column: 28, scope: !688, inlinedAt: !892)
!915 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !914)
!916 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !914)
!917 = !DILocation(line: 170, column: 51, scope: !688, inlinedAt: !892)
!918 = !DILocation(line: 170, column: 17, scope: !683, inlinedAt: !892)
!919 = !DILocation(line: 172, column: 25, scope: !698, inlinedAt: !892)
!920 = !DILocation(line: 0, scope: !301, inlinedAt: !921)
!921 = distinct !DILocation(line: 172, column: 28, scope: !698, inlinedAt: !892)
!922 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !921)
!923 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !921)
!924 = !DILocation(line: 172, column: 51, scope: !698, inlinedAt: !892)
!925 = !DILocation(line: 172, column: 17, scope: !683, inlinedAt: !892)
!926 = !DILocation(line: 168, column: 35, scope: !684, inlinedAt: !892)
!927 = !DILocation(line: 168, column: 27, scope: !684, inlinedAt: !892)
!928 = distinct !{!928, !906, !929, !287, !288}
!929 = !DILocation(line: 174, column: 9, scope: !679, inlinedAt: !892)
!930 = !DILocation(line: 167, column: 23, scope: !676, inlinedAt: !892)
!931 = !DILocation(line: 167, column: 5, scope: !677, inlinedAt: !892)
!932 = distinct !{!932, !931, !933, !287, !288}
!933 = !DILocation(line: 175, column: 5, scope: !677, inlinedAt: !892)
!934 = !DILocation(line: 219, column: 27, scope: !935)
!935 = distinct !DILexicalBlock(scope: !893, file: !26, line: 218, column: 30)
!936 = !DILocation(line: 220, column: 13, scope: !935)
!937 = !DILocation(line: 223, column: 1, scope: !825)
!938 = distinct !DISubprogram(name: "drawDigitFast", scope: !12, file: !12, line: 24, type: !939, scopeLine: 24, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !941)
!939 = !DISubroutineType(types: !940)
!940 = !{null, !8, !8, !8, !5, !5}
!941 = !{!942, !943, !944, !945, !946, !947, !948, !949, !950, !951, !952}
!942 = !DILocalVariable(name: "x", arg: 1, scope: !938, file: !12, line: 24, type: !8)
!943 = !DILocalVariable(name: "y", arg: 2, scope: !938, file: !12, line: 24, type: !8)
!944 = !DILocalVariable(name: "digit", arg: 3, scope: !938, file: !12, line: 24, type: !8)
!945 = !DILocalVariable(name: "fg", arg: 4, scope: !938, file: !12, line: 24, type: !5)
!946 = !DILocalVariable(name: "bg", arg: 5, scope: !938, file: !12, line: 24, type: !5)
!947 = !DILocalVariable(name: "bits", scope: !938, file: !12, line: 25, type: !5)
!948 = !DILocalVariable(name: "base_idx", scope: !938, file: !12, line: 26, type: !8)
!949 = !DILocalVariable(name: "byteIdx", scope: !938, file: !12, line: 27, type: !8)
!950 = !DILocalVariable(name: "p0", scope: !938, file: !12, line: 28, type: !5)
!951 = !DILocalVariable(name: "p1", scope: !938, file: !12, line: 28, type: !5)
!952 = !DILocalVariable(name: "p2", scope: !938, file: !12, line: 28, type: !5)
!953 = !DILocation(line: 0, scope: !938)
!954 = !DILocation(line: 30, column: 19, scope: !955)
!955 = distinct !DILexicalBlock(scope: !938, file: !12, line: 30, column: 9)
!956 = !DILocation(line: 32, column: 29, scope: !938)
!957 = !DILocation(line: 34, column: 12, scope: !938)
!958 = !DILocation(line: 34, column: 23, scope: !938)
!959 = !DILocation(line: 34, column: 18, scope: !938)
!960 = !DILocation(line: 36, column: 12, scope: !938)
!961 = !DILocation(line: 37, column: 11, scope: !938)
!962 = !DILocation(line: 37, column: 16, scope: !938)
!963 = !DILocation(line: 37, column: 10, scope: !938)
!964 = !DILocation(line: 38, column: 16, scope: !938)
!965 = !DILocation(line: 38, column: 10, scope: !938)
!966 = !DILocation(line: 39, column: 16, scope: !938)
!967 = !DILocation(line: 39, column: 10, scope: !938)
!968 = !DILocation(line: 40, column: 39, scope: !938)
!969 = !DILocation(line: 40, column: 45, scope: !938)
!970 = !DILocation(line: 40, column: 5, scope: !938)
!971 = !DILocation(line: 40, column: 26, scope: !938)
!972 = !DILocation(line: 42, column: 20, scope: !938)
!973 = !DILocation(line: 42, column: 26, scope: !938)
!974 = !DILocation(line: 41, column: 25, scope: !938)
!975 = !DILocation(line: 41, column: 5, scope: !938)
!976 = !DILocation(line: 41, column: 30, scope: !938)
!977 = !DILocation(line: 44, column: 32, scope: !938)
!978 = !DILocation(line: 44, column: 12, scope: !938)
!979 = !DILocation(line: 45, column: 11, scope: !938)
!980 = !DILocation(line: 45, column: 16, scope: !938)
!981 = !DILocation(line: 45, column: 10, scope: !938)
!982 = !DILocation(line: 46, column: 16, scope: !938)
!983 = !DILocation(line: 46, column: 10, scope: !938)
!984 = !DILocation(line: 47, column: 16, scope: !938)
!985 = !DILocation(line: 47, column: 10, scope: !938)
!986 = !DILocation(line: 49, column: 20, scope: !938)
!987 = !DILocation(line: 49, column: 26, scope: !938)
!988 = !DILocation(line: 48, column: 25, scope: !938)
!989 = !DILocation(line: 48, column: 5, scope: !938)
!990 = !DILocation(line: 48, column: 31, scope: !938)
!991 = !DILocation(line: 51, column: 20, scope: !938)
!992 = !DILocation(line: 51, column: 26, scope: !938)
!993 = !DILocation(line: 50, column: 25, scope: !938)
!994 = !DILocation(line: 50, column: 5, scope: !938)
!995 = !DILocation(line: 50, column: 31, scope: !938)
!996 = !DILocation(line: 53, column: 32, scope: !938)
!997 = !DILocation(line: 53, column: 12, scope: !938)
!998 = !DILocation(line: 54, column: 11, scope: !938)
!999 = !DILocation(line: 54, column: 16, scope: !938)
!1000 = !DILocation(line: 54, column: 10, scope: !938)
!1001 = !DILocation(line: 55, column: 16, scope: !938)
!1002 = !DILocation(line: 55, column: 10, scope: !938)
!1003 = !DILocation(line: 56, column: 16, scope: !938)
!1004 = !DILocation(line: 56, column: 10, scope: !938)
!1005 = !DILocation(line: 58, column: 20, scope: !938)
!1006 = !DILocation(line: 58, column: 26, scope: !938)
!1007 = !DILocation(line: 57, column: 25, scope: !938)
!1008 = !DILocation(line: 57, column: 5, scope: !938)
!1009 = !DILocation(line: 57, column: 31, scope: !938)
!1010 = !DILocation(line: 60, column: 20, scope: !938)
!1011 = !DILocation(line: 60, column: 26, scope: !938)
!1012 = !DILocation(line: 59, column: 25, scope: !938)
!1013 = !DILocation(line: 59, column: 5, scope: !938)
!1014 = !DILocation(line: 59, column: 31, scope: !938)
!1015 = !DILocation(line: 62, column: 32, scope: !938)
!1016 = !DILocation(line: 62, column: 12, scope: !938)
!1017 = !DILocation(line: 63, column: 11, scope: !938)
!1018 = !DILocation(line: 63, column: 16, scope: !938)
!1019 = !DILocation(line: 63, column: 10, scope: !938)
!1020 = !DILocation(line: 64, column: 16, scope: !938)
!1021 = !DILocation(line: 64, column: 10, scope: !938)
!1022 = !DILocation(line: 65, column: 16, scope: !938)
!1023 = !DILocation(line: 65, column: 10, scope: !938)
!1024 = !DILocation(line: 67, column: 20, scope: !938)
!1025 = !DILocation(line: 67, column: 26, scope: !938)
!1026 = !DILocation(line: 66, column: 25, scope: !938)
!1027 = !DILocation(line: 66, column: 5, scope: !938)
!1028 = !DILocation(line: 66, column: 31, scope: !938)
!1029 = !DILocation(line: 69, column: 20, scope: !938)
!1030 = !DILocation(line: 69, column: 26, scope: !938)
!1031 = !DILocation(line: 68, column: 25, scope: !938)
!1032 = !DILocation(line: 68, column: 5, scope: !938)
!1033 = !DILocation(line: 68, column: 31, scope: !938)
!1034 = !DILocation(line: 71, column: 32, scope: !938)
!1035 = !DILocation(line: 71, column: 12, scope: !938)
!1036 = !DILocation(line: 72, column: 11, scope: !938)
!1037 = !DILocation(line: 72, column: 16, scope: !938)
!1038 = !DILocation(line: 72, column: 10, scope: !938)
!1039 = !DILocation(line: 73, column: 16, scope: !938)
!1040 = !DILocation(line: 73, column: 10, scope: !938)
!1041 = !DILocation(line: 74, column: 16, scope: !938)
!1042 = !DILocation(line: 74, column: 10, scope: !938)
!1043 = !DILocation(line: 76, column: 20, scope: !938)
!1044 = !DILocation(line: 76, column: 26, scope: !938)
!1045 = !DILocation(line: 75, column: 25, scope: !938)
!1046 = !DILocation(line: 75, column: 5, scope: !938)
!1047 = !DILocation(line: 75, column: 32, scope: !938)
!1048 = !DILocation(line: 78, column: 20, scope: !938)
!1049 = !DILocation(line: 78, column: 26, scope: !938)
!1050 = !DILocation(line: 77, column: 25, scope: !938)
!1051 = !DILocation(line: 77, column: 5, scope: !938)
!1052 = !DILocation(line: 77, column: 32, scope: !938)
!1053 = !DILocation(line: 79, column: 1, scope: !938)
!1054 = distinct !DISubprogram(name: "drawNumberInTile", scope: !12, file: !12, line: 99, type: !1055, scopeLine: 99, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1057)
!1055 = !DISubroutineType(types: !1056)
!1056 = !{null, !8, !8, !5, !5, !5}
!1057 = !{!1058, !1059, !1060, !1061, !1062, !1063, !1064, !1065, !1066, !1067}
!1058 = !DILocalVariable(name: "cx", arg: 1, scope: !1054, file: !12, line: 99, type: !8)
!1059 = !DILocalVariable(name: "cy", arg: 2, scope: !1054, file: !12, line: 99, type: !8)
!1060 = !DILocalVariable(name: "power", arg: 3, scope: !1054, file: !12, line: 99, type: !5)
!1061 = !DILocalVariable(name: "fg", arg: 4, scope: !1054, file: !12, line: 99, type: !5)
!1062 = !DILocalVariable(name: "bg", arg: 5, scope: !1054, file: !12, line: 99, type: !5)
!1063 = !DILocalVariable(name: "base", scope: !1054, file: !12, line: 100, type: !8)
!1064 = !DILocalVariable(name: "num_digits", scope: !1054, file: !12, line: 100, type: !8)
!1065 = !DILocalVariable(name: "width", scope: !1054, file: !12, line: 100, type: !8)
!1066 = !DILocalVariable(name: "start_x", scope: !1054, file: !12, line: 100, type: !8)
!1067 = !DILocalVariable(name: "i", scope: !1054, file: !12, line: 100, type: !8)
!1068 = !DILocation(line: 0, scope: !1054)
!1069 = !DILocation(line: 102, column: 15, scope: !1070)
!1070 = distinct !DILexicalBlock(scope: !1054, file: !12, line: 102, column: 9)
!1071 = !DILocation(line: 102, column: 20, scope: !1070)
!1072 = !DILocation(line: 102, column: 9, scope: !1070)
!1073 = !DILocation(line: 105, column: 25, scope: !1054)
!1074 = !DILocation(line: 108, column: 20, scope: !1075)
!1075 = distinct !DILexicalBlock(scope: !1054, file: !12, line: 108, column: 9)
!1076 = !DILocation(line: 108, column: 9, scope: !1054)
!1077 = !DILocation(line: 109, column: 26, scope: !1078)
!1078 = distinct !DILexicalBlock(scope: !1075, file: !12, line: 108, column: 26)
!1079 = !DILocation(line: 109, column: 34, scope: !1078)
!1080 = !DILocation(line: 109, column: 56, scope: !1078)
!1081 = !DILocation(line: 109, column: 39, scope: !1078)
!1082 = !DILocation(line: 109, column: 9, scope: !1078)
!1083 = !DILocation(line: 110, column: 9, scope: !1078)
!1084 = !DILocation(line: 116, column: 32, scope: !1085)
!1085 = distinct !DILexicalBlock(scope: !1086, file: !12, line: 116, column: 5)
!1086 = distinct !DILexicalBlock(scope: !1054, file: !12, line: 116, column: 5)
!1087 = !DILocation(line: 116, column: 5, scope: !1086)
!1088 = !DILocation(line: 106, column: 18, scope: !1054)
!1089 = !DILocation(line: 108, column: 9, scope: !1075)
!1090 = !DILocation(line: 113, column: 13, scope: !1054)
!1091 = !DILocation(line: 114, column: 15, scope: !1054)
!1092 = !DILocation(line: 117, column: 61, scope: !1093)
!1093 = distinct !DILexicalBlock(scope: !1085, file: !12, line: 116, column: 42)
!1094 = !DILocation(line: 117, column: 40, scope: !1093)
!1095 = !DILocation(line: 117, column: 9, scope: !1093)
!1096 = !DILocation(line: 118, column: 27, scope: !1093)
!1097 = !DILocation(line: 116, column: 38, scope: !1085)
!1098 = distinct !{!1098, !1087, !1099, !287, !288}
!1099 = !DILocation(line: 119, column: 5, scope: !1086)
!1100 = !DILocation(line: 120, column: 1, scope: !1054)
!1101 = distinct !DISubprogram(name: "tile_color", scope: !12, file: !12, line: 122, type: !489, scopeLine: 122, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1102)
!1102 = !{!1103}
!1103 = !DILocalVariable(name: "power", arg: 1, scope: !1101, file: !12, line: 122, type: !5)
!1104 = !DILocation(line: 0, scope: !1101)
!1105 = !DILocation(line: 123, column: 9, scope: !1101)
!1106 = !DILocation(line: 128, column: 1, scope: !1101)
!1107 = distinct !DISubprogram(name: "text_color", scope: !12, file: !12, line: 130, type: !489, scopeLine: 130, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1108)
!1108 = !{!1109}
!1109 = !DILocalVariable(name: "power", arg: 1, scope: !1107, file: !12, line: 130, type: !5)
!1110 = !DILocation(line: 0, scope: !1107)
!1111 = !DILocation(line: 131, column: 15, scope: !1112)
!1112 = distinct !DILexicalBlock(scope: !1107, file: !12, line: 131, column: 9)
!1113 = !DILocation(line: 134, column: 1, scope: !1107)
!1114 = distinct !DISubprogram(name: "drawTile", scope: !12, file: !12, line: 136, type: !1115, scopeLine: 136, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1117)
!1115 = !DISubroutineType(types: !1116)
!1116 = !{null, !8, !8}
!1117 = !{!1118, !1119, !1120, !1121, !1122, !1123, !1124}
!1118 = !DILocalVariable(name: "col", arg: 1, scope: !1114, file: !12, line: 136, type: !8)
!1119 = !DILocalVariable(name: "row", arg: 2, scope: !1114, file: !12, line: 136, type: !8)
!1120 = !DILocalVariable(name: "power", scope: !1114, file: !12, line: 137, type: !5)
!1121 = !DILocalVariable(name: "bg", scope: !1114, file: !12, line: 138, type: !5)
!1122 = !DILocalVariable(name: "fg", scope: !1114, file: !12, line: 139, type: !5)
!1123 = !DILocalVariable(name: "x", scope: !1114, file: !12, line: 140, type: !8)
!1124 = !DILocalVariable(name: "y", scope: !1114, file: !12, line: 140, type: !8)
!1125 = !DILocation(line: 0, scope: !1114)
!1126 = !DILocation(line: 0, scope: !301, inlinedAt: !1127)
!1127 = distinct !DILocation(line: 137, column: 18, scope: !1114)
!1128 = !DILocation(line: 25, column: 53, scope: !301, inlinedAt: !1127)
!1129 = !DILocation(line: 25, column: 57, scope: !301, inlinedAt: !1127)
!1130 = !DILocation(line: 25, column: 65, scope: !301, inlinedAt: !1127)
!1131 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !1127)
!1132 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !1127)
!1133 = !DILocation(line: 0, scope: !1101, inlinedAt: !1134)
!1134 = distinct !DILocation(line: 138, column: 15, scope: !1114)
!1135 = !DILocation(line: 123, column: 9, scope: !1101, inlinedAt: !1134)
!1136 = !DILocation(line: 142, column: 5, scope: !1114)
!1137 = !DILocation(line: 144, column: 15, scope: !1138)
!1138 = distinct !DILexicalBlock(scope: !1114, file: !12, line: 144, column: 9)
!1139 = !DILocation(line: 144, column: 9, scope: !1114)
!1140 = !DILocation(line: 0, scope: !1107, inlinedAt: !1141)
!1141 = distinct !DILocation(line: 147, column: 10, scope: !1114)
!1142 = !DILocation(line: 131, column: 15, scope: !1112, inlinedAt: !1141)
!1143 = !DILocation(line: 148, column: 13, scope: !1114)
!1144 = !DILocation(line: 149, column: 13, scope: !1114)
!1145 = !DILocation(line: 150, column: 24, scope: !1114)
!1146 = !DILocation(line: 150, column: 31, scope: !1114)
!1147 = !DILocation(line: 150, column: 5, scope: !1114)
!1148 = !DILocation(line: 151, column: 1, scope: !1114)
!1149 = distinct !DISubprogram(name: "draw_board", scope: !12, file: !12, line: 153, type: !346, scopeLine: 153, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1150)
!1150 = !{!1151, !1152, !1153}
!1151 = !DILocalVariable(name: "row", scope: !1149, file: !12, line: 154, type: !8)
!1152 = !DILocalVariable(name: "col", scope: !1149, file: !12, line: 154, type: !8)
!1153 = !DILocalVariable(name: "idx", scope: !1149, file: !12, line: 154, type: !8)
!1154 = !DILocation(line: 0, scope: !1149)
!1155 = !DILocation(line: 156, column: 5, scope: !1156)
!1156 = distinct !DILexicalBlock(scope: !1149, file: !12, line: 156, column: 5)
!1157 = !DILocation(line: 157, column: 9, scope: !1158)
!1158 = distinct !DILexicalBlock(scope: !1159, file: !12, line: 157, column: 9)
!1159 = distinct !DILexicalBlock(scope: !1160, file: !12, line: 156, column: 35)
!1160 = distinct !DILexicalBlock(scope: !1156, file: !12, line: 156, column: 5)
!1161 = !DILocation(line: 158, column: 17, scope: !1162)
!1162 = distinct !DILexicalBlock(scope: !1163, file: !12, line: 158, column: 17)
!1163 = distinct !DILexicalBlock(scope: !1164, file: !12, line: 157, column: 39)
!1164 = distinct !DILexicalBlock(scope: !1158, file: !12, line: 157, column: 9)
!1165 = !DILocation(line: 158, column: 35, scope: !1162)
!1166 = !DILocation(line: 0, scope: !806, inlinedAt: !1167)
!1167 = distinct !DILocation(line: 158, column: 38, scope: !1162)
!1168 = !DILocation(line: 197, column: 37, scope: !806, inlinedAt: !1167)
!1169 = !DILocation(line: 197, column: 51, scope: !806, inlinedAt: !1167)
!1170 = !DILocation(line: 197, column: 48, scope: !806, inlinedAt: !1167)
!1171 = !DILocation(line: 158, column: 17, scope: !1163)
!1172 = !DILocation(line: 0, scope: !1114, inlinedAt: !1173)
!1173 = distinct !DILocation(line: 159, column: 17, scope: !1174)
!1174 = distinct !DILexicalBlock(scope: !1162, file: !12, line: 158, column: 55)
!1175 = !DILocation(line: 0, scope: !301, inlinedAt: !1176)
!1176 = distinct !DILocation(line: 137, column: 18, scope: !1114, inlinedAt: !1173)
!1177 = !DILocation(line: 25, column: 63, scope: !301, inlinedAt: !1176)
!1178 = !DILocation(line: 25, column: 46, scope: !301, inlinedAt: !1176)
!1179 = !DILocation(line: 0, scope: !1101, inlinedAt: !1180)
!1180 = distinct !DILocation(line: 138, column: 15, scope: !1114, inlinedAt: !1173)
!1181 = !DILocation(line: 123, column: 9, scope: !1101, inlinedAt: !1180)
!1182 = !DILocation(line: 142, column: 5, scope: !1114, inlinedAt: !1173)
!1183 = !DILocation(line: 144, column: 15, scope: !1138, inlinedAt: !1173)
!1184 = !DILocation(line: 144, column: 9, scope: !1114, inlinedAt: !1173)
!1185 = !DILocation(line: 0, scope: !1107, inlinedAt: !1186)
!1186 = distinct !DILocation(line: 147, column: 10, scope: !1114, inlinedAt: !1173)
!1187 = !DILocation(line: 131, column: 15, scope: !1112, inlinedAt: !1186)
!1188 = !DILocation(line: 150, column: 5, scope: !1114, inlinedAt: !1173)
!1189 = !DILocation(line: 151, column: 1, scope: !1114, inlinedAt: !1173)
!1190 = !DILocation(line: 161, column: 16, scope: !1163)
!1191 = !DILocation(line: 157, column: 35, scope: !1164)
!1192 = !DILocation(line: 157, column: 27, scope: !1164)
!1193 = distinct !{!1193, !1157, !1194, !287, !288}
!1194 = !DILocation(line: 162, column: 9, scope: !1158)
!1195 = !DILocation(line: 156, column: 31, scope: !1160)
!1196 = !DILocation(line: 156, column: 23, scope: !1160)
!1197 = distinct !{!1197, !1155, !1198, !287, !288}
!1198 = !DILocation(line: 163, column: 5, scope: !1156)
!1199 = !DILocation(line: 164, column: 1, scope: !1149)
!1200 = distinct !DISubprogram(name: "drawScore", scope: !12, file: !12, line: 169, type: !939, scopeLine: 169, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1201)
!1201 = !{!1202, !1203, !1204, !1205, !1206, !1207, !1208, !1209, !1210, !1211}
!1202 = !DILocalVariable(name: "cx", arg: 1, scope: !1200, file: !12, line: 169, type: !8)
!1203 = !DILocalVariable(name: "cy", arg: 2, scope: !1200, file: !12, line: 169, type: !8)
!1204 = !DILocalVariable(name: "value", arg: 3, scope: !1200, file: !12, line: 169, type: !8)
!1205 = !DILocalVariable(name: "fg", arg: 4, scope: !1200, file: !12, line: 169, type: !5)
!1206 = !DILocalVariable(name: "bg", arg: 5, scope: !1200, file: !12, line: 169, type: !5)
!1207 = !DILocalVariable(name: "num_digits", scope: !1200, file: !12, line: 170, type: !8)
!1208 = !DILocalVariable(name: "temp", scope: !1200, file: !12, line: 170, type: !8)
!1209 = !DILocalVariable(name: "width", scope: !1200, file: !12, line: 170, type: !8)
!1210 = !DILocalVariable(name: "start_x", scope: !1200, file: !12, line: 170, type: !8)
!1211 = !DILocalVariable(name: "i", scope: !1200, file: !12, line: 170, type: !8)
!1212 = !DILocation(line: 0, scope: !1200)
!1213 = !DILocation(line: 172, column: 15, scope: !1214)
!1214 = distinct !DILexicalBlock(scope: !1200, file: !12, line: 172, column: 9)
!1215 = !DILocation(line: 172, column: 9, scope: !1200)
!1216 = !DILocation(line: 173, column: 26, scope: !1217)
!1217 = distinct !DILexicalBlock(scope: !1214, file: !12, line: 172, column: 21)
!1218 = !DILocation(line: 173, column: 34, scope: !1217)
!1219 = !DILocation(line: 173, column: 9, scope: !1217)
!1220 = !DILocation(line: 174, column: 9, scope: !1217)
!1221 = !DILocation(line: 179, column: 12, scope: !1200)
!1222 = !DILocation(line: 181, column: 33, scope: !1223)
!1223 = distinct !DILexicalBlock(scope: !1200, file: !12, line: 179, column: 40)
!1224 = !DILocation(line: 181, column: 39, scope: !1223)
!1225 = !DILocation(line: 181, column: 25, scope: !1223)
!1226 = !DILocation(line: 181, column: 13, scope: !1223)
!1227 = !DILocation(line: 180, column: 9, scope: !1223)
!1228 = !DILocation(line: 180, column: 35, scope: !1223)
!1229 = !DILocation(line: 182, column: 16, scope: !1223)
!1230 = !DILocation(line: 183, column: 19, scope: !1223)
!1231 = !DILocation(line: 179, column: 17, scope: !1200)
!1232 = !DILocation(line: 179, column: 21, scope: !1200)
!1233 = !DILocation(line: 179, column: 5, scope: !1200)
!1234 = distinct !{!1234, !1233, !1235, !287, !288}
!1235 = !DILocation(line: 184, column: 5, scope: !1200)
!1236 = !DILocation(line: 189, column: 32, scope: !1237)
!1237 = distinct !DILexicalBlock(scope: !1238, file: !12, line: 189, column: 5)
!1238 = distinct !DILexicalBlock(scope: !1200, file: !12, line: 189, column: 5)
!1239 = !DILocation(line: 186, column: 25, scope: !1200)
!1240 = !DILocation(line: 186, column: 31, scope: !1200)
!1241 = !DILocation(line: 187, column: 36, scope: !1200)
!1242 = !DILocation(line: 187, column: 18, scope: !1200)
!1243 = !DILocation(line: 189, column: 5, scope: !1238)
!1244 = !DILocation(line: 189, column: 30, scope: !1237)
!1245 = !DILocation(line: 190, column: 40, scope: !1246)
!1246 = distinct !DILexicalBlock(scope: !1237, file: !12, line: 189, column: 43)
!1247 = !DILocation(line: 190, column: 9, scope: !1246)
!1248 = !DILocation(line: 191, column: 27, scope: !1246)
!1249 = !DILocation(line: 189, scope: !1238)
!1250 = distinct !{!1250, !1243, !1251, !287, !288}
!1251 = !DILocation(line: 192, column: 5, scope: !1238)
!1252 = !DILocation(line: 193, column: 1, scope: !1200)
!1253 = distinct !DISubprogram(name: "draw_game_over", scope: !12, file: !12, line: 195, type: !346, scopeLine: 195, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1254)
!1254 = !{!1255, !1256, !1257, !1258, !1259, !1260, !1261}
!1255 = !DILocalVariable(name: "cx", scope: !1253, file: !12, line: 196, type: !8)
!1256 = !DILocalVariable(name: "cy", scope: !1253, file: !12, line: 197, type: !8)
!1257 = !DILocalVariable(name: "x0", scope: !1253, file: !12, line: 198, type: !8)
!1258 = !DILocalVariable(name: "y0", scope: !1253, file: !12, line: 198, type: !8)
!1259 = !DILocalVariable(name: "x1", scope: !1253, file: !12, line: 198, type: !8)
!1260 = !DILocalVariable(name: "y1", scope: !1253, file: !12, line: 198, type: !8)
!1261 = !DILocalVariable(name: "y", scope: !1253, file: !12, line: 198, type: !8)
!1262 = !DILocation(line: 0, scope: !1253)
!1263 = !DILocation(line: 0, scope: !202, inlinedAt: !1264)
!1264 = distinct !DILocation(line: 200, column: 5, scope: !1253)
!1265 = !DILocation(line: 136, column: 5, scope: !235, inlinedAt: !1264)
!1266 = !DILocation(line: 137, column: 21, scope: !243, inlinedAt: !1264)
!1267 = !DILocation(line: 147, column: 33, scope: !267, inlinedAt: !1264)
!1268 = !DILocation(line: 148, column: 13, scope: !267, inlinedAt: !1264)
!1269 = !DILocation(line: 0, scope: !72, inlinedAt: !1270)
!1270 = distinct !DILocation(line: 153, column: 13, scope: !277, inlinedAt: !1264)
!1271 = !DILocation(line: 136, column: 28, scope: !244, inlinedAt: !1264)
!1272 = !DILocation(line: 136, column: 20, scope: !244, inlinedAt: !1264)
!1273 = distinct !{!1273, !1265, !1274, !287, !288}
!1274 = !DILocation(line: 155, column: 5, scope: !235, inlinedAt: !1264)
!1275 = !DILocation(line: 0, scope: !134, inlinedAt: !1276)
!1276 = distinct !DILocation(line: 206, column: 5, scope: !1253)
!1277 = !DILocation(line: 102, column: 9, scope: !185, inlinedAt: !1276)
!1278 = !DILocation(line: 0, scope: !72, inlinedAt: !1279)
!1279 = distinct !DILocation(line: 107, column: 9, scope: !195, inlinedAt: !1276)
!1280 = !DILocation(line: 0, scope: !134, inlinedAt: !1281)
!1281 = distinct !DILocation(line: 207, column: 5, scope: !1253)
!1282 = !DILocation(line: 102, column: 9, scope: !185, inlinedAt: !1281)
!1283 = !DILocation(line: 0, scope: !72, inlinedAt: !1284)
!1284 = distinct !DILocation(line: 107, column: 9, scope: !195, inlinedAt: !1281)
!1285 = !DILocation(line: 208, column: 5, scope: !1286)
!1286 = distinct !DILexicalBlock(scope: !1253, file: !12, line: 208, column: 5)
!1287 = !DILocation(line: 0, scope: !72, inlinedAt: !1288)
!1288 = distinct !DILocation(line: 209, column: 9, scope: !1289)
!1289 = distinct !DILexicalBlock(scope: !1290, file: !12, line: 208, column: 32)
!1290 = distinct !DILexicalBlock(scope: !1286, file: !12, line: 208, column: 5)
!1291 = !DILocation(line: 43, column: 12, scope: !72, inlinedAt: !1288)
!1292 = !DILocation(line: 43, column: 18, scope: !72, inlinedAt: !1288)
!1293 = !DILocation(line: 51, column: 22, scope: !101, inlinedAt: !1288)
!1294 = !DILocation(line: 51, column: 51, scope: !101, inlinedAt: !1288)
!1295 = !DILocation(line: 51, column: 59, scope: !101, inlinedAt: !1288)
!1296 = !DILocation(line: 50, column: 30, scope: !101, inlinedAt: !1288)
!1297 = !DILocation(line: 0, scope: !72, inlinedAt: !1298)
!1298 = distinct !DILocation(line: 210, column: 9, scope: !1289)
!1299 = !DILocation(line: 43, column: 18, scope: !72, inlinedAt: !1298)
!1300 = !DILocation(line: 47, column: 22, scope: !96, inlinedAt: !1298)
!1301 = !DILocation(line: 47, column: 51, scope: !96, inlinedAt: !1298)
!1302 = !DILocation(line: 47, column: 59, scope: !96, inlinedAt: !1298)
!1303 = !DILocation(line: 46, column: 30, scope: !96, inlinedAt: !1298)
!1304 = !DILocation(line: 208, column: 28, scope: !1290)
!1305 = !DILocation(line: 208, column: 20, scope: !1290)
!1306 = distinct !{!1306, !1285, !1307, !287, !288}
!1307 = !DILocation(line: 211, column: 5, scope: !1286)
!1308 = !DILocation(line: 213, column: 23, scope: !1253)
!1309 = !DILocation(line: 0, scope: !1200, inlinedAt: !1310)
!1310 = distinct !DILocation(line: 213, column: 5, scope: !1253)
!1311 = !DILocation(line: 172, column: 15, scope: !1214, inlinedAt: !1310)
!1312 = !DILocation(line: 172, column: 9, scope: !1200, inlinedAt: !1310)
!1313 = !DILocation(line: 173, column: 9, scope: !1217, inlinedAt: !1310)
!1314 = !DILocation(line: 174, column: 9, scope: !1217, inlinedAt: !1310)
!1315 = !DILocation(line: 179, column: 12, scope: !1200, inlinedAt: !1310)
!1316 = !DILocation(line: 181, column: 33, scope: !1223, inlinedAt: !1310)
!1317 = !DILocation(line: 181, column: 39, scope: !1223, inlinedAt: !1310)
!1318 = !DILocation(line: 181, column: 25, scope: !1223, inlinedAt: !1310)
!1319 = !DILocation(line: 181, column: 13, scope: !1223, inlinedAt: !1310)
!1320 = !DILocation(line: 180, column: 9, scope: !1223, inlinedAt: !1310)
!1321 = !DILocation(line: 180, column: 35, scope: !1223, inlinedAt: !1310)
!1322 = !DILocation(line: 182, column: 16, scope: !1223, inlinedAt: !1310)
!1323 = !DILocation(line: 183, column: 19, scope: !1223, inlinedAt: !1310)
!1324 = !DILocation(line: 179, column: 17, scope: !1200, inlinedAt: !1310)
!1325 = !DILocation(line: 179, column: 21, scope: !1200, inlinedAt: !1310)
!1326 = !DILocation(line: 179, column: 5, scope: !1200, inlinedAt: !1310)
!1327 = distinct !{!1327, !1326, !1328, !287, !288}
!1328 = !DILocation(line: 184, column: 5, scope: !1200, inlinedAt: !1310)
!1329 = !DILocation(line: 189, column: 32, scope: !1237, inlinedAt: !1310)
!1330 = !DILocation(line: 186, column: 25, scope: !1200, inlinedAt: !1310)
!1331 = !DILocation(line: 186, column: 31, scope: !1200, inlinedAt: !1310)
!1332 = !DILocation(line: 187, column: 36, scope: !1200, inlinedAt: !1310)
!1333 = !DILocation(line: 187, column: 18, scope: !1200, inlinedAt: !1310)
!1334 = !DILocation(line: 189, column: 5, scope: !1238, inlinedAt: !1310)
!1335 = !DILocation(line: 190, column: 40, scope: !1246, inlinedAt: !1310)
!1336 = !DILocation(line: 190, column: 9, scope: !1246, inlinedAt: !1310)
!1337 = !DILocation(line: 191, column: 27, scope: !1246, inlinedAt: !1310)
!1338 = !DILocation(line: 189, scope: !1238, inlinedAt: !1310)
!1339 = distinct !{!1339, !1334, !1340, !287, !288}
!1340 = !DILocation(line: 192, column: 5, scope: !1238, inlinedAt: !1310)
!1341 = !DILocation(line: 214, column: 1, scope: !1253)
!1342 = distinct !DISubprogram(name: "render_game", scope: !12, file: !12, line: 216, type: !346, scopeLine: 216, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!1343 = !DILocation(line: 217, column: 5, scope: !1342)
!1344 = !DILocation(line: 218, column: 9, scope: !1345)
!1345 = distinct !DILexicalBlock(scope: !1342, file: !12, line: 218, column: 9)
!1346 = !DILocation(line: 218, column: 9, scope: !1342)
!1347 = !DILocation(line: 219, column: 9, scope: !1348)
!1348 = distinct !DILexicalBlock(scope: !1345, file: !12, line: 218, column: 20)
!1349 = !DILocation(line: 220, column: 5, scope: !1348)
!1350 = !DILocation(line: 0, scope: !815, inlinedAt: !1351)
!1351 = distinct !DILocation(line: 221, column: 5, scope: !1342)
!1352 = !DILocation(line: 202, column: 23, scope: !820, inlinedAt: !1351)
!1353 = !DILocation(line: 204, column: 23, scope: !815, inlinedAt: !1351)
!1354 = !DILocation(line: 222, column: 1, scope: !1342)
!1355 = distinct !DISubprogram(name: "process", scope: !3, file: !3, line: 13, type: !1356, scopeLine: 13, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1360)
!1356 = !DISubroutineType(types: !1357)
!1357 = !{null, !1358, !8}
!1358 = !DIDerivedType(tag: DW_TAG_typedef, name: "APDU", file: !6, line: 11, baseType: !1359)
!1359 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 32)
!1360 = !{!1361, !1362, !1363, !1364, !1365}
!1361 = !DILocalVariable(name: "apdu", arg: 1, scope: !1355, file: !3, line: 13, type: !1358)
!1362 = !DILocalVariable(name: "apdu_len", arg: 2, scope: !1355, file: !3, line: 13, type: !8)
!1363 = !DILocalVariable(name: "buffer", scope: !1355, file: !3, line: 14, type: !71)
!1364 = !DILocalVariable(name: "ins", scope: !1355, file: !3, line: 15, type: !5)
!1365 = !DILocalVariable(name: "dir", scope: !1366, file: !3, line: 29, type: !5)
!1366 = distinct !DILexicalBlock(scope: !1367, file: !3, line: 28, column: 27)
!1367 = distinct !DILexicalBlock(scope: !1355, file: !3, line: 28, column: 9)
!1368 = !DILocation(line: 0, scope: !1355)
!1369 = !DILocation(line: 14, column: 20, scope: !1355)
!1370 = !DILocation(line: 15, column: 16, scope: !1355)
!1371 = !DILocation(line: 17, column: 10, scope: !1372)
!1372 = distinct !DILexicalBlock(scope: !1355, file: !3, line: 17, column: 9)
!1373 = !DILocation(line: 17, column: 9, scope: !1355)
!1374 = !DILocation(line: 18, column: 9, scope: !1375)
!1375 = distinct !DILexicalBlock(scope: !1372, file: !3, line: 17, column: 28)
!1376 = !DILocation(line: 19, column: 26, scope: !1375)
!1377 = !DILocation(line: 20, column: 5, scope: !1375)
!1378 = !DILocation(line: 22, column: 9, scope: !1355)
!1379 = !DILocation(line: 23, column: 9, scope: !1380)
!1380 = distinct !DILexicalBlock(scope: !1381, file: !3, line: 22, column: 27)
!1381 = distinct !DILexicalBlock(scope: !1355, file: !3, line: 22, column: 9)
!1382 = !DILocation(line: 24, column: 9, scope: !1383)
!1383 = distinct !DILexicalBlock(scope: !1380, file: !3, line: 24, column: 9)
!1384 = !DILocation(line: 25, column: 9, scope: !1380)
!1385 = !DILocation(line: 29, column: 30, scope: !1366)
!1386 = !DILocation(line: 29, column: 20, scope: !1366)
!1387 = !DILocation(line: 29, column: 38, scope: !1366)
!1388 = !DILocation(line: 0, scope: !1366)
!1389 = !DILocation(line: 31, column: 9, scope: !1366)
!1390 = !DILocation(line: 32, column: 13, scope: !1391)
!1391 = distinct !DILexicalBlock(scope: !1366, file: !3, line: 32, column: 13)
!1392 = !DILocation(line: 32, column: 13, scope: !1366)
!1393 = !DILocation(line: 0, scope: !56, inlinedAt: !1394)
!1394 = distinct !DILocation(line: 33, column: 13, scope: !1395)
!1395 = distinct !DILexicalBlock(scope: !1391, file: !3, line: 32, column: 32)
!1396 = !DILocation(line: 31, column: 5, scope: !56, inlinedAt: !1394)
!1397 = !DILocation(line: 34, column: 9, scope: !1395)
!1398 = !DILocation(line: 217, column: 5, scope: !1342, inlinedAt: !1399)
!1399 = distinct !DILocation(line: 35, column: 9, scope: !1366)
!1400 = !DILocation(line: 218, column: 9, scope: !1345, inlinedAt: !1399)
!1401 = !DILocation(line: 218, column: 9, scope: !1342, inlinedAt: !1399)
!1402 = !DILocation(line: 219, column: 9, scope: !1348, inlinedAt: !1399)
!1403 = !DILocation(line: 220, column: 5, scope: !1348, inlinedAt: !1399)
!1404 = !DILocation(line: 0, scope: !815, inlinedAt: !1405)
!1405 = distinct !DILocation(line: 221, column: 5, scope: !1342, inlinedAt: !1399)
!1406 = !DILocation(line: 202, column: 23, scope: !820, inlinedAt: !1405)
!1407 = !DILocation(line: 204, column: 23, scope: !815, inlinedAt: !1405)
!1408 = !DILocation(line: 37, column: 9, scope: !1366)
!1409 = !DILocation(line: 38, column: 9, scope: !1366)
!1410 = !DILocation(line: 39, column: 9, scope: !1366)
!1411 = !DILocation(line: 43, column: 5, scope: !1355)
!1412 = !DILocation(line: 44, column: 1, scope: !1355)
!1413 = !DISubprogram(name: "jc_APDU_getBuffer", scope: !6, file: !6, line: 94, type: !1414, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1414 = !DISubroutineType(types: !1415)
!1415 = !{!71, !1358}
!1416 = !DISubprogram(name: "jc_APDU_setOutgoing", scope: !6, file: !6, line: 96, type: !1417, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1417 = !DISubroutineType(types: !1418)
!1418 = !{!8, !1358}
!1419 = !DISubprogram(name: "jc_APDU_setOutgoingLength", scope: !6, file: !6, line: 97, type: !1356, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1420 = !DISubprogram(name: "jc_APDU_sendBytes", scope: !6, file: !6, line: 98, type: !1421, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1421 = !DISubroutineType(types: !1422)
!1422 = !{null, !1358, !8, !8}
!1423 = !DISubprogram(name: "jc_APDU_sendBytesLong", scope: !6, file: !6, line: 99, type: !1424, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1424 = !DISubroutineType(types: !1425)
!1425 = !{null, !1358, !71, !8, !8}
!1426 = !DISubprogram(name: "jc_ISOException_throwIt", scope: !6, file: !6, line: 120, type: !1427, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!1427 = !DISubroutineType(types: !1428)
!1428 = !{null, !8}
!1429 = distinct !DISubprogram(name: "_jcsl_method_cap_fix", scope: !3, file: !3, line: 47, type: !346, scopeLine: 47, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!1430 = !DILocation(line: 47, column: 34, scope: !1429)
