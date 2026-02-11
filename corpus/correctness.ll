; ModuleID = 'main.c'
source_filename = "main.c"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-n32:64-S128-ni:1:10:20"
target triple = "wasm32-unknown-unknown"

%struct.pool_obj_t = type { i16, i16, i8, i8 }
%struct.Item = type { i16, i8 }
%struct.point_s = type { i16, i16 }
%struct.pipe_s = type { i16, i16, i8, i8 }

@PALETTE = hidden local_unnamed_addr constant [3 x i8] c"\00\7F\FF", align 1, !dbg !0
@WAVE = hidden local_unnamed_addr constant [4 x i16] [i16 100, i16 200, i16 300, i16 400], align 2, !dbg !10
@LOOKUP = hidden local_unnamed_addr constant [2 x i32] [i32 100000, i32 200000], align 4, !dbg !16
@FONT_5x3 = hidden local_unnamed_addr constant [50 x i8] c"\07\05\05\05\07\02\06\02\02\07\07\01\07\04\07\07\01\07\01\07\05\05\07\01\01\07\04\07\01\07\07\04\07\05\07\07\01\01\01\01\07\05\07\05\07\07\05\07\01\07", align 16, !dbg !23
@shared_fb = hidden global [80 x i8] zeroinitializer, align 16, !dbg !36
@pool = hidden local_unnamed_addr global [4 x %struct.pool_obj_t] zeroinitializer, align 16, !dbg !62
@BIRD_SPRITE = hidden local_unnamed_addr constant [3 x i8] c"\07\07\07", align 1, !dbg !30
@g_byte = hidden local_unnamed_addr global i8 0, align 1, !dbg !41
@g_short = hidden local_unnamed_addr global i16 0, align 2, !dbg !48
@g_int = hidden local_unnamed_addr global i32 0, align 4, !dbg !53
@g_shorts = hidden local_unnamed_addr global [8 x i16] zeroinitializer, align 16, !dbg !43
@items = hidden local_unnamed_addr global [4 x %struct.Item] zeroinitializer, align 16, !dbg !55
@g_ints = hidden local_unnamed_addr global [4 x i32] zeroinitializer, align 16, !dbg !50
@g_pts = hidden local_unnamed_addr global [4 x %struct.point_s] zeroinitializer, align 16, !dbg !72
@g_pipes = hidden local_unnamed_addr global [3 x %struct.pipe_s] zeroinitializer, align 16, !dbg !79
@g_rng_seed = hidden local_unnamed_addr global i16 0, align 2, !dbg !88
@g_state = hidden local_unnamed_addr global i16 0, align 2, !dbg !90
@g_frame = hidden local_unnamed_addr global i16 0, align 2, !dbg !92

; Function Attrs: nounwind
define hidden void @sendResult(ptr noundef %0, ptr nocapture noundef writeonly %1, i16 noundef signext %2) local_unnamed_addr #0 !dbg !99 {
    #dbg_value(ptr %0, !106, !DIExpression(), !109)
    #dbg_value(ptr %1, !107, !DIExpression(), !109)
    #dbg_value(i16 %2, !108, !DIExpression(), !109)
  %4 = lshr i16 %2, 8, !dbg !110
  %5 = trunc nuw i16 %4 to i8, !dbg !111
  store i8 %5, ptr %1, align 1, !dbg !112, !tbaa !113
  %6 = trunc i16 %2 to i8, !dbg !116
  %7 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !117
  store i8 %6, ptr %7, align 1, !dbg !118, !tbaa !113
  %8 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !119
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !120
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !121
  ret void, !dbg !122
}

declare !dbg !123 signext i16 @jc_APDU_setOutgoing(ptr noundef) local_unnamed_addr #1

declare !dbg !126 void @jc_APDU_setOutgoingLength(ptr noundef, i16 noundef signext) local_unnamed_addr #1

declare !dbg !129 void @jc_APDU_sendBytes(ptr noundef, i16 noundef signext, i16 noundef signext) local_unnamed_addr #1

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define hidden noundef signext i16 @add_shorts(i16 noundef signext %0, i16 noundef signext %1) local_unnamed_addr #2 !dbg !132 {
    #dbg_value(i16 %0, !136, !DIExpression(), !138)
    #dbg_value(i16 %1, !137, !DIExpression(), !138)
  %3 = add i16 %1, %0, !dbg !139
  ret i16 %3, !dbg !140
}

; Function Attrs: nounwind
define hidden void @test_font_lookup(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !141 {
    #dbg_value(ptr %0, !145, !DIExpression(), !201)
    #dbg_value(ptr %1, !146, !DIExpression(), !201)
    #dbg_value(i8 %2, !147, !DIExpression(), !201)
  switch i8 %2, label %24 [
    i8 0, label %25
    i8 1, label %4
    i8 2, label %5
    i8 3, label %25
    i8 4, label %25
    i8 5, label %6
    i8 6, label %7
    i8 7, label %8
    i8 8, label %25
    i8 9, label %9
    i8 10, label %25
    i8 11, label %10
    i8 12, label %11
    i8 13, label %12
    i8 14, label %13
    i8 15, label %14
    i8 16, label %15
    i8 17, label %16
    i8 18, label %17
    i8 19, label %18
    i8 20, label %19
    i8 21, label %20
    i8 22, label %21
    i8 23, label %22
    i8 24, label %23
  ], !dbg !202

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !203)
    #dbg_value(ptr %1, !107, !DIExpression(), !203)
    #dbg_value(i16 5, !108, !DIExpression(), !203)
  br label %25, !dbg !207

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !208)
    #dbg_value(ptr %1, !107, !DIExpression(), !208)
    #dbg_value(i16 2, !108, !DIExpression(), !208)
  br label %25, !dbg !212

6:                                                ; preds = %3
    #dbg_value(i16 7, !148, !DIExpression(), !201)
    #dbg_value(i16 3, !149, !DIExpression(), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !213)
    #dbg_value(ptr %1, !107, !DIExpression(), !213)
    #dbg_value(i16 1, !108, !DIExpression(), !213)
  br label %25, !dbg !217

7:                                                ; preds = %3
    #dbg_value(i16 poison, !150, !DIExpression(), !201)
    #dbg_value(i16 poison, !149, !DIExpression(), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !218)
    #dbg_value(ptr %1, !107, !DIExpression(), !218)
    #dbg_value(i16 29, !108, !DIExpression(), !218)
  br label %25, !dbg !222

8:                                                ; preds = %3
    #dbg_value(i16 poison, !150, !DIExpression(), !201)
    #dbg_value(i16 poison, !149, !DIExpression(), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !223)
    #dbg_value(ptr %1, !107, !DIExpression(), !223)
    #dbg_value(i16 19, !108, !DIExpression(), !223)
  br label %25, !dbg !227

9:                                                ; preds = %3
    #dbg_value(i8 7, !152, !DIExpression(), !201)
    #dbg_value(i8 0, !153, !DIExpression(), !201)
    #dbg_value(i8 5, !154, !DIExpression(), !201)
    #dbg_value(i8 -32, !155, !DIExpression(), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !228)
    #dbg_value(ptr %1, !107, !DIExpression(), !228)
    #dbg_value(i16 -32, !108, !DIExpression(), !228)
  br label %25, !dbg !232

10:                                               ; preds = %3
    #dbg_value(i8 5, !152, !DIExpression(), !201)
    #dbg_value(i8 3, !153, !DIExpression(), !201)
    #dbg_value(i8 2, !154, !DIExpression(), !201)
    #dbg_value(i8 20, !155, !DIExpression(), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !233)
    #dbg_value(ptr %1, !107, !DIExpression(), !233)
    #dbg_value(i16 20, !108, !DIExpression(), !233)
  br label %25, !dbg !237

11:                                               ; preds = %3
    #dbg_value(i8 7, !152, !DIExpression(), !201)
    #dbg_value(i8 6, !153, !DIExpression(), !201)
    #dbg_value(i8 1, !154, !DIExpression(), !201)
    #dbg_value(i8 3, !155, !DIExpression(), !201)
    #dbg_value(i32 896, !156, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !238)
    #dbg_value(ptr %1, !107, !DIExpression(), !238)
    #dbg_value(i16 3, !108, !DIExpression(), !238)
  br label %25, !dbg !242

12:                                               ; preds = %3
    #dbg_value(i8 7, !152, !DIExpression(), !201)
    #dbg_value(i8 6, !153, !DIExpression(), !201)
    #dbg_value(i8 1, !154, !DIExpression(), !201)
    #dbg_value(i32 3, !155, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !201)
    #dbg_value(i8 -128, !156, !DIExpression(), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !243)
    #dbg_value(ptr %1, !107, !DIExpression(), !243)
    #dbg_value(i16 -128, !108, !DIExpression(), !243)
  br label %25, !dbg !247

13:                                               ; preds = %3
    #dbg_value(i8 7, !152, !DIExpression(), !201)
    #dbg_value(i8 7, !153, !DIExpression(), !201)
    #dbg_value(i8 2, !154, !DIExpression(), !201)
    #dbg_value(i8 1, !155, !DIExpression(), !201)
    #dbg_value(i32 448, !156, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !248)
    #dbg_value(ptr %1, !107, !DIExpression(), !248)
    #dbg_value(i16 1, !108, !DIExpression(), !248)
  br label %25, !dbg !252

14:                                               ; preds = %3
    #dbg_value(i8 7, !152, !DIExpression(), !201)
    #dbg_value(i8 7, !153, !DIExpression(), !201)
    #dbg_value(i8 2, !154, !DIExpression(), !201)
    #dbg_value(i32 1, !155, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !201)
    #dbg_value(i8 -64, !156, !DIExpression(), !201)
    #dbg_value(ptr %0, !106, !DIExpression(), !253)
    #dbg_value(ptr %1, !107, !DIExpression(), !253)
    #dbg_value(i16 -64, !108, !DIExpression(), !253)
  br label %25, !dbg !257

15:                                               ; preds = %3
    #dbg_value(i16 123, !157, !DIExpression(), !258)
    #dbg_value(i16 3, !160, !DIExpression(), !258)
    #dbg_value(ptr %0, !106, !DIExpression(), !259)
    #dbg_value(ptr %1, !107, !DIExpression(), !259)
    #dbg_value(i16 3, !108, !DIExpression(), !259)
  br label %25

16:                                               ; preds = %3
    #dbg_value(i16 123, !161, !DIExpression(), !261)
    #dbg_value(i16 12, !164, !DIExpression(), !261)
    #dbg_value(i16 2, !165, !DIExpression(), !261)
    #dbg_value(ptr %0, !106, !DIExpression(), !262)
    #dbg_value(ptr %1, !107, !DIExpression(), !262)
    #dbg_value(i16 2, !108, !DIExpression(), !262)
  br label %25

17:                                               ; preds = %3
    #dbg_value(i16 123, !166, !DIExpression(), !264)
    #dbg_value(i16 12, !169, !DIExpression(), !264)
    #dbg_value(i16 1, !169, !DIExpression(), !264)
    #dbg_value(i16 1, !170, !DIExpression(), !264)
    #dbg_value(ptr %0, !106, !DIExpression(), !265)
    #dbg_value(ptr %1, !107, !DIExpression(), !265)
    #dbg_value(i16 1, !108, !DIExpression(), !265)
  br label %25

18:                                               ; preds = %3
    #dbg_value(i16 0, !171, !DIExpression(), !267)
    #dbg_value(i16 1, !174, !DIExpression(), !267)
    #dbg_value(i16 0, !175, !DIExpression(), !267)
    #dbg_value(i16 0, !175, !DIExpression(), !267)
    #dbg_value(i16 1, !174, !DIExpression(), !267)
    #dbg_value(ptr %0, !106, !DIExpression(), !268)
    #dbg_value(ptr %1, !107, !DIExpression(), !268)
    #dbg_value(i16 1, !108, !DIExpression(), !268)
  br label %25

19:                                               ; preds = %3
    #dbg_value(i32 poison, !180, !DIExpression(), !270)
    #dbg_value(i16 poison, !179, !DIExpression(), !270)
    #dbg_value(ptr %0, !106, !DIExpression(), !271)
    #dbg_value(ptr %1, !107, !DIExpression(), !271)
    #dbg_value(i16 1, !108, !DIExpression(), !271)
  br label %25

20:                                               ; preds = %3
    #dbg_value(i16 poison, !184, !DIExpression(), !273)
    #dbg_value(i32 poison, !185, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !273)
    #dbg_value(ptr %0, !106, !DIExpression(), !274)
    #dbg_value(ptr %1, !107, !DIExpression(), !274)
    #dbg_value(i16 2, !108, !DIExpression(), !274)
  br label %25

21:                                               ; preds = %3
    #dbg_value(i16 poison, !189, !DIExpression(), !276)
    #dbg_value(i32 poison, !190, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !276)
    #dbg_value(ptr %0, !106, !DIExpression(), !277)
    #dbg_value(ptr %1, !107, !DIExpression(), !277)
    #dbg_value(i16 3, !108, !DIExpression(), !277)
  br label %25

22:                                               ; preds = %3
    #dbg_value(i16 3, !191, !DIExpression(), !279)
    #dbg_value(i16 11, !194, !DIExpression(), !279)
    #dbg_value(ptr %0, !106, !DIExpression(), !280)
    #dbg_value(ptr %1, !107, !DIExpression(), !280)
    #dbg_value(i16 11, !108, !DIExpression(), !280)
  br label %25

23:                                               ; preds = %3
    #dbg_value(i16 16, !195, !DIExpression(), !282)
    #dbg_value(i16 3, !198, !DIExpression(), !282)
    #dbg_value(i16 11, !199, !DIExpression(), !282)
    #dbg_value(i16 11, !200, !DIExpression(), !282)
    #dbg_value(ptr %0, !106, !DIExpression(), !283)
    #dbg_value(ptr %1, !107, !DIExpression(), !283)
    #dbg_value(i16 11, !108, !DIExpression(), !283)
  br label %25

24:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !285)
    #dbg_value(ptr %1, !107, !DIExpression(), !285)
    #dbg_value(i16 -1, !108, !DIExpression(), !285)
  br label %25, !dbg !287

25:                                               ; preds = %3, %3, %3, %3, %3, %24, %23, %22, %21, %20, %19, %18, %17, %16, %15, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %26 = phi i8 [ -1, %24 ], [ 0, %23 ], [ 0, %22 ], [ 0, %21 ], [ 0, %20 ], [ 0, %19 ], [ 0, %18 ], [ 0, %17 ], [ 0, %16 ], [ 0, %15 ], [ -1, %14 ], [ 0, %13 ], [ -1, %12 ], [ 0, %11 ], [ 0, %10 ], [ -1, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %27 = phi i8 [ -1, %24 ], [ 11, %23 ], [ 11, %22 ], [ 3, %21 ], [ 2, %20 ], [ 1, %19 ], [ 1, %18 ], [ 1, %17 ], [ 2, %16 ], [ 3, %15 ], [ -64, %14 ], [ 1, %13 ], [ -128, %12 ], [ 3, %11 ], [ 20, %10 ], [ -32, %9 ], [ 19, %8 ], [ 29, %7 ], [ 1, %6 ], [ 2, %5 ], [ 5, %4 ], [ 7, %3 ], [ 7, %3 ], [ 7, %3 ], [ 7, %3 ], [ 7, %3 ]
  %28 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !288
  store i8 %26, ptr %1, align 1, !dbg !289, !tbaa !113
  store i8 %27, ptr %28, align 1, !dbg !290, !tbaa !113
  %29 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !291
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !292
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !293
  ret void, !dbg !287
}

; Function Attrs: nofree norecurse nosync nounwind memory(read, argmem: none, inaccessiblemem: none)
define hidden signext i16 @fb_checksum() local_unnamed_addr #3 !dbg !294 {
    #dbg_value(i16 0, !300, !DIExpression(), !301)
    #dbg_value(i16 0, !299, !DIExpression(), !301)
    #dbg_value(i16 poison, !299, !DIExpression(), !301)
  br label %1, !dbg !302

1:                                                ; preds = %0, %1
  %2 = phi i32 [ 0, %0 ], [ %10, %1 ]
  %3 = phi i16 [ 0, %0 ], [ %7, %1 ]
    #dbg_value(i16 %3, !300, !DIExpression(), !301)
  %4 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %2, !dbg !304
  %5 = load i8, ptr %4, align 1, !dbg !304, !tbaa !113
  %6 = zext i8 %5 to i16, !dbg !304
  %7 = add i16 %3, %6, !dbg !307
    #dbg_value(i16 %7, !300, !DIExpression(), !301)
    #dbg_value(i16 poison, !299, !DIExpression(), !301)
  %8 = shl nsw i32 %2, 16, !dbg !308
  %9 = add i32 %8, 65536, !dbg !308
  %10 = ashr exact i32 %9, 16, !dbg !308
  %11 = icmp slt i32 %10, 32, !dbg !309
  br i1 %11, label %1, label %12, !dbg !302, !llvm.loop !310

12:                                               ; preds = %1
  ret i16 %7, !dbg !314
}

; Function Attrs: nounwind
define hidden void @test_fillrect(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !315 {
    #dbg_value(ptr %0, !317, !DIExpression(), !340)
    #dbg_value(ptr %1, !318, !DIExpression(), !340)
    #dbg_value(i8 %2, !319, !DIExpression(), !340)
  switch i8 %2, label %145 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
    i8 5, label %9
    i8 6, label %10
    i8 7, label %11
    i8 8, label %12
    i8 9, label %13
    i8 10, label %14
    i8 11, label %15
    i8 12, label %16
    i8 13, label %17
    i8 14, label %18
    i8 15, label %19
    i8 16, label %20
    i8 17, label %21
    i8 18, label %22
    i8 19, label %23
    i8 20, label %24
    i8 21, label %41
    i8 22, label %59
    i8 23, label %77
    i8 24, label %81
    i8 25, label %103
    i8 26, label %107
    i8 27, label %139
    i8 28, label %143
  ], !dbg !341

4:                                                ; preds = %3
    #dbg_value(i16 0, !320, !DIExpression(), !340)
    #dbg_value(i8 -1, !327, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !342)
    #dbg_value(ptr %1, !107, !DIExpression(), !342)
    #dbg_value(i16 255, !108, !DIExpression(), !342)
  store i8 0, ptr %1, align 1, !dbg !346, !tbaa !113
  br label %146, !dbg !347

5:                                                ; preds = %3
    #dbg_value(i16 3, !320, !DIExpression(), !340)
    #dbg_value(i8 31, !327, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !348)
    #dbg_value(ptr %1, !107, !DIExpression(), !348)
    #dbg_value(i16 31, !108, !DIExpression(), !348)
  store i8 0, ptr %1, align 1, !dbg !352, !tbaa !113
  br label %146, !dbg !353

6:                                                ; preds = %3
    #dbg_value(i16 7, !320, !DIExpression(), !340)
    #dbg_value(i8 1, !327, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !354)
    #dbg_value(ptr %1, !107, !DIExpression(), !354)
    #dbg_value(i16 1, !108, !DIExpression(), !354)
  store i8 0, ptr %1, align 1, !dbg !358, !tbaa !113
  br label %146, !dbg !359

7:                                                ; preds = %3
    #dbg_value(i16 8, !320, !DIExpression(), !340)
    #dbg_value(i8 -1, !327, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !360)
    #dbg_value(ptr %1, !107, !DIExpression(), !360)
    #dbg_value(i16 255, !108, !DIExpression(), !360)
  store i8 0, ptr %1, align 1, !dbg !364, !tbaa !113
  br label %146, !dbg !365

8:                                                ; preds = %3
    #dbg_value(i16 7, !322, !DIExpression(), !340)
    #dbg_value(i8 -1, !328, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !366)
    #dbg_value(ptr %1, !107, !DIExpression(), !366)
    #dbg_value(i16 255, !108, !DIExpression(), !366)
  store i8 0, ptr %1, align 1, !dbg !370, !tbaa !113
  br label %146, !dbg !371

9:                                                ; preds = %3
    #dbg_value(i16 4, !322, !DIExpression(), !340)
    #dbg_value(i8 -8, !328, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !372)
    #dbg_value(ptr %1, !107, !DIExpression(), !372)
    #dbg_value(i16 248, !108, !DIExpression(), !372)
  store i8 0, ptr %1, align 1, !dbg !376, !tbaa !113
  br label %146, !dbg !377

10:                                               ; preds = %3
    #dbg_value(i16 0, !322, !DIExpression(), !340)
    #dbg_value(i8 -128, !328, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !378)
    #dbg_value(ptr %1, !107, !DIExpression(), !378)
    #dbg_value(i16 128, !108, !DIExpression(), !378)
  store i8 0, ptr %1, align 1, !dbg !382, !tbaa !113
  br label %146, !dbg !383

11:                                               ; preds = %3
    #dbg_value(i16 15, !322, !DIExpression(), !340)
    #dbg_value(i8 -1, !328, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !384)
    #dbg_value(ptr %1, !107, !DIExpression(), !384)
    #dbg_value(i16 255, !108, !DIExpression(), !384)
  store i8 0, ptr %1, align 1, !dbg !388, !tbaa !113
  br label %146, !dbg !389

12:                                               ; preds = %3
    #dbg_value(i16 2, !320, !DIExpression(), !340)
    #dbg_value(i16 5, !322, !DIExpression(), !340)
    #dbg_value(i8 63, !327, !DIExpression(), !340)
    #dbg_value(i8 -4, !328, !DIExpression(), !340)
    #dbg_value(i8 60, !332, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !390)
    #dbg_value(ptr %1, !107, !DIExpression(), !390)
    #dbg_value(i16 60, !108, !DIExpression(), !390)
  store i8 0, ptr %1, align 1, !dbg !394, !tbaa !113
  br label %146, !dbg !395

13:                                               ; preds = %3
    #dbg_value(i16 0, !320, !DIExpression(), !340)
    #dbg_value(i16 7, !322, !DIExpression(), !340)
    #dbg_value(i8 -1, !327, !DIExpression(), !340)
    #dbg_value(i8 -1, !328, !DIExpression(), !340)
    #dbg_value(i8 -1, !332, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !396)
    #dbg_value(ptr %1, !107, !DIExpression(), !396)
    #dbg_value(i16 255, !108, !DIExpression(), !396)
  store i8 0, ptr %1, align 1, !dbg !400, !tbaa !113
  br label %146, !dbg !401

14:                                               ; preds = %3
    #dbg_value(i16 3, !320, !DIExpression(), !340)
    #dbg_value(i16 3, !322, !DIExpression(), !340)
    #dbg_value(i8 31, !327, !DIExpression(), !340)
    #dbg_value(i8 -16, !328, !DIExpression(), !340)
    #dbg_value(i8 16, !332, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !402)
    #dbg_value(ptr %1, !107, !DIExpression(), !402)
    #dbg_value(i16 16, !108, !DIExpression(), !402)
  store i8 0, ptr %1, align 1, !dbg !406, !tbaa !113
  br label %146, !dbg !407

15:                                               ; preds = %3
    #dbg_value(i16 0, !320, !DIExpression(), !340)
    #dbg_value(i16 7, !322, !DIExpression(), !340)
    #dbg_value(i16 0, !324, !DIExpression(), !340)
    #dbg_value(i16 0, !325, !DIExpression(), !340)
    #dbg_value(i16 -1, !326, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !408)
    #dbg_value(ptr %1, !107, !DIExpression(), !408)
    #dbg_value(i16 -1, !108, !DIExpression(), !408)
  store i8 -1, ptr %1, align 1, !dbg !412, !tbaa !113
  br label %146, !dbg !413

16:                                               ; preds = %3
    #dbg_value(i16 0, !320, !DIExpression(), !340)
    #dbg_value(i16 15, !322, !DIExpression(), !340)
    #dbg_value(i16 0, !324, !DIExpression(), !340)
    #dbg_value(i16 1, !325, !DIExpression(), !340)
    #dbg_value(i16 0, !326, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !414)
    #dbg_value(ptr %1, !107, !DIExpression(), !414)
    #dbg_value(i16 0, !108, !DIExpression(), !414)
  store i8 0, ptr %1, align 1, !dbg !418, !tbaa !113
  br label %146, !dbg !419

17:                                               ; preds = %3
    #dbg_value(i16 0, !320, !DIExpression(), !340)
    #dbg_value(i16 23, !322, !DIExpression(), !340)
    #dbg_value(i16 0, !324, !DIExpression(), !340)
    #dbg_value(i16 2, !325, !DIExpression(), !340)
    #dbg_value(i16 1, !326, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !420)
    #dbg_value(ptr %1, !107, !DIExpression(), !420)
    #dbg_value(i16 1, !108, !DIExpression(), !420)
  store i8 0, ptr %1, align 1, !dbg !424, !tbaa !113
  br label %146, !dbg !425

18:                                               ; preds = %3
    #dbg_value(i16 0, !320, !DIExpression(), !340)
    #dbg_value(i16 31, !322, !DIExpression(), !340)
    #dbg_value(i16 0, !324, !DIExpression(), !340)
    #dbg_value(i16 3, !325, !DIExpression(), !340)
    #dbg_value(i16 2, !326, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !426)
    #dbg_value(ptr %1, !107, !DIExpression(), !426)
    #dbg_value(i16 2, !108, !DIExpression(), !426)
  store i8 0, ptr %1, align 1, !dbg !430, !tbaa !113
  br label %146, !dbg !431

19:                                               ; preds = %3
    #dbg_value(i16 0, !330, !DIExpression(), !340)
    #dbg_value(i16 0, !331, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !432)
    #dbg_value(ptr %1, !107, !DIExpression(), !432)
    #dbg_value(i16 0, !108, !DIExpression(), !432)
  store i8 0, ptr %1, align 1, !dbg !436, !tbaa !113
  br label %146, !dbg !437

20:                                               ; preds = %3
    #dbg_value(i16 3, !330, !DIExpression(), !340)
    #dbg_value(i16 12, !331, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !438)
    #dbg_value(ptr %1, !107, !DIExpression(), !438)
    #dbg_value(i16 12, !108, !DIExpression(), !438)
  store i8 0, ptr %1, align 1, !dbg !442, !tbaa !113
  br label %146, !dbg !443

21:                                               ; preds = %3
    #dbg_value(i16 7, !330, !DIExpression(), !340)
    #dbg_value(i16 28, !331, !DIExpression(), !340)
    #dbg_value(ptr %0, !106, !DIExpression(), !444)
    #dbg_value(ptr %1, !107, !DIExpression(), !444)
    #dbg_value(i16 28, !108, !DIExpression(), !444)
  store i8 0, ptr %1, align 1, !dbg !448, !tbaa !113
  br label %146, !dbg !449

22:                                               ; preds = %3
    #dbg_value(i16 0, !321, !DIExpression(), !340)
    #dbg_value(i16 0, !323, !DIExpression(), !340)
    #dbg_value(i16 4, !334, !DIExpression(), !450)
    #dbg_value(ptr %0, !106, !DIExpression(), !451)
    #dbg_value(ptr %1, !107, !DIExpression(), !451)
    #dbg_value(i16 4, !108, !DIExpression(), !451)
  store i8 0, ptr %1, align 1, !dbg !453, !tbaa !113
  br label %146

23:                                               ; preds = %3
    #dbg_value(i16 2, !321, !DIExpression(), !340)
    #dbg_value(i16 5, !323, !DIExpression(), !340)
    #dbg_value(i16 16, !337, !DIExpression(), !454)
    #dbg_value(ptr %0, !106, !DIExpression(), !455)
    #dbg_value(ptr %1, !107, !DIExpression(), !455)
    #dbg_value(i16 16, !108, !DIExpression(), !455)
  store i8 0, ptr %1, align 1, !dbg !457, !tbaa !113
  br label %146

24:                                               ; preds = %3
  %25 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !458
    #dbg_value(i16 0, !300, !DIExpression(), !461)
    #dbg_value(i16 0, !299, !DIExpression(), !461)
    #dbg_value(i16 poison, !299, !DIExpression(), !461)
  br label %26, !dbg !463

26:                                               ; preds = %26, %24
  %27 = phi i32 [ 0, %24 ], [ %35, %26 ]
  %28 = phi i16 [ 0, %24 ], [ %32, %26 ]
    #dbg_value(i16 %28, !300, !DIExpression(), !461)
  %29 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %27, !dbg !464
  %30 = load i8, ptr %29, align 1, !dbg !464, !tbaa !113
  %31 = zext i8 %30 to i16, !dbg !464
  %32 = add i16 %28, %31, !dbg !465
    #dbg_value(i16 %32, !300, !DIExpression(), !461)
    #dbg_value(i16 poison, !299, !DIExpression(), !461)
  %33 = shl nsw i32 %27, 16, !dbg !466
  %34 = add i32 %33, 65536, !dbg !466
  %35 = ashr exact i32 %34, 16, !dbg !466
  %36 = icmp slt i32 %35, 32, !dbg !467
  br i1 %36, label %26, label %37, !dbg !463, !llvm.loop !468

37:                                               ; preds = %26
    #dbg_value(ptr %0, !106, !DIExpression(), !470)
    #dbg_value(ptr %1, !107, !DIExpression(), !470)
    #dbg_value(i16 %32, !108, !DIExpression(), !470)
  %38 = lshr i16 %32, 8, !dbg !472
  %39 = trunc nuw i16 %38 to i8, !dbg !473
  store i8 %39, ptr %1, align 1, !dbg !474, !tbaa !113
  %40 = trunc i16 %32 to i8, !dbg !475
  br label %146, !dbg !476

41:                                               ; preds = %3
  %42 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !477
    #dbg_value(i16 0, !330, !DIExpression(), !340)
  %43 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 4, i8 noundef signext -1) #11, !dbg !480
    #dbg_value(i16 0, !300, !DIExpression(), !481)
    #dbg_value(i16 0, !299, !DIExpression(), !481)
    #dbg_value(i16 poison, !299, !DIExpression(), !481)
  br label %44, !dbg !483

44:                                               ; preds = %44, %41
  %45 = phi i32 [ 0, %41 ], [ %53, %44 ]
  %46 = phi i16 [ 0, %41 ], [ %50, %44 ]
    #dbg_value(i16 %46, !300, !DIExpression(), !481)
  %47 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %45, !dbg !484
  %48 = load i8, ptr %47, align 1, !dbg !484, !tbaa !113
  %49 = zext i8 %48 to i16, !dbg !484
  %50 = add i16 %46, %49, !dbg !485
    #dbg_value(i16 %50, !300, !DIExpression(), !481)
    #dbg_value(i16 poison, !299, !DIExpression(), !481)
  %51 = shl nsw i32 %45, 16, !dbg !486
  %52 = add i32 %51, 65536, !dbg !486
  %53 = ashr exact i32 %52, 16, !dbg !486
  %54 = icmp slt i32 %53, 32, !dbg !487
  br i1 %54, label %44, label %55, !dbg !483, !llvm.loop !488

55:                                               ; preds = %44
    #dbg_value(ptr %0, !106, !DIExpression(), !490)
    #dbg_value(ptr %1, !107, !DIExpression(), !490)
    #dbg_value(i16 %50, !108, !DIExpression(), !490)
  %56 = lshr i16 %50, 8, !dbg !492
  %57 = trunc nuw i16 %56 to i8, !dbg !493
  store i8 %57, ptr %1, align 1, !dbg !494, !tbaa !113
  %58 = trunc i16 %50 to i8, !dbg !495
  br label %146, !dbg !496

59:                                               ; preds = %3
  %60 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !497
    #dbg_value(i16 2, !321, !DIExpression(), !340)
    #dbg_value(i16 4, !323, !DIExpression(), !340)
  %61 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 8, i16 noundef signext 12, i8 noundef signext -1) #11, !dbg !500
    #dbg_value(i16 0, !300, !DIExpression(), !501)
    #dbg_value(i16 0, !299, !DIExpression(), !501)
    #dbg_value(i16 poison, !299, !DIExpression(), !501)
  br label %62, !dbg !503

62:                                               ; preds = %62, %59
  %63 = phi i32 [ 0, %59 ], [ %71, %62 ]
  %64 = phi i16 [ 0, %59 ], [ %68, %62 ]
    #dbg_value(i16 %64, !300, !DIExpression(), !501)
  %65 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %63, !dbg !504
  %66 = load i8, ptr %65, align 1, !dbg !504, !tbaa !113
  %67 = zext i8 %66 to i16, !dbg !504
  %68 = add i16 %64, %67, !dbg !505
    #dbg_value(i16 %68, !300, !DIExpression(), !501)
    #dbg_value(i16 poison, !299, !DIExpression(), !501)
  %69 = shl nsw i32 %63, 16, !dbg !506
  %70 = add i32 %69, 65536, !dbg !506
  %71 = ashr exact i32 %70, 16, !dbg !506
  %72 = icmp slt i32 %71, 32, !dbg !507
  br i1 %72, label %62, label %73, !dbg !503, !llvm.loop !508

73:                                               ; preds = %62
    #dbg_value(ptr %0, !106, !DIExpression(), !510)
    #dbg_value(ptr %1, !107, !DIExpression(), !510)
    #dbg_value(i16 %68, !108, !DIExpression(), !510)
  %74 = lshr i16 %68, 8, !dbg !512
  %75 = trunc nuw i16 %74 to i8, !dbg !513
  store i8 %75, ptr %1, align 1, !dbg !514, !tbaa !113
  %76 = trunc i16 %68 to i8, !dbg !515
  br label %146, !dbg !516

77:                                               ; preds = %3
  %78 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !517
    #dbg_value(i16 2, !320, !DIExpression(), !340)
    #dbg_value(i16 5, !322, !DIExpression(), !340)
    #dbg_value(i8 63, !327, !DIExpression(), !340)
    #dbg_value(i8 -4, !328, !DIExpression(), !340)
    #dbg_value(i8 60, !332, !DIExpression(), !340)
  %79 = load i8, ptr @shared_fb, align 16, !dbg !520, !tbaa !113
  %80 = or i8 %79, 60, !dbg !520
  store i8 %80, ptr @shared_fb, align 16, !dbg !520, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !521)
    #dbg_value(ptr %1, !107, !DIExpression(), !521)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !521)
  store i8 0, ptr %1, align 1, !dbg !523, !tbaa !113
  br label %146, !dbg !524

81:                                               ; preds = %3
  %82 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !525
    #dbg_value(i16 4, !320, !DIExpression(), !340)
    #dbg_value(i16 19, !322, !DIExpression(), !340)
    #dbg_value(i16 0, !330, !DIExpression(), !340)
    #dbg_value(i16 0, !324, !DIExpression(), !340)
    #dbg_value(i16 2, !325, !DIExpression(), !340)
    #dbg_value(i8 15, !327, !DIExpression(), !340)
    #dbg_value(i8 -16, !328, !DIExpression(), !340)
    #dbg_value(i16 0, !331, !DIExpression(), !340)
  %83 = load i8, ptr @shared_fb, align 16, !dbg !528, !tbaa !113
  %84 = or i8 %83, 15, !dbg !528
  store i8 %84, ptr @shared_fb, align 16, !dbg !528, !tbaa !113
    #dbg_value(i16 1, !326, !DIExpression(), !340)
  %85 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 1, i16 noundef signext 1, i8 noundef signext -1) #11, !dbg !529
  %86 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !532, !tbaa !113
  %87 = or i8 %86, -16, !dbg !532
  store i8 %87, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !532, !tbaa !113
    #dbg_value(i16 0, !300, !DIExpression(), !533)
    #dbg_value(i16 0, !299, !DIExpression(), !533)
    #dbg_value(i16 poison, !299, !DIExpression(), !533)
  br label %88, !dbg !535

88:                                               ; preds = %88, %81
  %89 = phi i32 [ 0, %81 ], [ %97, %88 ]
  %90 = phi i16 [ 0, %81 ], [ %94, %88 ]
    #dbg_value(i16 %90, !300, !DIExpression(), !533)
  %91 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %89, !dbg !536
  %92 = load i8, ptr %91, align 1, !dbg !536, !tbaa !113
  %93 = zext i8 %92 to i16, !dbg !536
  %94 = add i16 %90, %93, !dbg !537
    #dbg_value(i16 %94, !300, !DIExpression(), !533)
    #dbg_value(i16 poison, !299, !DIExpression(), !533)
  %95 = shl nsw i32 %89, 16, !dbg !538
  %96 = add i32 %95, 65536, !dbg !538
  %97 = ashr exact i32 %96, 16, !dbg !538
  %98 = icmp slt i32 %97, 32, !dbg !539
  br i1 %98, label %88, label %99, !dbg !535, !llvm.loop !540

99:                                               ; preds = %88
    #dbg_value(ptr %0, !106, !DIExpression(), !542)
    #dbg_value(ptr %1, !107, !DIExpression(), !542)
    #dbg_value(i16 %94, !108, !DIExpression(), !542)
  %100 = lshr i16 %94, 8, !dbg !544
  %101 = trunc nuw i16 %100 to i8, !dbg !545
  store i8 %101, ptr %1, align 1, !dbg !546, !tbaa !113
  %102 = trunc i16 %94 to i8, !dbg !547
  br label %146, !dbg !548

103:                                              ; preds = %3
  %104 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext -1) #11, !dbg !549
    #dbg_value(i16 2, !320, !DIExpression(), !340)
    #dbg_value(i16 5, !322, !DIExpression(), !340)
    #dbg_value(i8 63, !327, !DIExpression(), !340)
    #dbg_value(i8 -4, !328, !DIExpression(), !340)
    #dbg_value(i8 60, !332, !DIExpression(), !340)
  %105 = load i8, ptr @shared_fb, align 16, !dbg !552, !tbaa !113
  %106 = and i8 %105, -61, !dbg !553
  store i8 %106, ptr @shared_fb, align 16, !dbg !554, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !555)
    #dbg_value(ptr %1, !107, !DIExpression(), !555)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !555)
  store i8 0, ptr %1, align 1, !dbg !557, !tbaa !113
  br label %146, !dbg !558

107:                                              ; preds = %3
  %108 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !559
    #dbg_value(i16 4, !320, !DIExpression(), !340)
    #dbg_value(i16 19, !322, !DIExpression(), !340)
    #dbg_value(i16 1, !321, !DIExpression(), !340)
    #dbg_value(i16 2, !323, !DIExpression(), !340)
    #dbg_value(i16 0, !324, !DIExpression(), !340)
    #dbg_value(i16 2, !325, !DIExpression(), !340)
    #dbg_value(i8 15, !327, !DIExpression(), !340)
    #dbg_value(i8 -16, !328, !DIExpression(), !340)
    #dbg_value(i16 1, !326, !DIExpression(), !340)
    #dbg_value(i16 1, !330, !DIExpression(), !340)
  br label %109, !dbg !562

109:                                              ; preds = %107, %109
  %110 = phi i32 [ 1, %107 ], [ %122, %109 ]
    #dbg_value(i32 %110, !330, !DIExpression(), !340)
  %111 = shl nsw i32 %110, 2, !dbg !564
    #dbg_value(i32 %111, !331, !DIExpression(), !340)
  %112 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %111, !dbg !567
  %113 = load i8, ptr %112, align 4, !dbg !568, !tbaa !113
  %114 = or i8 %113, 15, !dbg !568
  store i8 %114, ptr %112, align 4, !dbg !568, !tbaa !113
  %115 = trunc i32 %111 to i16, !dbg !569
  %116 = or disjoint i16 %115, 1, !dbg !569
  %117 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext %116, i16 noundef signext 1, i8 noundef signext -1) #11, !dbg !569
  %118 = or disjoint i32 %111, 2, !dbg !572
  %119 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %118, !dbg !573
  %120 = load i8, ptr %119, align 2, !dbg !574, !tbaa !113
  %121 = or i8 %120, -16, !dbg !574
  store i8 %121, ptr %119, align 2, !dbg !574, !tbaa !113
  %122 = add nuw nsw i32 %110, 1, !dbg !575
    #dbg_value(i32 %122, !330, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !340)
    #dbg_value(i32 %122, !330, !DIExpression(), !340)
  %123 = icmp eq i32 %122, 3, !dbg !576
  br i1 %123, label %124, label %109, !dbg !562, !llvm.loop !577

124:                                              ; preds = %109, %124
  %125 = phi i32 [ %133, %124 ], [ 0, %109 ]
  %126 = phi i16 [ %130, %124 ], [ 0, %109 ]
    #dbg_value(i16 %126, !300, !DIExpression(), !579)
  %127 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %125, !dbg !581
  %128 = load i8, ptr %127, align 1, !dbg !581, !tbaa !113
  %129 = zext i8 %128 to i16, !dbg !581
  %130 = add i16 %126, %129, !dbg !582
    #dbg_value(i16 %130, !300, !DIExpression(), !579)
    #dbg_value(i16 poison, !299, !DIExpression(), !579)
  %131 = shl nsw i32 %125, 16, !dbg !583
  %132 = add i32 %131, 65536, !dbg !583
  %133 = ashr exact i32 %132, 16, !dbg !583
  %134 = icmp slt i32 %133, 32, !dbg !584
  br i1 %134, label %124, label %135, !dbg !585, !llvm.loop !586

135:                                              ; preds = %124
    #dbg_value(ptr %0, !106, !DIExpression(), !588)
    #dbg_value(ptr %1, !107, !DIExpression(), !588)
    #dbg_value(i16 %130, !108, !DIExpression(), !588)
  %136 = lshr i16 %130, 8, !dbg !590
  %137 = trunc nuw i16 %136 to i8, !dbg !591
  store i8 %137, ptr %1, align 1, !dbg !592, !tbaa !113
  %138 = trunc i16 %130 to i8, !dbg !593
  br label %146, !dbg !594

139:                                              ; preds = %3
  %140 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !595
    #dbg_value(i16 5, !320, !DIExpression(), !340)
    #dbg_value(i16 5, !322, !DIExpression(), !340)
    #dbg_value(i8 7, !327, !DIExpression(), !340)
    #dbg_value(i8 -4, !328, !DIExpression(), !340)
    #dbg_value(i8 4, !332, !DIExpression(), !340)
  %141 = load i8, ptr @shared_fb, align 16, !dbg !598, !tbaa !113
  %142 = or i8 %141, 4, !dbg !598
  store i8 %142, ptr @shared_fb, align 16, !dbg !598, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !599)
    #dbg_value(ptr %1, !107, !DIExpression(), !599)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !599)
  store i8 0, ptr %1, align 1, !dbg !601, !tbaa !113
  br label %146, !dbg !602

143:                                              ; preds = %3
  %144 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !603
    #dbg_value(i16 8, !320, !DIExpression(), !340)
    #dbg_value(i16 15, !322, !DIExpression(), !340)
    #dbg_value(i16 1, !324, !DIExpression(), !340)
    #dbg_value(i32 1, !325, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !340)
    #dbg_value(i8 -1, !327, !DIExpression(), !340)
    #dbg_value(i8 -1, !328, !DIExpression(), !340)
    #dbg_value(i8 -1, !332, !DIExpression(), !340)
  store i8 -1, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !606, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !607)
    #dbg_value(ptr %1, !107, !DIExpression(), !607)
    #dbg_value(i16 255, !108, !DIExpression(), !607)
  store i8 0, ptr %1, align 1, !dbg !609, !tbaa !113
  br label %146, !dbg !610

145:                                              ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !611)
    #dbg_value(ptr %1, !107, !DIExpression(), !611)
    #dbg_value(i16 -1, !108, !DIExpression(), !611)
  store i8 -1, ptr %1, align 1, !dbg !613, !tbaa !113
  br label %146, !dbg !614

146:                                              ; preds = %145, %143, %139, %135, %103, %99, %77, %73, %55, %37, %23, %22, %21, %20, %19, %18, %17, %16, %15, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %147 = phi i8 [ -1, %145 ], [ -1, %143 ], [ %142, %139 ], [ %138, %135 ], [ %106, %103 ], [ %102, %99 ], [ %80, %77 ], [ %76, %73 ], [ %58, %55 ], [ %40, %37 ], [ 16, %23 ], [ 4, %22 ], [ 28, %21 ], [ 12, %20 ], [ 0, %19 ], [ 2, %18 ], [ 1, %17 ], [ 0, %16 ], [ -1, %15 ], [ 16, %14 ], [ -1, %13 ], [ 60, %12 ], [ -1, %11 ], [ -128, %10 ], [ -8, %9 ], [ -1, %8 ], [ -1, %7 ], [ 1, %6 ], [ 31, %5 ], [ -1, %4 ]
  %148 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !615
  store i8 %147, ptr %148, align 1, !dbg !616, !tbaa !113
  %149 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !617
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !618
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !619
  ret void, !dbg !614
}

declare !dbg !620 signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef, i16 noundef signext, i16 noundef signext, i8 noundef signext) local_unnamed_addr #1

; Function Attrs: nofree norecurse nosync nounwind memory(write, argmem: none, inaccessiblemem: none)
define hidden void @reset_pool() local_unnamed_addr #4 !dbg !623 {
    #dbg_value(i16 0, !627, !DIExpression(), !628)
    #dbg_value(i16 poison, !627, !DIExpression(), !628)
  br label %1, !dbg !629

1:                                                ; preds = %0, %1
  %2 = phi i32 [ 0, %0 ], [ %6, %1 ]
  %3 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %2, !dbg !631
    #dbg_value(i16 poison, !627, !DIExpression(), !628)
  %4 = shl nsw i32 %2, 16, !dbg !634
  %5 = add i32 %4, 65536, !dbg !634
  %6 = ashr exact i32 %5, 16, !dbg !634
  %7 = icmp slt i32 %6, 4, !dbg !635
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %3, i8 0, i64 6, i1 false), !dbg !636
  br i1 %7, label %1, label %8, !dbg !629, !llvm.loop !637

8:                                                ; preds = %1
  ret void, !dbg !639
}

; Function Attrs: nounwind
define hidden void @test_object_pool(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !640 {
    #dbg_value(ptr %0, !642, !DIExpression(), !650)
    #dbg_value(ptr %1, !643, !DIExpression(), !650)
    #dbg_value(i8 %2, !644, !DIExpression(), !650)
  switch i8 %2, label %582 [
    i8 0, label %4
    i8 1, label %12
    i8 2, label %20
    i8 3, label %28
    i8 4, label %51
    i8 5, label %75
    i8 6, label %99
    i8 7, label %122
    i8 8, label %146
    i8 9, label %170
    i8 10, label %200
    i8 11, label %228
    i8 12, label %257
    i8 13, label %286
    i8 14, label %325
    i8 15, label %353
    i8 16, label %380
    i8 17, label %408
    i8 18, label %436
    i8 19, label %468
    i8 20, label %496
    i8 21, label %524
    i8 22, label %554
  ], !dbg !651

4:                                                ; preds = %3, %4
  %5 = phi i32 [ %9, %4 ], [ 0, %3 ]
  %6 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %5, !dbg !652
    #dbg_value(i16 poison, !627, !DIExpression(), !656)
  %7 = shl nsw i32 %5, 16, !dbg !657
  %8 = add i32 %7, 65536, !dbg !657
  %9 = ashr exact i32 %8, 16, !dbg !657
  %10 = icmp slt i32 %9, 4, !dbg !658
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %6, i8 0, i64 6, i1 false), !dbg !659
  br i1 %10, label %4, label %11, !dbg !660, !llvm.loop !661

11:                                               ; preds = %4
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !663, !tbaa !664
    #dbg_value(ptr %0, !106, !DIExpression(), !667)
    #dbg_value(ptr %1, !107, !DIExpression(), !667)
    #dbg_value(i16 1, !108, !DIExpression(), !667)
  store i8 0, ptr %1, align 1, !dbg !669, !tbaa !113
  br label %583, !dbg !670

12:                                               ; preds = %3, %12
  %13 = phi i32 [ %17, %12 ], [ 0, %3 ]
  %14 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %13, !dbg !671
    #dbg_value(i16 poison, !627, !DIExpression(), !675)
  %15 = shl nsw i32 %13, 16, !dbg !676
  %16 = add i32 %15, 65536, !dbg !676
  %17 = ashr exact i32 %16, 16, !dbg !676
  %18 = icmp slt i32 %17, 4, !dbg !677
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %14, i8 0, i64 6, i1 false), !dbg !678
  br i1 %18, label %12, label %19, !dbg !679, !llvm.loop !680

19:                                               ; preds = %12
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !682, !tbaa !664
    #dbg_value(ptr %0, !106, !DIExpression(), !683)
    #dbg_value(ptr %1, !107, !DIExpression(), !683)
    #dbg_value(i16 1, !108, !DIExpression(), !683)
  store i8 0, ptr %1, align 1, !dbg !685, !tbaa !113
  br label %583, !dbg !686

20:                                               ; preds = %3, %20
  %21 = phi i32 [ %25, %20 ], [ 0, %3 ]
  %22 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %21, !dbg !687
    #dbg_value(i16 poison, !627, !DIExpression(), !691)
  %23 = shl nsw i32 %21, 16, !dbg !692
  %24 = add i32 %23, 65536, !dbg !692
  %25 = ashr exact i32 %24, 16, !dbg !692
  %26 = icmp slt i32 %25, 4, !dbg !693
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %22, i8 0, i64 6, i1 false), !dbg !694
  br i1 %26, label %20, label %27, !dbg !695, !llvm.loop !696

27:                                               ; preds = %20
  store i8 0, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !698, !tbaa !664
    #dbg_value(ptr %0, !106, !DIExpression(), !699)
    #dbg_value(ptr %1, !107, !DIExpression(), !699)
    #dbg_value(i16 0, !108, !DIExpression(), !699)
  store i8 0, ptr %1, align 1, !dbg !701, !tbaa !113
  br label %583, !dbg !702

28:                                               ; preds = %3, %28
  %29 = phi i32 [ %33, %28 ], [ 0, %3 ]
  %30 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %29, !dbg !703
    #dbg_value(i16 poison, !627, !DIExpression(), !707)
  %31 = shl nsw i32 %29, 16, !dbg !708
  %32 = add i32 %31, 65536, !dbg !708
  %33 = ashr exact i32 %32, 16, !dbg !708
  %34 = icmp slt i32 %33, 4, !dbg !709
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %30, i8 0, i64 6, i1 false), !dbg !710
  br i1 %34, label %28, label %35, !dbg !711, !llvm.loop !712

35:                                               ; preds = %28, %35
  %36 = phi i32 [ %45, %35 ], [ 0, %28 ]
  %37 = phi i16 [ %42, %35 ], [ 0, %28 ]
    #dbg_value(i16 %37, !646, !DIExpression(), !650)
  %38 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %36, i32 2, !dbg !714
  %39 = load i8, ptr %38, align 2, !dbg !714, !tbaa !664
  %40 = icmp ne i8 %39, 0, !dbg !719
  %41 = zext i1 %40 to i16, !dbg !720
  %42 = add i16 %37, %41, !dbg !720
    #dbg_value(i16 %42, !646, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %43 = shl nsw i32 %36, 16, !dbg !721
  %44 = add i32 %43, 65536, !dbg !721
  %45 = ashr exact i32 %44, 16, !dbg !721
  %46 = icmp slt i32 %45, 4, !dbg !722
  br i1 %46, label %35, label %47, !dbg !723, !llvm.loop !724

47:                                               ; preds = %35
    #dbg_value(ptr %0, !106, !DIExpression(), !726)
    #dbg_value(ptr %1, !107, !DIExpression(), !726)
    #dbg_value(i16 %42, !108, !DIExpression(), !726)
  %48 = lshr i16 %42, 8, !dbg !728
  %49 = trunc nuw i16 %48 to i8, !dbg !729
  store i8 %49, ptr %1, align 1, !dbg !730, !tbaa !113
  %50 = trunc i16 %42 to i8, !dbg !731
  br label %583, !dbg !732

51:                                               ; preds = %3, %51
  %52 = phi i32 [ %56, %51 ], [ 0, %3 ]
  %53 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %52, !dbg !733
    #dbg_value(i16 poison, !627, !DIExpression(), !737)
  %54 = shl nsw i32 %52, 16, !dbg !738
  %55 = add i32 %54, 65536, !dbg !738
  %56 = ashr exact i32 %55, 16, !dbg !738
  %57 = icmp slt i32 %56, 4, !dbg !739
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %53, i8 0, i64 6, i1 false), !dbg !740
  br i1 %57, label %51, label %58, !dbg !741, !llvm.loop !742

58:                                               ; preds = %51
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !744, !tbaa !664
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !745, !tbaa !664
    #dbg_value(i16 0, !646, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %59, !dbg !746

59:                                               ; preds = %58, %59
  %60 = phi i32 [ 0, %58 ], [ %69, %59 ]
  %61 = phi i16 [ 0, %58 ], [ %66, %59 ]
    #dbg_value(i16 %61, !646, !DIExpression(), !650)
  %62 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %60, i32 2, !dbg !748
  %63 = load i8, ptr %62, align 2, !dbg !748, !tbaa !664
  %64 = icmp ne i8 %63, 0, !dbg !752
  %65 = zext i1 %64 to i16, !dbg !753
  %66 = add i16 %61, %65, !dbg !753
    #dbg_value(i16 %66, !646, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %67 = shl nsw i32 %60, 16, !dbg !754
  %68 = add i32 %67, 65536, !dbg !754
  %69 = ashr exact i32 %68, 16, !dbg !754
  %70 = icmp slt i32 %69, 4, !dbg !755
  br i1 %70, label %59, label %71, !dbg !746, !llvm.loop !756

71:                                               ; preds = %59
    #dbg_value(ptr %0, !106, !DIExpression(), !758)
    #dbg_value(ptr %1, !107, !DIExpression(), !758)
    #dbg_value(i16 %66, !108, !DIExpression(), !758)
  %72 = lshr i16 %66, 8, !dbg !760
  %73 = trunc nuw i16 %72 to i8, !dbg !761
  store i8 %73, ptr %1, align 1, !dbg !762, !tbaa !113
  %74 = trunc i16 %66 to i8, !dbg !763
  br label %583, !dbg !764

75:                                               ; preds = %3, %75
  %76 = phi i32 [ %80, %75 ], [ 0, %3 ]
  %77 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %76, !dbg !765
    #dbg_value(i16 poison, !627, !DIExpression(), !769)
  %78 = shl nsw i32 %76, 16, !dbg !770
  %79 = add i32 %78, 65536, !dbg !770
  %80 = ashr exact i32 %79, 16, !dbg !770
  %81 = icmp slt i32 %80, 4, !dbg !771
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %77, i8 0, i64 6, i1 false), !dbg !772
  br i1 %81, label %75, label %82, !dbg !773, !llvm.loop !774

82:                                               ; preds = %75
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !776, !tbaa !664
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !777, !tbaa !664
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !778, !tbaa !664
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 22), align 2, !dbg !779, !tbaa !664
    #dbg_value(i16 0, !646, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %83, !dbg !780

83:                                               ; preds = %82, %83
  %84 = phi i32 [ 0, %82 ], [ %93, %83 ]
  %85 = phi i16 [ 0, %82 ], [ %90, %83 ]
    #dbg_value(i16 %85, !646, !DIExpression(), !650)
  %86 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %84, i32 2, !dbg !782
  %87 = load i8, ptr %86, align 2, !dbg !782, !tbaa !664
  %88 = icmp ne i8 %87, 0, !dbg !786
  %89 = zext i1 %88 to i16, !dbg !787
  %90 = add i16 %85, %89, !dbg !787
    #dbg_value(i16 %90, !646, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %91 = shl nsw i32 %84, 16, !dbg !788
  %92 = add i32 %91, 65536, !dbg !788
  %93 = ashr exact i32 %92, 16, !dbg !788
  %94 = icmp slt i32 %93, 4, !dbg !789
  br i1 %94, label %83, label %95, !dbg !780, !llvm.loop !790

95:                                               ; preds = %83
    #dbg_value(ptr %0, !106, !DIExpression(), !792)
    #dbg_value(ptr %1, !107, !DIExpression(), !792)
    #dbg_value(i16 %90, !108, !DIExpression(), !792)
  %96 = lshr i16 %90, 8, !dbg !794
  %97 = trunc nuw i16 %96 to i8, !dbg !795
  store i8 %97, ptr %1, align 1, !dbg !796, !tbaa !113
  %98 = trunc i16 %90 to i8, !dbg !797
  br label %583, !dbg !798

99:                                               ; preds = %3, %99
  %100 = phi i32 [ %104, %99 ], [ 0, %3 ]
  %101 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %100, !dbg !799
    #dbg_value(i16 poison, !627, !DIExpression(), !803)
  %102 = shl nsw i32 %100, 16, !dbg !804
  %103 = add i32 %102, 65536, !dbg !804
  %104 = ashr exact i32 %103, 16, !dbg !804
  %105 = icmp slt i32 %104, 4, !dbg !805
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %101, i8 0, i64 6, i1 false), !dbg !806
  br i1 %105, label %99, label %106, !dbg !807, !llvm.loop !808

106:                                              ; preds = %99, %112
  %107 = phi i16 [ %113, %112 ], [ 0, %99 ]
    #dbg_value(i16 %107, !645, !DIExpression(), !650)
  %108 = zext nneg i16 %107 to i32, !dbg !810
  %109 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %108, i32 2, !dbg !813
  %110 = load i8, ptr %109, align 2, !dbg !813, !tbaa !664
  %111 = icmp eq i8 %110, 0, !dbg !816
  br i1 %111, label %115, label %112, !dbg !817

112:                                              ; preds = %106
  %113 = add nuw nsw i16 %107, 1, !dbg !818
    #dbg_value(i16 %113, !645, !DIExpression(), !650)
  %114 = icmp ult i16 %107, 3, !dbg !819
  br i1 %114, label %106, label %119, !dbg !820, !llvm.loop !821

115:                                              ; preds = %106
  %116 = trunc i16 %107 to i8
  %117 = lshr i16 %107, 8
  %118 = trunc nuw nsw i16 %117 to i8
  br label %119, !dbg !823

119:                                              ; preds = %112, %115
  %120 = phi i8 [ %116, %115 ], [ -1, %112 ]
  %121 = phi i8 [ %118, %115 ], [ -1, %112 ]
    #dbg_value(i16 poison, !647, !DIExpression(), !650)
    #dbg_value(ptr %0, !106, !DIExpression(), !825)
    #dbg_value(ptr %1, !107, !DIExpression(), !825)
    #dbg_value(i16 poison, !108, !DIExpression(), !825)
  store i8 %121, ptr %1, align 1, !dbg !823, !tbaa !113
  br label %583, !dbg !826

122:                                              ; preds = %3, %122
  %123 = phi i32 [ %127, %122 ], [ 0, %3 ]
  %124 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %123, !dbg !827
    #dbg_value(i16 poison, !627, !DIExpression(), !831)
  %125 = shl nsw i32 %123, 16, !dbg !832
  %126 = add i32 %125, 65536, !dbg !832
  %127 = ashr exact i32 %126, 16, !dbg !832
  %128 = icmp slt i32 %127, 4, !dbg !833
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %124, i8 0, i64 6, i1 false), !dbg !834
  br i1 %128, label %122, label %129, !dbg !835, !llvm.loop !836

129:                                              ; preds = %122
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !838, !tbaa !664
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !839, !tbaa !664
    #dbg_value(i16 -1, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
  br label %130, !dbg !840

130:                                              ; preds = %129, %136
  %131 = phi i16 [ 0, %129 ], [ %137, %136 ]
    #dbg_value(i16 %131, !645, !DIExpression(), !650)
  %132 = zext nneg i16 %131 to i32, !dbg !842
  %133 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %132, i32 2, !dbg !844
  %134 = load i8, ptr %133, align 2, !dbg !844, !tbaa !664
  %135 = icmp eq i8 %134, 0, !dbg !847
  br i1 %135, label %139, label %136, !dbg !848

136:                                              ; preds = %130
  %137 = add nuw nsw i16 %131, 1, !dbg !849
    #dbg_value(i16 %137, !645, !DIExpression(), !650)
  %138 = icmp ult i16 %131, 3, !dbg !850
  br i1 %138, label %130, label %143, !dbg !840, !llvm.loop !851

139:                                              ; preds = %130
  %140 = trunc i16 %131 to i8
  %141 = lshr i16 %131, 8
  %142 = trunc nuw nsw i16 %141 to i8
  br label %143, !dbg !853

143:                                              ; preds = %136, %139
  %144 = phi i8 [ %140, %139 ], [ -1, %136 ]
  %145 = phi i8 [ %142, %139 ], [ -1, %136 ]
    #dbg_value(i16 poison, !647, !DIExpression(), !650)
    #dbg_value(ptr %0, !106, !DIExpression(), !855)
    #dbg_value(ptr %1, !107, !DIExpression(), !855)
    #dbg_value(i16 poison, !108, !DIExpression(), !855)
  store i8 %145, ptr %1, align 1, !dbg !853, !tbaa !113
  br label %583, !dbg !856

146:                                              ; preds = %3, %146
  %147 = phi i32 [ %151, %146 ], [ 0, %3 ]
  %148 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %147, !dbg !857
    #dbg_value(i16 poison, !627, !DIExpression(), !861)
  %149 = shl nsw i32 %147, 16, !dbg !862
  %150 = add i32 %149, 65536, !dbg !862
  %151 = ashr exact i32 %150, 16, !dbg !862
  %152 = icmp slt i32 %151, 4, !dbg !863
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %148, i8 0, i64 6, i1 false), !dbg !864
  br i1 %152, label %146, label %153, !dbg !865, !llvm.loop !866

153:                                              ; preds = %146
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !868, !tbaa !664
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !869, !tbaa !664
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !870, !tbaa !664
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 22), align 2, !dbg !871, !tbaa !664
    #dbg_value(i16 -1, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
  br label %154, !dbg !872

154:                                              ; preds = %153, %160
  %155 = phi i16 [ 0, %153 ], [ %161, %160 ]
    #dbg_value(i16 %155, !645, !DIExpression(), !650)
  %156 = zext nneg i16 %155 to i32, !dbg !874
  %157 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %156, i32 2, !dbg !876
  %158 = load i8, ptr %157, align 2, !dbg !876, !tbaa !664
  %159 = icmp eq i8 %158, 0, !dbg !879
  br i1 %159, label %163, label %160, !dbg !880

160:                                              ; preds = %154
  %161 = add nuw nsw i16 %155, 1, !dbg !881
    #dbg_value(i16 %161, !645, !DIExpression(), !650)
  %162 = icmp ult i16 %155, 3, !dbg !882
  br i1 %162, label %154, label %167, !dbg !872, !llvm.loop !883

163:                                              ; preds = %154
  %164 = trunc i16 %155 to i8
  %165 = lshr i16 %155, 8
  %166 = trunc nuw nsw i16 %165 to i8
  br label %167, !dbg !885

167:                                              ; preds = %160, %163
  %168 = phi i8 [ %164, %163 ], [ -1, %160 ]
  %169 = phi i8 [ %166, %163 ], [ -1, %160 ]
    #dbg_value(i16 poison, !647, !DIExpression(), !650)
    #dbg_value(ptr %0, !106, !DIExpression(), !887)
    #dbg_value(ptr %1, !107, !DIExpression(), !887)
    #dbg_value(i16 poison, !108, !DIExpression(), !887)
  store i8 %169, ptr %1, align 1, !dbg !885, !tbaa !113
  br label %583, !dbg !888

170:                                              ; preds = %3, %170
  %171 = phi i32 [ %175, %170 ], [ 0, %3 ]
  %172 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %171, !dbg !889
    #dbg_value(i16 poison, !627, !DIExpression(), !893)
  %173 = shl nsw i32 %171, 16, !dbg !894
  %174 = add i32 %173, 65536, !dbg !894
  %175 = ashr exact i32 %174, 16, !dbg !894
  %176 = icmp slt i32 %175, 4, !dbg !895
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %172, i8 0, i64 6, i1 false), !dbg !896
  br i1 %176, label %170, label %177, !dbg !897, !llvm.loop !898

177:                                              ; preds = %170
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !900, !tbaa !664
    #dbg_value(i16 -1, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
  br label %181, !dbg !901

178:                                              ; preds = %181
  %179 = add nuw nsw i16 %182, 1, !dbg !903
    #dbg_value(i16 %179, !645, !DIExpression(), !650)
    #dbg_value(i16 %179, !645, !DIExpression(), !650)
  %180 = icmp ult i16 %182, 3, !dbg !905
  br i1 %180, label %181, label %187, !dbg !901, !llvm.loop !906

181:                                              ; preds = %177, %178
  %182 = phi i16 [ 0, %177 ], [ %179, %178 ]
    #dbg_value(i16 %182, !645, !DIExpression(), !650)
  %183 = zext nneg i16 %182 to i32, !dbg !908
  %184 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %183, i32 2, !dbg !909
  %185 = load i8, ptr %184, align 2, !dbg !909, !tbaa !664
  %186 = icmp eq i8 %185, 0, !dbg !912
    #dbg_value(i16 %182, !645, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !650)
  br i1 %186, label %187, label %178, !dbg !913

187:                                              ; preds = %181, %178
  %188 = phi i32 [ -1, %178 ], [ %183, %181 ], !dbg !914
    #dbg_value(i32 %188, !647, !DIExpression(), !650)
  %189 = icmp sgt i32 %188, -1, !dbg !915
  br i1 %189, label %190, label %195, !dbg !917

190:                                              ; preds = %187
  %191 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %188, !dbg !918
  store i16 100, ptr %191, align 2, !dbg !920, !tbaa !921
  %192 = getelementptr inbounds i8, ptr %191, i32 2, !dbg !922
  store i16 50, ptr %192, align 2, !dbg !923, !tbaa !924
  %193 = getelementptr inbounds i8, ptr %191, i32 4, !dbg !925
  store i8 1, ptr %193, align 2, !dbg !926, !tbaa !664
  %194 = getelementptr inbounds i8, ptr %191, i32 5, !dbg !927
  store i8 2, ptr %194, align 1, !dbg !928, !tbaa !929
  br label %195, !dbg !930

195:                                              ; preds = %190, %187
  %196 = load i16, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !931, !tbaa !921
    #dbg_value(ptr %0, !106, !DIExpression(), !932)
    #dbg_value(ptr %1, !107, !DIExpression(), !932)
    #dbg_value(i16 %196, !108, !DIExpression(), !932)
  %197 = lshr i16 %196, 8, !dbg !934
  %198 = trunc nuw i16 %197 to i8, !dbg !935
  store i8 %198, ptr %1, align 1, !dbg !936, !tbaa !113
  %199 = trunc i16 %196 to i8, !dbg !937
  br label %583, !dbg !938

200:                                              ; preds = %3, %200
  %201 = phi i32 [ %205, %200 ], [ 0, %3 ]
  %202 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %201, !dbg !939
    #dbg_value(i16 poison, !627, !DIExpression(), !943)
  %203 = shl nsw i32 %201, 16, !dbg !944
  %204 = add i32 %203, 65536, !dbg !944
  %205 = ashr exact i32 %204, 16, !dbg !944
  %206 = icmp slt i32 %205, 4, !dbg !945
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %202, i8 0, i64 6, i1 false), !dbg !946
  br i1 %206, label %200, label %207, !dbg !947, !llvm.loop !948

207:                                              ; preds = %200
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !950, !tbaa !664
    #dbg_value(i16 -1, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
  br label %211, !dbg !951

208:                                              ; preds = %211
  %209 = add nuw nsw i16 %212, 1, !dbg !953
    #dbg_value(i16 %209, !645, !DIExpression(), !650)
    #dbg_value(i16 %209, !645, !DIExpression(), !650)
  %210 = icmp ult i16 %212, 3, !dbg !955
  br i1 %210, label %211, label %217, !dbg !951, !llvm.loop !956

211:                                              ; preds = %207, %208
  %212 = phi i16 [ 0, %207 ], [ %209, %208 ]
    #dbg_value(i16 %212, !645, !DIExpression(), !650)
  %213 = zext nneg i16 %212 to i32, !dbg !958
  %214 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %213, i32 2, !dbg !959
  %215 = load i8, ptr %214, align 2, !dbg !959, !tbaa !664
  %216 = icmp eq i8 %215, 0, !dbg !962
    #dbg_value(i16 %212, !645, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !650)
  br i1 %216, label %217, label %208, !dbg !963

217:                                              ; preds = %211, %208
  %218 = phi i32 [ -1, %208 ], [ %213, %211 ], !dbg !964
    #dbg_value(i32 %218, !647, !DIExpression(), !650)
  %219 = icmp sgt i32 %218, -1, !dbg !965
  br i1 %219, label %220, label %225, !dbg !967

220:                                              ; preds = %217
  %221 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %218, !dbg !968
  store i16 100, ptr %221, align 2, !dbg !970, !tbaa !921
  %222 = getelementptr inbounds i8, ptr %221, i32 2, !dbg !971
  store i16 50, ptr %222, align 2, !dbg !972, !tbaa !924
  %223 = getelementptr inbounds i8, ptr %221, i32 4, !dbg !973
  store i8 1, ptr %223, align 2, !dbg !974, !tbaa !664
  %224 = getelementptr inbounds i8, ptr %221, i32 5, !dbg !975
  store i8 2, ptr %224, align 1, !dbg !976, !tbaa !929
  br label %225, !dbg !977

225:                                              ; preds = %220, %217
  %226 = load i8, ptr getelementptr inbounds (i8, ptr @pool, i32 11), align 1, !dbg !978, !tbaa !929
    #dbg_value(ptr %0, !106, !DIExpression(), !979)
    #dbg_value(ptr %1, !107, !DIExpression(), !979)
    #dbg_value(i8 %226, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !979)
  %227 = ashr i8 %226, 7, !dbg !981
  store i8 %227, ptr %1, align 1, !dbg !982, !tbaa !113
  br label %583, !dbg !983

228:                                              ; preds = %3, %228
  %229 = phi i32 [ %233, %228 ], [ 0, %3 ]
  %230 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %229, !dbg !984
    #dbg_value(i16 poison, !627, !DIExpression(), !988)
  %231 = shl nsw i32 %229, 16, !dbg !989
  %232 = add i32 %231, 65536, !dbg !989
  %233 = ashr exact i32 %232, 16, !dbg !989
  %234 = icmp slt i32 %233, 4, !dbg !990
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %230, i8 0, i64 6, i1 false), !dbg !991
  br i1 %234, label %228, label %235, !dbg !992, !llvm.loop !993

235:                                              ; preds = %228
  store i16 10, ptr @pool, align 16, !dbg !995, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !996, !tbaa !664
  store i16 20, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !997, !tbaa !921
  store i8 0, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !998, !tbaa !664
  store i16 30, ptr getelementptr inbounds (i8, ptr @pool, i32 12), align 4, !dbg !999, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !1000, !tbaa !664
  store i16 40, ptr getelementptr inbounds (i8, ptr @pool, i32 18), align 2, !dbg !1001, !tbaa !921
  store i8 0, ptr getelementptr inbounds (i8, ptr @pool, i32 22), align 2, !dbg !1002, !tbaa !664
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %236, !dbg !1003

236:                                              ; preds = %235, %245
  %237 = phi i32 [ 0, %235 ], [ %248, %245 ]
  %238 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %237, !dbg !1005
  %239 = getelementptr inbounds i8, ptr %238, i32 4, !dbg !1009
  %240 = load i8, ptr %239, align 2, !dbg !1009, !tbaa !664
  %241 = icmp eq i8 %240, 0, !dbg !1005
  br i1 %241, label %245, label %242, !dbg !1010

242:                                              ; preds = %236
  %243 = load i16, ptr %238, align 2, !dbg !1011, !tbaa !921
  %244 = add i16 %243, -1, !dbg !1012
  store i16 %244, ptr %238, align 2, !dbg !1013, !tbaa !921
  br label %245, !dbg !1014

245:                                              ; preds = %236, %242
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %246 = shl nsw i32 %237, 16, !dbg !1015
  %247 = add i32 %246, 65536, !dbg !1015
  %248 = ashr exact i32 %247, 16, !dbg !1015
  %249 = icmp slt i32 %248, 4, !dbg !1016
  br i1 %249, label %236, label %250, !dbg !1003, !llvm.loop !1017

250:                                              ; preds = %245
  %251 = load i16, ptr @pool, align 16, !dbg !1019, !tbaa !921
  %252 = load i16, ptr getelementptr inbounds (i8, ptr @pool, i32 12), align 4, !dbg !1020, !tbaa !921
  %253 = add i16 %252, %251, !dbg !1021
    #dbg_value(ptr %0, !106, !DIExpression(), !1022)
    #dbg_value(ptr %1, !107, !DIExpression(), !1022)
    #dbg_value(i16 %253, !108, !DIExpression(), !1022)
  %254 = lshr i16 %253, 8, !dbg !1024
  %255 = trunc nuw i16 %254 to i8, !dbg !1025
  store i8 %255, ptr %1, align 1, !dbg !1026, !tbaa !113
  %256 = trunc i16 %253 to i8, !dbg !1027
  br label %583, !dbg !1028

257:                                              ; preds = %3, %257
  %258 = phi i32 [ %262, %257 ], [ 0, %3 ]
  %259 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %258, !dbg !1029
    #dbg_value(i16 poison, !627, !DIExpression(), !1033)
  %260 = shl nsw i32 %258, 16, !dbg !1034
  %261 = add i32 %260, 65536, !dbg !1034
  %262 = ashr exact i32 %261, 16, !dbg !1034
  %263 = icmp slt i32 %262, 4, !dbg !1035
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %259, i8 0, i64 6, i1 false), !dbg !1036
  br i1 %263, label %257, label %264, !dbg !1037, !llvm.loop !1038

264:                                              ; preds = %257
  store i16 10, ptr @pool, align 16, !dbg !1040, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1041, !tbaa !664
  store i16 20, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1042, !tbaa !921
  store i8 0, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !1043, !tbaa !664
  store i16 30, ptr getelementptr inbounds (i8, ptr @pool, i32 12), align 4, !dbg !1044, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !1045, !tbaa !664
  store i16 40, ptr getelementptr inbounds (i8, ptr @pool, i32 18), align 2, !dbg !1046, !tbaa !921
  store i8 0, ptr getelementptr inbounds (i8, ptr @pool, i32 22), align 2, !dbg !1047, !tbaa !664
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %265, !dbg !1048

265:                                              ; preds = %264, %274
  %266 = phi i32 [ 0, %264 ], [ %277, %274 ]
  %267 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %266, !dbg !1050
  %268 = getelementptr inbounds i8, ptr %267, i32 4, !dbg !1054
  %269 = load i8, ptr %268, align 2, !dbg !1054, !tbaa !664
  %270 = icmp eq i8 %269, 0, !dbg !1050
  br i1 %270, label %274, label %271, !dbg !1055

271:                                              ; preds = %265
  %272 = load i16, ptr %267, align 2, !dbg !1056, !tbaa !921
  %273 = add i16 %272, -1, !dbg !1057
  store i16 %273, ptr %267, align 2, !dbg !1058, !tbaa !921
  br label %274, !dbg !1059

274:                                              ; preds = %265, %271
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %275 = shl nsw i32 %266, 16, !dbg !1060
  %276 = add i32 %275, 65536, !dbg !1060
  %277 = ashr exact i32 %276, 16, !dbg !1060
  %278 = icmp slt i32 %277, 4, !dbg !1061
  br i1 %278, label %265, label %279, !dbg !1048, !llvm.loop !1062

279:                                              ; preds = %274
  %280 = load i16, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1064, !tbaa !921
  %281 = load i16, ptr getelementptr inbounds (i8, ptr @pool, i32 18), align 2, !dbg !1065, !tbaa !921
  %282 = add i16 %281, %280, !dbg !1066
    #dbg_value(ptr %0, !106, !DIExpression(), !1067)
    #dbg_value(ptr %1, !107, !DIExpression(), !1067)
    #dbg_value(i16 %282, !108, !DIExpression(), !1067)
  %283 = lshr i16 %282, 8, !dbg !1069
  %284 = trunc nuw i16 %283 to i8, !dbg !1070
  store i8 %284, ptr %1, align 1, !dbg !1071, !tbaa !113
  %285 = trunc i16 %282 to i8, !dbg !1072
  br label %583, !dbg !1073

286:                                              ; preds = %3, %286
  %287 = phi i32 [ %291, %286 ], [ 0, %3 ]
  %288 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %287, !dbg !1074
    #dbg_value(i16 poison, !627, !DIExpression(), !1078)
  %289 = shl nsw i32 %287, 16, !dbg !1079
  %290 = add i32 %289, 65536, !dbg !1079
  %291 = ashr exact i32 %290, 16, !dbg !1079
  %292 = icmp slt i32 %291, 4, !dbg !1080
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %288, i8 0, i64 6, i1 false), !dbg !1081
  br i1 %292, label %286, label %293, !dbg !1082, !llvm.loop !1083

293:                                              ; preds = %286
  store i16 -5, ptr @pool, align 16, !dbg !1085, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1086, !tbaa !664
  store i16 10, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1087, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !1088, !tbaa !664
  store i16 -2, ptr getelementptr inbounds (i8, ptr @pool, i32 12), align 4, !dbg !1089, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !1090, !tbaa !664
  store i16 20, ptr getelementptr inbounds (i8, ptr @pool, i32 18), align 2, !dbg !1091, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 22), align 2, !dbg !1092, !tbaa !664
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %294, !dbg !1093

294:                                              ; preds = %293, %304
  %295 = phi i32 [ 0, %293 ], [ %307, %304 ]
  %296 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %295, !dbg !1095
  %297 = getelementptr inbounds i8, ptr %296, i32 4, !dbg !1099
  %298 = load i8, ptr %297, align 2, !dbg !1099, !tbaa !664
  %299 = icmp eq i8 %298, 0, !dbg !1095
  br i1 %299, label %304, label %300, !dbg !1100

300:                                              ; preds = %294
  %301 = load i16, ptr %296, align 2, !dbg !1101, !tbaa !921
  %302 = icmp slt i16 %301, 0, !dbg !1103
  br i1 %302, label %303, label %304, !dbg !1104

303:                                              ; preds = %300
  store i8 0, ptr %297, align 2, !dbg !1105, !tbaa !664
  br label %304, !dbg !1107

304:                                              ; preds = %300, %303, %294
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %305 = shl nsw i32 %295, 16, !dbg !1108
  %306 = add i32 %305, 65536, !dbg !1108
  %307 = ashr exact i32 %306, 16, !dbg !1108
  %308 = icmp slt i32 %307, 4, !dbg !1109
  br i1 %308, label %294, label %309, !dbg !1093, !llvm.loop !1110

309:                                              ; preds = %304, %309
  %310 = phi i32 [ %319, %309 ], [ 0, %304 ]
  %311 = phi i16 [ %316, %309 ], [ 0, %304 ]
    #dbg_value(i16 %311, !646, !DIExpression(), !650)
  %312 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %310, i32 2, !dbg !1112
  %313 = load i8, ptr %312, align 2, !dbg !1112, !tbaa !664
  %314 = icmp ne i8 %313, 0, !dbg !1117
  %315 = zext i1 %314 to i16, !dbg !1118
  %316 = add i16 %311, %315, !dbg !1118
    #dbg_value(i16 %316, !646, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %317 = shl nsw i32 %310, 16, !dbg !1119
  %318 = add i32 %317, 65536, !dbg !1119
  %319 = ashr exact i32 %318, 16, !dbg !1119
  %320 = icmp slt i32 %319, 4, !dbg !1120
  br i1 %320, label %309, label %321, !dbg !1121, !llvm.loop !1122

321:                                              ; preds = %309
    #dbg_value(ptr %0, !106, !DIExpression(), !1124)
    #dbg_value(ptr %1, !107, !DIExpression(), !1124)
    #dbg_value(i16 %316, !108, !DIExpression(), !1124)
  %322 = lshr i16 %316, 8, !dbg !1126
  %323 = trunc nuw i16 %322 to i8, !dbg !1127
  store i8 %323, ptr %1, align 1, !dbg !1128, !tbaa !113
  %324 = trunc i16 %316 to i8, !dbg !1129
  br label %583, !dbg !1130

325:                                              ; preds = %3, %325
  %326 = phi i32 [ %330, %325 ], [ 0, %3 ]
  %327 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %326, !dbg !1131
    #dbg_value(i16 poison, !627, !DIExpression(), !1135)
  %328 = shl nsw i32 %326, 16, !dbg !1136
  %329 = add i32 %328, 65536, !dbg !1136
  %330 = ashr exact i32 %329, 16, !dbg !1136
  %331 = icmp slt i32 %330, 4, !dbg !1137
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %327, i8 0, i64 6, i1 false), !dbg !1138
  br i1 %331, label %325, label %332, !dbg !1139, !llvm.loop !1140

332:                                              ; preds = %325
  store i16 10, ptr @pool, align 16, !dbg !1142, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1143, !tbaa !664
  store i16 30, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1144, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !1145, !tbaa !664
  store i16 5, ptr getelementptr inbounds (i8, ptr @pool, i32 12), align 4, !dbg !1146, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !1147, !tbaa !664
  store i16 25, ptr getelementptr inbounds (i8, ptr @pool, i32 18), align 2, !dbg !1148, !tbaa !921
  store i8 0, ptr getelementptr inbounds (i8, ptr @pool, i32 22), align 2, !dbg !1149, !tbaa !664
    #dbg_value(i16 -100, !649, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %333, !dbg !1150

333:                                              ; preds = %332, %343
  %334 = phi i32 [ 0, %332 ], [ %347, %343 ]
  %335 = phi i16 [ -100, %332 ], [ %344, %343 ]
    #dbg_value(i16 %335, !649, !DIExpression(), !650)
  %336 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %334, !dbg !1152
  %337 = getelementptr inbounds i8, ptr %336, i32 4, !dbg !1156
  %338 = load i8, ptr %337, align 2, !dbg !1156, !tbaa !664
  %339 = icmp eq i8 %338, 0, !dbg !1152
  br i1 %339, label %343, label %340, !dbg !1157

340:                                              ; preds = %333
  %341 = load i16, ptr %336, align 2, !dbg !1158, !tbaa !921
  %342 = tail call i16 @llvm.smax.i16(i16 %341, i16 %335), !dbg !1159
  br label %343, !dbg !1159

343:                                              ; preds = %340, %333
  %344 = phi i16 [ %335, %333 ], [ %342, %340 ], !dbg !1160
    #dbg_value(i16 %344, !649, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %345 = shl nsw i32 %334, 16, !dbg !1161
  %346 = add i32 %345, 65536, !dbg !1161
  %347 = ashr exact i32 %346, 16, !dbg !1161
  %348 = icmp slt i32 %347, 4, !dbg !1162
  br i1 %348, label %333, label %349, !dbg !1150, !llvm.loop !1163

349:                                              ; preds = %343
    #dbg_value(ptr %0, !106, !DIExpression(), !1165)
    #dbg_value(ptr %1, !107, !DIExpression(), !1165)
    #dbg_value(i16 %344, !108, !DIExpression(), !1165)
  %350 = lshr i16 %344, 8, !dbg !1167
  %351 = trunc nuw i16 %350 to i8, !dbg !1168
  store i8 %351, ptr %1, align 1, !dbg !1169, !tbaa !113
  %352 = trunc i16 %344 to i8, !dbg !1170
  br label %583, !dbg !1171

353:                                              ; preds = %3, %353
  %354 = phi i32 [ %358, %353 ], [ 0, %3 ]
  %355 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %354, !dbg !1172
    #dbg_value(i16 poison, !627, !DIExpression(), !1176)
  %356 = shl nsw i32 %354, 16, !dbg !1177
  %357 = add i32 %356, 65536, !dbg !1177
  %358 = ashr exact i32 %357, 16, !dbg !1177
  %359 = icmp slt i32 %358, 4, !dbg !1178
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %355, i8 0, i64 6, i1 false), !dbg !1179
  br i1 %359, label %353, label %360, !dbg !1180, !llvm.loop !1181

360:                                              ; preds = %353, %370
  %361 = phi i32 [ %374, %370 ], [ 0, %353 ]
  %362 = phi i16 [ %371, %370 ], [ -100, %353 ]
    #dbg_value(i16 %362, !649, !DIExpression(), !650)
  %363 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %361, !dbg !1183
  %364 = getelementptr inbounds i8, ptr %363, i32 4, !dbg !1188
  %365 = load i8, ptr %364, align 2, !dbg !1188, !tbaa !664
  %366 = icmp eq i8 %365, 0, !dbg !1183
  br i1 %366, label %370, label %367, !dbg !1189

367:                                              ; preds = %360
  %368 = load i16, ptr %363, align 2, !dbg !1190, !tbaa !921
  %369 = tail call i16 @llvm.smax.i16(i16 %368, i16 %362), !dbg !1191
  br label %370, !dbg !1191

370:                                              ; preds = %367, %360
  %371 = phi i16 [ %362, %360 ], [ %369, %367 ], !dbg !1192
    #dbg_value(i16 %371, !649, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %372 = shl nsw i32 %361, 16, !dbg !1193
  %373 = add i32 %372, 65536, !dbg !1193
  %374 = ashr exact i32 %373, 16, !dbg !1193
  %375 = icmp slt i32 %374, 4, !dbg !1194
  br i1 %375, label %360, label %376, !dbg !1195, !llvm.loop !1196

376:                                              ; preds = %370
    #dbg_value(ptr %0, !106, !DIExpression(), !1198)
    #dbg_value(ptr %1, !107, !DIExpression(), !1198)
    #dbg_value(i16 %371, !108, !DIExpression(), !1198)
  %377 = lshr i16 %371, 8, !dbg !1200
  %378 = trunc nuw i16 %377 to i8, !dbg !1201
  store i8 %378, ptr %1, align 1, !dbg !1202, !tbaa !113
  %379 = trunc i16 %371 to i8, !dbg !1203
  br label %583, !dbg !1204

380:                                              ; preds = %3, %380
  %381 = phi i32 [ %385, %380 ], [ 0, %3 ]
  %382 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %381, !dbg !1205
    #dbg_value(i16 poison, !627, !DIExpression(), !1209)
  %383 = shl nsw i32 %381, 16, !dbg !1210
  %384 = add i32 %383, 65536, !dbg !1210
  %385 = ashr exact i32 %384, 16, !dbg !1210
  %386 = icmp slt i32 %385, 4, !dbg !1211
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %382, i8 0, i64 6, i1 false), !dbg !1212
  br i1 %386, label %380, label %387, !dbg !1213, !llvm.loop !1214

387:                                              ; preds = %380
  store i16 10, ptr @pool, align 16, !dbg !1216, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1217, !tbaa !664
  store i16 20, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1218, !tbaa !921
  store i8 0, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !1219, !tbaa !664
  store i16 30, ptr getelementptr inbounds (i8, ptr @pool, i32 12), align 4, !dbg !1220, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !1221, !tbaa !664
  store i16 40, ptr getelementptr inbounds (i8, ptr @pool, i32 18), align 2, !dbg !1222, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 22), align 2, !dbg !1223, !tbaa !664
    #dbg_value(i16 0, !648, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %388, !dbg !1224

388:                                              ; preds = %387, %398
  %389 = phi i32 [ 0, %387 ], [ %402, %398 ]
  %390 = phi i16 [ 0, %387 ], [ %399, %398 ]
    #dbg_value(i16 %390, !648, !DIExpression(), !650)
  %391 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %389, !dbg !1226
  %392 = getelementptr inbounds i8, ptr %391, i32 4, !dbg !1230
  %393 = load i8, ptr %392, align 2, !dbg !1230, !tbaa !664
  %394 = icmp eq i8 %393, 0, !dbg !1226
  br i1 %394, label %398, label %395, !dbg !1231

395:                                              ; preds = %388
  %396 = load i16, ptr %391, align 2, !dbg !1232, !tbaa !921
  %397 = add i16 %396, %390, !dbg !1233
    #dbg_value(i16 %397, !648, !DIExpression(), !650)
  br label %398, !dbg !1234

398:                                              ; preds = %388, %395
  %399 = phi i16 [ %397, %395 ], [ %390, %388 ], !dbg !1235
    #dbg_value(i16 %399, !648, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %400 = shl nsw i32 %389, 16, !dbg !1236
  %401 = add i32 %400, 65536, !dbg !1236
  %402 = ashr exact i32 %401, 16, !dbg !1236
  %403 = icmp slt i32 %402, 4, !dbg !1237
  br i1 %403, label %388, label %404, !dbg !1224, !llvm.loop !1238

404:                                              ; preds = %398
    #dbg_value(ptr %0, !106, !DIExpression(), !1240)
    #dbg_value(ptr %1, !107, !DIExpression(), !1240)
    #dbg_value(i16 %399, !108, !DIExpression(), !1240)
  %405 = lshr i16 %399, 8, !dbg !1242
  %406 = trunc nuw i16 %405 to i8, !dbg !1243
  store i8 %406, ptr %1, align 1, !dbg !1244, !tbaa !113
  %407 = trunc i16 %399 to i8, !dbg !1245
  br label %583, !dbg !1246

408:                                              ; preds = %3, %408
  %409 = phi i32 [ %413, %408 ], [ 0, %3 ]
  %410 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %409, !dbg !1247
    #dbg_value(i16 poison, !627, !DIExpression(), !1251)
  %411 = shl nsw i32 %409, 16, !dbg !1252
  %412 = add i32 %411, 65536, !dbg !1252
  %413 = ashr exact i32 %412, 16, !dbg !1252
  %414 = icmp slt i32 %413, 4, !dbg !1253
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %410, i8 0, i64 6, i1 false), !dbg !1254
  br i1 %414, label %408, label %415, !dbg !1255, !llvm.loop !1256

415:                                              ; preds = %408
  store i16 5, ptr @pool, align 16, !dbg !1258, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 5), align 1, !dbg !1259, !tbaa !929
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1260, !tbaa !664
  store i16 15, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1261, !tbaa !921
  store i8 0, ptr getelementptr inbounds (i8, ptr @pool, i32 11), align 1, !dbg !1262, !tbaa !929
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !1263, !tbaa !664
  store i16 8, ptr getelementptr inbounds (i8, ptr @pool, i32 12), align 4, !dbg !1264, !tbaa !921
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 17), align 1, !dbg !1265, !tbaa !929
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 16), align 16, !dbg !1266, !tbaa !664
    #dbg_value(i16 -1, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
  br label %416, !dbg !1267

416:                                              ; preds = %415, %426
  %417 = phi i32 [ 0, %415 ], [ %427, %426 ]
    #dbg_value(i32 %417, !645, !DIExpression(), !650)
  %418 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %417, !dbg !1269
  %419 = getelementptr inbounds i8, ptr %418, i32 4, !dbg !1273
  %420 = load i8, ptr %419, align 2, !dbg !1273, !tbaa !664
  %421 = icmp eq i8 %420, 0, !dbg !1269
  br i1 %421, label %426, label %422, !dbg !1274

422:                                              ; preds = %416
  %423 = getelementptr inbounds i8, ptr %418, i32 5, !dbg !1275
  %424 = load i8, ptr %423, align 1, !dbg !1275, !tbaa !929
  %425 = icmp eq i8 %424, 0, !dbg !1277
  br i1 %425, label %429, label %426, !dbg !1278

426:                                              ; preds = %422, %416
  %427 = add nuw nsw i32 %417, 1, !dbg !1279
    #dbg_value(i32 %427, !645, !DIExpression(), !650)
  %428 = icmp eq i32 %427, 4, !dbg !1280
  br i1 %428, label %433, label %416, !dbg !1267, !llvm.loop !1281

429:                                              ; preds = %422
  %430 = trunc i32 %417 to i8
  %431 = lshr i32 %417, 8
  %432 = trunc i32 %431 to i8
  br label %433, !dbg !1283

433:                                              ; preds = %426, %429
  %434 = phi i8 [ %430, %429 ], [ -1, %426 ]
  %435 = phi i8 [ %432, %429 ], [ -1, %426 ]
    #dbg_value(i16 poison, !647, !DIExpression(), !650)
    #dbg_value(ptr %0, !106, !DIExpression(), !1285)
    #dbg_value(ptr %1, !107, !DIExpression(), !1285)
    #dbg_value(i16 poison, !108, !DIExpression(), !1285)
  store i8 %435, ptr %1, align 1, !dbg !1283, !tbaa !113
  br label %583, !dbg !1286

436:                                              ; preds = %3, %436
  %437 = phi i32 [ %441, %436 ], [ 0, %3 ]
  %438 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %437, !dbg !1287
    #dbg_value(i16 poison, !627, !DIExpression(), !1291)
  %439 = shl nsw i32 %437, 16, !dbg !1292
  %440 = add i32 %439, 65536, !dbg !1292
  %441 = ashr exact i32 %440, 16, !dbg !1292
  %442 = icmp slt i32 %441, 4, !dbg !1293
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %438, i8 0, i64 6, i1 false), !dbg !1294
  br i1 %442, label %436, label %443, !dbg !1295, !llvm.loop !1296

443:                                              ; preds = %436
  store i16 100, ptr @pool, align 16, !dbg !1298, !tbaa !921
  store i16 50, ptr getelementptr inbounds (i8, ptr @pool, i32 2), align 2, !dbg !1299, !tbaa !924
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1300, !tbaa !664
  store i16 200, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1301, !tbaa !921
  store i16 60, ptr getelementptr inbounds (i8, ptr @pool, i32 8), align 8, !dbg !1302, !tbaa !924
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !1303, !tbaa !664
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %444, !dbg !1304

444:                                              ; preds = %443, %456
  %445 = phi i32 [ 0, %443 ], [ %459, %456 ]
  %446 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %445, !dbg !1306
  %447 = getelementptr inbounds i8, ptr %446, i32 4, !dbg !1310
  %448 = load i8, ptr %447, align 2, !dbg !1310, !tbaa !664
  %449 = icmp eq i8 %448, 0, !dbg !1306
  br i1 %449, label %456, label %450, !dbg !1311

450:                                              ; preds = %444
  %451 = load i16, ptr %446, align 2, !dbg !1312, !tbaa !921
  %452 = add i16 %451, -5, !dbg !1313
  store i16 %452, ptr %446, align 2, !dbg !1314, !tbaa !921
  %453 = getelementptr inbounds i8, ptr %446, i32 2, !dbg !1315
  %454 = load i16, ptr %453, align 2, !dbg !1315, !tbaa !924
  %455 = add i16 %454, 2, !dbg !1316
  store i16 %455, ptr %453, align 2, !dbg !1317, !tbaa !924
  br label %456, !dbg !1318

456:                                              ; preds = %444, %450
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %457 = shl nsw i32 %445, 16, !dbg !1319
  %458 = add i32 %457, 65536, !dbg !1319
  %459 = ashr exact i32 %458, 16, !dbg !1319
  %460 = icmp slt i32 %459, 4, !dbg !1320
  br i1 %460, label %444, label %461, !dbg !1304, !llvm.loop !1321

461:                                              ; preds = %456
  %462 = load i16, ptr @pool, align 16, !dbg !1323, !tbaa !921
  %463 = load i16, ptr getelementptr inbounds (i8, ptr @pool, i32 2), align 2, !dbg !1324, !tbaa !924
  %464 = add i16 %463, %462, !dbg !1325
    #dbg_value(ptr %0, !106, !DIExpression(), !1326)
    #dbg_value(ptr %1, !107, !DIExpression(), !1326)
    #dbg_value(i16 %464, !108, !DIExpression(), !1326)
  %465 = lshr i16 %464, 8, !dbg !1328
  %466 = trunc nuw i16 %465 to i8, !dbg !1329
  store i8 %466, ptr %1, align 1, !dbg !1330, !tbaa !113
  %467 = trunc i16 %464 to i8, !dbg !1331
  br label %583, !dbg !1332

468:                                              ; preds = %3, %468
  %469 = phi i32 [ %473, %468 ], [ 0, %3 ]
  %470 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %469, !dbg !1333
    #dbg_value(i16 poison, !627, !DIExpression(), !1337)
  %471 = shl nsw i32 %469, 16, !dbg !1338
  %472 = add i32 %471, 65536, !dbg !1338
  %473 = ashr exact i32 %472, 16, !dbg !1338
  %474 = icmp slt i32 %473, 4, !dbg !1339
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %470, i8 0, i64 6, i1 false), !dbg !1340
  br i1 %474, label %468, label %475, !dbg !1341, !llvm.loop !1342

475:                                              ; preds = %468
  store i16 10, ptr @pool, align 16, !dbg !1344, !tbaa !921
  store i16 20, ptr getelementptr inbounds (i8, ptr @pool, i32 2), align 2, !dbg !1345, !tbaa !924
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1346, !tbaa !664
  store i16 50, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1347, !tbaa !921
  store i16 60, ptr getelementptr inbounds (i8, ptr @pool, i32 8), align 8, !dbg !1348, !tbaa !924
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !1349, !tbaa !664
    #dbg_value(i16 0, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %476, !dbg !1350

476:                                              ; preds = %475, %489
  %477 = phi i32 [ 0, %475 ], [ %492, %489 ]
  %478 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %477, !dbg !1352
  %479 = getelementptr inbounds i8, ptr %478, i32 4, !dbg !1356
  %480 = load i8, ptr %479, align 2, !dbg !1356, !tbaa !664
  %481 = icmp eq i8 %480, 0, !dbg !1352
  br i1 %481, label %489, label %482, !dbg !1357

482:                                              ; preds = %476
  %483 = load i16, ptr %478, align 2, !dbg !1358, !tbaa !921
  %484 = icmp eq i16 %483, 10, !dbg !1360
  br i1 %484, label %485, label %489, !dbg !1361

485:                                              ; preds = %482
  %486 = getelementptr inbounds i8, ptr %478, i32 2, !dbg !1362
  %487 = load i16, ptr %486, align 2, !dbg !1362, !tbaa !924
  %488 = icmp eq i16 %487, 20, !dbg !1363
  br i1 %488, label %494, label %489, !dbg !1364

489:                                              ; preds = %482, %485, %476
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %490 = shl nsw i32 %477, 16, !dbg !1365
  %491 = add i32 %490, 65536, !dbg !1365
  %492 = ashr exact i32 %491, 16, !dbg !1365
  %493 = icmp slt i32 %492, 4, !dbg !1366
  br i1 %493, label %476, label %494, !dbg !1350, !llvm.loop !1367

494:                                              ; preds = %485, %489
  %495 = phi i8 [ 0, %489 ], [ 1, %485 ]
    #dbg_value(i16 poison, !647, !DIExpression(), !650)
    #dbg_value(ptr %0, !106, !DIExpression(), !1369)
    #dbg_value(ptr %1, !107, !DIExpression(), !1369)
    #dbg_value(i16 poison, !108, !DIExpression(), !1369)
  store i8 0, ptr %1, align 1, !dbg !1371, !tbaa !113
  br label %583, !dbg !1372

496:                                              ; preds = %3, %496
  %497 = phi i32 [ %501, %496 ], [ 0, %3 ]
  %498 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %497, !dbg !1373
    #dbg_value(i16 poison, !627, !DIExpression(), !1377)
  %499 = shl nsw i32 %497, 16, !dbg !1378
  %500 = add i32 %499, 65536, !dbg !1378
  %501 = ashr exact i32 %500, 16, !dbg !1378
  %502 = icmp slt i32 %501, 4, !dbg !1379
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %498, i8 0, i64 6, i1 false), !dbg !1380
  br i1 %502, label %496, label %503, !dbg !1381, !llvm.loop !1382

503:                                              ; preds = %496
  store i16 10, ptr @pool, align 16, !dbg !1384, !tbaa !921
  store i16 20, ptr getelementptr inbounds (i8, ptr @pool, i32 2), align 2, !dbg !1385, !tbaa !924
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1386, !tbaa !664
  store i16 50, ptr getelementptr inbounds (i8, ptr @pool, i32 6), align 2, !dbg !1387, !tbaa !921
  store i16 60, ptr getelementptr inbounds (i8, ptr @pool, i32 8), align 8, !dbg !1388, !tbaa !924
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 10), align 2, !dbg !1389, !tbaa !664
    #dbg_value(i16 0, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %504, !dbg !1390

504:                                              ; preds = %503, %517
  %505 = phi i32 [ 0, %503 ], [ %520, %517 ]
  %506 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %505, !dbg !1392
  %507 = getelementptr inbounds i8, ptr %506, i32 4, !dbg !1396
  %508 = load i8, ptr %507, align 2, !dbg !1396, !tbaa !664
  %509 = icmp eq i8 %508, 0, !dbg !1392
  br i1 %509, label %517, label %510, !dbg !1397

510:                                              ; preds = %504
  %511 = load i16, ptr %506, align 2, !dbg !1398, !tbaa !921
  %512 = icmp eq i16 %511, 30, !dbg !1400
  br i1 %512, label %513, label %517, !dbg !1401

513:                                              ; preds = %510
  %514 = getelementptr inbounds i8, ptr %506, i32 2, !dbg !1402
  %515 = load i16, ptr %514, align 2, !dbg !1402, !tbaa !924
  %516 = icmp eq i16 %515, 40, !dbg !1403
  br i1 %516, label %522, label %517, !dbg !1404

517:                                              ; preds = %510, %513, %504
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %518 = shl nsw i32 %505, 16, !dbg !1405
  %519 = add i32 %518, 65536, !dbg !1405
  %520 = ashr exact i32 %519, 16, !dbg !1405
  %521 = icmp slt i32 %520, 4, !dbg !1406
  br i1 %521, label %504, label %522, !dbg !1390, !llvm.loop !1407

522:                                              ; preds = %513, %517
  %523 = phi i8 [ 0, %517 ], [ 1, %513 ]
    #dbg_value(i16 poison, !647, !DIExpression(), !650)
    #dbg_value(ptr %0, !106, !DIExpression(), !1409)
    #dbg_value(ptr %1, !107, !DIExpression(), !1409)
    #dbg_value(i16 poison, !108, !DIExpression(), !1409)
  store i8 0, ptr %1, align 1, !dbg !1411, !tbaa !113
  br label %583, !dbg !1412

524:                                              ; preds = %3, %524
  %525 = phi i32 [ %529, %524 ], [ 0, %3 ]
  %526 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %525, !dbg !1413
    #dbg_value(i16 poison, !627, !DIExpression(), !1417)
  %527 = shl nsw i32 %525, 16, !dbg !1418
  %528 = add i32 %527, 65536, !dbg !1418
  %529 = ashr exact i32 %528, 16, !dbg !1418
  %530 = icmp slt i32 %529, 4, !dbg !1419
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %526, i8 0, i64 6, i1 false), !dbg !1420
  br i1 %530, label %524, label %531, !dbg !1421, !llvm.loop !1422

531:                                              ; preds = %524
  store i16 10, ptr @pool, align 16, !dbg !1424, !tbaa !921
  store i16 20, ptr getelementptr inbounds (i8, ptr @pool, i32 2), align 2, !dbg !1425, !tbaa !924
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1426, !tbaa !664
    #dbg_value(i16 0, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %532, !dbg !1427

532:                                              ; preds = %531, %547
  %533 = phi i32 [ 0, %531 ], [ %550, %547 ]
  %534 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %533, !dbg !1429
  %535 = getelementptr inbounds i8, ptr %534, i32 4, !dbg !1433
  %536 = load i8, ptr %535, align 2, !dbg !1433, !tbaa !664
  %537 = icmp eq i8 %536, 0, !dbg !1429
  br i1 %537, label %547, label %538, !dbg !1434

538:                                              ; preds = %532
  %539 = load i16, ptr %534, align 2, !dbg !1435, !tbaa !921
  %540 = add i16 %539, -5, !dbg !1437
  %541 = icmp ult i16 %540, 11, !dbg !1437
  br i1 %541, label %542, label %547, !dbg !1437

542:                                              ; preds = %538
  %543 = getelementptr inbounds i8, ptr %534, i32 2, !dbg !1438
  %544 = load i16, ptr %543, align 2, !dbg !1438, !tbaa !924
  %545 = add i16 %544, -15, !dbg !1439
  %546 = icmp ult i16 %545, 11, !dbg !1439
  br i1 %546, label %552, label %547, !dbg !1439

547:                                              ; preds = %538, %542, %532
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %548 = shl nsw i32 %533, 16, !dbg !1440
  %549 = add i32 %548, 65536, !dbg !1440
  %550 = ashr exact i32 %549, 16, !dbg !1440
  %551 = icmp slt i32 %550, 4, !dbg !1441
  br i1 %551, label %532, label %552, !dbg !1427, !llvm.loop !1442

552:                                              ; preds = %542, %547
  %553 = phi i8 [ 0, %547 ], [ 1, %542 ]
    #dbg_value(i16 poison, !647, !DIExpression(), !650)
    #dbg_value(ptr %0, !106, !DIExpression(), !1444)
    #dbg_value(ptr %1, !107, !DIExpression(), !1444)
    #dbg_value(i16 poison, !108, !DIExpression(), !1444)
  store i8 0, ptr %1, align 1, !dbg !1446, !tbaa !113
  br label %583, !dbg !1447

554:                                              ; preds = %3, %554
  %555 = phi i32 [ %559, %554 ], [ 0, %3 ]
  %556 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %555, !dbg !1448
    #dbg_value(i16 poison, !627, !DIExpression(), !1452)
  %557 = shl nsw i32 %555, 16, !dbg !1453
  %558 = add i32 %557, 65536, !dbg !1453
  %559 = ashr exact i32 %558, 16, !dbg !1453
  %560 = icmp slt i32 %559, 4, !dbg !1454
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 2 dereferenceable(6) %556, i8 0, i64 6, i1 false), !dbg !1455
  br i1 %560, label %554, label %561, !dbg !1456, !llvm.loop !1457

561:                                              ; preds = %554
  store i16 10, ptr @pool, align 16, !dbg !1459, !tbaa !921
  store i16 20, ptr getelementptr inbounds (i8, ptr @pool, i32 2), align 2, !dbg !1460, !tbaa !924
  store i8 1, ptr getelementptr inbounds (i8, ptr @pool, i32 4), align 4, !dbg !1461, !tbaa !664
    #dbg_value(i16 0, !647, !DIExpression(), !650)
    #dbg_value(i16 0, !645, !DIExpression(), !650)
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  br label %562, !dbg !1462

562:                                              ; preds = %561, %575
  %563 = phi i32 [ 0, %561 ], [ %578, %575 ]
  %564 = getelementptr inbounds [4 x %struct.pool_obj_t], ptr @pool, i32 0, i32 %563, !dbg !1464
  %565 = getelementptr inbounds i8, ptr %564, i32 4, !dbg !1468
  %566 = load i8, ptr %565, align 2, !dbg !1468, !tbaa !664
  %567 = icmp eq i8 %566, 0, !dbg !1464
  br i1 %567, label %575, label %568, !dbg !1469

568:                                              ; preds = %562
  %569 = load i16, ptr %564, align 2, !dbg !1470, !tbaa !921
  %570 = icmp ult i16 %569, 6
  br i1 %570, label %571, label %575, !dbg !1472

571:                                              ; preds = %568
  %572 = getelementptr inbounds i8, ptr %564, i32 2, !dbg !1473
  %573 = load i16, ptr %572, align 2, !dbg !1473, !tbaa !924
  %574 = icmp ult i16 %573, 6
  br i1 %574, label %580, label %575, !dbg !1474

575:                                              ; preds = %568, %571, %562
    #dbg_value(i16 poison, !645, !DIExpression(), !650)
  %576 = shl nsw i32 %563, 16, !dbg !1475
  %577 = add i32 %576, 65536, !dbg !1475
  %578 = ashr exact i32 %577, 16, !dbg !1475
  %579 = icmp slt i32 %578, 4, !dbg !1476
  br i1 %579, label %562, label %580, !dbg !1462, !llvm.loop !1477

580:                                              ; preds = %571, %575
  %581 = phi i8 [ 0, %575 ], [ 1, %571 ]
    #dbg_value(i16 poison, !647, !DIExpression(), !650)
    #dbg_value(ptr %0, !106, !DIExpression(), !1479)
    #dbg_value(ptr %1, !107, !DIExpression(), !1479)
    #dbg_value(i16 poison, !108, !DIExpression(), !1479)
  store i8 0, ptr %1, align 1, !dbg !1481, !tbaa !113
  br label %583, !dbg !1482

582:                                              ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !1483)
    #dbg_value(ptr %1, !107, !DIExpression(), !1483)
    #dbg_value(i16 -1, !108, !DIExpression(), !1483)
  store i8 -1, ptr %1, align 1, !dbg !1485, !tbaa !113
  br label %583, !dbg !1486

583:                                              ; preds = %582, %580, %552, %522, %494, %461, %433, %404, %376, %349, %321, %279, %250, %225, %195, %167, %143, %119, %95, %71, %47, %27, %19, %11
  %584 = phi i8 [ -1, %582 ], [ %581, %580 ], [ %553, %552 ], [ %523, %522 ], [ %495, %494 ], [ %467, %461 ], [ %434, %433 ], [ %407, %404 ], [ %379, %376 ], [ %352, %349 ], [ %324, %321 ], [ %285, %279 ], [ %256, %250 ], [ %226, %225 ], [ %199, %195 ], [ %168, %167 ], [ %144, %143 ], [ %120, %119 ], [ %98, %95 ], [ %74, %71 ], [ %50, %47 ], [ 0, %27 ], [ 1, %19 ], [ 1, %11 ]
  %585 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !1487
  store i8 %584, ptr %585, align 1, !dbg !1488, !tbaa !113
  %586 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !1489
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !1490
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !1491
  ret void, !dbg !1486
}

; Function Attrs: nofree norecurse nosync nounwind memory(read, argmem: none, inaccessiblemem: none)
define hidden signext i16 @render_checksum() local_unnamed_addr #3 !dbg !1492 {
    #dbg_value(i16 0, !1495, !DIExpression(), !1496)
    #dbg_value(i16 0, !1494, !DIExpression(), !1496)
    #dbg_value(i16 poison, !1494, !DIExpression(), !1496)
  br label %1, !dbg !1497

1:                                                ; preds = %0, %1
  %2 = phi i32 [ 0, %0 ], [ %10, %1 ]
  %3 = phi i16 [ 0, %0 ], [ %7, %1 ]
    #dbg_value(i16 %3, !1495, !DIExpression(), !1496)
  %4 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %2, !dbg !1499
  %5 = load i8, ptr %4, align 1, !dbg !1499, !tbaa !113
  %6 = zext i8 %5 to i16, !dbg !1499
  %7 = add i16 %3, %6, !dbg !1502
    #dbg_value(i16 %7, !1495, !DIExpression(), !1496)
    #dbg_value(i16 poison, !1494, !DIExpression(), !1496)
  %8 = shl nsw i32 %2, 16, !dbg !1503
  %9 = add i32 %8, 65536, !dbg !1503
  %10 = ashr exact i32 %9, 16, !dbg !1503
  %11 = icmp slt i32 %10, 32, !dbg !1504
  br i1 %11, label %1, label %12, !dbg !1497, !llvm.loop !1505

12:                                               ; preds = %1
  ret i16 %7, !dbg !1507
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden void @render_setPixel(i16 noundef signext %0, i16 noundef signext %1, i8 noundef signext %2) local_unnamed_addr #5 !dbg !1508 {
    #dbg_value(i16 %0, !1512, !DIExpression(), !1517)
    #dbg_value(i16 %1, !1513, !DIExpression(), !1517)
    #dbg_value(i8 %2, !1514, !DIExpression(), !1517)
  %4 = icmp ugt i16 %0, 31, !dbg !1518
  %5 = icmp ugt i16 %1, 7, !dbg !1518
  %6 = or i1 %4, %5, !dbg !1518
  br i1 %6, label %22, label %7, !dbg !1518

7:                                                ; preds = %3
  %8 = shl nuw nsw i16 %1, 2, !dbg !1520
  %9 = lshr i16 %0, 3, !dbg !1521
  %10 = or disjoint i16 %8, %9, !dbg !1522
    #dbg_value(i16 %10, !1515, !DIExpression(), !1517)
  %11 = trunc nuw i16 %0 to i8, !dbg !1523
  %12 = and i8 %11, 7, !dbg !1523
  %13 = lshr exact i8 -128, %12, !dbg !1524
    #dbg_value(i8 %13, !1516, !DIExpression(), !1517)
  %14 = icmp eq i8 %2, 0, !dbg !1525
  %15 = zext nneg i16 %10 to i32, !dbg !1527
  %16 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %15, !dbg !1527
  %17 = load i8, ptr %16, align 1, !dbg !1527, !tbaa !113
  %18 = or i8 %17, %13, !dbg !1528
  %19 = xor i8 %13, -1, !dbg !1528
  %20 = and i8 %17, %19, !dbg !1528
  %21 = select i1 %14, i8 %20, i8 %18, !dbg !1528
  store i8 %21, ptr %16, align 1, !dbg !1527, !tbaa !113
  br label %22, !dbg !1529

22:                                               ; preds = %7, %3
  ret void, !dbg !1529
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden void @draw_sprite(i16 noundef signext %0, i16 noundef signext %1, i16 noundef signext %2) local_unnamed_addr #6 !dbg !1530 {
    #dbg_value(i16 %0, !1534, !DIExpression(), !1544)
    #dbg_value(i16 %1, !1535, !DIExpression(), !1544)
    #dbg_value(i16 %2, !1536, !DIExpression(), !1544)
    #dbg_value(i16 %0, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1544)
    #dbg_value(i16 0, !1537, !DIExpression(), !1544)
  %4 = sext i16 %2 to i32
    #dbg_value(i16 poison, !1537, !DIExpression(), !1544)
  %5 = icmp sgt i16 %2, 0, !dbg !1545
  br i1 %5, label %6, label %63, !dbg !1548

6:                                                ; preds = %3
  %7 = and i16 %0, 7, !dbg !1549
  %8 = sext i16 %1 to i32
  %9 = ashr i16 %0, 3
  %10 = icmp ult i16 %7, 6
  %11 = add nuw nsw i16 %7, 251
  %12 = and i16 %11, 255
  %13 = zext nneg i16 %12 to i32
  %14 = sub nsw i32 8, %13
  %15 = sub nsw i16 5, %7
  %16 = and i16 %15, 255
  %17 = zext nneg i16 %16 to i32
  br label %18, !dbg !1548

18:                                               ; preds = %6, %58
  %19 = phi i32 [ 0, %6 ], [ %61, %58 ]
  %20 = add nsw i32 %19, %8, !dbg !1550
  %21 = icmp ugt i32 %20, 7, !dbg !1553
  br i1 %21, label %58, label %22, !dbg !1553

22:                                               ; preds = %18
  %23 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %19, !dbg !1554
  %24 = load i8, ptr %23, align 1, !dbg !1554, !tbaa !113
    #dbg_value(i8 %24, !1539, !DIExpression(), !1544)
  %25 = trunc nuw i32 %20 to i16, !dbg !1555
  %26 = shl nuw nsw i16 %25, 2, !dbg !1555
  %27 = add nsw i16 %26, %9, !dbg !1555
    #dbg_value(i16 %27, !1538, !DIExpression(), !1544)
  br i1 %10, label %28, label %35, !dbg !1556

28:                                               ; preds = %22
    #dbg_value(!DIArgList(i8 5, i16 %7), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1544)
    #dbg_value(!DIArgList(i8 %24, i16 5, i16 %7), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
  %29 = icmp ult i16 %27, 32, !dbg !1557
  br i1 %29, label %30, label %58, !dbg !1557

30:                                               ; preds = %28
  %31 = zext nneg i16 %27 to i32, !dbg !1561
  %32 = and i8 %24, 7, !dbg !1562
    #dbg_value(!DIArgList(i8 %32, i16 5, i16 %7), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
  %33 = zext nneg i8 %32 to i32, !dbg !1562
    #dbg_value(!DIArgList(i32 %33, i16 5, i16 %7), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
    #dbg_value(!DIArgList(i32 %33, i16 %15), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
    #dbg_value(!DIArgList(i32 %33, i16 %16), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
    #dbg_value(!DIArgList(i32 %33, i32 %17), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
  %34 = shl i32 %33, %17, !dbg !1563
    #dbg_value(i32 %34, !1542, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
  br label %51, !dbg !1564

35:                                               ; preds = %22
    #dbg_value(i16 %7, !1541, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !1544)
  %36 = and i8 %24, 7, !dbg !1566
  %37 = zext nneg i8 %36 to i32, !dbg !1566
    #dbg_value(!DIArgList(i32 %37, i32 %13), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
  %38 = shl nuw nsw i32 %37, %14, !dbg !1568
    #dbg_value(i32 %38, !1543, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
  %39 = sext i16 %27 to i32, !dbg !1569
  %40 = icmp ult i16 %27, 32, !dbg !1571
  br i1 %40, label %41, label %47, !dbg !1571

41:                                               ; preds = %35
  %42 = lshr i32 %37, %13, !dbg !1572
    #dbg_value(i32 %42, !1542, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1544)
  %43 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %39, !dbg !1573
  %44 = load i8, ptr %43, align 1, !dbg !1573, !tbaa !113
  %45 = trunc nuw nsw i32 %42 to i8, !dbg !1575
  %46 = or i8 %44, %45, !dbg !1575
  store i8 %46, ptr %43, align 1, !dbg !1576, !tbaa !113
  br label %47, !dbg !1577

47:                                               ; preds = %41, %35
  %48 = icmp slt i16 %27, 31, !dbg !1578
  br i1 %48, label %49, label %58, !dbg !1580

49:                                               ; preds = %47
  %50 = add nsw i32 %39, 1, !dbg !1581
  br label %51, !dbg !1582

51:                                               ; preds = %49, %30
  %52 = phi i32 [ %31, %30 ], [ %50, %49 ]
  %53 = phi i32 [ %34, %30 ], [ %38, %49 ]
  %54 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %52, !dbg !1584
  %55 = load i8, ptr %54, align 1, !dbg !1584, !tbaa !113
  %56 = trunc i32 %53 to i8, !dbg !1584
  %57 = or i8 %55, %56, !dbg !1584
  store i8 %57, ptr %54, align 1, !dbg !1584, !tbaa !113
  br label %58, !dbg !1585

58:                                               ; preds = %51, %28, %47, %18
    #dbg_value(i16 poison, !1537, !DIExpression(), !1544)
  %59 = shl nsw i32 %19, 16, !dbg !1585
  %60 = add i32 %59, 65536, !dbg !1585
  %61 = ashr exact i32 %60, 16, !dbg !1585
  %62 = icmp slt i32 %61, %4, !dbg !1545
  br i1 %62, label %18, label %63, !dbg !1548, !llvm.loop !1586

63:                                               ; preds = %58, %3
  ret void, !dbg !1588
}

; Function Attrs: nounwind
define hidden void @test_rendering(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !1589 {
    #dbg_value(ptr %0, !1591, !DIExpression(), !1609)
    #dbg_value(ptr %1, !1592, !DIExpression(), !1609)
    #dbg_value(i8 %2, !1593, !DIExpression(), !1609)
  switch i8 %2, label %525 [
    i8 0, label %4
    i8 1, label %21
    i8 2, label %25
    i8 3, label %29
    i8 4, label %33
    i8 5, label %53
    i8 6, label %73
    i8 7, label %106
    i8 8, label %127
    i8 9, label %147
    i8 10, label %173
    i8 11, label %199
    i8 12, label %225
    i8 13, label %251
    i8 14, label %303
    i8 15, label %324
    i8 16, label %343
    i8 17, label %362
    i8 18, label %382
    i8 19, label %432
    i8 20, label %483
    i8 21, label %504
  ], !dbg !1610

4:                                                ; preds = %3
  %5 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1611
    #dbg_value(i16 0, !1495, !DIExpression(), !1614)
    #dbg_value(i16 0, !1494, !DIExpression(), !1614)
    #dbg_value(i16 poison, !1494, !DIExpression(), !1614)
  br label %6, !dbg !1616

6:                                                ; preds = %6, %4
  %7 = phi i32 [ 0, %4 ], [ %15, %6 ]
  %8 = phi i16 [ 0, %4 ], [ %12, %6 ]
    #dbg_value(i16 %8, !1495, !DIExpression(), !1614)
  %9 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %7, !dbg !1617
  %10 = load i8, ptr %9, align 1, !dbg !1617, !tbaa !113
  %11 = zext i8 %10 to i16, !dbg !1617
  %12 = add i16 %8, %11, !dbg !1618
    #dbg_value(i16 %12, !1495, !DIExpression(), !1614)
    #dbg_value(i16 poison, !1494, !DIExpression(), !1614)
  %13 = shl nsw i32 %7, 16, !dbg !1619
  %14 = add i32 %13, 65536, !dbg !1619
  %15 = ashr exact i32 %14, 16, !dbg !1619
  %16 = icmp slt i32 %15, 32, !dbg !1620
  br i1 %16, label %6, label %17, !dbg !1616, !llvm.loop !1621

17:                                               ; preds = %6
    #dbg_value(ptr %0, !106, !DIExpression(), !1623)
    #dbg_value(ptr %1, !107, !DIExpression(), !1623)
    #dbg_value(i16 %12, !108, !DIExpression(), !1623)
  %18 = lshr i16 %12, 8, !dbg !1625
  %19 = trunc nuw i16 %18 to i8, !dbg !1626
  store i8 %19, ptr %1, align 1, !dbg !1627, !tbaa !113
  %20 = trunc i16 %12 to i8, !dbg !1628
  br label %526, !dbg !1629

21:                                               ; preds = %3
  %22 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1630
    #dbg_value(i16 0, !1512, !DIExpression(), !1633)
    #dbg_value(i16 0, !1513, !DIExpression(), !1633)
    #dbg_value(i8 1, !1514, !DIExpression(), !1633)
    #dbg_value(i16 0, !1515, !DIExpression(), !1633)
    #dbg_value(i8 -128, !1516, !DIExpression(), !1633)
  %23 = load i8, ptr @shared_fb, align 16, !dbg !1635, !tbaa !113
  %24 = or i8 %23, -128, !dbg !1636
  store i8 %24, ptr @shared_fb, align 16, !dbg !1637, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1638)
    #dbg_value(ptr %1, !107, !DIExpression(), !1638)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1638)
  store i8 0, ptr %1, align 1, !dbg !1640, !tbaa !113
  br label %526, !dbg !1641

25:                                               ; preds = %3
  %26 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1642
    #dbg_value(i16 7, !1512, !DIExpression(), !1645)
    #dbg_value(i16 0, !1513, !DIExpression(), !1645)
    #dbg_value(i8 1, !1514, !DIExpression(), !1645)
    #dbg_value(i16 0, !1515, !DIExpression(), !1645)
    #dbg_value(i8 1, !1516, !DIExpression(), !1645)
  %27 = load i8, ptr @shared_fb, align 16, !dbg !1647, !tbaa !113
  %28 = or i8 %27, 1, !dbg !1648
  store i8 %28, ptr @shared_fb, align 16, !dbg !1649, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1650)
    #dbg_value(ptr %1, !107, !DIExpression(), !1650)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1650)
  store i8 0, ptr %1, align 1, !dbg !1652, !tbaa !113
  br label %526, !dbg !1653

29:                                               ; preds = %3
  %30 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1654
    #dbg_value(i16 8, !1512, !DIExpression(), !1657)
    #dbg_value(i16 0, !1513, !DIExpression(), !1657)
    #dbg_value(i8 1, !1514, !DIExpression(), !1657)
    #dbg_value(i16 1, !1515, !DIExpression(), !1657)
    #dbg_value(i8 -128, !1516, !DIExpression(), !1657)
  %31 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !1659, !tbaa !113
  %32 = or i8 %31, -128, !dbg !1660
  store i8 %32, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !1661, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1662)
    #dbg_value(ptr %1, !107, !DIExpression(), !1662)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1662)
  store i8 0, ptr %1, align 1, !dbg !1664, !tbaa !113
  br label %526, !dbg !1665

33:                                               ; preds = %3
  %34 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1666
    #dbg_value(i16 0, !1534, !DIExpression(), !1669)
    #dbg_value(i16 0, !1535, !DIExpression(), !1669)
    #dbg_value(i16 3, !1536, !DIExpression(), !1669)
    #dbg_value(i16 0, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1669)
    #dbg_value(i16 0, !1537, !DIExpression(), !1669)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1669)
  br label %35, !dbg !1671

35:                                               ; preds = %46, %33
  %36 = phi i32 [ 0, %33 ], [ %49, %46 ]
  %37 = icmp ugt i32 %36, 7, !dbg !1672
  br i1 %37, label %46, label %38, !dbg !1672

38:                                               ; preds = %35
    #dbg_value(i8 poison, !1539, !DIExpression(), !1669)
    #dbg_value(i32 %36, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1669)
    #dbg_value(!DIArgList(i8 5, i16 0), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1669)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1669)
    #dbg_value(i32 %36, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1669)
  %39 = shl nuw nsw i32 %36, 2, !dbg !1673
    #dbg_value(i32 %36, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1669)
  %40 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %36, !dbg !1674
  %41 = load i8, ptr %40, align 1, !dbg !1674, !tbaa !113
    #dbg_value(i8 %41, !1539, !DIExpression(), !1669)
    #dbg_value(!DIArgList(i8 %41, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1669)
    #dbg_value(!DIArgList(i8 %41, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1669)
    #dbg_value(!DIArgList(i8 %41, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1669)
    #dbg_value(!DIArgList(i8 %41, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1669)
    #dbg_value(!DIArgList(i8 %41, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1669)
    #dbg_value(!DIArgList(i8 %41, i32 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1669)
  %42 = shl i8 %41, 5, !dbg !1675
    #dbg_value(i8 %42, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1669)
  %43 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %39, !dbg !1676
  %44 = load i8, ptr %43, align 4, !dbg !1676, !tbaa !113
  %45 = or i8 %44, %42, !dbg !1677
  store i8 %45, ptr %43, align 4, !dbg !1678, !tbaa !113
  br label %46, !dbg !1679

46:                                               ; preds = %38, %35
    #dbg_value(i16 poison, !1537, !DIExpression(), !1669)
  %47 = shl nsw i32 %36, 16, !dbg !1680
  %48 = add i32 %47, 65536, !dbg !1680
  %49 = ashr exact i32 %48, 16, !dbg !1680
  %50 = icmp slt i32 %49, 3, !dbg !1681
  br i1 %50, label %35, label %51, !dbg !1671, !llvm.loop !1682

51:                                               ; preds = %46
  %52 = load i8, ptr @shared_fb, align 16, !dbg !1684, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1685)
    #dbg_value(ptr %1, !107, !DIExpression(), !1685)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1685)
  store i8 0, ptr %1, align 1, !dbg !1687, !tbaa !113
  br label %526, !dbg !1688

53:                                               ; preds = %3
  %54 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1689
    #dbg_value(i16 0, !1534, !DIExpression(), !1692)
    #dbg_value(i16 0, !1535, !DIExpression(), !1692)
    #dbg_value(i16 3, !1536, !DIExpression(), !1692)
    #dbg_value(i16 0, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1692)
    #dbg_value(i16 0, !1537, !DIExpression(), !1692)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1692)
  br label %55, !dbg !1694

55:                                               ; preds = %66, %53
  %56 = phi i32 [ 0, %53 ], [ %69, %66 ]
  %57 = icmp ugt i32 %56, 7, !dbg !1695
  br i1 %57, label %66, label %58, !dbg !1695

58:                                               ; preds = %55
    #dbg_value(i8 poison, !1539, !DIExpression(), !1692)
    #dbg_value(i32 %56, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1692)
    #dbg_value(!DIArgList(i8 5, i16 0), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1692)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1692)
    #dbg_value(i32 %56, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1692)
  %59 = shl nuw nsw i32 %56, 2, !dbg !1696
    #dbg_value(i32 %56, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1692)
  %60 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %56, !dbg !1697
  %61 = load i8, ptr %60, align 1, !dbg !1697, !tbaa !113
    #dbg_value(i8 %61, !1539, !DIExpression(), !1692)
    #dbg_value(!DIArgList(i8 %61, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1692)
    #dbg_value(!DIArgList(i8 %61, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1692)
    #dbg_value(!DIArgList(i8 %61, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1692)
    #dbg_value(!DIArgList(i8 %61, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1692)
    #dbg_value(!DIArgList(i8 %61, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1692)
    #dbg_value(!DIArgList(i8 %61, i32 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1692)
  %62 = shl i8 %61, 5, !dbg !1698
    #dbg_value(i8 %62, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1692)
  %63 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %59, !dbg !1699
  %64 = load i8, ptr %63, align 4, !dbg !1699, !tbaa !113
  %65 = or i8 %64, %62, !dbg !1700
  store i8 %65, ptr %63, align 4, !dbg !1701, !tbaa !113
  br label %66, !dbg !1702

66:                                               ; preds = %58, %55
    #dbg_value(i16 poison, !1537, !DIExpression(), !1692)
  %67 = shl nsw i32 %56, 16, !dbg !1703
  %68 = add i32 %67, 65536, !dbg !1703
  %69 = ashr exact i32 %68, 16, !dbg !1703
  %70 = icmp slt i32 %69, 3, !dbg !1704
  br i1 %70, label %55, label %71, !dbg !1694, !llvm.loop !1705

71:                                               ; preds = %66
  %72 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 4), align 4, !dbg !1707, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1708)
    #dbg_value(ptr %1, !107, !DIExpression(), !1708)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1708)
  store i8 0, ptr %1, align 1, !dbg !1710, !tbaa !113
  br label %526, !dbg !1711

73:                                               ; preds = %3
  %74 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1712
    #dbg_value(i16 0, !1534, !DIExpression(), !1715)
    #dbg_value(i16 0, !1535, !DIExpression(), !1715)
    #dbg_value(i16 3, !1536, !DIExpression(), !1715)
    #dbg_value(i16 0, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1715)
    #dbg_value(i16 0, !1537, !DIExpression(), !1715)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1715)
  br label %75, !dbg !1717

75:                                               ; preds = %86, %73
  %76 = phi i32 [ 0, %73 ], [ %89, %86 ]
  %77 = icmp ugt i32 %76, 7, !dbg !1718
  br i1 %77, label %86, label %78, !dbg !1718

78:                                               ; preds = %75
    #dbg_value(i8 poison, !1539, !DIExpression(), !1715)
    #dbg_value(i32 %76, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1715)
    #dbg_value(!DIArgList(i8 5, i16 0), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1715)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1715)
    #dbg_value(i32 %76, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1715)
  %79 = shl nuw nsw i32 %76, 2, !dbg !1719
    #dbg_value(i32 %76, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1715)
  %80 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %76, !dbg !1720
  %81 = load i8, ptr %80, align 1, !dbg !1720, !tbaa !113
    #dbg_value(i8 %81, !1539, !DIExpression(), !1715)
    #dbg_value(!DIArgList(i8 %81, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1715)
    #dbg_value(!DIArgList(i8 %81, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1715)
    #dbg_value(!DIArgList(i8 %81, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1715)
    #dbg_value(!DIArgList(i8 %81, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1715)
    #dbg_value(!DIArgList(i8 %81, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1715)
    #dbg_value(!DIArgList(i8 %81, i32 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1715)
  %82 = shl i8 %81, 5, !dbg !1721
    #dbg_value(i8 %82, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1715)
  %83 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %79, !dbg !1722
  %84 = load i8, ptr %83, align 4, !dbg !1722, !tbaa !113
  %85 = or i8 %84, %82, !dbg !1723
  store i8 %85, ptr %83, align 4, !dbg !1724, !tbaa !113
  br label %86, !dbg !1725

86:                                               ; preds = %78, %75
    #dbg_value(i16 poison, !1537, !DIExpression(), !1715)
  %87 = shl nsw i32 %76, 16, !dbg !1726
  %88 = add i32 %87, 65536, !dbg !1726
  %89 = ashr exact i32 %88, 16, !dbg !1726
  %90 = icmp slt i32 %89, 3, !dbg !1727
  br i1 %90, label %75, label %91, !dbg !1717, !llvm.loop !1728

91:                                               ; preds = %86, %91
  %92 = phi i32 [ %100, %91 ], [ 0, %86 ]
  %93 = phi i16 [ %97, %91 ], [ 0, %86 ]
    #dbg_value(i16 %93, !1495, !DIExpression(), !1730)
  %94 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %92, !dbg !1732
  %95 = load i8, ptr %94, align 1, !dbg !1732, !tbaa !113
  %96 = zext i8 %95 to i16, !dbg !1732
  %97 = add i16 %93, %96, !dbg !1733
    #dbg_value(i16 %97, !1495, !DIExpression(), !1730)
    #dbg_value(i16 poison, !1494, !DIExpression(), !1730)
  %98 = shl nsw i32 %92, 16, !dbg !1734
  %99 = add i32 %98, 65536, !dbg !1734
  %100 = ashr exact i32 %99, 16, !dbg !1734
  %101 = icmp slt i32 %100, 32, !dbg !1735
  br i1 %101, label %91, label %102, !dbg !1736, !llvm.loop !1737

102:                                              ; preds = %91
    #dbg_value(ptr %0, !106, !DIExpression(), !1739)
    #dbg_value(ptr %1, !107, !DIExpression(), !1739)
    #dbg_value(i16 %97, !108, !DIExpression(), !1739)
  %103 = lshr i16 %97, 8, !dbg !1741
  %104 = trunc nuw i16 %103 to i8, !dbg !1742
  store i8 %104, ptr %1, align 1, !dbg !1743, !tbaa !113
  %105 = trunc i16 %97 to i8, !dbg !1744
  br label %526, !dbg !1745

106:                                              ; preds = %3
  %107 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1746
    #dbg_value(i16 3, !1534, !DIExpression(), !1749)
    #dbg_value(i16 0, !1535, !DIExpression(), !1749)
    #dbg_value(i16 3, !1536, !DIExpression(), !1749)
    #dbg_value(i16 3, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1749)
    #dbg_value(i16 0, !1537, !DIExpression(), !1749)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1749)
  br label %108, !dbg !1751

108:                                              ; preds = %120, %106
  %109 = phi i32 [ 0, %106 ], [ %123, %120 ]
  %110 = icmp ugt i32 %109, 7, !dbg !1752
  br i1 %110, label %120, label %111, !dbg !1752

111:                                              ; preds = %108
    #dbg_value(i8 poison, !1539, !DIExpression(), !1749)
    #dbg_value(i32 %109, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1749)
    #dbg_value(!DIArgList(i8 5, i16 3), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1749)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1749)
    #dbg_value(i32 %109, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1749)
  %112 = shl nuw nsw i32 %109, 2, !dbg !1753
    #dbg_value(i32 %109, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1749)
  %113 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %109, !dbg !1754
  %114 = load i8, ptr %113, align 1, !dbg !1754, !tbaa !113
    #dbg_value(i8 %114, !1539, !DIExpression(), !1749)
    #dbg_value(!DIArgList(i8 %114, i16 5, i16 3), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1749)
    #dbg_value(!DIArgList(i8 %114, i16 5, i16 3), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1749)
    #dbg_value(!DIArgList(i8 %114, i16 5, i16 3), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1749)
    #dbg_value(!DIArgList(i8 %114, i16 2), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1749)
    #dbg_value(!DIArgList(i8 %114, i16 2), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1749)
    #dbg_value(!DIArgList(i8 %114, i32 2), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1749)
  %115 = shl i8 %114, 2, !dbg !1755
  %116 = and i8 %115, 28, !dbg !1755
    #dbg_value(i8 %116, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1749)
  %117 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %112, !dbg !1756
  %118 = load i8, ptr %117, align 4, !dbg !1756, !tbaa !113
  %119 = or i8 %116, %118, !dbg !1757
  store i8 %119, ptr %117, align 4, !dbg !1758, !tbaa !113
  br label %120, !dbg !1759

120:                                              ; preds = %111, %108
    #dbg_value(i16 poison, !1537, !DIExpression(), !1749)
  %121 = shl nsw i32 %109, 16, !dbg !1760
  %122 = add i32 %121, 65536, !dbg !1760
  %123 = ashr exact i32 %122, 16, !dbg !1760
  %124 = icmp slt i32 %123, 3, !dbg !1761
  br i1 %124, label %108, label %125, !dbg !1751, !llvm.loop !1762

125:                                              ; preds = %120
  %126 = load i8, ptr @shared_fb, align 16, !dbg !1764, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1765)
    #dbg_value(ptr %1, !107, !DIExpression(), !1765)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1765)
  store i8 0, ptr %1, align 1, !dbg !1767, !tbaa !113
  br label %526, !dbg !1768

127:                                              ; preds = %3
  %128 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1769
    #dbg_value(i16 5, !1534, !DIExpression(), !1772)
    #dbg_value(i16 0, !1535, !DIExpression(), !1772)
    #dbg_value(i16 3, !1536, !DIExpression(), !1772)
    #dbg_value(i16 5, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1772)
    #dbg_value(i16 0, !1537, !DIExpression(), !1772)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1772)
  br label %129, !dbg !1774

129:                                              ; preds = %140, %127
  %130 = phi i32 [ 0, %127 ], [ %143, %140 ]
  %131 = icmp ugt i32 %130, 7, !dbg !1775
  br i1 %131, label %140, label %132, !dbg !1775

132:                                              ; preds = %129
    #dbg_value(i8 poison, !1539, !DIExpression(), !1772)
    #dbg_value(i32 %130, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1772)
    #dbg_value(!DIArgList(i8 5, i16 5), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1772)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1772)
    #dbg_value(i32 %130, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1772)
  %133 = shl nuw nsw i32 %130, 2, !dbg !1776
    #dbg_value(i32 %130, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1772)
  %134 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %130, !dbg !1777
  %135 = load i8, ptr %134, align 1, !dbg !1777, !tbaa !113
    #dbg_value(i8 %135, !1539, !DIExpression(), !1772)
    #dbg_value(!DIArgList(i8 %135, i16 5, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1772)
  %136 = and i8 %135, 7, !dbg !1778
    #dbg_value(!DIArgList(i8 %136, i16 5, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1772)
    #dbg_value(!DIArgList(i8 %136, i16 5, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1772)
    #dbg_value(!DIArgList(i8 %136, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1772)
    #dbg_value(!DIArgList(i8 %136, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1772)
    #dbg_value(!DIArgList(i8 %136, i32 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1772)
    #dbg_value(i8 %136, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1772)
  %137 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %133, !dbg !1779
  %138 = load i8, ptr %137, align 4, !dbg !1779, !tbaa !113
  %139 = or i8 %138, %136, !dbg !1780
  store i8 %139, ptr %137, align 4, !dbg !1781, !tbaa !113
  br label %140, !dbg !1782

140:                                              ; preds = %132, %129
    #dbg_value(i16 poison, !1537, !DIExpression(), !1772)
  %141 = shl nsw i32 %130, 16, !dbg !1783
  %142 = add i32 %141, 65536, !dbg !1783
  %143 = ashr exact i32 %142, 16, !dbg !1783
  %144 = icmp slt i32 %143, 3, !dbg !1784
  br i1 %144, label %129, label %145, !dbg !1774, !llvm.loop !1785

145:                                              ; preds = %140
  %146 = load i8, ptr @shared_fb, align 16, !dbg !1787, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1788)
    #dbg_value(ptr %1, !107, !DIExpression(), !1788)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1788)
  store i8 0, ptr %1, align 1, !dbg !1790, !tbaa !113
  br label %526, !dbg !1791

147:                                              ; preds = %3
  %148 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1792
    #dbg_value(i16 6, !1534, !DIExpression(), !1795)
    #dbg_value(i16 0, !1535, !DIExpression(), !1795)
    #dbg_value(i16 3, !1536, !DIExpression(), !1795)
    #dbg_value(i16 6, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1795)
    #dbg_value(i16 0, !1537, !DIExpression(), !1795)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1795)
  br label %149, !dbg !1797

149:                                              ; preds = %166, %147
  %150 = phi i32 [ 0, %147 ], [ %169, %166 ]
  %151 = icmp ugt i32 %150, 7, !dbg !1798
  br i1 %151, label %166, label %152, !dbg !1798

152:                                              ; preds = %149
  %153 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %150, !dbg !1799
  %154 = load i8, ptr %153, align 1, !dbg !1799, !tbaa !113
    #dbg_value(i8 %154, !1539, !DIExpression(), !1795)
  %155 = shl nuw nsw i32 %150, 2, !dbg !1800
    #dbg_value(i32 %150, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1795)
    #dbg_value(i16 6, !1541, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !1795)
    #dbg_value(!DIArgList(i8 %154, i32 1), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1795)
  %156 = shl i8 %154, 7, !dbg !1801
    #dbg_value(i8 %154, !1543, !DIExpression(DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1795)
  %157 = lshr i8 %154, 1, !dbg !1802
  %158 = and i8 %157, 3, !dbg !1802
    #dbg_value(i8 %154, !1542, !DIExpression(DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_constu, 1, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1795)
  %159 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %155, !dbg !1803
  %160 = load i8, ptr %159, align 4, !dbg !1803, !tbaa !113
  %161 = or i8 %158, %160, !dbg !1804
  store i8 %161, ptr %159, align 4, !dbg !1805, !tbaa !113
  %162 = or disjoint i32 %155, 1, !dbg !1806
  %163 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %162, !dbg !1807
  %164 = load i8, ptr %163, align 1, !dbg !1807, !tbaa !113
  %165 = or i8 %164, %156, !dbg !1808
  store i8 %165, ptr %163, align 1, !dbg !1809, !tbaa !113
  br label %166, !dbg !1810

166:                                              ; preds = %152, %149
    #dbg_value(i16 poison, !1537, !DIExpression(), !1795)
  %167 = shl nsw i32 %150, 16, !dbg !1811
  %168 = add i32 %167, 65536, !dbg !1811
  %169 = ashr exact i32 %168, 16, !dbg !1811
  %170 = icmp slt i32 %169, 3, !dbg !1812
  br i1 %170, label %149, label %171, !dbg !1797, !llvm.loop !1813

171:                                              ; preds = %166
  %172 = load i8, ptr @shared_fb, align 16, !dbg !1815, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1816)
    #dbg_value(ptr %1, !107, !DIExpression(), !1816)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1816)
  store i8 0, ptr %1, align 1, !dbg !1818, !tbaa !113
  br label %526, !dbg !1819

173:                                              ; preds = %3
  %174 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1820
    #dbg_value(i16 6, !1534, !DIExpression(), !1823)
    #dbg_value(i16 0, !1535, !DIExpression(), !1823)
    #dbg_value(i16 3, !1536, !DIExpression(), !1823)
    #dbg_value(i16 6, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1823)
    #dbg_value(i16 0, !1537, !DIExpression(), !1823)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1823)
  br label %175, !dbg !1825

175:                                              ; preds = %192, %173
  %176 = phi i32 [ 0, %173 ], [ %195, %192 ]
  %177 = icmp ugt i32 %176, 7, !dbg !1826
  br i1 %177, label %192, label %178, !dbg !1826

178:                                              ; preds = %175
  %179 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %176, !dbg !1827
  %180 = load i8, ptr %179, align 1, !dbg !1827, !tbaa !113
    #dbg_value(i8 %180, !1539, !DIExpression(), !1823)
  %181 = shl nuw nsw i32 %176, 2, !dbg !1828
    #dbg_value(i32 %176, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1823)
    #dbg_value(i16 6, !1541, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !1823)
    #dbg_value(!DIArgList(i8 %180, i32 1), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1823)
  %182 = shl i8 %180, 7, !dbg !1829
    #dbg_value(i8 %180, !1543, !DIExpression(DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1823)
  %183 = lshr i8 %180, 1, !dbg !1830
  %184 = and i8 %183, 3, !dbg !1830
    #dbg_value(i8 %180, !1542, !DIExpression(DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_constu, 1, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1823)
  %185 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %181, !dbg !1831
  %186 = load i8, ptr %185, align 4, !dbg !1831, !tbaa !113
  %187 = or i8 %184, %186, !dbg !1832
  store i8 %187, ptr %185, align 4, !dbg !1833, !tbaa !113
  %188 = or disjoint i32 %181, 1, !dbg !1834
  %189 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %188, !dbg !1835
  %190 = load i8, ptr %189, align 1, !dbg !1835, !tbaa !113
  %191 = or i8 %190, %182, !dbg !1836
  store i8 %191, ptr %189, align 1, !dbg !1837, !tbaa !113
  br label %192, !dbg !1838

192:                                              ; preds = %178, %175
    #dbg_value(i16 poison, !1537, !DIExpression(), !1823)
  %193 = shl nsw i32 %176, 16, !dbg !1839
  %194 = add i32 %193, 65536, !dbg !1839
  %195 = ashr exact i32 %194, 16, !dbg !1839
  %196 = icmp slt i32 %195, 3, !dbg !1840
  br i1 %196, label %175, label %197, !dbg !1825, !llvm.loop !1841

197:                                              ; preds = %192
  %198 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !1843, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1844)
    #dbg_value(ptr %1, !107, !DIExpression(), !1844)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1844)
  store i8 0, ptr %1, align 1, !dbg !1846, !tbaa !113
  br label %526, !dbg !1847

199:                                              ; preds = %3
  %200 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1848
    #dbg_value(i16 7, !1534, !DIExpression(), !1851)
    #dbg_value(i16 0, !1535, !DIExpression(), !1851)
    #dbg_value(i16 3, !1536, !DIExpression(), !1851)
    #dbg_value(i16 7, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1851)
    #dbg_value(i16 0, !1537, !DIExpression(), !1851)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1851)
  br label %201, !dbg !1853

201:                                              ; preds = %218, %199
  %202 = phi i32 [ 0, %199 ], [ %221, %218 ]
  %203 = icmp ugt i32 %202, 7, !dbg !1854
  br i1 %203, label %218, label %204, !dbg !1854

204:                                              ; preds = %201
  %205 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %202, !dbg !1855
  %206 = load i8, ptr %205, align 1, !dbg !1855, !tbaa !113
    #dbg_value(i8 %206, !1539, !DIExpression(), !1851)
  %207 = shl nuw nsw i32 %202, 2, !dbg !1856
    #dbg_value(i32 %202, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1851)
    #dbg_value(i16 7, !1541, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !1851)
    #dbg_value(!DIArgList(i8 %206, i32 2), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1851)
  %208 = shl i8 %206, 6, !dbg !1857
    #dbg_value(i8 %206, !1543, !DIExpression(DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_constu, 6, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1851)
  %209 = lshr i8 %206, 2, !dbg !1858
  %210 = and i8 %209, 1, !dbg !1858
    #dbg_value(i8 %206, !1542, !DIExpression(DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1851)
  %211 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %207, !dbg !1859
  %212 = load i8, ptr %211, align 4, !dbg !1859, !tbaa !113
  %213 = or i8 %210, %212, !dbg !1860
  store i8 %213, ptr %211, align 4, !dbg !1861, !tbaa !113
  %214 = or disjoint i32 %207, 1, !dbg !1862
  %215 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %214, !dbg !1863
  %216 = load i8, ptr %215, align 1, !dbg !1863, !tbaa !113
  %217 = or i8 %216, %208, !dbg !1864
  store i8 %217, ptr %215, align 1, !dbg !1865, !tbaa !113
  br label %218, !dbg !1866

218:                                              ; preds = %204, %201
    #dbg_value(i16 poison, !1537, !DIExpression(), !1851)
  %219 = shl nsw i32 %202, 16, !dbg !1867
  %220 = add i32 %219, 65536, !dbg !1867
  %221 = ashr exact i32 %220, 16, !dbg !1867
  %222 = icmp slt i32 %221, 3, !dbg !1868
  br i1 %222, label %201, label %223, !dbg !1853, !llvm.loop !1869

223:                                              ; preds = %218
  %224 = load i8, ptr @shared_fb, align 16, !dbg !1871, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1872)
    #dbg_value(ptr %1, !107, !DIExpression(), !1872)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1872)
  store i8 0, ptr %1, align 1, !dbg !1874, !tbaa !113
  br label %526, !dbg !1875

225:                                              ; preds = %3
  %226 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1876
    #dbg_value(i16 7, !1534, !DIExpression(), !1879)
    #dbg_value(i16 0, !1535, !DIExpression(), !1879)
    #dbg_value(i16 3, !1536, !DIExpression(), !1879)
    #dbg_value(i16 7, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1879)
    #dbg_value(i16 0, !1537, !DIExpression(), !1879)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1879)
  br label %227, !dbg !1881

227:                                              ; preds = %244, %225
  %228 = phi i32 [ 0, %225 ], [ %247, %244 ]
  %229 = icmp ugt i32 %228, 7, !dbg !1882
  br i1 %229, label %244, label %230, !dbg !1882

230:                                              ; preds = %227
  %231 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %228, !dbg !1883
  %232 = load i8, ptr %231, align 1, !dbg !1883, !tbaa !113
    #dbg_value(i8 %232, !1539, !DIExpression(), !1879)
  %233 = shl nuw nsw i32 %228, 2, !dbg !1884
    #dbg_value(i32 %228, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1879)
    #dbg_value(i16 7, !1541, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !1879)
    #dbg_value(!DIArgList(i8 %232, i32 2), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1879)
  %234 = shl i8 %232, 6, !dbg !1885
    #dbg_value(i8 %232, !1543, !DIExpression(DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_constu, 6, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1879)
  %235 = lshr i8 %232, 2, !dbg !1886
  %236 = and i8 %235, 1, !dbg !1886
    #dbg_value(i8 %232, !1542, !DIExpression(DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1879)
  %237 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %233, !dbg !1887
  %238 = load i8, ptr %237, align 4, !dbg !1887, !tbaa !113
  %239 = or i8 %236, %238, !dbg !1888
  store i8 %239, ptr %237, align 4, !dbg !1889, !tbaa !113
  %240 = or disjoint i32 %233, 1, !dbg !1890
  %241 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %240, !dbg !1891
  %242 = load i8, ptr %241, align 1, !dbg !1891, !tbaa !113
  %243 = or i8 %242, %234, !dbg !1892
  store i8 %243, ptr %241, align 1, !dbg !1893, !tbaa !113
  br label %244, !dbg !1894

244:                                              ; preds = %230, %227
    #dbg_value(i16 poison, !1537, !DIExpression(), !1879)
  %245 = shl nsw i32 %228, 16, !dbg !1895
  %246 = add i32 %245, 65536, !dbg !1895
  %247 = ashr exact i32 %246, 16, !dbg !1895
  %248 = icmp slt i32 %247, 3, !dbg !1896
  br i1 %248, label %227, label %249, !dbg !1881, !llvm.loop !1897

249:                                              ; preds = %244
  %250 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !1899, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1900)
    #dbg_value(ptr %1, !107, !DIExpression(), !1900)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1900)
  store i8 0, ptr %1, align 1, !dbg !1902, !tbaa !113
  br label %526, !dbg !1903

251:                                              ; preds = %3
  %252 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1904
    #dbg_value(i16 0, !1534, !DIExpression(), !1907)
    #dbg_value(i16 0, !1535, !DIExpression(), !1907)
    #dbg_value(i16 3, !1536, !DIExpression(), !1907)
    #dbg_value(i16 0, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1907)
    #dbg_value(i16 0, !1537, !DIExpression(), !1907)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1907)
  br label %253, !dbg !1909

253:                                              ; preds = %264, %251
  %254 = phi i32 [ 0, %251 ], [ %267, %264 ]
  %255 = icmp ugt i32 %254, 7, !dbg !1910
  br i1 %255, label %264, label %256, !dbg !1910

256:                                              ; preds = %253
    #dbg_value(i8 poison, !1539, !DIExpression(), !1907)
    #dbg_value(i32 %254, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1907)
    #dbg_value(!DIArgList(i8 5, i16 0), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1907)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1907)
    #dbg_value(i32 %254, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1907)
  %257 = shl nuw nsw i32 %254, 2, !dbg !1911
    #dbg_value(i32 %254, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1907)
  %258 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %254, !dbg !1912
  %259 = load i8, ptr %258, align 1, !dbg !1912, !tbaa !113
    #dbg_value(i8 %259, !1539, !DIExpression(), !1907)
    #dbg_value(!DIArgList(i8 %259, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1907)
    #dbg_value(!DIArgList(i8 %259, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1907)
    #dbg_value(!DIArgList(i8 %259, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1907)
    #dbg_value(!DIArgList(i8 %259, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1907)
    #dbg_value(!DIArgList(i8 %259, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1907)
    #dbg_value(!DIArgList(i8 %259, i32 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1907)
  %260 = shl i8 %259, 5, !dbg !1913
    #dbg_value(i8 %260, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1907)
  %261 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %257, !dbg !1914
  %262 = load i8, ptr %261, align 4, !dbg !1914, !tbaa !113
  %263 = or i8 %262, %260, !dbg !1915
  store i8 %263, ptr %261, align 4, !dbg !1916, !tbaa !113
  br label %264, !dbg !1917

264:                                              ; preds = %256, %253
    #dbg_value(i16 poison, !1537, !DIExpression(), !1907)
  %265 = shl nsw i32 %254, 16, !dbg !1918
  %266 = add i32 %265, 65536, !dbg !1918
  %267 = ashr exact i32 %266, 16, !dbg !1918
  %268 = icmp slt i32 %267, 3, !dbg !1919
  br i1 %268, label %253, label %269, !dbg !1909, !llvm.loop !1920

269:                                              ; preds = %264, %283
  %270 = phi i32 [ %286, %283 ], [ 0, %264 ]
  %271 = add nsw i32 %270, 2, !dbg !1922
  %272 = icmp ugt i32 %271, 7, !dbg !1924
  br i1 %272, label %283, label %273, !dbg !1924

273:                                              ; preds = %269
    #dbg_value(i8 poison, !1539, !DIExpression(), !1925)
    #dbg_value(i32 %271, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 1, DW_OP_or, DW_OP_stack_value), !1925)
    #dbg_value(!DIArgList(i8 5, i16 2), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1925)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1925)
    #dbg_value(i32 %271, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 1, DW_OP_or, DW_OP_stack_value), !1925)
  %274 = shl nuw nsw i32 %271, 2, !dbg !1926
    #dbg_value(i32 %271, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 1, DW_OP_or, DW_OP_stack_value), !1925)
  %275 = or disjoint i32 %274, 1, !dbg !1926
  %276 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %270, !dbg !1927
  %277 = load i8, ptr %276, align 1, !dbg !1927, !tbaa !113
    #dbg_value(i8 %277, !1539, !DIExpression(), !1925)
    #dbg_value(!DIArgList(i8 %277, i16 5, i16 2), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1925)
    #dbg_value(!DIArgList(i8 %277, i16 5, i16 2), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1925)
    #dbg_value(!DIArgList(i8 %277, i16 5, i16 2), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1925)
    #dbg_value(!DIArgList(i8 %277, i16 3), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1925)
    #dbg_value(!DIArgList(i8 %277, i16 3), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1925)
    #dbg_value(!DIArgList(i8 %277, i32 3), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1925)
  %278 = shl i8 %277, 3, !dbg !1928
  %279 = and i8 %278, 56, !dbg !1928
    #dbg_value(i8 %279, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1925)
  %280 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %275, !dbg !1929
  %281 = load i8, ptr %280, align 1, !dbg !1929, !tbaa !113
  %282 = or i8 %279, %281, !dbg !1930
  store i8 %282, ptr %280, align 1, !dbg !1931, !tbaa !113
  br label %283, !dbg !1932

283:                                              ; preds = %273, %269
    #dbg_value(i16 poison, !1537, !DIExpression(), !1925)
  %284 = shl nsw i32 %270, 16, !dbg !1933
  %285 = add i32 %284, 65536, !dbg !1933
  %286 = ashr exact i32 %285, 16, !dbg !1933
  %287 = icmp slt i32 %286, 3, !dbg !1934
  br i1 %287, label %269, label %288, !dbg !1935, !llvm.loop !1936

288:                                              ; preds = %283, %288
  %289 = phi i32 [ %297, %288 ], [ 0, %283 ]
  %290 = phi i16 [ %294, %288 ], [ 0, %283 ]
    #dbg_value(i16 %290, !1495, !DIExpression(), !1938)
  %291 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %289, !dbg !1940
  %292 = load i8, ptr %291, align 1, !dbg !1940, !tbaa !113
  %293 = zext i8 %292 to i16, !dbg !1940
  %294 = add i16 %290, %293, !dbg !1941
    #dbg_value(i16 %294, !1495, !DIExpression(), !1938)
    #dbg_value(i16 poison, !1494, !DIExpression(), !1938)
  %295 = shl nsw i32 %289, 16, !dbg !1942
  %296 = add i32 %295, 65536, !dbg !1942
  %297 = ashr exact i32 %296, 16, !dbg !1942
  %298 = icmp slt i32 %297, 32, !dbg !1943
  br i1 %298, label %288, label %299, !dbg !1944, !llvm.loop !1945

299:                                              ; preds = %288
    #dbg_value(ptr %0, !106, !DIExpression(), !1947)
    #dbg_value(ptr %1, !107, !DIExpression(), !1947)
    #dbg_value(i16 %294, !108, !DIExpression(), !1947)
  %300 = lshr i16 %294, 8, !dbg !1949
  %301 = trunc nuw i16 %300 to i8, !dbg !1950
  store i8 %301, ptr %1, align 1, !dbg !1951, !tbaa !113
  %302 = trunc i16 %294 to i8, !dbg !1952
  br label %526, !dbg !1953

303:                                              ; preds = %3
  %304 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1954
    #dbg_value(i16 0, !1534, !DIExpression(), !1957)
    #dbg_value(i16 2, !1535, !DIExpression(), !1957)
    #dbg_value(i16 3, !1536, !DIExpression(), !1957)
    #dbg_value(i16 0, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !1957)
    #dbg_value(i16 0, !1537, !DIExpression(), !1957)
    #dbg_value(i16 poison, !1537, !DIExpression(), !1957)
  br label %305, !dbg !1959

305:                                              ; preds = %317, %303
  %306 = phi i32 [ 0, %303 ], [ %320, %317 ]
  %307 = add nsw i32 %306, 2, !dbg !1960
  %308 = icmp ugt i32 %307, 7, !dbg !1961
  br i1 %308, label %317, label %309, !dbg !1961

309:                                              ; preds = %305
    #dbg_value(i8 poison, !1539, !DIExpression(), !1957)
    #dbg_value(i32 %307, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1957)
    #dbg_value(!DIArgList(i8 5, i16 0), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !1957)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1957)
    #dbg_value(i32 %307, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1957)
  %310 = shl nuw nsw i32 %307, 2, !dbg !1962
    #dbg_value(i32 %307, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_stack_value), !1957)
  %311 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %306, !dbg !1963
  %312 = load i8, ptr %311, align 1, !dbg !1963, !tbaa !113
    #dbg_value(i8 %312, !1539, !DIExpression(), !1957)
    #dbg_value(!DIArgList(i8 %312, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1957)
    #dbg_value(!DIArgList(i8 %312, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1957)
    #dbg_value(!DIArgList(i8 %312, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1957)
    #dbg_value(!DIArgList(i8 %312, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1957)
    #dbg_value(!DIArgList(i8 %312, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1957)
    #dbg_value(!DIArgList(i8 %312, i32 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1957)
  %313 = shl i8 %312, 5, !dbg !1964
    #dbg_value(i8 %313, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !1957)
  %314 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %310, !dbg !1965
  %315 = load i8, ptr %314, align 4, !dbg !1965, !tbaa !113
  %316 = or i8 %315, %313, !dbg !1966
  store i8 %316, ptr %314, align 4, !dbg !1967, !tbaa !113
  br label %317, !dbg !1968

317:                                              ; preds = %309, %305
    #dbg_value(i16 poison, !1537, !DIExpression(), !1957)
  %318 = shl nsw i32 %306, 16, !dbg !1969
  %319 = add i32 %318, 65536, !dbg !1969
  %320 = ashr exact i32 %319, 16, !dbg !1969
  %321 = icmp slt i32 %320, 3, !dbg !1970
  br i1 %321, label %305, label %322, !dbg !1959, !llvm.loop !1971

322:                                              ; preds = %317
  %323 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 8), align 8, !dbg !1973, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1974)
    #dbg_value(ptr %1, !107, !DIExpression(), !1974)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1974)
  store i8 0, ptr %1, align 1, !dbg !1976, !tbaa !113
  br label %526, !dbg !1977

324:                                              ; preds = %3
  %325 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !1978
    #dbg_value(i16 0, !1597, !DIExpression(), !1609)
    #dbg_value(i16 0, !1594, !DIExpression(), !1609)
    #dbg_value(i16 0, !1595, !DIExpression(), !1609)
    #dbg_value(i8 0, !1601, !DIExpression(), !1609)
    #dbg_value(i16 0, !1596, !DIExpression(), !1609)
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  br label %326, !dbg !1981

326:                                              ; preds = %324, %326
  %327 = phi i32 [ 0, %324 ], [ %339, %326 ]
  %328 = phi i32 [ 0, %324 ], [ %337, %326 ]
  %329 = getelementptr inbounds [50 x i8], ptr @FONT_5x3, i32 0, i32 %327, !dbg !1983
  %330 = load i8, ptr %329, align 1, !dbg !1983, !tbaa !113
    #dbg_value(i8 %330, !1600, !DIExpression(), !1609)
    #dbg_value(i32 undef, !1599, !DIExpression(DW_OP_constu, 14, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1609)
    #dbg_value(i8 5, !1602, !DIExpression(), !1609)
  %331 = shl i8 %330, 5, !dbg !1986
    #dbg_value(i8 %331, !1603, !DIExpression(), !1609)
  %332 = shl i32 %328, 18, !dbg !1987
  %333 = ashr exact i32 %332, 16, !dbg !1987
  %334 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %333, !dbg !1987
  %335 = load i8, ptr %334, align 4, !dbg !1987, !tbaa !113
  %336 = or i8 %335, %331, !dbg !1988
  store i8 %336, ptr %334, align 4, !dbg !1989, !tbaa !113
  %337 = add nsw i32 %327, 1, !dbg !1990
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  %338 = shl i32 %337, 16, !dbg !1991
  %339 = ashr exact i32 %338, 16, !dbg !1991
  %340 = icmp slt i32 %339, 5, !dbg !1992
  br i1 %340, label %326, label %341, !dbg !1981, !llvm.loop !1993

341:                                              ; preds = %326
  %342 = load i8, ptr @shared_fb, align 16, !dbg !1995, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !1996)
    #dbg_value(ptr %1, !107, !DIExpression(), !1996)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1996)
  store i8 0, ptr %1, align 1, !dbg !1998, !tbaa !113
  br label %526, !dbg !1999

343:                                              ; preds = %3
  %344 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !2000
    #dbg_value(i16 0, !1597, !DIExpression(), !1609)
    #dbg_value(i16 0, !1594, !DIExpression(), !1609)
    #dbg_value(i16 0, !1595, !DIExpression(), !1609)
    #dbg_value(i8 0, !1601, !DIExpression(), !1609)
    #dbg_value(i16 0, !1596, !DIExpression(), !1609)
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  br label %345, !dbg !2003

345:                                              ; preds = %343, %345
  %346 = phi i32 [ 0, %343 ], [ %358, %345 ]
  %347 = phi i32 [ 0, %343 ], [ %356, %345 ]
  %348 = getelementptr inbounds [50 x i8], ptr @FONT_5x3, i32 0, i32 %346, !dbg !2005
  %349 = load i8, ptr %348, align 1, !dbg !2005, !tbaa !113
    #dbg_value(i8 %349, !1600, !DIExpression(), !1609)
    #dbg_value(i32 undef, !1599, !DIExpression(DW_OP_constu, 14, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1609)
    #dbg_value(i8 5, !1602, !DIExpression(), !1609)
  %350 = shl i8 %349, 5, !dbg !2008
    #dbg_value(i8 %350, !1603, !DIExpression(), !1609)
  %351 = shl i32 %347, 18, !dbg !2009
  %352 = ashr exact i32 %351, 16, !dbg !2009
  %353 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %352, !dbg !2009
  %354 = load i8, ptr %353, align 4, !dbg !2009, !tbaa !113
  %355 = or i8 %354, %350, !dbg !2010
  store i8 %355, ptr %353, align 4, !dbg !2011, !tbaa !113
  %356 = add nsw i32 %346, 1, !dbg !2012
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  %357 = shl i32 %356, 16, !dbg !2013
  %358 = ashr exact i32 %357, 16, !dbg !2013
  %359 = icmp slt i32 %358, 5, !dbg !2014
  br i1 %359, label %345, label %360, !dbg !2003, !llvm.loop !2015

360:                                              ; preds = %345
  %361 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 4), align 4, !dbg !2017, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2018)
    #dbg_value(ptr %1, !107, !DIExpression(), !2018)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2018)
  store i8 0, ptr %1, align 1, !dbg !2020, !tbaa !113
  br label %526, !dbg !2021

362:                                              ; preds = %3
  %363 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !2022
    #dbg_value(i16 1, !1597, !DIExpression(), !1609)
    #dbg_value(i16 0, !1594, !DIExpression(), !1609)
    #dbg_value(i16 0, !1595, !DIExpression(), !1609)
    #dbg_value(i8 0, !1601, !DIExpression(), !1609)
    #dbg_value(i16 0, !1596, !DIExpression(), !1609)
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  br label %364, !dbg !2025

364:                                              ; preds = %362, %364
  %365 = phi i32 [ 0, %362 ], [ %378, %364 ]
  %366 = phi i32 [ 0, %362 ], [ %376, %364 ]
  %367 = add nsw i32 %365, 5, !dbg !2027
  %368 = getelementptr inbounds [50 x i8], ptr @FONT_5x3, i32 0, i32 %367, !dbg !2030
  %369 = load i8, ptr %368, align 1, !dbg !2030, !tbaa !113
    #dbg_value(i8 %369, !1600, !DIExpression(), !1609)
    #dbg_value(i32 undef, !1599, !DIExpression(DW_OP_constu, 14, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1609)
    #dbg_value(i8 5, !1602, !DIExpression(), !1609)
  %370 = shl i8 %369, 5, !dbg !2031
    #dbg_value(i8 %370, !1603, !DIExpression(), !1609)
  %371 = shl i32 %366, 18, !dbg !2032
  %372 = ashr exact i32 %371, 16, !dbg !2032
  %373 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %372, !dbg !2032
  %374 = load i8, ptr %373, align 4, !dbg !2032, !tbaa !113
  %375 = or i8 %374, %370, !dbg !2033
  store i8 %375, ptr %373, align 4, !dbg !2034, !tbaa !113
  %376 = add nsw i32 %365, 1, !dbg !2035
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  %377 = shl i32 %376, 16, !dbg !2036
  %378 = ashr exact i32 %377, 16, !dbg !2036
  %379 = icmp slt i32 %378, 5, !dbg !2037
  br i1 %379, label %364, label %380, !dbg !2025, !llvm.loop !2038

380:                                              ; preds = %364
  %381 = load i8, ptr @shared_fb, align 16, !dbg !2040, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2041)
    #dbg_value(ptr %1, !107, !DIExpression(), !2041)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2041)
  store i8 0, ptr %1, align 1, !dbg !2043, !tbaa !113
  br label %526, !dbg !2044

382:                                              ; preds = %3
  %383 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !2045
    #dbg_value(i16 42, !1598, !DIExpression(), !1609)
    #dbg_value(i16 2, !1605, !DIExpression(), !2046)
    #dbg_value(i16 4, !1608, !DIExpression(), !2046)
    #dbg_value(i16 0, !1594, !DIExpression(), !1609)
    #dbg_value(i16 0, !1595, !DIExpression(), !1609)
    #dbg_value(i8 0, !1601, !DIExpression(), !1609)
    #dbg_value(i16 0, !1596, !DIExpression(), !1609)
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  br label %384, !dbg !2047

384:                                              ; preds = %382, %384
  %385 = phi i32 [ 0, %382 ], [ %398, %384 ]
  %386 = phi i32 [ 0, %382 ], [ %396, %384 ]
  %387 = add nsw i32 %385, 20, !dbg !2049
  %388 = getelementptr inbounds [50 x i8], ptr @FONT_5x3, i32 0, i32 %387, !dbg !2052
  %389 = load i8, ptr %388, align 1, !dbg !2052, !tbaa !113
    #dbg_value(i8 %389, !1600, !DIExpression(), !1609)
    #dbg_value(i32 undef, !1599, !DIExpression(DW_OP_constu, 14, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1609)
    #dbg_value(i8 5, !1602, !DIExpression(), !1609)
  %390 = shl i8 %389, 5, !dbg !2053
    #dbg_value(i8 %390, !1603, !DIExpression(), !1609)
  %391 = shl i32 %386, 18, !dbg !2054
  %392 = ashr exact i32 %391, 16, !dbg !2054
  %393 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %392, !dbg !2054
  %394 = load i8, ptr %393, align 4, !dbg !2054, !tbaa !113
  %395 = or i8 %394, %390, !dbg !2055
  store i8 %395, ptr %393, align 4, !dbg !2056, !tbaa !113
  %396 = add nsw i32 %385, 1, !dbg !2057
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  %397 = shl i32 %396, 16, !dbg !2058
  %398 = ashr exact i32 %397, 16, !dbg !2058
  %399 = icmp slt i32 %398, 5, !dbg !2059
  br i1 %399, label %384, label %400, !dbg !2047, !llvm.loop !2060

400:                                              ; preds = %384, %400
  %401 = phi i32 [ %415, %400 ], [ 0, %384 ]
  %402 = phi i32 [ %413, %400 ], [ 0, %384 ]
  %403 = add nsw i32 %401, 10, !dbg !2062
  %404 = getelementptr inbounds [50 x i8], ptr @FONT_5x3, i32 0, i32 %403, !dbg !2066
  %405 = load i8, ptr %404, align 1, !dbg !2066, !tbaa !113
    #dbg_value(i8 %405, !1600, !DIExpression(), !1609)
    #dbg_value(i32 undef, !1599, !DIExpression(DW_OP_constu, 14, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1609)
    #dbg_value(i8 1, !1602, !DIExpression(), !1609)
  %406 = shl i8 %405, 1, !dbg !2067
  %407 = and i8 %406, 14, !dbg !2067
    #dbg_value(i8 %407, !1603, !DIExpression(), !1609)
  %408 = shl i32 %402, 18, !dbg !2068
  %409 = ashr exact i32 %408, 16, !dbg !2068
  %410 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %409, !dbg !2068
  %411 = load i8, ptr %410, align 4, !dbg !2068, !tbaa !113
  %412 = or i8 %407, %411, !dbg !2069
  store i8 %412, ptr %410, align 4, !dbg !2070, !tbaa !113
  %413 = add nsw i32 %401, 1, !dbg !2071
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  %414 = shl i32 %413, 16, !dbg !2072
  %415 = ashr exact i32 %414, 16, !dbg !2072
  %416 = icmp slt i32 %415, 5, !dbg !2073
  br i1 %416, label %400, label %417, !dbg !2074, !llvm.loop !2075

417:                                              ; preds = %400, %417
  %418 = phi i32 [ %426, %417 ], [ 0, %400 ]
  %419 = phi i16 [ %423, %417 ], [ 0, %400 ]
    #dbg_value(i16 %419, !1495, !DIExpression(), !2077)
  %420 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %418, !dbg !2079
  %421 = load i8, ptr %420, align 1, !dbg !2079, !tbaa !113
  %422 = zext i8 %421 to i16, !dbg !2079
  %423 = add i16 %419, %422, !dbg !2080
    #dbg_value(i16 %423, !1495, !DIExpression(), !2077)
    #dbg_value(i16 poison, !1494, !DIExpression(), !2077)
  %424 = shl nsw i32 %418, 16, !dbg !2081
  %425 = add i32 %424, 65536, !dbg !2081
  %426 = ashr exact i32 %425, 16, !dbg !2081
  %427 = icmp slt i32 %426, 32, !dbg !2082
  br i1 %427, label %417, label %428, !dbg !2083, !llvm.loop !2084

428:                                              ; preds = %417
    #dbg_value(ptr %0, !106, !DIExpression(), !2086)
    #dbg_value(ptr %1, !107, !DIExpression(), !2086)
    #dbg_value(i16 %423, !108, !DIExpression(), !2086)
  %429 = lshr i16 %423, 8, !dbg !2088
  %430 = trunc nuw i16 %429 to i8, !dbg !2089
  store i8 %430, ptr %1, align 1, !dbg !2090, !tbaa !113
  %431 = trunc i16 %423 to i8, !dbg !2091
  br label %526

432:                                              ; preds = %3
  %433 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !2092
    #dbg_value(i16 8, !1534, !DIExpression(), !2095)
    #dbg_value(i16 2, !1535, !DIExpression(), !2095)
    #dbg_value(i16 3, !1536, !DIExpression(), !2095)
    #dbg_value(i16 8, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !2095)
    #dbg_value(i16 0, !1537, !DIExpression(), !2095)
    #dbg_value(i16 poison, !1537, !DIExpression(), !2095)
  br label %434, !dbg !2097

434:                                              ; preds = %447, %432
  %435 = phi i32 [ 0, %432 ], [ %450, %447 ]
  %436 = add nsw i32 %435, 2, !dbg !2098
  %437 = icmp ugt i32 %436, 7, !dbg !2099
  br i1 %437, label %447, label %438, !dbg !2099

438:                                              ; preds = %434
    #dbg_value(i8 poison, !1539, !DIExpression(), !2095)
    #dbg_value(i32 %436, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 1, DW_OP_or, DW_OP_stack_value), !2095)
    #dbg_value(!DIArgList(i8 5, i16 0), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !2095)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2095)
    #dbg_value(i32 %436, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 1, DW_OP_or, DW_OP_stack_value), !2095)
  %439 = shl nuw nsw i32 %436, 2, !dbg !2100
    #dbg_value(i32 %436, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 1, DW_OP_or, DW_OP_stack_value), !2095)
  %440 = or disjoint i32 %439, 1, !dbg !2100
  %441 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %435, !dbg !2101
  %442 = load i8, ptr %441, align 1, !dbg !2101, !tbaa !113
    #dbg_value(i8 %442, !1539, !DIExpression(), !2095)
    #dbg_value(!DIArgList(i8 %442, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2095)
    #dbg_value(!DIArgList(i8 %442, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2095)
    #dbg_value(!DIArgList(i8 %442, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2095)
    #dbg_value(!DIArgList(i8 %442, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2095)
    #dbg_value(!DIArgList(i8 %442, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2095)
    #dbg_value(!DIArgList(i8 %442, i32 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2095)
  %443 = shl i8 %442, 5, !dbg !2102
    #dbg_value(i8 %443, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2095)
  %444 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %440, !dbg !2103
  %445 = load i8, ptr %444, align 1, !dbg !2103, !tbaa !113
  %446 = or i8 %445, %443, !dbg !2104
  store i8 %446, ptr %444, align 1, !dbg !2105, !tbaa !113
  br label %447, !dbg !2106

447:                                              ; preds = %438, %434
    #dbg_value(i16 poison, !1537, !DIExpression(), !2095)
  %448 = shl nsw i32 %435, 16, !dbg !2107
  %449 = add i32 %448, 65536, !dbg !2107
  %450 = ashr exact i32 %449, 16, !dbg !2107
  %451 = icmp slt i32 %450, 3, !dbg !2108
  br i1 %451, label %434, label %452, !dbg !2097, !llvm.loop !2109

452:                                              ; preds = %447, %452
  %453 = phi i32 [ %466, %452 ], [ 0, %447 ]
  %454 = phi i32 [ %464, %452 ], [ 0, %447 ]
  %455 = add nsw i32 %453, 25, !dbg !2111
  %456 = getelementptr inbounds [50 x i8], ptr @FONT_5x3, i32 0, i32 %455, !dbg !2115
  %457 = load i8, ptr %456, align 1, !dbg !2115, !tbaa !113
    #dbg_value(i8 %457, !1600, !DIExpression(), !1609)
    #dbg_value(i32 undef, !1599, !DIExpression(DW_OP_constu, 14, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !1609)
    #dbg_value(i8 5, !1602, !DIExpression(), !1609)
  %458 = shl i8 %457, 5, !dbg !2116
    #dbg_value(i8 %458, !1603, !DIExpression(), !1609)
  %459 = shl i32 %454, 18, !dbg !2117
  %460 = ashr exact i32 %459, 16, !dbg !2117
  %461 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %460, !dbg !2117
  %462 = load i8, ptr %461, align 4, !dbg !2117, !tbaa !113
  %463 = or i8 %462, %458, !dbg !2118
  store i8 %463, ptr %461, align 4, !dbg !2119, !tbaa !113
  %464 = add nsw i32 %453, 1, !dbg !2120
    #dbg_value(i16 poison, !1596, !DIExpression(), !1609)
  %465 = shl i32 %464, 16, !dbg !2121
  %466 = ashr exact i32 %465, 16, !dbg !2121
  %467 = icmp slt i32 %466, 5, !dbg !2122
  br i1 %467, label %452, label %468, !dbg !2123, !llvm.loop !2124

468:                                              ; preds = %452, %468
  %469 = phi i32 [ %477, %468 ], [ 0, %452 ]
  %470 = phi i16 [ %474, %468 ], [ 0, %452 ]
    #dbg_value(i16 %470, !1495, !DIExpression(), !2126)
  %471 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %469, !dbg !2128
  %472 = load i8, ptr %471, align 1, !dbg !2128, !tbaa !113
  %473 = zext i8 %472 to i16, !dbg !2128
  %474 = add i16 %470, %473, !dbg !2129
    #dbg_value(i16 %474, !1495, !DIExpression(), !2126)
    #dbg_value(i16 poison, !1494, !DIExpression(), !2126)
  %475 = shl nsw i32 %469, 16, !dbg !2130
  %476 = add i32 %475, 65536, !dbg !2130
  %477 = ashr exact i32 %476, 16, !dbg !2130
  %478 = icmp slt i32 %477, 32, !dbg !2131
  br i1 %478, label %468, label %479, !dbg !2132, !llvm.loop !2133

479:                                              ; preds = %468
    #dbg_value(ptr %0, !106, !DIExpression(), !2135)
    #dbg_value(ptr %1, !107, !DIExpression(), !2135)
    #dbg_value(i16 %474, !108, !DIExpression(), !2135)
  %480 = lshr i16 %474, 8, !dbg !2137
  %481 = trunc nuw i16 %480 to i8, !dbg !2138
  store i8 %481, ptr %1, align 1, !dbg !2139, !tbaa !113
  %482 = trunc i16 %474 to i8, !dbg !2140
  br label %526, !dbg !2141

483:                                              ; preds = %3
  %484 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !2142
    #dbg_value(i16 24, !1534, !DIExpression(), !2145)
    #dbg_value(i16 0, !1535, !DIExpression(), !2145)
    #dbg_value(i16 3, !1536, !DIExpression(), !2145)
    #dbg_value(i16 24, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !2145)
    #dbg_value(i16 0, !1537, !DIExpression(), !2145)
    #dbg_value(i16 poison, !1537, !DIExpression(), !2145)
  br label %485, !dbg !2147

485:                                              ; preds = %497, %483
  %486 = phi i32 [ 0, %483 ], [ %500, %497 ]
  %487 = icmp ugt i32 %486, 7, !dbg !2148
  br i1 %487, label %497, label %488, !dbg !2148

488:                                              ; preds = %485
    #dbg_value(i8 poison, !1539, !DIExpression(), !2145)
    #dbg_value(i32 %486, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 3, DW_OP_or, DW_OP_stack_value), !2145)
    #dbg_value(!DIArgList(i8 5, i16 0), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !2145)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2145)
    #dbg_value(i32 %486, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 3, DW_OP_or, DW_OP_stack_value), !2145)
  %489 = shl nuw nsw i32 %486, 2, !dbg !2149
    #dbg_value(i32 %486, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 3, DW_OP_or, DW_OP_stack_value), !2145)
  %490 = or disjoint i32 %489, 3, !dbg !2149
  %491 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %486, !dbg !2150
  %492 = load i8, ptr %491, align 1, !dbg !2150, !tbaa !113
    #dbg_value(i8 %492, !1539, !DIExpression(), !2145)
    #dbg_value(!DIArgList(i8 %492, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2145)
    #dbg_value(!DIArgList(i8 %492, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2145)
    #dbg_value(!DIArgList(i8 %492, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2145)
    #dbg_value(!DIArgList(i8 %492, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2145)
    #dbg_value(!DIArgList(i8 %492, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2145)
    #dbg_value(!DIArgList(i8 %492, i32 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2145)
  %493 = shl i8 %492, 5, !dbg !2151
    #dbg_value(i8 %493, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2145)
  %494 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %490, !dbg !2152
  %495 = load i8, ptr %494, align 1, !dbg !2152, !tbaa !113
  %496 = or i8 %495, %493, !dbg !2153
  store i8 %496, ptr %494, align 1, !dbg !2154, !tbaa !113
  br label %497, !dbg !2155

497:                                              ; preds = %488, %485
    #dbg_value(i16 poison, !1537, !DIExpression(), !2145)
  %498 = shl nsw i32 %486, 16, !dbg !2156
  %499 = add i32 %498, 65536, !dbg !2156
  %500 = ashr exact i32 %499, 16, !dbg !2156
  %501 = icmp slt i32 %500, 3, !dbg !2157
  br i1 %501, label %485, label %502, !dbg !2147, !llvm.loop !2158

502:                                              ; preds = %497
  %503 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !2160, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2161)
    #dbg_value(ptr %1, !107, !DIExpression(), !2161)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2161)
  store i8 0, ptr %1, align 1, !dbg !2163, !tbaa !113
  br label %526, !dbg !2164

504:                                              ; preds = %3
  %505 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 32, i8 noundef signext 0) #11, !dbg !2165
    #dbg_value(i16 24, !1534, !DIExpression(), !2168)
    #dbg_value(i16 0, !1535, !DIExpression(), !2168)
    #dbg_value(i16 3, !1536, !DIExpression(), !2168)
    #dbg_value(i16 24, !1540, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_stack_value), !2168)
    #dbg_value(i16 0, !1537, !DIExpression(), !2168)
    #dbg_value(i16 poison, !1537, !DIExpression(), !2168)
  br label %506, !dbg !2170

506:                                              ; preds = %518, %504
  %507 = phi i32 [ 0, %504 ], [ %521, %518 ]
  %508 = icmp ugt i32 %507, 7, !dbg !2171
  br i1 %508, label %518, label %509, !dbg !2171

509:                                              ; preds = %506
    #dbg_value(i8 poison, !1539, !DIExpression(), !2168)
    #dbg_value(i32 %507, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 3, DW_OP_or, DW_OP_stack_value), !2168)
    #dbg_value(!DIArgList(i8 5, i16 0), !1541, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_minus, DW_OP_stack_value), !2168)
    #dbg_value(!DIArgList(i8 poison, i16 poison, i16 poison), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2168)
    #dbg_value(i32 %507, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 3, DW_OP_or, DW_OP_stack_value), !2168)
  %510 = shl nuw nsw i32 %507, 2, !dbg !2172
    #dbg_value(i32 %507, !1538, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_constu, 2, DW_OP_shl, DW_OP_constu, 3, DW_OP_or, DW_OP_stack_value), !2168)
  %511 = or disjoint i32 %510, 3, !dbg !2172
  %512 = getelementptr inbounds [3 x i8], ptr @BIRD_SPRITE, i32 0, i32 %507, !dbg !2173
  %513 = load i8, ptr %512, align 1, !dbg !2173, !tbaa !113
    #dbg_value(i8 %513, !1539, !DIExpression(), !2168)
    #dbg_value(!DIArgList(i8 %513, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2168)
    #dbg_value(!DIArgList(i8 %513, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2168)
    #dbg_value(!DIArgList(i8 %513, i16 5, i16 0), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2168)
    #dbg_value(!DIArgList(i8 %513, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_constu, 255, DW_OP_and, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2168)
    #dbg_value(!DIArgList(i8 %513, i16 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2168)
    #dbg_value(!DIArgList(i8 %513, i32 5), !1542, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2168)
  %514 = shl i8 %513, 5, !dbg !2174
    #dbg_value(i8 %514, !1542, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_stack_value), !2168)
  %515 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %511, !dbg !2175
  %516 = load i8, ptr %515, align 1, !dbg !2175, !tbaa !113
  %517 = or i8 %516, %514, !dbg !2176
  store i8 %517, ptr %515, align 1, !dbg !2177, !tbaa !113
  br label %518, !dbg !2178

518:                                              ; preds = %509, %506
    #dbg_value(i16 poison, !1537, !DIExpression(), !2168)
  %519 = shl nsw i32 %507, 16, !dbg !2179
  %520 = add i32 %519, 65536, !dbg !2179
  %521 = ashr exact i32 %520, 16, !dbg !2179
  %522 = icmp slt i32 %521, 3, !dbg !2180
  br i1 %522, label %506, label %523, !dbg !2170, !llvm.loop !2181

523:                                              ; preds = %518
  %524 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 3), align 1, !dbg !2183, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2184)
    #dbg_value(ptr %1, !107, !DIExpression(), !2184)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2184)
  store i8 0, ptr %1, align 1, !dbg !2186, !tbaa !113
  br label %526, !dbg !2187

525:                                              ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2188)
    #dbg_value(ptr %1, !107, !DIExpression(), !2188)
    #dbg_value(i16 -1, !108, !DIExpression(), !2188)
  store i8 -1, ptr %1, align 1, !dbg !2190, !tbaa !113
  br label %526, !dbg !2191

526:                                              ; preds = %525, %523, %502, %479, %428, %380, %360, %341, %322, %299, %249, %223, %197, %171, %145, %125, %102, %71, %51, %29, %25, %21, %17
  %527 = phi i8 [ -1, %525 ], [ %524, %523 ], [ %503, %502 ], [ %482, %479 ], [ %431, %428 ], [ %381, %380 ], [ %361, %360 ], [ %342, %341 ], [ %323, %322 ], [ %302, %299 ], [ %250, %249 ], [ %224, %223 ], [ %198, %197 ], [ %172, %171 ], [ %146, %145 ], [ %126, %125 ], [ %105, %102 ], [ %72, %71 ], [ %52, %51 ], [ %32, %29 ], [ %28, %25 ], [ %24, %21 ], [ %20, %17 ]
  %528 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !2192
  store i8 %527, ptr %528, align 1, !dbg !2193, !tbaa !113
  %529 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !2194
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !2195
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !2196
  ret void, !dbg !2191
}

; Function Attrs: nofree norecurse nosync nounwind memory(read, argmem: none, inaccessiblemem: none)
define hidden signext i16 @frame1_checksum() local_unnamed_addr #3 !dbg !2197 {
    #dbg_value(i16 0, !2201, !DIExpression(), !2202)
    #dbg_value(i16 0, !2200, !DIExpression(), !2202)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2202)
  br label %1, !dbg !2203

1:                                                ; preds = %0, %1
  %2 = phi i32 [ 0, %0 ], [ %10, %1 ]
  %3 = phi i16 [ 0, %0 ], [ %7, %1 ]
    #dbg_value(i16 %3, !2201, !DIExpression(), !2202)
  %4 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %2, !dbg !2205
  %5 = load i8, ptr %4, align 1, !dbg !2205, !tbaa !113
  %6 = zext i8 %5 to i16, !dbg !2205
  %7 = add i16 %3, %6, !dbg !2208
    #dbg_value(i16 %7, !2201, !DIExpression(), !2202)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2202)
  %8 = shl nsw i32 %2, 16, !dbg !2209
  %9 = add i32 %8, 65536, !dbg !2209
  %10 = ashr exact i32 %9, 16, !dbg !2209
  %11 = icmp slt i32 %10, 80, !dbg !2210
  br i1 %11, label %1, label %12, !dbg !2203, !llvm.loop !2211

12:                                               ; preds = %1
  ret i16 %7, !dbg !2213
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden void @frame1_setPixel(i16 noundef signext %0, i16 noundef signext %1, i8 noundef signext %2) local_unnamed_addr #5 !dbg !2214 {
    #dbg_value(i16 %0, !2216, !DIExpression(), !2221)
    #dbg_value(i16 %1, !2217, !DIExpression(), !2221)
    #dbg_value(i8 %2, !2218, !DIExpression(), !2221)
  %4 = icmp ugt i16 %0, 31, !dbg !2222
  %5 = icmp ugt i16 %1, 19, !dbg !2222
  %6 = or i1 %4, %5, !dbg !2222
  br i1 %6, label %22, label %7, !dbg !2222

7:                                                ; preds = %3
  %8 = shl nuw nsw i16 %1, 2, !dbg !2224
  %9 = lshr i16 %0, 3, !dbg !2225
  %10 = or disjoint i16 %8, %9, !dbg !2226
    #dbg_value(i16 %10, !2219, !DIExpression(), !2221)
  %11 = trunc nuw i16 %0 to i8, !dbg !2227
  %12 = and i8 %11, 7, !dbg !2227
  %13 = lshr exact i8 -128, %12, !dbg !2228
    #dbg_value(i8 %13, !2220, !DIExpression(), !2221)
  %14 = icmp eq i8 %2, 0, !dbg !2229
  %15 = zext nneg i16 %10 to i32, !dbg !2231
  %16 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %15, !dbg !2231
  %17 = load i8, ptr %16, align 1, !dbg !2231, !tbaa !113
  %18 = or i8 %17, %13, !dbg !2232
  %19 = xor i8 %13, -1, !dbg !2232
  %20 = and i8 %17, %19, !dbg !2232
  %21 = select i1 %14, i8 %20, i8 %18, !dbg !2232
  store i8 %21, ptr %16, align 1, !dbg !2231, !tbaa !113
  br label %22, !dbg !2233

22:                                               ; preds = %7, %3
  ret void, !dbg !2233
}

; Function Attrs: nounwind
define hidden void @frame1_fillRect(i16 noundef signext %0, i16 noundef signext %1, i16 noundef signext %2, i16 noundef signext %3, i8 noundef signext %4) local_unnamed_addr #0 !dbg !2234 {
    #dbg_value(i16 %0, !2238, !DIExpression(), !2252)
    #dbg_value(i16 %1, !2239, !DIExpression(), !2252)
    #dbg_value(i16 %2, !2240, !DIExpression(), !2252)
    #dbg_value(i16 %3, !2241, !DIExpression(), !2252)
    #dbg_value(i8 %4, !2242, !DIExpression(), !2252)
  %6 = or i16 %3, %2, !dbg !2253
  %7 = icmp slt i16 %6, 0, !dbg !2253
  %8 = icmp sgt i16 %0, 31
  %9 = or i1 %8, %7, !dbg !2253
  %10 = icmp sgt i16 %1, 19
  %11 = or i1 %10, %9, !dbg !2253
  br i1 %11, label %88, label %12, !dbg !2253

12:                                               ; preds = %5
  %13 = tail call i16 @llvm.smax.i16(i16 %0, i16 0), !dbg !2255
    #dbg_value(i16 %13, !2238, !DIExpression(), !2252)
  %14 = tail call i16 @llvm.smax.i16(i16 %1, i16 0), !dbg !2256
    #dbg_value(i16 %14, !2239, !DIExpression(), !2252)
  %15 = tail call i16 @llvm.smin.i16(i16 %2, i16 31), !dbg !2257
    #dbg_value(i16 %15, !2240, !DIExpression(), !2252)
  %16 = tail call i16 @llvm.smin.i16(i16 %3, i16 19), !dbg !2258
    #dbg_value(i16 %16, !2241, !DIExpression(), !2252)
  %17 = lshr i16 %13, 3, !dbg !2259
    #dbg_value(i16 %17, !2245, !DIExpression(), !2252)
  %18 = lshr i16 %15, 3, !dbg !2260
    #dbg_value(i16 %18, !2246, !DIExpression(), !2252)
  %19 = and i16 %13, 7, !dbg !2261
  %20 = lshr i16 255, %19, !dbg !2262
  %21 = trunc nuw i16 %20 to i8, !dbg !2263
    #dbg_value(i8 %21, !2248, !DIExpression(), !2252)
  %22 = and i16 %15, 7, !dbg !2264
  %23 = xor i16 %22, 7, !dbg !2265
  %24 = shl nuw nsw i16 255, %23, !dbg !2266
  %25 = trunc i16 %24 to i8, !dbg !2267
    #dbg_value(i8 %25, !2249, !DIExpression(), !2252)
  %26 = icmp ne i8 %4, 0, !dbg !2268
  %27 = sext i1 %26 to i8, !dbg !2268
    #dbg_value(i8 %27, !2250, !DIExpression(), !2252)
  %28 = icmp slt i16 %0, 1, !dbg !2269
  %29 = icmp sgt i16 %2, 30
  %30 = and i1 %28, %29, !dbg !2271
  br i1 %30, label %31, label %37, !dbg !2271

31:                                               ; preds = %12
  %32 = shl i16 %14, 2, !dbg !2272
  %33 = sub nsw i16 %16, %14, !dbg !2272
  %34 = shl i16 %33, 2, !dbg !2272
  %35 = add i16 %34, 4, !dbg !2272
  %36 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext %32, i16 noundef signext %35, i8 noundef signext %27) #11, !dbg !2272
  br label %88, !dbg !2274

37:                                               ; preds = %12
  %38 = zext nneg i16 %18 to i32, !dbg !2275
  %39 = zext nneg i16 %17 to i32, !dbg !2276
  %40 = xor i16 %17, -1, !dbg !2277
  %41 = add nsw i16 %18, %40, !dbg !2277
    #dbg_value(i16 %41, !2247, !DIExpression(), !2252)
    #dbg_value(i16 %14, !2243, !DIExpression(), !2252)
  %42 = icmp sgt i16 %14, %16, !dbg !2278
  br i1 %42, label %88, label %43, !dbg !2281

43:                                               ; preds = %37
  %44 = icmp eq i16 %17, %18
  %45 = icmp eq i8 %4, 0
  %46 = xor i8 %21, -1
  %47 = icmp sgt i16 %41, 0
  %48 = add nuw nsw i16 %17, 1
  %49 = xor i8 %25, -1
  %50 = and i16 %24, %20
  %51 = trunc nuw i16 %50 to i8
  %52 = xor i8 %51, -1
  %53 = zext nneg i16 %14 to i32, !dbg !2281
  %54 = add nsw i16 %16, 1, !dbg !2281
  %55 = sext i16 %54 to i32, !dbg !2278
  br label %56, !dbg !2281

56:                                               ; preds = %43, %85
  %57 = phi i32 [ %53, %43 ], [ %86, %85 ]
    #dbg_value(i32 %57, !2243, !DIExpression(), !2252)
  %58 = trunc nuw nsw i32 %57 to i16, !dbg !2282
  %59 = shl i16 %58, 2, !dbg !2282
    #dbg_value(i16 %59, !2244, !DIExpression(), !2252)
  %60 = sext i16 %59 to i32, !dbg !2284
  %61 = add nsw i32 %60, %39, !dbg !2284
  %62 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %61, !dbg !2284
  %63 = load i8, ptr %62, align 1, !dbg !2284, !tbaa !113
  br i1 %44, label %64, label %69, !dbg !2286

64:                                               ; preds = %56
    #dbg_value(i8 %51, !2251, !DIExpression(), !2252)
  br i1 %45, label %67, label %65, !dbg !2287

65:                                               ; preds = %64
  %66 = or i8 %63, %51, !dbg !2289
  store i8 %66, ptr %62, align 1, !dbg !2289, !tbaa !113
  br label %85, !dbg !2291

67:                                               ; preds = %64
  %68 = and i8 %63, %52, !dbg !2292
  store i8 %68, ptr %62, align 1, !dbg !2292, !tbaa !113
  br label %85

69:                                               ; preds = %56
  %70 = and i8 %63, %46, !dbg !2293
  %71 = or i8 %63, %21, !dbg !2293
  %72 = select i1 %45, i8 %70, i8 %71, !dbg !2293
  store i8 %72, ptr %62, align 1, !dbg !2295, !tbaa !113
  br i1 %47, label %73, label %76, !dbg !2297

73:                                               ; preds = %69
  %74 = add i16 %48, %59, !dbg !2298
  %75 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext %74, i16 noundef signext %41, i8 noundef signext %27) #11, !dbg !2298
  br label %76, !dbg !2301

76:                                               ; preds = %73, %69
  %77 = sext i16 %59 to i32, !dbg !2302
  %78 = or disjoint i32 %77, %38, !dbg !2302
  %79 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %78, !dbg !2302
  %80 = load i8, ptr %79, align 1, !dbg !2302, !tbaa !113
  br i1 %45, label %83, label %81, !dbg !2304

81:                                               ; preds = %76
  %82 = or i8 %80, %25, !dbg !2305
  store i8 %82, ptr %79, align 1, !dbg !2305, !tbaa !113
  br label %85, !dbg !2306

83:                                               ; preds = %76
  %84 = and i8 %80, %49, !dbg !2307
  store i8 %84, ptr %79, align 1, !dbg !2307, !tbaa !113
  br label %85

85:                                               ; preds = %67, %65, %83, %81
  %86 = add nuw nsw i32 %57, 1, !dbg !2308
    #dbg_value(i32 %86, !2243, !DIExpression(), !2252)
  %87 = icmp eq i32 %86, %55, !dbg !2278
  br i1 %87, label %88, label %56, !dbg !2281, !llvm.loop !2309

88:                                               ; preds = %85, %37, %5, %31
  ret void, !dbg !2311
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden void @frame1_render_ready_screen() local_unnamed_addr #6 !dbg !2312 {
    #dbg_value(i16 10, !2314, !DIExpression(), !2317)
    #dbg_value(i16 8, !2315, !DIExpression(), !2317)
    #dbg_value(i16 3, !2316, !DIExpression(), !2317)
    #dbg_value(i16 8, !2238, !DIExpression(), !2318)
    #dbg_value(i16 9, !2239, !DIExpression(), !2318)
    #dbg_value(i16 10, !2240, !DIExpression(), !2318)
    #dbg_value(i16 11, !2241, !DIExpression(), !2318)
    #dbg_value(i8 1, !2242, !DIExpression(), !2318)
    #dbg_value(i16 8, !2238, !DIExpression(), !2318)
    #dbg_value(i16 9, !2239, !DIExpression(), !2318)
    #dbg_value(i16 10, !2240, !DIExpression(), !2318)
    #dbg_value(i16 11, !2241, !DIExpression(), !2318)
    #dbg_value(i16 1, !2245, !DIExpression(), !2318)
    #dbg_value(i16 1, !2246, !DIExpression(), !2318)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2318)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2318)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2318)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2318)
    #dbg_value(i16 9, !2243, !DIExpression(), !2318)
  br label %1, !dbg !2320

1:                                                ; preds = %1, %0
  %2 = phi i32 [ 9, %0 ], [ %10, %1 ]
    #dbg_value(i32 %2, !2243, !DIExpression(), !2318)
  %3 = trunc nuw nsw i32 %2 to i16, !dbg !2321
  %4 = shl i16 %3, 2, !dbg !2321
    #dbg_value(i16 %4, !2244, !DIExpression(), !2318)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2318)
  %5 = or disjoint i16 %4, 1, !dbg !2322
  %6 = sext i16 %5 to i32, !dbg !2322
  %7 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %6, !dbg !2323
  %8 = load i8, ptr %7, align 1, !dbg !2324, !tbaa !113
  %9 = or i8 %8, -32, !dbg !2324
  store i8 %9, ptr %7, align 1, !dbg !2324, !tbaa !113
  %10 = add nuw nsw i32 %2, 1, !dbg !2325
    #dbg_value(i32 %10, !2243, !DIExpression(), !2318)
  %11 = icmp eq i32 %10, 12, !dbg !2326
  br i1 %11, label %12, label %1, !dbg !2320, !llvm.loop !2327

12:                                               ; preds = %1
    #dbg_value(i16 9, !2216, !DIExpression(), !2329)
    #dbg_value(i16 6, !2217, !DIExpression(), !2329)
    #dbg_value(i8 1, !2218, !DIExpression(), !2329)
    #dbg_value(i16 25, !2219, !DIExpression(), !2329)
    #dbg_value(i8 64, !2220, !DIExpression(), !2329)
  %13 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2331, !tbaa !113
  %14 = or i8 %13, 64, !dbg !2332
  store i8 %14, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2333, !tbaa !113
    #dbg_value(i16 8, !2216, !DIExpression(), !2334)
    #dbg_value(i16 7, !2217, !DIExpression(), !2334)
    #dbg_value(i8 1, !2218, !DIExpression(), !2334)
    #dbg_value(i16 29, !2219, !DIExpression(), !2334)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2334)
  %15 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2336, !tbaa !113
    #dbg_value(i16 9, !2216, !DIExpression(), !2337)
    #dbg_value(i16 7, !2217, !DIExpression(), !2337)
    #dbg_value(i8 1, !2218, !DIExpression(), !2337)
    #dbg_value(i16 29, !2219, !DIExpression(), !2337)
    #dbg_value(i8 64, !2220, !DIExpression(), !2337)
    #dbg_value(i16 10, !2216, !DIExpression(), !2339)
    #dbg_value(i16 7, !2217, !DIExpression(), !2339)
    #dbg_value(i8 1, !2218, !DIExpression(), !2339)
    #dbg_value(i16 29, !2219, !DIExpression(), !2339)
    #dbg_value(i8 32, !2220, !DIExpression(), !2339)
  %16 = or i8 %15, -32, !dbg !2341
  store i8 %16, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2342, !tbaa !113
  ret void, !dbg !2343
}

; Function Attrs: nounwind
define hidden void @test_frame1(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !2344 {
    #dbg_value(ptr %0, !2346, !DIExpression(), !2374)
    #dbg_value(ptr %1, !2347, !DIExpression(), !2374)
    #dbg_value(i8 %2, !2348, !DIExpression(), !2374)
  switch i8 %2, label %221 [
    i8 0, label %4
    i8 1, label %37
    i8 2, label %54
    i8 3, label %82
    i8 4, label %103
    i8 5, label %121
    i8 6, label %139
    i8 7, label %158
    i8 8, label %177
    i8 10, label %196
    i8 11, label %200
    i8 12, label %204
    i8 13, label %208
    i8 14, label %212
    i8 15, label %213
    i8 16, label %217
    i8 17, label %218
    i8 18, label %219
    i8 19, label %220
  ], !dbg !2375

4:                                                ; preds = %3
  %5 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2376
    #dbg_value(i16 10, !2314, !DIExpression(), !2379)
    #dbg_value(i16 8, !2315, !DIExpression(), !2379)
    #dbg_value(i16 3, !2316, !DIExpression(), !2379)
    #dbg_value(i16 8, !2238, !DIExpression(), !2381)
    #dbg_value(i16 9, !2239, !DIExpression(), !2381)
    #dbg_value(i16 10, !2240, !DIExpression(), !2381)
    #dbg_value(i16 11, !2241, !DIExpression(), !2381)
    #dbg_value(i8 1, !2242, !DIExpression(), !2381)
    #dbg_value(i16 8, !2238, !DIExpression(), !2381)
    #dbg_value(i16 9, !2239, !DIExpression(), !2381)
    #dbg_value(i16 10, !2240, !DIExpression(), !2381)
    #dbg_value(i16 11, !2241, !DIExpression(), !2381)
    #dbg_value(i16 1, !2245, !DIExpression(), !2381)
    #dbg_value(i16 1, !2246, !DIExpression(), !2381)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2381)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2381)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2381)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2381)
    #dbg_value(i16 9, !2243, !DIExpression(), !2381)
  br label %6, !dbg !2383

6:                                                ; preds = %6, %4
  %7 = phi i32 [ 9, %4 ], [ %15, %6 ]
    #dbg_value(i32 %7, !2243, !DIExpression(), !2381)
  %8 = trunc nuw nsw i32 %7 to i16, !dbg !2384
  %9 = shl i16 %8, 2, !dbg !2384
    #dbg_value(i16 %9, !2244, !DIExpression(), !2381)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2381)
  %10 = or disjoint i16 %9, 1, !dbg !2385
  %11 = sext i16 %10 to i32, !dbg !2385
  %12 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %11, !dbg !2386
  %13 = load i8, ptr %12, align 1, !dbg !2387, !tbaa !113
  %14 = or i8 %13, -32, !dbg !2387
  store i8 %14, ptr %12, align 1, !dbg !2387, !tbaa !113
  %15 = add nuw nsw i32 %7, 1, !dbg !2388
    #dbg_value(i32 %15, !2243, !DIExpression(), !2381)
  %16 = icmp eq i32 %15, 12, !dbg !2389
  br i1 %16, label %17, label %6, !dbg !2383, !llvm.loop !2390

17:                                               ; preds = %6
    #dbg_value(i16 9, !2216, !DIExpression(), !2392)
    #dbg_value(i16 6, !2217, !DIExpression(), !2392)
    #dbg_value(i8 1, !2218, !DIExpression(), !2392)
    #dbg_value(i16 25, !2219, !DIExpression(), !2392)
    #dbg_value(i8 64, !2220, !DIExpression(), !2392)
  %18 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2394, !tbaa !113
  %19 = or i8 %18, 64, !dbg !2395
  store i8 %19, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2396, !tbaa !113
    #dbg_value(i16 8, !2216, !DIExpression(), !2397)
    #dbg_value(i16 7, !2217, !DIExpression(), !2397)
    #dbg_value(i8 1, !2218, !DIExpression(), !2397)
    #dbg_value(i16 29, !2219, !DIExpression(), !2397)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2397)
  %20 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2399, !tbaa !113
    #dbg_value(i16 9, !2216, !DIExpression(), !2400)
    #dbg_value(i16 7, !2217, !DIExpression(), !2400)
    #dbg_value(i8 1, !2218, !DIExpression(), !2400)
    #dbg_value(i16 29, !2219, !DIExpression(), !2400)
    #dbg_value(i8 64, !2220, !DIExpression(), !2400)
    #dbg_value(i16 10, !2216, !DIExpression(), !2402)
    #dbg_value(i16 7, !2217, !DIExpression(), !2402)
    #dbg_value(i8 1, !2218, !DIExpression(), !2402)
    #dbg_value(i16 29, !2219, !DIExpression(), !2402)
    #dbg_value(i8 32, !2220, !DIExpression(), !2402)
  %21 = or i8 %20, -32, !dbg !2404
  store i8 %21, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2405, !tbaa !113
    #dbg_value(i16 0, !2201, !DIExpression(), !2406)
    #dbg_value(i16 0, !2200, !DIExpression(), !2406)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2406)
  br label %22, !dbg !2408

22:                                               ; preds = %22, %17
  %23 = phi i32 [ 0, %17 ], [ %31, %22 ]
  %24 = phi i16 [ 0, %17 ], [ %28, %22 ]
    #dbg_value(i16 %24, !2201, !DIExpression(), !2406)
  %25 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %23, !dbg !2409
  %26 = load i8, ptr %25, align 1, !dbg !2409, !tbaa !113
  %27 = zext i8 %26 to i16, !dbg !2409
  %28 = add i16 %24, %27, !dbg !2410
    #dbg_value(i16 %28, !2201, !DIExpression(), !2406)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2406)
  %29 = shl nsw i32 %23, 16, !dbg !2411
  %30 = add i32 %29, 65536, !dbg !2411
  %31 = ashr exact i32 %30, 16, !dbg !2411
  %32 = icmp slt i32 %31, 80, !dbg !2412
  br i1 %32, label %22, label %33, !dbg !2408, !llvm.loop !2413

33:                                               ; preds = %22
    #dbg_value(ptr %0, !106, !DIExpression(), !2415)
    #dbg_value(ptr %1, !107, !DIExpression(), !2415)
    #dbg_value(i16 %28, !108, !DIExpression(), !2415)
  %34 = lshr i16 %28, 8, !dbg !2417
  %35 = trunc nuw i16 %34 to i8, !dbg !2418
  store i8 %35, ptr %1, align 1, !dbg !2419, !tbaa !113
  %36 = trunc i16 %28 to i8, !dbg !2420
  br label %222, !dbg !2421

37:                                               ; preds = %3
  %38 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2422
    #dbg_value(i16 0, !2201, !DIExpression(), !2425)
    #dbg_value(i16 0, !2200, !DIExpression(), !2425)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2425)
  br label %39, !dbg !2427

39:                                               ; preds = %39, %37
  %40 = phi i32 [ 0, %37 ], [ %48, %39 ]
  %41 = phi i16 [ 0, %37 ], [ %45, %39 ]
    #dbg_value(i16 %41, !2201, !DIExpression(), !2425)
  %42 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %40, !dbg !2428
  %43 = load i8, ptr %42, align 1, !dbg !2428, !tbaa !113
  %44 = zext i8 %43 to i16, !dbg !2428
  %45 = add i16 %41, %44, !dbg !2429
    #dbg_value(i16 %45, !2201, !DIExpression(), !2425)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2425)
  %46 = shl nsw i32 %40, 16, !dbg !2430
  %47 = add i32 %46, 65536, !dbg !2430
  %48 = ashr exact i32 %47, 16, !dbg !2430
  %49 = icmp slt i32 %48, 80, !dbg !2431
  br i1 %49, label %39, label %50, !dbg !2427, !llvm.loop !2432

50:                                               ; preds = %39
    #dbg_value(ptr %0, !106, !DIExpression(), !2434)
    #dbg_value(ptr %1, !107, !DIExpression(), !2434)
    #dbg_value(i16 %45, !108, !DIExpression(), !2434)
  %51 = lshr i16 %45, 8, !dbg !2436
  %52 = trunc nuw i16 %51 to i8, !dbg !2437
  store i8 %52, ptr %1, align 1, !dbg !2438, !tbaa !113
  %53 = trunc i16 %45 to i8, !dbg !2439
  br label %222, !dbg !2440

54:                                               ; preds = %3
  %55 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2441
    #dbg_value(i16 8, !2238, !DIExpression(), !2444)
    #dbg_value(i16 9, !2239, !DIExpression(), !2444)
    #dbg_value(i16 10, !2240, !DIExpression(), !2444)
    #dbg_value(i16 11, !2241, !DIExpression(), !2444)
    #dbg_value(i8 1, !2242, !DIExpression(), !2444)
    #dbg_value(i16 8, !2238, !DIExpression(), !2444)
    #dbg_value(i16 9, !2239, !DIExpression(), !2444)
    #dbg_value(i16 10, !2240, !DIExpression(), !2444)
    #dbg_value(i16 11, !2241, !DIExpression(), !2444)
    #dbg_value(i16 1, !2245, !DIExpression(), !2444)
    #dbg_value(i16 1, !2246, !DIExpression(), !2444)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2444)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2444)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2444)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2444)
    #dbg_value(i16 9, !2243, !DIExpression(), !2444)
  br label %56, !dbg !2446

56:                                               ; preds = %56, %54
  %57 = phi i32 [ 9, %54 ], [ %65, %56 ]
    #dbg_value(i32 %57, !2243, !DIExpression(), !2444)
  %58 = trunc nuw nsw i32 %57 to i16, !dbg !2447
  %59 = shl i16 %58, 2, !dbg !2447
    #dbg_value(i16 %59, !2244, !DIExpression(), !2444)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2444)
  %60 = or disjoint i16 %59, 1, !dbg !2448
  %61 = sext i16 %60 to i32, !dbg !2448
  %62 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %61, !dbg !2449
  %63 = load i8, ptr %62, align 1, !dbg !2450, !tbaa !113
  %64 = or i8 %63, -32, !dbg !2450
  store i8 %64, ptr %62, align 1, !dbg !2450, !tbaa !113
  %65 = add nuw nsw i32 %57, 1, !dbg !2451
    #dbg_value(i32 %65, !2243, !DIExpression(), !2444)
  %66 = icmp eq i32 %65, 12, !dbg !2452
  br i1 %66, label %67, label %56, !dbg !2446, !llvm.loop !2453

67:                                               ; preds = %56, %67
  %68 = phi i32 [ %76, %67 ], [ 0, %56 ]
  %69 = phi i16 [ %73, %67 ], [ 0, %56 ]
    #dbg_value(i16 %69, !2201, !DIExpression(), !2455)
  %70 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %68, !dbg !2457
  %71 = load i8, ptr %70, align 1, !dbg !2457, !tbaa !113
  %72 = zext i8 %71 to i16, !dbg !2457
  %73 = add i16 %69, %72, !dbg !2458
    #dbg_value(i16 %73, !2201, !DIExpression(), !2455)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2455)
  %74 = shl nsw i32 %68, 16, !dbg !2459
  %75 = add i32 %74, 65536, !dbg !2459
  %76 = ashr exact i32 %75, 16, !dbg !2459
  %77 = icmp slt i32 %76, 80, !dbg !2460
  br i1 %77, label %67, label %78, !dbg !2461, !llvm.loop !2462

78:                                               ; preds = %67
    #dbg_value(ptr %0, !106, !DIExpression(), !2464)
    #dbg_value(ptr %1, !107, !DIExpression(), !2464)
    #dbg_value(i16 %73, !108, !DIExpression(), !2464)
  %79 = lshr i16 %73, 8, !dbg !2466
  %80 = trunc nuw i16 %79 to i8, !dbg !2467
  store i8 %80, ptr %1, align 1, !dbg !2468, !tbaa !113
  %81 = trunc i16 %73 to i8, !dbg !2469
  br label %222, !dbg !2470

82:                                               ; preds = %3
  %83 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2471
    #dbg_value(i16 9, !2216, !DIExpression(), !2474)
    #dbg_value(i16 6, !2217, !DIExpression(), !2474)
    #dbg_value(i8 1, !2218, !DIExpression(), !2474)
    #dbg_value(i16 25, !2219, !DIExpression(), !2474)
    #dbg_value(i8 64, !2220, !DIExpression(), !2474)
  %84 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2476, !tbaa !113
  %85 = or i8 %84, 64, !dbg !2477
  store i8 %85, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2478, !tbaa !113
    #dbg_value(i16 8, !2216, !DIExpression(), !2479)
    #dbg_value(i16 7, !2217, !DIExpression(), !2479)
    #dbg_value(i8 1, !2218, !DIExpression(), !2479)
    #dbg_value(i16 29, !2219, !DIExpression(), !2479)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2479)
  %86 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2481, !tbaa !113
    #dbg_value(i16 9, !2216, !DIExpression(), !2482)
    #dbg_value(i16 7, !2217, !DIExpression(), !2482)
    #dbg_value(i8 1, !2218, !DIExpression(), !2482)
    #dbg_value(i16 29, !2219, !DIExpression(), !2482)
    #dbg_value(i8 64, !2220, !DIExpression(), !2482)
    #dbg_value(i16 10, !2216, !DIExpression(), !2484)
    #dbg_value(i16 7, !2217, !DIExpression(), !2484)
    #dbg_value(i8 1, !2218, !DIExpression(), !2484)
    #dbg_value(i16 29, !2219, !DIExpression(), !2484)
    #dbg_value(i8 32, !2220, !DIExpression(), !2484)
  %87 = or i8 %86, -32, !dbg !2486
  store i8 %87, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2487, !tbaa !113
    #dbg_value(i16 0, !2201, !DIExpression(), !2488)
    #dbg_value(i16 0, !2200, !DIExpression(), !2488)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2488)
  br label %88, !dbg !2490

88:                                               ; preds = %88, %82
  %89 = phi i32 [ 0, %82 ], [ %97, %88 ]
  %90 = phi i16 [ 0, %82 ], [ %94, %88 ]
    #dbg_value(i16 %90, !2201, !DIExpression(), !2488)
  %91 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %89, !dbg !2491
  %92 = load i8, ptr %91, align 1, !dbg !2491, !tbaa !113
  %93 = zext i8 %92 to i16, !dbg !2491
  %94 = add i16 %90, %93, !dbg !2492
    #dbg_value(i16 %94, !2201, !DIExpression(), !2488)
    #dbg_value(i16 poison, !2200, !DIExpression(), !2488)
  %95 = shl nsw i32 %89, 16, !dbg !2493
  %96 = add i32 %95, 65536, !dbg !2493
  %97 = ashr exact i32 %96, 16, !dbg !2493
  %98 = icmp slt i32 %97, 80, !dbg !2494
  br i1 %98, label %88, label %99, !dbg !2490, !llvm.loop !2495

99:                                               ; preds = %88
    #dbg_value(ptr %0, !106, !DIExpression(), !2497)
    #dbg_value(ptr %1, !107, !DIExpression(), !2497)
    #dbg_value(i16 %94, !108, !DIExpression(), !2497)
  %100 = lshr i16 %94, 8, !dbg !2499
  %101 = trunc nuw i16 %100 to i8, !dbg !2500
  store i8 %101, ptr %1, align 1, !dbg !2501, !tbaa !113
  %102 = trunc i16 %94 to i8, !dbg !2502
  br label %222, !dbg !2503

103:                                              ; preds = %3
  %104 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2504
    #dbg_value(i16 10, !2314, !DIExpression(), !2507)
    #dbg_value(i16 8, !2315, !DIExpression(), !2507)
    #dbg_value(i16 3, !2316, !DIExpression(), !2507)
    #dbg_value(i16 8, !2238, !DIExpression(), !2509)
    #dbg_value(i16 9, !2239, !DIExpression(), !2509)
    #dbg_value(i16 10, !2240, !DIExpression(), !2509)
    #dbg_value(i16 11, !2241, !DIExpression(), !2509)
    #dbg_value(i8 1, !2242, !DIExpression(), !2509)
    #dbg_value(i16 8, !2238, !DIExpression(), !2509)
    #dbg_value(i16 9, !2239, !DIExpression(), !2509)
    #dbg_value(i16 10, !2240, !DIExpression(), !2509)
    #dbg_value(i16 11, !2241, !DIExpression(), !2509)
    #dbg_value(i16 1, !2245, !DIExpression(), !2509)
    #dbg_value(i16 1, !2246, !DIExpression(), !2509)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2509)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2509)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2509)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2509)
    #dbg_value(i16 9, !2243, !DIExpression(), !2509)
  br label %105, !dbg !2511

105:                                              ; preds = %105, %103
  %106 = phi i32 [ 9, %103 ], [ %114, %105 ]
    #dbg_value(i32 %106, !2243, !DIExpression(), !2509)
  %107 = trunc nuw nsw i32 %106 to i16, !dbg !2512
  %108 = shl i16 %107, 2, !dbg !2512
    #dbg_value(i16 %108, !2244, !DIExpression(), !2509)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2509)
  %109 = or disjoint i16 %108, 1, !dbg !2513
  %110 = sext i16 %109 to i32, !dbg !2513
  %111 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %110, !dbg !2514
  %112 = load i8, ptr %111, align 1, !dbg !2515, !tbaa !113
  %113 = or i8 %112, -32, !dbg !2515
  store i8 %113, ptr %111, align 1, !dbg !2515, !tbaa !113
  %114 = add nuw nsw i32 %106, 1, !dbg !2516
    #dbg_value(i32 %114, !2243, !DIExpression(), !2509)
  %115 = icmp eq i32 %114, 12, !dbg !2517
  br i1 %115, label %116, label %105, !dbg !2511, !llvm.loop !2518

116:                                              ; preds = %105
    #dbg_value(i16 9, !2216, !DIExpression(), !2520)
    #dbg_value(i16 6, !2217, !DIExpression(), !2520)
    #dbg_value(i8 1, !2218, !DIExpression(), !2520)
    #dbg_value(i16 25, !2219, !DIExpression(), !2520)
    #dbg_value(i8 64, !2220, !DIExpression(), !2520)
  %117 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2522, !tbaa !113
  %118 = or i8 %117, 64, !dbg !2523
  store i8 %118, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2524, !tbaa !113
    #dbg_value(i16 8, !2216, !DIExpression(), !2525)
    #dbg_value(i16 7, !2217, !DIExpression(), !2525)
    #dbg_value(i8 1, !2218, !DIExpression(), !2525)
    #dbg_value(i16 29, !2219, !DIExpression(), !2525)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2525)
  %119 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2527, !tbaa !113
    #dbg_value(i16 9, !2216, !DIExpression(), !2528)
    #dbg_value(i16 7, !2217, !DIExpression(), !2528)
    #dbg_value(i8 1, !2218, !DIExpression(), !2528)
    #dbg_value(i16 29, !2219, !DIExpression(), !2528)
    #dbg_value(i8 64, !2220, !DIExpression(), !2528)
    #dbg_value(i16 10, !2216, !DIExpression(), !2530)
    #dbg_value(i16 7, !2217, !DIExpression(), !2530)
    #dbg_value(i8 1, !2218, !DIExpression(), !2530)
    #dbg_value(i16 29, !2219, !DIExpression(), !2530)
    #dbg_value(i8 32, !2220, !DIExpression(), !2530)
  %120 = or i8 %119, -32, !dbg !2532
  store i8 %120, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2533, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2534)
    #dbg_value(ptr %1, !107, !DIExpression(), !2534)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2534)
  store i8 0, ptr %1, align 1, !dbg !2536, !tbaa !113
  br label %222, !dbg !2537

121:                                              ; preds = %3
  %122 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2538
    #dbg_value(i16 10, !2314, !DIExpression(), !2541)
    #dbg_value(i16 8, !2315, !DIExpression(), !2541)
    #dbg_value(i16 3, !2316, !DIExpression(), !2541)
    #dbg_value(i16 8, !2238, !DIExpression(), !2543)
    #dbg_value(i16 9, !2239, !DIExpression(), !2543)
    #dbg_value(i16 10, !2240, !DIExpression(), !2543)
    #dbg_value(i16 11, !2241, !DIExpression(), !2543)
    #dbg_value(i8 1, !2242, !DIExpression(), !2543)
    #dbg_value(i16 8, !2238, !DIExpression(), !2543)
    #dbg_value(i16 9, !2239, !DIExpression(), !2543)
    #dbg_value(i16 10, !2240, !DIExpression(), !2543)
    #dbg_value(i16 11, !2241, !DIExpression(), !2543)
    #dbg_value(i16 1, !2245, !DIExpression(), !2543)
    #dbg_value(i16 1, !2246, !DIExpression(), !2543)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2543)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2543)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2543)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2543)
    #dbg_value(i16 9, !2243, !DIExpression(), !2543)
  br label %123, !dbg !2545

123:                                              ; preds = %123, %121
  %124 = phi i32 [ 9, %121 ], [ %132, %123 ]
    #dbg_value(i32 %124, !2243, !DIExpression(), !2543)
  %125 = trunc nuw nsw i32 %124 to i16, !dbg !2546
  %126 = shl i16 %125, 2, !dbg !2546
    #dbg_value(i16 %126, !2244, !DIExpression(), !2543)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2543)
  %127 = or disjoint i16 %126, 1, !dbg !2547
  %128 = sext i16 %127 to i32, !dbg !2547
  %129 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %128, !dbg !2548
  %130 = load i8, ptr %129, align 1, !dbg !2549, !tbaa !113
  %131 = or i8 %130, -32, !dbg !2549
  store i8 %131, ptr %129, align 1, !dbg !2549, !tbaa !113
  %132 = add nuw nsw i32 %124, 1, !dbg !2550
    #dbg_value(i32 %132, !2243, !DIExpression(), !2543)
  %133 = icmp eq i32 %132, 12, !dbg !2551
  br i1 %133, label %134, label %123, !dbg !2545, !llvm.loop !2552

134:                                              ; preds = %123
    #dbg_value(i16 9, !2216, !DIExpression(), !2554)
    #dbg_value(i16 6, !2217, !DIExpression(), !2554)
    #dbg_value(i8 1, !2218, !DIExpression(), !2554)
    #dbg_value(i16 25, !2219, !DIExpression(), !2554)
    #dbg_value(i8 64, !2220, !DIExpression(), !2554)
  %135 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2556, !tbaa !113
  %136 = or i8 %135, 64, !dbg !2557
  store i8 %136, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2558, !tbaa !113
    #dbg_value(i16 8, !2216, !DIExpression(), !2559)
    #dbg_value(i16 7, !2217, !DIExpression(), !2559)
    #dbg_value(i8 1, !2218, !DIExpression(), !2559)
    #dbg_value(i16 29, !2219, !DIExpression(), !2559)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2559)
  %137 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2561, !tbaa !113
    #dbg_value(i16 9, !2216, !DIExpression(), !2562)
    #dbg_value(i16 7, !2217, !DIExpression(), !2562)
    #dbg_value(i8 1, !2218, !DIExpression(), !2562)
    #dbg_value(i16 29, !2219, !DIExpression(), !2562)
    #dbg_value(i8 64, !2220, !DIExpression(), !2562)
    #dbg_value(i16 10, !2216, !DIExpression(), !2564)
    #dbg_value(i16 7, !2217, !DIExpression(), !2564)
    #dbg_value(i8 1, !2218, !DIExpression(), !2564)
    #dbg_value(i16 29, !2219, !DIExpression(), !2564)
    #dbg_value(i8 32, !2220, !DIExpression(), !2564)
  %138 = or i8 %137, -32, !dbg !2566
  store i8 %138, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2567, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2568)
    #dbg_value(ptr %1, !107, !DIExpression(), !2568)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2568)
  store i8 0, ptr %1, align 1, !dbg !2570, !tbaa !113
  br label %222, !dbg !2571

139:                                              ; preds = %3
  %140 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2572
    #dbg_value(i16 10, !2314, !DIExpression(), !2575)
    #dbg_value(i16 8, !2315, !DIExpression(), !2575)
    #dbg_value(i16 3, !2316, !DIExpression(), !2575)
    #dbg_value(i16 8, !2238, !DIExpression(), !2577)
    #dbg_value(i16 9, !2239, !DIExpression(), !2577)
    #dbg_value(i16 10, !2240, !DIExpression(), !2577)
    #dbg_value(i16 11, !2241, !DIExpression(), !2577)
    #dbg_value(i8 1, !2242, !DIExpression(), !2577)
    #dbg_value(i16 8, !2238, !DIExpression(), !2577)
    #dbg_value(i16 9, !2239, !DIExpression(), !2577)
    #dbg_value(i16 10, !2240, !DIExpression(), !2577)
    #dbg_value(i16 11, !2241, !DIExpression(), !2577)
    #dbg_value(i16 1, !2245, !DIExpression(), !2577)
    #dbg_value(i16 1, !2246, !DIExpression(), !2577)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2577)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2577)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2577)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2577)
    #dbg_value(i16 9, !2243, !DIExpression(), !2577)
  br label %141, !dbg !2579

141:                                              ; preds = %141, %139
  %142 = phi i32 [ 9, %139 ], [ %150, %141 ]
    #dbg_value(i32 %142, !2243, !DIExpression(), !2577)
  %143 = trunc nuw nsw i32 %142 to i16, !dbg !2580
  %144 = shl i16 %143, 2, !dbg !2580
    #dbg_value(i16 %144, !2244, !DIExpression(), !2577)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2577)
  %145 = or disjoint i16 %144, 1, !dbg !2581
  %146 = sext i16 %145 to i32, !dbg !2581
  %147 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %146, !dbg !2582
  %148 = load i8, ptr %147, align 1, !dbg !2583, !tbaa !113
  %149 = or i8 %148, -32, !dbg !2583
  store i8 %149, ptr %147, align 1, !dbg !2583, !tbaa !113
  %150 = add nuw nsw i32 %142, 1, !dbg !2584
    #dbg_value(i32 %150, !2243, !DIExpression(), !2577)
  %151 = icmp eq i32 %150, 12, !dbg !2585
  br i1 %151, label %152, label %141, !dbg !2579, !llvm.loop !2586

152:                                              ; preds = %141
    #dbg_value(i16 9, !2216, !DIExpression(), !2588)
    #dbg_value(i16 6, !2217, !DIExpression(), !2588)
    #dbg_value(i8 1, !2218, !DIExpression(), !2588)
    #dbg_value(i16 25, !2219, !DIExpression(), !2588)
    #dbg_value(i8 64, !2220, !DIExpression(), !2588)
  %153 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2590, !tbaa !113
  %154 = or i8 %153, 64, !dbg !2591
  store i8 %154, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2592, !tbaa !113
    #dbg_value(i16 8, !2216, !DIExpression(), !2593)
    #dbg_value(i16 7, !2217, !DIExpression(), !2593)
    #dbg_value(i8 1, !2218, !DIExpression(), !2593)
    #dbg_value(i16 29, !2219, !DIExpression(), !2593)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2593)
  %155 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2595, !tbaa !113
    #dbg_value(i16 9, !2216, !DIExpression(), !2596)
    #dbg_value(i16 7, !2217, !DIExpression(), !2596)
    #dbg_value(i8 1, !2218, !DIExpression(), !2596)
    #dbg_value(i16 29, !2219, !DIExpression(), !2596)
    #dbg_value(i8 64, !2220, !DIExpression(), !2596)
    #dbg_value(i16 10, !2216, !DIExpression(), !2598)
    #dbg_value(i16 7, !2217, !DIExpression(), !2598)
    #dbg_value(i8 1, !2218, !DIExpression(), !2598)
    #dbg_value(i16 29, !2219, !DIExpression(), !2598)
    #dbg_value(i8 32, !2220, !DIExpression(), !2598)
  %156 = or i8 %155, -32, !dbg !2600
  store i8 %156, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2601, !tbaa !113
  %157 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 37), align 1, !dbg !2602, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2603)
    #dbg_value(ptr %1, !107, !DIExpression(), !2603)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2603)
  store i8 0, ptr %1, align 1, !dbg !2605, !tbaa !113
  br label %222, !dbg !2606

158:                                              ; preds = %3
  %159 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2607
    #dbg_value(i16 10, !2314, !DIExpression(), !2610)
    #dbg_value(i16 8, !2315, !DIExpression(), !2610)
    #dbg_value(i16 3, !2316, !DIExpression(), !2610)
    #dbg_value(i16 8, !2238, !DIExpression(), !2612)
    #dbg_value(i16 9, !2239, !DIExpression(), !2612)
    #dbg_value(i16 10, !2240, !DIExpression(), !2612)
    #dbg_value(i16 11, !2241, !DIExpression(), !2612)
    #dbg_value(i8 1, !2242, !DIExpression(), !2612)
    #dbg_value(i16 8, !2238, !DIExpression(), !2612)
    #dbg_value(i16 9, !2239, !DIExpression(), !2612)
    #dbg_value(i16 10, !2240, !DIExpression(), !2612)
    #dbg_value(i16 11, !2241, !DIExpression(), !2612)
    #dbg_value(i16 1, !2245, !DIExpression(), !2612)
    #dbg_value(i16 1, !2246, !DIExpression(), !2612)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2612)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2612)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2612)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2612)
    #dbg_value(i16 9, !2243, !DIExpression(), !2612)
  br label %160, !dbg !2614

160:                                              ; preds = %160, %158
  %161 = phi i32 [ 9, %158 ], [ %169, %160 ]
    #dbg_value(i32 %161, !2243, !DIExpression(), !2612)
  %162 = trunc nuw nsw i32 %161 to i16, !dbg !2615
  %163 = shl i16 %162, 2, !dbg !2615
    #dbg_value(i16 %163, !2244, !DIExpression(), !2612)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2612)
  %164 = or disjoint i16 %163, 1, !dbg !2616
  %165 = sext i16 %164 to i32, !dbg !2616
  %166 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %165, !dbg !2617
  %167 = load i8, ptr %166, align 1, !dbg !2618, !tbaa !113
  %168 = or i8 %167, -32, !dbg !2618
  store i8 %168, ptr %166, align 1, !dbg !2618, !tbaa !113
  %169 = add nuw nsw i32 %161, 1, !dbg !2619
    #dbg_value(i32 %169, !2243, !DIExpression(), !2612)
  %170 = icmp eq i32 %169, 12, !dbg !2620
  br i1 %170, label %171, label %160, !dbg !2614, !llvm.loop !2621

171:                                              ; preds = %160
    #dbg_value(i16 9, !2216, !DIExpression(), !2623)
    #dbg_value(i16 6, !2217, !DIExpression(), !2623)
    #dbg_value(i8 1, !2218, !DIExpression(), !2623)
    #dbg_value(i16 25, !2219, !DIExpression(), !2623)
    #dbg_value(i8 64, !2220, !DIExpression(), !2623)
  %172 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2625, !tbaa !113
  %173 = or i8 %172, 64, !dbg !2626
  store i8 %173, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2627, !tbaa !113
    #dbg_value(i16 8, !2216, !DIExpression(), !2628)
    #dbg_value(i16 7, !2217, !DIExpression(), !2628)
    #dbg_value(i8 1, !2218, !DIExpression(), !2628)
    #dbg_value(i16 29, !2219, !DIExpression(), !2628)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2628)
  %174 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2630, !tbaa !113
    #dbg_value(i16 9, !2216, !DIExpression(), !2631)
    #dbg_value(i16 7, !2217, !DIExpression(), !2631)
    #dbg_value(i8 1, !2218, !DIExpression(), !2631)
    #dbg_value(i16 29, !2219, !DIExpression(), !2631)
    #dbg_value(i8 64, !2220, !DIExpression(), !2631)
    #dbg_value(i16 10, !2216, !DIExpression(), !2633)
    #dbg_value(i16 7, !2217, !DIExpression(), !2633)
    #dbg_value(i8 1, !2218, !DIExpression(), !2633)
    #dbg_value(i16 29, !2219, !DIExpression(), !2633)
    #dbg_value(i8 32, !2220, !DIExpression(), !2633)
  %175 = or i8 %174, -32, !dbg !2635
  store i8 %175, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2636, !tbaa !113
  %176 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 41), align 1, !dbg !2637, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2638)
    #dbg_value(ptr %1, !107, !DIExpression(), !2638)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2638)
  store i8 0, ptr %1, align 1, !dbg !2640, !tbaa !113
  br label %222, !dbg !2641

177:                                              ; preds = %3
  %178 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2642
    #dbg_value(i16 10, !2314, !DIExpression(), !2645)
    #dbg_value(i16 8, !2315, !DIExpression(), !2645)
    #dbg_value(i16 3, !2316, !DIExpression(), !2645)
    #dbg_value(i16 8, !2238, !DIExpression(), !2647)
    #dbg_value(i16 9, !2239, !DIExpression(), !2647)
    #dbg_value(i16 10, !2240, !DIExpression(), !2647)
    #dbg_value(i16 11, !2241, !DIExpression(), !2647)
    #dbg_value(i8 1, !2242, !DIExpression(), !2647)
    #dbg_value(i16 8, !2238, !DIExpression(), !2647)
    #dbg_value(i16 9, !2239, !DIExpression(), !2647)
    #dbg_value(i16 10, !2240, !DIExpression(), !2647)
    #dbg_value(i16 11, !2241, !DIExpression(), !2647)
    #dbg_value(i16 1, !2245, !DIExpression(), !2647)
    #dbg_value(i16 1, !2246, !DIExpression(), !2647)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2647)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2647)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2647)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2647)
    #dbg_value(i16 9, !2243, !DIExpression(), !2647)
  br label %179, !dbg !2649

179:                                              ; preds = %179, %177
  %180 = phi i32 [ 9, %177 ], [ %188, %179 ]
    #dbg_value(i32 %180, !2243, !DIExpression(), !2647)
  %181 = trunc nuw nsw i32 %180 to i16, !dbg !2650
  %182 = shl i16 %181, 2, !dbg !2650
    #dbg_value(i16 %182, !2244, !DIExpression(), !2647)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2647)
  %183 = or disjoint i16 %182, 1, !dbg !2651
  %184 = sext i16 %183 to i32, !dbg !2651
  %185 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %184, !dbg !2652
  %186 = load i8, ptr %185, align 1, !dbg !2653, !tbaa !113
  %187 = or i8 %186, -32, !dbg !2653
  store i8 %187, ptr %185, align 1, !dbg !2653, !tbaa !113
  %188 = add nuw nsw i32 %180, 1, !dbg !2654
    #dbg_value(i32 %188, !2243, !DIExpression(), !2647)
  %189 = icmp eq i32 %188, 12, !dbg !2655
  br i1 %189, label %190, label %179, !dbg !2649, !llvm.loop !2656

190:                                              ; preds = %179
    #dbg_value(i16 9, !2216, !DIExpression(), !2658)
    #dbg_value(i16 6, !2217, !DIExpression(), !2658)
    #dbg_value(i8 1, !2218, !DIExpression(), !2658)
    #dbg_value(i16 25, !2219, !DIExpression(), !2658)
    #dbg_value(i8 64, !2220, !DIExpression(), !2658)
  %191 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2660, !tbaa !113
  %192 = or i8 %191, 64, !dbg !2661
  store i8 %192, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2662, !tbaa !113
    #dbg_value(i16 8, !2216, !DIExpression(), !2663)
    #dbg_value(i16 7, !2217, !DIExpression(), !2663)
    #dbg_value(i8 1, !2218, !DIExpression(), !2663)
    #dbg_value(i16 29, !2219, !DIExpression(), !2663)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2663)
  %193 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2665, !tbaa !113
    #dbg_value(i16 9, !2216, !DIExpression(), !2666)
    #dbg_value(i16 7, !2217, !DIExpression(), !2666)
    #dbg_value(i8 1, !2218, !DIExpression(), !2666)
    #dbg_value(i16 29, !2219, !DIExpression(), !2666)
    #dbg_value(i8 64, !2220, !DIExpression(), !2666)
    #dbg_value(i16 10, !2216, !DIExpression(), !2668)
    #dbg_value(i16 7, !2217, !DIExpression(), !2668)
    #dbg_value(i8 1, !2218, !DIExpression(), !2668)
    #dbg_value(i16 29, !2219, !DIExpression(), !2668)
    #dbg_value(i8 32, !2220, !DIExpression(), !2668)
  %194 = or i8 %193, -32, !dbg !2670
  store i8 %194, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2671, !tbaa !113
  %195 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 45), align 1, !dbg !2672, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2673)
    #dbg_value(ptr %1, !107, !DIExpression(), !2673)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2673)
  store i8 0, ptr %1, align 1, !dbg !2675, !tbaa !113
  br label %222, !dbg !2676

196:                                              ; preds = %3
  %197 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2677
    #dbg_value(i16 9, !2216, !DIExpression(), !2680)
    #dbg_value(i16 6, !2217, !DIExpression(), !2680)
    #dbg_value(i8 1, !2218, !DIExpression(), !2680)
    #dbg_value(i16 25, !2219, !DIExpression(), !2680)
    #dbg_value(i8 64, !2220, !DIExpression(), !2680)
  %198 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2682, !tbaa !113
  %199 = or i8 %198, 64, !dbg !2683
  store i8 %199, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 25), align 1, !dbg !2684, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2685)
    #dbg_value(ptr %1, !107, !DIExpression(), !2685)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2685)
  store i8 0, ptr %1, align 1, !dbg !2687, !tbaa !113
  br label %222, !dbg !2688

200:                                              ; preds = %3
  %201 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2689
    #dbg_value(i16 8, !2216, !DIExpression(), !2692)
    #dbg_value(i16 7, !2217, !DIExpression(), !2692)
    #dbg_value(i8 1, !2218, !DIExpression(), !2692)
    #dbg_value(i16 29, !2219, !DIExpression(), !2692)
    #dbg_value(i8 -128, !2220, !DIExpression(), !2692)
  %202 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2694, !tbaa !113
  %203 = or i8 %202, -128, !dbg !2695
  store i8 %203, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2696, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2697)
    #dbg_value(ptr %1, !107, !DIExpression(), !2697)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2697)
  store i8 0, ptr %1, align 1, !dbg !2699, !tbaa !113
  br label %222, !dbg !2700

204:                                              ; preds = %3
  %205 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2701
    #dbg_value(i16 9, !2216, !DIExpression(), !2704)
    #dbg_value(i16 7, !2217, !DIExpression(), !2704)
    #dbg_value(i8 1, !2218, !DIExpression(), !2704)
    #dbg_value(i16 29, !2219, !DIExpression(), !2704)
    #dbg_value(i8 64, !2220, !DIExpression(), !2704)
  %206 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2706, !tbaa !113
  %207 = or i8 %206, 64, !dbg !2707
  store i8 %207, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2708, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2709)
    #dbg_value(ptr %1, !107, !DIExpression(), !2709)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2709)
  store i8 0, ptr %1, align 1, !dbg !2711, !tbaa !113
  br label %222, !dbg !2712

208:                                              ; preds = %3
  %209 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2713
    #dbg_value(i16 10, !2216, !DIExpression(), !2716)
    #dbg_value(i16 7, !2217, !DIExpression(), !2716)
    #dbg_value(i8 1, !2218, !DIExpression(), !2716)
    #dbg_value(i16 29, !2219, !DIExpression(), !2716)
    #dbg_value(i8 32, !2220, !DIExpression(), !2716)
  %210 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2718, !tbaa !113
  %211 = or i8 %210, 32, !dbg !2719
  store i8 %211, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 29), align 1, !dbg !2720, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !2721)
    #dbg_value(ptr %1, !107, !DIExpression(), !2721)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2721)
  store i8 0, ptr %1, align 1, !dbg !2723, !tbaa !113
  br label %222, !dbg !2724

212:                                              ; preds = %3
    #dbg_value(i16 8, !2349, !DIExpression(), !2725)
    #dbg_value(i16 10, !2352, !DIExpression(), !2725)
    #dbg_value(i8 -1, !2353, !DIExpression(), !2725)
    #dbg_value(i8 -32, !2354, !DIExpression(), !2725)
    #dbg_value(i8 -32, !2355, !DIExpression(), !2725)
    #dbg_value(ptr %0, !106, !DIExpression(), !2726)
    #dbg_value(ptr %1, !107, !DIExpression(), !2726)
    #dbg_value(i16 224, !108, !DIExpression(), !2726)
  store i8 0, ptr %1, align 1, !dbg !2728, !tbaa !113
  br label %222

213:                                              ; preds = %3
  %214 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 80, i8 noundef signext 0) #11, !dbg !2729
    #dbg_value(i16 8, !2238, !DIExpression(), !2732)
    #dbg_value(i16 9, !2239, !DIExpression(), !2732)
    #dbg_value(i16 10, !2240, !DIExpression(), !2732)
    #dbg_value(i16 9, !2241, !DIExpression(), !2732)
    #dbg_value(i8 1, !2242, !DIExpression(), !2732)
    #dbg_value(i16 8, !2238, !DIExpression(), !2732)
    #dbg_value(i16 9, !2239, !DIExpression(), !2732)
    #dbg_value(i16 10, !2240, !DIExpression(), !2732)
    #dbg_value(i16 9, !2241, !DIExpression(), !2732)
    #dbg_value(i16 1, !2245, !DIExpression(), !2732)
    #dbg_value(i16 1, !2246, !DIExpression(), !2732)
    #dbg_value(i8 -1, !2248, !DIExpression(), !2732)
    #dbg_value(i8 -32, !2249, !DIExpression(), !2732)
    #dbg_value(i8 -1, !2250, !DIExpression(), !2732)
    #dbg_value(i16 -1, !2247, !DIExpression(), !2732)
    #dbg_value(i16 9, !2243, !DIExpression(), !2732)
    #dbg_value(i32 9, !2243, !DIExpression(), !2732)
    #dbg_value(i16 36, !2244, !DIExpression(), !2732)
    #dbg_value(i8 -32, !2251, !DIExpression(), !2732)
  %215 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 37), align 1, !dbg !2734, !tbaa !113
  %216 = or i8 %215, -32, !dbg !2734
  store i8 %216, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 37), align 1, !dbg !2734, !tbaa !113
    #dbg_value(i32 10, !2243, !DIExpression(), !2732)
    #dbg_value(ptr %0, !106, !DIExpression(), !2735)
    #dbg_value(ptr %1, !107, !DIExpression(), !2735)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !2735)
  store i8 0, ptr %1, align 1, !dbg !2737, !tbaa !113
  br label %222, !dbg !2738

217:                                              ; preds = %3
    #dbg_value(i16 8, !2356, !DIExpression(), !2739)
    #dbg_value(i16 1, !2359, !DIExpression(), !2739)
    #dbg_value(ptr %0, !106, !DIExpression(), !2740)
    #dbg_value(ptr %1, !107, !DIExpression(), !2740)
    #dbg_value(i16 1, !108, !DIExpression(), !2740)
  store i8 0, ptr %1, align 1, !dbg !2742, !tbaa !113
  br label %222

218:                                              ; preds = %3
    #dbg_value(i16 10, !2360, !DIExpression(), !2743)
    #dbg_value(i16 1, !2363, !DIExpression(), !2743)
    #dbg_value(ptr %0, !106, !DIExpression(), !2744)
    #dbg_value(ptr %1, !107, !DIExpression(), !2744)
    #dbg_value(i16 1, !108, !DIExpression(), !2744)
  store i8 0, ptr %1, align 1, !dbg !2746, !tbaa !113
  br label %222

219:                                              ; preds = %3
    #dbg_value(i16 9, !2364, !DIExpression(), !2747)
    #dbg_value(i16 36, !2367, !DIExpression(), !2747)
    #dbg_value(ptr %0, !106, !DIExpression(), !2748)
    #dbg_value(ptr %1, !107, !DIExpression(), !2748)
    #dbg_value(i16 36, !108, !DIExpression(), !2748)
  store i8 0, ptr %1, align 1, !dbg !2750, !tbaa !113
  br label %222

220:                                              ; preds = %3
    #dbg_value(i16 9, !2368, !DIExpression(), !2751)
    #dbg_value(i16 8, !2371, !DIExpression(), !2751)
    #dbg_value(i16 36, !2372, !DIExpression(), !2751)
    #dbg_value(i16 1, !2373, !DIExpression(), !2751)
    #dbg_value(ptr %0, !106, !DIExpression(), !2752)
    #dbg_value(ptr %1, !107, !DIExpression(), !2752)
    #dbg_value(i16 37, !108, !DIExpression(), !2752)
  store i8 0, ptr %1, align 1, !dbg !2754, !tbaa !113
  br label %222

221:                                              ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2755)
    #dbg_value(ptr %1, !107, !DIExpression(), !2755)
    #dbg_value(i16 -1, !108, !DIExpression(), !2755)
  store i8 -1, ptr %1, align 1, !dbg !2757, !tbaa !113
  br label %222, !dbg !2758

222:                                              ; preds = %221, %220, %219, %218, %217, %213, %212, %208, %204, %200, %196, %190, %171, %152, %134, %116, %99, %78, %50, %33
  %223 = phi i8 [ -1, %221 ], [ 37, %220 ], [ 36, %219 ], [ 1, %218 ], [ 1, %217 ], [ %216, %213 ], [ -32, %212 ], [ %211, %208 ], [ %207, %204 ], [ %203, %200 ], [ %199, %196 ], [ %195, %190 ], [ %176, %171 ], [ %157, %152 ], [ %138, %134 ], [ %118, %116 ], [ %102, %99 ], [ %81, %78 ], [ %53, %50 ], [ %36, %33 ]
  %224 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !2759
  store i8 %223, ptr %224, align 1, !dbg !2760, !tbaa !113
  %225 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !2761
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !2762
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !2763
  ret void, !dbg !2758
}

; Function Attrs: nounwind
define hidden void @test_arithmetic(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !2764 {
    #dbg_value(ptr %0, !2766, !DIExpression(), !2771)
    #dbg_value(ptr %1, !2767, !DIExpression(), !2771)
    #dbg_value(i8 %2, !2768, !DIExpression(), !2771)
    #dbg_value(i16 10, !2769, !DIExpression(), !2771)
    #dbg_value(i16 3, !2770, !DIExpression(), !2771)
  switch i8 %2, label %11 [
    i8 0, label %12
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %10
  ], !dbg !2772

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2773)
    #dbg_value(ptr %1, !107, !DIExpression(), !2773)
    #dbg_value(i16 7, !108, !DIExpression(), !2773)
  br label %12, !dbg !2777

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2778)
    #dbg_value(ptr %1, !107, !DIExpression(), !2778)
    #dbg_value(i16 30, !108, !DIExpression(), !2778)
  br label %12, !dbg !2782

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2783)
    #dbg_value(ptr %1, !107, !DIExpression(), !2783)
    #dbg_value(i16 3, !108, !DIExpression(), !2783)
  br label %12, !dbg !2787

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2788)
    #dbg_value(ptr %1, !107, !DIExpression(), !2788)
    #dbg_value(i16 1, !108, !DIExpression(), !2788)
  br label %12, !dbg !2792

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2793)
    #dbg_value(ptr %1, !107, !DIExpression(), !2793)
    #dbg_value(i16 -10, !108, !DIExpression(), !2793)
  br label %12, !dbg !2797

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2798)
    #dbg_value(ptr %1, !107, !DIExpression(), !2798)
    #dbg_value(i16 16, !108, !DIExpression(), !2798)
  br label %12, !dbg !2802

10:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2803)
    #dbg_value(ptr %1, !107, !DIExpression(), !2803)
    #dbg_value(i16 26, !108, !DIExpression(), !2803)
  br label %12, !dbg !2807

11:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2808)
    #dbg_value(ptr %1, !107, !DIExpression(), !2808)
    #dbg_value(i16 -1, !108, !DIExpression(), !2808)
  br label %12, !dbg !2810

12:                                               ; preds = %3, %11, %10, %9, %8, %7, %6, %5, %4
  %13 = phi i8 [ -1, %11 ], [ 0, %10 ], [ 0, %9 ], [ -1, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %14 = phi i8 [ -1, %11 ], [ 26, %10 ], [ 16, %9 ], [ -10, %8 ], [ 1, %7 ], [ 3, %6 ], [ 30, %5 ], [ 7, %4 ], [ 13, %3 ]
  %15 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !2811
  store i8 %13, ptr %1, align 1, !dbg !2812, !tbaa !113
  store i8 %14, ptr %15, align 1, !dbg !2813, !tbaa !113
  %16 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !2814
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !2815
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !2816
  ret void, !dbg !2810
}

; Function Attrs: nounwind
define hidden void @test_bitwise(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !2817 {
    #dbg_value(ptr %0, !2819, !DIExpression(), !2824)
    #dbg_value(ptr %1, !2820, !DIExpression(), !2824)
    #dbg_value(i8 %2, !2821, !DIExpression(), !2824)
    #dbg_value(i16 15, !2822, !DIExpression(), !2824)
    #dbg_value(i16 51, !2823, !DIExpression(), !2824)
  switch i8 %2, label %9 [
    i8 0, label %10
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
  ], !dbg !2825

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2826)
    #dbg_value(ptr %1, !107, !DIExpression(), !2826)
    #dbg_value(i16 63, !108, !DIExpression(), !2826)
  br label %10, !dbg !2830

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2831)
    #dbg_value(ptr %1, !107, !DIExpression(), !2831)
    #dbg_value(i16 60, !108, !DIExpression(), !2831)
  br label %10, !dbg !2835

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2836)
    #dbg_value(ptr %1, !107, !DIExpression(), !2836)
    #dbg_value(i16 60, !108, !DIExpression(), !2836)
  br label %10, !dbg !2840

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2841)
    #dbg_value(ptr %1, !107, !DIExpression(), !2841)
    #dbg_value(i16 12, !108, !DIExpression(), !2841)
  br label %10, !dbg !2845

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2846)
    #dbg_value(ptr %1, !107, !DIExpression(), !2846)
    #dbg_value(i16 240, !108, !DIExpression(), !2846)
  br label %10, !dbg !2850

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2851)
    #dbg_value(ptr %1, !107, !DIExpression(), !2851)
    #dbg_value(i16 -1, !108, !DIExpression(), !2851)
  br label %10, !dbg !2853

10:                                               ; preds = %3, %9, %8, %7, %6, %5, %4
  %11 = phi i8 [ -1, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %12 = phi i8 [ -1, %9 ], [ -16, %8 ], [ 12, %7 ], [ 60, %6 ], [ 60, %5 ], [ 63, %4 ], [ 3, %3 ]
  %13 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !2854
  store i8 %11, ptr %1, align 1, !dbg !2855, !tbaa !113
  store i8 %12, ptr %13, align 1, !dbg !2856, !tbaa !113
  %14 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !2857
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !2858
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !2859
  ret void, !dbg !2853
}

; Function Attrs: nounwind
define hidden void @test_comparison(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !2860 {
    #dbg_value(ptr %0, !2862, !DIExpression(), !2867)
    #dbg_value(ptr %1, !2863, !DIExpression(), !2867)
    #dbg_value(i8 %2, !2864, !DIExpression(), !2867)
    #dbg_value(i16 10, !2865, !DIExpression(), !2867)
    #dbg_value(i16 20, !2866, !DIExpression(), !2867)
  switch i8 %2, label %9 [
    i8 0, label %10
    i8 1, label %4
    i8 2, label %5
    i8 3, label %10
    i8 4, label %6
    i8 5, label %10
    i8 6, label %7
    i8 7, label %8
  ], !dbg !2868

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2869)
    #dbg_value(ptr %1, !107, !DIExpression(), !2869)
    #dbg_value(i16 1, !108, !DIExpression(), !2869)
  br label %10, !dbg !2873

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2874)
    #dbg_value(ptr %1, !107, !DIExpression(), !2874)
    #dbg_value(i16 1, !108, !DIExpression(), !2874)
  br label %10, !dbg !2878

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2879)
    #dbg_value(ptr %1, !107, !DIExpression(), !2879)
    #dbg_value(i16 1, !108, !DIExpression(), !2879)
  br label %10, !dbg !2883

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2884)
    #dbg_value(ptr %1, !107, !DIExpression(), !2884)
    #dbg_value(i16 1, !108, !DIExpression(), !2884)
  br label %10, !dbg !2888

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2889)
    #dbg_value(ptr %1, !107, !DIExpression(), !2889)
    #dbg_value(i16 1, !108, !DIExpression(), !2889)
  br label %10, !dbg !2893

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2894)
    #dbg_value(ptr %1, !107, !DIExpression(), !2894)
    #dbg_value(i16 -1, !108, !DIExpression(), !2894)
  br label %10, !dbg !2896

10:                                               ; preds = %3, %3, %3, %9, %8, %7, %6, %5, %4
  %11 = phi i8 [ -1, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %12 = phi i8 [ -1, %9 ], [ 1, %8 ], [ 1, %7 ], [ 1, %6 ], [ 1, %5 ], [ 1, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %13 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !2897
  store i8 %11, ptr %1, align 1, !dbg !2898, !tbaa !113
  store i8 %12, ptr %13, align 1, !dbg !2899, !tbaa !113
  %14 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !2900
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !2901
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !2902
  ret void, !dbg !2896
}

; Function Attrs: nounwind
define hidden void @test_logical(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !2903 {
    #dbg_value(ptr %0, !2905, !DIExpression(), !2910)
    #dbg_value(ptr %1, !2906, !DIExpression(), !2910)
    #dbg_value(i8 %2, !2907, !DIExpression(), !2910)
    #dbg_value(i16 1, !2908, !DIExpression(), !2910)
    #dbg_value(i16 0, !2909, !DIExpression(), !2910)
  switch i8 %2, label %9 [
    i8 0, label %10
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %10
    i8 5, label %10
    i8 6, label %10
    i8 7, label %7
    i8 8, label %8
    i8 9, label %10
  ], !dbg !2911

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2912)
    #dbg_value(ptr %1, !107, !DIExpression(), !2912)
    #dbg_value(i16 0, !108, !DIExpression(), !2912)
  br label %10, !dbg !2916

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2917)
    #dbg_value(ptr %1, !107, !DIExpression(), !2917)
    #dbg_value(i16 0, !108, !DIExpression(), !2917)
  br label %10, !dbg !2921

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2922)
    #dbg_value(ptr %1, !107, !DIExpression(), !2922)
    #dbg_value(i16 0, !108, !DIExpression(), !2922)
  br label %10, !dbg !2926

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2927)
    #dbg_value(ptr %1, !107, !DIExpression(), !2927)
    #dbg_value(i16 0, !108, !DIExpression(), !2927)
  br label %10, !dbg !2931

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2932)
    #dbg_value(ptr %1, !107, !DIExpression(), !2932)
    #dbg_value(i16 0, !108, !DIExpression(), !2932)
  br label %10, !dbg !2936

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !2937)
    #dbg_value(ptr %1, !107, !DIExpression(), !2937)
    #dbg_value(i16 -1, !108, !DIExpression(), !2937)
  br label %10, !dbg !2939

10:                                               ; preds = %3, %3, %3, %3, %3, %9, %8, %7, %6, %5, %4
  %11 = phi i8 [ -1, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %12 = phi i8 [ -1, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ]
  %13 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !2940
  store i8 %11, ptr %1, align 1, !dbg !2941, !tbaa !113
  store i8 %12, ptr %13, align 1, !dbg !2942, !tbaa !113
  %14 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !2943
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !2944
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !2945
  ret void, !dbg !2939
}

; Function Attrs: nounwind
define hidden void @test_incdec(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !2946 {
    #dbg_value(ptr %0, !2948, !DIExpression(), !2952)
    #dbg_value(ptr %1, !2949, !DIExpression(), !2952)
    #dbg_value(i8 %2, !2950, !DIExpression(), !2952)
  switch i8 %2, label %16 [
    i8 0, label %17
    i8 1, label %4
    i8 2, label %17
    i8 3, label %5
    i8 4, label %6
    i8 5, label %7
    i8 6, label %8
    i8 7, label %9
    i8 8, label %10
    i8 9, label %11
    i8 10, label %12
    i8 11, label %13
    i8 12, label %14
    i8 13, label %15
  ], !dbg !2953

4:                                                ; preds = %3
    #dbg_value(i16 5, !2951, !DIExpression(), !2952)
    #dbg_value(i16 5, !2951, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2954)
    #dbg_value(ptr %1, !107, !DIExpression(), !2954)
    #dbg_value(i16 5, !108, !DIExpression(), !2954)
  br label %17, !dbg !2958

5:                                                ; preds = %3
    #dbg_value(i16 5, !2951, !DIExpression(), !2952)
    #dbg_value(i16 4, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2959)
    #dbg_value(ptr %1, !107, !DIExpression(), !2959)
    #dbg_value(i16 4, !108, !DIExpression(), !2959)
  br label %17, !dbg !2963

6:                                                ; preds = %3
    #dbg_value(i16 5, !2951, !DIExpression(), !2952)
    #dbg_value(i16 5, !2951, !DIExpression(DW_OP_constu, 1, DW_OP_minus, DW_OP_stack_value), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2964)
    #dbg_value(ptr %1, !107, !DIExpression(), !2964)
    #dbg_value(i16 5, !108, !DIExpression(), !2964)
  br label %17, !dbg !2968

7:                                                ; preds = %3
    #dbg_value(i16 5, !2951, !DIExpression(), !2952)
    #dbg_value(i16 4, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2969)
    #dbg_value(ptr %1, !107, !DIExpression(), !2969)
    #dbg_value(i16 4, !108, !DIExpression(), !2969)
  br label %17, !dbg !2973

8:                                                ; preds = %3
    #dbg_value(i16 100, !2951, !DIExpression(), !2952)
    #dbg_value(i16 300, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2974)
    #dbg_value(ptr %1, !107, !DIExpression(), !2974)
    #dbg_value(i16 300, !108, !DIExpression(), !2974)
  br label %17, !dbg !2978

9:                                                ; preds = %3
    #dbg_value(i16 500, !2951, !DIExpression(), !2952)
    #dbg_value(i16 200, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2979)
    #dbg_value(ptr %1, !107, !DIExpression(), !2979)
    #dbg_value(i16 200, !108, !DIExpression(), !2979)
  br label %17, !dbg !2983

10:                                               ; preds = %3
    #dbg_value(i16 0, !2951, !DIExpression(), !2952)
    #dbg_value(i16 1000, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2984)
    #dbg_value(ptr %1, !107, !DIExpression(), !2984)
    #dbg_value(i16 1000, !108, !DIExpression(), !2984)
  br label %17, !dbg !2988

11:                                               ; preds = %3
    #dbg_value(i16 2000, !2951, !DIExpression(), !2952)
    #dbg_value(i16 500, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2989)
    #dbg_value(ptr %1, !107, !DIExpression(), !2989)
    #dbg_value(i16 500, !108, !DIExpression(), !2989)
  br label %17, !dbg !2993

12:                                               ; preds = %3
    #dbg_value(i16 0, !2951, !DIExpression(), !2952)
    #dbg_value(i16 127, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2994)
    #dbg_value(ptr %1, !107, !DIExpression(), !2994)
    #dbg_value(i16 127, !108, !DIExpression(), !2994)
  br label %17, !dbg !2998

13:                                               ; preds = %3
    #dbg_value(i16 0, !2951, !DIExpression(), !2952)
    #dbg_value(i16 128, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !2999)
    #dbg_value(ptr %1, !107, !DIExpression(), !2999)
    #dbg_value(i16 128, !108, !DIExpression(), !2999)
  br label %17, !dbg !3003

14:                                               ; preds = %3
    #dbg_value(i16 200, !2951, !DIExpression(), !2952)
    #dbg_value(i16 72, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !3004)
    #dbg_value(ptr %1, !107, !DIExpression(), !3004)
    #dbg_value(i16 72, !108, !DIExpression(), !3004)
  br label %17, !dbg !3008

15:                                               ; preds = %3
    #dbg_value(i16 200, !2951, !DIExpression(), !2952)
    #dbg_value(i16 71, !2951, !DIExpression(), !2952)
    #dbg_value(ptr %0, !106, !DIExpression(), !3009)
    #dbg_value(ptr %1, !107, !DIExpression(), !3009)
    #dbg_value(i16 71, !108, !DIExpression(), !3009)
  br label %17, !dbg !3013

16:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3014)
    #dbg_value(ptr %1, !107, !DIExpression(), !3014)
    #dbg_value(i16 -1, !108, !DIExpression(), !3014)
  br label %17, !dbg !3016

17:                                               ; preds = %3, %3, %16, %15, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %18 = phi i8 [ -1, %16 ], [ 0, %15 ], [ 0, %14 ], [ 0, %13 ], [ 0, %12 ], [ 1, %11 ], [ 3, %10 ], [ 0, %9 ], [ 1, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ]
  %19 = phi i8 [ -1, %16 ], [ 71, %15 ], [ 72, %14 ], [ -128, %13 ], [ 127, %12 ], [ -12, %11 ], [ -24, %10 ], [ -56, %9 ], [ 44, %8 ], [ 4, %7 ], [ 5, %6 ], [ 4, %5 ], [ 5, %4 ], [ 6, %3 ], [ 6, %3 ]
  %20 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3017
  store i8 %18, ptr %1, align 1, !dbg !3018, !tbaa !113
  store i8 %19, ptr %20, align 1, !dbg !3019, !tbaa !113
  %21 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3020
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3021
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3022
  ret void, !dbg !3016
}

; Function Attrs: nounwind
define hidden void @test_ternary(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3023 {
    #dbg_value(ptr %0, !3025, !DIExpression(), !3030)
    #dbg_value(ptr %1, !3026, !DIExpression(), !3030)
    #dbg_value(i8 %2, !3027, !DIExpression(), !3030)
    #dbg_value(i16 10, !3028, !DIExpression(), !3030)
    #dbg_value(i16 20, !3029, !DIExpression(), !3030)
  switch i8 %2, label %8 [
    i8 0, label %9
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
  ], !dbg !3031

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3032)
    #dbg_value(ptr %1, !107, !DIExpression(), !3032)
    #dbg_value(i16 10, !108, !DIExpression(), !3032)
  br label %9, !dbg !3036

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3037)
    #dbg_value(ptr %1, !107, !DIExpression(), !3037)
    #dbg_value(i16 1, !108, !DIExpression(), !3037)
  br label %9, !dbg !3041

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3042)
    #dbg_value(ptr %1, !107, !DIExpression(), !3042)
    #dbg_value(i16 0, !108, !DIExpression(), !3042)
  br label %9, !dbg !3046

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3047)
    #dbg_value(ptr %1, !107, !DIExpression(), !3047)
    #dbg_value(i16 3, !108, !DIExpression(), !3047)
  br label %9, !dbg !3051

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3052)
    #dbg_value(ptr %1, !107, !DIExpression(), !3052)
    #dbg_value(i16 -1, !108, !DIExpression(), !3052)
  br label %9, !dbg !3054

9:                                                ; preds = %3, %8, %7, %6, %5, %4
  %10 = phi i8 [ -1, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %11 = phi i8 [ -1, %8 ], [ 3, %7 ], [ 0, %6 ], [ 1, %5 ], [ 10, %4 ], [ 20, %3 ]
  %12 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3055
  store i8 %10, ptr %1, align 1, !dbg !3056, !tbaa !113
  store i8 %11, ptr %12, align 1, !dbg !3057, !tbaa !113
  %13 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3058
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3059
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3060
  ret void, !dbg !3054
}

; Function Attrs: nounwind
define hidden void @test_casts(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3061 {
    #dbg_value(ptr %0, !3063, !DIExpression(), !3069)
    #dbg_value(ptr %1, !3064, !DIExpression(), !3069)
    #dbg_value(i8 %2, !3065, !DIExpression(), !3069)
  switch i8 %2, label %7 [
    i8 0, label %8
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
  ], !dbg !3070

4:                                                ; preds = %3
    #dbg_value(i16 258, !3067, !DIExpression(), !3069)
    #dbg_value(i8 2, !3068, !DIExpression(), !3069)
    #dbg_value(ptr %0, !106, !DIExpression(), !3071)
    #dbg_value(ptr %1, !107, !DIExpression(), !3071)
    #dbg_value(i16 2, !108, !DIExpression(), !3071)
  br label %8, !dbg !3075

5:                                                ; preds = %3
    #dbg_value(i8 -1, !3068, !DIExpression(), !3069)
    #dbg_value(i16 -1, !3067, !DIExpression(), !3069)
    #dbg_value(ptr %0, !106, !DIExpression(), !3076)
    #dbg_value(ptr %1, !107, !DIExpression(), !3076)
    #dbg_value(i16 -1, !108, !DIExpression(), !3076)
  br label %8, !dbg !3080

6:                                                ; preds = %3
    #dbg_value(i16 1000, !3067, !DIExpression(), !3069)
    #dbg_value(ptr %0, !106, !DIExpression(), !3081)
    #dbg_value(ptr %1, !107, !DIExpression(), !3081)
    #dbg_value(i16 3, !108, !DIExpression(), !3081)
  br label %8, !dbg !3085

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3086)
    #dbg_value(ptr %1, !107, !DIExpression(), !3086)
    #dbg_value(i16 -1, !108, !DIExpression(), !3086)
  br label %8, !dbg !3088

8:                                                ; preds = %3, %7, %6, %5, %4
  %9 = phi i8 [ -1, %7 ], [ 0, %6 ], [ -1, %5 ], [ 0, %4 ], [ %2, %3 ]
  %10 = phi i8 [ -1, %7 ], [ 3, %6 ], [ -1, %5 ], [ 2, %4 ], [ 1, %3 ]
  %11 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3089
  store i8 %9, ptr %1, align 1, !dbg !3090, !tbaa !113
  store i8 %10, ptr %11, align 1, !dbg !3091, !tbaa !113
  %12 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3092
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3093
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3094
  ret void, !dbg !3088
}

; Function Attrs: nounwind
define hidden void @test_if_else(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3095 {
    #dbg_value(ptr %0, !3097, !DIExpression(), !3101)
    #dbg_value(ptr %1, !3098, !DIExpression(), !3101)
    #dbg_value(i8 %2, !3099, !DIExpression(), !3101)
    #dbg_value(i8 %2, !3100, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !3101)
  switch i8 %2, label %8 [
    i8 0, label %9
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
  ], !dbg !3102

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3103)
    #dbg_value(ptr %1, !107, !DIExpression(), !3103)
    #dbg_value(i16 50, !108, !DIExpression(), !3103)
  br label %9, !dbg !3107

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3108)
    #dbg_value(ptr %1, !107, !DIExpression(), !3108)
    #dbg_value(i16 10, !108, !DIExpression(), !3108)
  br label %9, !dbg !3114

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3115)
    #dbg_value(ptr %1, !107, !DIExpression(), !3115)
    #dbg_value(i16 20, !108, !DIExpression(), !3115)
  br label %9, !dbg !3121

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3122)
    #dbg_value(ptr %1, !107, !DIExpression(), !3122)
    #dbg_value(i16 30, !108, !DIExpression(), !3122)
  br label %9, !dbg !3130

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3131)
    #dbg_value(ptr %1, !107, !DIExpression(), !3131)
    #dbg_value(i16 -1, !108, !DIExpression(), !3131)
  br label %9, !dbg !3133

9:                                                ; preds = %3, %8, %7, %6, %5, %4
  %10 = phi i8 [ -1, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %11 = phi i8 [ -1, %8 ], [ 30, %7 ], [ 20, %6 ], [ 10, %5 ], [ 50, %4 ], [ 100, %3 ]
  %12 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3134
  store i8 %10, ptr %1, align 1, !dbg !3135, !tbaa !113
  store i8 %11, ptr %12, align 1, !dbg !3136, !tbaa !113
  %13 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3137
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3138
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3139
  ret void, !dbg !3133
}

; Function Attrs: nounwind
define hidden void @test_loops(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3140 {
    #dbg_value(ptr %0, !3142, !DIExpression(), !3147)
    #dbg_value(ptr %1, !3143, !DIExpression(), !3147)
    #dbg_value(i8 %2, !3144, !DIExpression(), !3147)
  switch i8 %2, label %6 [
    i8 0, label %7
    i8 1, label %7
    i8 2, label %4
    i8 3, label %5
  ], !dbg !3148

4:                                                ; preds = %3
    #dbg_value(i16 0, !3145, !DIExpression(), !3147)
    #dbg_value(i16 10, !3146, !DIExpression(), !3147)
    #dbg_value(i16 10, !3146, !DIExpression(), !3147)
    #dbg_value(i16 0, !3145, !DIExpression(), !3147)
    #dbg_value(i16 1, !3145, !DIExpression(), !3147)
    #dbg_value(i16 11, !3146, !DIExpression(), !3147)
    #dbg_value(ptr %0, !106, !DIExpression(), !3149)
    #dbg_value(ptr %1, !107, !DIExpression(), !3149)
    #dbg_value(i16 1, !108, !DIExpression(), !3149)
  br label %7, !dbg !3153

5:                                                ; preds = %3
    #dbg_value(i16 poison, !3145, !DIExpression(), !3147)
    #dbg_value(i16 poison, !3146, !DIExpression(), !3147)
    #dbg_value(ptr %0, !106, !DIExpression(), !3154)
    #dbg_value(ptr %1, !107, !DIExpression(), !3154)
    #dbg_value(i16 12, !108, !DIExpression(), !3154)
  br label %7, !dbg !3158

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3159)
    #dbg_value(ptr %1, !107, !DIExpression(), !3159)
    #dbg_value(i16 -1, !108, !DIExpression(), !3159)
  br label %7, !dbg !3161

7:                                                ; preds = %3, %3, %6, %5, %4
  %8 = phi i8 [ -1, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ]
  %9 = phi i8 [ -1, %6 ], [ 12, %5 ], [ 1, %4 ], [ 15, %3 ], [ 15, %3 ]
  %10 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3162
  store i8 %8, ptr %1, align 1, !dbg !3163, !tbaa !113
  store i8 %9, ptr %10, align 1, !dbg !3164, !tbaa !113
  %11 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3165
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3166
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3167
  ret void, !dbg !3161
}

; Function Attrs: nounwind
define hidden void @test_globals(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3168 {
    #dbg_value(ptr %0, !3170, !DIExpression(), !3173)
    #dbg_value(ptr %1, !3171, !DIExpression(), !3173)
    #dbg_value(i8 %2, !3172, !DIExpression(), !3173)
  switch i8 %2, label %13 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
    i8 5, label %9
    i8 6, label %10
    i8 7, label %11
    i8 8, label %12
  ], !dbg !3174

4:                                                ; preds = %3
  store i8 42, ptr @g_byte, align 1, !dbg !3175, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !3178)
    #dbg_value(ptr %1, !107, !DIExpression(), !3178)
    #dbg_value(i16 42, !108, !DIExpression(), !3178)
  br label %13, !dbg !3180

5:                                                ; preds = %3
  store i16 1234, ptr @g_short, align 2, !dbg !3181, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3185)
    #dbg_value(ptr %1, !107, !DIExpression(), !3185)
    #dbg_value(i16 1234, !108, !DIExpression(), !3185)
  br label %13, !dbg !3187

6:                                                ; preds = %3
  store i32 100000, ptr @g_int, align 4, !dbg !3188, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !3193)
    #dbg_value(ptr %1, !107, !DIExpression(), !3193)
    #dbg_value(i16 1000, !108, !DIExpression(), !3193)
  br label %13, !dbg !3195

7:                                                ; preds = %3
  store i16 15, ptr @g_short, align 2, !dbg !3196, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3199)
    #dbg_value(ptr %1, !107, !DIExpression(), !3199)
    #dbg_value(i16 15, !108, !DIExpression(), !3199)
  br label %13, !dbg !3201

8:                                                ; preds = %3
  store i8 1, ptr @g_byte, align 1, !dbg !3202, !tbaa !113
  store i16 2, ptr @g_short, align 2, !dbg !3205, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3206)
    #dbg_value(ptr %1, !107, !DIExpression(), !3206)
    #dbg_value(i16 3, !108, !DIExpression(), !3206)
  br label %13, !dbg !3208

9:                                                ; preds = %3
  store i16 11, ptr @g_short, align 2, !dbg !3209, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3212)
    #dbg_value(ptr %1, !107, !DIExpression(), !3212)
    #dbg_value(i16 11, !108, !DIExpression(), !3212)
  br label %13, !dbg !3214

10:                                               ; preds = %3
  store i16 11, ptr @g_short, align 2, !dbg !3215, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3218)
    #dbg_value(ptr %1, !107, !DIExpression(), !3218)
    #dbg_value(i16 10, !108, !DIExpression(), !3218)
  br label %13, !dbg !3220

11:                                               ; preds = %3
  store i16 11, ptr @g_short, align 2, !dbg !3221, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3224)
    #dbg_value(ptr %1, !107, !DIExpression(), !3224)
    #dbg_value(i16 11, !108, !DIExpression(), !3224)
  br label %13, !dbg !3226

12:                                               ; preds = %3
  store i16 9, ptr @g_short, align 2, !dbg !3227, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3230)
    #dbg_value(ptr %1, !107, !DIExpression(), !3230)
    #dbg_value(i16 9, !108, !DIExpression(), !3230)
  br label %13, !dbg !3232

13:                                               ; preds = %3, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %14 = phi i8 [ 0, %12 ], [ 0, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 3, %6 ], [ 4, %5 ], [ 0, %4 ], [ -1, %3 ]
  %15 = phi i8 [ 9, %12 ], [ 11, %11 ], [ 10, %10 ], [ 11, %9 ], [ 3, %8 ], [ 15, %7 ], [ -24, %6 ], [ -46, %5 ], [ 42, %4 ], [ -1, %3 ]
  store i8 %14, ptr %1, align 1, !dbg !3233, !tbaa !113
  %16 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3234
  store i8 %15, ptr %16, align 1, !dbg !3235, !tbaa !113
  %17 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3236
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3237
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3238
  ret void, !dbg !3239
}

; Function Attrs: nounwind
define hidden void @test_arrays(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3240 {
    #dbg_value(ptr %0, !3242, !DIExpression(), !3246)
    #dbg_value(ptr %1, !3243, !DIExpression(), !3246)
    #dbg_value(i8 %2, !3244, !DIExpression(), !3246)
  switch i8 %2, label %24 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
  ], !dbg !3247

4:                                                ; preds = %3
  store i8 10, ptr @shared_fb, align 16, !dbg !3248, !tbaa !113
  store i8 20, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !3251, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !3252)
    #dbg_value(ptr %1, !107, !DIExpression(), !3252)
    #dbg_value(i16 30, !108, !DIExpression(), !3252)
  store i8 0, ptr %1, align 1, !dbg !3254, !tbaa !113
  br label %25, !dbg !3255

5:                                                ; preds = %3
  store i16 100, ptr @g_shorts, align 16, !dbg !3256, !tbaa !3184
  store i16 200, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 2), align 2, !dbg !3259, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3260)
    #dbg_value(ptr %1, !107, !DIExpression(), !3260)
    #dbg_value(i16 300, !108, !DIExpression(), !3260)
  store i8 1, ptr %1, align 1, !dbg !3262, !tbaa !113
  br label %25, !dbg !3263

6:                                                ; preds = %3
    #dbg_value(i16 2, !3245, !DIExpression(), !3246)
  store i16 50, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 4), align 4, !dbg !3264, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3267)
    #dbg_value(ptr %1, !107, !DIExpression(), !3267)
    #dbg_value(i16 50, !108, !DIExpression(), !3267)
  store i8 0, ptr %1, align 1, !dbg !3269, !tbaa !113
  br label %25, !dbg !3270

7:                                                ; preds = %3
  store i16 15, ptr @g_shorts, align 16, !dbg !3271, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3274)
    #dbg_value(ptr %1, !107, !DIExpression(), !3274)
    #dbg_value(i16 15, !108, !DIExpression(), !3274)
  store i8 0, ptr %1, align 1, !dbg !3276, !tbaa !113
  br label %25, !dbg !3277

8:                                                ; preds = %3
  store i8 1, ptr @shared_fb, align 16, !dbg !3278, !tbaa !113
  store i8 2, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !3281, !tbaa !113
  store i8 3, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !3282, !tbaa !113
  store i8 4, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 3), align 1, !dbg !3283, !tbaa !113
  store i16 0, ptr @g_short, align 2, !dbg !3284, !tbaa !3184
    #dbg_value(i16 0, !3245, !DIExpression(), !3246)
    #dbg_value(i16 poison, !3245, !DIExpression(), !3246)
  br label %9, !dbg !3285

9:                                                ; preds = %8, %9
  %10 = phi i32 [ 0, %8 ], [ %18, %9 ]
  %11 = phi i16 [ 0, %8 ], [ %15, %9 ]
  %12 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %10, !dbg !3287
  %13 = load i8, ptr %12, align 1, !dbg !3287, !tbaa !113
  %14 = sext i8 %13 to i16, !dbg !3287
  %15 = add i16 %11, %14, !dbg !3290
    #dbg_value(i16 poison, !3245, !DIExpression(), !3246)
  %16 = shl nsw i32 %10, 16, !dbg !3291
  %17 = add i32 %16, 65536, !dbg !3291
  %18 = ashr exact i32 %17, 16, !dbg !3291
  %19 = icmp slt i32 %18, 4, !dbg !3292
  br i1 %19, label %9, label %20, !dbg !3285, !llvm.loop !3293

20:                                               ; preds = %9
  store i16 %15, ptr @g_short, align 2, !dbg !3295, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !3296)
    #dbg_value(ptr %1, !107, !DIExpression(), !3296)
    #dbg_value(i16 %15, !108, !DIExpression(), !3296)
  %21 = lshr i16 %15, 8, !dbg !3298
  %22 = trunc nuw i16 %21 to i8, !dbg !3299
  store i8 %22, ptr %1, align 1, !dbg !3300, !tbaa !113
  %23 = trunc i16 %15 to i8, !dbg !3301
  br label %25, !dbg !3302

24:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3303)
    #dbg_value(ptr %1, !107, !DIExpression(), !3303)
    #dbg_value(i16 -1, !108, !DIExpression(), !3303)
  store i8 -1, ptr %1, align 1, !dbg !3305, !tbaa !113
  br label %25, !dbg !3306

25:                                               ; preds = %24, %20, %7, %6, %5, %4
  %26 = phi i8 [ -1, %24 ], [ %23, %20 ], [ 15, %7 ], [ 50, %6 ], [ 44, %5 ], [ 30, %4 ]
  %27 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3307
  store i8 %26, ptr %27, align 1, !dbg !3308, !tbaa !113
  %28 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3309
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3310
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3311
  ret void, !dbg !3306
}

; Function Attrs: nounwind
define hidden void @test_structs(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3312 {
    #dbg_value(ptr %0, !3314, !DIExpression(), !3317)
    #dbg_value(ptr %1, !3315, !DIExpression(), !3317)
    #dbg_value(i8 %2, !3316, !DIExpression(), !3317)
  switch i8 %2, label %9 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
  ], !dbg !3318

4:                                                ; preds = %3
  store i16 100, ptr @items, align 16, !dbg !3319, !tbaa !3322
    #dbg_value(ptr %0, !106, !DIExpression(), !3324)
    #dbg_value(ptr %1, !107, !DIExpression(), !3324)
    #dbg_value(i16 100, !108, !DIExpression(), !3324)
  br label %9, !dbg !3326

5:                                                ; preds = %3
  store i16 10, ptr @items, align 16, !dbg !3327, !tbaa !3322
  store i8 1, ptr getelementptr inbounds (i8, ptr @items, i32 2), align 2, !dbg !3330, !tbaa !3331
    #dbg_value(ptr %0, !106, !DIExpression(), !3332)
    #dbg_value(ptr %1, !107, !DIExpression(), !3332)
    #dbg_value(i16 11, !108, !DIExpression(), !3332)
  br label %9, !dbg !3334

6:                                                ; preds = %3
  store i16 1, ptr @items, align 16, !dbg !3335, !tbaa !3322
  store i16 2, ptr getelementptr inbounds (i8, ptr @items, i32 4), align 4, !dbg !3338, !tbaa !3322
  store i16 3, ptr getelementptr inbounds (i8, ptr @items, i32 8), align 8, !dbg !3339, !tbaa !3322
    #dbg_value(ptr %0, !106, !DIExpression(), !3340)
    #dbg_value(ptr %1, !107, !DIExpression(), !3340)
    #dbg_value(i16 6, !108, !DIExpression(), !3340)
  br label %9, !dbg !3342

7:                                                ; preds = %3
  store i16 15, ptr @items, align 16, !dbg !3343, !tbaa !3322
    #dbg_value(ptr %0, !106, !DIExpression(), !3346)
    #dbg_value(ptr %1, !107, !DIExpression(), !3346)
    #dbg_value(i16 15, !108, !DIExpression(), !3346)
  br label %9, !dbg !3348

8:                                                ; preds = %3
  store i16 1, ptr @g_short, align 2, !dbg !3349, !tbaa !3184
  store i16 42, ptr getelementptr inbounds (i8, ptr @items, i32 4), align 4, !dbg !3352, !tbaa !3322
    #dbg_value(ptr %0, !106, !DIExpression(), !3353)
    #dbg_value(ptr %1, !107, !DIExpression(), !3353)
    #dbg_value(i16 42, !108, !DIExpression(), !3353)
  br label %9, !dbg !3355

9:                                                ; preds = %3, %8, %7, %6, %5, %4
  %10 = phi i8 [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ -1, %3 ]
  %11 = phi i8 [ 42, %8 ], [ 15, %7 ], [ 6, %6 ], [ 11, %5 ], [ 100, %4 ], [ -1, %3 ]
  store i8 %10, ptr %1, align 1, !dbg !3356, !tbaa !113
  %12 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3357
  store i8 %11, ptr %12, align 1, !dbg !3358, !tbaa !113
  %13 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3359
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3360
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3361
  ret void, !dbg !3362
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define hidden noundef signext i16 @multiply(i16 noundef signext %0, i16 noundef signext %1) local_unnamed_addr #2 !dbg !3363 {
    #dbg_value(i16 %0, !3365, !DIExpression(), !3367)
    #dbg_value(i16 %1, !3366, !DIExpression(), !3367)
  %3 = mul i16 %1, %0, !dbg !3368
  ret i16 %3, !dbg !3369
}

; Function Attrs: nofree norecurse nosync nounwind memory(none)
define hidden signext i16 @factorial(i16 noundef signext %0) local_unnamed_addr #7 !dbg !3370 {
    #dbg_value(i16 %0, !3374, !DIExpression(), !3376)
    #dbg_value(i16 1, !3375, !DIExpression(), !3376)
  %2 = icmp sgt i16 %0, 1, !dbg !3377
  br i1 %2, label %3, label %9, !dbg !3378

3:                                                ; preds = %1, %3
  %4 = phi i16 [ %6, %3 ], [ 1, %1 ]
  %5 = phi i16 [ %7, %3 ], [ %0, %1 ]
    #dbg_value(i16 %4, !3375, !DIExpression(), !3376)
    #dbg_value(i16 %5, !3374, !DIExpression(), !3376)
  %6 = mul i16 %4, %5, !dbg !3379
    #dbg_value(i16 %6, !3375, !DIExpression(), !3376)
  %7 = add nsw i16 %5, -1, !dbg !3381
    #dbg_value(i16 %7, !3374, !DIExpression(), !3376)
  %8 = icmp sgt i16 %5, 2, !dbg !3377
  br i1 %8, label %3, label %9, !dbg !3378, !llvm.loop !3382

9:                                                ; preds = %3, %1
  %10 = phi i16 [ 1, %1 ], [ %6, %3 ], !dbg !3376
  ret i16 %10, !dbg !3384
}

; Function Attrs: nounwind
define hidden void @test_functions(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3385 {
    #dbg_value(ptr %0, !3387, !DIExpression(), !3390)
    #dbg_value(ptr %1, !3388, !DIExpression(), !3390)
    #dbg_value(i8 %2, !3389, !DIExpression(), !3390)
  switch i8 %2, label %8 [
    i8 0, label %9
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
  ], !dbg !3391

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3392)
    #dbg_value(ptr %1, !107, !DIExpression(), !3392)
    #dbg_value(i16 14, !108, !DIExpression(), !3392)
  br label %9, !dbg !3396

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3397)
    #dbg_value(ptr %1, !107, !DIExpression(), !3397)
    #dbg_value(i16 10, !108, !DIExpression(), !3397)
  br label %9, !dbg !3401

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3402)
    #dbg_value(ptr %1, !107, !DIExpression(), !3402)
    #dbg_value(i16 12, !108, !DIExpression(), !3402)
  br label %9, !dbg !3406

7:                                                ; preds = %3
    #dbg_value(i16 poison, !3375, !DIExpression(), !3407)
    #dbg_value(i16 poison, !3374, !DIExpression(), !3407)
    #dbg_value(ptr %0, !106, !DIExpression(), !3411)
    #dbg_value(ptr %1, !107, !DIExpression(), !3411)
    #dbg_value(i16 120, !108, !DIExpression(), !3411)
  br label %9, !dbg !3413

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3414)
    #dbg_value(ptr %1, !107, !DIExpression(), !3414)
    #dbg_value(i16 -1, !108, !DIExpression(), !3414)
  br label %9, !dbg !3416

9:                                                ; preds = %3, %8, %7, %6, %5, %4
  %10 = phi i8 [ -1, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %11 = phi i8 [ -1, %8 ], [ 120, %7 ], [ 12, %6 ], [ 10, %5 ], [ 14, %4 ], [ 7, %3 ]
  %12 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3417
  store i8 %10, ptr %1, align 1, !dbg !3418, !tbaa !113
  store i8 %11, ptr %12, align 1, !dbg !3419, !tbaa !113
  %13 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3420
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3421
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3422
  ret void, !dbg !3416
}

; Function Attrs: nounwind
define hidden void @test_apdu(ptr noundef %0, ptr nocapture noundef %1, i8 noundef signext %2, i16 noundef signext %3) local_unnamed_addr #0 !dbg !3423 {
    #dbg_value(ptr %0, !3427, !DIExpression(), !3431)
    #dbg_value(ptr %1, !3428, !DIExpression(), !3431)
    #dbg_value(i8 %2, !3429, !DIExpression(), !3431)
    #dbg_value(i16 %3, !3430, !DIExpression(), !3431)
  switch i8 %2, label %21 [
    i8 0, label %5
    i8 1, label %9
    i8 2, label %13
    i8 3, label %16
  ], !dbg !3432

5:                                                ; preds = %4
  %6 = load i8, ptr %1, align 1, !dbg !3433, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !3436)
    #dbg_value(ptr %1, !107, !DIExpression(), !3436)
    #dbg_value(i8 %6, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !3436)
  %7 = ashr i8 %6, 7, !dbg !3438
  store i8 %7, ptr %1, align 1, !dbg !3439, !tbaa !113
  %8 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3440
  store i8 %6, ptr %8, align 1, !dbg !3441, !tbaa !113
  br label %23, !dbg !3442

9:                                                ; preds = %4
  %10 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3443
  %11 = load i8, ptr %10, align 1, !dbg !3443, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !3446)
    #dbg_value(ptr %1, !107, !DIExpression(), !3446)
    #dbg_value(i8 %11, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !3446)
  %12 = ashr i8 %11, 7, !dbg !3448
  store i8 %12, ptr %1, align 1, !dbg !3449, !tbaa !113
  br label %23, !dbg !3450

13:                                               ; preds = %4
  %14 = getelementptr inbounds i8, ptr %1, i32 5, !dbg !3451
  store i8 99, ptr %14, align 1, !dbg !3454, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !3455)
    #dbg_value(ptr %1, !107, !DIExpression(), !3455)
    #dbg_value(i16 99, !108, !DIExpression(), !3455)
  store i8 0, ptr %1, align 1, !dbg !3457, !tbaa !113
  %15 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3458
  store i8 99, ptr %15, align 1, !dbg !3459, !tbaa !113
  br label %23, !dbg !3460

16:                                               ; preds = %4
    #dbg_value(ptr %0, !106, !DIExpression(), !3461)
    #dbg_value(ptr %1, !107, !DIExpression(), !3461)
    #dbg_value(i16 %3, !108, !DIExpression(), !3461)
  %17 = lshr i16 %3, 8, !dbg !3465
  %18 = trunc nuw i16 %17 to i8, !dbg !3466
  store i8 %18, ptr %1, align 1, !dbg !3467, !tbaa !113
  %19 = trunc i16 %3 to i8, !dbg !3468
  %20 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3469
  store i8 %19, ptr %20, align 1, !dbg !3470, !tbaa !113
  br label %23, !dbg !3471

21:                                               ; preds = %4
    #dbg_value(ptr %0, !106, !DIExpression(), !3472)
    #dbg_value(ptr %1, !107, !DIExpression(), !3472)
    #dbg_value(i16 -1, !108, !DIExpression(), !3472)
  store i8 -1, ptr %1, align 1, !dbg !3474, !tbaa !113
  %22 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3475
  store i8 -1, ptr %22, align 1, !dbg !3476, !tbaa !113
  br label %23, !dbg !3477

23:                                               ; preds = %21, %16, %13, %9, %5
  %24 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3478
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3479
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3480
  ret void, !dbg !3477
}

; Function Attrs: nounwind
define hidden void @test_int_ops(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3481 {
    #dbg_value(ptr %0, !3483, !DIExpression(), !3489)
    #dbg_value(ptr %1, !3484, !DIExpression(), !3489)
    #dbg_value(i8 %2, !3485, !DIExpression(), !3489)
    #dbg_value(i32 100000, !3486, !DIExpression(), !3489)
    #dbg_value(i32 50000, !3487, !DIExpression(), !3489)
  switch i8 %2, label %8 [
    i8 0, label %9
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
  ], !dbg !3490

4:                                                ; preds = %3
    #dbg_value(i32 50000, !3488, !DIExpression(), !3489)
    #dbg_value(ptr %0, !106, !DIExpression(), !3491)
    #dbg_value(ptr %1, !107, !DIExpression(), !3491)
    #dbg_value(i16 50, !108, !DIExpression(), !3491)
  br label %9, !dbg !3495

5:                                                ; preds = %3
    #dbg_value(i32 200000, !3488, !DIExpression(), !3489)
    #dbg_value(ptr %0, !106, !DIExpression(), !3496)
    #dbg_value(ptr %1, !107, !DIExpression(), !3496)
    #dbg_value(i16 200, !108, !DIExpression(), !3496)
  br label %9, !dbg !3500

6:                                                ; preds = %3
    #dbg_value(i32 1000, !3488, !DIExpression(), !3489)
    #dbg_value(ptr %0, !106, !DIExpression(), !3501)
    #dbg_value(ptr %1, !107, !DIExpression(), !3501)
    #dbg_value(i16 1000, !108, !DIExpression(), !3501)
  br label %9, !dbg !3505

7:                                                ; preds = %3
  store i16 1000, ptr @g_short, align 2, !dbg !3506, !tbaa !3184
    #dbg_value(i32 101000, !3488, !DIExpression(), !3489)
    #dbg_value(ptr %0, !106, !DIExpression(), !3509)
    #dbg_value(ptr %1, !107, !DIExpression(), !3509)
    #dbg_value(i16 101, !108, !DIExpression(), !3509)
  br label %9, !dbg !3511

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3512)
    #dbg_value(ptr %1, !107, !DIExpression(), !3512)
    #dbg_value(i16 -1, !108, !DIExpression(), !3512)
  br label %9, !dbg !3514

9:                                                ; preds = %3, %8, %7, %6, %5, %4
  %10 = phi i8 [ -1, %8 ], [ 0, %7 ], [ %2, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %11 = phi i8 [ -1, %8 ], [ 101, %7 ], [ -24, %6 ], [ -56, %5 ], [ 50, %4 ], [ -106, %3 ]
  store i8 %10, ptr %1, align 1, !dbg !3515, !tbaa !113
  %12 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3516
  store i8 %11, ptr %12, align 1, !dbg !3517, !tbaa !113
  %13 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3518
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3519
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3520
  ret void, !dbg !3514
}

; Function Attrs: nounwind
define hidden void @test_lshr(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3521 {
    #dbg_value(ptr %0, !3523, !DIExpression(), !3527)
    #dbg_value(ptr %1, !3524, !DIExpression(), !3527)
    #dbg_value(i8 %2, !3525, !DIExpression(), !3527)
  switch i8 %2, label %15 [
    i8 3, label %4
    i8 4, label %10
  ], !dbg !3528

4:                                                ; preds = %3
    #dbg_value(i32 -2147483648, !3526, !DIExpression(), !3527)
  %5 = tail call i32 @lshr_int(i32 noundef -2147483648, i32 noundef 1) #11, !dbg !3529
  %6 = sdiv i32 %5, 65536, !dbg !3532
    #dbg_value(ptr %0, !106, !DIExpression(), !3533)
    #dbg_value(ptr %1, !107, !DIExpression(), !3533)
    #dbg_value(i32 %6, !108, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !3533)
  %7 = lshr i32 %6, 8, !dbg !3535
  %8 = trunc i32 %7 to i8, !dbg !3535
  store i8 %8, ptr %1, align 1, !dbg !3536, !tbaa !113
  %9 = trunc i32 %6 to i8, !dbg !3537
  br label %16, !dbg !3538

10:                                               ; preds = %3
    #dbg_value(i32 -1, !3526, !DIExpression(), !3527)
  %11 = tail call i32 @lshr_int(i32 noundef -1, i32 noundef 16) #11, !dbg !3539
    #dbg_value(ptr %0, !106, !DIExpression(), !3542)
    #dbg_value(ptr %1, !107, !DIExpression(), !3542)
    #dbg_value(i32 %11, !108, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !3542)
  %12 = lshr i32 %11, 8, !dbg !3544
  %13 = trunc i32 %12 to i8, !dbg !3544
  store i8 %13, ptr %1, align 1, !dbg !3545, !tbaa !113
  %14 = trunc i32 %11 to i8, !dbg !3546
  br label %16, !dbg !3547

15:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3548)
    #dbg_value(ptr %1, !107, !DIExpression(), !3548)
    #dbg_value(i16 -1, !108, !DIExpression(), !3548)
  store i8 -1, ptr %1, align 1, !dbg !3550, !tbaa !113
  br label %16, !dbg !3551

16:                                               ; preds = %15, %10, %4
  %17 = phi i8 [ -1, %15 ], [ %14, %10 ], [ %9, %4 ]
  %18 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3552
  store i8 %17, ptr %18, align 1, !dbg !3553, !tbaa !113
  %19 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3554
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3555
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3556
  ret void, !dbg !3551
}

declare !dbg !3557 i32 @lshr_int(i32 noundef, i32 noundef) local_unnamed_addr #1

; Function Attrs: nounwind
define hidden void @test_hex_literals(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3560 {
    #dbg_value(ptr %0, !3562, !DIExpression(), !3567)
    #dbg_value(ptr %1, !3563, !DIExpression(), !3567)
    #dbg_value(i8 %2, !3564, !DIExpression(), !3567)
    #dbg_value(i32 0, !3566, !DIExpression(), !3567)
  switch i8 %2, label %5 [
    i8 0, label %6
    i8 1, label %4
    i8 2, label %6
    i8 3, label %6
    i8 4, label %6
  ], !dbg !3568

4:                                                ; preds = %3
    #dbg_value(i32 -1, !3565, !DIExpression(), !3567)
    #dbg_value(ptr %0, !106, !DIExpression(), !3569)
    #dbg_value(ptr %1, !107, !DIExpression(), !3569)
    #dbg_value(i16 -1, !108, !DIExpression(), !3569)
  br label %6, !dbg !3573

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3574)
    #dbg_value(ptr %1, !107, !DIExpression(), !3574)
    #dbg_value(i16 -1, !108, !DIExpression(), !3574)
  br label %6, !dbg !3576

6:                                                ; preds = %3, %3, %3, %3, %5, %4
  %7 = phi i8 [ -1, %5 ], [ -1, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %8 = phi i8 [ -1, %5 ], [ -1, %4 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ]
  %9 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3577
  store i8 %7, ptr %1, align 1, !dbg !3578, !tbaa !113
  store i8 %8, ptr %9, align 1, !dbg !3579, !tbaa !113
  %10 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3580
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3581
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3582
  ret void, !dbg !3576
}

; Function Attrs: nounwind
define hidden void @test_int_comparison(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3583 {
    #dbg_value(ptr %0, !3585, !DIExpression(), !3590)
    #dbg_value(ptr %1, !3586, !DIExpression(), !3590)
    #dbg_value(i8 %2, !3587, !DIExpression(), !3590)
    #dbg_value(i32 0, !3589, !DIExpression(), !3590)
    #dbg_value(i32 2147483647, !3588, !DIExpression(), !3590)
  switch i8 %2, label %10 [
    i8 0, label %11
    i8 1, label %11
    i8 2, label %4
    i8 3, label %5
    i8 4, label %6
    i8 5, label %11
    i8 6, label %11
    i8 7, label %11
    i8 8, label %7
    i8 9, label %8
    i8 10, label %9
    i8 11, label %11
  ], !dbg !3591

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3592)
    #dbg_value(ptr %1, !107, !DIExpression(), !3592)
    #dbg_value(i16 0, !108, !DIExpression(), !3592)
  br label %11, !dbg !3596

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3597)
    #dbg_value(ptr %1, !107, !DIExpression(), !3597)
    #dbg_value(i16 0, !108, !DIExpression(), !3597)
  br label %11, !dbg !3601

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3602)
    #dbg_value(ptr %1, !107, !DIExpression(), !3602)
    #dbg_value(i16 0, !108, !DIExpression(), !3602)
  br label %11, !dbg !3606

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3607)
    #dbg_value(ptr %1, !107, !DIExpression(), !3607)
    #dbg_value(i16 0, !108, !DIExpression(), !3607)
  br label %11, !dbg !3611

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3612)
    #dbg_value(ptr %1, !107, !DIExpression(), !3612)
    #dbg_value(i16 0, !108, !DIExpression(), !3612)
  br label %11, !dbg !3616

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3617)
    #dbg_value(ptr %1, !107, !DIExpression(), !3617)
    #dbg_value(i16 0, !108, !DIExpression(), !3617)
  br label %11, !dbg !3621

10:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3622)
    #dbg_value(ptr %1, !107, !DIExpression(), !3622)
    #dbg_value(i16 -1, !108, !DIExpression(), !3622)
  br label %11, !dbg !3624

11:                                               ; preds = %3, %3, %3, %3, %3, %3, %10, %9, %8, %7, %6, %5, %4
  %12 = phi i8 [ -1, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %13 = phi i8 [ -1, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ]
  %14 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3625
  store i8 %12, ptr %1, align 1, !dbg !3626, !tbaa !113
  store i8 %13, ptr %14, align 1, !dbg !3627, !tbaa !113
  %15 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3628
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3629
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3630
  ret void, !dbg !3624
}

; Function Attrs: nounwind
define hidden void @test_const_arrays(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3631 {
    #dbg_value(ptr %0, !3633, !DIExpression(), !3638)
    #dbg_value(ptr %1, !3634, !DIExpression(), !3638)
    #dbg_value(i8 %2, !3635, !DIExpression(), !3638)
  switch i8 %2, label %13 [
    i8 0, label %14
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %10
    i8 8, label %11
    i8 9, label %12
  ], !dbg !3639

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3640)
    #dbg_value(ptr %1, !107, !DIExpression(), !3640)
    #dbg_value(i16 127, !108, !DIExpression(), !3640)
  br label %14, !dbg !3644

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3645)
    #dbg_value(ptr %1, !107, !DIExpression(), !3645)
    #dbg_value(i16 -1, !108, !DIExpression(), !3645)
  br label %14, !dbg !3649

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3650)
    #dbg_value(ptr %1, !107, !DIExpression(), !3650)
    #dbg_value(i16 100, !108, !DIExpression(), !3650)
  br label %14, !dbg !3654

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3655)
    #dbg_value(ptr %1, !107, !DIExpression(), !3655)
    #dbg_value(i16 300, !108, !DIExpression(), !3655)
  br label %14, !dbg !3659

8:                                                ; preds = %3
    #dbg_value(i16 poison, !3637, !DIExpression(), !3638)
    #dbg_value(i16 poison, !3636, !DIExpression(), !3638)
    #dbg_value(ptr %0, !106, !DIExpression(), !3660)
    #dbg_value(ptr %1, !107, !DIExpression(), !3660)
    #dbg_value(i16 1000, !108, !DIExpression(), !3660)
  br label %14, !dbg !3664

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3665)
    #dbg_value(ptr %1, !107, !DIExpression(), !3665)
    #dbg_value(i16 100, !108, !DIExpression(), !3665)
  br label %14, !dbg !3669

10:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3670)
    #dbg_value(ptr %1, !107, !DIExpression(), !3670)
    #dbg_value(i16 200, !108, !DIExpression(), !3670)
  br label %14, !dbg !3674

11:                                               ; preds = %3
    #dbg_value(i16 1, !3636, !DIExpression(), !3638)
    #dbg_value(ptr %0, !106, !DIExpression(), !3675)
    #dbg_value(ptr %1, !107, !DIExpression(), !3675)
    #dbg_value(i16 200, !108, !DIExpression(), !3675)
  br label %14, !dbg !3679

12:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3680)
    #dbg_value(ptr %1, !107, !DIExpression(), !3680)
    #dbg_value(i16 300, !108, !DIExpression(), !3680)
  br label %14, !dbg !3684

13:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3685)
    #dbg_value(ptr %1, !107, !DIExpression(), !3685)
    #dbg_value(i16 -1, !108, !DIExpression(), !3685)
  br label %14, !dbg !3687

14:                                               ; preds = %3, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %15 = phi i8 [ -1, %13 ], [ 1, %12 ], [ 0, %11 ], [ 0, %10 ], [ 0, %9 ], [ 3, %8 ], [ 1, %7 ], [ 0, %6 ], [ -1, %5 ], [ 0, %4 ], [ %2, %3 ]
  %16 = phi i8 [ -1, %13 ], [ 44, %12 ], [ -56, %11 ], [ -56, %10 ], [ 100, %9 ], [ -24, %8 ], [ 44, %7 ], [ 100, %6 ], [ -1, %5 ], [ 127, %4 ], [ %2, %3 ]
  %17 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3688
  store i8 %15, ptr %1, align 1, !dbg !3689, !tbaa !113
  store i8 %16, ptr %17, align 1, !dbg !3690, !tbaa !113
  %18 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3691
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3692
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3693
  ret void, !dbg !3687
}

; Function Attrs: nounwind
define hidden void @test_zero_comparison(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3694 {
    #dbg_value(ptr %0, !3696, !DIExpression(), !3701)
    #dbg_value(ptr %1, !3697, !DIExpression(), !3701)
    #dbg_value(i8 %2, !3698, !DIExpression(), !3701)
  switch i8 %2, label %9 [
    i8 0, label %10
    i8 1, label %4
    i8 2, label %10
    i8 3, label %5
    i8 4, label %10
    i8 5, label %6
    i8 6, label %10
    i8 7, label %7
    i8 8, label %10
    i8 9, label %10
    i8 10, label %10
    i8 11, label %8
    i8 12, label %10
    i8 13, label %10
    i8 14, label %10
  ], !dbg !3702

4:                                                ; preds = %3
    #dbg_value(i16 1, !3699, !DIExpression(), !3701)
    #dbg_value(ptr %0, !106, !DIExpression(), !3703)
    #dbg_value(ptr %1, !107, !DIExpression(), !3703)
    #dbg_value(i16 0, !108, !DIExpression(), !3703)
  br label %10, !dbg !3707

5:                                                ; preds = %3
    #dbg_value(i16 0, !3699, !DIExpression(), !3701)
    #dbg_value(ptr %0, !106, !DIExpression(), !3708)
    #dbg_value(ptr %1, !107, !DIExpression(), !3708)
    #dbg_value(i16 0, !108, !DIExpression(), !3708)
  br label %10, !dbg !3712

6:                                                ; preds = %3
    #dbg_value(i16 0, !3699, !DIExpression(), !3701)
    #dbg_value(ptr %0, !106, !DIExpression(), !3713)
    #dbg_value(ptr %1, !107, !DIExpression(), !3713)
    #dbg_value(i16 0, !108, !DIExpression(), !3713)
  br label %10, !dbg !3717

7:                                                ; preds = %3
    #dbg_value(i16 0, !3699, !DIExpression(), !3701)
    #dbg_value(ptr %0, !106, !DIExpression(), !3718)
    #dbg_value(ptr %1, !107, !DIExpression(), !3718)
    #dbg_value(i16 0, !108, !DIExpression(), !3718)
  br label %10, !dbg !3722

8:                                                ; preds = %3
    #dbg_value(i16 0, !3699, !DIExpression(), !3701)
    #dbg_value(ptr %0, !106, !DIExpression(), !3723)
    #dbg_value(ptr %1, !107, !DIExpression(), !3723)
    #dbg_value(i16 0, !108, !DIExpression(), !3723)
  br label %10, !dbg !3727

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3728)
    #dbg_value(ptr %1, !107, !DIExpression(), !3728)
    #dbg_value(i16 -1, !108, !DIExpression(), !3728)
  br label %10, !dbg !3730

10:                                               ; preds = %3, %3, %3, %3, %3, %3, %3, %3, %3, %3, %9, %8, %7, %6, %5, %4
  %11 = phi i8 [ -1, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %12 = phi i8 [ -1, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ]
  %13 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3731
  store i8 %11, ptr %1, align 1, !dbg !3732, !tbaa !113
  store i8 %12, ptr %13, align 1, !dbg !3733, !tbaa !113
  %14 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3734
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3735
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3736
  ret void, !dbg !3730
}

; Function Attrs: nounwind
define hidden void @test_overflow(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3737 {
    #dbg_value(ptr %0, !3739, !DIExpression(), !3744)
    #dbg_value(ptr %1, !3740, !DIExpression(), !3744)
    #dbg_value(i8 %2, !3741, !DIExpression(), !3744)
  switch i8 %2, label %10 [
    i8 0, label %11
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %11
  ], !dbg !3745

4:                                                ; preds = %3
    #dbg_value(i16 -32768, !3742, !DIExpression(), !3744)
    #dbg_value(ptr %0, !106, !DIExpression(), !3746)
    #dbg_value(ptr %1, !107, !DIExpression(), !3746)
    #dbg_value(i16 32767, !108, !DIExpression(), !3746)
  br label %11, !dbg !3750

5:                                                ; preds = %3
    #dbg_value(i16 200, !3742, !DIExpression(), !3744)
    #dbg_value(ptr %0, !106, !DIExpression(), !3751)
    #dbg_value(ptr %1, !107, !DIExpression(), !3751)
    #dbg_value(i16 -25536, !108, !DIExpression(), !3751)
  br label %11, !dbg !3755

6:                                                ; preds = %3
    #dbg_value(i32 2147483647, !3743, !DIExpression(), !3744)
    #dbg_value(ptr %0, !106, !DIExpression(), !3756)
    #dbg_value(ptr %1, !107, !DIExpression(), !3756)
    #dbg_value(i16 0, !108, !DIExpression(), !3756)
  br label %11, !dbg !3760

7:                                                ; preds = %3
    #dbg_value(i16 32767, !3742, !DIExpression(), !3744)
    #dbg_value(i16 -2, !3742, !DIExpression(), !3744)
    #dbg_value(ptr %0, !106, !DIExpression(), !3761)
    #dbg_value(ptr %1, !107, !DIExpression(), !3761)
    #dbg_value(i16 -2, !108, !DIExpression(), !3761)
  br label %11, !dbg !3765

8:                                                ; preds = %3
    #dbg_value(i16 0, !3742, !DIExpression(), !3744)
    #dbg_value(i16 -1, !3742, !DIExpression(), !3744)
    #dbg_value(ptr %0, !106, !DIExpression(), !3766)
    #dbg_value(ptr %1, !107, !DIExpression(), !3766)
    #dbg_value(i16 -1, !108, !DIExpression(), !3766)
  br label %11, !dbg !3770

9:                                                ; preds = %3
    #dbg_value(i16 -1, !3742, !DIExpression(), !3744)
    #dbg_value(i16 -2, !3742, !DIExpression(), !3744)
    #dbg_value(ptr %0, !106, !DIExpression(), !3771)
    #dbg_value(ptr %1, !107, !DIExpression(), !3771)
    #dbg_value(i16 -2, !108, !DIExpression(), !3771)
  br label %11, !dbg !3775

10:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3776)
    #dbg_value(ptr %1, !107, !DIExpression(), !3776)
    #dbg_value(i16 -1, !108, !DIExpression(), !3776)
  br label %11, !dbg !3778

11:                                               ; preds = %3, %3, %10, %9, %8, %7, %6, %5, %4
  %12 = phi i8 [ -1, %10 ], [ -1, %9 ], [ -1, %8 ], [ -1, %7 ], [ 0, %6 ], [ -100, %5 ], [ 127, %4 ], [ -128, %3 ], [ -128, %3 ]
  %13 = phi i8 [ -1, %10 ], [ -2, %9 ], [ -1, %8 ], [ -2, %7 ], [ 0, %6 ], [ 64, %5 ], [ -1, %4 ], [ 0, %3 ], [ 0, %3 ]
  %14 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3779
  store i8 %12, ptr %1, align 1, !dbg !3780, !tbaa !113
  store i8 %13, ptr %14, align 1, !dbg !3781, !tbaa !113
  %15 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3782
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3783
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3784
  ret void, !dbg !3778
}

; Function Attrs: nounwind
define hidden void @test_negative_math(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3785 {
    #dbg_value(ptr %0, !3787, !DIExpression(), !3793)
    #dbg_value(ptr %1, !3788, !DIExpression(), !3793)
    #dbg_value(i8 %2, !3789, !DIExpression(), !3793)
  switch i8 %2, label %14 [
    i8 0, label %15
    i8 1, label %15
    i8 2, label %4
    i8 3, label %5
    i8 4, label %6
    i8 5, label %7
    i8 6, label %8
    i8 7, label %9
    i8 8, label %10
    i8 9, label %11
    i8 10, label %12
    i8 11, label %13
  ], !dbg !3794

4:                                                ; preds = %3
    #dbg_value(i16 -10, !3790, !DIExpression(), !3793)
    #dbg_value(i16 -3, !3791, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3795)
    #dbg_value(ptr %1, !107, !DIExpression(), !3795)
    #dbg_value(i16 3, !108, !DIExpression(), !3795)
  br label %15, !dbg !3799

5:                                                ; preds = %3
    #dbg_value(i16 -10, !3790, !DIExpression(), !3793)
    #dbg_value(i16 3, !3791, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3800)
    #dbg_value(ptr %1, !107, !DIExpression(), !3800)
    #dbg_value(i16 -1, !108, !DIExpression(), !3800)
  br label %15, !dbg !3804

6:                                                ; preds = %3
    #dbg_value(i16 10, !3790, !DIExpression(), !3793)
    #dbg_value(i16 -3, !3791, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3805)
    #dbg_value(ptr %1, !107, !DIExpression(), !3805)
    #dbg_value(i16 1, !108, !DIExpression(), !3805)
  br label %15, !dbg !3809

7:                                                ; preds = %3
    #dbg_value(i16 -10, !3790, !DIExpression(), !3793)
    #dbg_value(i16 -3, !3791, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3810)
    #dbg_value(ptr %1, !107, !DIExpression(), !3810)
    #dbg_value(i16 -1, !108, !DIExpression(), !3810)
  br label %15, !dbg !3814

8:                                                ; preds = %3
    #dbg_value(i16 -1, !3790, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3815)
    #dbg_value(ptr %1, !107, !DIExpression(), !3815)
    #dbg_value(i16 -1, !108, !DIExpression(), !3815)
  br label %15, !dbg !3819

9:                                                ; preds = %3
    #dbg_value(i16 -128, !3790, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3820)
    #dbg_value(ptr %1, !107, !DIExpression(), !3820)
    #dbg_value(i16 -8, !108, !DIExpression(), !3820)
  br label %15, !dbg !3824

10:                                               ; preds = %3
    #dbg_value(i32 -1, !3792, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3825)
    #dbg_value(ptr %1, !107, !DIExpression(), !3825)
    #dbg_value(i16 -1, !108, !DIExpression(), !3825)
  br label %15, !dbg !3829

11:                                               ; preds = %3
    #dbg_value(i16 -1, !3790, !DIExpression(), !3793)
    #dbg_value(i16 2, !3791, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3830)
    #dbg_value(ptr %1, !107, !DIExpression(), !3830)
    #dbg_value(i16 -2, !108, !DIExpression(), !3830)
  br label %15, !dbg !3834

12:                                               ; preds = %3
    #dbg_value(i16 -100, !3790, !DIExpression(), !3793)
    #dbg_value(i16 -10, !3791, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3835)
    #dbg_value(ptr %1, !107, !DIExpression(), !3835)
    #dbg_value(i16 1000, !108, !DIExpression(), !3835)
  br label %15, !dbg !3839

13:                                               ; preds = %3
    #dbg_value(i16 -1, !3790, !DIExpression(), !3793)
    #dbg_value(ptr %0, !106, !DIExpression(), !3840)
    #dbg_value(ptr %1, !107, !DIExpression(), !3840)
    #dbg_value(i16 255, !108, !DIExpression(), !3840)
  br label %15, !dbg !3844

14:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3845)
    #dbg_value(ptr %1, !107, !DIExpression(), !3845)
    #dbg_value(i16 -1, !108, !DIExpression(), !3845)
  br label %15, !dbg !3847

15:                                               ; preds = %3, %3, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %16 = phi i8 [ -1, %14 ], [ 0, %13 ], [ 3, %12 ], [ -1, %11 ], [ -1, %10 ], [ -1, %9 ], [ -1, %8 ], [ -1, %7 ], [ 0, %6 ], [ -1, %5 ], [ 0, %4 ], [ -1, %3 ], [ -1, %3 ]
  %17 = phi i8 [ -1, %14 ], [ -1, %13 ], [ -24, %12 ], [ -2, %11 ], [ -1, %10 ], [ -8, %9 ], [ -1, %8 ], [ -1, %7 ], [ 1, %6 ], [ -1, %5 ], [ 3, %4 ], [ -3, %3 ], [ -3, %3 ]
  %18 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3848
  store i8 %16, ptr %1, align 1, !dbg !3849, !tbaa !113
  store i8 %17, ptr %18, align 1, !dbg !3850, !tbaa !113
  %19 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3851
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3852
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3853
  ret void, !dbg !3847
}

; Function Attrs: nounwind
define hidden void @test_coercion(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3854 {
    #dbg_value(ptr %0, !3856, !DIExpression(), !3862)
    #dbg_value(ptr %1, !3857, !DIExpression(), !3862)
    #dbg_value(i8 %2, !3858, !DIExpression(), !3862)
  switch i8 %2, label %15 [
    i8 0, label %16
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
    i8 11, label %14
  ], !dbg !3863

4:                                                ; preds = %3
    #dbg_value(i16 100, !3860, !DIExpression(), !3862)
    #dbg_value(i32 200, !3861, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3864)
    #dbg_value(ptr %1, !107, !DIExpression(), !3864)
    #dbg_value(i16 300, !108, !DIExpression(), !3864)
  br label %16, !dbg !3868

5:                                                ; preds = %3
    #dbg_value(i8 -1, !3859, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3869)
    #dbg_value(ptr %1, !107, !DIExpression(), !3869)
    #dbg_value(i16 -1, !108, !DIExpression(), !3869)
  br label %16, !dbg !3873

6:                                                ; preds = %3
    #dbg_value(i8 -1, !3859, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3874)
    #dbg_value(ptr %1, !107, !DIExpression(), !3874)
    #dbg_value(i16 255, !108, !DIExpression(), !3874)
  br label %16, !dbg !3878

7:                                                ; preds = %3
    #dbg_value(i8 100, !3859, !DIExpression(), !3862)
    #dbg_value(i16 200, !3860, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3879)
    #dbg_value(ptr %1, !107, !DIExpression(), !3879)
    #dbg_value(i16 20000, !108, !DIExpression(), !3879)
  br label %16, !dbg !3883

8:                                                ; preds = %3
    #dbg_value(i8 50, !3859, !DIExpression(), !3862)
    #dbg_value(i32 100, !3861, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3884)
    #dbg_value(ptr %1, !107, !DIExpression(), !3884)
    #dbg_value(i16 150, !108, !DIExpression(), !3884)
  br label %16, !dbg !3888

9:                                                ; preds = %3
    #dbg_value(i16 -1, !3860, !DIExpression(), !3862)
    #dbg_value(i32 -1, !3861, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3889)
    #dbg_value(ptr %1, !107, !DIExpression(), !3889)
    #dbg_value(i16 -1, !108, !DIExpression(), !3889)
  br label %16, !dbg !3893

10:                                               ; preds = %3
    #dbg_value(i32 65537, !3861, !DIExpression(), !3862)
    #dbg_value(i16 1, !3860, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3894)
    #dbg_value(ptr %1, !107, !DIExpression(), !3894)
    #dbg_value(i16 1, !108, !DIExpression(), !3894)
  br label %16, !dbg !3898

11:                                               ; preds = %3
    #dbg_value(i8 127, !3859, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3899)
    #dbg_value(ptr %1, !107, !DIExpression(), !3899)
    #dbg_value(i16 128, !108, !DIExpression(), !3899)
  br label %16, !dbg !3903

12:                                               ; preds = %3
    #dbg_value(i8 -128, !3859, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3904)
    #dbg_value(ptr %1, !107, !DIExpression(), !3904)
    #dbg_value(i16 -129, !108, !DIExpression(), !3904)
  br label %16, !dbg !3908

13:                                               ; preds = %3
    #dbg_value(i8 10, !3859, !DIExpression(), !3862)
    #dbg_value(i16 20, !3860, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3909)
    #dbg_value(ptr %1, !107, !DIExpression(), !3909)
    #dbg_value(i16 1, !108, !DIExpression(), !3909)
  br label %16, !dbg !3913

14:                                               ; preds = %3
    #dbg_value(i16 100, !3860, !DIExpression(), !3862)
    #dbg_value(i32 100, !3861, !DIExpression(), !3862)
    #dbg_value(ptr %0, !106, !DIExpression(), !3914)
    #dbg_value(ptr %1, !107, !DIExpression(), !3914)
    #dbg_value(i16 1, !108, !DIExpression(), !3914)
  br label %16, !dbg !3918

15:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !3919)
    #dbg_value(ptr %1, !107, !DIExpression(), !3919)
    #dbg_value(i16 -1, !108, !DIExpression(), !3919)
  br label %16, !dbg !3921

16:                                               ; preds = %3, %15, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %17 = phi i8 [ -1, %15 ], [ 0, %14 ], [ 0, %13 ], [ -1, %12 ], [ 0, %11 ], [ 0, %10 ], [ -1, %9 ], [ 0, %8 ], [ 78, %7 ], [ 0, %6 ], [ -1, %5 ], [ %2, %4 ], [ %2, %3 ]
  %18 = phi i8 [ -1, %15 ], [ 1, %14 ], [ 1, %13 ], [ 127, %12 ], [ -128, %11 ], [ 1, %10 ], [ -1, %9 ], [ -106, %8 ], [ 32, %7 ], [ -1, %6 ], [ -1, %5 ], [ 44, %4 ], [ 30, %3 ]
  %19 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3922
  store i8 %17, ptr %1, align 1, !dbg !3923, !tbaa !113
  store i8 %18, ptr %19, align 1, !dbg !3924, !tbaa !113
  %20 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3925
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3926
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3927
  ret void, !dbg !3921
}

; Function Attrs: nounwind
define hidden void @test_switch_dense(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3928 {
    #dbg_value(ptr %0, !3930, !DIExpression(), !3934)
    #dbg_value(ptr %1, !3931, !DIExpression(), !3934)
    #dbg_value(i8 %2, !3932, !DIExpression(), !3934)
  switch i8 %2, label %11 [
    i8 0, label %12
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %10
  ], !dbg !3935

4:                                                ; preds = %3
    #dbg_value(i16 101, !3933, !DIExpression(), !3934)
  br label %12, !dbg !3936

5:                                                ; preds = %3
    #dbg_value(i16 102, !3933, !DIExpression(), !3934)
  br label %12, !dbg !3938

6:                                                ; preds = %3
    #dbg_value(i16 103, !3933, !DIExpression(), !3934)
  br label %12, !dbg !3939

7:                                                ; preds = %3
    #dbg_value(i16 104, !3933, !DIExpression(), !3934)
  br label %12, !dbg !3940

8:                                                ; preds = %3
    #dbg_value(i16 105, !3933, !DIExpression(), !3934)
  br label %12, !dbg !3941

9:                                                ; preds = %3
    #dbg_value(i16 106, !3933, !DIExpression(), !3934)
  br label %12, !dbg !3942

10:                                               ; preds = %3
    #dbg_value(i16 107, !3933, !DIExpression(), !3934)
  br label %12, !dbg !3943

11:                                               ; preds = %3
    #dbg_value(i16 -1, !3933, !DIExpression(), !3934)
  br label %12, !dbg !3944

12:                                               ; preds = %3, %11, %10, %9, %8, %7, %6, %5, %4
  %13 = phi i8 [ -1, %11 ], [ 107, %10 ], [ 106, %9 ], [ 105, %8 ], [ 104, %7 ], [ 103, %6 ], [ 102, %5 ], [ 101, %4 ], [ 100, %3 ]
  %14 = phi i8 [ -1, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
    #dbg_value(i16 poison, !3933, !DIExpression(), !3934)
    #dbg_value(ptr %0, !106, !DIExpression(), !3945)
    #dbg_value(ptr %1, !107, !DIExpression(), !3945)
    #dbg_value(i16 poison, !108, !DIExpression(), !3945)
  store i8 %14, ptr %1, align 1, !dbg !3947, !tbaa !113
  %15 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3948
  store i8 %13, ptr %15, align 1, !dbg !3949, !tbaa !113
  %16 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3950
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3951
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3952
  ret void, !dbg !3953
}

; Function Attrs: nounwind
define hidden void @test_switch_sparse(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3954 {
    #dbg_value(ptr %0, !3956, !DIExpression(), !3960)
    #dbg_value(ptr %1, !3957, !DIExpression(), !3960)
    #dbg_value(i8 %2, !3958, !DIExpression(), !3960)
  switch i8 %2, label %8 [
    i8 1, label %9
    i8 10, label %4
    i8 50, label %5
    i8 100, label %6
    i8 120, label %7
  ], !dbg !3961

4:                                                ; preds = %3
    #dbg_value(i16 20, !3959, !DIExpression(), !3960)
  br label %9, !dbg !3962

5:                                                ; preds = %3
    #dbg_value(i16 30, !3959, !DIExpression(), !3960)
  br label %9, !dbg !3964

6:                                                ; preds = %3
    #dbg_value(i16 40, !3959, !DIExpression(), !3960)
  br label %9, !dbg !3965

7:                                                ; preds = %3
    #dbg_value(i16 50, !3959, !DIExpression(), !3960)
  br label %9, !dbg !3966

8:                                                ; preds = %3
    #dbg_value(i16 -1, !3959, !DIExpression(), !3960)
  br label %9, !dbg !3967

9:                                                ; preds = %3, %8, %7, %6, %5, %4
  %10 = phi i8 [ -1, %8 ], [ 50, %7 ], [ 40, %6 ], [ 30, %5 ], [ 20, %4 ], [ 10, %3 ]
  %11 = phi i8 [ -1, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ]
    #dbg_value(i16 poison, !3959, !DIExpression(), !3960)
    #dbg_value(ptr %0, !106, !DIExpression(), !3968)
    #dbg_value(ptr %1, !107, !DIExpression(), !3968)
    #dbg_value(i16 poison, !108, !DIExpression(), !3968)
  store i8 %11, ptr %1, align 1, !dbg !3970, !tbaa !113
  %12 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !3971
  store i8 %10, ptr %12, align 1, !dbg !3972, !tbaa !113
  %13 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !3973
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !3974
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !3975
  ret void, !dbg !3976
}

; Function Attrs: nounwind
define hidden void @test_break_continue(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !3977 {
    #dbg_value(ptr %0, !3979, !DIExpression(), !3990)
    #dbg_value(ptr %1, !3980, !DIExpression(), !3990)
    #dbg_value(i8 %2, !3981, !DIExpression(), !3990)
  switch i8 %2, label %7 [
    i8 0, label %8
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
  ], !dbg !3991

4:                                                ; preds = %3
    #dbg_value(i16 poison, !3983, !DIExpression(), !3990)
    #dbg_value(i16 poison, !3982, !DIExpression(), !3990)
    #dbg_value(ptr %0, !106, !DIExpression(), !3992)
    #dbg_value(ptr %1, !107, !DIExpression(), !3992)
    #dbg_value(i16 9, !108, !DIExpression(), !3992)
  br label %8, !dbg !3996

5:                                                ; preds = %3
    #dbg_value(i16 poison, !3983, !DIExpression(), !3990)
    #dbg_value(i16 poison, !3982, !DIExpression(), !3990)
    #dbg_value(ptr %0, !106, !DIExpression(), !3997)
    #dbg_value(ptr %1, !107, !DIExpression(), !3997)
    #dbg_value(i16 12, !108, !DIExpression(), !3997)
  br label %8, !dbg !4001

6:                                                ; preds = %3
    #dbg_value(i16 poison, !3983, !DIExpression(), !3990)
    #dbg_value(i16 poison, !3982, !DIExpression(), !3990)
    #dbg_value(ptr %0, !106, !DIExpression(), !4002)
    #dbg_value(ptr %1, !107, !DIExpression(), !4002)
    #dbg_value(i16 6, !108, !DIExpression(), !4002)
  br label %8, !dbg !4004

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4005)
    #dbg_value(ptr %1, !107, !DIExpression(), !4005)
    #dbg_value(i16 -1, !108, !DIExpression(), !4005)
  br label %8, !dbg !4007

8:                                                ; preds = %3, %7, %6, %5, %4
  %9 = phi i8 [ -1, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %10 = phi i8 [ -1, %7 ], [ 6, %6 ], [ 12, %5 ], [ 9, %4 ], [ 3, %3 ]
  %11 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4008
  store i8 %9, ptr %1, align 1, !dbg !4009, !tbaa !113
  store i8 %10, ptr %11, align 1, !dbg !4010, !tbaa !113
  %12 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4011
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4012
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4013
  ret void, !dbg !4007
}

; Function Attrs: nounwind
define hidden void @test_complex_boolean(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4014 {
    #dbg_value(ptr %0, !4016, !DIExpression(), !4027)
    #dbg_value(ptr %1, !4017, !DIExpression(), !4027)
    #dbg_value(i8 %2, !4018, !DIExpression(), !4027)
    #dbg_value(i16 5, !4019, !DIExpression(), !4027)
    #dbg_value(i16 10, !4020, !DIExpression(), !4027)
    #dbg_value(i16 15, !4021, !DIExpression(), !4027)
    #dbg_value(i16 20, !4022, !DIExpression(), !4027)
  switch i8 %2, label %6 [
    i8 0, label %7
    i8 1, label %7
    i8 2, label %4
    i8 3, label %7
    i8 4, label %7
    i8 5, label %5
    i8 6, label %7
    i8 7, label %7
  ], !dbg !4028

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4029)
    #dbg_value(ptr %1, !107, !DIExpression(), !4029)
    #dbg_value(i16 0, !108, !DIExpression(), !4029)
  br label %7, !dbg !4033

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4034)
    #dbg_value(ptr %1, !107, !DIExpression(), !4034)
    #dbg_value(i16 0, !108, !DIExpression(), !4034)
  br label %7, !dbg !4038

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4039)
    #dbg_value(ptr %1, !107, !DIExpression(), !4039)
    #dbg_value(i16 -1, !108, !DIExpression(), !4039)
  br label %7, !dbg !4041

7:                                                ; preds = %3, %3, %3, %3, %3, %3, %6, %5, %4
  %8 = phi i8 [ -1, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %9 = phi i8 [ -1, %6 ], [ 0, %5 ], [ 0, %4 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ]
  %10 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4042
  store i8 %8, ptr %1, align 1, !dbg !4043, !tbaa !113
  store i8 %9, ptr %10, align 1, !dbg !4044, !tbaa !113
  %11 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4045
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4046
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4047
  ret void, !dbg !4041
}

; Function Attrs: nounwind
define hidden void @test_deep_nesting(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4048 {
    #dbg_value(ptr %0, !4050, !DIExpression(), !4068)
    #dbg_value(ptr %1, !4051, !DIExpression(), !4068)
    #dbg_value(i8 %2, !4052, !DIExpression(), !4068)
    #dbg_value(i8 %2, !4053, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4068)
    #dbg_value(i16 0, !4054, !DIExpression(), !4068)
  switch i8 %2, label %28 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
  ], !dbg !4069

4:                                                ; preds = %3
    #dbg_value(i8 %2, !4053, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_stack_value), !4068)
    #dbg_value(i16 100, !4054, !DIExpression(), !4068)
    #dbg_value(i16 100, !4054, !DIExpression(), !4068)
    #dbg_value(ptr %0, !106, !DIExpression(), !4070)
    #dbg_value(ptr %1, !107, !DIExpression(), !4070)
    #dbg_value(i16 100, !108, !DIExpression(), !4070)
  store i8 0, ptr %1, align 1, !dbg !4074, !tbaa !113
  br label %29, !dbg !4075

5:                                                ; preds = %3
    #dbg_value(i16 poison, !4054, !DIExpression(), !4068)
    #dbg_value(i16 poison, !4058, !DIExpression(), !4076)
    #dbg_value(i16 poison, !4055, !DIExpression(), !4076)
    #dbg_value(ptr %0, !106, !DIExpression(), !4077)
    #dbg_value(ptr %1, !107, !DIExpression(), !4077)
    #dbg_value(i16 9, !108, !DIExpression(), !4077)
  store i8 0, ptr %1, align 1, !dbg !4079, !tbaa !113
  br label %29

6:                                                ; preds = %3
    #dbg_value(i16 poison, !4054, !DIExpression(), !4068)
    #dbg_value(i32 poison, !4063, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !4080)
    #dbg_value(i32 poison, !4062, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !4080)
    #dbg_value(i32 poison, !4059, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !4080)
    #dbg_value(ptr %0, !106, !DIExpression(), !4081)
    #dbg_value(ptr %1, !107, !DIExpression(), !4081)
    #dbg_value(i16 8, !108, !DIExpression(), !4081)
  store i8 0, ptr %1, align 1, !dbg !4083, !tbaa !113
  br label %29

7:                                                ; preds = %3, %18
  %8 = phi i32 [ %22, %18 ], [ 0, %3 ]
  %9 = phi i16 [ %19, %18 ], [ 0, %3 ]
    #dbg_value(i16 %9, !4054, !DIExpression(), !4068)
  %10 = icmp sgt i32 %8, 0, !dbg !4084
  br i1 %10, label %11, label %18, !dbg !4089

11:                                               ; preds = %7, %11
  %12 = phi i32 [ %16, %11 ], [ 0, %7 ]
  %13 = phi i16 [ %14, %11 ], [ %9, %7 ]
    #dbg_value(i16 %13, !4054, !DIExpression(), !4068)
  %14 = add i16 %13, 1, !dbg !4090
    #dbg_value(i16 %14, !4054, !DIExpression(), !4068)
  %15 = add nuw nsw i32 %12, 1, !dbg !4095
    #dbg_value(i32 %15, !4067, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !4096)
  %16 = and i32 %15, 65535, !dbg !4097
    #dbg_value(i32 %15, !4067, !DIExpression(), !4096)
  %17 = icmp slt i32 %16, %8, !dbg !4098
  br i1 %17, label %11, label %18, !dbg !4099, !llvm.loop !4100

18:                                               ; preds = %11, %7
  %19 = phi i16 [ %9, %7 ], [ %14, %11 ], !dbg !4102
    #dbg_value(i16 %19, !4054, !DIExpression(), !4068)
    #dbg_value(i16 poison, !4064, !DIExpression(), !4096)
  %20 = shl nsw i32 %8, 16, !dbg !4103
  %21 = add i32 %20, 65536, !dbg !4103
  %22 = ashr exact i32 %21, 16, !dbg !4103
  %23 = icmp slt i32 %22, 3, !dbg !4104
  br i1 %23, label %7, label %24, !dbg !4105, !llvm.loop !4106

24:                                               ; preds = %18
    #dbg_value(ptr %0, !106, !DIExpression(), !4108)
    #dbg_value(ptr %1, !107, !DIExpression(), !4108)
    #dbg_value(i16 %19, !108, !DIExpression(), !4108)
  %25 = lshr i16 %19, 8, !dbg !4110
  %26 = trunc nuw i16 %25 to i8, !dbg !4111
  store i8 %26, ptr %1, align 1, !dbg !4112, !tbaa !113
  %27 = trunc i16 %19 to i8, !dbg !4113
  br label %29

28:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4114)
    #dbg_value(ptr %1, !107, !DIExpression(), !4114)
    #dbg_value(i16 -1, !108, !DIExpression(), !4114)
  store i8 -1, ptr %1, align 1, !dbg !4116, !tbaa !113
  br label %29, !dbg !4117

29:                                               ; preds = %28, %24, %6, %5, %4
  %30 = phi i8 [ -1, %28 ], [ %27, %24 ], [ 8, %6 ], [ 9, %5 ], [ 100, %4 ]
  %31 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4118
  store i8 %30, ptr %31, align 1, !dbg !4119, !tbaa !113
  %32 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4120
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4121
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4122
  ret void, !dbg !4117
}

; Function Attrs: nounwind
define hidden void @test_many_locals(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4123 {
    #dbg_value(ptr %0, !4125, !DIExpression(), !4144)
    #dbg_value(ptr %1, !4126, !DIExpression(), !4144)
    #dbg_value(i8 %2, !4127, !DIExpression(), !4144)
    #dbg_value(i16 1, !4128, !DIExpression(), !4144)
    #dbg_value(i16 2, !4129, !DIExpression(), !4144)
    #dbg_value(i16 3, !4130, !DIExpression(), !4144)
    #dbg_value(i16 4, !4131, !DIExpression(), !4144)
    #dbg_value(i16 5, !4132, !DIExpression(), !4144)
    #dbg_value(i16 6, !4133, !DIExpression(), !4144)
    #dbg_value(i16 7, !4134, !DIExpression(), !4144)
    #dbg_value(i16 8, !4135, !DIExpression(), !4144)
    #dbg_value(i16 9, !4136, !DIExpression(), !4144)
    #dbg_value(i16 10, !4137, !DIExpression(), !4144)
    #dbg_value(i16 11, !4138, !DIExpression(), !4144)
    #dbg_value(i16 12, !4139, !DIExpression(), !4144)
    #dbg_value(i16 13, !4140, !DIExpression(), !4144)
    #dbg_value(i16 14, !4141, !DIExpression(), !4144)
    #dbg_value(i16 15, !4142, !DIExpression(), !4144)
    #dbg_value(i16 16, !4143, !DIExpression(), !4144)
  switch i8 %2, label %11 [
    i8 0, label %12
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %10
  ], !dbg !4145

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4146)
    #dbg_value(ptr %1, !107, !DIExpression(), !4146)
    #dbg_value(i16 26, !108, !DIExpression(), !4146)
  br label %12, !dbg !4150

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4151)
    #dbg_value(ptr %1, !107, !DIExpression(), !4151)
    #dbg_value(i16 42, !108, !DIExpression(), !4151)
  br label %12, !dbg !4155

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4156)
    #dbg_value(ptr %1, !107, !DIExpression(), !4156)
    #dbg_value(i16 58, !108, !DIExpression(), !4156)
  br label %12, !dbg !4160

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4161)
    #dbg_value(ptr %1, !107, !DIExpression(), !4161)
    #dbg_value(i16 34, !108, !DIExpression(), !4161)
  br label %12, !dbg !4165

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4166)
    #dbg_value(ptr %1, !107, !DIExpression(), !4166)
    #dbg_value(i16 136, !108, !DIExpression(), !4166)
  br label %12, !dbg !4170

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4171)
    #dbg_value(ptr %1, !107, !DIExpression(), !4171)
    #dbg_value(i16 24, !108, !DIExpression(), !4171)
  br label %12, !dbg !4175

10:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4176)
    #dbg_value(ptr %1, !107, !DIExpression(), !4176)
    #dbg_value(i16 22, !108, !DIExpression(), !4176)
  br label %12, !dbg !4180

11:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4181)
    #dbg_value(ptr %1, !107, !DIExpression(), !4181)
    #dbg_value(i16 -1, !108, !DIExpression(), !4181)
  br label %12, !dbg !4183

12:                                               ; preds = %3, %11, %10, %9, %8, %7, %6, %5, %4
  %13 = phi i8 [ -1, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %14 = phi i8 [ -1, %11 ], [ 22, %10 ], [ 24, %9 ], [ -120, %8 ], [ 34, %7 ], [ 58, %6 ], [ 42, %5 ], [ 26, %4 ], [ 10, %3 ]
  %15 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4184
  store i8 %13, ptr %1, align 1, !dbg !4185, !tbaa !113
  store i8 %14, ptr %15, align 1, !dbg !4186, !tbaa !113
  %16 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4187
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4188
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4189
  ret void, !dbg !4183
}

; Function Attrs: nounwind
define hidden void @test_int_arrays(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4190 {
    #dbg_value(ptr %0, !4192, !DIExpression(), !4199)
    #dbg_value(ptr %1, !4193, !DIExpression(), !4199)
    #dbg_value(i8 %2, !4194, !DIExpression(), !4199)
  switch i8 %2, label %33 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
    i8 5, label %9
    i8 6, label %10
  ], !dbg !4200

4:                                                ; preds = %3
  store i32 100000, ptr @g_ints, align 16, !dbg !4201, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !4204)
    #dbg_value(ptr %1, !107, !DIExpression(), !4204)
    #dbg_value(i16 100, !108, !DIExpression(), !4204)
  store i8 0, ptr %1, align 1, !dbg !4206, !tbaa !113
  br label %34, !dbg !4207

5:                                                ; preds = %3
  store i32 100000, ptr @g_ints, align 16, !dbg !4208, !tbaa !3191
  store i32 200000, ptr getelementptr inbounds (i8, ptr @g_ints, i32 4), align 4, !dbg !4211, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !4212)
    #dbg_value(ptr %1, !107, !DIExpression(), !4212)
    #dbg_value(i16 300, !108, !DIExpression(), !4212)
  store i8 1, ptr %1, align 1, !dbg !4214, !tbaa !113
  br label %34, !dbg !4215

6:                                                ; preds = %3
    #dbg_value(i16 2, !4195, !DIExpression(), !4199)
  store i32 50000, ptr getelementptr inbounds (i8, ptr @g_ints, i32 8), align 8, !dbg !4216, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !4219)
    #dbg_value(ptr %1, !107, !DIExpression(), !4219)
    #dbg_value(i16 50, !108, !DIExpression(), !4219)
  store i8 0, ptr %1, align 1, !dbg !4221, !tbaa !113
  br label %34, !dbg !4222

7:                                                ; preds = %3
  store i32 2147483647, ptr @g_ints, align 16, !dbg !4223, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !4226)
    #dbg_value(ptr %1, !107, !DIExpression(), !4226)
    #dbg_value(i16 1, !108, !DIExpression(), !4226)
  store i8 0, ptr %1, align 1, !dbg !4228, !tbaa !113
  br label %34, !dbg !4229

8:                                                ; preds = %3
  store i32 -2147483648, ptr @g_ints, align 16, !dbg !4230, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !4233)
    #dbg_value(ptr %1, !107, !DIExpression(), !4233)
    #dbg_value(i16 1, !108, !DIExpression(), !4233)
  store i8 0, ptr %1, align 1, !dbg !4235, !tbaa !113
  br label %34, !dbg !4236

9:                                                ; preds = %3
  store i32 -100000, ptr @g_ints, align 16, !dbg !4237, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !4240)
    #dbg_value(ptr %1, !107, !DIExpression(), !4240)
    #dbg_value(i16 -100, !108, !DIExpression(), !4240)
  store i8 -1, ptr %1, align 1, !dbg !4242, !tbaa !113
  br label %34, !dbg !4243

10:                                               ; preds = %3, %10
  %11 = phi i32 [ %16, %10 ], [ 0, %3 ]
  %12 = add nsw i32 %11, 1, !dbg !4244
  %13 = mul nsw i32 %12, 10000, !dbg !4248
  %14 = getelementptr inbounds [4 x i32], ptr @g_ints, i32 0, i32 %11, !dbg !4249
  store i32 %13, ptr %14, align 4, !dbg !4250, !tbaa !3191
    #dbg_value(i16 poison, !4195, !DIExpression(), !4199)
  %15 = shl i32 %12, 16, !dbg !4251
  %16 = ashr exact i32 %15, 16, !dbg !4251
  %17 = icmp slt i32 %16, 4, !dbg !4252
  br i1 %17, label %10, label %18, !dbg !4253, !llvm.loop !4254

18:                                               ; preds = %10, %18
  %19 = phi i32 [ %26, %18 ], [ 0, %10 ]
  %20 = phi i32 [ %23, %18 ], [ 0, %10 ]
    #dbg_value(i32 %20, !4196, !DIExpression(), !4256)
  %21 = getelementptr inbounds [4 x i32], ptr @g_ints, i32 0, i32 %19, !dbg !4257
  %22 = load i32, ptr %21, align 4, !dbg !4257, !tbaa !3191
  %23 = add nsw i32 %22, %20, !dbg !4261
    #dbg_value(i32 %23, !4196, !DIExpression(), !4256)
    #dbg_value(i16 poison, !4195, !DIExpression(), !4199)
  %24 = shl nsw i32 %19, 16, !dbg !4262
  %25 = add i32 %24, 65536, !dbg !4262
  %26 = ashr exact i32 %25, 16, !dbg !4262
  %27 = icmp slt i32 %26, 4, !dbg !4263
  br i1 %27, label %18, label %28, !dbg !4264, !llvm.loop !4265

28:                                               ; preds = %18
  %29 = sdiv i32 %23, 1000, !dbg !4267
    #dbg_value(ptr %0, !106, !DIExpression(), !4268)
    #dbg_value(ptr %1, !107, !DIExpression(), !4268)
    #dbg_value(i32 %29, !108, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !4268)
  %30 = lshr i32 %29, 8, !dbg !4270
  %31 = trunc i32 %30 to i8, !dbg !4270
  store i8 %31, ptr %1, align 1, !dbg !4271, !tbaa !113
  %32 = trunc i32 %29 to i8, !dbg !4272
  br label %34

33:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4273)
    #dbg_value(ptr %1, !107, !DIExpression(), !4273)
    #dbg_value(i16 -1, !108, !DIExpression(), !4273)
  store i8 -1, ptr %1, align 1, !dbg !4275, !tbaa !113
  br label %34, !dbg !4276

34:                                               ; preds = %33, %28, %9, %8, %7, %6, %5, %4
  %35 = phi i8 [ -1, %33 ], [ %32, %28 ], [ -100, %9 ], [ 1, %8 ], [ 1, %7 ], [ 50, %6 ], [ 44, %5 ], [ 100, %4 ]
  %36 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4277
  store i8 %35, ptr %36, align 1, !dbg !4278, !tbaa !113
  %37 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4279
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4280
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4281
  ret void, !dbg !4276
}

; Function Attrs: nounwind
define hidden void @test_phi_patterns(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4282 {
    #dbg_value(ptr %0, !4284, !DIExpression(), !4304)
    #dbg_value(ptr %1, !4285, !DIExpression(), !4304)
    #dbg_value(i8 %2, !4286, !DIExpression(), !4304)
  switch i8 %2, label %24 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %22
    i8 5, label %23
  ], !dbg !4305

4:                                                ; preds = %3
    #dbg_value(i16 poison, !4290, !DIExpression(), !4304)
    #dbg_value(i16 poison, !4289, !DIExpression(), !4304)
    #dbg_value(ptr %0, !106, !DIExpression(), !4306)
    #dbg_value(ptr %1, !107, !DIExpression(), !4306)
    #dbg_value(i16 15, !108, !DIExpression(), !4306)
  store i8 0, ptr %1, align 1, !dbg !4310, !tbaa !113
  br label %25, !dbg !4311

5:                                                ; preds = %3
    #dbg_value(i16 undef, !4287, !DIExpression(), !4304)
    #dbg_value(i16 undef, !4288, !DIExpression(), !4304)
    #dbg_value(i16 poison, !4289, !DIExpression(), !4304)
    #dbg_value(ptr %0, !106, !DIExpression(), !4312)
    #dbg_value(ptr %1, !107, !DIExpression(), !4312)
    #dbg_value(i16 55, !108, !DIExpression(), !4312)
  store i8 0, ptr %1, align 1, !dbg !4314, !tbaa !113
  br label %25, !dbg !4315

6:                                                ; preds = %3
    #dbg_value(i16 poison, !4290, !DIExpression(), !4304)
    #dbg_value(i16 poison, !4289, !DIExpression(), !4304)
    #dbg_value(ptr %0, !106, !DIExpression(), !4316)
    #dbg_value(ptr %1, !107, !DIExpression(), !4316)
    #dbg_value(i16 20, !108, !DIExpression(), !4316)
  store i8 0, ptr %1, align 1, !dbg !4320, !tbaa !113
  br label %25, !dbg !4321

7:                                                ; preds = %3
    #dbg_value(i16 0, !4297, !DIExpression(), !4322)
  store i16 5, ptr @g_shorts, align 16, !dbg !4323, !tbaa !3184
  store i16 12, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 2), align 2, !dbg !4324, !tbaa !3184
  store i16 3, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 4), align 4, !dbg !4325, !tbaa !3184
  store i16 9, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 6), align 2, !dbg !4326, !tbaa !3184
    #dbg_value(i16 0, !4289, !DIExpression(), !4304)
    #dbg_value(i16 0, !4297, !DIExpression(), !4322)
    #dbg_value(i16 poison, !4289, !DIExpression(), !4304)
  br label %8, !dbg !4327

8:                                                ; preds = %7, %8
  %9 = phi i32 [ 0, %7 ], [ %16, %8 ]
  %10 = phi i16 [ 0, %7 ], [ %13, %8 ]
    #dbg_value(i16 %10, !4297, !DIExpression(), !4322)
  %11 = getelementptr inbounds [8 x i16], ptr @g_shorts, i32 0, i32 %9, !dbg !4329
  %12 = load i16, ptr %11, align 2, !dbg !4329, !tbaa !3184
  %13 = tail call i16 @llvm.smax.i16(i16 %12, i16 %10), !dbg !4333
    #dbg_value(i16 %13, !4297, !DIExpression(), !4322)
    #dbg_value(i16 poison, !4289, !DIExpression(), !4304)
  %14 = shl nsw i32 %9, 16, !dbg !4334
  %15 = add i32 %14, 65536, !dbg !4334
  %16 = ashr exact i32 %15, 16, !dbg !4334
  %17 = icmp slt i32 %16, 4, !dbg !4335
  br i1 %17, label %8, label %18, !dbg !4327, !llvm.loop !4336

18:                                               ; preds = %8
    #dbg_value(ptr %0, !106, !DIExpression(), !4338)
    #dbg_value(ptr %1, !107, !DIExpression(), !4338)
    #dbg_value(i16 %13, !108, !DIExpression(), !4338)
  %19 = lshr i16 %13, 8, !dbg !4340
  %20 = trunc nuw nsw i16 %19 to i8, !dbg !4341
  store i8 %20, ptr %1, align 1, !dbg !4342, !tbaa !113
  %21 = trunc i16 %13 to i8, !dbg !4343
  br label %25

22:                                               ; preds = %3
    #dbg_value(i16 poison, !4290, !DIExpression(), !4304)
    #dbg_value(i16 poison, !4289, !DIExpression(), !4304)
    #dbg_value(ptr %0, !106, !DIExpression(), !4344)
    #dbg_value(ptr %1, !107, !DIExpression(), !4344)
    #dbg_value(i16 10, !108, !DIExpression(), !4344)
  store i8 0, ptr %1, align 1, !dbg !4348, !tbaa !113
  br label %25, !dbg !4349

23:                                               ; preds = %3
    #dbg_value(i16 poison, !4303, !DIExpression(), !4350)
    #dbg_value(i16 poison, !4300, !DIExpression(), !4350)
    #dbg_value(i16 poison, !4289, !DIExpression(), !4304)
    #dbg_value(ptr %0, !106, !DIExpression(), !4351)
    #dbg_value(ptr %1, !107, !DIExpression(), !4351)
    #dbg_value(i16 30, !108, !DIExpression(), !4351)
  store i8 0, ptr %1, align 1, !dbg !4353, !tbaa !113
  br label %25

24:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4354)
    #dbg_value(ptr %1, !107, !DIExpression(), !4354)
    #dbg_value(i16 -1, !108, !DIExpression(), !4354)
  store i8 -1, ptr %1, align 1, !dbg !4356, !tbaa !113
  br label %25, !dbg !4357

25:                                               ; preds = %24, %23, %22, %18, %6, %5, %4
  %26 = phi i8 [ -1, %24 ], [ 30, %23 ], [ 10, %22 ], [ %21, %18 ], [ 20, %6 ], [ 55, %5 ], [ 15, %4 ]
  %27 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4358
  store i8 %26, ptr %27, align 1, !dbg !4359, !tbaa !113
  %28 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4360
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4361
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4362
  ret void, !dbg !4357
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define hidden i32 @FixedMul(i32 noundef %0, i32 noundef %1) local_unnamed_addr #2 !dbg !4363 {
    #dbg_value(i32 %0, !4365, !DIExpression(), !4379)
    #dbg_value(i32 %1, !4366, !DIExpression(), !4379)
    #dbg_value(i32 %0, !4367, !DIExpression(DW_OP_constu, 16, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !4379)
    #dbg_value(i32 %1, !4368, !DIExpression(DW_OP_constu, 16, DW_OP_shr, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !4379)
    #dbg_value(i32 %0, !4369, !DIExpression(DW_OP_constu, 65535, DW_OP_and, DW_OP_stack_value), !4379)
  %3 = and i32 %1, 65535, !dbg !4380
    #dbg_value(i32 %1, !4370, !DIExpression(DW_OP_constu, 65535, DW_OP_and, DW_OP_stack_value), !4379)
  %4 = ashr i32 %0, 16, !dbg !4381
  %5 = ashr i32 %1, 16, !dbg !4382
    #dbg_value(i32 %0, !4371, !DIExpression(DW_OP_constu, 18446744073709486080, DW_OP_and, DW_OP_stack_value), !4379)
  %6 = mul nsw i32 %3, %4, !dbg !4383
    #dbg_value(!DIArgList(i32 %0, i32 %6), !4371, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 18446744073709486080, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_plus, DW_OP_stack_value), !4379)
    #dbg_value(i32 poison, !4371, !DIExpression(), !4379)
  %7 = lshr i32 %0, 8, !dbg !4384
  %8 = and i32 %7, 255, !dbg !4385
    #dbg_value(i32 %8, !4372, !DIExpression(), !4379)
  %9 = and i32 %0, 255, !dbg !4386
    #dbg_value(i32 %9, !4373, !DIExpression(), !4379)
  %10 = lshr i32 %1, 8, !dbg !4387
  %11 = and i32 %10, 255, !dbg !4388
    #dbg_value(i32 %11, !4374, !DIExpression(), !4379)
  %12 = and i32 %1, 255, !dbg !4389
    #dbg_value(i32 %12, !4375, !DIExpression(), !4379)
  %13 = mul nuw nsw i32 %8, %12, !dbg !4390
  %14 = mul nuw nsw i32 %11, %9, !dbg !4391
  %15 = add nuw nsw i32 %14, %13, !dbg !4392
    #dbg_value(i32 %15, !4376, !DIExpression(), !4379)
  %16 = mul nuw nsw i32 %12, %9, !dbg !4393
    #dbg_value(i32 %16, !4377, !DIExpression(), !4379)
  %17 = and i32 %15, 255, !dbg !4394
  %18 = lshr i32 %16, 8, !dbg !4395
  %19 = add nuw nsw i32 %17, %18, !dbg !4396
  %20 = icmp ugt i32 %19, 255, !dbg !4397
  %21 = zext i1 %20 to i32, !dbg !4398
    #dbg_value(i32 %21, !4378, !DIExpression(), !4379)
  %22 = mul nuw nsw i32 %11, %8, !dbg !4399
  %23 = lshr i32 %15, 8, !dbg !4400
  %24 = mul i32 %5, %0
  %25 = add nsw i32 %22, %6, !dbg !4401
  %26 = add i32 %25, %24, !dbg !4402
  %27 = add i32 %26, %23, !dbg !4403
  %28 = add i32 %27, %21, !dbg !4404
    #dbg_value(i32 %28, !4371, !DIExpression(), !4379)
  ret i32 %28, !dbg !4405
}

; Function Attrs: nounwind
define hidden void @test_doom_math(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4406 {
    #dbg_value(ptr %0, !4408, !DIExpression(), !4414)
    #dbg_value(ptr %1, !4409, !DIExpression(), !4414)
    #dbg_value(i8 %2, !4410, !DIExpression(), !4414)
  switch i8 %2, label %8 [
    i8 0, label %9
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
  ], !dbg !4415

4:                                                ; preds = %3
    #dbg_value(i32 131072, !4411, !DIExpression(), !4414)
    #dbg_value(i32 131072, !4412, !DIExpression(), !4414)
    #dbg_value(i32 262144, !4413, !DIExpression(), !4414)
    #dbg_value(ptr %0, !106, !DIExpression(), !4416)
    #dbg_value(ptr %1, !107, !DIExpression(), !4416)
    #dbg_value(i16 4, !108, !DIExpression(), !4416)
  br label %9, !dbg !4420

5:                                                ; preds = %3
    #dbg_value(i32 98304, !4411, !DIExpression(), !4414)
    #dbg_value(i32 131072, !4412, !DIExpression(), !4414)
    #dbg_value(i32 196608, !4413, !DIExpression(), !4414)
    #dbg_value(ptr %0, !106, !DIExpression(), !4421)
    #dbg_value(ptr %1, !107, !DIExpression(), !4421)
    #dbg_value(i16 3, !108, !DIExpression(), !4421)
  br label %9, !dbg !4425

6:                                                ; preds = %3
    #dbg_value(i32 32768, !4411, !DIExpression(), !4414)
    #dbg_value(i32 32768, !4412, !DIExpression(), !4414)
    #dbg_value(i32 16384, !4413, !DIExpression(), !4414)
    #dbg_value(ptr %0, !106, !DIExpression(), !4426)
    #dbg_value(ptr %1, !107, !DIExpression(), !4426)
    #dbg_value(i16 0, !108, !DIExpression(), !4426)
  br label %9, !dbg !4430

7:                                                ; preds = %3
    #dbg_value(i32 98304, !4411, !DIExpression(), !4414)
    #dbg_value(i32 98304, !4412, !DIExpression(), !4414)
    #dbg_value(i32 147456, !4413, !DIExpression(), !4414)
    #dbg_value(ptr %0, !106, !DIExpression(), !4431)
    #dbg_value(ptr %1, !107, !DIExpression(), !4431)
    #dbg_value(i16 2, !108, !DIExpression(), !4431)
  br label %9, !dbg !4435

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4436)
    #dbg_value(ptr %1, !107, !DIExpression(), !4436)
    #dbg_value(i16 -1, !108, !DIExpression(), !4436)
  br label %9, !dbg !4438

9:                                                ; preds = %3, %8, %7, %6, %5, %4
  %10 = phi i8 [ -1, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %11 = phi i8 [ -1, %8 ], [ 2, %7 ], [ 0, %6 ], [ 3, %5 ], [ 4, %4 ], [ 1, %3 ]
  %12 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4439
  store i8 %10, ptr %1, align 1, !dbg !4440, !tbaa !113
  store i8 %11, ptr %12, align 1, !dbg !4441, !tbaa !113
  %13 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4442
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4443
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4444
  ret void, !dbg !4438
}

; Function Attrs: nounwind
define hidden void @test_memset(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4445 {
    #dbg_value(ptr %0, !4447, !DIExpression(), !4454)
    #dbg_value(ptr %1, !4448, !DIExpression(), !4454)
    #dbg_value(i8 %2, !4449, !DIExpression(), !4454)
  switch i8 %2, label %51 [
    i8 0, label %4
    i8 1, label %8
    i8 2, label %23
    i8 3, label %28
    i8 4, label %33
    i8 5, label %38
    i8 6, label %43
    i8 7, label %47
  ], !dbg !4455

4:                                                ; preds = %3
  %5 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 8, i8 noundef signext 42) #11, !dbg !4456
  %6 = load i8, ptr @shared_fb, align 16, !dbg !4459, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4460)
    #dbg_value(ptr %1, !107, !DIExpression(), !4460)
    #dbg_value(i8 %6, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4460)
  %7 = ashr i8 %6, 7, !dbg !4462
  store i8 %7, ptr %1, align 1, !dbg !4463, !tbaa !113
  br label %52, !dbg !4464

8:                                                ; preds = %3
  %9 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 8, i8 noundef signext 99) #11, !dbg !4465
    #dbg_value(i16 1, !4451, !DIExpression(), !4466)
    #dbg_value(i16 0, !4450, !DIExpression(), !4454)
    #dbg_value(i16 poison, !4450, !DIExpression(), !4454)
  br label %10, !dbg !4467

10:                                               ; preds = %8, %10
  %11 = phi i32 [ 0, %8 ], [ %19, %10 ]
  %12 = phi i16 [ 1, %8 ], [ %16, %10 ]
    #dbg_value(i16 %12, !4451, !DIExpression(), !4466)
  %13 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %11, !dbg !4469
  %14 = load i8, ptr %13, align 1, !dbg !4469, !tbaa !113
  %15 = icmp eq i8 %14, 99, !dbg !4473
  %16 = select i1 %15, i16 %12, i16 0, !dbg !4474
    #dbg_value(i16 %16, !4451, !DIExpression(), !4466)
    #dbg_value(i16 poison, !4450, !DIExpression(), !4454)
  %17 = shl nsw i32 %11, 16, !dbg !4475
  %18 = add i32 %17, 65536, !dbg !4475
  %19 = ashr exact i32 %18, 16, !dbg !4475
  %20 = icmp slt i32 %19, 8, !dbg !4476
  br i1 %20, label %10, label %21, !dbg !4467, !llvm.loop !4477

21:                                               ; preds = %10
    #dbg_value(ptr %0, !106, !DIExpression(), !4479)
    #dbg_value(ptr %1, !107, !DIExpression(), !4479)
    #dbg_value(i16 %16, !108, !DIExpression(), !4479)
  store i8 0, ptr %1, align 1, !dbg !4481, !tbaa !113
  %22 = trunc nuw nsw i16 %16 to i8, !dbg !4482
  br label %52

23:                                               ; preds = %3
  %24 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 8, i8 noundef signext 0) #11, !dbg !4483
  %25 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 4, i8 noundef signext 55) #11, !dbg !4486
  %26 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 3), align 1, !dbg !4487, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4488)
    #dbg_value(ptr %1, !107, !DIExpression(), !4488)
    #dbg_value(i8 %26, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4488)
  %27 = ashr i8 %26, 7, !dbg !4490
  store i8 %27, ptr %1, align 1, !dbg !4491, !tbaa !113
  br label %52, !dbg !4492

28:                                               ; preds = %3
  %29 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 8, i8 noundef signext 0) #11, !dbg !4493
  %30 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 4, i8 noundef signext 55) #11, !dbg !4496
  %31 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 4), align 4, !dbg !4497, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4498)
    #dbg_value(ptr %1, !107, !DIExpression(), !4498)
    #dbg_value(i8 %31, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4498)
  %32 = ashr i8 %31, 7, !dbg !4500
  store i8 %32, ptr %1, align 1, !dbg !4501, !tbaa !113
  br label %52, !dbg !4502

33:                                               ; preds = %3
  %34 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 8, i8 noundef signext 0) #11, !dbg !4503
  %35 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 2, i16 noundef signext 4, i8 noundef signext 77) #11, !dbg !4506
  %36 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !4507, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4508)
    #dbg_value(ptr %1, !107, !DIExpression(), !4508)
    #dbg_value(i8 %36, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4508)
  %37 = ashr i8 %36, 7, !dbg !4510
  store i8 %37, ptr %1, align 1, !dbg !4511, !tbaa !113
  br label %52, !dbg !4512

38:                                               ; preds = %3
  %39 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 8, i8 noundef signext 0) #11, !dbg !4513
  %40 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 2, i16 noundef signext 4, i8 noundef signext 77) #11, !dbg !4516
  %41 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !4517, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4518)
    #dbg_value(ptr %1, !107, !DIExpression(), !4518)
    #dbg_value(i8 %41, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4518)
  %42 = ashr i8 %41, 7, !dbg !4520
  store i8 %42, ptr %1, align 1, !dbg !4521, !tbaa !113
  br label %52, !dbg !4522

43:                                               ; preds = %3
  %44 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 8, i8 noundef signext -1) #11, !dbg !4523
  %45 = load i8, ptr @shared_fb, align 16, !dbg !4526, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4527)
    #dbg_value(ptr %1, !107, !DIExpression(), !4527)
    #dbg_value(i8 %45, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4527)
  %46 = ashr i8 %45, 7, !dbg !4529
  store i8 %46, ptr %1, align 1, !dbg !4530, !tbaa !113
  br label %52, !dbg !4531

47:                                               ; preds = %3
  %48 = tail call signext i16 @jc_Util_arrayFillNonAtomic(ptr noundef nonnull @shared_fb, i16 noundef signext 0, i16 noundef signext 8, i8 noundef signext 0) #11, !dbg !4532
  %49 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 7), align 1, !dbg !4535, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4536)
    #dbg_value(ptr %1, !107, !DIExpression(), !4536)
    #dbg_value(i8 %49, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4536)
  %50 = ashr i8 %49, 7, !dbg !4538
  store i8 %50, ptr %1, align 1, !dbg !4539, !tbaa !113
  br label %52, !dbg !4540

51:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4541)
    #dbg_value(ptr %1, !107, !DIExpression(), !4541)
    #dbg_value(i16 -1, !108, !DIExpression(), !4541)
  store i8 -1, ptr %1, align 1, !dbg !4543, !tbaa !113
  br label %52, !dbg !4544

52:                                               ; preds = %51, %47, %43, %38, %33, %28, %23, %21, %4
  %53 = phi i8 [ -1, %51 ], [ %49, %47 ], [ %45, %43 ], [ %41, %38 ], [ %36, %33 ], [ %31, %28 ], [ %26, %23 ], [ %22, %21 ], [ %6, %4 ]
  %54 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4545
  store i8 %53, ptr %54, align 1, !dbg !4546, !tbaa !113
  %55 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4547
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4548
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4549
  ret void, !dbg !4544
}

; Function Attrs: nounwind
define hidden void @test_shift_combinations(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4550 {
    #dbg_value(ptr %0, !4552, !DIExpression(), !4561)
    #dbg_value(ptr %1, !4553, !DIExpression(), !4561)
    #dbg_value(i8 %2, !4554, !DIExpression(), !4561)
  switch i8 %2, label %18 [
    i8 0, label %19
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
    i8 11, label %14
    i8 12, label %15
    i8 13, label %16
    i8 14, label %17
  ], !dbg !4562

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4563)
    #dbg_value(ptr %1, !107, !DIExpression(), !4563)
    #dbg_value(i16 128, !108, !DIExpression(), !4563)
  br label %19, !dbg !4567

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4568)
    #dbg_value(ptr %1, !107, !DIExpression(), !4568)
    #dbg_value(i16 16, !108, !DIExpression(), !4568)
  br label %19, !dbg !4572

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4573)
    #dbg_value(ptr %1, !107, !DIExpression(), !4573)
    #dbg_value(i16 128, !108, !DIExpression(), !4573)
  br label %19, !dbg !4577

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4578)
    #dbg_value(ptr %1, !107, !DIExpression(), !4578)
    #dbg_value(i16 1, !108, !DIExpression(), !4578)
  br label %19, !dbg !4582

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4583)
    #dbg_value(ptr %1, !107, !DIExpression(), !4583)
    #dbg_value(i16 1, !108, !DIExpression(), !4583)
  br label %19, !dbg !4587

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4588)
    #dbg_value(ptr %1, !107, !DIExpression(), !4588)
    #dbg_value(i16 -32768, !108, !DIExpression(), !4588)
  br label %19, !dbg !4592

10:                                               ; preds = %3
    #dbg_value(i8 -128, !4558, !DIExpression(), !4593)
    #dbg_value(ptr %0, !106, !DIExpression(), !4594)
    #dbg_value(ptr %1, !107, !DIExpression(), !4594)
    #dbg_value(i16 -16, !108, !DIExpression(), !4594)
  br label %19

11:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4596)
    #dbg_value(ptr %1, !107, !DIExpression(), !4596)
    #dbg_value(i16 240, !108, !DIExpression(), !4596)
  br label %19, !dbg !4600

12:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4601)
    #dbg_value(ptr %1, !107, !DIExpression(), !4601)
    #dbg_value(i16 255, !108, !DIExpression(), !4601)
  br label %19, !dbg !4605

13:                                               ; preds = %3
    #dbg_value(i16 5, !4555, !DIExpression(), !4561)
    #dbg_value(i16 16, !4556, !DIExpression(), !4561)
    #dbg_value(ptr %0, !106, !DIExpression(), !4606)
    #dbg_value(ptr %1, !107, !DIExpression(), !4606)
    #dbg_value(i16 22, !108, !DIExpression(), !4606)
  br label %19, !dbg !4610

14:                                               ; preds = %3
    #dbg_value(i16 0, !4555, !DIExpression(), !4561)
    #dbg_value(i16 0, !4556, !DIExpression(), !4561)
    #dbg_value(ptr %0, !106, !DIExpression(), !4611)
    #dbg_value(ptr %1, !107, !DIExpression(), !4611)
    #dbg_value(i16 0, !108, !DIExpression(), !4611)
  br label %19, !dbg !4615

15:                                               ; preds = %3
    #dbg_value(i16 19, !4555, !DIExpression(), !4561)
    #dbg_value(i16 31, !4556, !DIExpression(), !4561)
    #dbg_value(ptr %0, !106, !DIExpression(), !4616)
    #dbg_value(ptr %1, !107, !DIExpression(), !4616)
    #dbg_value(i16 79, !108, !DIExpression(), !4616)
  br label %19, !dbg !4620

16:                                               ; preds = %3
    #dbg_value(i16 4660, !4557, !DIExpression(), !4561)
    #dbg_value(ptr %0, !106, !DIExpression(), !4621)
    #dbg_value(ptr %1, !107, !DIExpression(), !4621)
    #dbg_value(i16 18, !108, !DIExpression(), !4621)
  br label %19, !dbg !4625

17:                                               ; preds = %3
    #dbg_value(i16 4660, !4557, !DIExpression(), !4561)
    #dbg_value(ptr %0, !106, !DIExpression(), !4626)
    #dbg_value(ptr %1, !107, !DIExpression(), !4626)
    #dbg_value(i16 18, !108, !DIExpression(), !4626)
  br label %19, !dbg !4630

18:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4631)
    #dbg_value(ptr %1, !107, !DIExpression(), !4631)
    #dbg_value(i16 -1, !108, !DIExpression(), !4631)
  br label %19, !dbg !4633

19:                                               ; preds = %3, %18, %17, %16, %15, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %20 = phi i8 [ -1, %18 ], [ 0, %17 ], [ 0, %16 ], [ 0, %15 ], [ 0, %14 ], [ 0, %13 ], [ 0, %12 ], [ 0, %11 ], [ -1, %10 ], [ -128, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %21 = phi i8 [ -1, %18 ], [ 18, %17 ], [ 18, %16 ], [ 79, %15 ], [ 0, %14 ], [ 22, %13 ], [ -1, %12 ], [ -16, %11 ], [ -16, %10 ], [ 0, %9 ], [ 1, %8 ], [ 1, %7 ], [ -128, %6 ], [ 16, %5 ], [ -128, %4 ], [ 43, %3 ]
  %22 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4634
  store i8 %20, ptr %1, align 1, !dbg !4635, !tbaa !113
  store i8 %21, ptr %22, align 1, !dbg !4636, !tbaa !113
  %23 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4637
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4638
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4639
  ret void, !dbg !4633
}

; Function Attrs: nounwind
define hidden void @test_pixel_masks(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4640 {
    #dbg_value(ptr %0, !4642, !DIExpression(), !4647)
    #dbg_value(ptr %1, !4643, !DIExpression(), !4647)
    #dbg_value(i8 %2, !4644, !DIExpression(), !4647)
  switch i8 %2, label %12 [
    i8 0, label %13
    i8 1, label %4
    i8 2, label %5
    i8 3, label %13
    i8 4, label %6
    i8 5, label %7
    i8 6, label %8
    i8 7, label %13
    i8 8, label %9
    i8 9, label %10
    i8 10, label %11
    i8 11, label %13
  ], !dbg !4648

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4649)
    #dbg_value(ptr %1, !107, !DIExpression(), !4649)
    #dbg_value(i16 64, !108, !DIExpression(), !4649)
  br label %13, !dbg !4653

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4654)
    #dbg_value(ptr %1, !107, !DIExpression(), !4654)
    #dbg_value(i16 1, !108, !DIExpression(), !4654)
  br label %13, !dbg !4658

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4659)
    #dbg_value(ptr %1, !107, !DIExpression(), !4659)
    #dbg_value(i16 1, !108, !DIExpression(), !4659)
  br label %13, !dbg !4663

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4664)
    #dbg_value(ptr %1, !107, !DIExpression(), !4664)
    #dbg_value(i16 239, !108, !DIExpression(), !4664)
  br label %13, !dbg !4668

8:                                                ; preds = %3
    #dbg_value(i16 0, !4645, !DIExpression(), !4647)
    #dbg_value(i16 7, !4646, !DIExpression(), !4647)
    #dbg_value(ptr %0, !106, !DIExpression(), !4669)
    #dbg_value(ptr %1, !107, !DIExpression(), !4669)
    #dbg_value(i16 129, !108, !DIExpression(), !4669)
  br label %13, !dbg !4673

9:                                                ; preds = %3
    #dbg_value(i16 7, !4645, !DIExpression(), !4647)
    #dbg_value(ptr %0, !106, !DIExpression(), !4674)
    #dbg_value(ptr %1, !107, !DIExpression(), !4674)
    #dbg_value(i16 1, !108, !DIExpression(), !4674)
  br label %13, !dbg !4678

10:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4679)
    #dbg_value(ptr %1, !107, !DIExpression(), !4679)
    #dbg_value(i16 0, !108, !DIExpression(), !4679)
  br label %13, !dbg !4683

11:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4684)
    #dbg_value(ptr %1, !107, !DIExpression(), !4684)
    #dbg_value(i16 255, !108, !DIExpression(), !4684)
  br label %13, !dbg !4688

12:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4689)
    #dbg_value(ptr %1, !107, !DIExpression(), !4689)
    #dbg_value(i16 -1, !108, !DIExpression(), !4689)
  br label %13, !dbg !4691

13:                                               ; preds = %3, %3, %3, %3, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %14 = phi i8 [ -1, %12 ], [ 0, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %15 = phi i8 [ -1, %12 ], [ -1, %11 ], [ 0, %10 ], [ 1, %9 ], [ -127, %8 ], [ -17, %7 ], [ 1, %6 ], [ 1, %5 ], [ 64, %4 ], [ -128, %3 ], [ -128, %3 ], [ -128, %3 ], [ -128, %3 ]
  %16 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4692
  store i8 %14, ptr %1, align 1, !dbg !4693, !tbaa !113
  store i8 %15, ptr %16, align 1, !dbg !4694, !tbaa !113
  %17 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4695
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4696
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4697
  ret void, !dbg !4691
}

; Function Attrs: nounwind
define hidden void @test_fixed_point(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4698 {
    #dbg_value(ptr %0, !4700, !DIExpression(), !4705)
    #dbg_value(ptr %1, !4701, !DIExpression(), !4705)
    #dbg_value(i8 %2, !4702, !DIExpression(), !4705)
  switch i8 %2, label %13 [
    i8 0, label %14
    i8 1, label %14
    i8 2, label %14
    i8 3, label %4
    i8 4, label %5
    i8 5, label %6
    i8 6, label %7
    i8 7, label %8
    i8 8, label %9
    i8 9, label %10
    i8 10, label %11
    i8 11, label %12
  ], !dbg !4706

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4707)
    #dbg_value(ptr %1, !107, !DIExpression(), !4707)
    #dbg_value(i16 2, !108, !DIExpression(), !4707)
  br label %14, !dbg !4711

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4712)
    #dbg_value(ptr %1, !107, !DIExpression(), !4712)
    #dbg_value(i16 2, !108, !DIExpression(), !4712)
  br label %14, !dbg !4716

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4717)
    #dbg_value(ptr %1, !107, !DIExpression(), !4717)
    #dbg_value(i16 -1, !108, !DIExpression(), !4717)
  br label %14, !dbg !4721

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4722)
    #dbg_value(ptr %1, !107, !DIExpression(), !4722)
    #dbg_value(i16 255, !108, !DIExpression(), !4722)
  br label %14, !dbg !4726

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4727)
    #dbg_value(ptr %1, !107, !DIExpression(), !4727)
    #dbg_value(i16 10, !108, !DIExpression(), !4727)
  br label %14, !dbg !4731

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4732)
    #dbg_value(ptr %1, !107, !DIExpression(), !4732)
    #dbg_value(i16 1000, !108, !DIExpression(), !4732)
  br label %14, !dbg !4736

10:                                               ; preds = %3
    #dbg_value(i16 512, !4703, !DIExpression(), !4705)
    #dbg_value(i16 256, !4704, !DIExpression(), !4705)
    #dbg_value(ptr %0, !106, !DIExpression(), !4737)
    #dbg_value(ptr %1, !107, !DIExpression(), !4737)
    #dbg_value(i16 3, !108, !DIExpression(), !4737)
  br label %14, !dbg !4741

11:                                               ; preds = %3
    #dbg_value(i16 512, !4703, !DIExpression(), !4705)
    #dbg_value(i16 256, !4704, !DIExpression(), !4705)
    #dbg_value(ptr %0, !106, !DIExpression(), !4742)
    #dbg_value(ptr %1, !107, !DIExpression(), !4742)
    #dbg_value(i16 3, !108, !DIExpression(), !4742)
  br label %14, !dbg !4746

12:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4747)
    #dbg_value(ptr %1, !107, !DIExpression(), !4747)
    #dbg_value(i16 127, !108, !DIExpression(), !4747)
  br label %14, !dbg !4751

13:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4752)
    #dbg_value(ptr %1, !107, !DIExpression(), !4752)
    #dbg_value(i16 -1, !108, !DIExpression(), !4752)
  br label %14, !dbg !4754

14:                                               ; preds = %3, %3, %3, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %15 = phi i8 [ -1, %13 ], [ 0, %12 ], [ 0, %11 ], [ 0, %10 ], [ 3, %9 ], [ 0, %8 ], [ 0, %7 ], [ -1, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %16 = phi i8 [ -1, %13 ], [ 127, %12 ], [ 3, %11 ], [ 3, %10 ], [ -24, %9 ], [ 10, %8 ], [ -1, %7 ], [ -1, %6 ], [ 2, %5 ], [ 2, %4 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ]
  %17 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4755
  store i8 %15, ptr %1, align 1, !dbg !4756, !tbaa !113
  store i8 %16, ptr %17, align 1, !dbg !4757, !tbaa !113
  %18 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4758
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4759
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4760
  ret void, !dbg !4754
}

; Function Attrs: nounwind
define hidden void @test_byte_array_index(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4761 {
    #dbg_value(ptr %0, !4763, !DIExpression(), !4773)
    #dbg_value(ptr %1, !4764, !DIExpression(), !4773)
    #dbg_value(i8 %2, !4765, !DIExpression(), !4773)
  switch i8 %2, label %13 [
    i8 0, label %14
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %10
    i8 8, label %11
    i8 9, label %12
  ], !dbg !4774

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4775)
    #dbg_value(ptr %1, !107, !DIExpression(), !4775)
    #dbg_value(i16 3, !108, !DIExpression(), !4775)
  br label %14, !dbg !4779

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4780)
    #dbg_value(ptr %1, !107, !DIExpression(), !4780)
    #dbg_value(i16 76, !108, !DIExpression(), !4780)
  br label %14, !dbg !4784

6:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4785)
    #dbg_value(ptr %1, !107, !DIExpression(), !4785)
    #dbg_value(i16 79, !108, !DIExpression(), !4785)
  br label %14, !dbg !4789

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4790)
    #dbg_value(ptr %1, !107, !DIExpression(), !4790)
    #dbg_value(i16 42, !108, !DIExpression(), !4790)
  br label %14, !dbg !4794

8:                                                ; preds = %3
    #dbg_value(i16 10, !4766, !DIExpression(), !4773)
    #dbg_value(i16 24, !4767, !DIExpression(), !4773)
    #dbg_value(ptr %0, !106, !DIExpression(), !4795)
    #dbg_value(ptr %1, !107, !DIExpression(), !4795)
    #dbg_value(i16 43, !108, !DIExpression(), !4795)
  br label %14, !dbg !4799

9:                                                ; preds = %3
    #dbg_value(i16 1, !4766, !DIExpression(), !4773)
    #dbg_value(i16 8, !4767, !DIExpression(), !4773)
  store i8 99, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 5), align 1, !dbg !4800, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4803)
    #dbg_value(ptr %1, !107, !DIExpression(), !4803)
    #dbg_value(i16 99, !108, !DIExpression(), !4803)
  br label %14, !dbg !4805

10:                                               ; preds = %3
  store i8 15, ptr @shared_fb, align 16, !dbg !4806, !tbaa !113
  store i8 -16, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 7), align 1, !dbg !4809, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4810)
    #dbg_value(ptr %1, !107, !DIExpression(), !4810)
    #dbg_value(i16 255, !108, !DIExpression(), !4810)
  br label %14, !dbg !4812

11:                                               ; preds = %3
    #dbg_value(i16 5, !4766, !DIExpression(), !4773)
    #dbg_value(i16 8, !4767, !DIExpression(), !4773)
    #dbg_value(i16 2, !4770, !DIExpression(), !4813)
    #dbg_value(ptr %0, !106, !DIExpression(), !4814)
    #dbg_value(ptr %1, !107, !DIExpression(), !4814)
    #dbg_value(i16 29, !108, !DIExpression(), !4814)
  br label %14

12:                                               ; preds = %3
    #dbg_value(i16 10, !4768, !DIExpression(), !4773)
    #dbg_value(i16 5, !4769, !DIExpression(), !4773)
    #dbg_value(ptr %0, !106, !DIExpression(), !4816)
    #dbg_value(ptr %1, !107, !DIExpression(), !4816)
    #dbg_value(i16 7, !108, !DIExpression(), !4816)
  br label %14, !dbg !4820

13:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !4821)
    #dbg_value(ptr %1, !107, !DIExpression(), !4821)
    #dbg_value(i16 -1, !108, !DIExpression(), !4821)
  br label %14, !dbg !4823

14:                                               ; preds = %3, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %15 = phi i8 [ -1, %13 ], [ 0, %12 ], [ 0, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %16 = phi i8 [ -1, %13 ], [ 7, %12 ], [ 29, %11 ], [ -1, %10 ], [ 99, %9 ], [ 43, %8 ], [ 42, %7 ], [ 79, %6 ], [ 76, %5 ], [ 3, %4 ], [ %2, %3 ]
  store i8 %15, ptr %1, align 1, !dbg !4824, !tbaa !113
  %17 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4825
  store i8 %16, ptr %17, align 1, !dbg !4826, !tbaa !113
  %18 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4827
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4828
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4829
  ret void, !dbg !4823
}

; Function Attrs: nounwind
define hidden void @test_bitwise_rmw(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4830 {
    #dbg_value(ptr %0, !4832, !DIExpression(), !4843)
    #dbg_value(ptr %1, !4833, !DIExpression(), !4843)
    #dbg_value(i8 %2, !4834, !DIExpression(), !4843)
  switch i8 %2, label %19 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
    i8 5, label %9
    i8 6, label %10
    i8 7, label %11
    i8 8, label %12
    i8 9, label %13
    i8 10, label %14
    i8 11, label %15
    i8 12, label %16
    i8 13, label %17
    i8 14, label %18
  ], !dbg !4844

4:                                                ; preds = %3
  store i8 -128, ptr @shared_fb, align 16, !dbg !4845, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4848)
    #dbg_value(ptr %1, !107, !DIExpression(), !4848)
    #dbg_value(i16 -128, !108, !DIExpression(), !4848)
  br label %19, !dbg !4850

5:                                                ; preds = %3
  store i8 127, ptr @shared_fb, align 16, !dbg !4851, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4854)
    #dbg_value(ptr %1, !107, !DIExpression(), !4854)
    #dbg_value(i16 127, !108, !DIExpression(), !4854)
  br label %19, !dbg !4856

6:                                                ; preds = %3
  store i8 -86, ptr @shared_fb, align 16, !dbg !4857, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4860)
    #dbg_value(ptr %1, !107, !DIExpression(), !4860)
    #dbg_value(i16 -86, !108, !DIExpression(), !4860)
  br label %19, !dbg !4862

7:                                                ; preds = %3
  store i8 -127, ptr @shared_fb, align 16, !dbg !4863, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4866)
    #dbg_value(ptr %1, !107, !DIExpression(), !4866)
    #dbg_value(i16 -127, !108, !DIExpression(), !4866)
  br label %19, !dbg !4868

8:                                                ; preds = %3
  store i8 127, ptr @shared_fb, align 16, !dbg !4869, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4872)
    #dbg_value(ptr %1, !107, !DIExpression(), !4872)
    #dbg_value(i16 127, !108, !DIExpression(), !4872)
  br label %19, !dbg !4874

9:                                                ; preds = %3
  store i8 -64, ptr @shared_fb, align 16, !dbg !4875, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4878)
    #dbg_value(ptr %1, !107, !DIExpression(), !4878)
    #dbg_value(i16 -64, !108, !DIExpression(), !4878)
  br label %19, !dbg !4880

10:                                               ; preds = %3
    #dbg_value(i16 5, !4835, !DIExpression(), !4843)
    #dbg_value(i16 3, !4836, !DIExpression(), !4843)
  store i8 8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 5), align 1, !dbg !4881, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4884)
    #dbg_value(ptr %1, !107, !DIExpression(), !4884)
    #dbg_value(i16 8, !108, !DIExpression(), !4884)
  br label %19, !dbg !4886

11:                                               ; preds = %3
    #dbg_value(i16 5, !4835, !DIExpression(), !4843)
    #dbg_value(i16 3, !4836, !DIExpression(), !4843)
  store i8 -9, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 5), align 1, !dbg !4887, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4890)
    #dbg_value(ptr %1, !107, !DIExpression(), !4890)
    #dbg_value(i16 247, !108, !DIExpression(), !4890)
  br label %19, !dbg !4892

12:                                               ; preds = %3
    #dbg_value(i16 5, !4835, !DIExpression(), !4843)
    #dbg_value(i16 3, !4836, !DIExpression(), !4843)
  store i8 8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 5), align 1, !dbg !4893, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4896)
    #dbg_value(ptr %1, !107, !DIExpression(), !4896)
    #dbg_value(i16 0, !108, !DIExpression(), !4896)
  br label %19, !dbg !4898

13:                                               ; preds = %3
    #dbg_value(i16 0, !4835, !DIExpression(), !4843)
    #dbg_value(i16 poison, !4835, !DIExpression(), !4843)
    #dbg_value(i16 poison, !4835, !DIExpression(), !4843)
  store i8 -1, ptr @shared_fb, align 16, !dbg !4899, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4905)
    #dbg_value(ptr %1, !107, !DIExpression(), !4905)
    #dbg_value(i8 -1, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !4905)
  br label %19, !dbg !4907

14:                                               ; preds = %3
  store i8 0, ptr @shared_fb, align 16, !dbg !4908, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4911)
    #dbg_value(ptr %1, !107, !DIExpression(), !4911)
    #dbg_value(i16 0, !108, !DIExpression(), !4911)
  br label %19, !dbg !4913

15:                                               ; preds = %3
  store i8 64, ptr @shared_fb, align 16, !dbg !4914, !tbaa !113
    #dbg_value(i8 -128, !4837, !DIExpression(), !4915)
    #dbg_value(ptr %0, !106, !DIExpression(), !4916)
    #dbg_value(ptr %1, !107, !DIExpression(), !4916)
    #dbg_value(i16 -128, !108, !DIExpression(), !4916)
  br label %19

16:                                               ; preds = %3
  store i8 -128, ptr @shared_fb, align 16, !dbg !4918, !tbaa !113
    #dbg_value(i8 -64, !4840, !DIExpression(), !4919)
    #dbg_value(ptr %0, !106, !DIExpression(), !4920)
    #dbg_value(ptr %1, !107, !DIExpression(), !4920)
    #dbg_value(i16 -64, !108, !DIExpression(), !4920)
  br label %19

17:                                               ; preds = %3
  store i8 15, ptr @shared_fb, align 16, !dbg !4922, !tbaa !113
  store i8 -16, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !4925, !tbaa !113
  store i8 -86, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !4926, !tbaa !113
  store i8 85, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 3), align 1, !dbg !4927, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4928)
    #dbg_value(ptr %1, !107, !DIExpression(), !4928)
    #dbg_value(i16 255, !108, !DIExpression(), !4928)
  br label %19, !dbg !4930

18:                                               ; preds = %3
  store i8 0, ptr @shared_fb, align 16, !dbg !4931, !tbaa !113
  store i8 0, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !4934, !tbaa !113
  store i8 1, ptr @shared_fb, align 16, !dbg !4935, !tbaa !113
  store i8 -128, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !4936, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !4937)
    #dbg_value(ptr %1, !107, !DIExpression(), !4937)
    #dbg_value(i16 129, !108, !DIExpression(), !4937)
  br label %19, !dbg !4939

19:                                               ; preds = %3, %18, %17, %16, %15, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %20 = phi i8 [ 0, %18 ], [ 0, %17 ], [ -1, %16 ], [ -1, %15 ], [ 0, %14 ], [ -1, %13 ], [ 0, %12 ], [ 0, %11 ], [ 0, %10 ], [ -1, %9 ], [ 0, %8 ], [ -1, %7 ], [ -1, %6 ], [ 0, %5 ], [ -1, %4 ], [ -1, %3 ]
  %21 = phi i8 [ -127, %18 ], [ -1, %17 ], [ -64, %16 ], [ -128, %15 ], [ 0, %14 ], [ -1, %13 ], [ 0, %12 ], [ -9, %11 ], [ 8, %10 ], [ -64, %9 ], [ 127, %8 ], [ -127, %7 ], [ -86, %6 ], [ 127, %5 ], [ -128, %4 ], [ -1, %3 ]
  store i8 %20, ptr %1, align 1, !dbg !4940, !tbaa !113
  %22 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !4941
  store i8 %21, ptr %22, align 1, !dbg !4942, !tbaa !113
  %23 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !4943
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !4944
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !4945
  ret void, !dbg !4946
}

; Function Attrs: nounwind
define hidden void @test_signed_shifts(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !4947 {
    #dbg_value(ptr %0, !4949, !DIExpression(), !4955)
    #dbg_value(ptr %1, !4950, !DIExpression(), !4955)
    #dbg_value(i8 %2, !4951, !DIExpression(), !4955)
  switch i8 %2, label %25 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
    i8 5, label %9
    i8 6, label %14
    i8 7, label %15
    i8 8, label %16
    i8 9, label %17
    i8 10, label %18
    i8 11, label %19
  ], !dbg !4956

4:                                                ; preds = %3
    #dbg_value(i16 -1, !4952, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !4957)
    #dbg_value(ptr %1, !107, !DIExpression(), !4957)
    #dbg_value(i16 -1, !108, !DIExpression(), !4957)
  store i8 -1, ptr %1, align 1, !dbg !4961, !tbaa !113
  br label %26, !dbg !4962

5:                                                ; preds = %3
    #dbg_value(i16 -1, !4952, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !4963)
    #dbg_value(ptr %1, !107, !DIExpression(), !4963)
    #dbg_value(i16 32767, !108, !DIExpression(), !4963)
  store i8 127, ptr %1, align 1, !dbg !4967, !tbaa !113
  br label %26, !dbg !4968

6:                                                ; preds = %3
    #dbg_value(i16 -128, !4952, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !4969)
    #dbg_value(ptr %1, !107, !DIExpression(), !4969)
    #dbg_value(i16 -8, !108, !DIExpression(), !4969)
  store i8 -1, ptr %1, align 1, !dbg !4973, !tbaa !113
  br label %26, !dbg !4974

7:                                                ; preds = %3
    #dbg_value(i16 -128, !4952, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !4975)
    #dbg_value(ptr %1, !107, !DIExpression(), !4975)
    #dbg_value(i16 -8, !108, !DIExpression(), !4975)
  store i8 -1, ptr %1, align 1, !dbg !4979, !tbaa !113
  br label %26, !dbg !4980

8:                                                ; preds = %3
    #dbg_value(i16 -1, !4952, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !4981)
    #dbg_value(ptr %1, !107, !DIExpression(), !4981)
    #dbg_value(i16 -1, !108, !DIExpression(), !4981)
  store i8 -1, ptr %1, align 1, !dbg !4985, !tbaa !113
  br label %26, !dbg !4986

9:                                                ; preds = %3
    #dbg_value(i32 -1, !4953, !DIExpression(), !4955)
  %10 = tail call i32 @lshr_int(i32 noundef -1, i32 noundef 31) #11, !dbg !4987
    #dbg_value(ptr %0, !106, !DIExpression(), !4990)
    #dbg_value(ptr %1, !107, !DIExpression(), !4990)
    #dbg_value(i32 %10, !108, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !4990)
  %11 = lshr i32 %10, 8, !dbg !4992
  %12 = trunc i32 %11 to i8, !dbg !4992
  store i8 %12, ptr %1, align 1, !dbg !4993, !tbaa !113
  %13 = trunc i32 %10 to i8, !dbg !4994
  br label %26, !dbg !4995

14:                                               ; preds = %3
    #dbg_value(i16 -32768, !4952, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !4996)
    #dbg_value(ptr %1, !107, !DIExpression(), !4996)
    #dbg_value(i16 -16384, !108, !DIExpression(), !4996)
  store i8 -64, ptr %1, align 1, !dbg !5000, !tbaa !113
  br label %26, !dbg !5001

15:                                               ; preds = %3
    #dbg_value(i16 -32768, !4952, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !5002)
    #dbg_value(ptr %1, !107, !DIExpression(), !5002)
    #dbg_value(i16 0, !108, !DIExpression(), !5002)
  store i8 0, ptr %1, align 1, !dbg !5006, !tbaa !113
  br label %26, !dbg !5007

16:                                               ; preds = %3
    #dbg_value(i16 -256, !4952, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !5008)
    #dbg_value(ptr %1, !107, !DIExpression(), !5008)
    #dbg_value(i16 -1, !108, !DIExpression(), !5008)
  store i8 -1, ptr %1, align 1, !dbg !5012, !tbaa !113
  br label %26, !dbg !5013

17:                                               ; preds = %3
    #dbg_value(i8 -1, !4954, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !5014)
    #dbg_value(ptr %1, !107, !DIExpression(), !5014)
    #dbg_value(i16 -1, !108, !DIExpression(), !5014)
  store i8 -1, ptr %1, align 1, !dbg !5018, !tbaa !113
  br label %26, !dbg !5019

18:                                               ; preds = %3
    #dbg_value(i32 -1, !4953, !DIExpression(), !4955)
    #dbg_value(ptr %0, !106, !DIExpression(), !5020)
    #dbg_value(ptr %1, !107, !DIExpression(), !5020)
    #dbg_value(i16 -1, !108, !DIExpression(), !5020)
  store i8 -1, ptr %1, align 1, !dbg !5024, !tbaa !113
  br label %26, !dbg !5025

19:                                               ; preds = %3
    #dbg_value(i32 -2147483648, !4953, !DIExpression(), !4955)
  %20 = tail call i32 @lshr_int(i32 noundef -2147483648, i32 noundef 1) #11, !dbg !5026
  %21 = lshr i32 %20, 16, !dbg !5029
    #dbg_value(ptr %0, !106, !DIExpression(), !5030)
    #dbg_value(ptr %1, !107, !DIExpression(), !5030)
    #dbg_value(i32 %21, !108, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !5030)
  %22 = lshr i32 %20, 24, !dbg !5032
  %23 = trunc nuw i32 %22 to i8, !dbg !5032
  store i8 %23, ptr %1, align 1, !dbg !5033, !tbaa !113
  %24 = trunc i32 %21 to i8, !dbg !5034
  br label %26, !dbg !5035

25:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5036)
    #dbg_value(ptr %1, !107, !DIExpression(), !5036)
    #dbg_value(i16 -1, !108, !DIExpression(), !5036)
  store i8 -1, ptr %1, align 1, !dbg !5038, !tbaa !113
  br label %26, !dbg !5039

26:                                               ; preds = %25, %19, %18, %17, %16, %15, %14, %9, %8, %7, %6, %5, %4
  %27 = phi i8 [ -1, %25 ], [ %24, %19 ], [ -1, %18 ], [ -1, %17 ], [ -1, %16 ], [ 0, %15 ], [ 0, %14 ], [ %13, %9 ], [ -1, %8 ], [ -8, %7 ], [ -8, %6 ], [ -1, %5 ], [ -1, %4 ]
  %28 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5040
  store i8 %27, ptr %28, align 1, !dbg !5041, !tbaa !113
  %29 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5042
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5043
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5044
  ret void, !dbg !5039
}

; Function Attrs: nounwind
define hidden void @test_struct_arrays(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5045 {
    #dbg_value(ptr %0, !5047, !DIExpression(), !5059)
    #dbg_value(ptr %1, !5048, !DIExpression(), !5059)
    #dbg_value(i8 %2, !5049, !DIExpression(), !5059)
  switch i8 %2, label %60 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %22
    i8 5, label %23
    i8 6, label %24
    i8 7, label %41
    i8 8, label %56
    i8 9, label %57
    i8 10, label %58
    i8 11, label %59
  ], !dbg !5060

4:                                                ; preds = %3
  store i16 10, ptr @g_pts, align 16, !dbg !5061, !tbaa !5064
    #dbg_value(ptr %0, !106, !DIExpression(), !5066)
    #dbg_value(ptr %1, !107, !DIExpression(), !5066)
    #dbg_value(i16 10, !108, !DIExpression(), !5066)
  store i8 0, ptr %1, align 1, !dbg !5068, !tbaa !113
  br label %61, !dbg !5069

5:                                                ; preds = %3
  store i16 10, ptr @g_pts, align 16, !dbg !5070, !tbaa !5064
  store i16 20, ptr getelementptr inbounds (i8, ptr @g_pts, i32 2), align 2, !dbg !5073, !tbaa !5074
    #dbg_value(ptr %0, !106, !DIExpression(), !5075)
    #dbg_value(ptr %1, !107, !DIExpression(), !5075)
    #dbg_value(i16 30, !108, !DIExpression(), !5075)
  store i8 0, ptr %1, align 1, !dbg !5077, !tbaa !113
  br label %61, !dbg !5078

6:                                                ; preds = %3
  store i16 5, ptr getelementptr inbounds (i8, ptr @g_pts, i32 4), align 4, !dbg !5079, !tbaa !5064
  store i16 15, ptr getelementptr inbounds (i8, ptr @g_pts, i32 8), align 8, !dbg !5082, !tbaa !5064
    #dbg_value(ptr %0, !106, !DIExpression(), !5083)
    #dbg_value(ptr %1, !107, !DIExpression(), !5083)
    #dbg_value(i16 20, !108, !DIExpression(), !5083)
  store i8 0, ptr %1, align 1, !dbg !5085, !tbaa !113
  br label %61, !dbg !5086

7:                                                ; preds = %3, %7
  %8 = phi i32 [ %15, %7 ], [ 0, %3 ]
  %9 = phi i32 [ %13, %7 ], [ 0, %3 ]
  %10 = trunc i32 %9 to i16, !dbg !5087
  %11 = mul i16 %10, 10, !dbg !5087
  %12 = getelementptr inbounds [4 x %struct.point_s], ptr @g_pts, i32 0, i32 %8, !dbg !5093
  store i16 %11, ptr %12, align 4, !dbg !5094, !tbaa !5064
  %13 = add nsw i32 %8, 1, !dbg !5095
    #dbg_value(i16 poison, !5050, !DIExpression(), !5059)
  %14 = shl i32 %13, 16, !dbg !5096
  %15 = ashr exact i32 %14, 16, !dbg !5096
  %16 = icmp slt i32 %15, 4, !dbg !5097
  br i1 %16, label %7, label %17, !dbg !5098, !llvm.loop !5099

17:                                               ; preds = %7
  %18 = load i16, ptr getelementptr inbounds (i8, ptr @g_pts, i32 8), align 8, !dbg !5101, !tbaa !5064
    #dbg_value(ptr %0, !106, !DIExpression(), !5102)
    #dbg_value(ptr %1, !107, !DIExpression(), !5102)
    #dbg_value(i16 %18, !108, !DIExpression(), !5102)
  %19 = lshr i16 %18, 8, !dbg !5104
  %20 = trunc nuw i16 %19 to i8, !dbg !5105
  store i8 %20, ptr %1, align 1, !dbg !5106, !tbaa !113
  %21 = trunc i16 %18 to i8, !dbg !5107
  br label %61, !dbg !5108

22:                                               ; preds = %3
  store i16 100, ptr @g_pipes, align 16, !dbg !5109, !tbaa !5112
  store i16 50, ptr getelementptr inbounds (i8, ptr @g_pipes, i32 2), align 2, !dbg !5114, !tbaa !5115
    #dbg_value(ptr %0, !106, !DIExpression(), !5116)
    #dbg_value(ptr %1, !107, !DIExpression(), !5116)
    #dbg_value(i16 100, !108, !DIExpression(), !5116)
  store i8 0, ptr %1, align 1, !dbg !5118, !tbaa !113
  br label %61, !dbg !5119

23:                                               ; preds = %3
  store i8 1, ptr getelementptr inbounds (i8, ptr @g_pipes, i32 10), align 2, !dbg !5120, !tbaa !5123
    #dbg_value(ptr %0, !106, !DIExpression(), !5124)
    #dbg_value(ptr %1, !107, !DIExpression(), !5124)
    #dbg_value(i16 1, !108, !DIExpression(), !5124)
  store i8 0, ptr %1, align 1, !dbg !5126, !tbaa !113
  br label %61, !dbg !5127

24:                                               ; preds = %3
  store i8 0, ptr getelementptr inbounds (i8, ptr @g_pipes, i32 4), align 4, !dbg !5128, !tbaa !5123
  store i8 0, ptr getelementptr inbounds (i8, ptr @g_pipes, i32 10), align 2, !dbg !5129, !tbaa !5123
  store i8 1, ptr getelementptr inbounds (i8, ptr @g_pipes, i32 16), align 16, !dbg !5130, !tbaa !5123
    #dbg_value(i16 -1, !5052, !DIExpression(), !5131)
    #dbg_value(i16 0, !5050, !DIExpression(), !5059)
  br label %25, !dbg !5132

25:                                               ; preds = %24, %25
  %26 = phi i32 [ 0, %24 ], [ %35, %25 ]
  %27 = phi i16 [ -1, %24 ], [ %34, %25 ]
    #dbg_value(i32 %26, !5050, !DIExpression(), !5059)
    #dbg_value(i16 %27, !5052, !DIExpression(), !5131)
  %28 = getelementptr inbounds [3 x %struct.pipe_s], ptr @g_pipes, i32 0, i32 %26, i32 2, !dbg !5134
  %29 = load i8, ptr %28, align 2, !dbg !5134, !tbaa !5123
  %30 = icmp ne i8 %29, 0, !dbg !5138
  %31 = icmp slt i16 %27, 0
  %32 = select i1 %30, i1 %31, i1 false, !dbg !5139
  %33 = trunc nuw nsw i32 %26 to i16, !dbg !5139
  %34 = select i1 %32, i16 %33, i16 %27, !dbg !5139
    #dbg_value(i16 %34, !5052, !DIExpression(), !5131)
  %35 = add nuw nsw i32 %26, 1, !dbg !5140
    #dbg_value(i32 %35, !5050, !DIExpression(), !5059)
  %36 = icmp eq i32 %35, 3, !dbg !5141
  br i1 %36, label %37, label %25, !dbg !5132, !llvm.loop !5142

37:                                               ; preds = %25
    #dbg_value(ptr %0, !106, !DIExpression(), !5144)
    #dbg_value(ptr %1, !107, !DIExpression(), !5144)
    #dbg_value(i16 %34, !108, !DIExpression(), !5144)
  %38 = lshr i16 %34, 8, !dbg !5146
  %39 = trunc nuw i16 %38 to i8, !dbg !5147
  store i8 %39, ptr %1, align 1, !dbg !5148, !tbaa !113
  %40 = trunc i16 %34 to i8, !dbg !5149
  br label %61

41:                                               ; preds = %3
  store i16 1, ptr @g_pts, align 16, !dbg !5150, !tbaa !5064
  store i16 2, ptr getelementptr inbounds (i8, ptr @g_pts, i32 4), align 4, !dbg !5153, !tbaa !5064
  store i16 3, ptr getelementptr inbounds (i8, ptr @g_pts, i32 8), align 8, !dbg !5154, !tbaa !5064
  store i16 4, ptr getelementptr inbounds (i8, ptr @g_pts, i32 12), align 4, !dbg !5155, !tbaa !5064
    #dbg_value(i16 0, !5051, !DIExpression(), !5059)
    #dbg_value(i16 0, !5050, !DIExpression(), !5059)
    #dbg_value(i16 poison, !5050, !DIExpression(), !5059)
  br label %42, !dbg !5156

42:                                               ; preds = %41, %42
  %43 = phi i32 [ 0, %41 ], [ %50, %42 ]
  %44 = phi i16 [ 0, %41 ], [ %47, %42 ]
    #dbg_value(i16 %44, !5051, !DIExpression(), !5059)
  %45 = getelementptr inbounds [4 x %struct.point_s], ptr @g_pts, i32 0, i32 %43, !dbg !5158
  %46 = load i16, ptr %45, align 4, !dbg !5161, !tbaa !5064
  %47 = add i16 %46, %44, !dbg !5162
    #dbg_value(i16 %47, !5051, !DIExpression(), !5059)
    #dbg_value(i16 poison, !5050, !DIExpression(), !5059)
  %48 = shl nsw i32 %43, 16, !dbg !5163
  %49 = add i32 %48, 65536, !dbg !5163
  %50 = ashr exact i32 %49, 16, !dbg !5163
  %51 = icmp slt i32 %50, 4, !dbg !5164
  br i1 %51, label %42, label %52, !dbg !5156, !llvm.loop !5165

52:                                               ; preds = %42
    #dbg_value(ptr %0, !106, !DIExpression(), !5167)
    #dbg_value(ptr %1, !107, !DIExpression(), !5167)
    #dbg_value(i16 %47, !108, !DIExpression(), !5167)
  %53 = lshr i16 %47, 8, !dbg !5169
  %54 = trunc nuw i16 %53 to i8, !dbg !5170
  store i8 %54, ptr %1, align 1, !dbg !5171, !tbaa !113
  %55 = trunc i16 %47 to i8, !dbg !5172
  br label %61, !dbg !5173

56:                                               ; preds = %3
  store i8 2, ptr getelementptr inbounds (i8, ptr @g_pipes, i32 4), align 4, !dbg !5174, !tbaa !5123
  store i16 42, ptr getelementptr inbounds (i8, ptr @g_pts, i32 8), align 8, !dbg !5177, !tbaa !5064
    #dbg_value(ptr %0, !106, !DIExpression(), !5178)
    #dbg_value(ptr %1, !107, !DIExpression(), !5178)
    #dbg_value(i16 42, !108, !DIExpression(), !5178)
  store i8 0, ptr %1, align 1, !dbg !5180, !tbaa !113
  br label %61, !dbg !5181

57:                                               ; preds = %3
  store i16 10, ptr @g_pts, align 16, !dbg !5182, !tbaa !5064
  store i16 20, ptr getelementptr inbounds (i8, ptr @g_pts, i32 2), align 2, !dbg !5183, !tbaa !5074
  store i16 30, ptr getelementptr inbounds (i8, ptr @g_pts, i32 4), align 4, !dbg !5184, !tbaa !5064
  store i16 40, ptr getelementptr inbounds (i8, ptr @g_pts, i32 6), align 2, !dbg !5185, !tbaa !5074
    #dbg_value(i16 10, !5055, !DIExpression(), !5186)
    #dbg_value(i16 20, !5058, !DIExpression(), !5186)
  store i16 30, ptr @g_pts, align 16, !dbg !5187, !tbaa !5064
  store i16 40, ptr getelementptr inbounds (i8, ptr @g_pts, i32 2), align 2, !dbg !5188, !tbaa !5074
  store i16 10, ptr getelementptr inbounds (i8, ptr @g_pts, i32 4), align 4, !dbg !5189, !tbaa !5064
  store i16 20, ptr getelementptr inbounds (i8, ptr @g_pts, i32 6), align 2, !dbg !5190, !tbaa !5074
    #dbg_value(ptr %0, !106, !DIExpression(), !5191)
    #dbg_value(ptr %1, !107, !DIExpression(), !5191)
    #dbg_value(i16 50, !108, !DIExpression(), !5191)
  store i8 0, ptr %1, align 1, !dbg !5193, !tbaa !113
  br label %61

58:                                               ; preds = %3
  store i16 100, ptr @g_pts, align 16, !dbg !5194, !tbaa !5064
  store i16 200, ptr getelementptr inbounds (i8, ptr @g_pts, i32 2), align 2, !dbg !5197, !tbaa !5074
  store i16 100, ptr getelementptr inbounds (i8, ptr @g_pts, i32 4), align 4, !dbg !5198, !tbaa !5064
  store i16 200, ptr getelementptr inbounds (i8, ptr @g_pts, i32 6), align 2, !dbg !5199, !tbaa !5074
    #dbg_value(ptr %0, !106, !DIExpression(), !5200)
    #dbg_value(ptr %1, !107, !DIExpression(), !5200)
    #dbg_value(i16 300, !108, !DIExpression(), !5200)
  store i8 1, ptr %1, align 1, !dbg !5202, !tbaa !113
  br label %61, !dbg !5203

59:                                               ; preds = %3
  store i16 1, ptr @g_pts, align 16, !dbg !5204, !tbaa !5064
  store i16 2, ptr getelementptr inbounds (i8, ptr @g_pts, i32 4), align 4, !dbg !5207, !tbaa !5064
  store i16 3, ptr getelementptr inbounds (i8, ptr @g_pts, i32 8), align 8, !dbg !5208, !tbaa !5064
  store i16 4, ptr getelementptr inbounds (i8, ptr @g_pts, i32 12), align 4, !dbg !5209, !tbaa !5064
    #dbg_value(ptr %0, !106, !DIExpression(), !5210)
    #dbg_value(ptr %1, !107, !DIExpression(), !5210)
    #dbg_value(i16 3, !108, !DIExpression(), !5210)
  store i8 0, ptr %1, align 1, !dbg !5212, !tbaa !113
  br label %61, !dbg !5213

60:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5214)
    #dbg_value(ptr %1, !107, !DIExpression(), !5214)
    #dbg_value(i16 -1, !108, !DIExpression(), !5214)
  store i8 -1, ptr %1, align 1, !dbg !5216, !tbaa !113
  br label %61, !dbg !5217

61:                                               ; preds = %60, %59, %58, %57, %56, %52, %37, %23, %22, %17, %6, %5, %4
  %62 = phi i8 [ -1, %60 ], [ 3, %59 ], [ 44, %58 ], [ 50, %57 ], [ 42, %56 ], [ %55, %52 ], [ %40, %37 ], [ 1, %23 ], [ 100, %22 ], [ %21, %17 ], [ 20, %6 ], [ 30, %5 ], [ 10, %4 ]
  %63 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5218
  store i8 %62, ptr %63, align 1, !dbg !5219, !tbaa !113
  %64 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5220
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5221
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5222
  ret void, !dbg !5217
}

; Function Attrs: nounwind
define hidden void @test_high_local_count(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5223 {
    #dbg_value(ptr %0, !5225, !DIExpression(), !5256)
    #dbg_value(ptr %1, !5226, !DIExpression(), !5256)
    #dbg_value(i8 %2, !5227, !DIExpression(), !5256)
  switch i8 %2, label %17 [
    i8 0, label %18
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %16
  ], !dbg !5257

4:                                                ; preds = %3
    #dbg_value(i16 poison, !5239, !DIExpression(), !5258)
    #dbg_value(i16 poison, !5236, !DIExpression(), !5258)
    #dbg_value(ptr %0, !106, !DIExpression(), !5259)
    #dbg_value(ptr %1, !107, !DIExpression(), !5259)
    #dbg_value(i16 136, !108, !DIExpression(), !5259)
  br label %18

5:                                                ; preds = %3
    #dbg_value(i16 1, !5240, !DIExpression(), !5261)
    #dbg_value(i16 2, !5228, !DIExpression(), !5256)
    #dbg_value(i16 1, !5229, !DIExpression(), !5256)
    #dbg_value(ptr %0, !106, !DIExpression(), !5262)
    #dbg_value(ptr %1, !107, !DIExpression(), !5262)
    #dbg_value(i16 21, !108, !DIExpression(), !5262)
  br label %18

6:                                                ; preds = %3
    #dbg_value(i16 1, !5228, !DIExpression(), !5256)
    #dbg_value(i16 2, !5229, !DIExpression(), !5256)
    #dbg_value(i16 3, !5230, !DIExpression(), !5256)
    #dbg_value(i16 4, !5231, !DIExpression(), !5256)
    #dbg_value(i32 1000, !5243, !DIExpression(), !5264)
    #dbg_value(i32 2000, !5246, !DIExpression(), !5264)
    #dbg_value(ptr %0, !106, !DIExpression(), !5265)
    #dbg_value(ptr %1, !107, !DIExpression(), !5265)
    #dbg_value(i16 40, !108, !DIExpression(), !5265)
  br label %18

7:                                                ; preds = %3
    #dbg_value(i16 poison, !5251, !DIExpression(), !5267)
    #dbg_value(i16 poison, !5250, !DIExpression(), !5267)
    #dbg_value(i16 poison, !5247, !DIExpression(), !5267)
    #dbg_value(ptr %0, !106, !DIExpression(), !5268)
    #dbg_value(ptr %1, !107, !DIExpression(), !5268)
    #dbg_value(i16 25, !108, !DIExpression(), !5268)
  br label %18

8:                                                ; preds = %3
    #dbg_value(i16 10, !5228, !DIExpression(), !5256)
    #dbg_value(i16 20, !5229, !DIExpression(), !5256)
    #dbg_value(i16 20, !5229, !DIExpression(), !5256)
    #dbg_value(ptr %0, !106, !DIExpression(), !5270)
    #dbg_value(ptr %1, !107, !DIExpression(), !5270)
    #dbg_value(i16 30, !108, !DIExpression(), !5270)
  br label %18, !dbg !5274

9:                                                ; preds = %3, %9
  %10 = phi i16 [ %14, %9 ], [ 1, %3 ]
    #dbg_value(i16 poison, !5255, !DIExpression(), !5275)
    #dbg_value(i16 %10, !5252, !DIExpression(), !5275)
  %11 = and i16 %10, 7, !dbg !5276
  %12 = zext nneg i16 %11 to i32, !dbg !5276
  %13 = getelementptr inbounds [8 x i16], ptr @g_shorts, i32 0, i32 %12, !dbg !5280
  store i16 %10, ptr %13, align 2, !dbg !5281, !tbaa !3184
    #dbg_value(!DIArgList(i16 poison, i16 %10), !5255, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus, DW_OP_stack_value), !5275)
  %14 = add nuw nsw i16 %10, 1, !dbg !5282
    #dbg_value(i16 %14, !5252, !DIExpression(), !5275)
  %15 = icmp ult i16 %10, 20, !dbg !5283
  br i1 %15, label %9, label %18, !dbg !5284, !llvm.loop !5285

16:                                               ; preds = %3
    #dbg_value(i16 42, !5228, !DIExpression(), !5256)
    #dbg_value(i16 42, !5229, !DIExpression(), !5256)
    #dbg_value(i16 42, !5230, !DIExpression(), !5256)
    #dbg_value(i16 42, !5231, !DIExpression(), !5256)
    #dbg_value(ptr %0, !106, !DIExpression(), !5287)
    #dbg_value(ptr %1, !107, !DIExpression(), !5287)
    #dbg_value(i16 168, !108, !DIExpression(), !5287)
  br label %18, !dbg !5291

17:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5292)
    #dbg_value(ptr %1, !107, !DIExpression(), !5292)
    #dbg_value(i16 -1, !108, !DIExpression(), !5292)
  br label %18, !dbg !5294

18:                                               ; preds = %9, %3, %17, %16, %8, %7, %6, %5, %4
  %19 = phi i8 [ -1, %17 ], [ 0, %16 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ], [ 0, %9 ]
  %20 = phi i8 [ -1, %17 ], [ -88, %16 ], [ 30, %8 ], [ 25, %7 ], [ 40, %6 ], [ 21, %5 ], [ -120, %4 ], [ 36, %3 ], [ -46, %9 ]
  store i8 %19, ptr %1, align 1, !dbg !5295, !tbaa !113
  %21 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5296
  store i8 %20, ptr %21, align 1, !dbg !5297, !tbaa !113
  %22 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5298
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5299
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5300
  ret void, !dbg !5294
}

; Function Attrs: nounwind
define hidden void @test_graphics_primitives(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5301 {
    #dbg_value(ptr %0, !5303, !DIExpression(), !5311)
    #dbg_value(ptr %1, !5304, !DIExpression(), !5311)
    #dbg_value(i8 %2, !5305, !DIExpression(), !5311)
  switch i8 %2, label %28 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %21
    i8 4, label %22
    i8 5, label %23
    i8 6, label %24
    i8 7, label %25
    i8 8, label %26
    i8 9, label %27
  ], !dbg !5312

4:                                                ; preds = %3
  store i8 -1, ptr @shared_fb, align 16, !dbg !5313, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5316)
    #dbg_value(ptr %1, !107, !DIExpression(), !5316)
    #dbg_value(i16 -1, !108, !DIExpression(), !5316)
  br label %28, !dbg !5318

5:                                                ; preds = %3
  store i8 16, ptr @shared_fb, align 16, !dbg !5319, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5322)
    #dbg_value(ptr %1, !107, !DIExpression(), !5322)
    #dbg_value(i16 16, !108, !DIExpression(), !5322)
  br label %28, !dbg !5324

6:                                                ; preds = %3, %6
  %7 = phi i32 [ %11, %6 ], [ 0, %3 ]
  %8 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %7, !dbg !5325
  store i8 -1, ptr %8, align 1, !dbg !5331, !tbaa !113
    #dbg_value(i16 poison, !5307, !DIExpression(), !5311)
  %9 = shl nsw i32 %7, 16, !dbg !5332
  %10 = add i32 %9, 65536, !dbg !5332
  %11 = ashr exact i32 %10, 16, !dbg !5332
  %12 = icmp slt i32 %11, 4, !dbg !5333
  br i1 %12, label %6, label %13, !dbg !5334, !llvm.loop !5335

13:                                               ; preds = %6
  %14 = load i8, ptr @shared_fb, align 16, !dbg !5337, !tbaa !113
  %15 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !5338, !tbaa !113
  %16 = and i8 %15, %14, !dbg !5339
  %17 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !5340, !tbaa !113
  %18 = and i8 %16, %17, !dbg !5341
  %19 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 3), align 1, !dbg !5342, !tbaa !113
  %20 = and i8 %18, %19, !dbg !5343
    #dbg_value(ptr %0, !106, !DIExpression(), !5344)
    #dbg_value(ptr %1, !107, !DIExpression(), !5344)
    #dbg_value(i8 undef, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !5344)
  br label %28, !dbg !5346

21:                                               ; preds = %3
  store i32 0, ptr @shared_fb, align 16, !dbg !5347
  store i8 -1, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !5350, !tbaa !113
  store i8 -1, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !5351, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5352)
    #dbg_value(ptr %1, !107, !DIExpression(), !5352)
    #dbg_value(i16 510, !108, !DIExpression(), !5352)
  br label %28, !dbg !5354

22:                                               ; preds = %3
  store i8 31, ptr @shared_fb, align 16, !dbg !5355, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5358)
    #dbg_value(ptr %1, !107, !DIExpression(), !5358)
    #dbg_value(i16 31, !108, !DIExpression(), !5358)
  br label %28, !dbg !5360

23:                                               ; preds = %3
  store i8 -32, ptr @shared_fb, align 16, !dbg !5361, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5364)
    #dbg_value(ptr %1, !107, !DIExpression(), !5364)
    #dbg_value(i16 -32, !108, !DIExpression(), !5364)
  br label %28, !dbg !5366

24:                                               ; preds = %3
  store i8 0, ptr @shared_fb, align 16, !dbg !5367, !tbaa !113
  store i8 0, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !5370, !tbaa !113
  store i8 0, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !5371, !tbaa !113
  store i8 15, ptr @shared_fb, align 16, !dbg !5372, !tbaa !113
  store i8 -1, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 1), align 1, !dbg !5373, !tbaa !113
  store i8 -16, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !5374, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5375)
    #dbg_value(ptr %1, !107, !DIExpression(), !5375)
    #dbg_value(i16 510, !108, !DIExpression(), !5375)
  br label %28, !dbg !5377

25:                                               ; preds = %3
  store i8 -17, ptr @shared_fb, align 16, !dbg !5378, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5381)
    #dbg_value(ptr %1, !107, !DIExpression(), !5381)
    #dbg_value(i16 239, !108, !DIExpression(), !5381)
  br label %28, !dbg !5383

26:                                               ; preds = %3
  store i8 90, ptr @shared_fb, align 16, !dbg !5384, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5387)
    #dbg_value(ptr %1, !107, !DIExpression(), !5387)
    #dbg_value(i16 90, !108, !DIExpression(), !5387)
  br label %28, !dbg !5389

27:                                               ; preds = %3
  store i8 16, ptr @shared_fb, align 16, !dbg !5390, !tbaa !113
    #dbg_value(i16 3, !5306, !DIExpression(), !5311)
    #dbg_value(i16 1, !5308, !DIExpression(), !5391)
    #dbg_value(ptr %0, !106, !DIExpression(), !5392)
    #dbg_value(ptr %1, !107, !DIExpression(), !5392)
    #dbg_value(i16 1, !108, !DIExpression(), !5392)
  br label %28

28:                                               ; preds = %3, %27, %26, %25, %24, %23, %22, %21, %13, %5, %4
  %29 = phi i8 [ 0, %27 ], [ 0, %26 ], [ 0, %25 ], [ 1, %24 ], [ -1, %23 ], [ 0, %22 ], [ 1, %21 ], [ 0, %13 ], [ 0, %5 ], [ -1, %4 ], [ -1, %3 ]
  %30 = phi i8 [ 1, %27 ], [ 90, %26 ], [ -17, %25 ], [ -2, %24 ], [ -32, %23 ], [ 31, %22 ], [ -2, %21 ], [ %20, %13 ], [ 16, %5 ], [ -1, %4 ], [ -1, %3 ]
  store i8 %29, ptr %1, align 1, !dbg !5394, !tbaa !113
  %31 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5395
  store i8 %30, ptr %31, align 1, !dbg !5396, !tbaa !113
  %32 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5397
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5398
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5399
  ret void, !dbg !5400
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(write, argmem: none, inaccessiblemem: none)
define hidden noundef signext i16 @set_global_short() local_unnamed_addr #8 !dbg !5401 {
  store i16 1, ptr @g_short, align 2, !dbg !5402, !tbaa !3184
  ret i16 1, !dbg !5403
}

; Function Attrs: nounwind
define hidden void @test_boolean_density(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5404 {
    #dbg_value(ptr %0, !5406, !DIExpression(), !5435)
    #dbg_value(ptr %1, !5407, !DIExpression(), !5435)
    #dbg_value(i8 %2, !5408, !DIExpression(), !5435)
    #dbg_value(i16 1, !5409, !DIExpression(), !5435)
    #dbg_value(i16 1, !5410, !DIExpression(), !5435)
    #dbg_value(i16 0, !5411, !DIExpression(), !5435)
    #dbg_value(i16 0, !5412, !DIExpression(), !5435)
  switch i8 %2, label %7 [
    i8 0, label %8
    i8 1, label %8
    i8 2, label %8
    i8 3, label %8
    i8 4, label %8
    i8 5, label %8
    i8 6, label %4
    i8 7, label %5
    i8 8, label %8
    i8 9, label %6
    i8 10, label %8
    i8 11, label %8
  ], !dbg !5436

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5437)
    #dbg_value(ptr %1, !107, !DIExpression(), !5437)
    #dbg_value(i16 0, !108, !DIExpression(), !5437)
  br label %8, !dbg !5441

5:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5442)
    #dbg_value(ptr %1, !107, !DIExpression(), !5442)
    #dbg_value(i16 0, !108, !DIExpression(), !5442)
  br label %8, !dbg !5446

6:                                                ; preds = %3
  store i16 0, ptr @g_short, align 2, !dbg !5447, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5450)
    #dbg_value(ptr %1, !107, !DIExpression(), !5450)
    #dbg_value(i16 0, !108, !DIExpression(), !5450)
  br label %8, !dbg !5452

7:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5453)
    #dbg_value(ptr %1, !107, !DIExpression(), !5453)
    #dbg_value(i16 -1, !108, !DIExpression(), !5453)
  br label %8, !dbg !5455

8:                                                ; preds = %3, %3, %3, %3, %3, %3, %3, %3, %3, %7, %6, %5, %4
  %9 = phi i8 [ -1, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ], [ 0, %3 ]
  %10 = phi i8 [ -1, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ], [ 1, %3 ]
  store i8 %9, ptr %1, align 1, !dbg !5456, !tbaa !113
  %11 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5457
  store i8 %10, ptr %11, align 1, !dbg !5458, !tbaa !113
  %12 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5459
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5460
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5461
  ret void, !dbg !5455
}

; Function Attrs: nounwind
define hidden void @test_loop_edge_cases(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5462 {
    #dbg_value(ptr %0, !5464, !DIExpression(), !5472)
    #dbg_value(ptr %1, !5465, !DIExpression(), !5472)
    #dbg_value(i8 %2, !5466, !DIExpression(), !5472)
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
  ], !dbg !5473

4:                                                ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i32 poison, !5467, !DIExpression(), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5474)
    #dbg_value(ptr %1, !107, !DIExpression(), !5474)
    #dbg_value(i16 1, !108, !DIExpression(), !5474)
  br label %29, !dbg !5478

5:                                                ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5479)
    #dbg_value(ptr %1, !107, !DIExpression(), !5479)
    #dbg_value(i16 55, !108, !DIExpression(), !5479)
  br label %29, !dbg !5483

6:                                                ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5484)
    #dbg_value(ptr %1, !107, !DIExpression(), !5484)
    #dbg_value(i16 20, !108, !DIExpression(), !5484)
  br label %29, !dbg !5488

7:                                                ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5489)
    #dbg_value(ptr %1, !107, !DIExpression(), !5489)
    #dbg_value(i16 15, !108, !DIExpression(), !5489)
  br label %29, !dbg !5493

8:                                                ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 undef, !5467, !DIExpression(), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5494)
    #dbg_value(ptr %1, !107, !DIExpression(), !5494)
    #dbg_value(i16 10, !108, !DIExpression(), !5494)
  br label %29, !dbg !5498

9:                                                ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
    #dbg_value(i32 10, !5468, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5499)
    #dbg_value(ptr %1, !107, !DIExpression(), !5499)
    #dbg_value(i32 10, !108, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !5499)
  br label %29, !dbg !5503

10:                                               ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5469, !DIExpression(), !5504)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5505)
    #dbg_value(ptr %1, !107, !DIExpression(), !5505)
    #dbg_value(i16 12, !108, !DIExpression(), !5505)
  br label %29

11:                                               ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5507)
    #dbg_value(ptr %1, !107, !DIExpression(), !5507)
    #dbg_value(i16 7, !108, !DIExpression(), !5507)
  br label %29, !dbg !5511

12:                                               ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5512)
    #dbg_value(ptr %1, !107, !DIExpression(), !5512)
    #dbg_value(i16 9, !108, !DIExpression(), !5512)
  br label %29, !dbg !5516

13:                                               ; preds = %3, %16
  %14 = phi i32 [ %18, %16 ], [ 0, %3 ]
  %15 = phi i16 [ %17, %16 ], [ 0, %3 ]
    #dbg_value(i16 %15, !5468, !DIExpression(), !5472)
  switch i32 %14, label %16 [
    i32 327680, label %22
    i32 196608, label %22
  ], !dbg !5517

16:                                               ; preds = %13
  %17 = add nuw nsw i16 %15, 1, !dbg !5521
    #dbg_value(i16 %17, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
  %18 = add nuw nsw i32 %14, 65536, !dbg !5524
  %19 = icmp ugt i32 %14, 524288, !dbg !5525
  br i1 %19, label %26, label %13, !dbg !5517, !llvm.loop !5526

20:                                               ; preds = %3
    #dbg_value(i16 poison, !5468, !DIExpression(), !5472)
    #dbg_value(i16 poison, !5467, !DIExpression(), !5472)
    #dbg_value(i32 10, !5468, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !5472)
    #dbg_value(ptr %0, !106, !DIExpression(), !5528)
    #dbg_value(ptr %1, !107, !DIExpression(), !5528)
    #dbg_value(i32 10, !108, !DIExpression(DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_stack_value), !5528)
  br label %29, !dbg !5532

21:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5533)
    #dbg_value(ptr %1, !107, !DIExpression(), !5533)
    #dbg_value(i16 -1, !108, !DIExpression(), !5533)
  br label %29, !dbg !5535

22:                                               ; preds = %13, %13
  %23 = trunc i16 %15 to i8
  %24 = lshr i16 %15, 8
  %25 = trunc nuw nsw i16 %24 to i8
  br label %29, !dbg !5536

26:                                               ; preds = %16
  %27 = lshr i16 %17, 8
  %28 = trunc nuw nsw i16 %27 to i8
  br label %29, !dbg !5536

29:                                               ; preds = %22, %26, %3, %21, %20, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %30 = phi i8 [ -1, %21 ], [ 0, %20 ], [ 0, %12 ], [ 0, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ], [ %25, %22 ], [ %28, %26 ]
  %31 = phi i8 [ -1, %21 ], [ 10, %20 ], [ %2, %12 ], [ 7, %11 ], [ 12, %10 ], [ 10, %9 ], [ 10, %8 ], [ 15, %7 ], [ 20, %6 ], [ 55, %5 ], [ %2, %4 ], [ %2, %3 ], [ %23, %22 ], [ 10, %26 ]
  store i8 %30, ptr %1, align 1, !dbg !5536, !tbaa !113
  %32 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5537
  store i8 %31, ptr %32, align 1, !dbg !5538, !tbaa !113
  %33 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5539
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5540
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5541
  ret void, !dbg !5535
}

; Function Attrs: nounwind
define hidden void @test_type_coercion_edge(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5542 {
    #dbg_value(ptr %0, !5544, !DIExpression(), !5560)
    #dbg_value(ptr %1, !5545, !DIExpression(), !5560)
    #dbg_value(i8 %2, !5546, !DIExpression(), !5560)
  switch i8 %2, label %18 [
    i8 0, label %19
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
    i8 11, label %14
    i8 12, label %15
    i8 13, label %16
    i8 14, label %17
  ], !dbg !5561

4:                                                ; preds = %3
    #dbg_value(i16 -1, !5548, !DIExpression(), !5560)
    #dbg_value(i8 -1, !5547, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5562)
    #dbg_value(ptr %1, !107, !DIExpression(), !5562)
    #dbg_value(i16 -1, !108, !DIExpression(), !5562)
  br label %19, !dbg !5566

5:                                                ; preds = %3
    #dbg_value(i32 305419896, !5549, !DIExpression(), !5560)
    #dbg_value(i16 22136, !5548, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5567)
    #dbg_value(ptr %1, !107, !DIExpression(), !5567)
    #dbg_value(i16 22136, !108, !DIExpression(), !5567)
  br label %19, !dbg !5571

6:                                                ; preds = %3
    #dbg_value(i16 4660, !5548, !DIExpression(), !5560)
    #dbg_value(i8 52, !5547, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5572)
    #dbg_value(ptr %1, !107, !DIExpression(), !5572)
    #dbg_value(i16 52, !108, !DIExpression(), !5572)
  br label %19, !dbg !5576

7:                                                ; preds = %3
    #dbg_value(i8 -1, !5547, !DIExpression(), !5560)
    #dbg_value(i16 -1, !5548, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5577)
    #dbg_value(ptr %1, !107, !DIExpression(), !5577)
    #dbg_value(i16 -1, !108, !DIExpression(), !5577)
  br label %19, !dbg !5581

8:                                                ; preds = %3
    #dbg_value(i16 -1, !5548, !DIExpression(), !5560)
    #dbg_value(i32 -1, !5549, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5582)
    #dbg_value(ptr %1, !107, !DIExpression(), !5582)
    #dbg_value(i16 -1, !108, !DIExpression(), !5582)
  br label %19, !dbg !5586

9:                                                ; preds = %3
    #dbg_value(i8 -128, !5547, !DIExpression(), !5560)
    #dbg_value(i16 -128, !5548, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5587)
    #dbg_value(ptr %1, !107, !DIExpression(), !5587)
    #dbg_value(i16 -128, !108, !DIExpression(), !5587)
  br label %19, !dbg !5591

10:                                               ; preds = %3
    #dbg_value(i8 10, !5547, !DIExpression(), !5560)
    #dbg_value(i16 20, !5548, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5592)
    #dbg_value(ptr %1, !107, !DIExpression(), !5592)
    #dbg_value(i16 30, !108, !DIExpression(), !5592)
  br label %19, !dbg !5596

11:                                               ; preds = %3
    #dbg_value(i8 16, !5547, !DIExpression(), !5560)
    #dbg_value(i8 16, !5550, !DIExpression(), !5597)
    #dbg_value(ptr %0, !106, !DIExpression(), !5598)
    #dbg_value(ptr %1, !107, !DIExpression(), !5598)
    #dbg_value(i16 256, !108, !DIExpression(), !5598)
  br label %19

12:                                               ; preds = %3
    #dbg_value(i16 100, !5548, !DIExpression(), !5560)
    #dbg_value(i8 7, !5547, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5600)
    #dbg_value(ptr %1, !107, !DIExpression(), !5600)
    #dbg_value(i16 14, !108, !DIExpression(), !5600)
  br label %19, !dbg !5604

13:                                               ; preds = %3
    #dbg_value(i16 200, !5553, !DIExpression(), !5605)
    #dbg_value(i16 100, !5556, !DIExpression(), !5605)
    #dbg_value(i8 44, !5547, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5606)
    #dbg_value(ptr %1, !107, !DIExpression(), !5606)
    #dbg_value(i16 44, !108, !DIExpression(), !5606)
  br label %19

14:                                               ; preds = %3
    #dbg_value(i8 10, !5547, !DIExpression(), !5560)
    #dbg_value(i16 20, !5548, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5608)
    #dbg_value(ptr %1, !107, !DIExpression(), !5608)
    #dbg_value(i16 1, !108, !DIExpression(), !5608)
  br label %19, !dbg !5612

15:                                               ; preds = %3
    #dbg_value(i8 2, !5547, !DIExpression(), !5560)
  store i16 42, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 4), align 4, !dbg !5613, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5616)
    #dbg_value(ptr %1, !107, !DIExpression(), !5616)
    #dbg_value(i16 42, !108, !DIExpression(), !5616)
  br label %19, !dbg !5618

16:                                               ; preds = %3
    #dbg_value(i16 1000, !5548, !DIExpression(), !5560)
    #dbg_value(i16 -14, !5557, !DIExpression(), !5619)
    #dbg_value(ptr %0, !106, !DIExpression(), !5620)
    #dbg_value(ptr %1, !107, !DIExpression(), !5620)
    #dbg_value(i16 -14, !108, !DIExpression(), !5620)
  br label %19

17:                                               ; preds = %3
    #dbg_value(i16 4660, !5548, !DIExpression(), !5560)
    #dbg_value(i8 52, !5547, !DIExpression(), !5560)
    #dbg_value(ptr %0, !106, !DIExpression(), !5622)
    #dbg_value(ptr %1, !107, !DIExpression(), !5622)
    #dbg_value(i16 52, !108, !DIExpression(), !5622)
  br label %19, !dbg !5626

18:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5627)
    #dbg_value(ptr %1, !107, !DIExpression(), !5627)
    #dbg_value(i16 -1, !108, !DIExpression(), !5627)
  br label %19, !dbg !5629

19:                                               ; preds = %3, %18, %17, %16, %15, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %20 = phi i8 [ -1, %18 ], [ 0, %17 ], [ -1, %16 ], [ 0, %15 ], [ 0, %14 ], [ 0, %13 ], [ 0, %12 ], [ 1, %11 ], [ 0, %10 ], [ -1, %9 ], [ -1, %8 ], [ -1, %7 ], [ 0, %6 ], [ 86, %5 ], [ -1, %4 ], [ %2, %3 ]
  %21 = phi i8 [ -1, %18 ], [ 52, %17 ], [ -14, %16 ], [ 42, %15 ], [ 1, %14 ], [ 44, %13 ], [ 14, %12 ], [ 0, %11 ], [ 30, %10 ], [ -128, %9 ], [ -1, %8 ], [ -1, %7 ], [ 52, %6 ], [ 120, %5 ], [ -1, %4 ], [ %2, %3 ]
  store i8 %20, ptr %1, align 1, !dbg !5630, !tbaa !113
  %22 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5631
  store i8 %21, ptr %22, align 1, !dbg !5632, !tbaa !113
  %23 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5633
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5634
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5635
  ret void, !dbg !5629
}

; Function Attrs: nounwind
define hidden void @test_array_bounds(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5636 {
    #dbg_value(ptr %0, !5638, !DIExpression(), !5643)
    #dbg_value(ptr %1, !5639, !DIExpression(), !5643)
    #dbg_value(i8 %2, !5640, !DIExpression(), !5643)
  switch i8 %2, label %105 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
    i8 5, label %31
    i8 6, label %55
    i8 7, label %75
    i8 8, label %87
    i8 9, label %88
  ], !dbg !5644

4:                                                ; preds = %3
  store i8 1, ptr @shared_fb, align 16, !dbg !5645, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5648)
    #dbg_value(ptr %1, !107, !DIExpression(), !5648)
    #dbg_value(i16 1, !108, !DIExpression(), !5648)
  store i8 0, ptr %1, align 1, !dbg !5650, !tbaa !113
  br label %106, !dbg !5651

5:                                                ; preds = %3
  store i8 1, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 7), align 1, !dbg !5652, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5655)
    #dbg_value(ptr %1, !107, !DIExpression(), !5655)
    #dbg_value(i16 1, !108, !DIExpression(), !5655)
  store i8 0, ptr %1, align 1, !dbg !5657, !tbaa !113
  br label %106, !dbg !5658

6:                                                ; preds = %3
  store i16 1000, ptr @g_shorts, align 16, !dbg !5659, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5662)
    #dbg_value(ptr %1, !107, !DIExpression(), !5662)
    #dbg_value(i16 1000, !108, !DIExpression(), !5662)
  store i8 3, ptr %1, align 1, !dbg !5664, !tbaa !113
  br label %106, !dbg !5665

7:                                                ; preds = %3
  store i16 1000, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 14), align 2, !dbg !5666, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5669)
    #dbg_value(ptr %1, !107, !DIExpression(), !5669)
    #dbg_value(i16 1000, !108, !DIExpression(), !5669)
  store i8 3, ptr %1, align 1, !dbg !5671, !tbaa !113
  br label %106, !dbg !5672

8:                                                ; preds = %3, %8
  %9 = phi i32 [ %14, %8 ], [ 0, %3 ]
  %10 = add nsw i32 %9, 1, !dbg !5673
  %11 = trunc i32 %10 to i8, !dbg !5679
  %12 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %9, !dbg !5680
  store i8 %11, ptr %12, align 1, !dbg !5681, !tbaa !113
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  %13 = shl i32 %10, 16, !dbg !5682
  %14 = ashr exact i32 %13, 16, !dbg !5682
  %15 = icmp slt i32 %14, 8, !dbg !5683
  br i1 %15, label %8, label %16, !dbg !5684, !llvm.loop !5685

16:                                               ; preds = %8, %16
  %17 = phi i32 [ %25, %16 ], [ 0, %8 ]
  %18 = phi i16 [ %22, %16 ], [ 0, %8 ]
    #dbg_value(i16 %18, !5642, !DIExpression(), !5643)
  %19 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %17, !dbg !5687
  %20 = load i8, ptr %19, align 1, !dbg !5687, !tbaa !113
  %21 = sext i8 %20 to i16, !dbg !5687
  %22 = add i16 %18, %21, !dbg !5691
    #dbg_value(i16 %22, !5642, !DIExpression(), !5643)
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  %23 = shl nsw i32 %17, 16, !dbg !5692
  %24 = add i32 %23, 65536, !dbg !5692
  %25 = ashr exact i32 %24, 16, !dbg !5692
  %26 = icmp slt i32 %25, 8, !dbg !5693
  br i1 %26, label %16, label %27, !dbg !5694, !llvm.loop !5695

27:                                               ; preds = %16
    #dbg_value(ptr %0, !106, !DIExpression(), !5697)
    #dbg_value(ptr %1, !107, !DIExpression(), !5697)
    #dbg_value(i16 %22, !108, !DIExpression(), !5697)
  %28 = lshr i16 %22, 8, !dbg !5699
  %29 = trunc nuw i16 %28 to i8, !dbg !5700
  store i8 %29, ptr %1, align 1, !dbg !5701, !tbaa !113
  %30 = trunc i16 %22 to i8, !dbg !5702
  br label %106, !dbg !5703

31:                                               ; preds = %3, %31
  %32 = phi i32 [ %35, %31 ], [ 0, %3 ]
    #dbg_value(i32 %32, !5641, !DIExpression(), !5643)
  %33 = trunc i32 %32 to i8, !dbg !5704
  %34 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %32, !dbg !5710
  store i8 %33, ptr %34, align 1, !dbg !5711, !tbaa !113
  %35 = add nuw nsw i32 %32, 1, !dbg !5712
    #dbg_value(i32 %35, !5641, !DIExpression(), !5643)
  %36 = icmp eq i32 %35, 8, !dbg !5713
  br i1 %36, label %37, label %31, !dbg !5714, !llvm.loop !5715

37:                                               ; preds = %31, %37
  %38 = phi i32 [ %46, %37 ], [ 0, %31 ]
  %39 = sub nsw i32 7, %38, !dbg !5717
  %40 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %39, !dbg !5721
  %41 = load i8, ptr %40, align 1, !dbg !5721, !tbaa !113
  %42 = sext i8 %41 to i16, !dbg !5721
  %43 = getelementptr inbounds [8 x i16], ptr @g_shorts, i32 0, i32 %38, !dbg !5722
  store i16 %42, ptr %43, align 2, !dbg !5723, !tbaa !3184
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  %44 = shl nsw i32 %38, 16, !dbg !5724
  %45 = add i32 %44, 65536, !dbg !5724
  %46 = ashr exact i32 %45, 16, !dbg !5724
  %47 = icmp slt i32 %46, 8, !dbg !5725
  br i1 %47, label %37, label %48, !dbg !5726, !llvm.loop !5727

48:                                               ; preds = %37
  %49 = load i16, ptr @g_shorts, align 16, !dbg !5729, !tbaa !3184
  %50 = load i16, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 14), align 2, !dbg !5730, !tbaa !3184
  %51 = add i16 %50, %49, !dbg !5731
    #dbg_value(ptr %0, !106, !DIExpression(), !5732)
    #dbg_value(ptr %1, !107, !DIExpression(), !5732)
    #dbg_value(i16 %51, !108, !DIExpression(), !5732)
  %52 = lshr i16 %51, 8, !dbg !5734
  %53 = trunc nuw i16 %52 to i8, !dbg !5735
  store i8 %53, ptr %1, align 1, !dbg !5736, !tbaa !113
  %54 = trunc i16 %51 to i8, !dbg !5737
  br label %106, !dbg !5738

55:                                               ; preds = %3
  store i16 1, ptr @g_shorts, align 16, !dbg !5739, !tbaa !3184
  store i16 1, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 2), align 2, !dbg !5742, !tbaa !3184
    #dbg_value(i16 2, !5641, !DIExpression(), !5643)
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  br label %56, !dbg !5743

56:                                               ; preds = %55, %56
  %57 = phi i32 [ 2, %55 ], [ %68, %56 ]
  %58 = add nsw i32 %57, -1, !dbg !5745
  %59 = getelementptr inbounds [8 x i16], ptr @g_shorts, i32 0, i32 %58, !dbg !5748
  %60 = load i16, ptr %59, align 2, !dbg !5748, !tbaa !3184
  %61 = add nsw i32 %57, -2, !dbg !5749
  %62 = getelementptr inbounds [8 x i16], ptr @g_shorts, i32 0, i32 %61, !dbg !5750
  %63 = load i16, ptr %62, align 2, !dbg !5750, !tbaa !3184
  %64 = add i16 %63, %60, !dbg !5751
  %65 = getelementptr inbounds [8 x i16], ptr @g_shorts, i32 0, i32 %57, !dbg !5752
  store i16 %64, ptr %65, align 2, !dbg !5753, !tbaa !3184
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  %66 = shl nsw i32 %57, 16, !dbg !5754
  %67 = add i32 %66, 65536, !dbg !5754
  %68 = ashr exact i32 %67, 16, !dbg !5754
  %69 = icmp slt i32 %68, 8, !dbg !5755
  br i1 %69, label %56, label %70, !dbg !5743, !llvm.loop !5756

70:                                               ; preds = %56
  %71 = load i16, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 14), align 2, !dbg !5758, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5759)
    #dbg_value(ptr %1, !107, !DIExpression(), !5759)
    #dbg_value(i16 %71, !108, !DIExpression(), !5759)
  %72 = lshr i16 %71, 8, !dbg !5761
  %73 = trunc nuw i16 %72 to i8, !dbg !5762
  store i8 %73, ptr %1, align 1, !dbg !5763, !tbaa !113
  %74 = trunc i16 %71 to i8, !dbg !5764
  br label %106, !dbg !5765

75:                                               ; preds = %3, %75
  %76 = phi i32 [ %81, %75 ], [ 0, %3 ]
  %77 = add nsw i32 %76, 1, !dbg !5766
  %78 = trunc i32 %77 to i8, !dbg !5772
  %79 = getelementptr inbounds [80 x i8], ptr @shared_fb, i32 0, i32 %76, !dbg !5773
  store i8 %78, ptr %79, align 1, !dbg !5774, !tbaa !113
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  %80 = shl i32 %77, 16, !dbg !5775
  %81 = ashr exact i32 %80, 16, !dbg !5775
  %82 = icmp slt i32 %81, 8, !dbg !5776
  br i1 %82, label %75, label %83, !dbg !5777, !llvm.loop !5778

83:                                               ; preds = %75
  %84 = load i32, ptr @shared_fb, align 16, !dbg !5780, !tbaa !113
  store i32 %84, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 2), align 2, !dbg !5780, !tbaa !113
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  %85 = load i8, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 4), align 4, !dbg !5784, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5785)
    #dbg_value(ptr %1, !107, !DIExpression(), !5785)
    #dbg_value(i8 %85, !108, !DIExpression(DW_OP_LLVM_convert, 8, DW_ATE_signed, DW_OP_LLVM_convert, 16, DW_ATE_signed, DW_OP_stack_value), !5785)
  %86 = ashr i8 %85, 7, !dbg !5787
  store i8 %86, ptr %1, align 1, !dbg !5788, !tbaa !113
  br label %106, !dbg !5789

87:                                               ; preds = %3
  store i8 5, ptr @shared_fb, align 16, !dbg !5790, !tbaa !113
  store i8 42, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 5), align 1, !dbg !5793, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5794)
    #dbg_value(ptr %1, !107, !DIExpression(), !5794)
    #dbg_value(i16 42, !108, !DIExpression(), !5794)
  store i8 0, ptr %1, align 1, !dbg !5796, !tbaa !113
  br label %106, !dbg !5797

88:                                               ; preds = %3
  store i16 1, ptr @g_shorts, align 16, !dbg !5798, !tbaa !3184
    #dbg_value(i16 1, !5641, !DIExpression(), !5643)
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  br label %89, !dbg !5801

89:                                               ; preds = %88, %89
  %90 = phi i32 [ 1, %88 ], [ %98, %89 ]
  %91 = add nsw i32 %90, -1, !dbg !5803
  %92 = getelementptr inbounds [8 x i16], ptr @g_shorts, i32 0, i32 %91, !dbg !5806
  %93 = load i16, ptr %92, align 2, !dbg !5806, !tbaa !3184
  %94 = shl i16 %93, 1, !dbg !5807
  %95 = getelementptr inbounds [8 x i16], ptr @g_shorts, i32 0, i32 %90, !dbg !5808
  store i16 %94, ptr %95, align 2, !dbg !5809, !tbaa !3184
    #dbg_value(i16 poison, !5641, !DIExpression(), !5643)
  %96 = shl nsw i32 %90, 16, !dbg !5810
  %97 = add i32 %96, 65536, !dbg !5810
  %98 = ashr exact i32 %97, 16, !dbg !5810
  %99 = icmp slt i32 %98, 8, !dbg !5811
  br i1 %99, label %89, label %100, !dbg !5801, !llvm.loop !5812

100:                                              ; preds = %89
  %101 = load i16, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 14), align 2, !dbg !5814, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5815)
    #dbg_value(ptr %1, !107, !DIExpression(), !5815)
    #dbg_value(i16 %101, !108, !DIExpression(), !5815)
  %102 = lshr i16 %101, 8, !dbg !5817
  %103 = trunc nuw i16 %102 to i8, !dbg !5818
  store i8 %103, ptr %1, align 1, !dbg !5819, !tbaa !113
  %104 = trunc i16 %101 to i8, !dbg !5820
  br label %106, !dbg !5821

105:                                              ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5822)
    #dbg_value(ptr %1, !107, !DIExpression(), !5822)
    #dbg_value(i16 -1, !108, !DIExpression(), !5822)
  store i8 -1, ptr %1, align 1, !dbg !5824, !tbaa !113
  br label %106, !dbg !5825

106:                                              ; preds = %105, %100, %87, %83, %70, %48, %27, %7, %6, %5, %4
  %107 = phi i8 [ -1, %105 ], [ %104, %100 ], [ 42, %87 ], [ %85, %83 ], [ %74, %70 ], [ %54, %48 ], [ %30, %27 ], [ -24, %7 ], [ -24, %6 ], [ 1, %5 ], [ 1, %4 ]
  %108 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5826
  store i8 %107, ptr %108, align 1, !dbg !5827, !tbaa !113
  %109 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5828
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5829
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5830
  ret void, !dbg !5825
}

; Function Attrs: nounwind
define hidden void @test_global_array_ops(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5831 {
    #dbg_value(ptr %0, !5833, !DIExpression(), !5840)
    #dbg_value(ptr %1, !5834, !DIExpression(), !5840)
    #dbg_value(i8 %2, !5835, !DIExpression(), !5840)
  switch i8 %2, label %14 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
    i8 5, label %9
    i8 6, label %10
    i8 7, label %11
    i8 8, label %12
    i8 9, label %13
  ], !dbg !5841

4:                                                ; preds = %3
  store i8 42, ptr @g_byte, align 1, !dbg !5842, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5845)
    #dbg_value(ptr %1, !107, !DIExpression(), !5845)
    #dbg_value(i16 42, !108, !DIExpression(), !5845)
  br label %14, !dbg !5847

5:                                                ; preds = %3
  store i16 1000, ptr @g_short, align 2, !dbg !5848, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5851)
    #dbg_value(ptr %1, !107, !DIExpression(), !5851)
    #dbg_value(i16 1000, !108, !DIExpression(), !5851)
  br label %14, !dbg !5853

6:                                                ; preds = %3
  store i32 100000, ptr @g_int, align 4, !dbg !5854, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !5857)
    #dbg_value(ptr %1, !107, !DIExpression(), !5857)
    #dbg_value(i16 390, !108, !DIExpression(), !5857)
  br label %14, !dbg !5859

7:                                                ; preds = %3
  store i8 99, ptr getelementptr inbounds (i8, ptr @shared_fb, i32 5), align 1, !dbg !5860, !tbaa !113
    #dbg_value(ptr %0, !106, !DIExpression(), !5863)
    #dbg_value(ptr %1, !107, !DIExpression(), !5863)
    #dbg_value(i16 99, !108, !DIExpression(), !5863)
  br label %14, !dbg !5865

8:                                                ; preds = %3
    #dbg_value(i16 0, !5836, !DIExpression(), !5840)
    #dbg_value(i16 poison, !5836, !DIExpression(), !5840)
    #dbg_value(i16 poison, !5836, !DIExpression(), !5840)
  store i16 45, ptr @g_short, align 2, !dbg !5866, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5872)
    #dbg_value(ptr %1, !107, !DIExpression(), !5872)
    #dbg_value(i16 45, !108, !DIExpression(), !5872)
  br label %14, !dbg !5874

9:                                                ; preds = %3
  store i16 100, ptr @items, align 16, !dbg !5875, !tbaa !3322
  store i8 5, ptr getelementptr inbounds (i8, ptr @items, i32 2), align 2, !dbg !5878, !tbaa !3331
    #dbg_value(ptr %0, !106, !DIExpression(), !5879)
    #dbg_value(ptr %1, !107, !DIExpression(), !5879)
    #dbg_value(i16 105, !108, !DIExpression(), !5879)
  br label %14, !dbg !5881

10:                                               ; preds = %3
    #dbg_value(i16 10, !5837, !DIExpression(), !5882)
  store i16 20, ptr @g_short, align 2, !dbg !5883, !tbaa !3184
    #dbg_value(i16 20, !5837, !DIExpression(), !5882)
    #dbg_value(ptr %0, !106, !DIExpression(), !5884)
    #dbg_value(ptr %1, !107, !DIExpression(), !5884)
    #dbg_value(i16 1, !108, !DIExpression(), !5884)
  br label %14

11:                                               ; preds = %3
    #dbg_value(i16 1, !5836, !DIExpression(), !5840)
    #dbg_value(i16 poison, !5836, !DIExpression(), !5840)
    #dbg_value(i16 poison, !5836, !DIExpression(), !5840)
  store i16 55, ptr @g_shorts, align 16, !dbg !5886, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5892)
    #dbg_value(ptr %1, !107, !DIExpression(), !5892)
    #dbg_value(i16 55, !108, !DIExpression(), !5892)
  br label %14, !dbg !5894

12:                                               ; preds = %3
  store i8 1, ptr @g_byte, align 1, !dbg !5895, !tbaa !113
  store i16 10, ptr @g_short, align 2, !dbg !5898, !tbaa !3184
  store i8 2, ptr @g_byte, align 1, !dbg !5899, !tbaa !113
  store i16 20, ptr @g_short, align 2, !dbg !5900, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !5901)
    #dbg_value(ptr %1, !107, !DIExpression(), !5901)
    #dbg_value(i16 22, !108, !DIExpression(), !5901)
  br label %14, !dbg !5903

13:                                               ; preds = %3
  store i32 12345, ptr @g_ints, align 16, !dbg !5904, !tbaa !3191
    #dbg_value(ptr %0, !106, !DIExpression(), !5907)
    #dbg_value(ptr %1, !107, !DIExpression(), !5907)
    #dbg_value(i16 123, !108, !DIExpression(), !5907)
  br label %14, !dbg !5909

14:                                               ; preds = %3, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %15 = phi i8 [ 0, %13 ], [ 0, %12 ], [ 0, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 1, %6 ], [ 3, %5 ], [ 0, %4 ], [ -1, %3 ]
  %16 = phi i8 [ 123, %13 ], [ 22, %12 ], [ 55, %11 ], [ 1, %10 ], [ 105, %9 ], [ 45, %8 ], [ 99, %7 ], [ -122, %6 ], [ -24, %5 ], [ 42, %4 ], [ -1, %3 ]
  store i8 %15, ptr %1, align 1, !dbg !5910, !tbaa !113
  %17 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5911
  store i8 %16, ptr %17, align 1, !dbg !5912, !tbaa !113
  %18 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5913
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5914
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !5915
  ret void, !dbg !5916
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define hidden noundef signext i16 @ternary_func1() local_unnamed_addr #2 !dbg !5917 {
  ret i16 10, !dbg !5918
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define hidden noundef signext i16 @ternary_func2() local_unnamed_addr #2 !dbg !5919 {
  ret i16 20, !dbg !5920
}

; Function Attrs: nounwind
define hidden void @test_ternary_patterns(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !5921 {
    #dbg_value(ptr %0, !5923, !DIExpression(), !5959)
    #dbg_value(ptr %1, !5924, !DIExpression(), !5959)
    #dbg_value(i8 %2, !5925, !DIExpression(), !5959)
    #dbg_value(i16 15, !5926, !DIExpression(), !5959)
    #dbg_value(i16 10, !5927, !DIExpression(), !5959)
  switch i8 %2, label %13 [
    i8 0, label %14
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %10
    i8 8, label %11
    i8 9, label %12
  ], !dbg !5960

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5961)
    #dbg_value(ptr %1, !107, !DIExpression(), !5961)
    #dbg_value(i16 10, !108, !DIExpression(), !5961)
  br label %14, !dbg !5965

5:                                                ; preds = %3
    #dbg_value(i16 -5, !5928, !DIExpression(), !5966)
    #dbg_value(ptr %0, !106, !DIExpression(), !5967)
    #dbg_value(ptr %1, !107, !DIExpression(), !5967)
    #dbg_value(i16 5, !108, !DIExpression(), !5967)
  br label %14

6:                                                ; preds = %3
    #dbg_value(i16 -5, !5931, !DIExpression(), !5969)
    #dbg_value(ptr %0, !106, !DIExpression(), !5970)
    #dbg_value(ptr %1, !107, !DIExpression(), !5970)
    #dbg_value(i16 -1, !108, !DIExpression(), !5970)
  br label %14

7:                                                ; preds = %3
    #dbg_value(i16 1, !5934, !DIExpression(), !5972)
    #dbg_value(ptr %0, !106, !DIExpression(), !5973)
    #dbg_value(ptr %1, !107, !DIExpression(), !5973)
    #dbg_value(i16 10, !108, !DIExpression(), !5973)
  br label %14

8:                                                ; preds = %3
  store i16 100, ptr @g_shorts, align 16, !dbg !5975, !tbaa !3184
  store i16 200, ptr getelementptr inbounds (i8, ptr @g_shorts, i32 2), align 2, !dbg !5976, !tbaa !3184
    #dbg_value(i16 0, !5937, !DIExpression(), !5977)
    #dbg_value(i16 0, !5940, !DIExpression(), !5977)
    #dbg_value(i16 1, !5941, !DIExpression(), !5977)
    #dbg_value(ptr %0, !106, !DIExpression(), !5978)
    #dbg_value(ptr %1, !107, !DIExpression(), !5978)
    #dbg_value(i16 200, !108, !DIExpression(), !5978)
  br label %14

9:                                                ; preds = %3
    #dbg_value(i16 5, !5942, !DIExpression(), !5980)
    #dbg_value(i16 3, !5945, !DIExpression(), !5980)
    #dbg_value(ptr %0, !106, !DIExpression(), !5981)
    #dbg_value(ptr %1, !107, !DIExpression(), !5981)
    #dbg_value(i16 1, !108, !DIExpression(), !5981)
  br label %14

10:                                               ; preds = %3
    #dbg_value(i16 100, !5946, !DIExpression(), !5983)
    #dbg_value(i16 50, !5949, !DIExpression(), !5983)
    #dbg_value(i16 50, !5946, !DIExpression(), !5983)
    #dbg_value(ptr %0, !106, !DIExpression(), !5984)
    #dbg_value(ptr %1, !107, !DIExpression(), !5984)
    #dbg_value(i16 50, !108, !DIExpression(), !5984)
  br label %14

11:                                               ; preds = %3
    #dbg_value(i16 5, !5950, !DIExpression(), !5986)
    #dbg_value(i16 10, !5953, !DIExpression(), !5986)
    #dbg_value(i16 10, !5950, !DIExpression(), !5986)
    #dbg_value(ptr %0, !106, !DIExpression(), !5987)
    #dbg_value(ptr %1, !107, !DIExpression(), !5987)
    #dbg_value(i16 10, !108, !DIExpression(), !5987)
  br label %14

12:                                               ; preds = %3
    #dbg_value(i16 1, !5954, !DIExpression(), !5989)
    #dbg_value(i16 15, !5957, !DIExpression(), !5989)
    #dbg_value(i16 240, !5958, !DIExpression(), !5989)
    #dbg_value(i16 255, !5957, !DIExpression(), !5989)
    #dbg_value(ptr %0, !106, !DIExpression(), !5990)
    #dbg_value(ptr %1, !107, !DIExpression(), !5990)
    #dbg_value(i16 255, !108, !DIExpression(), !5990)
  br label %14

13:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !5992)
    #dbg_value(ptr %1, !107, !DIExpression(), !5992)
    #dbg_value(i16 -1, !108, !DIExpression(), !5992)
  br label %14, !dbg !5994

14:                                               ; preds = %3, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %15 = phi i8 [ -1, %13 ], [ 0, %12 ], [ 0, %11 ], [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ -1, %6 ], [ 0, %5 ], [ 0, %4 ], [ %2, %3 ]
  %16 = phi i8 [ -1, %13 ], [ -1, %12 ], [ 10, %11 ], [ 50, %10 ], [ 1, %9 ], [ -56, %8 ], [ 10, %7 ], [ -1, %6 ], [ 5, %5 ], [ 10, %4 ], [ 15, %3 ]
  store i8 %15, ptr %1, align 1, !dbg !5995, !tbaa !113
  %17 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !5996
  store i8 %16, ptr %17, align 1, !dbg !5997, !tbaa !113
  %18 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !5998
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !5999
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !6000
  ret void, !dbg !5994
}

; Function Attrs: nounwind
define hidden void @test_mul_div_edge(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !6001 {
    #dbg_value(ptr %0, !6003, !DIExpression(), !6008)
    #dbg_value(ptr %1, !6004, !DIExpression(), !6008)
    #dbg_value(i8 %2, !6005, !DIExpression(), !6008)
  switch i8 %2, label %15 [
    i8 0, label %16
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
    i8 11, label %14
  ], !dbg !6009

4:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !6010)
    #dbg_value(ptr %1, !107, !DIExpression(), !6010)
    #dbg_value(i16 -25536, !108, !DIExpression(), !6010)
  br label %16, !dbg !6014

5:                                                ; preds = %3
    #dbg_value(i16 300, !6006, !DIExpression(), !6008)
    #dbg_value(i16 300, !6007, !DIExpression(), !6008)
    #dbg_value(ptr %0, !106, !DIExpression(), !6015)
    #dbg_value(ptr %1, !107, !DIExpression(), !6015)
    #dbg_value(i16 24464, !108, !DIExpression(), !6015)
  br label %16, !dbg !6019

6:                                                ; preds = %3
    #dbg_value(i16 -10, !6006, !DIExpression(), !6008)
    #dbg_value(i16 5, !6007, !DIExpression(), !6008)
    #dbg_value(ptr %0, !106, !DIExpression(), !6020)
    #dbg_value(ptr %1, !107, !DIExpression(), !6020)
    #dbg_value(i16 -50, !108, !DIExpression(), !6020)
  br label %16, !dbg !6024

7:                                                ; preds = %3
    #dbg_value(i16 -10, !6006, !DIExpression(), !6008)
    #dbg_value(i16 -5, !6007, !DIExpression(), !6008)
    #dbg_value(ptr %0, !106, !DIExpression(), !6025)
    #dbg_value(ptr %1, !107, !DIExpression(), !6025)
    #dbg_value(i16 50, !108, !DIExpression(), !6025)
  br label %16, !dbg !6029

8:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !6030)
    #dbg_value(ptr %1, !107, !DIExpression(), !6030)
    #dbg_value(i16 14, !108, !DIExpression(), !6030)
  br label %16, !dbg !6034

9:                                                ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !6035)
    #dbg_value(ptr %1, !107, !DIExpression(), !6035)
    #dbg_value(i16 2, !108, !DIExpression(), !6035)
  br label %16, !dbg !6039

10:                                               ; preds = %3
    #dbg_value(i16 -100, !6006, !DIExpression(), !6008)
    #dbg_value(i16 7, !6007, !DIExpression(), !6008)
    #dbg_value(ptr %0, !106, !DIExpression(), !6040)
    #dbg_value(ptr %1, !107, !DIExpression(), !6040)
    #dbg_value(i16 -14, !108, !DIExpression(), !6040)
  br label %16, !dbg !6044

11:                                               ; preds = %3
    #dbg_value(i16 -100, !6006, !DIExpression(), !6008)
    #dbg_value(i16 7, !6007, !DIExpression(), !6008)
    #dbg_value(ptr %0, !106, !DIExpression(), !6045)
    #dbg_value(ptr %1, !107, !DIExpression(), !6045)
    #dbg_value(i16 -2, !108, !DIExpression(), !6045)
  br label %16, !dbg !6049

12:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !6050)
    #dbg_value(ptr %1, !107, !DIExpression(), !6050)
    #dbg_value(i16 0, !108, !DIExpression(), !6050)
  br label %16, !dbg !6054

13:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !6055)
    #dbg_value(ptr %1, !107, !DIExpression(), !6055)
    #dbg_value(i16 5, !108, !DIExpression(), !6055)
  br label %16, !dbg !6059

14:                                               ; preds = %3
    #dbg_value(i16 32767, !6006, !DIExpression(), !6008)
    #dbg_value(ptr %0, !106, !DIExpression(), !6060)
    #dbg_value(ptr %1, !107, !DIExpression(), !6060)
    #dbg_value(i16 -2, !108, !DIExpression(), !6060)
  br label %16, !dbg !6064

15:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !6065)
    #dbg_value(ptr %1, !107, !DIExpression(), !6065)
    #dbg_value(i16 -1, !108, !DIExpression(), !6065)
  br label %16, !dbg !6067

16:                                               ; preds = %3, %15, %14, %13, %12, %11, %10, %9, %8, %7, %6, %5, %4
  %17 = phi i8 [ -1, %15 ], [ -1, %14 ], [ 0, %13 ], [ 0, %12 ], [ -1, %11 ], [ -1, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ -1, %6 ], [ 95, %5 ], [ -100, %4 ], [ %2, %3 ]
  %18 = phi i8 [ -1, %15 ], [ -2, %14 ], [ 5, %13 ], [ 0, %12 ], [ -2, %11 ], [ -14, %10 ], [ 2, %9 ], [ 14, %8 ], [ 50, %7 ], [ -50, %6 ], [ -112, %5 ], [ 64, %4 ], [ 77, %3 ]
  %19 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !6068
  store i8 %17, ptr %1, align 1, !dbg !6069, !tbaa !113
  store i8 %18, ptr %19, align 1, !dbg !6070, !tbaa !113
  %20 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !6071
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !6072
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !6073
  ret void, !dbg !6067
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define hidden signext range(i16 0, -32768) i16 @lcg_next() local_unnamed_addr #5 !dbg !6074 {
  %1 = load i16, ptr @g_rng_seed, align 2, !dbg !6075, !tbaa !3184
  %2 = mul i16 %1, 25173, !dbg !6076
  %3 = add i16 %2, 13849, !dbg !6077
  %4 = and i16 %3, 32767, !dbg !6078
  store i16 %4, ptr @g_rng_seed, align 2, !dbg !6079, !tbaa !3184
  ret i16 %4, !dbg !6080
}

; Function Attrs: nounwind
define hidden void @test_rng(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !6081 {
    #dbg_value(ptr %0, !6083, !DIExpression(), !6108)
    #dbg_value(ptr %1, !6084, !DIExpression(), !6108)
    #dbg_value(i8 %2, !6085, !DIExpression(), !6108)
  switch i8 %2, label %15 [
    i8 0, label %11
    i8 1, label %4
    i8 2, label %5
    i8 3, label %6
    i8 4, label %7
    i8 5, label %8
    i8 6, label %9
    i8 7, label %10
  ], !dbg !6109

4:                                                ; preds = %3
    #dbg_value(i16 0, !6086, !DIExpression(), !6108)
    #dbg_value(i16 poison, !6086, !DIExpression(), !6108)
    #dbg_value(i16 poison, !6086, !DIExpression(), !6108)
    #dbg_value(ptr %0, !106, !DIExpression(), !6110)
    #dbg_value(ptr %1, !107, !DIExpression(), !6110)
    #dbg_value(i16 20919, !108, !DIExpression(DW_OP_constu, 32767, DW_OP_and, DW_OP_stack_value), !6110)
  br label %11, !dbg !6114

5:                                                ; preds = %3
    #dbg_value(i16 6254, !6087, !DIExpression(), !6115)
    #dbg_value(ptr %0, !106, !DIExpression(), !6116)
    #dbg_value(ptr %1, !107, !DIExpression(), !6116)
    #dbg_value(i16 24, !108, !DIExpression(), !6116)
  br label %11

6:                                                ; preds = %3
    #dbg_value(i16 6254, !6090, !DIExpression(), !6118)
    #dbg_value(ptr %0, !106, !DIExpression(), !6119)
    #dbg_value(ptr %1, !107, !DIExpression(), !6119)
    #dbg_value(i16 4, !108, !DIExpression(), !6119)
  br label %11

7:                                                ; preds = %3
    #dbg_value(i16 6254, !6093, !DIExpression(), !6121)
    #dbg_value(i16 5, !6096, !DIExpression(), !6121)
    #dbg_value(i16 15, !6097, !DIExpression(), !6121)
    #dbg_value(ptr %0, !106, !DIExpression(), !6122)
    #dbg_value(ptr %1, !107, !DIExpression(), !6122)
    #dbg_value(i16 9, !108, !DIExpression(), !6122)
  br label %11

8:                                                ; preds = %3
    #dbg_value(i16 6254, !6098, !DIExpression(), !6124)
    #dbg_value(ptr %0, !106, !DIExpression(), !6125)
    #dbg_value(ptr %1, !107, !DIExpression(), !6125)
    #dbg_value(i16 0, !108, !DIExpression(), !6125)
  br label %11

9:                                                ; preds = %3
    #dbg_value(i16 6254, !6101, !DIExpression(), !6127)
    #dbg_value(ptr %0, !106, !DIExpression(), !6128)
    #dbg_value(ptr %1, !107, !DIExpression(), !6128)
    #dbg_value(i16 0, !108, !DIExpression(), !6128)
  br label %11

10:                                               ; preds = %3
    #dbg_value(i16 22539, !6104, !DIExpression(), !6130)
    #dbg_value(i16 22539, !6107, !DIExpression(), !6130)
    #dbg_value(ptr %0, !106, !DIExpression(), !6131)
    #dbg_value(ptr %1, !107, !DIExpression(), !6131)
    #dbg_value(i16 1, !108, !DIExpression(), !6131)
  br label %11

11:                                               ; preds = %3, %4, %5, %6, %7, %8, %9, %10
  %12 = phi i16 [ 22539, %10 ], [ 6254, %9 ], [ 6254, %8 ], [ 6254, %7 ], [ 6254, %6 ], [ 6254, %5 ], [ 20919, %4 ], [ 6254, %3 ]
  %13 = phi i8 [ 0, %10 ], [ 0, %9 ], [ 0, %8 ], [ 0, %7 ], [ 0, %6 ], [ 0, %5 ], [ 81, %4 ], [ 24, %3 ]
  %14 = phi i8 [ 1, %10 ], [ 0, %9 ], [ 0, %8 ], [ 9, %7 ], [ 4, %6 ], [ 24, %5 ], [ -73, %4 ], [ 110, %3 ]
  store i16 %12, ptr @g_rng_seed, align 2, !dbg !6133, !tbaa !3184
  br label %15, !dbg !6134

15:                                               ; preds = %11, %3
  %16 = phi i8 [ -1, %3 ], [ %13, %11 ]
  %17 = phi i8 [ -1, %3 ], [ %14, %11 ]
  store i8 %16, ptr %1, align 1, !dbg !6134, !tbaa !113
  %18 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !6135
  store i8 %17, ptr %18, align 1, !dbg !6136, !tbaa !113
  %19 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !6137
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !6138
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !6139
  ret void, !dbg !6140
}

; Function Attrs: nounwind
define hidden void @test_state_machine(ptr noundef %0, ptr nocapture noundef writeonly %1, i8 noundef signext %2) local_unnamed_addr #0 !dbg !6141 {
    #dbg_value(ptr %0, !6143, !DIExpression(), !6161)
    #dbg_value(ptr %1, !6144, !DIExpression(), !6161)
    #dbg_value(i8 %2, !6145, !DIExpression(), !6161)
  switch i8 %2, label %28 [
    i8 0, label %4
    i8 1, label %5
    i8 2, label %6
    i8 3, label %7
    i8 4, label %8
    i8 5, label %9
    i8 6, label %10
    i8 7, label %11
  ], !dbg !6162

4:                                                ; preds = %3
  store i16 0, ptr @g_state, align 2, !dbg !6163, !tbaa !3184
    #dbg_value(ptr %0, !106, !DIExpression(), !6166)
    #dbg_value(ptr %1, !107, !DIExpression(), !6166)
    #dbg_value(i16 0, !108, !DIExpression(), !6166)
  store i8 0, ptr %1, align 1, !dbg !6168, !tbaa !113
  br label %29, !dbg !6169

5:                                                ; preds = %3
  store i16 1, ptr @g_state, align 2, !dbg !6170
    #dbg_value(ptr %0, !106, !DIExpression(), !6173)
    #dbg_value(ptr %1, !107, !DIExpression(), !6173)
    #dbg_value(i16 1, !108, !DIExpression(), !6173)
  store i8 0, ptr %1, align 1, !dbg !6175, !tbaa !113
  br label %29, !dbg !6176

6:                                                ; preds = %3
  store i16 2, ptr @g_state, align 2, !dbg !6177
    #dbg_value(ptr %0, !106, !DIExpression(), !6180)
    #dbg_value(ptr %1, !107, !DIExpression(), !6180)
    #dbg_value(i16 2, !108, !DIExpression(), !6180)
  store i8 0, ptr %1, align 1, !dbg !6182, !tbaa !113
  br label %29, !dbg !6183

7:                                                ; preds = %3
  store i16 0, ptr @g_state, align 2, !dbg !6184, !tbaa !3184
    #dbg_value(i16 0, !6146, !DIExpression(), !6185)
    #dbg_value(ptr %0, !106, !DIExpression(), !6186)
    #dbg_value(ptr %1, !107, !DIExpression(), !6186)
    #dbg_value(i16 1, !108, !DIExpression(), !6186)
  store i8 0, ptr %1, align 1, !dbg !6188, !tbaa !113
  br label %29

8:                                                ; preds = %3
  store i16 1, ptr @g_state, align 2, !dbg !6189, !tbaa !3184
    #dbg_value(i16 0, !6149, !DIExpression(), !6190)
    #dbg_value(i16 0, !6149, !DIExpression(), !6190)
    #dbg_value(i16 20, !6149, !DIExpression(), !6190)
    #dbg_value(i16 20, !6149, !DIExpression(), !6190)
    #dbg_value(ptr %0, !106, !DIExpression(), !6191)
    #dbg_value(ptr %1, !107, !DIExpression(), !6191)
    #dbg_value(i16 20, !108, !DIExpression(), !6191)
  store i8 0, ptr %1, align 1, !dbg !6193, !tbaa !113
  br label %29

9:                                                ; preds = %3
  store i16 2, ptr @g_state, align 2, !dbg !6194, !tbaa !3184
    #dbg_value(i16 300, !6152, !DIExpression(), !6195)
    #dbg_value(i16 300, !6152, !DIExpression(), !6195)
    #dbg_value(ptr %0, !106, !DIExpression(), !6196)
    #dbg_value(ptr %1, !107, !DIExpression(), !6196)
    #dbg_value(i16 300, !108, !DIExpression(), !6196)
  store i8 1, ptr %1, align 1, !dbg !6198, !tbaa !113
  br label %29

10:                                               ; preds = %3
  store i16 1, ptr @g_state, align 2, !dbg !6199, !tbaa !3184
    #dbg_value(i16 200, !6155, !DIExpression(), !6200)
    #dbg_value(i16 200, !6155, !DIExpression(), !6200)
    #dbg_value(ptr %0, !106, !DIExpression(), !6201)
    #dbg_value(ptr %1, !107, !DIExpression(), !6201)
    #dbg_value(i16 200, !108, !DIExpression(), !6201)
  store i8 0, ptr %1, align 1, !dbg !6203, !tbaa !113
  br label %29

11:                                               ; preds = %3
  store i16 1, ptr @g_state, align 2, !dbg !6204, !tbaa !3184
  store i16 0, ptr @g_frame, align 2, !dbg !6205, !tbaa !3184
    #dbg_value(i16 0, !6158, !DIExpression(), !6206)
    #dbg_value(i16 poison, !6158, !DIExpression(), !6206)
  br label %12, !dbg !6207

12:                                               ; preds = %11, %18
  %13 = phi i32 [ 0, %11 ], [ %19, %18 ]
  %14 = phi i16 [ 0, %11 ], [ %15, %18 ]
  %15 = add nuw nsw i16 %14, 1, !dbg !6209
  %16 = icmp eq i16 %15, 5, !dbg !6212
  br i1 %16, label %17, label %18, !dbg !6214

17:                                               ; preds = %12
  store i16 2, ptr @g_state, align 2, !dbg !6215, !tbaa !3184
  br label %18, !dbg !6217

18:                                               ; preds = %12, %17
    #dbg_value(i16 poison, !6158, !DIExpression(), !6206)
  %19 = add nuw nsw i32 %13, 65536, !dbg !6218
  %20 = icmp ult i32 %13, 589824, !dbg !6219
  br i1 %20, label %12, label %21, !dbg !6207, !llvm.loop !6220

21:                                               ; preds = %18
  store i16 10, ptr @g_frame, align 2, !dbg !6222, !tbaa !3184
  %22 = load i16, ptr @g_state, align 2, !dbg !6223, !tbaa !3184
  %23 = mul i16 %22, 10, !dbg !6224
  %24 = add i16 %23, 10, !dbg !6225
    #dbg_value(ptr %0, !106, !DIExpression(), !6226)
    #dbg_value(ptr %1, !107, !DIExpression(), !6226)
    #dbg_value(i16 %24, !108, !DIExpression(), !6226)
  %25 = lshr i16 %24, 8, !dbg !6228
  %26 = trunc nuw i16 %25 to i8, !dbg !6229
  store i8 %26, ptr %1, align 1, !dbg !6230, !tbaa !113
  %27 = trunc i16 %24 to i8, !dbg !6231
  br label %29

28:                                               ; preds = %3
    #dbg_value(ptr %0, !106, !DIExpression(), !6232)
    #dbg_value(ptr %1, !107, !DIExpression(), !6232)
    #dbg_value(i16 -1, !108, !DIExpression(), !6232)
  store i8 -1, ptr %1, align 1, !dbg !6234, !tbaa !113
  br label %29, !dbg !6235

29:                                               ; preds = %28, %21, %10, %9, %8, %7, %6, %5, %4
  %30 = phi i8 [ -1, %28 ], [ %27, %21 ], [ -56, %10 ], [ 44, %9 ], [ 20, %8 ], [ 1, %7 ], [ 2, %6 ], [ 1, %5 ], [ 0, %4 ]
  %31 = getelementptr inbounds i8, ptr %1, i32 1, !dbg !6236
  store i8 %30, ptr %31, align 1, !dbg !6237, !tbaa !113
  %32 = tail call signext i16 @jc_APDU_setOutgoing(ptr noundef %0) #11, !dbg !6238
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %0, i16 noundef signext 2) #11, !dbg !6239
  tail call void @jc_APDU_sendBytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #11, !dbg !6240
  ret void, !dbg !6235
}

; Function Attrs: nounwind
define hidden void @process(ptr noundef %0, i16 noundef signext %1) local_unnamed_addr #0 !dbg !6241 {
    #dbg_value(ptr %0, !6243, !DIExpression(), !6248)
    #dbg_value(i16 %1, !6244, !DIExpression(), !6248)
  %3 = tail call ptr @jc_APDU_getBuffer(ptr noundef %0) #11, !dbg !6249
    #dbg_value(ptr %3, !6245, !DIExpression(), !6248)
  %4 = getelementptr inbounds i8, ptr %3, i32 1, !dbg !6250
  %5 = load i8, ptr %4, align 1, !dbg !6250, !tbaa !113
    #dbg_value(i8 %5, !6246, !DIExpression(), !6248)
  %6 = getelementptr inbounds i8, ptr %3, i32 2, !dbg !6251
  %7 = load i8, ptr %6, align 1, !dbg !6251, !tbaa !113
    #dbg_value(i8 %7, !6247, !DIExpression(), !6248)
  switch i8 %5, label %64 [
    i8 1, label %8
    i8 2, label %9
    i8 3, label %10
    i8 4, label %11
    i8 5, label %12
    i8 6, label %13
    i8 7, label %14
    i8 8, label %15
    i8 9, label %16
    i8 10, label %17
    i8 11, label %18
    i8 12, label %19
    i8 13, label %20
    i8 14, label %21
    i8 15, label %22
    i8 16, label %23
    i8 17, label %24
    i8 18, label %25
    i8 19, label %26
    i8 20, label %27
    i8 32, label %28
    i8 33, label %29
    i8 34, label %30
    i8 35, label %31
    i8 36, label %32
    i8 37, label %33
    i8 38, label %34
    i8 39, label %35
    i8 40, label %36
    i8 41, label %37
    i8 42, label %38
    i8 43, label %39
    i8 44, label %40
    i8 48, label %41
    i8 49, label %42
    i8 50, label %43
    i8 51, label %44
    i8 52, label %45
    i8 53, label %46
    i8 54, label %47
    i8 55, label %48
    i8 56, label %49
    i8 57, label %50
    i8 58, label %51
    i8 59, label %52
    i8 60, label %53
    i8 61, label %54
    i8 62, label %55
    i8 63, label %56
    i8 64, label %57
    i8 65, label %58
    i8 80, label %59
    i8 81, label %60
    i8 82, label %61
    i8 83, label %62
    i8 84, label %63
  ], !dbg !6252

8:                                                ; preds = %2
  tail call void @test_arithmetic(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6253
  br label %65, !dbg !6256

9:                                                ; preds = %2
  tail call void @test_bitwise(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6257
  br label %65, !dbg !6260

10:                                               ; preds = %2
  tail call void @test_comparison(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6261
  br label %65, !dbg !6264

11:                                               ; preds = %2
  tail call void @test_logical(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6265
  br label %65, !dbg !6268

12:                                               ; preds = %2
  tail call void @test_incdec(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6269
  br label %65, !dbg !6272

13:                                               ; preds = %2
  tail call void @test_ternary(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6273
  br label %65, !dbg !6276

14:                                               ; preds = %2
  tail call void @test_casts(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6277
  br label %65, !dbg !6280

15:                                               ; preds = %2
  tail call void @test_if_else(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6281
  br label %65, !dbg !6284

16:                                               ; preds = %2
  tail call void @test_loops(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6285
  br label %65, !dbg !6288

17:                                               ; preds = %2
  tail call void @test_globals(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6289
  br label %65, !dbg !6292

18:                                               ; preds = %2
  tail call void @test_arrays(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6293
  br label %65, !dbg !6296

19:                                               ; preds = %2
  tail call void @test_structs(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6297
  br label %65, !dbg !6300

20:                                               ; preds = %2
  tail call void @test_functions(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6301
  br label %65, !dbg !6304

21:                                               ; preds = %2
  tail call void @test_apdu(ptr noundef %0, ptr noundef %3, i8 noundef signext %7, i16 noundef signext %1), !dbg !6305
  br label %65, !dbg !6308

22:                                               ; preds = %2
  tail call void @test_int_ops(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6309
  br label %65, !dbg !6312

23:                                               ; preds = %2
  tail call void @test_lshr(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6313
  br label %65, !dbg !6316

24:                                               ; preds = %2
  tail call void @test_hex_literals(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6317
  br label %65, !dbg !6320

25:                                               ; preds = %2
  tail call void @test_int_comparison(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6321
  br label %65, !dbg !6324

26:                                               ; preds = %2
  tail call void @test_const_arrays(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6325
  br label %65, !dbg !6328

27:                                               ; preds = %2
  tail call void @test_zero_comparison(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6329
  br label %65, !dbg !6332

28:                                               ; preds = %2
  tail call void @test_overflow(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6333
  br label %65, !dbg !6336

29:                                               ; preds = %2
  tail call void @test_negative_math(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6337
  br label %65, !dbg !6340

30:                                               ; preds = %2
  tail call void @test_coercion(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6341
  br label %65, !dbg !6344

31:                                               ; preds = %2
  tail call void @test_switch_dense(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6345
  br label %65, !dbg !6348

32:                                               ; preds = %2
  tail call void @test_switch_sparse(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6349
  br label %65, !dbg !6352

33:                                               ; preds = %2
  tail call void @test_break_continue(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6353
  br label %65, !dbg !6356

34:                                               ; preds = %2
  tail call void @test_complex_boolean(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6357
  br label %65, !dbg !6360

35:                                               ; preds = %2
  tail call void @test_deep_nesting(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6361
  br label %65, !dbg !6364

36:                                               ; preds = %2
  tail call void @test_many_locals(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6365
  br label %65, !dbg !6368

37:                                               ; preds = %2
  tail call void @test_int_arrays(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6369
  br label %65, !dbg !6372

38:                                               ; preds = %2
  tail call void @test_phi_patterns(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6373
  br label %65, !dbg !6376

39:                                               ; preds = %2
  tail call void @test_doom_math(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6377
  br label %65, !dbg !6380

40:                                               ; preds = %2
  tail call void @test_memset(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6381
  br label %65, !dbg !6384

41:                                               ; preds = %2
  tail call void @test_shift_combinations(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6385
  br label %65, !dbg !6388

42:                                               ; preds = %2
  tail call void @test_pixel_masks(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6389
  br label %65, !dbg !6392

43:                                               ; preds = %2
  tail call void @test_fixed_point(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6393
  br label %65, !dbg !6396

44:                                               ; preds = %2
  tail call void @test_byte_array_index(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6397
  br label %65, !dbg !6400

45:                                               ; preds = %2
  tail call void @test_bitwise_rmw(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6401
  br label %65, !dbg !6404

46:                                               ; preds = %2
  tail call void @test_signed_shifts(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6405
  br label %65, !dbg !6408

47:                                               ; preds = %2
  tail call void @test_struct_arrays(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6409
  br label %65, !dbg !6412

48:                                               ; preds = %2
  tail call void @test_high_local_count(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6413
  br label %65, !dbg !6416

49:                                               ; preds = %2
  tail call void @test_graphics_primitives(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6417
  br label %65, !dbg !6420

50:                                               ; preds = %2
  tail call void @test_boolean_density(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6421
  br label %65, !dbg !6424

51:                                               ; preds = %2
  tail call void @test_loop_edge_cases(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6425
  br label %65, !dbg !6428

52:                                               ; preds = %2
  tail call void @test_type_coercion_edge(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6429
  br label %65, !dbg !6432

53:                                               ; preds = %2
  tail call void @test_array_bounds(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6433
  br label %65, !dbg !6436

54:                                               ; preds = %2
  tail call void @test_global_array_ops(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6437
  br label %65, !dbg !6440

55:                                               ; preds = %2
  tail call void @test_ternary_patterns(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6441
  br label %65, !dbg !6444

56:                                               ; preds = %2
  tail call void @test_mul_div_edge(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6445
  br label %65, !dbg !6448

57:                                               ; preds = %2
  tail call void @test_rng(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6449
  br label %65, !dbg !6452

58:                                               ; preds = %2
  tail call void @test_state_machine(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6453
  br label %65, !dbg !6456

59:                                               ; preds = %2
  tail call void @test_font_lookup(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6457
  br label %65, !dbg !6460

60:                                               ; preds = %2
  tail call void @test_fillrect(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6461
  br label %65, !dbg !6464

61:                                               ; preds = %2
  tail call void @test_object_pool(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6465
  br label %65, !dbg !6468

62:                                               ; preds = %2
  tail call void @test_rendering(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6469
  br label %65, !dbg !6472

63:                                               ; preds = %2
  tail call void @test_frame1(ptr noundef %0, ptr noundef %3, i8 noundef signext %7), !dbg !6473
  br label %65, !dbg !6476

64:                                               ; preds = %2
  tail call void @jc_ISOException_throwIt(i16 noundef signext 27904) #11, !dbg !6477
  br label %65, !dbg !6478

65:                                               ; preds = %64, %63, %62, %61, %60, %59, %58, %57, %56, %55, %54, %53, %52, %51, %50, %49, %48, %47, %46, %45, %44, %43, %42, %41, %40, %39, %38, %37, %36, %35, %34, %33, %32, %31, %30, %29, %28, %27, %26, %25, %24, %23, %22, %21, %20, %19, %18, %17, %16, %15, %14, %13, %12, %11, %10, %9, %8
  ret void, !dbg !6478
}

declare !dbg !6479 ptr @jc_APDU_getBuffer(ptr noundef) local_unnamed_addr #1

declare !dbg !6482 void @jc_ISOException_throwIt(i16 noundef signext) local_unnamed_addr #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i16 @llvm.smax.i16(i16, i16) #9

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i16 @llvm.smin.i16(i16, i16) #9

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #10

attributes #0 = { nounwind "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #1 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #2 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #3 = { nofree norecurse nosync nounwind memory(read, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #4 = { nofree norecurse nosync nounwind memory(write, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #5 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #6 = { nofree norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #7 = { nofree norecurse nosync nounwind memory(none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #8 = { mustprogress nofree norecurse nosync nounwind willreturn memory(write, argmem: none, inaccessiblemem: none) "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+multivalue,+mutable-globals,+reference-types,+sign-ext" }
attributes #9 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #10 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #11 = { nounwind }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!94, !95, !96, !97}
!llvm.ident = !{!98}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "PALETTE", scope: !2, file: !3, line: 83, type: !33, isLocal: false, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C11, file: !3, producer: "Apple clang version 17.0.0 (clang-1700.6.3.2)", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !4, globals: !9, splitDebugInlining: false, nameTableKind: None)
!3 = !DIFile(filename: "main.c", directory: "/home/user/jcc/examples/correctness")
!4 = !{!5, !8}
!5 = !DIDerivedType(tag: DW_TAG_typedef, name: "byte", file: !6, line: 7, baseType: !7)
!6 = !DIFile(filename: "include/jcc.h", directory: "/home/user/jcc")
!7 = !DIBasicType(name: "signed char", size: 8, encoding: DW_ATE_signed_char)
!8 = !DIBasicType(name: "short", size: 16, encoding: DW_ATE_signed)
!9 = !{!0, !10, !16, !23, !30, !36, !41, !43, !48, !50, !53, !55, !62, !72, !79, !88, !90, !92}
!10 = !DIGlobalVariableExpression(var: !11, expr: !DIExpression())
!11 = distinct !DIGlobalVariable(name: "WAVE", scope: !2, file: !3, line: 84, type: !12, isLocal: false, isDefinition: true)
!12 = !DICompositeType(tag: DW_TAG_array_type, baseType: !13, size: 64, elements: !14)
!13 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !8)
!14 = !{!15}
!15 = !DISubrange(count: 4)
!16 = !DIGlobalVariableExpression(var: !17, expr: !DIExpression())
!17 = distinct !DIGlobalVariable(name: "LOOKUP", scope: !2, file: !3, line: 85, type: !18, isLocal: false, isDefinition: true)
!18 = !DICompositeType(tag: DW_TAG_array_type, baseType: !19, size: 64, elements: !21)
!19 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !20)
!20 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!21 = !{!22}
!22 = !DISubrange(count: 2)
!23 = !DIGlobalVariableExpression(var: !24, expr: !DIExpression())
!24 = distinct !DIGlobalVariable(name: "FONT_5x3", scope: !2, file: !25, line: 8, type: !26, isLocal: false, isDefinition: true)
!25 = !DIFile(filename: "./test_font_lookup.h", directory: "/home/user/jcc/examples/correctness")
!26 = !DICompositeType(tag: DW_TAG_array_type, baseType: !27, size: 400, elements: !28)
!27 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !5)
!28 = !{!29}
!29 = !DISubrange(count: 50)
!30 = !DIGlobalVariableExpression(var: !31, expr: !DIExpression())
!31 = distinct !DIGlobalVariable(name: "BIRD_SPRITE", scope: !2, file: !32, line: 14, type: !33, isLocal: false, isDefinition: true)
!32 = !DIFile(filename: "./test_rendering.h", directory: "/home/user/jcc/examples/correctness")
!33 = !DICompositeType(tag: DW_TAG_array_type, baseType: !27, size: 24, elements: !34)
!34 = !{!35}
!35 = !DISubrange(count: 3)
!36 = !DIGlobalVariableExpression(var: !37, expr: !DIExpression())
!37 = distinct !DIGlobalVariable(name: "shared_fb", scope: !2, file: !3, line: 64, type: !38, isLocal: false, isDefinition: true)
!38 = !DICompositeType(tag: DW_TAG_array_type, baseType: !5, size: 640, elements: !39)
!39 = !{!40}
!40 = !DISubrange(count: 80)
!41 = !DIGlobalVariableExpression(var: !42, expr: !DIExpression())
!42 = distinct !DIGlobalVariable(name: "g_byte", scope: !2, file: !3, line: 67, type: !5, isLocal: false, isDefinition: true)
!43 = !DIGlobalVariableExpression(var: !44, expr: !DIExpression())
!44 = distinct !DIGlobalVariable(name: "g_shorts", scope: !2, file: !3, line: 69, type: !45, isLocal: false, isDefinition: true)
!45 = !DICompositeType(tag: DW_TAG_array_type, baseType: !8, size: 128, elements: !46)
!46 = !{!47}
!47 = !DISubrange(count: 8)
!48 = !DIGlobalVariableExpression(var: !49, expr: !DIExpression())
!49 = distinct !DIGlobalVariable(name: "g_short", scope: !2, file: !3, line: 70, type: !8, isLocal: false, isDefinition: true)
!50 = !DIGlobalVariableExpression(var: !51, expr: !DIExpression())
!51 = distinct !DIGlobalVariable(name: "g_ints", scope: !2, file: !3, line: 72, type: !52, isLocal: false, isDefinition: true)
!52 = !DICompositeType(tag: DW_TAG_array_type, baseType: !20, size: 128, elements: !14)
!53 = !DIGlobalVariableExpression(var: !54, expr: !DIExpression())
!54 = distinct !DIGlobalVariable(name: "g_int", scope: !2, file: !3, line: 73, type: !20, isLocal: false, isDefinition: true)
!55 = !DIGlobalVariableExpression(var: !56, expr: !DIExpression())
!56 = distinct !DIGlobalVariable(name: "items", scope: !2, file: !3, line: 80, type: !57, isLocal: false, isDefinition: true)
!57 = !DICompositeType(tag: DW_TAG_array_type, baseType: !58, size: 128, elements: !14)
!58 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "Item", file: !3, line: 75, size: 32, elements: !59)
!59 = !{!60, !61}
!60 = !DIDerivedType(tag: DW_TAG_member, name: "value", scope: !58, file: !3, line: 76, baseType: !8, size: 16)
!61 = !DIDerivedType(tag: DW_TAG_member, name: "flag", scope: !58, file: !3, line: 77, baseType: !5, size: 8, offset: 16)
!62 = !DIGlobalVariableExpression(var: !63, expr: !DIExpression())
!63 = distinct !DIGlobalVariable(name: "pool", scope: !2, file: !64, line: 15, type: !65, isLocal: false, isDefinition: true)
!64 = !DIFile(filename: "./test_object_pool.h", directory: "/home/user/jcc/examples/correctness")
!65 = !DICompositeType(tag: DW_TAG_array_type, baseType: !66, size: 192, elements: !14)
!66 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "pool_obj_t", file: !64, line: 8, size: 48, elements: !67)
!67 = !{!68, !69, !70, !71}
!68 = !DIDerivedType(tag: DW_TAG_member, name: "x", scope: !66, file: !64, line: 9, baseType: !8, size: 16)
!69 = !DIDerivedType(tag: DW_TAG_member, name: "y", scope: !66, file: !64, line: 10, baseType: !8, size: 16, offset: 16)
!70 = !DIDerivedType(tag: DW_TAG_member, name: "active", scope: !66, file: !64, line: 11, baseType: !5, size: 8, offset: 32)
!71 = !DIDerivedType(tag: DW_TAG_member, name: "type", scope: !66, file: !64, line: 12, baseType: !5, size: 8, offset: 40)
!72 = !DIGlobalVariableExpression(var: !73, expr: !DIExpression())
!73 = distinct !DIGlobalVariable(name: "g_pts", scope: !2, file: !3, line: 1750, type: !74, isLocal: false, isDefinition: true)
!74 = !DICompositeType(tag: DW_TAG_array_type, baseType: !75, size: 128, elements: !14)
!75 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "point_s", file: !3, line: 1747, size: 32, elements: !76)
!76 = !{!77, !78}
!77 = !DIDerivedType(tag: DW_TAG_member, name: "x", scope: !75, file: !3, line: 1747, baseType: !8, size: 16)
!78 = !DIDerivedType(tag: DW_TAG_member, name: "y", scope: !75, file: !3, line: 1747, baseType: !8, size: 16, offset: 16)
!79 = !DIGlobalVariableExpression(var: !80, expr: !DIExpression())
!80 = distinct !DIGlobalVariable(name: "g_pipes", scope: !2, file: !3, line: 1751, type: !81, isLocal: false, isDefinition: true)
!81 = !DICompositeType(tag: DW_TAG_array_type, baseType: !82, size: 144, elements: !34)
!82 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "pipe_s", file: !3, line: 1748, size: 48, elements: !83)
!83 = !{!84, !85, !86, !87}
!84 = !DIDerivedType(tag: DW_TAG_member, name: "x", scope: !82, file: !3, line: 1748, baseType: !8, size: 16)
!85 = !DIDerivedType(tag: DW_TAG_member, name: "gap_y", scope: !82, file: !3, line: 1748, baseType: !8, size: 16, offset: 16)
!86 = !DIDerivedType(tag: DW_TAG_member, name: "active", scope: !82, file: !3, line: 1748, baseType: !5, size: 8, offset: 32)
!87 = !DIDerivedType(tag: DW_TAG_member, name: "scored", scope: !82, file: !3, line: 1748, baseType: !5, size: 8, offset: 40)
!88 = !DIGlobalVariableExpression(var: !89, expr: !DIExpression())
!89 = distinct !DIGlobalVariable(name: "g_rng_seed", scope: !2, file: !3, line: 2630, type: !8, isLocal: false, isDefinition: true)
!90 = !DIGlobalVariableExpression(var: !91, expr: !DIExpression())
!91 = distinct !DIGlobalVariable(name: "g_state", scope: !2, file: !3, line: 2712, type: !8, isLocal: false, isDefinition: true)
!92 = !DIGlobalVariableExpression(var: !93, expr: !DIExpression())
!93 = distinct !DIGlobalVariable(name: "g_frame", scope: !2, file: !3, line: 2713, type: !8, isLocal: false, isDefinition: true)
!94 = !{i32 7, !"Dwarf Version", i32 4}
!95 = !{i32 2, !"Debug Info Version", i32 3}
!96 = !{i32 1, !"wchar_size", i32 4}
!97 = !{i32 7, !"debug-info-assignment-tracking", i1 true}
!98 = !{!"Apple clang version 17.0.0 (clang-1700.6.3.2)"}
!99 = distinct !DISubprogram(name: "sendResult", scope: !3, file: !3, line: 91, type: !100, scopeLine: 91, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !105)
!100 = !DISubroutineType(types: !101)
!101 = !{null, !102, !104, !8}
!102 = !DIDerivedType(tag: DW_TAG_typedef, name: "APDU", file: !6, line: 11, baseType: !103)
!103 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 32)
!104 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !5, size: 32)
!105 = !{!106, !107, !108}
!106 = !DILocalVariable(name: "apdu", arg: 1, scope: !99, file: !3, line: 91, type: !102)
!107 = !DILocalVariable(name: "buffer", arg: 2, scope: !99, file: !3, line: 91, type: !104)
!108 = !DILocalVariable(name: "result", arg: 3, scope: !99, file: !3, line: 91, type: !8)
!109 = !DILocation(line: 0, scope: !99)
!110 = !DILocation(line: 92, column: 31, scope: !99)
!111 = !DILocation(line: 92, column: 17, scope: !99)
!112 = !DILocation(line: 92, column: 15, scope: !99)
!113 = !{!114, !114, i64 0}
!114 = !{!"omnipotent char", !115, i64 0}
!115 = !{!"Simple C/C++ TBAA"}
!116 = !DILocation(line: 93, column: 17, scope: !99)
!117 = !DILocation(line: 93, column: 5, scope: !99)
!118 = !DILocation(line: 93, column: 15, scope: !99)
!119 = !DILocation(line: 94, column: 5, scope: !99)
!120 = !DILocation(line: 95, column: 5, scope: !99)
!121 = !DILocation(line: 96, column: 5, scope: !99)
!122 = !DILocation(line: 97, column: 1, scope: !99)
!123 = !DISubprogram(name: "jc_APDU_setOutgoing", scope: !6, file: !6, line: 96, type: !124, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!124 = !DISubroutineType(types: !125)
!125 = !{!8, !102}
!126 = !DISubprogram(name: "jc_APDU_setOutgoingLength", scope: !6, file: !6, line: 97, type: !127, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!127 = !DISubroutineType(types: !128)
!128 = !{null, !102, !8}
!129 = !DISubprogram(name: "jc_APDU_sendBytes", scope: !6, file: !6, line: 98, type: !130, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!130 = !DISubroutineType(types: !131)
!131 = !{null, !102, !8, !8}
!132 = distinct !DISubprogram(name: "add_shorts", scope: !3, file: !3, line: 103, type: !133, scopeLine: 103, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !135)
!133 = !DISubroutineType(types: !134)
!134 = !{!8, !8, !8}
!135 = !{!136, !137}
!136 = !DILocalVariable(name: "a", arg: 1, scope: !132, file: !3, line: 103, type: !8)
!137 = !DILocalVariable(name: "b", arg: 2, scope: !132, file: !3, line: 103, type: !8)
!138 = !DILocation(line: 0, scope: !132)
!139 = !DILocation(line: 104, column: 14, scope: !132)
!140 = !DILocation(line: 104, column: 5, scope: !132)
!141 = distinct !DISubprogram(name: "test_font_lookup", scope: !25, file: !25, line: 21, type: !142, scopeLine: 21, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !144)
!142 = !DISubroutineType(types: !143)
!143 = !{null, !102, !104, !5}
!144 = !{!145, !146, !147, !148, !149, !150, !151, !152, !153, !154, !155, !156, !157, !160, !161, !164, !165, !166, !169, !170, !171, !174, !175, !176, !179, !180, !181, !184, !185, !186, !189, !190, !191, !194, !195, !198, !199, !200}
!145 = !DILocalVariable(name: "apdu", arg: 1, scope: !141, file: !25, line: 21, type: !102)
!146 = !DILocalVariable(name: "buffer", arg: 2, scope: !141, file: !25, line: 21, type: !104)
!147 = !DILocalVariable(name: "p1", arg: 3, scope: !141, file: !25, line: 21, type: !5)
!148 = !DILocalVariable(name: "digit", scope: !141, file: !25, line: 22, type: !8)
!149 = !DILocalVariable(name: "row", scope: !141, file: !25, line: 23, type: !8)
!150 = !DILocalVariable(name: "sum", scope: !141, file: !25, line: 24, type: !8)
!151 = !DILocalVariable(name: "i", scope: !141, file: !25, line: 25, type: !8)
!152 = !DILocalVariable(name: "fontRow", scope: !141, file: !25, line: 26, type: !5)
!153 = !DILocalVariable(name: "xBit", scope: !141, file: !25, line: 27, type: !5)
!154 = !DILocalVariable(name: "shift", scope: !141, file: !25, line: 28, type: !5)
!155 = !DILocalVariable(name: "mask1", scope: !141, file: !25, line: 29, type: !5)
!156 = !DILocalVariable(name: "mask2", scope: !141, file: !25, line: 30, type: !5)
!157 = !DILocalVariable(name: "num", scope: !158, file: !25, line: 167, type: !8)
!158 = distinct !DILexicalBlock(scope: !159, file: !25, line: 166, column: 19)
!159 = distinct !DILexicalBlock(scope: !141, file: !25, line: 166, column: 9)
!160 = !DILocalVariable(name: "d0", scope: !158, file: !25, line: 168, type: !8)
!161 = !DILocalVariable(name: "num", scope: !162, file: !25, line: 173, type: !8)
!162 = distinct !DILexicalBlock(scope: !163, file: !25, line: 172, column: 19)
!163 = distinct !DILexicalBlock(scope: !141, file: !25, line: 172, column: 9)
!164 = !DILocalVariable(name: "temp", scope: !162, file: !25, line: 174, type: !8)
!165 = !DILocalVariable(name: "d1", scope: !162, file: !25, line: 175, type: !8)
!166 = !DILocalVariable(name: "num", scope: !167, file: !25, line: 180, type: !8)
!167 = distinct !DILexicalBlock(scope: !168, file: !25, line: 179, column: 19)
!168 = distinct !DILexicalBlock(scope: !141, file: !25, line: 179, column: 9)
!169 = !DILocalVariable(name: "temp", scope: !167, file: !25, line: 181, type: !8)
!170 = !DILocalVariable(name: "d2", scope: !167, file: !25, line: 183, type: !8)
!171 = !DILocalVariable(name: "num", scope: !172, file: !25, line: 190, type: !8)
!172 = distinct !DILexicalBlock(scope: !173, file: !25, line: 189, column: 19)
!173 = distinct !DILexicalBlock(scope: !141, file: !25, line: 189, column: 9)
!174 = !DILocalVariable(name: "count", scope: !172, file: !25, line: 191, type: !8)
!175 = !DILocalVariable(name: "temp", scope: !172, file: !25, line: 192, type: !8)
!176 = !DILocalVariable(name: "num", scope: !177, file: !25, line: 201, type: !8)
!177 = distinct !DILexicalBlock(scope: !178, file: !25, line: 200, column: 19)
!178 = distinct !DILexicalBlock(scope: !141, file: !25, line: 200, column: 9)
!179 = !DILocalVariable(name: "count", scope: !177, file: !25, line: 202, type: !8)
!180 = !DILocalVariable(name: "temp", scope: !177, file: !25, line: 203, type: !8)
!181 = !DILocalVariable(name: "num", scope: !182, file: !25, line: 212, type: !8)
!182 = distinct !DILexicalBlock(scope: !183, file: !25, line: 211, column: 19)
!183 = distinct !DILexicalBlock(scope: !141, file: !25, line: 211, column: 9)
!184 = !DILocalVariable(name: "count", scope: !182, file: !25, line: 213, type: !8)
!185 = !DILocalVariable(name: "temp", scope: !182, file: !25, line: 214, type: !8)
!186 = !DILocalVariable(name: "num", scope: !187, file: !25, line: 223, type: !8)
!187 = distinct !DILexicalBlock(scope: !188, file: !25, line: 222, column: 19)
!188 = distinct !DILexicalBlock(scope: !141, file: !25, line: 222, column: 9)
!189 = !DILocalVariable(name: "count", scope: !187, file: !25, line: 224, type: !8)
!190 = !DILocalVariable(name: "temp", scope: !187, file: !25, line: 225, type: !8)
!191 = !DILocalVariable(name: "num_digits", scope: !192, file: !25, line: 236, type: !8)
!192 = distinct !DILexicalBlock(scope: !193, file: !25, line: 235, column: 19)
!193 = distinct !DILexicalBlock(scope: !141, file: !25, line: 235, column: 9)
!194 = !DILocalVariable(name: "width", scope: !192, file: !25, line: 237, type: !8)
!195 = !DILocalVariable(name: "center_x", scope: !196, file: !25, line: 242, type: !8)
!196 = distinct !DILexicalBlock(scope: !197, file: !25, line: 241, column: 19)
!197 = distinct !DILexicalBlock(scope: !141, file: !25, line: 241, column: 9)
!198 = !DILocalVariable(name: "num_digits", scope: !196, file: !25, line: 243, type: !8)
!199 = !DILocalVariable(name: "width", scope: !196, file: !25, line: 244, type: !8)
!200 = !DILocalVariable(name: "start_x", scope: !196, file: !25, line: 245, type: !8)
!201 = !DILocation(line: 0, scope: !141)
!202 = !DILocation(line: 33, column: 9, scope: !141)
!203 = !DILocation(line: 0, scope: !99, inlinedAt: !204)
!204 = distinct !DILocation(line: 40, column: 9, scope: !205)
!205 = distinct !DILexicalBlock(scope: !206, file: !25, line: 38, column: 18)
!206 = distinct !DILexicalBlock(scope: !141, file: !25, line: 38, column: 9)
!207 = !DILocation(line: 41, column: 9, scope: !205)
!208 = !DILocation(line: 0, scope: !99, inlinedAt: !209)
!209 = distinct !DILocation(line: 45, column: 9, scope: !210)
!210 = distinct !DILexicalBlock(scope: !211, file: !25, line: 43, column: 18)
!211 = distinct !DILexicalBlock(scope: !141, file: !25, line: 43, column: 9)
!212 = !DILocation(line: 46, column: 9, scope: !210)
!213 = !DILocation(line: 0, scope: !99, inlinedAt: !214)
!214 = distinct !DILocation(line: 64, column: 9, scope: !215)
!215 = distinct !DILexicalBlock(scope: !216, file: !25, line: 61, column: 18)
!216 = distinct !DILexicalBlock(scope: !141, file: !25, line: 61, column: 9)
!217 = !DILocation(line: 65, column: 9, scope: !215)
!218 = !DILocation(line: 0, scope: !99, inlinedAt: !219)
!219 = distinct !DILocation(line: 75, column: 9, scope: !220)
!220 = distinct !DILexicalBlock(scope: !221, file: !25, line: 69, column: 18)
!221 = distinct !DILexicalBlock(scope: !141, file: !25, line: 69, column: 9)
!222 = !DILocation(line: 76, column: 9, scope: !220)
!223 = !DILocation(line: 0, scope: !99, inlinedAt: !224)
!224 = distinct !DILocation(line: 84, column: 9, scope: !225)
!225 = distinct !DILexicalBlock(scope: !226, file: !25, line: 78, column: 18)
!226 = distinct !DILexicalBlock(scope: !141, file: !25, line: 78, column: 9)
!227 = !DILocation(line: 85, column: 9, scope: !225)
!228 = !DILocation(line: 0, scope: !99, inlinedAt: !229)
!229 = distinct !DILocation(line: 106, column: 9, scope: !230)
!230 = distinct !DILexicalBlock(scope: !231, file: !25, line: 101, column: 18)
!231 = distinct !DILexicalBlock(scope: !141, file: !25, line: 101, column: 9)
!232 = !DILocation(line: 107, column: 9, scope: !230)
!233 = !DILocation(line: 0, scope: !99, inlinedAt: !234)
!234 = distinct !DILocation(line: 122, column: 9, scope: !235)
!235 = distinct !DILexicalBlock(scope: !236, file: !25, line: 117, column: 19)
!236 = distinct !DILexicalBlock(scope: !141, file: !25, line: 117, column: 9)
!237 = !DILocation(line: 123, column: 9, scope: !235)
!238 = !DILocation(line: 0, scope: !99, inlinedAt: !239)
!239 = distinct !DILocation(line: 134, column: 9, scope: !240)
!240 = distinct !DILexicalBlock(scope: !241, file: !25, line: 128, column: 19)
!241 = distinct !DILexicalBlock(scope: !141, file: !25, line: 128, column: 9)
!242 = !DILocation(line: 135, column: 9, scope: !240)
!243 = !DILocation(line: 0, scope: !99, inlinedAt: !244)
!244 = distinct !DILocation(line: 143, column: 9, scope: !245)
!245 = distinct !DILexicalBlock(scope: !246, file: !25, line: 137, column: 19)
!246 = distinct !DILexicalBlock(scope: !141, file: !25, line: 137, column: 9)
!247 = !DILocation(line: 144, column: 9, scope: !245)
!248 = !DILocation(line: 0, scope: !99, inlinedAt: !249)
!249 = distinct !DILocation(line: 152, column: 9, scope: !250)
!250 = distinct !DILexicalBlock(scope: !251, file: !25, line: 146, column: 19)
!251 = distinct !DILexicalBlock(scope: !141, file: !25, line: 146, column: 9)
!252 = !DILocation(line: 153, column: 9, scope: !250)
!253 = !DILocation(line: 0, scope: !99, inlinedAt: !254)
!254 = distinct !DILocation(line: 161, column: 9, scope: !255)
!255 = distinct !DILexicalBlock(scope: !256, file: !25, line: 155, column: 19)
!256 = distinct !DILexicalBlock(scope: !141, file: !25, line: 155, column: 9)
!257 = !DILocation(line: 162, column: 9, scope: !255)
!258 = !DILocation(line: 0, scope: !158)
!259 = !DILocation(line: 0, scope: !99, inlinedAt: !260)
!260 = distinct !DILocation(line: 169, column: 9, scope: !158)
!261 = !DILocation(line: 0, scope: !162)
!262 = !DILocation(line: 0, scope: !99, inlinedAt: !263)
!263 = distinct !DILocation(line: 176, column: 9, scope: !162)
!264 = !DILocation(line: 0, scope: !167)
!265 = !DILocation(line: 0, scope: !99, inlinedAt: !266)
!266 = distinct !DILocation(line: 184, column: 9, scope: !167)
!267 = !DILocation(line: 0, scope: !172)
!268 = !DILocation(line: 0, scope: !99, inlinedAt: !269)
!269 = distinct !DILocation(line: 197, column: 9, scope: !172)
!270 = !DILocation(line: 0, scope: !177)
!271 = !DILocation(line: 0, scope: !99, inlinedAt: !272)
!272 = distinct !DILocation(line: 208, column: 9, scope: !177)
!273 = !DILocation(line: 0, scope: !182)
!274 = !DILocation(line: 0, scope: !99, inlinedAt: !275)
!275 = distinct !DILocation(line: 219, column: 9, scope: !182)
!276 = !DILocation(line: 0, scope: !187)
!277 = !DILocation(line: 0, scope: !99, inlinedAt: !278)
!278 = distinct !DILocation(line: 230, column: 9, scope: !187)
!279 = !DILocation(line: 0, scope: !192)
!280 = !DILocation(line: 0, scope: !99, inlinedAt: !281)
!281 = distinct !DILocation(line: 238, column: 9, scope: !192)
!282 = !DILocation(line: 0, scope: !196)
!283 = !DILocation(line: 0, scope: !99, inlinedAt: !284)
!284 = distinct !DILocation(line: 246, column: 9, scope: !196)
!285 = !DILocation(line: 0, scope: !99, inlinedAt: !286)
!286 = distinct !DILocation(line: 250, column: 5, scope: !141)
!287 = !DILocation(line: 251, column: 1, scope: !141)
!288 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !201)
!289 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !201)
!290 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !201)
!291 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !201)
!292 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !201)
!293 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !201)
!294 = distinct !DISubprogram(name: "fb_checksum", scope: !295, file: !295, line: 16, type: !296, scopeLine: 16, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !298)
!295 = !DIFile(filename: "./test_fillrect.h", directory: "/home/user/jcc/examples/correctness")
!296 = !DISubroutineType(types: !297)
!297 = !{!8}
!298 = !{!299, !300}
!299 = !DILocalVariable(name: "i", scope: !294, file: !295, line: 17, type: !8)
!300 = !DILocalVariable(name: "sum", scope: !294, file: !295, line: 18, type: !8)
!301 = !DILocation(line: 0, scope: !294)
!302 = !DILocation(line: 19, column: 5, scope: !303)
!303 = distinct !DILexicalBlock(scope: !294, file: !295, line: 19, column: 5)
!304 = !DILocation(line: 20, column: 22, scope: !305)
!305 = distinct !DILexicalBlock(scope: !306, file: !295, line: 19, column: 46)
!306 = distinct !DILexicalBlock(scope: !303, file: !295, line: 19, column: 5)
!307 = !DILocation(line: 20, column: 19, scope: !305)
!308 = !DILocation(line: 19, column: 17, scope: !306)
!309 = !DILocation(line: 19, column: 19, scope: !306)
!310 = distinct !{!310, !302, !311, !312, !313}
!311 = !DILocation(line: 21, column: 5, scope: !303)
!312 = !{!"llvm.loop.mustprogress"}
!313 = !{!"llvm.loop.unroll.disable"}
!314 = !DILocation(line: 22, column: 5, scope: !294)
!315 = distinct !DISubprogram(name: "test_fillrect", scope: !295, file: !295, line: 25, type: !142, scopeLine: 25, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !316)
!316 = !{!317, !318, !319, !320, !321, !322, !323, !324, !325, !326, !327, !328, !329, !330, !331, !332, !333, !334, !337}
!317 = !DILocalVariable(name: "apdu", arg: 1, scope: !315, file: !295, line: 25, type: !102)
!318 = !DILocalVariable(name: "buffer", arg: 2, scope: !315, file: !295, line: 25, type: !104)
!319 = !DILocalVariable(name: "p1", arg: 3, scope: !315, file: !295, line: 25, type: !5)
!320 = !DILocalVariable(name: "x0", scope: !315, file: !295, line: 26, type: !8)
!321 = !DILocalVariable(name: "y0", scope: !315, file: !295, line: 26, type: !8)
!322 = !DILocalVariable(name: "x1", scope: !315, file: !295, line: 26, type: !8)
!323 = !DILocalVariable(name: "y1", scope: !315, file: !295, line: 26, type: !8)
!324 = !DILocalVariable(name: "startByte", scope: !315, file: !295, line: 27, type: !8)
!325 = !DILocalVariable(name: "endByte", scope: !315, file: !295, line: 27, type: !8)
!326 = !DILocalVariable(name: "middleBytes", scope: !315, file: !295, line: 27, type: !8)
!327 = !DILocalVariable(name: "startMask", scope: !315, file: !295, line: 28, type: !5)
!328 = !DILocalVariable(name: "endMask", scope: !315, file: !295, line: 28, type: !5)
!329 = !DILocalVariable(name: "fillByte", scope: !315, file: !295, line: 28, type: !5)
!330 = !DILocalVariable(name: "y", scope: !315, file: !295, line: 29, type: !8)
!331 = !DILocalVariable(name: "rowBase", scope: !315, file: !295, line: 29, type: !8)
!332 = !DILocalVariable(name: "mask", scope: !315, file: !295, line: 30, type: !5)
!333 = !DILocalVariable(name: "i", scope: !315, file: !295, line: 31, type: !8)
!334 = !DILocalVariable(name: "len", scope: !335, file: !295, line: 169, type: !8)
!335 = distinct !DILexicalBlock(scope: !336, file: !295, line: 167, column: 19)
!336 = distinct !DILexicalBlock(scope: !315, file: !295, line: 167, column: 9)
!337 = !DILocalVariable(name: "len", scope: !338, file: !295, line: 175, type: !8)
!338 = distinct !DILexicalBlock(scope: !339, file: !295, line: 173, column: 19)
!339 = distinct !DILexicalBlock(scope: !315, file: !295, line: 173, column: 9)
!340 = !DILocation(line: 0, scope: !315)
!341 = !DILocation(line: 34, column: 9, scope: !315)
!342 = !DILocation(line: 0, scope: !99, inlinedAt: !343)
!343 = distinct !DILocation(line: 37, column: 9, scope: !344)
!344 = distinct !DILexicalBlock(scope: !345, file: !295, line: 34, column: 18)
!345 = distinct !DILexicalBlock(scope: !315, file: !295, line: 34, column: 9)
!346 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !343)
!347 = !DILocation(line: 38, column: 9, scope: !344)
!348 = !DILocation(line: 0, scope: !99, inlinedAt: !349)
!349 = distinct !DILocation(line: 43, column: 9, scope: !350)
!350 = distinct !DILexicalBlock(scope: !351, file: !295, line: 40, column: 18)
!351 = distinct !DILexicalBlock(scope: !315, file: !295, line: 40, column: 9)
!352 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !349)
!353 = !DILocation(line: 44, column: 9, scope: !350)
!354 = !DILocation(line: 0, scope: !99, inlinedAt: !355)
!355 = distinct !DILocation(line: 49, column: 9, scope: !356)
!356 = distinct !DILexicalBlock(scope: !357, file: !295, line: 46, column: 18)
!357 = distinct !DILexicalBlock(scope: !315, file: !295, line: 46, column: 9)
!358 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !355)
!359 = !DILocation(line: 50, column: 9, scope: !356)
!360 = !DILocation(line: 0, scope: !99, inlinedAt: !361)
!361 = distinct !DILocation(line: 55, column: 9, scope: !362)
!362 = distinct !DILexicalBlock(scope: !363, file: !295, line: 52, column: 18)
!363 = distinct !DILexicalBlock(scope: !315, file: !295, line: 52, column: 9)
!364 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !361)
!365 = !DILocation(line: 56, column: 9, scope: !362)
!366 = !DILocation(line: 0, scope: !99, inlinedAt: !367)
!367 = distinct !DILocation(line: 63, column: 9, scope: !368)
!368 = distinct !DILexicalBlock(scope: !369, file: !295, line: 60, column: 18)
!369 = distinct !DILexicalBlock(scope: !315, file: !295, line: 60, column: 9)
!370 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !367)
!371 = !DILocation(line: 64, column: 9, scope: !368)
!372 = !DILocation(line: 0, scope: !99, inlinedAt: !373)
!373 = distinct !DILocation(line: 69, column: 9, scope: !374)
!374 = distinct !DILexicalBlock(scope: !375, file: !295, line: 66, column: 18)
!375 = distinct !DILexicalBlock(scope: !315, file: !295, line: 66, column: 9)
!376 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !373)
!377 = !DILocation(line: 70, column: 9, scope: !374)
!378 = !DILocation(line: 0, scope: !99, inlinedAt: !379)
!379 = distinct !DILocation(line: 75, column: 9, scope: !380)
!380 = distinct !DILexicalBlock(scope: !381, file: !295, line: 72, column: 18)
!381 = distinct !DILexicalBlock(scope: !315, file: !295, line: 72, column: 9)
!382 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !379)
!383 = !DILocation(line: 76, column: 9, scope: !380)
!384 = !DILocation(line: 0, scope: !99, inlinedAt: !385)
!385 = distinct !DILocation(line: 81, column: 9, scope: !386)
!386 = distinct !DILexicalBlock(scope: !387, file: !295, line: 78, column: 18)
!387 = distinct !DILexicalBlock(scope: !315, file: !295, line: 78, column: 9)
!388 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !385)
!389 = !DILocation(line: 82, column: 9, scope: !386)
!390 = !DILocation(line: 0, scope: !99, inlinedAt: !391)
!391 = distinct !DILocation(line: 91, column: 9, scope: !392)
!392 = distinct !DILexicalBlock(scope: !393, file: !295, line: 86, column: 18)
!393 = distinct !DILexicalBlock(scope: !315, file: !295, line: 86, column: 9)
!394 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !391)
!395 = !DILocation(line: 92, column: 9, scope: !392)
!396 = !DILocation(line: 0, scope: !99, inlinedAt: !397)
!397 = distinct !DILocation(line: 99, column: 9, scope: !398)
!398 = distinct !DILexicalBlock(scope: !399, file: !295, line: 94, column: 18)
!399 = distinct !DILexicalBlock(scope: !315, file: !295, line: 94, column: 9)
!400 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !397)
!401 = !DILocation(line: 100, column: 9, scope: !398)
!402 = !DILocation(line: 0, scope: !99, inlinedAt: !403)
!403 = distinct !DILocation(line: 107, column: 9, scope: !404)
!404 = distinct !DILexicalBlock(scope: !405, file: !295, line: 102, column: 19)
!405 = distinct !DILexicalBlock(scope: !315, file: !295, line: 102, column: 9)
!406 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !403)
!407 = !DILocation(line: 108, column: 9, scope: !404)
!408 = !DILocation(line: 0, scope: !99, inlinedAt: !409)
!409 = distinct !DILocation(line: 117, column: 9, scope: !410)
!410 = distinct !DILexicalBlock(scope: !411, file: !295, line: 112, column: 19)
!411 = distinct !DILexicalBlock(scope: !315, file: !295, line: 112, column: 9)
!412 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !409)
!413 = !DILocation(line: 118, column: 9, scope: !410)
!414 = !DILocation(line: 0, scope: !99, inlinedAt: !415)
!415 = distinct !DILocation(line: 125, column: 9, scope: !416)
!416 = distinct !DILexicalBlock(scope: !417, file: !295, line: 120, column: 19)
!417 = distinct !DILexicalBlock(scope: !315, file: !295, line: 120, column: 9)
!418 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !415)
!419 = !DILocation(line: 126, column: 9, scope: !416)
!420 = !DILocation(line: 0, scope: !99, inlinedAt: !421)
!421 = distinct !DILocation(line: 133, column: 9, scope: !422)
!422 = distinct !DILexicalBlock(scope: !423, file: !295, line: 128, column: 19)
!423 = distinct !DILexicalBlock(scope: !315, file: !295, line: 128, column: 9)
!424 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !421)
!425 = !DILocation(line: 134, column: 9, scope: !422)
!426 = !DILocation(line: 0, scope: !99, inlinedAt: !427)
!427 = distinct !DILocation(line: 141, column: 9, scope: !428)
!428 = distinct !DILexicalBlock(scope: !429, file: !295, line: 136, column: 19)
!429 = distinct !DILexicalBlock(scope: !315, file: !295, line: 136, column: 9)
!430 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !427)
!431 = !DILocation(line: 142, column: 9, scope: !428)
!432 = !DILocation(line: 0, scope: !99, inlinedAt: !433)
!433 = distinct !DILocation(line: 149, column: 9, scope: !434)
!434 = distinct !DILexicalBlock(scope: !435, file: !295, line: 146, column: 19)
!435 = distinct !DILexicalBlock(scope: !315, file: !295, line: 146, column: 9)
!436 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !433)
!437 = !DILocation(line: 150, column: 9, scope: !434)
!438 = !DILocation(line: 0, scope: !99, inlinedAt: !439)
!439 = distinct !DILocation(line: 155, column: 9, scope: !440)
!440 = distinct !DILexicalBlock(scope: !441, file: !295, line: 152, column: 19)
!441 = distinct !DILexicalBlock(scope: !315, file: !295, line: 152, column: 9)
!442 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !439)
!443 = !DILocation(line: 156, column: 9, scope: !440)
!444 = !DILocation(line: 0, scope: !99, inlinedAt: !445)
!445 = distinct !DILocation(line: 161, column: 9, scope: !446)
!446 = distinct !DILexicalBlock(scope: !447, file: !295, line: 158, column: 19)
!447 = distinct !DILexicalBlock(scope: !315, file: !295, line: 158, column: 9)
!448 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !445)
!449 = !DILocation(line: 162, column: 9, scope: !446)
!450 = !DILocation(line: 0, scope: !335)
!451 = !DILocation(line: 0, scope: !99, inlinedAt: !452)
!452 = distinct !DILocation(line: 170, column: 9, scope: !335)
!453 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !452)
!454 = !DILocation(line: 0, scope: !338)
!455 = !DILocation(line: 0, scope: !99, inlinedAt: !456)
!456 = distinct !DILocation(line: 176, column: 9, scope: !338)
!457 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !456)
!458 = !DILocation(line: 183, column: 9, scope: !459)
!459 = distinct !DILexicalBlock(scope: !460, file: !295, line: 182, column: 19)
!460 = distinct !DILexicalBlock(scope: !315, file: !295, line: 182, column: 9)
!461 = !DILocation(line: 0, scope: !294, inlinedAt: !462)
!462 = distinct !DILocation(line: 184, column: 34, scope: !459)
!463 = !DILocation(line: 19, column: 5, scope: !303, inlinedAt: !462)
!464 = !DILocation(line: 20, column: 22, scope: !305, inlinedAt: !462)
!465 = !DILocation(line: 20, column: 19, scope: !305, inlinedAt: !462)
!466 = !DILocation(line: 19, column: 17, scope: !306, inlinedAt: !462)
!467 = !DILocation(line: 19, column: 19, scope: !306, inlinedAt: !462)
!468 = distinct !{!468, !463, !469, !312, !313}
!469 = !DILocation(line: 21, column: 5, scope: !303, inlinedAt: !462)
!470 = !DILocation(line: 0, scope: !99, inlinedAt: !471)
!471 = distinct !DILocation(line: 184, column: 9, scope: !459)
!472 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !471)
!473 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !471)
!474 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !471)
!475 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !471)
!476 = !DILocation(line: 185, column: 9, scope: !459)
!477 = !DILocation(line: 190, column: 9, scope: !478)
!478 = distinct !DILexicalBlock(scope: !479, file: !295, line: 189, column: 19)
!479 = distinct !DILexicalBlock(scope: !315, file: !295, line: 189, column: 9)
!480 = !DILocation(line: 192, column: 9, scope: !478)
!481 = !DILocation(line: 0, scope: !294, inlinedAt: !482)
!482 = distinct !DILocation(line: 193, column: 34, scope: !478)
!483 = !DILocation(line: 19, column: 5, scope: !303, inlinedAt: !482)
!484 = !DILocation(line: 20, column: 22, scope: !305, inlinedAt: !482)
!485 = !DILocation(line: 20, column: 19, scope: !305, inlinedAt: !482)
!486 = !DILocation(line: 19, column: 17, scope: !306, inlinedAt: !482)
!487 = !DILocation(line: 19, column: 19, scope: !306, inlinedAt: !482)
!488 = distinct !{!488, !483, !489, !312, !313}
!489 = !DILocation(line: 21, column: 5, scope: !303, inlinedAt: !482)
!490 = !DILocation(line: 0, scope: !99, inlinedAt: !491)
!491 = distinct !DILocation(line: 193, column: 9, scope: !478)
!492 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !491)
!493 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !491)
!494 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !491)
!495 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !491)
!496 = !DILocation(line: 194, column: 9, scope: !478)
!497 = !DILocation(line: 199, column: 9, scope: !498)
!498 = distinct !DILexicalBlock(scope: !499, file: !295, line: 198, column: 19)
!499 = distinct !DILexicalBlock(scope: !315, file: !295, line: 198, column: 9)
!500 = !DILocation(line: 201, column: 9, scope: !498)
!501 = !DILocation(line: 0, scope: !294, inlinedAt: !502)
!502 = distinct !DILocation(line: 202, column: 34, scope: !498)
!503 = !DILocation(line: 19, column: 5, scope: !303, inlinedAt: !502)
!504 = !DILocation(line: 20, column: 22, scope: !305, inlinedAt: !502)
!505 = !DILocation(line: 20, column: 19, scope: !305, inlinedAt: !502)
!506 = !DILocation(line: 19, column: 17, scope: !306, inlinedAt: !502)
!507 = !DILocation(line: 19, column: 19, scope: !306, inlinedAt: !502)
!508 = distinct !{!508, !503, !509, !312, !313}
!509 = !DILocation(line: 21, column: 5, scope: !303, inlinedAt: !502)
!510 = !DILocation(line: 0, scope: !99, inlinedAt: !511)
!511 = distinct !DILocation(line: 202, column: 9, scope: !498)
!512 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !511)
!513 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !511)
!514 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !511)
!515 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !511)
!516 = !DILocation(line: 203, column: 9, scope: !498)
!517 = !DILocation(line: 208, column: 9, scope: !518)
!518 = distinct !DILexicalBlock(scope: !519, file: !295, line: 207, column: 19)
!519 = distinct !DILexicalBlock(scope: !315, file: !295, line: 207, column: 9)
!520 = !DILocation(line: 213, column: 20, scope: !518)
!521 = !DILocation(line: 0, scope: !99, inlinedAt: !522)
!522 = distinct !DILocation(line: 214, column: 9, scope: !518)
!523 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !522)
!524 = !DILocation(line: 215, column: 9, scope: !518)
!525 = !DILocation(line: 220, column: 9, scope: !526)
!526 = distinct !DILexicalBlock(scope: !527, file: !295, line: 219, column: 19)
!527 = distinct !DILexicalBlock(scope: !315, file: !295, line: 219, column: 9)
!528 = !DILocation(line: 230, column: 38, scope: !526)
!529 = !DILocation(line: 233, column: 13, scope: !530)
!530 = distinct !DILexicalBlock(scope: !531, file: !295, line: 232, column: 30)
!531 = distinct !DILexicalBlock(scope: !526, file: !295, line: 232, column: 13)
!532 = !DILocation(line: 235, column: 36, scope: !526)
!533 = !DILocation(line: 0, scope: !294, inlinedAt: !534)
!534 = distinct !DILocation(line: 237, column: 34, scope: !526)
!535 = !DILocation(line: 19, column: 5, scope: !303, inlinedAt: !534)
!536 = !DILocation(line: 20, column: 22, scope: !305, inlinedAt: !534)
!537 = !DILocation(line: 20, column: 19, scope: !305, inlinedAt: !534)
!538 = !DILocation(line: 19, column: 17, scope: !306, inlinedAt: !534)
!539 = !DILocation(line: 19, column: 19, scope: !306, inlinedAt: !534)
!540 = distinct !{!540, !535, !541, !312, !313}
!541 = !DILocation(line: 21, column: 5, scope: !303, inlinedAt: !534)
!542 = !DILocation(line: 0, scope: !99, inlinedAt: !543)
!543 = distinct !DILocation(line: 237, column: 9, scope: !526)
!544 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !543)
!545 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !543)
!546 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !543)
!547 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !543)
!548 = !DILocation(line: 238, column: 9, scope: !526)
!549 = !DILocation(line: 243, column: 9, scope: !550)
!550 = distinct !DILexicalBlock(scope: !551, file: !295, line: 242, column: 19)
!551 = distinct !DILexicalBlock(scope: !315, file: !295, line: 242, column: 9)
!552 = !DILocation(line: 248, column: 29, scope: !550)
!553 = !DILocation(line: 248, column: 40, scope: !550)
!554 = !DILocation(line: 248, column: 20, scope: !550)
!555 = !DILocation(line: 0, scope: !99, inlinedAt: !556)
!556 = distinct !DILocation(line: 249, column: 9, scope: !550)
!557 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !556)
!558 = !DILocation(line: 250, column: 9, scope: !550)
!559 = !DILocation(line: 255, column: 9, scope: !560)
!560 = distinct !DILexicalBlock(scope: !561, file: !295, line: 254, column: 19)
!561 = distinct !DILexicalBlock(scope: !315, file: !295, line: 254, column: 9)
!562 = !DILocation(line: 265, column: 9, scope: !563)
!563 = distinct !DILexicalBlock(scope: !560, file: !295, line: 265, column: 9)
!564 = !DILocation(line: 266, column: 23, scope: !565)
!565 = distinct !DILexicalBlock(scope: !566, file: !295, line: 265, column: 42)
!566 = distinct !DILexicalBlock(scope: !563, file: !295, line: 265, column: 9)
!567 = !DILocation(line: 267, column: 13, scope: !565)
!568 = !DILocation(line: 267, column: 42, scope: !565)
!569 = !DILocation(line: 269, column: 17, scope: !570)
!570 = distinct !DILexicalBlock(scope: !571, file: !295, line: 268, column: 34)
!571 = distinct !DILexicalBlock(scope: !565, file: !295, line: 268, column: 17)
!572 = !DILocation(line: 271, column: 29, scope: !565)
!573 = !DILocation(line: 271, column: 13, scope: !565)
!574 = !DILocation(line: 271, column: 40, scope: !565)
!575 = !DILocation(line: 265, column: 37, scope: !566)
!576 = !DILocation(line: 265, column: 24, scope: !566)
!577 = distinct !{!577, !562, !578, !312, !313}
!578 = !DILocation(line: 272, column: 9, scope: !563)
!579 = !DILocation(line: 0, scope: !294, inlinedAt: !580)
!580 = distinct !DILocation(line: 274, column: 34, scope: !560)
!581 = !DILocation(line: 20, column: 22, scope: !305, inlinedAt: !580)
!582 = !DILocation(line: 20, column: 19, scope: !305, inlinedAt: !580)
!583 = !DILocation(line: 19, column: 17, scope: !306, inlinedAt: !580)
!584 = !DILocation(line: 19, column: 19, scope: !306, inlinedAt: !580)
!585 = !DILocation(line: 19, column: 5, scope: !303, inlinedAt: !580)
!586 = distinct !{!586, !585, !587, !312, !313}
!587 = !DILocation(line: 21, column: 5, scope: !303, inlinedAt: !580)
!588 = !DILocation(line: 0, scope: !99, inlinedAt: !589)
!589 = distinct !DILocation(line: 274, column: 9, scope: !560)
!590 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !589)
!591 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !589)
!592 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !589)
!593 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !589)
!594 = !DILocation(line: 275, column: 9, scope: !560)
!595 = !DILocation(line: 280, column: 9, scope: !596)
!596 = distinct !DILexicalBlock(scope: !597, file: !295, line: 279, column: 19)
!597 = distinct !DILexicalBlock(scope: !315, file: !295, line: 279, column: 9)
!598 = !DILocation(line: 285, column: 20, scope: !596)
!599 = !DILocation(line: 0, scope: !99, inlinedAt: !600)
!600 = distinct !DILocation(line: 286, column: 9, scope: !596)
!601 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !600)
!602 = !DILocation(line: 287, column: 9, scope: !596)
!603 = !DILocation(line: 292, column: 9, scope: !604)
!604 = distinct !DILexicalBlock(scope: !605, file: !295, line: 291, column: 19)
!605 = distinct !DILexicalBlock(scope: !315, file: !295, line: 291, column: 9)
!606 = !DILocation(line: 299, column: 28, scope: !604)
!607 = !DILocation(line: 0, scope: !99, inlinedAt: !608)
!608 = distinct !DILocation(line: 300, column: 9, scope: !604)
!609 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !608)
!610 = !DILocation(line: 301, column: 9, scope: !604)
!611 = !DILocation(line: 0, scope: !99, inlinedAt: !612)
!612 = distinct !DILocation(line: 304, column: 5, scope: !315)
!613 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !612)
!614 = !DILocation(line: 305, column: 1, scope: !315)
!615 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !340)
!616 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !340)
!617 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !340)
!618 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !340)
!619 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !340)
!620 = !DISubprogram(name: "jc_Util_arrayFillNonAtomic", scope: !6, file: !6, line: 126, type: !621, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!621 = !DISubroutineType(types: !622)
!622 = !{!8, !104, !8, !8, !5}
!623 = distinct !DISubprogram(name: "reset_pool", scope: !64, file: !64, line: 18, type: !624, scopeLine: 18, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !626)
!624 = !DISubroutineType(types: !625)
!625 = !{null}
!626 = !{!627}
!627 = !DILocalVariable(name: "i", scope: !623, file: !64, line: 19, type: !8)
!628 = !DILocation(line: 0, scope: !623)
!629 = !DILocation(line: 20, column: 5, scope: !630)
!630 = distinct !DILexicalBlock(scope: !623, file: !64, line: 20, column: 5)
!631 = !DILocation(line: 21, column: 9, scope: !632)
!632 = distinct !DILexicalBlock(scope: !633, file: !64, line: 20, column: 43)
!633 = distinct !DILexicalBlock(scope: !630, file: !64, line: 20, column: 5)
!634 = !DILocation(line: 20, column: 17, scope: !633)
!635 = !DILocation(line: 20, column: 19, scope: !633)
!636 = !DILocation(line: 22, column: 19, scope: !632)
!637 = distinct !{!637, !629, !638, !312, !313}
!638 = !DILocation(line: 25, column: 5, scope: !630)
!639 = !DILocation(line: 26, column: 1, scope: !623)
!640 = distinct !DISubprogram(name: "test_object_pool", scope: !64, file: !64, line: 28, type: !142, scopeLine: 28, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !641)
!641 = !{!642, !643, !644, !645, !646, !647, !648, !649}
!642 = !DILocalVariable(name: "apdu", arg: 1, scope: !640, file: !64, line: 28, type: !102)
!643 = !DILocalVariable(name: "buffer", arg: 2, scope: !640, file: !64, line: 28, type: !104)
!644 = !DILocalVariable(name: "p1", arg: 3, scope: !640, file: !64, line: 28, type: !5)
!645 = !DILocalVariable(name: "i", scope: !640, file: !64, line: 29, type: !8)
!646 = !DILocalVariable(name: "count", scope: !640, file: !64, line: 30, type: !8)
!647 = !DILocalVariable(name: "found", scope: !640, file: !64, line: 31, type: !8)
!648 = !DILocalVariable(name: "sum", scope: !640, file: !64, line: 32, type: !8)
!649 = !DILocalVariable(name: "max_x", scope: !640, file: !64, line: 33, type: !8)
!650 = !DILocation(line: 0, scope: !640)
!651 = !DILocation(line: 36, column: 9, scope: !640)
!652 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !653)
!653 = distinct !DILocation(line: 37, column: 9, scope: !654)
!654 = distinct !DILexicalBlock(scope: !655, file: !64, line: 36, column: 18)
!655 = distinct !DILexicalBlock(scope: !640, file: !64, line: 36, column: 9)
!656 = !DILocation(line: 0, scope: !623, inlinedAt: !653)
!657 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !653)
!658 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !653)
!659 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !653)
!660 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !653)
!661 = distinct !{!661, !660, !662, !312, !313}
!662 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !653)
!663 = !DILocation(line: 38, column: 24, scope: !654)
!664 = !{!665, !114, i64 4}
!665 = !{!"pool_obj_t", !666, i64 0, !666, i64 2, !114, i64 4, !114, i64 5}
!666 = !{!"short", !114, i64 0}
!667 = !DILocation(line: 0, scope: !99, inlinedAt: !668)
!668 = distinct !DILocation(line: 39, column: 9, scope: !654)
!669 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !668)
!670 = !DILocation(line: 40, column: 9, scope: !654)
!671 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !672)
!672 = distinct !DILocation(line: 43, column: 9, scope: !673)
!673 = distinct !DILexicalBlock(scope: !674, file: !64, line: 42, column: 18)
!674 = distinct !DILexicalBlock(scope: !640, file: !64, line: 42, column: 9)
!675 = !DILocation(line: 0, scope: !623, inlinedAt: !672)
!676 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !672)
!677 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !672)
!678 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !672)
!679 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !672)
!680 = distinct !{!680, !679, !681, !312, !313}
!681 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !672)
!682 = !DILocation(line: 44, column: 24, scope: !673)
!683 = !DILocation(line: 0, scope: !99, inlinedAt: !684)
!684 = distinct !DILocation(line: 45, column: 9, scope: !673)
!685 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !684)
!686 = !DILocation(line: 46, column: 9, scope: !673)
!687 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !688)
!688 = distinct !DILocation(line: 49, column: 9, scope: !689)
!689 = distinct !DILexicalBlock(scope: !690, file: !64, line: 48, column: 18)
!690 = distinct !DILexicalBlock(scope: !640, file: !64, line: 48, column: 9)
!691 = !DILocation(line: 0, scope: !623, inlinedAt: !688)
!692 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !688)
!693 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !688)
!694 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !688)
!695 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !688)
!696 = distinct !{!696, !695, !697, !312, !313}
!697 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !688)
!698 = !DILocation(line: 51, column: 24, scope: !689)
!699 = !DILocation(line: 0, scope: !99, inlinedAt: !700)
!700 = distinct !DILocation(line: 52, column: 9, scope: !689)
!701 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !700)
!702 = !DILocation(line: 53, column: 9, scope: !689)
!703 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !704)
!704 = distinct !DILocation(line: 58, column: 9, scope: !705)
!705 = distinct !DILexicalBlock(scope: !706, file: !64, line: 57, column: 18)
!706 = distinct !DILexicalBlock(scope: !640, file: !64, line: 57, column: 9)
!707 = !DILocation(line: 0, scope: !623, inlinedAt: !704)
!708 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !704)
!709 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !704)
!710 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !704)
!711 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !704)
!712 = distinct !{!712, !711, !713, !312, !313}
!713 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !704)
!714 = !DILocation(line: 61, column: 25, scope: !715)
!715 = distinct !DILexicalBlock(scope: !716, file: !64, line: 61, column: 17)
!716 = distinct !DILexicalBlock(scope: !717, file: !64, line: 60, column: 47)
!717 = distinct !DILexicalBlock(scope: !718, file: !64, line: 60, column: 9)
!718 = distinct !DILexicalBlock(scope: !705, file: !64, line: 60, column: 9)
!719 = !DILocation(line: 61, column: 17, scope: !715)
!720 = !DILocation(line: 61, column: 17, scope: !716)
!721 = !DILocation(line: 60, column: 21, scope: !717)
!722 = !DILocation(line: 60, column: 23, scope: !717)
!723 = !DILocation(line: 60, column: 9, scope: !718)
!724 = distinct !{!724, !723, !725, !312, !313}
!725 = !DILocation(line: 64, column: 9, scope: !718)
!726 = !DILocation(line: 0, scope: !99, inlinedAt: !727)
!727 = distinct !DILocation(line: 65, column: 9, scope: !705)
!728 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !727)
!729 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !727)
!730 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !727)
!731 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !727)
!732 = !DILocation(line: 66, column: 9, scope: !705)
!733 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !734)
!734 = distinct !DILocation(line: 69, column: 9, scope: !735)
!735 = distinct !DILexicalBlock(scope: !736, file: !64, line: 68, column: 18)
!736 = distinct !DILexicalBlock(scope: !640, file: !64, line: 68, column: 9)
!737 = !DILocation(line: 0, scope: !623, inlinedAt: !734)
!738 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !734)
!739 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !734)
!740 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !734)
!741 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !734)
!742 = distinct !{!742, !741, !743, !312, !313}
!743 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !734)
!744 = !DILocation(line: 70, column: 24, scope: !735)
!745 = !DILocation(line: 71, column: 24, scope: !735)
!746 = !DILocation(line: 73, column: 9, scope: !747)
!747 = distinct !DILexicalBlock(scope: !735, file: !64, line: 73, column: 9)
!748 = !DILocation(line: 74, column: 25, scope: !749)
!749 = distinct !DILexicalBlock(scope: !750, file: !64, line: 74, column: 17)
!750 = distinct !DILexicalBlock(scope: !751, file: !64, line: 73, column: 47)
!751 = distinct !DILexicalBlock(scope: !747, file: !64, line: 73, column: 9)
!752 = !DILocation(line: 74, column: 17, scope: !749)
!753 = !DILocation(line: 74, column: 17, scope: !750)
!754 = !DILocation(line: 73, column: 21, scope: !751)
!755 = !DILocation(line: 73, column: 23, scope: !751)
!756 = distinct !{!756, !746, !757, !312, !313}
!757 = !DILocation(line: 77, column: 9, scope: !747)
!758 = !DILocation(line: 0, scope: !99, inlinedAt: !759)
!759 = distinct !DILocation(line: 78, column: 9, scope: !735)
!760 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !759)
!761 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !759)
!762 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !759)
!763 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !759)
!764 = !DILocation(line: 79, column: 9, scope: !735)
!765 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !766)
!766 = distinct !DILocation(line: 82, column: 9, scope: !767)
!767 = distinct !DILexicalBlock(scope: !768, file: !64, line: 81, column: 18)
!768 = distinct !DILexicalBlock(scope: !640, file: !64, line: 81, column: 9)
!769 = !DILocation(line: 0, scope: !623, inlinedAt: !766)
!770 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !766)
!771 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !766)
!772 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !766)
!773 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !766)
!774 = distinct !{!774, !773, !775, !312, !313}
!775 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !766)
!776 = !DILocation(line: 83, column: 24, scope: !767)
!777 = !DILocation(line: 84, column: 24, scope: !767)
!778 = !DILocation(line: 85, column: 24, scope: !767)
!779 = !DILocation(line: 86, column: 24, scope: !767)
!780 = !DILocation(line: 88, column: 9, scope: !781)
!781 = distinct !DILexicalBlock(scope: !767, file: !64, line: 88, column: 9)
!782 = !DILocation(line: 89, column: 25, scope: !783)
!783 = distinct !DILexicalBlock(scope: !784, file: !64, line: 89, column: 17)
!784 = distinct !DILexicalBlock(scope: !785, file: !64, line: 88, column: 47)
!785 = distinct !DILexicalBlock(scope: !781, file: !64, line: 88, column: 9)
!786 = !DILocation(line: 89, column: 17, scope: !783)
!787 = !DILocation(line: 89, column: 17, scope: !784)
!788 = !DILocation(line: 88, column: 21, scope: !785)
!789 = !DILocation(line: 88, column: 23, scope: !785)
!790 = distinct !{!790, !780, !791, !312, !313}
!791 = !DILocation(line: 92, column: 9, scope: !781)
!792 = !DILocation(line: 0, scope: !99, inlinedAt: !793)
!793 = distinct !DILocation(line: 93, column: 9, scope: !767)
!794 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !793)
!795 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !793)
!796 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !793)
!797 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !793)
!798 = !DILocation(line: 94, column: 9, scope: !767)
!799 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !800)
!800 = distinct !DILocation(line: 99, column: 9, scope: !801)
!801 = distinct !DILexicalBlock(scope: !802, file: !64, line: 98, column: 18)
!802 = distinct !DILexicalBlock(scope: !640, file: !64, line: 98, column: 9)
!803 = !DILocation(line: 0, scope: !623, inlinedAt: !800)
!804 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !800)
!805 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !800)
!806 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !800)
!807 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !800)
!808 = distinct !{!808, !807, !809, !312, !313}
!809 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !800)
!810 = !DILocation(line: 101, column: 21, scope: !811)
!811 = distinct !DILexicalBlock(scope: !812, file: !64, line: 101, column: 9)
!812 = distinct !DILexicalBlock(scope: !801, file: !64, line: 101, column: 9)
!813 = !DILocation(line: 102, column: 26, scope: !814)
!814 = distinct !DILexicalBlock(scope: !815, file: !64, line: 102, column: 17)
!815 = distinct !DILexicalBlock(scope: !811, file: !64, line: 101, column: 47)
!816 = !DILocation(line: 102, column: 18, scope: !814)
!817 = !DILocation(line: 102, column: 17, scope: !815)
!818 = !DILocation(line: 101, column: 42, scope: !811)
!819 = !DILocation(line: 101, column: 23, scope: !811)
!820 = !DILocation(line: 101, column: 9, scope: !812)
!821 = distinct !{!821, !820, !822, !312, !313}
!822 = !DILocation(line: 106, column: 9, scope: !812)
!823 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !824)
!824 = distinct !DILocation(line: 107, column: 9, scope: !801)
!825 = !DILocation(line: 0, scope: !99, inlinedAt: !824)
!826 = !DILocation(line: 108, column: 9, scope: !801)
!827 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !828)
!828 = distinct !DILocation(line: 111, column: 9, scope: !829)
!829 = distinct !DILexicalBlock(scope: !830, file: !64, line: 110, column: 18)
!830 = distinct !DILexicalBlock(scope: !640, file: !64, line: 110, column: 9)
!831 = !DILocation(line: 0, scope: !623, inlinedAt: !828)
!832 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !828)
!833 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !828)
!834 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !828)
!835 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !828)
!836 = distinct !{!836, !835, !837, !312, !313}
!837 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !828)
!838 = !DILocation(line: 112, column: 24, scope: !829)
!839 = !DILocation(line: 113, column: 24, scope: !829)
!840 = !DILocation(line: 115, column: 9, scope: !841)
!841 = distinct !DILexicalBlock(scope: !829, file: !64, line: 115, column: 9)
!842 = !DILocation(line: 115, column: 21, scope: !843)
!843 = distinct !DILexicalBlock(scope: !841, file: !64, line: 115, column: 9)
!844 = !DILocation(line: 116, column: 26, scope: !845)
!845 = distinct !DILexicalBlock(scope: !846, file: !64, line: 116, column: 17)
!846 = distinct !DILexicalBlock(scope: !843, file: !64, line: 115, column: 47)
!847 = !DILocation(line: 116, column: 18, scope: !845)
!848 = !DILocation(line: 116, column: 17, scope: !846)
!849 = !DILocation(line: 115, column: 42, scope: !843)
!850 = !DILocation(line: 115, column: 23, scope: !843)
!851 = distinct !{!851, !840, !852, !312, !313}
!852 = !DILocation(line: 120, column: 9, scope: !841)
!853 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !854)
!854 = distinct !DILocation(line: 121, column: 9, scope: !829)
!855 = !DILocation(line: 0, scope: !99, inlinedAt: !854)
!856 = !DILocation(line: 122, column: 9, scope: !829)
!857 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !858)
!858 = distinct !DILocation(line: 125, column: 9, scope: !859)
!859 = distinct !DILexicalBlock(scope: !860, file: !64, line: 124, column: 18)
!860 = distinct !DILexicalBlock(scope: !640, file: !64, line: 124, column: 9)
!861 = !DILocation(line: 0, scope: !623, inlinedAt: !858)
!862 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !858)
!863 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !858)
!864 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !858)
!865 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !858)
!866 = distinct !{!866, !865, !867, !312, !313}
!867 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !858)
!868 = !DILocation(line: 126, column: 24, scope: !859)
!869 = !DILocation(line: 127, column: 24, scope: !859)
!870 = !DILocation(line: 128, column: 24, scope: !859)
!871 = !DILocation(line: 129, column: 24, scope: !859)
!872 = !DILocation(line: 131, column: 9, scope: !873)
!873 = distinct !DILexicalBlock(scope: !859, file: !64, line: 131, column: 9)
!874 = !DILocation(line: 131, column: 21, scope: !875)
!875 = distinct !DILexicalBlock(scope: !873, file: !64, line: 131, column: 9)
!876 = !DILocation(line: 132, column: 26, scope: !877)
!877 = distinct !DILexicalBlock(scope: !878, file: !64, line: 132, column: 17)
!878 = distinct !DILexicalBlock(scope: !875, file: !64, line: 131, column: 47)
!879 = !DILocation(line: 132, column: 18, scope: !877)
!880 = !DILocation(line: 132, column: 17, scope: !878)
!881 = !DILocation(line: 131, column: 42, scope: !875)
!882 = !DILocation(line: 131, column: 23, scope: !875)
!883 = distinct !{!883, !872, !884, !312, !313}
!884 = !DILocation(line: 136, column: 9, scope: !873)
!885 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !886)
!886 = distinct !DILocation(line: 137, column: 9, scope: !859)
!887 = !DILocation(line: 0, scope: !99, inlinedAt: !886)
!888 = !DILocation(line: 138, column: 9, scope: !859)
!889 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !890)
!890 = distinct !DILocation(line: 143, column: 9, scope: !891)
!891 = distinct !DILexicalBlock(scope: !892, file: !64, line: 142, column: 18)
!892 = distinct !DILexicalBlock(scope: !640, file: !64, line: 142, column: 9)
!893 = !DILocation(line: 0, scope: !623, inlinedAt: !890)
!894 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !890)
!895 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !890)
!896 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !890)
!897 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !890)
!898 = distinct !{!898, !897, !899, !312, !313}
!899 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !890)
!900 = !DILocation(line: 144, column: 24, scope: !891)
!901 = !DILocation(line: 147, column: 9, scope: !902)
!902 = distinct !DILexicalBlock(scope: !891, file: !64, line: 147, column: 9)
!903 = !DILocation(line: 147, column: 42, scope: !904)
!904 = distinct !DILexicalBlock(scope: !902, file: !64, line: 147, column: 9)
!905 = !DILocation(line: 147, column: 23, scope: !904)
!906 = distinct !{!906, !901, !907, !312, !313}
!907 = !DILocation(line: 152, column: 9, scope: !902)
!908 = !DILocation(line: 147, column: 21, scope: !904)
!909 = !DILocation(line: 148, column: 26, scope: !910)
!910 = distinct !DILexicalBlock(scope: !911, file: !64, line: 148, column: 17)
!911 = distinct !DILexicalBlock(scope: !904, file: !64, line: 147, column: 47)
!912 = !DILocation(line: 148, column: 18, scope: !910)
!913 = !DILocation(line: 148, column: 17, scope: !911)
!914 = !DILocation(line: 0, scope: !891)
!915 = !DILocation(line: 154, column: 19, scope: !916)
!916 = distinct !DILexicalBlock(scope: !891, file: !64, line: 154, column: 13)
!917 = !DILocation(line: 154, column: 13, scope: !891)
!918 = !DILocation(line: 155, column: 13, scope: !919)
!919 = distinct !DILexicalBlock(scope: !916, file: !64, line: 154, column: 25)
!920 = !DILocation(line: 155, column: 27, scope: !919)
!921 = !{!665, !666, i64 0}
!922 = !DILocation(line: 156, column: 25, scope: !919)
!923 = !DILocation(line: 156, column: 27, scope: !919)
!924 = !{!665, !666, i64 2}
!925 = !DILocation(line: 157, column: 25, scope: !919)
!926 = !DILocation(line: 157, column: 32, scope: !919)
!927 = !DILocation(line: 158, column: 25, scope: !919)
!928 = !DILocation(line: 158, column: 30, scope: !919)
!929 = !{!665, !114, i64 5}
!930 = !DILocation(line: 159, column: 9, scope: !919)
!931 = !DILocation(line: 160, column: 42, scope: !891)
!932 = !DILocation(line: 0, scope: !99, inlinedAt: !933)
!933 = distinct !DILocation(line: 160, column: 9, scope: !891)
!934 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !933)
!935 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !933)
!936 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !933)
!937 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !933)
!938 = !DILocation(line: 161, column: 9, scope: !891)
!939 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !940)
!940 = distinct !DILocation(line: 164, column: 9, scope: !941)
!941 = distinct !DILexicalBlock(scope: !942, file: !64, line: 163, column: 19)
!942 = distinct !DILexicalBlock(scope: !640, file: !64, line: 163, column: 9)
!943 = !DILocation(line: 0, scope: !623, inlinedAt: !940)
!944 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !940)
!945 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !940)
!946 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !940)
!947 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !940)
!948 = distinct !{!948, !947, !949, !312, !313}
!949 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !940)
!950 = !DILocation(line: 165, column: 24, scope: !941)
!951 = !DILocation(line: 167, column: 9, scope: !952)
!952 = distinct !DILexicalBlock(scope: !941, file: !64, line: 167, column: 9)
!953 = !DILocation(line: 167, column: 42, scope: !954)
!954 = distinct !DILexicalBlock(scope: !952, file: !64, line: 167, column: 9)
!955 = !DILocation(line: 167, column: 23, scope: !954)
!956 = distinct !{!956, !951, !957, !312, !313}
!957 = !DILocation(line: 172, column: 9, scope: !952)
!958 = !DILocation(line: 167, column: 21, scope: !954)
!959 = !DILocation(line: 168, column: 26, scope: !960)
!960 = distinct !DILexicalBlock(scope: !961, file: !64, line: 168, column: 17)
!961 = distinct !DILexicalBlock(scope: !954, file: !64, line: 167, column: 47)
!962 = !DILocation(line: 168, column: 18, scope: !960)
!963 = !DILocation(line: 168, column: 17, scope: !961)
!964 = !DILocation(line: 0, scope: !941)
!965 = !DILocation(line: 173, column: 19, scope: !966)
!966 = distinct !DILexicalBlock(scope: !941, file: !64, line: 173, column: 13)
!967 = !DILocation(line: 173, column: 13, scope: !941)
!968 = !DILocation(line: 174, column: 13, scope: !969)
!969 = distinct !DILexicalBlock(scope: !966, file: !64, line: 173, column: 25)
!970 = !DILocation(line: 174, column: 27, scope: !969)
!971 = !DILocation(line: 175, column: 25, scope: !969)
!972 = !DILocation(line: 175, column: 27, scope: !969)
!973 = !DILocation(line: 176, column: 25, scope: !969)
!974 = !DILocation(line: 176, column: 32, scope: !969)
!975 = !DILocation(line: 177, column: 25, scope: !969)
!976 = !DILocation(line: 177, column: 30, scope: !969)
!977 = !DILocation(line: 178, column: 9, scope: !969)
!978 = !DILocation(line: 179, column: 42, scope: !941)
!979 = !DILocation(line: 0, scope: !99, inlinedAt: !980)
!980 = distinct !DILocation(line: 179, column: 9, scope: !941)
!981 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !980)
!982 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !980)
!983 = !DILocation(line: 180, column: 9, scope: !941)
!984 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !985)
!985 = distinct !DILocation(line: 185, column: 9, scope: !986)
!986 = distinct !DILexicalBlock(scope: !987, file: !64, line: 184, column: 19)
!987 = distinct !DILexicalBlock(scope: !640, file: !64, line: 184, column: 9)
!988 = !DILocation(line: 0, scope: !623, inlinedAt: !985)
!989 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !985)
!990 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !985)
!991 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !985)
!992 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !985)
!993 = distinct !{!993, !992, !994, !312, !313}
!994 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !985)
!995 = !DILocation(line: 186, column: 19, scope: !986)
!996 = !DILocation(line: 186, column: 40, scope: !986)
!997 = !DILocation(line: 187, column: 19, scope: !986)
!998 = !DILocation(line: 187, column: 40, scope: !986)
!999 = !DILocation(line: 188, column: 19, scope: !986)
!1000 = !DILocation(line: 188, column: 40, scope: !986)
!1001 = !DILocation(line: 189, column: 19, scope: !986)
!1002 = !DILocation(line: 189, column: 40, scope: !986)
!1003 = !DILocation(line: 191, column: 9, scope: !1004)
!1004 = distinct !DILexicalBlock(scope: !986, file: !64, line: 191, column: 9)
!1005 = !DILocation(line: 192, column: 18, scope: !1006)
!1006 = distinct !DILexicalBlock(scope: !1007, file: !64, line: 192, column: 17)
!1007 = distinct !DILexicalBlock(scope: !1008, file: !64, line: 191, column: 47)
!1008 = distinct !DILexicalBlock(scope: !1004, file: !64, line: 191, column: 9)
!1009 = !DILocation(line: 192, column: 26, scope: !1006)
!1010 = !DILocation(line: 192, column: 17, scope: !1007)
!1011 = !DILocation(line: 193, column: 33, scope: !1007)
!1012 = !DILocation(line: 193, column: 35, scope: !1007)
!1013 = !DILocation(line: 193, column: 23, scope: !1007)
!1014 = !DILocation(line: 194, column: 9, scope: !1007)
!1015 = !DILocation(line: 191, column: 21, scope: !1008)
!1016 = !DILocation(line: 191, column: 23, scope: !1008)
!1017 = distinct !{!1017, !1003, !1018, !312, !313}
!1018 = !DILocation(line: 194, column: 9, scope: !1004)
!1019 = !DILocation(line: 195, column: 42, scope: !986)
!1020 = !DILocation(line: 195, column: 54, scope: !986)
!1021 = !DILocation(line: 195, column: 44, scope: !986)
!1022 = !DILocation(line: 0, scope: !99, inlinedAt: !1023)
!1023 = distinct !DILocation(line: 195, column: 9, scope: !986)
!1024 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1023)
!1025 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1023)
!1026 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1023)
!1027 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1023)
!1028 = !DILocation(line: 196, column: 9, scope: !986)
!1029 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1030)
!1030 = distinct !DILocation(line: 199, column: 9, scope: !1031)
!1031 = distinct !DILexicalBlock(scope: !1032, file: !64, line: 198, column: 19)
!1032 = distinct !DILexicalBlock(scope: !640, file: !64, line: 198, column: 9)
!1033 = !DILocation(line: 0, scope: !623, inlinedAt: !1030)
!1034 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1030)
!1035 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1030)
!1036 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1030)
!1037 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1030)
!1038 = distinct !{!1038, !1037, !1039, !312, !313}
!1039 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1030)
!1040 = !DILocation(line: 200, column: 19, scope: !1031)
!1041 = !DILocation(line: 200, column: 40, scope: !1031)
!1042 = !DILocation(line: 201, column: 19, scope: !1031)
!1043 = !DILocation(line: 201, column: 40, scope: !1031)
!1044 = !DILocation(line: 202, column: 19, scope: !1031)
!1045 = !DILocation(line: 202, column: 40, scope: !1031)
!1046 = !DILocation(line: 203, column: 19, scope: !1031)
!1047 = !DILocation(line: 203, column: 40, scope: !1031)
!1048 = !DILocation(line: 204, column: 9, scope: !1049)
!1049 = distinct !DILexicalBlock(scope: !1031, file: !64, line: 204, column: 9)
!1050 = !DILocation(line: 205, column: 18, scope: !1051)
!1051 = distinct !DILexicalBlock(scope: !1052, file: !64, line: 205, column: 17)
!1052 = distinct !DILexicalBlock(scope: !1053, file: !64, line: 204, column: 47)
!1053 = distinct !DILexicalBlock(scope: !1049, file: !64, line: 204, column: 9)
!1054 = !DILocation(line: 205, column: 26, scope: !1051)
!1055 = !DILocation(line: 205, column: 17, scope: !1052)
!1056 = !DILocation(line: 206, column: 33, scope: !1052)
!1057 = !DILocation(line: 206, column: 35, scope: !1052)
!1058 = !DILocation(line: 206, column: 23, scope: !1052)
!1059 = !DILocation(line: 207, column: 9, scope: !1052)
!1060 = !DILocation(line: 204, column: 21, scope: !1053)
!1061 = !DILocation(line: 204, column: 23, scope: !1053)
!1062 = distinct !{!1062, !1048, !1063, !312, !313}
!1063 = !DILocation(line: 207, column: 9, scope: !1049)
!1064 = !DILocation(line: 209, column: 42, scope: !1031)
!1065 = !DILocation(line: 209, column: 54, scope: !1031)
!1066 = !DILocation(line: 209, column: 44, scope: !1031)
!1067 = !DILocation(line: 0, scope: !99, inlinedAt: !1068)
!1068 = distinct !DILocation(line: 209, column: 9, scope: !1031)
!1069 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1068)
!1070 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1068)
!1071 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1068)
!1072 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1068)
!1073 = !DILocation(line: 210, column: 9, scope: !1031)
!1074 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1075)
!1075 = distinct !DILocation(line: 215, column: 9, scope: !1076)
!1076 = distinct !DILexicalBlock(scope: !1077, file: !64, line: 214, column: 19)
!1077 = distinct !DILexicalBlock(scope: !640, file: !64, line: 214, column: 9)
!1078 = !DILocation(line: 0, scope: !623, inlinedAt: !1075)
!1079 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1075)
!1080 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1075)
!1081 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1075)
!1082 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1075)
!1083 = distinct !{!1083, !1082, !1084, !312, !313}
!1084 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1075)
!1085 = !DILocation(line: 216, column: 19, scope: !1076)
!1086 = !DILocation(line: 216, column: 40, scope: !1076)
!1087 = !DILocation(line: 217, column: 19, scope: !1076)
!1088 = !DILocation(line: 217, column: 40, scope: !1076)
!1089 = !DILocation(line: 218, column: 19, scope: !1076)
!1090 = !DILocation(line: 218, column: 40, scope: !1076)
!1091 = !DILocation(line: 219, column: 19, scope: !1076)
!1092 = !DILocation(line: 219, column: 40, scope: !1076)
!1093 = !DILocation(line: 221, column: 9, scope: !1094)
!1094 = distinct !DILexicalBlock(scope: !1076, file: !64, line: 221, column: 9)
!1095 = !DILocation(line: 222, column: 18, scope: !1096)
!1096 = distinct !DILexicalBlock(scope: !1097, file: !64, line: 222, column: 17)
!1097 = distinct !DILexicalBlock(scope: !1098, file: !64, line: 221, column: 47)
!1098 = distinct !DILexicalBlock(scope: !1094, file: !64, line: 221, column: 9)
!1099 = !DILocation(line: 222, column: 26, scope: !1096)
!1100 = !DILocation(line: 222, column: 17, scope: !1097)
!1101 = !DILocation(line: 223, column: 25, scope: !1102)
!1102 = distinct !DILexicalBlock(scope: !1097, file: !64, line: 223, column: 17)
!1103 = !DILocation(line: 223, column: 27, scope: !1102)
!1104 = !DILocation(line: 223, column: 17, scope: !1097)
!1105 = !DILocation(line: 224, column: 32, scope: !1106)
!1106 = distinct !DILexicalBlock(scope: !1102, file: !64, line: 223, column: 32)
!1107 = !DILocation(line: 225, column: 13, scope: !1106)
!1108 = !DILocation(line: 221, column: 21, scope: !1098)
!1109 = !DILocation(line: 221, column: 23, scope: !1098)
!1110 = distinct !{!1110, !1093, !1111, !312, !313}
!1111 = !DILocation(line: 226, column: 9, scope: !1094)
!1112 = !DILocation(line: 229, column: 25, scope: !1113)
!1113 = distinct !DILexicalBlock(scope: !1114, file: !64, line: 229, column: 17)
!1114 = distinct !DILexicalBlock(scope: !1115, file: !64, line: 228, column: 47)
!1115 = distinct !DILexicalBlock(scope: !1116, file: !64, line: 228, column: 9)
!1116 = distinct !DILexicalBlock(scope: !1076, file: !64, line: 228, column: 9)
!1117 = !DILocation(line: 229, column: 17, scope: !1113)
!1118 = !DILocation(line: 229, column: 17, scope: !1114)
!1119 = !DILocation(line: 228, column: 21, scope: !1115)
!1120 = !DILocation(line: 228, column: 23, scope: !1115)
!1121 = !DILocation(line: 228, column: 9, scope: !1116)
!1122 = distinct !{!1122, !1121, !1123, !312, !313}
!1123 = !DILocation(line: 230, column: 9, scope: !1116)
!1124 = !DILocation(line: 0, scope: !99, inlinedAt: !1125)
!1125 = distinct !DILocation(line: 231, column: 9, scope: !1076)
!1126 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1125)
!1127 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1125)
!1128 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1125)
!1129 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1125)
!1130 = !DILocation(line: 232, column: 9, scope: !1076)
!1131 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1132)
!1132 = distinct !DILocation(line: 237, column: 9, scope: !1133)
!1133 = distinct !DILexicalBlock(scope: !1134, file: !64, line: 236, column: 19)
!1134 = distinct !DILexicalBlock(scope: !640, file: !64, line: 236, column: 9)
!1135 = !DILocation(line: 0, scope: !623, inlinedAt: !1132)
!1136 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1132)
!1137 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1132)
!1138 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1132)
!1139 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1132)
!1140 = distinct !{!1140, !1139, !1141, !312, !313}
!1141 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1132)
!1142 = !DILocation(line: 238, column: 19, scope: !1133)
!1143 = !DILocation(line: 238, column: 40, scope: !1133)
!1144 = !DILocation(line: 239, column: 19, scope: !1133)
!1145 = !DILocation(line: 239, column: 40, scope: !1133)
!1146 = !DILocation(line: 240, column: 19, scope: !1133)
!1147 = !DILocation(line: 240, column: 40, scope: !1133)
!1148 = !DILocation(line: 241, column: 19, scope: !1133)
!1149 = !DILocation(line: 241, column: 40, scope: !1133)
!1150 = !DILocation(line: 243, column: 9, scope: !1151)
!1151 = distinct !DILexicalBlock(scope: !1133, file: !64, line: 243, column: 9)
!1152 = !DILocation(line: 244, column: 17, scope: !1153)
!1153 = distinct !DILexicalBlock(scope: !1154, file: !64, line: 244, column: 17)
!1154 = distinct !DILexicalBlock(scope: !1155, file: !64, line: 243, column: 47)
!1155 = distinct !DILexicalBlock(scope: !1151, file: !64, line: 243, column: 9)
!1156 = !DILocation(line: 244, column: 25, scope: !1153)
!1157 = !DILocation(line: 244, column: 32, scope: !1153)
!1158 = !DILocation(line: 244, column: 43, scope: !1153)
!1159 = !DILocation(line: 244, column: 17, scope: !1154)
!1160 = !DILocation(line: 0, scope: !1133)
!1161 = !DILocation(line: 243, column: 21, scope: !1155)
!1162 = !DILocation(line: 243, column: 23, scope: !1155)
!1163 = distinct !{!1163, !1150, !1164, !312, !313}
!1164 = !DILocation(line: 247, column: 9, scope: !1151)
!1165 = !DILocation(line: 0, scope: !99, inlinedAt: !1166)
!1166 = distinct !DILocation(line: 248, column: 9, scope: !1133)
!1167 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1166)
!1168 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1166)
!1169 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1166)
!1170 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1166)
!1171 = !DILocation(line: 249, column: 9, scope: !1133)
!1172 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1173)
!1173 = distinct !DILocation(line: 252, column: 9, scope: !1174)
!1174 = distinct !DILexicalBlock(scope: !1175, file: !64, line: 251, column: 19)
!1175 = distinct !DILexicalBlock(scope: !640, file: !64, line: 251, column: 9)
!1176 = !DILocation(line: 0, scope: !623, inlinedAt: !1173)
!1177 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1173)
!1178 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1173)
!1179 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1173)
!1180 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1173)
!1181 = distinct !{!1181, !1180, !1182, !312, !313}
!1182 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1173)
!1183 = !DILocation(line: 256, column: 17, scope: !1184)
!1184 = distinct !DILexicalBlock(scope: !1185, file: !64, line: 256, column: 17)
!1185 = distinct !DILexicalBlock(scope: !1186, file: !64, line: 255, column: 47)
!1186 = distinct !DILexicalBlock(scope: !1187, file: !64, line: 255, column: 9)
!1187 = distinct !DILexicalBlock(scope: !1174, file: !64, line: 255, column: 9)
!1188 = !DILocation(line: 256, column: 25, scope: !1184)
!1189 = !DILocation(line: 256, column: 32, scope: !1184)
!1190 = !DILocation(line: 256, column: 43, scope: !1184)
!1191 = !DILocation(line: 256, column: 17, scope: !1185)
!1192 = !DILocation(line: 0, scope: !1174)
!1193 = !DILocation(line: 255, column: 21, scope: !1186)
!1194 = !DILocation(line: 255, column: 23, scope: !1186)
!1195 = !DILocation(line: 255, column: 9, scope: !1187)
!1196 = distinct !{!1196, !1195, !1197, !312, !313}
!1197 = !DILocation(line: 259, column: 9, scope: !1187)
!1198 = !DILocation(line: 0, scope: !99, inlinedAt: !1199)
!1199 = distinct !DILocation(line: 260, column: 9, scope: !1174)
!1200 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1199)
!1201 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1199)
!1202 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1199)
!1203 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1199)
!1204 = !DILocation(line: 261, column: 9, scope: !1174)
!1205 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1206)
!1206 = distinct !DILocation(line: 266, column: 9, scope: !1207)
!1207 = distinct !DILexicalBlock(scope: !1208, file: !64, line: 265, column: 19)
!1208 = distinct !DILexicalBlock(scope: !640, file: !64, line: 265, column: 9)
!1209 = !DILocation(line: 0, scope: !623, inlinedAt: !1206)
!1210 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1206)
!1211 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1206)
!1212 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1206)
!1213 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1206)
!1214 = distinct !{!1214, !1213, !1215, !312, !313}
!1215 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1206)
!1216 = !DILocation(line: 267, column: 19, scope: !1207)
!1217 = !DILocation(line: 267, column: 40, scope: !1207)
!1218 = !DILocation(line: 268, column: 19, scope: !1207)
!1219 = !DILocation(line: 268, column: 40, scope: !1207)
!1220 = !DILocation(line: 269, column: 19, scope: !1207)
!1221 = !DILocation(line: 269, column: 40, scope: !1207)
!1222 = !DILocation(line: 270, column: 19, scope: !1207)
!1223 = !DILocation(line: 270, column: 40, scope: !1207)
!1224 = !DILocation(line: 272, column: 9, scope: !1225)
!1225 = distinct !DILexicalBlock(scope: !1207, file: !64, line: 272, column: 9)
!1226 = !DILocation(line: 273, column: 18, scope: !1227)
!1227 = distinct !DILexicalBlock(scope: !1228, file: !64, line: 273, column: 17)
!1228 = distinct !DILexicalBlock(scope: !1229, file: !64, line: 272, column: 47)
!1229 = distinct !DILexicalBlock(scope: !1225, file: !64, line: 272, column: 9)
!1230 = !DILocation(line: 273, column: 26, scope: !1227)
!1231 = !DILocation(line: 273, column: 17, scope: !1228)
!1232 = !DILocation(line: 274, column: 33, scope: !1228)
!1233 = !DILocation(line: 274, column: 23, scope: !1228)
!1234 = !DILocation(line: 275, column: 9, scope: !1228)
!1235 = !DILocation(line: 0, scope: !1207)
!1236 = !DILocation(line: 272, column: 21, scope: !1229)
!1237 = !DILocation(line: 272, column: 23, scope: !1229)
!1238 = distinct !{!1238, !1224, !1239, !312, !313}
!1239 = !DILocation(line: 275, column: 9, scope: !1225)
!1240 = !DILocation(line: 0, scope: !99, inlinedAt: !1241)
!1241 = distinct !DILocation(line: 276, column: 9, scope: !1207)
!1242 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1241)
!1243 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1241)
!1244 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1241)
!1245 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1241)
!1246 = !DILocation(line: 277, column: 9, scope: !1207)
!1247 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1248)
!1248 = distinct !DILocation(line: 282, column: 9, scope: !1249)
!1249 = distinct !DILexicalBlock(scope: !1250, file: !64, line: 281, column: 19)
!1250 = distinct !DILexicalBlock(scope: !640, file: !64, line: 281, column: 9)
!1251 = !DILocation(line: 0, scope: !623, inlinedAt: !1248)
!1252 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1248)
!1253 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1248)
!1254 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1248)
!1255 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1248)
!1256 = distinct !{!1256, !1255, !1257, !312, !313}
!1257 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1248)
!1258 = !DILocation(line: 283, column: 19, scope: !1249)
!1259 = !DILocation(line: 283, column: 38, scope: !1249)
!1260 = !DILocation(line: 283, column: 58, scope: !1249)
!1261 = !DILocation(line: 284, column: 19, scope: !1249)
!1262 = !DILocation(line: 284, column: 38, scope: !1249)
!1263 = !DILocation(line: 284, column: 58, scope: !1249)
!1264 = !DILocation(line: 285, column: 19, scope: !1249)
!1265 = !DILocation(line: 285, column: 38, scope: !1249)
!1266 = !DILocation(line: 285, column: 58, scope: !1249)
!1267 = !DILocation(line: 288, column: 9, scope: !1268)
!1268 = distinct !DILexicalBlock(scope: !1249, file: !64, line: 288, column: 9)
!1269 = !DILocation(line: 289, column: 18, scope: !1270)
!1270 = distinct !DILexicalBlock(scope: !1271, file: !64, line: 289, column: 17)
!1271 = distinct !DILexicalBlock(scope: !1272, file: !64, line: 288, column: 47)
!1272 = distinct !DILexicalBlock(scope: !1268, file: !64, line: 288, column: 9)
!1273 = !DILocation(line: 289, column: 26, scope: !1270)
!1274 = !DILocation(line: 289, column: 17, scope: !1271)
!1275 = !DILocation(line: 290, column: 25, scope: !1276)
!1276 = distinct !DILexicalBlock(scope: !1271, file: !64, line: 290, column: 17)
!1277 = !DILocation(line: 290, column: 30, scope: !1276)
!1278 = !DILocation(line: 290, column: 17, scope: !1271)
!1279 = !DILocation(line: 288, column: 42, scope: !1272)
!1280 = !DILocation(line: 288, column: 23, scope: !1272)
!1281 = distinct !{!1281, !1267, !1282, !312, !313}
!1282 = !DILocation(line: 294, column: 9, scope: !1268)
!1283 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1284)
!1284 = distinct !DILocation(line: 295, column: 9, scope: !1249)
!1285 = !DILocation(line: 0, scope: !99, inlinedAt: !1284)
!1286 = !DILocation(line: 296, column: 9, scope: !1249)
!1287 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1288)
!1288 = distinct !DILocation(line: 301, column: 9, scope: !1289)
!1289 = distinct !DILexicalBlock(scope: !1290, file: !64, line: 300, column: 19)
!1290 = distinct !DILexicalBlock(scope: !640, file: !64, line: 300, column: 9)
!1291 = !DILocation(line: 0, scope: !623, inlinedAt: !1288)
!1292 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1288)
!1293 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1288)
!1294 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1288)
!1295 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1288)
!1296 = distinct !{!1296, !1295, !1297, !312, !313}
!1297 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1288)
!1298 = !DILocation(line: 302, column: 19, scope: !1289)
!1299 = !DILocation(line: 302, column: 36, scope: !1289)
!1300 = !DILocation(line: 302, column: 57, scope: !1289)
!1301 = !DILocation(line: 303, column: 19, scope: !1289)
!1302 = !DILocation(line: 303, column: 36, scope: !1289)
!1303 = !DILocation(line: 303, column: 57, scope: !1289)
!1304 = !DILocation(line: 305, column: 9, scope: !1305)
!1305 = distinct !DILexicalBlock(scope: !1289, file: !64, line: 305, column: 9)
!1306 = !DILocation(line: 306, column: 18, scope: !1307)
!1307 = distinct !DILexicalBlock(scope: !1308, file: !64, line: 306, column: 17)
!1308 = distinct !DILexicalBlock(scope: !1309, file: !64, line: 305, column: 47)
!1309 = distinct !DILexicalBlock(scope: !1305, file: !64, line: 305, column: 9)
!1310 = !DILocation(line: 306, column: 26, scope: !1307)
!1311 = !DILocation(line: 306, column: 17, scope: !1308)
!1312 = !DILocation(line: 307, column: 33, scope: !1308)
!1313 = !DILocation(line: 307, column: 35, scope: !1308)
!1314 = !DILocation(line: 307, column: 23, scope: !1308)
!1315 = !DILocation(line: 308, column: 33, scope: !1308)
!1316 = !DILocation(line: 308, column: 35, scope: !1308)
!1317 = !DILocation(line: 308, column: 23, scope: !1308)
!1318 = !DILocation(line: 309, column: 9, scope: !1308)
!1319 = !DILocation(line: 305, column: 21, scope: !1309)
!1320 = !DILocation(line: 305, column: 23, scope: !1309)
!1321 = distinct !{!1321, !1304, !1322, !312, !313}
!1322 = !DILocation(line: 309, column: 9, scope: !1305)
!1323 = !DILocation(line: 310, column: 42, scope: !1289)
!1324 = !DILocation(line: 310, column: 54, scope: !1289)
!1325 = !DILocation(line: 310, column: 44, scope: !1289)
!1326 = !DILocation(line: 0, scope: !99, inlinedAt: !1327)
!1327 = distinct !DILocation(line: 310, column: 9, scope: !1289)
!1328 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1327)
!1329 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1327)
!1330 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1327)
!1331 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1327)
!1332 = !DILocation(line: 311, column: 9, scope: !1289)
!1333 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1334)
!1334 = distinct !DILocation(line: 316, column: 9, scope: !1335)
!1335 = distinct !DILexicalBlock(scope: !1336, file: !64, line: 315, column: 19)
!1336 = distinct !DILexicalBlock(scope: !640, file: !64, line: 315, column: 9)
!1337 = !DILocation(line: 0, scope: !623, inlinedAt: !1334)
!1338 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1334)
!1339 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1334)
!1340 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1334)
!1341 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1334)
!1342 = distinct !{!1342, !1341, !1343, !312, !313}
!1343 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1334)
!1344 = !DILocation(line: 317, column: 19, scope: !1335)
!1345 = !DILocation(line: 317, column: 35, scope: !1335)
!1346 = !DILocation(line: 317, column: 56, scope: !1335)
!1347 = !DILocation(line: 318, column: 19, scope: !1335)
!1348 = !DILocation(line: 318, column: 35, scope: !1335)
!1349 = !DILocation(line: 318, column: 56, scope: !1335)
!1350 = !DILocation(line: 321, column: 9, scope: !1351)
!1351 = distinct !DILexicalBlock(scope: !1335, file: !64, line: 321, column: 9)
!1352 = !DILocation(line: 322, column: 18, scope: !1353)
!1353 = distinct !DILexicalBlock(scope: !1354, file: !64, line: 322, column: 17)
!1354 = distinct !DILexicalBlock(scope: !1355, file: !64, line: 321, column: 47)
!1355 = distinct !DILexicalBlock(scope: !1351, file: !64, line: 321, column: 9)
!1356 = !DILocation(line: 322, column: 26, scope: !1353)
!1357 = !DILocation(line: 322, column: 17, scope: !1354)
!1358 = !DILocation(line: 323, column: 25, scope: !1359)
!1359 = distinct !DILexicalBlock(scope: !1354, file: !64, line: 323, column: 17)
!1360 = !DILocation(line: 323, column: 27, scope: !1359)
!1361 = !DILocation(line: 323, column: 33, scope: !1359)
!1362 = !DILocation(line: 323, column: 44, scope: !1359)
!1363 = !DILocation(line: 323, column: 46, scope: !1359)
!1364 = !DILocation(line: 323, column: 17, scope: !1354)
!1365 = !DILocation(line: 321, column: 21, scope: !1355)
!1366 = !DILocation(line: 321, column: 23, scope: !1355)
!1367 = distinct !{!1367, !1350, !1368, !312, !313}
!1368 = !DILocation(line: 327, column: 9, scope: !1351)
!1369 = !DILocation(line: 0, scope: !99, inlinedAt: !1370)
!1370 = distinct !DILocation(line: 328, column: 9, scope: !1335)
!1371 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1370)
!1372 = !DILocation(line: 329, column: 9, scope: !1335)
!1373 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1374)
!1374 = distinct !DILocation(line: 332, column: 9, scope: !1375)
!1375 = distinct !DILexicalBlock(scope: !1376, file: !64, line: 331, column: 19)
!1376 = distinct !DILexicalBlock(scope: !640, file: !64, line: 331, column: 9)
!1377 = !DILocation(line: 0, scope: !623, inlinedAt: !1374)
!1378 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1374)
!1379 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1374)
!1380 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1374)
!1381 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1374)
!1382 = distinct !{!1382, !1381, !1383, !312, !313}
!1383 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1374)
!1384 = !DILocation(line: 333, column: 19, scope: !1375)
!1385 = !DILocation(line: 333, column: 35, scope: !1375)
!1386 = !DILocation(line: 333, column: 56, scope: !1375)
!1387 = !DILocation(line: 334, column: 19, scope: !1375)
!1388 = !DILocation(line: 334, column: 35, scope: !1375)
!1389 = !DILocation(line: 334, column: 56, scope: !1375)
!1390 = !DILocation(line: 337, column: 9, scope: !1391)
!1391 = distinct !DILexicalBlock(scope: !1375, file: !64, line: 337, column: 9)
!1392 = !DILocation(line: 338, column: 18, scope: !1393)
!1393 = distinct !DILexicalBlock(scope: !1394, file: !64, line: 338, column: 17)
!1394 = distinct !DILexicalBlock(scope: !1395, file: !64, line: 337, column: 47)
!1395 = distinct !DILexicalBlock(scope: !1391, file: !64, line: 337, column: 9)
!1396 = !DILocation(line: 338, column: 26, scope: !1393)
!1397 = !DILocation(line: 338, column: 17, scope: !1394)
!1398 = !DILocation(line: 339, column: 25, scope: !1399)
!1399 = distinct !DILexicalBlock(scope: !1394, file: !64, line: 339, column: 17)
!1400 = !DILocation(line: 339, column: 27, scope: !1399)
!1401 = !DILocation(line: 339, column: 33, scope: !1399)
!1402 = !DILocation(line: 339, column: 44, scope: !1399)
!1403 = !DILocation(line: 339, column: 46, scope: !1399)
!1404 = !DILocation(line: 339, column: 17, scope: !1394)
!1405 = !DILocation(line: 337, column: 21, scope: !1395)
!1406 = !DILocation(line: 337, column: 23, scope: !1395)
!1407 = distinct !{!1407, !1390, !1408, !312, !313}
!1408 = !DILocation(line: 343, column: 9, scope: !1391)
!1409 = !DILocation(line: 0, scope: !99, inlinedAt: !1410)
!1410 = distinct !DILocation(line: 344, column: 9, scope: !1375)
!1411 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1410)
!1412 = !DILocation(line: 345, column: 9, scope: !1375)
!1413 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1414)
!1414 = distinct !DILocation(line: 350, column: 9, scope: !1415)
!1415 = distinct !DILexicalBlock(scope: !1416, file: !64, line: 349, column: 19)
!1416 = distinct !DILexicalBlock(scope: !640, file: !64, line: 349, column: 9)
!1417 = !DILocation(line: 0, scope: !623, inlinedAt: !1414)
!1418 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1414)
!1419 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1414)
!1420 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1414)
!1421 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1414)
!1422 = distinct !{!1422, !1421, !1423, !312, !313}
!1423 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1414)
!1424 = !DILocation(line: 351, column: 19, scope: !1415)
!1425 = !DILocation(line: 351, column: 35, scope: !1415)
!1426 = !DILocation(line: 351, column: 56, scope: !1415)
!1427 = !DILocation(line: 354, column: 9, scope: !1428)
!1428 = distinct !DILexicalBlock(scope: !1415, file: !64, line: 354, column: 9)
!1429 = !DILocation(line: 355, column: 18, scope: !1430)
!1430 = distinct !DILexicalBlock(scope: !1431, file: !64, line: 355, column: 17)
!1431 = distinct !DILexicalBlock(scope: !1432, file: !64, line: 354, column: 47)
!1432 = distinct !DILexicalBlock(scope: !1428, file: !64, line: 354, column: 9)
!1433 = !DILocation(line: 355, column: 26, scope: !1430)
!1434 = !DILocation(line: 355, column: 17, scope: !1431)
!1435 = !DILocation(line: 356, column: 25, scope: !1436)
!1436 = distinct !DILexicalBlock(scope: !1431, file: !64, line: 356, column: 17)
!1437 = !DILocation(line: 356, column: 32, scope: !1436)
!1438 = !DILocation(line: 357, column: 25, scope: !1436)
!1439 = !DILocation(line: 357, column: 33, scope: !1436)
!1440 = !DILocation(line: 354, column: 21, scope: !1432)
!1441 = !DILocation(line: 354, column: 23, scope: !1432)
!1442 = distinct !{!1442, !1427, !1443, !312, !313}
!1443 = !DILocation(line: 361, column: 9, scope: !1428)
!1444 = !DILocation(line: 0, scope: !99, inlinedAt: !1445)
!1445 = distinct !DILocation(line: 362, column: 9, scope: !1415)
!1446 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1445)
!1447 = !DILocation(line: 363, column: 9, scope: !1415)
!1448 = !DILocation(line: 21, column: 9, scope: !632, inlinedAt: !1449)
!1449 = distinct !DILocation(line: 366, column: 9, scope: !1450)
!1450 = distinct !DILexicalBlock(scope: !1451, file: !64, line: 365, column: 19)
!1451 = distinct !DILexicalBlock(scope: !640, file: !64, line: 365, column: 9)
!1452 = !DILocation(line: 0, scope: !623, inlinedAt: !1449)
!1453 = !DILocation(line: 20, column: 17, scope: !633, inlinedAt: !1449)
!1454 = !DILocation(line: 20, column: 19, scope: !633, inlinedAt: !1449)
!1455 = !DILocation(line: 22, column: 19, scope: !632, inlinedAt: !1449)
!1456 = !DILocation(line: 20, column: 5, scope: !630, inlinedAt: !1449)
!1457 = distinct !{!1457, !1456, !1458, !312, !313}
!1458 = !DILocation(line: 25, column: 5, scope: !630, inlinedAt: !1449)
!1459 = !DILocation(line: 367, column: 19, scope: !1450)
!1460 = !DILocation(line: 367, column: 35, scope: !1450)
!1461 = !DILocation(line: 367, column: 56, scope: !1450)
!1462 = !DILocation(line: 370, column: 9, scope: !1463)
!1463 = distinct !DILexicalBlock(scope: !1450, file: !64, line: 370, column: 9)
!1464 = !DILocation(line: 371, column: 18, scope: !1465)
!1465 = distinct !DILexicalBlock(scope: !1466, file: !64, line: 371, column: 17)
!1466 = distinct !DILexicalBlock(scope: !1467, file: !64, line: 370, column: 47)
!1467 = distinct !DILexicalBlock(scope: !1463, file: !64, line: 370, column: 9)
!1468 = !DILocation(line: 371, column: 26, scope: !1465)
!1469 = !DILocation(line: 371, column: 17, scope: !1466)
!1470 = !DILocation(line: 372, column: 25, scope: !1471)
!1471 = distinct !DILexicalBlock(scope: !1466, file: !64, line: 372, column: 17)
!1472 = !DILocation(line: 372, column: 32, scope: !1471)
!1473 = !DILocation(line: 373, column: 25, scope: !1471)
!1474 = !DILocation(line: 373, column: 32, scope: !1471)
!1475 = !DILocation(line: 370, column: 21, scope: !1467)
!1476 = !DILocation(line: 370, column: 23, scope: !1467)
!1477 = distinct !{!1477, !1462, !1478, !312, !313}
!1478 = !DILocation(line: 377, column: 9, scope: !1463)
!1479 = !DILocation(line: 0, scope: !99, inlinedAt: !1480)
!1480 = distinct !DILocation(line: 378, column: 9, scope: !1450)
!1481 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1480)
!1482 = !DILocation(line: 379, column: 9, scope: !1450)
!1483 = !DILocation(line: 0, scope: !99, inlinedAt: !1484)
!1484 = distinct !DILocation(line: 382, column: 5, scope: !640)
!1485 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1484)
!1486 = !DILocation(line: 383, column: 1, scope: !640)
!1487 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !650)
!1488 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !650)
!1489 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !650)
!1490 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !650)
!1491 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !650)
!1492 = distinct !DISubprogram(name: "render_checksum", scope: !32, file: !32, line: 19, type: !296, scopeLine: 19, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1493)
!1493 = !{!1494, !1495}
!1494 = !DILocalVariable(name: "i", scope: !1492, file: !32, line: 20, type: !8)
!1495 = !DILocalVariable(name: "sum", scope: !1492, file: !32, line: 21, type: !8)
!1496 = !DILocation(line: 0, scope: !1492)
!1497 = !DILocation(line: 22, column: 5, scope: !1498)
!1498 = distinct !DILexicalBlock(scope: !1492, file: !32, line: 22, column: 5)
!1499 = !DILocation(line: 23, column: 22, scope: !1500)
!1500 = distinct !DILexicalBlock(scope: !1501, file: !32, line: 22, column: 48)
!1501 = distinct !DILexicalBlock(scope: !1498, file: !32, line: 22, column: 5)
!1502 = !DILocation(line: 23, column: 19, scope: !1500)
!1503 = !DILocation(line: 22, column: 17, scope: !1501)
!1504 = !DILocation(line: 22, column: 19, scope: !1501)
!1505 = distinct !{!1505, !1497, !1506, !312, !313}
!1506 = !DILocation(line: 24, column: 5, scope: !1498)
!1507 = !DILocation(line: 25, column: 5, scope: !1492)
!1508 = distinct !DISubprogram(name: "render_setPixel", scope: !32, file: !32, line: 29, type: !1509, scopeLine: 29, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1511)
!1509 = !DISubroutineType(types: !1510)
!1510 = !{null, !8, !8, !5}
!1511 = !{!1512, !1513, !1514, !1515, !1516}
!1512 = !DILocalVariable(name: "x", arg: 1, scope: !1508, file: !32, line: 29, type: !8)
!1513 = !DILocalVariable(name: "y", arg: 2, scope: !1508, file: !32, line: 29, type: !8)
!1514 = !DILocalVariable(name: "color", arg: 3, scope: !1508, file: !32, line: 29, type: !5)
!1515 = !DILocalVariable(name: "byteIdx", scope: !1508, file: !32, line: 30, type: !8)
!1516 = !DILocalVariable(name: "mask", scope: !1508, file: !32, line: 31, type: !5)
!1517 = !DILocation(line: 0, scope: !1508)
!1518 = !DILocation(line: 33, column: 15, scope: !1519)
!1519 = distinct !DILexicalBlock(scope: !1508, file: !32, line: 33, column: 9)
!1520 = !DILocation(line: 36, column: 18, scope: !1508)
!1521 = !DILocation(line: 36, column: 29, scope: !1508)
!1522 = !DILocation(line: 36, column: 24, scope: !1508)
!1523 = !DILocation(line: 37, column: 30, scope: !1508)
!1524 = !DILocation(line: 37, column: 24, scope: !1508)
!1525 = !DILocation(line: 39, column: 9, scope: !1526)
!1526 = distinct !DILexicalBlock(scope: !1508, file: !32, line: 39, column: 9)
!1527 = !DILocation(line: 0, scope: !1526)
!1528 = !DILocation(line: 39, column: 9, scope: !1508)
!1529 = !DILocation(line: 43, column: 1, scope: !1508)
!1530 = distinct !DISubprogram(name: "draw_sprite", scope: !32, file: !32, line: 47, type: !1531, scopeLine: 47, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1533)
!1531 = !DISubroutineType(types: !1532)
!1532 = !{null, !8, !8, !8}
!1533 = !{!1534, !1535, !1536, !1537, !1538, !1539, !1540, !1541, !1542, !1543}
!1534 = !DILocalVariable(name: "x", arg: 1, scope: !1530, file: !32, line: 47, type: !8)
!1535 = !DILocalVariable(name: "y", arg: 2, scope: !1530, file: !32, line: 47, type: !8)
!1536 = !DILocalVariable(name: "height", arg: 3, scope: !1530, file: !32, line: 47, type: !8)
!1537 = !DILocalVariable(name: "row", scope: !1530, file: !32, line: 48, type: !8)
!1538 = !DILocalVariable(name: "byteIdx", scope: !1530, file: !32, line: 49, type: !8)
!1539 = !DILocalVariable(name: "spriteRow", scope: !1530, file: !32, line: 50, type: !5)
!1540 = !DILocalVariable(name: "xBit", scope: !1530, file: !32, line: 51, type: !5)
!1541 = !DILocalVariable(name: "shift", scope: !1530, file: !32, line: 52, type: !5)
!1542 = !DILocalVariable(name: "mask1", scope: !1530, file: !32, line: 53, type: !5)
!1543 = !DILocalVariable(name: "mask2", scope: !1530, file: !32, line: 54, type: !5)
!1544 = !DILocation(line: 0, scope: !1530)
!1545 = !DILocation(line: 58, column: 23, scope: !1546)
!1546 = distinct !DILexicalBlock(scope: !1547, file: !32, line: 58, column: 5)
!1547 = distinct !DILexicalBlock(scope: !1530, file: !32, line: 58, column: 5)
!1548 = !DILocation(line: 58, column: 5, scope: !1547)
!1549 = !DILocation(line: 56, column: 12, scope: !1530)
!1550 = !DILocation(line: 59, column: 15, scope: !1551)
!1551 = distinct !DILexicalBlock(scope: !1552, file: !32, line: 59, column: 13)
!1552 = distinct !DILexicalBlock(scope: !1546, file: !32, line: 58, column: 48)
!1553 = !DILocation(line: 59, column: 25, scope: !1551)
!1554 = !DILocation(line: 61, column: 21, scope: !1552)
!1555 = !DILocation(line: 62, column: 19, scope: !1552)
!1556 = !DILocation(line: 64, column: 13, scope: !1552)
!1557 = !DILocation(line: 68, column: 30, scope: !1558)
!1558 = distinct !DILexicalBlock(scope: !1559, file: !32, line: 68, column: 17)
!1559 = distinct !DILexicalBlock(scope: !1560, file: !32, line: 64, column: 24)
!1560 = distinct !DILexicalBlock(scope: !1552, file: !32, line: 64, column: 13)
!1561 = !DILocation(line: 68, column: 17, scope: !1558)
!1562 = !DILocation(line: 67, column: 39, scope: !1559)
!1563 = !DILocation(line: 67, column: 47, scope: !1559)
!1564 = !DILocation(line: 70, column: 13, scope: !1565)
!1565 = distinct !DILexicalBlock(scope: !1558, file: !32, line: 68, column: 59)
!1566 = !DILocation(line: 74, column: 39, scope: !1567)
!1567 = distinct !DILexicalBlock(scope: !1560, file: !32, line: 71, column: 16)
!1568 = !DILocation(line: 75, column: 47, scope: !1567)
!1569 = !DILocation(line: 76, column: 17, scope: !1570)
!1570 = distinct !DILexicalBlock(scope: !1567, file: !32, line: 76, column: 17)
!1571 = !DILocation(line: 76, column: 30, scope: !1570)
!1572 = !DILocation(line: 74, column: 47, scope: !1567)
!1573 = !DILocation(line: 77, column: 46, scope: !1574)
!1574 = distinct !DILexicalBlock(scope: !1570, file: !32, line: 76, column: 59)
!1575 = !DILocation(line: 77, column: 38, scope: !1574)
!1576 = !DILocation(line: 77, column: 36, scope: !1574)
!1577 = !DILocation(line: 78, column: 13, scope: !1574)
!1578 = !DILocation(line: 79, column: 29, scope: !1579)
!1579 = distinct !DILexicalBlock(scope: !1567, file: !32, line: 79, column: 17)
!1580 = !DILocation(line: 79, column: 17, scope: !1567)
!1581 = !DILocation(line: 79, column: 25, scope: !1579)
!1582 = !DILocation(line: 81, column: 13, scope: !1583)
!1583 = distinct !DILexicalBlock(scope: !1579, file: !32, line: 79, column: 47)
!1584 = !DILocation(line: 0, scope: !1560)
!1585 = !DILocation(line: 58, column: 19, scope: !1546)
!1586 = distinct !{!1586, !1548, !1587, !312, !313}
!1587 = !DILocation(line: 83, column: 5, scope: !1547)
!1588 = !DILocation(line: 84, column: 1, scope: !1530)
!1589 = distinct !DISubprogram(name: "test_rendering", scope: !32, file: !32, line: 86, type: !142, scopeLine: 86, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !1590)
!1590 = !{!1591, !1592, !1593, !1594, !1595, !1596, !1597, !1598, !1599, !1600, !1601, !1602, !1603, !1604, !1605, !1608}
!1591 = !DILocalVariable(name: "apdu", arg: 1, scope: !1589, file: !32, line: 86, type: !102)
!1592 = !DILocalVariable(name: "buffer", arg: 2, scope: !1589, file: !32, line: 86, type: !104)
!1593 = !DILocalVariable(name: "p1", arg: 3, scope: !1589, file: !32, line: 86, type: !5)
!1594 = !DILocalVariable(name: "x", scope: !1589, file: !32, line: 87, type: !8)
!1595 = !DILocalVariable(name: "y", scope: !1589, file: !32, line: 87, type: !8)
!1596 = !DILocalVariable(name: "row", scope: !1589, file: !32, line: 88, type: !8)
!1597 = !DILocalVariable(name: "digit", scope: !1589, file: !32, line: 89, type: !8)
!1598 = !DILocalVariable(name: "num", scope: !1589, file: !32, line: 90, type: !8)
!1599 = !DILocalVariable(name: "byteIdx", scope: !1589, file: !32, line: 91, type: !8)
!1600 = !DILocalVariable(name: "fontRow", scope: !1589, file: !32, line: 92, type: !5)
!1601 = !DILocalVariable(name: "xBit", scope: !1589, file: !32, line: 93, type: !5)
!1602 = !DILocalVariable(name: "shift", scope: !1589, file: !32, line: 94, type: !5)
!1603 = !DILocalVariable(name: "mask1", scope: !1589, file: !32, line: 95, type: !5)
!1604 = !DILocalVariable(name: "mask2", scope: !1589, file: !32, line: 96, type: !5)
!1605 = !DILocalVariable(name: "d0", scope: !1606, file: !32, line: 268, type: !8)
!1606 = distinct !DILexicalBlock(scope: !1607, file: !32, line: 264, column: 19)
!1607 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 264, column: 9)
!1608 = !DILocalVariable(name: "d1", scope: !1606, file: !32, line: 269, type: !8)
!1609 = !DILocation(line: 0, scope: !1589)
!1610 = !DILocation(line: 99, column: 9, scope: !1589)
!1611 = !DILocation(line: 100, column: 9, scope: !1612)
!1612 = distinct !DILexicalBlock(scope: !1613, file: !32, line: 99, column: 18)
!1613 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 99, column: 9)
!1614 = !DILocation(line: 0, scope: !1492, inlinedAt: !1615)
!1615 = distinct !DILocation(line: 101, column: 34, scope: !1612)
!1616 = !DILocation(line: 22, column: 5, scope: !1498, inlinedAt: !1615)
!1617 = !DILocation(line: 23, column: 22, scope: !1500, inlinedAt: !1615)
!1618 = !DILocation(line: 23, column: 19, scope: !1500, inlinedAt: !1615)
!1619 = !DILocation(line: 22, column: 17, scope: !1501, inlinedAt: !1615)
!1620 = !DILocation(line: 22, column: 19, scope: !1501, inlinedAt: !1615)
!1621 = distinct !{!1621, !1616, !1622, !312, !313}
!1622 = !DILocation(line: 24, column: 5, scope: !1498, inlinedAt: !1615)
!1623 = !DILocation(line: 0, scope: !99, inlinedAt: !1624)
!1624 = distinct !DILocation(line: 101, column: 9, scope: !1612)
!1625 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1624)
!1626 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1624)
!1627 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1624)
!1628 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1624)
!1629 = !DILocation(line: 102, column: 9, scope: !1612)
!1630 = !DILocation(line: 107, column: 9, scope: !1631)
!1631 = distinct !DILexicalBlock(scope: !1632, file: !32, line: 106, column: 18)
!1632 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 106, column: 9)
!1633 = !DILocation(line: 0, scope: !1508, inlinedAt: !1634)
!1634 = distinct !DILocation(line: 108, column: 9, scope: !1631)
!1635 = !DILocation(line: 40, column: 38, scope: !1526, inlinedAt: !1634)
!1636 = !DILocation(line: 40, column: 65, scope: !1526, inlinedAt: !1634)
!1637 = !DILocation(line: 40, column: 28, scope: !1526, inlinedAt: !1634)
!1638 = !DILocation(line: 0, scope: !99, inlinedAt: !1639)
!1639 = distinct !DILocation(line: 109, column: 9, scope: !1631)
!1640 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1639)
!1641 = !DILocation(line: 110, column: 9, scope: !1631)
!1642 = !DILocation(line: 113, column: 9, scope: !1643)
!1643 = distinct !DILexicalBlock(scope: !1644, file: !32, line: 112, column: 18)
!1644 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 112, column: 9)
!1645 = !DILocation(line: 0, scope: !1508, inlinedAt: !1646)
!1646 = distinct !DILocation(line: 114, column: 9, scope: !1643)
!1647 = !DILocation(line: 40, column: 38, scope: !1526, inlinedAt: !1646)
!1648 = !DILocation(line: 40, column: 65, scope: !1526, inlinedAt: !1646)
!1649 = !DILocation(line: 40, column: 28, scope: !1526, inlinedAt: !1646)
!1650 = !DILocation(line: 0, scope: !99, inlinedAt: !1651)
!1651 = distinct !DILocation(line: 115, column: 9, scope: !1643)
!1652 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1651)
!1653 = !DILocation(line: 116, column: 9, scope: !1643)
!1654 = !DILocation(line: 119, column: 9, scope: !1655)
!1655 = distinct !DILexicalBlock(scope: !1656, file: !32, line: 118, column: 18)
!1656 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 118, column: 9)
!1657 = !DILocation(line: 0, scope: !1508, inlinedAt: !1658)
!1658 = distinct !DILocation(line: 120, column: 9, scope: !1655)
!1659 = !DILocation(line: 40, column: 38, scope: !1526, inlinedAt: !1658)
!1660 = !DILocation(line: 40, column: 65, scope: !1526, inlinedAt: !1658)
!1661 = !DILocation(line: 40, column: 28, scope: !1526, inlinedAt: !1658)
!1662 = !DILocation(line: 0, scope: !99, inlinedAt: !1663)
!1663 = distinct !DILocation(line: 121, column: 9, scope: !1655)
!1664 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1663)
!1665 = !DILocation(line: 122, column: 9, scope: !1655)
!1666 = !DILocation(line: 127, column: 9, scope: !1667)
!1667 = distinct !DILexicalBlock(scope: !1668, file: !32, line: 126, column: 18)
!1668 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 126, column: 9)
!1669 = !DILocation(line: 0, scope: !1530, inlinedAt: !1670)
!1670 = distinct !DILocation(line: 128, column: 9, scope: !1667)
!1671 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1670)
!1672 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1670)
!1673 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1670)
!1674 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1670)
!1675 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !1670)
!1676 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !1670)
!1677 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !1670)
!1678 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !1670)
!1679 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !1670)
!1680 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1670)
!1681 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1670)
!1682 = distinct !{!1682, !1671, !1683, !312, !313}
!1683 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1670)
!1684 = !DILocation(line: 130, column: 34, scope: !1667)
!1685 = !DILocation(line: 0, scope: !99, inlinedAt: !1686)
!1686 = distinct !DILocation(line: 130, column: 9, scope: !1667)
!1687 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1686)
!1688 = !DILocation(line: 131, column: 9, scope: !1667)
!1689 = !DILocation(line: 134, column: 9, scope: !1690)
!1690 = distinct !DILexicalBlock(scope: !1691, file: !32, line: 133, column: 18)
!1691 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 133, column: 9)
!1692 = !DILocation(line: 0, scope: !1530, inlinedAt: !1693)
!1693 = distinct !DILocation(line: 135, column: 9, scope: !1690)
!1694 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1693)
!1695 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1693)
!1696 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1693)
!1697 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1693)
!1698 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !1693)
!1699 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !1693)
!1700 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !1693)
!1701 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !1693)
!1702 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !1693)
!1703 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1693)
!1704 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1693)
!1705 = distinct !{!1705, !1694, !1706, !312, !313}
!1706 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1693)
!1707 = !DILocation(line: 136, column: 34, scope: !1690)
!1708 = !DILocation(line: 0, scope: !99, inlinedAt: !1709)
!1709 = distinct !DILocation(line: 136, column: 9, scope: !1690)
!1710 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1709)
!1711 = !DILocation(line: 137, column: 9, scope: !1690)
!1712 = !DILocation(line: 140, column: 9, scope: !1713)
!1713 = distinct !DILexicalBlock(scope: !1714, file: !32, line: 139, column: 18)
!1714 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 139, column: 9)
!1715 = !DILocation(line: 0, scope: !1530, inlinedAt: !1716)
!1716 = distinct !DILocation(line: 141, column: 9, scope: !1713)
!1717 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1716)
!1718 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1716)
!1719 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1716)
!1720 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1716)
!1721 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !1716)
!1722 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !1716)
!1723 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !1716)
!1724 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !1716)
!1725 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !1716)
!1726 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1716)
!1727 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1716)
!1728 = distinct !{!1728, !1717, !1729, !312, !313}
!1729 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1716)
!1730 = !DILocation(line: 0, scope: !1492, inlinedAt: !1731)
!1731 = distinct !DILocation(line: 142, column: 34, scope: !1713)
!1732 = !DILocation(line: 23, column: 22, scope: !1500, inlinedAt: !1731)
!1733 = !DILocation(line: 23, column: 19, scope: !1500, inlinedAt: !1731)
!1734 = !DILocation(line: 22, column: 17, scope: !1501, inlinedAt: !1731)
!1735 = !DILocation(line: 22, column: 19, scope: !1501, inlinedAt: !1731)
!1736 = !DILocation(line: 22, column: 5, scope: !1498, inlinedAt: !1731)
!1737 = distinct !{!1737, !1736, !1738, !312, !313}
!1738 = !DILocation(line: 24, column: 5, scope: !1498, inlinedAt: !1731)
!1739 = !DILocation(line: 0, scope: !99, inlinedAt: !1740)
!1740 = distinct !DILocation(line: 142, column: 9, scope: !1713)
!1741 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1740)
!1742 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1740)
!1743 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1740)
!1744 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1740)
!1745 = !DILocation(line: 143, column: 9, scope: !1713)
!1746 = !DILocation(line: 148, column: 9, scope: !1747)
!1747 = distinct !DILexicalBlock(scope: !1748, file: !32, line: 147, column: 18)
!1748 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 147, column: 9)
!1749 = !DILocation(line: 0, scope: !1530, inlinedAt: !1750)
!1750 = distinct !DILocation(line: 149, column: 9, scope: !1747)
!1751 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1750)
!1752 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1750)
!1753 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1750)
!1754 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1750)
!1755 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !1750)
!1756 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !1750)
!1757 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !1750)
!1758 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !1750)
!1759 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !1750)
!1760 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1750)
!1761 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1750)
!1762 = distinct !{!1762, !1751, !1763, !312, !313}
!1763 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1750)
!1764 = !DILocation(line: 151, column: 34, scope: !1747)
!1765 = !DILocation(line: 0, scope: !99, inlinedAt: !1766)
!1766 = distinct !DILocation(line: 151, column: 9, scope: !1747)
!1767 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1766)
!1768 = !DILocation(line: 152, column: 9, scope: !1747)
!1769 = !DILocation(line: 155, column: 9, scope: !1770)
!1770 = distinct !DILexicalBlock(scope: !1771, file: !32, line: 154, column: 18)
!1771 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 154, column: 9)
!1772 = !DILocation(line: 0, scope: !1530, inlinedAt: !1773)
!1773 = distinct !DILocation(line: 156, column: 9, scope: !1770)
!1774 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1773)
!1775 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1773)
!1776 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1773)
!1777 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1773)
!1778 = !DILocation(line: 67, column: 39, scope: !1559, inlinedAt: !1773)
!1779 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !1773)
!1780 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !1773)
!1781 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !1773)
!1782 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !1773)
!1783 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1773)
!1784 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1773)
!1785 = distinct !{!1785, !1774, !1786, !312, !313}
!1786 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1773)
!1787 = !DILocation(line: 158, column: 34, scope: !1770)
!1788 = !DILocation(line: 0, scope: !99, inlinedAt: !1789)
!1789 = distinct !DILocation(line: 158, column: 9, scope: !1770)
!1790 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1789)
!1791 = !DILocation(line: 159, column: 9, scope: !1770)
!1792 = !DILocation(line: 164, column: 9, scope: !1793)
!1793 = distinct !DILexicalBlock(scope: !1794, file: !32, line: 163, column: 18)
!1794 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 163, column: 9)
!1795 = !DILocation(line: 0, scope: !1530, inlinedAt: !1796)
!1796 = distinct !DILocation(line: 165, column: 9, scope: !1793)
!1797 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1796)
!1798 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1796)
!1799 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1796)
!1800 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1796)
!1801 = !DILocation(line: 75, column: 47, scope: !1567, inlinedAt: !1796)
!1802 = !DILocation(line: 74, column: 47, scope: !1567, inlinedAt: !1796)
!1803 = !DILocation(line: 77, column: 46, scope: !1574, inlinedAt: !1796)
!1804 = !DILocation(line: 77, column: 38, scope: !1574, inlinedAt: !1796)
!1805 = !DILocation(line: 77, column: 36, scope: !1574, inlinedAt: !1796)
!1806 = !DILocation(line: 79, column: 25, scope: !1579, inlinedAt: !1796)
!1807 = !DILocation(line: 80, column: 50, scope: !1583, inlinedAt: !1796)
!1808 = !DILocation(line: 80, column: 42, scope: !1583, inlinedAt: !1796)
!1809 = !DILocation(line: 80, column: 40, scope: !1583, inlinedAt: !1796)
!1810 = !DILocation(line: 81, column: 13, scope: !1583, inlinedAt: !1796)
!1811 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1796)
!1812 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1796)
!1813 = distinct !{!1813, !1797, !1814, !312, !313}
!1814 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1796)
!1815 = !DILocation(line: 168, column: 34, scope: !1793)
!1816 = !DILocation(line: 0, scope: !99, inlinedAt: !1817)
!1817 = distinct !DILocation(line: 168, column: 9, scope: !1793)
!1818 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1817)
!1819 = !DILocation(line: 169, column: 9, scope: !1793)
!1820 = !DILocation(line: 172, column: 9, scope: !1821)
!1821 = distinct !DILexicalBlock(scope: !1822, file: !32, line: 171, column: 19)
!1822 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 171, column: 9)
!1823 = !DILocation(line: 0, scope: !1530, inlinedAt: !1824)
!1824 = distinct !DILocation(line: 173, column: 9, scope: !1821)
!1825 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1824)
!1826 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1824)
!1827 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1824)
!1828 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1824)
!1829 = !DILocation(line: 75, column: 47, scope: !1567, inlinedAt: !1824)
!1830 = !DILocation(line: 74, column: 47, scope: !1567, inlinedAt: !1824)
!1831 = !DILocation(line: 77, column: 46, scope: !1574, inlinedAt: !1824)
!1832 = !DILocation(line: 77, column: 38, scope: !1574, inlinedAt: !1824)
!1833 = !DILocation(line: 77, column: 36, scope: !1574, inlinedAt: !1824)
!1834 = !DILocation(line: 79, column: 25, scope: !1579, inlinedAt: !1824)
!1835 = !DILocation(line: 80, column: 50, scope: !1583, inlinedAt: !1824)
!1836 = !DILocation(line: 80, column: 42, scope: !1583, inlinedAt: !1824)
!1837 = !DILocation(line: 80, column: 40, scope: !1583, inlinedAt: !1824)
!1838 = !DILocation(line: 81, column: 13, scope: !1583, inlinedAt: !1824)
!1839 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1824)
!1840 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1824)
!1841 = distinct !{!1841, !1825, !1842, !312, !313}
!1842 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1824)
!1843 = !DILocation(line: 174, column: 34, scope: !1821)
!1844 = !DILocation(line: 0, scope: !99, inlinedAt: !1845)
!1845 = distinct !DILocation(line: 174, column: 9, scope: !1821)
!1846 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1845)
!1847 = !DILocation(line: 175, column: 9, scope: !1821)
!1848 = !DILocation(line: 178, column: 9, scope: !1849)
!1849 = distinct !DILexicalBlock(scope: !1850, file: !32, line: 177, column: 19)
!1850 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 177, column: 9)
!1851 = !DILocation(line: 0, scope: !1530, inlinedAt: !1852)
!1852 = distinct !DILocation(line: 179, column: 9, scope: !1849)
!1853 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1852)
!1854 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1852)
!1855 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1852)
!1856 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1852)
!1857 = !DILocation(line: 75, column: 47, scope: !1567, inlinedAt: !1852)
!1858 = !DILocation(line: 74, column: 47, scope: !1567, inlinedAt: !1852)
!1859 = !DILocation(line: 77, column: 46, scope: !1574, inlinedAt: !1852)
!1860 = !DILocation(line: 77, column: 38, scope: !1574, inlinedAt: !1852)
!1861 = !DILocation(line: 77, column: 36, scope: !1574, inlinedAt: !1852)
!1862 = !DILocation(line: 79, column: 25, scope: !1579, inlinedAt: !1852)
!1863 = !DILocation(line: 80, column: 50, scope: !1583, inlinedAt: !1852)
!1864 = !DILocation(line: 80, column: 42, scope: !1583, inlinedAt: !1852)
!1865 = !DILocation(line: 80, column: 40, scope: !1583, inlinedAt: !1852)
!1866 = !DILocation(line: 81, column: 13, scope: !1583, inlinedAt: !1852)
!1867 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1852)
!1868 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1852)
!1869 = distinct !{!1869, !1853, !1870, !312, !313}
!1870 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1852)
!1871 = !DILocation(line: 182, column: 34, scope: !1849)
!1872 = !DILocation(line: 0, scope: !99, inlinedAt: !1873)
!1873 = distinct !DILocation(line: 182, column: 9, scope: !1849)
!1874 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1873)
!1875 = !DILocation(line: 183, column: 9, scope: !1849)
!1876 = !DILocation(line: 186, column: 9, scope: !1877)
!1877 = distinct !DILexicalBlock(scope: !1878, file: !32, line: 185, column: 19)
!1878 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 185, column: 9)
!1879 = !DILocation(line: 0, scope: !1530, inlinedAt: !1880)
!1880 = distinct !DILocation(line: 187, column: 9, scope: !1877)
!1881 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1880)
!1882 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1880)
!1883 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1880)
!1884 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1880)
!1885 = !DILocation(line: 75, column: 47, scope: !1567, inlinedAt: !1880)
!1886 = !DILocation(line: 74, column: 47, scope: !1567, inlinedAt: !1880)
!1887 = !DILocation(line: 77, column: 46, scope: !1574, inlinedAt: !1880)
!1888 = !DILocation(line: 77, column: 38, scope: !1574, inlinedAt: !1880)
!1889 = !DILocation(line: 77, column: 36, scope: !1574, inlinedAt: !1880)
!1890 = !DILocation(line: 79, column: 25, scope: !1579, inlinedAt: !1880)
!1891 = !DILocation(line: 80, column: 50, scope: !1583, inlinedAt: !1880)
!1892 = !DILocation(line: 80, column: 42, scope: !1583, inlinedAt: !1880)
!1893 = !DILocation(line: 80, column: 40, scope: !1583, inlinedAt: !1880)
!1894 = !DILocation(line: 81, column: 13, scope: !1583, inlinedAt: !1880)
!1895 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1880)
!1896 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1880)
!1897 = distinct !{!1897, !1881, !1898, !312, !313}
!1898 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1880)
!1899 = !DILocation(line: 188, column: 34, scope: !1877)
!1900 = !DILocation(line: 0, scope: !99, inlinedAt: !1901)
!1901 = distinct !DILocation(line: 188, column: 9, scope: !1877)
!1902 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1901)
!1903 = !DILocation(line: 189, column: 9, scope: !1877)
!1904 = !DILocation(line: 194, column: 9, scope: !1905)
!1905 = distinct !DILexicalBlock(scope: !1906, file: !32, line: 193, column: 19)
!1906 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 193, column: 9)
!1907 = !DILocation(line: 0, scope: !1530, inlinedAt: !1908)
!1908 = distinct !DILocation(line: 195, column: 9, scope: !1905)
!1909 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1908)
!1910 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1908)
!1911 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1908)
!1912 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1908)
!1913 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !1908)
!1914 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !1908)
!1915 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !1908)
!1916 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !1908)
!1917 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !1908)
!1918 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1908)
!1919 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1908)
!1920 = distinct !{!1920, !1909, !1921, !312, !313}
!1921 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1908)
!1922 = !DILocation(line: 59, column: 15, scope: !1551, inlinedAt: !1923)
!1923 = distinct !DILocation(line: 196, column: 9, scope: !1905)
!1924 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1923)
!1925 = !DILocation(line: 0, scope: !1530, inlinedAt: !1923)
!1926 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1923)
!1927 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1923)
!1928 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !1923)
!1929 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !1923)
!1930 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !1923)
!1931 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !1923)
!1932 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !1923)
!1933 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1923)
!1934 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1923)
!1935 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1923)
!1936 = distinct !{!1936, !1935, !1937, !312, !313}
!1937 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1923)
!1938 = !DILocation(line: 0, scope: !1492, inlinedAt: !1939)
!1939 = distinct !DILocation(line: 197, column: 34, scope: !1905)
!1940 = !DILocation(line: 23, column: 22, scope: !1500, inlinedAt: !1939)
!1941 = !DILocation(line: 23, column: 19, scope: !1500, inlinedAt: !1939)
!1942 = !DILocation(line: 22, column: 17, scope: !1501, inlinedAt: !1939)
!1943 = !DILocation(line: 22, column: 19, scope: !1501, inlinedAt: !1939)
!1944 = !DILocation(line: 22, column: 5, scope: !1498, inlinedAt: !1939)
!1945 = distinct !{!1945, !1944, !1946, !312, !313}
!1946 = !DILocation(line: 24, column: 5, scope: !1498, inlinedAt: !1939)
!1947 = !DILocation(line: 0, scope: !99, inlinedAt: !1948)
!1948 = distinct !DILocation(line: 197, column: 9, scope: !1905)
!1949 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !1948)
!1950 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !1948)
!1951 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1948)
!1952 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !1948)
!1953 = !DILocation(line: 198, column: 9, scope: !1905)
!1954 = !DILocation(line: 203, column: 9, scope: !1955)
!1955 = distinct !DILexicalBlock(scope: !1956, file: !32, line: 202, column: 19)
!1956 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 202, column: 9)
!1957 = !DILocation(line: 0, scope: !1530, inlinedAt: !1958)
!1958 = distinct !DILocation(line: 204, column: 9, scope: !1955)
!1959 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !1958)
!1960 = !DILocation(line: 59, column: 15, scope: !1551, inlinedAt: !1958)
!1961 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !1958)
!1962 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !1958)
!1963 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !1958)
!1964 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !1958)
!1965 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !1958)
!1966 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !1958)
!1967 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !1958)
!1968 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !1958)
!1969 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !1958)
!1970 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !1958)
!1971 = distinct !{!1971, !1959, !1972, !312, !313}
!1972 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !1958)
!1973 = !DILocation(line: 206, column: 34, scope: !1955)
!1974 = !DILocation(line: 0, scope: !99, inlinedAt: !1975)
!1975 = distinct !DILocation(line: 206, column: 9, scope: !1955)
!1976 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1975)
!1977 = !DILocation(line: 207, column: 9, scope: !1955)
!1978 = !DILocation(line: 212, column: 9, scope: !1979)
!1979 = distinct !DILexicalBlock(scope: !1980, file: !32, line: 211, column: 19)
!1980 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 211, column: 9)
!1981 = !DILocation(line: 216, column: 9, scope: !1982)
!1982 = distinct !DILexicalBlock(scope: !1979, file: !32, line: 216, column: 9)
!1983 = !DILocation(line: 217, column: 23, scope: !1984)
!1984 = distinct !DILexicalBlock(scope: !1985, file: !32, line: 216, column: 47)
!1985 = distinct !DILexicalBlock(scope: !1982, file: !32, line: 216, column: 9)
!1986 = !DILocation(line: 220, column: 45, scope: !1984)
!1987 = !DILocation(line: 221, column: 42, scope: !1984)
!1988 = !DILocation(line: 221, column: 69, scope: !1984)
!1989 = !DILocation(line: 221, column: 32, scope: !1984)
!1990 = !DILocation(line: 216, column: 42, scope: !1985)
!1991 = !DILocation(line: 216, column: 23, scope: !1985)
!1992 = !DILocation(line: 216, column: 27, scope: !1985)
!1993 = distinct !{!1993, !1981, !1994, !312, !313}
!1994 = !DILocation(line: 222, column: 9, scope: !1982)
!1995 = !DILocation(line: 225, column: 34, scope: !1979)
!1996 = !DILocation(line: 0, scope: !99, inlinedAt: !1997)
!1997 = distinct !DILocation(line: 225, column: 9, scope: !1979)
!1998 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !1997)
!1999 = !DILocation(line: 226, column: 9, scope: !1979)
!2000 = !DILocation(line: 229, column: 9, scope: !2001)
!2001 = distinct !DILexicalBlock(scope: !2002, file: !32, line: 228, column: 19)
!2002 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 228, column: 9)
!2003 = !DILocation(line: 233, column: 9, scope: !2004)
!2004 = distinct !DILexicalBlock(scope: !2001, file: !32, line: 233, column: 9)
!2005 = !DILocation(line: 234, column: 23, scope: !2006)
!2006 = distinct !DILexicalBlock(scope: !2007, file: !32, line: 233, column: 47)
!2007 = distinct !DILexicalBlock(scope: !2004, file: !32, line: 233, column: 9)
!2008 = !DILocation(line: 237, column: 45, scope: !2006)
!2009 = !DILocation(line: 238, column: 42, scope: !2006)
!2010 = !DILocation(line: 238, column: 69, scope: !2006)
!2011 = !DILocation(line: 238, column: 32, scope: !2006)
!2012 = !DILocation(line: 233, column: 42, scope: !2007)
!2013 = !DILocation(line: 233, column: 23, scope: !2007)
!2014 = !DILocation(line: 233, column: 27, scope: !2007)
!2015 = distinct !{!2015, !2003, !2016, !312, !313}
!2016 = !DILocation(line: 239, column: 9, scope: !2004)
!2017 = !DILocation(line: 240, column: 34, scope: !2001)
!2018 = !DILocation(line: 0, scope: !99, inlinedAt: !2019)
!2019 = distinct !DILocation(line: 240, column: 9, scope: !2001)
!2020 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2019)
!2021 = !DILocation(line: 241, column: 9, scope: !2001)
!2022 = !DILocation(line: 246, column: 9, scope: !2023)
!2023 = distinct !DILexicalBlock(scope: !2024, file: !32, line: 245, column: 19)
!2024 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 245, column: 9)
!2025 = !DILocation(line: 250, column: 9, scope: !2026)
!2026 = distinct !DILexicalBlock(scope: !2023, file: !32, line: 250, column: 9)
!2027 = !DILocation(line: 251, column: 42, scope: !2028)
!2028 = distinct !DILexicalBlock(scope: !2029, file: !32, line: 250, column: 47)
!2029 = distinct !DILexicalBlock(scope: !2026, file: !32, line: 250, column: 9)
!2030 = !DILocation(line: 251, column: 23, scope: !2028)
!2031 = !DILocation(line: 254, column: 45, scope: !2028)
!2032 = !DILocation(line: 255, column: 42, scope: !2028)
!2033 = !DILocation(line: 255, column: 69, scope: !2028)
!2034 = !DILocation(line: 255, column: 32, scope: !2028)
!2035 = !DILocation(line: 250, column: 42, scope: !2029)
!2036 = !DILocation(line: 250, column: 23, scope: !2029)
!2037 = !DILocation(line: 250, column: 27, scope: !2029)
!2038 = distinct !{!2038, !2025, !2039, !312, !313}
!2039 = !DILocation(line: 256, column: 9, scope: !2026)
!2040 = !DILocation(line: 259, column: 34, scope: !2023)
!2041 = !DILocation(line: 0, scope: !99, inlinedAt: !2042)
!2042 = distinct !DILocation(line: 259, column: 9, scope: !2023)
!2043 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2042)
!2044 = !DILocation(line: 260, column: 9, scope: !2023)
!2045 = !DILocation(line: 265, column: 9, scope: !1606)
!2046 = !DILocation(line: 0, scope: !1606)
!2047 = !DILocation(line: 273, column: 9, scope: !2048)
!2048 = distinct !DILexicalBlock(scope: !1606, file: !32, line: 273, column: 9)
!2049 = !DILocation(line: 274, column: 39, scope: !2050)
!2050 = distinct !DILexicalBlock(scope: !2051, file: !32, line: 273, column: 47)
!2051 = distinct !DILexicalBlock(scope: !2048, file: !32, line: 273, column: 9)
!2052 = !DILocation(line: 274, column: 23, scope: !2050)
!2053 = !DILocation(line: 277, column: 45, scope: !2050)
!2054 = !DILocation(line: 278, column: 42, scope: !2050)
!2055 = !DILocation(line: 278, column: 69, scope: !2050)
!2056 = !DILocation(line: 278, column: 32, scope: !2050)
!2057 = !DILocation(line: 273, column: 42, scope: !2051)
!2058 = !DILocation(line: 273, column: 23, scope: !2051)
!2059 = !DILocation(line: 273, column: 27, scope: !2051)
!2060 = distinct !{!2060, !2047, !2061, !312, !313}
!2061 = !DILocation(line: 279, column: 9, scope: !2048)
!2062 = !DILocation(line: 283, column: 39, scope: !2063)
!2063 = distinct !DILexicalBlock(scope: !2064, file: !32, line: 282, column: 47)
!2064 = distinct !DILexicalBlock(scope: !2065, file: !32, line: 282, column: 9)
!2065 = distinct !DILexicalBlock(scope: !1606, file: !32, line: 282, column: 9)
!2066 = !DILocation(line: 283, column: 23, scope: !2063)
!2067 = !DILocation(line: 286, column: 45, scope: !2063)
!2068 = !DILocation(line: 287, column: 42, scope: !2063)
!2069 = !DILocation(line: 287, column: 69, scope: !2063)
!2070 = !DILocation(line: 287, column: 32, scope: !2063)
!2071 = !DILocation(line: 282, column: 42, scope: !2064)
!2072 = !DILocation(line: 282, column: 23, scope: !2064)
!2073 = !DILocation(line: 282, column: 27, scope: !2064)
!2074 = !DILocation(line: 282, column: 9, scope: !2065)
!2075 = distinct !{!2075, !2074, !2076, !312, !313}
!2076 = !DILocation(line: 288, column: 9, scope: !2065)
!2077 = !DILocation(line: 0, scope: !1492, inlinedAt: !2078)
!2078 = distinct !DILocation(line: 289, column: 34, scope: !1606)
!2079 = !DILocation(line: 23, column: 22, scope: !1500, inlinedAt: !2078)
!2080 = !DILocation(line: 23, column: 19, scope: !1500, inlinedAt: !2078)
!2081 = !DILocation(line: 22, column: 17, scope: !1501, inlinedAt: !2078)
!2082 = !DILocation(line: 22, column: 19, scope: !1501, inlinedAt: !2078)
!2083 = !DILocation(line: 22, column: 5, scope: !1498, inlinedAt: !2078)
!2084 = distinct !{!2084, !2083, !2085, !312, !313}
!2085 = !DILocation(line: 24, column: 5, scope: !1498, inlinedAt: !2078)
!2086 = !DILocation(line: 0, scope: !99, inlinedAt: !2087)
!2087 = distinct !DILocation(line: 289, column: 9, scope: !1606)
!2088 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !2087)
!2089 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !2087)
!2090 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2087)
!2091 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !2087)
!2092 = !DILocation(line: 295, column: 9, scope: !2093)
!2093 = distinct !DILexicalBlock(scope: !2094, file: !32, line: 294, column: 19)
!2094 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 294, column: 9)
!2095 = !DILocation(line: 0, scope: !1530, inlinedAt: !2096)
!2096 = distinct !DILocation(line: 297, column: 9, scope: !2093)
!2097 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !2096)
!2098 = !DILocation(line: 59, column: 15, scope: !1551, inlinedAt: !2096)
!2099 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !2096)
!2100 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !2096)
!2101 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !2096)
!2102 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !2096)
!2103 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !2096)
!2104 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !2096)
!2105 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !2096)
!2106 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !2096)
!2107 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !2096)
!2108 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !2096)
!2109 = distinct !{!2109, !2097, !2110, !312, !313}
!2110 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !2096)
!2111 = !DILocation(line: 303, column: 42, scope: !2112)
!2112 = distinct !DILexicalBlock(scope: !2113, file: !32, line: 302, column: 47)
!2113 = distinct !DILexicalBlock(scope: !2114, file: !32, line: 302, column: 9)
!2114 = distinct !DILexicalBlock(scope: !2093, file: !32, line: 302, column: 9)
!2115 = !DILocation(line: 303, column: 23, scope: !2112)
!2116 = !DILocation(line: 306, column: 45, scope: !2112)
!2117 = !DILocation(line: 307, column: 42, scope: !2112)
!2118 = !DILocation(line: 307, column: 69, scope: !2112)
!2119 = !DILocation(line: 307, column: 32, scope: !2112)
!2120 = !DILocation(line: 302, column: 42, scope: !2113)
!2121 = !DILocation(line: 302, column: 23, scope: !2113)
!2122 = !DILocation(line: 302, column: 27, scope: !2113)
!2123 = !DILocation(line: 302, column: 9, scope: !2114)
!2124 = distinct !{!2124, !2123, !2125, !312, !313}
!2125 = !DILocation(line: 308, column: 9, scope: !2114)
!2126 = !DILocation(line: 0, scope: !1492, inlinedAt: !2127)
!2127 = distinct !DILocation(line: 309, column: 34, scope: !2093)
!2128 = !DILocation(line: 23, column: 22, scope: !1500, inlinedAt: !2127)
!2129 = !DILocation(line: 23, column: 19, scope: !1500, inlinedAt: !2127)
!2130 = !DILocation(line: 22, column: 17, scope: !1501, inlinedAt: !2127)
!2131 = !DILocation(line: 22, column: 19, scope: !1501, inlinedAt: !2127)
!2132 = !DILocation(line: 22, column: 5, scope: !1498, inlinedAt: !2127)
!2133 = distinct !{!2133, !2132, !2134, !312, !313}
!2134 = !DILocation(line: 24, column: 5, scope: !1498, inlinedAt: !2127)
!2135 = !DILocation(line: 0, scope: !99, inlinedAt: !2136)
!2136 = distinct !DILocation(line: 309, column: 9, scope: !2093)
!2137 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !2136)
!2138 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !2136)
!2139 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2136)
!2140 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !2136)
!2141 = !DILocation(line: 310, column: 9, scope: !2093)
!2142 = !DILocation(line: 315, column: 9, scope: !2143)
!2143 = distinct !DILexicalBlock(scope: !2144, file: !32, line: 314, column: 19)
!2144 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 314, column: 9)
!2145 = !DILocation(line: 0, scope: !1530, inlinedAt: !2146)
!2146 = distinct !DILocation(line: 317, column: 9, scope: !2143)
!2147 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !2146)
!2148 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !2146)
!2149 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !2146)
!2150 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !2146)
!2151 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !2146)
!2152 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !2146)
!2153 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !2146)
!2154 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !2146)
!2155 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !2146)
!2156 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !2146)
!2157 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !2146)
!2158 = distinct !{!2158, !2147, !2159, !312, !313}
!2159 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !2146)
!2160 = !DILocation(line: 319, column: 34, scope: !2143)
!2161 = !DILocation(line: 0, scope: !99, inlinedAt: !2162)
!2162 = distinct !DILocation(line: 319, column: 9, scope: !2143)
!2163 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2162)
!2164 = !DILocation(line: 320, column: 9, scope: !2143)
!2165 = !DILocation(line: 323, column: 9, scope: !2166)
!2166 = distinct !DILexicalBlock(scope: !2167, file: !32, line: 322, column: 19)
!2167 = distinct !DILexicalBlock(scope: !1589, file: !32, line: 322, column: 9)
!2168 = !DILocation(line: 0, scope: !1530, inlinedAt: !2169)
!2169 = distinct !DILocation(line: 324, column: 9, scope: !2166)
!2170 = !DILocation(line: 58, column: 5, scope: !1547, inlinedAt: !2169)
!2171 = !DILocation(line: 59, column: 25, scope: !1551, inlinedAt: !2169)
!2172 = !DILocation(line: 62, column: 19, scope: !1552, inlinedAt: !2169)
!2173 = !DILocation(line: 61, column: 21, scope: !1552, inlinedAt: !2169)
!2174 = !DILocation(line: 67, column: 47, scope: !1559, inlinedAt: !2169)
!2175 = !DILocation(line: 69, column: 46, scope: !1565, inlinedAt: !2169)
!2176 = !DILocation(line: 69, column: 38, scope: !1565, inlinedAt: !2169)
!2177 = !DILocation(line: 69, column: 36, scope: !1565, inlinedAt: !2169)
!2178 = !DILocation(line: 70, column: 13, scope: !1565, inlinedAt: !2169)
!2179 = !DILocation(line: 58, column: 19, scope: !1546, inlinedAt: !2169)
!2180 = !DILocation(line: 58, column: 23, scope: !1546, inlinedAt: !2169)
!2181 = distinct !{!2181, !2170, !2182, !312, !313}
!2182 = !DILocation(line: 83, column: 5, scope: !1547, inlinedAt: !2169)
!2183 = !DILocation(line: 325, column: 34, scope: !2166)
!2184 = !DILocation(line: 0, scope: !99, inlinedAt: !2185)
!2185 = distinct !DILocation(line: 325, column: 9, scope: !2166)
!2186 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2185)
!2187 = !DILocation(line: 326, column: 9, scope: !2166)
!2188 = !DILocation(line: 0, scope: !99, inlinedAt: !2189)
!2189 = distinct !DILocation(line: 329, column: 5, scope: !1589)
!2190 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2189)
!2191 = !DILocation(line: 330, column: 1, scope: !1589)
!2192 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !1609)
!2193 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !1609)
!2194 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !1609)
!2195 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !1609)
!2196 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !1609)
!2197 = distinct !DISubprogram(name: "frame1_checksum", scope: !2198, file: !2198, line: 30, type: !296, scopeLine: 30, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2199)
!2198 = !DIFile(filename: "./test_frame1.h", directory: "/home/user/jcc/examples/correctness")
!2199 = !{!2200, !2201}
!2200 = !DILocalVariable(name: "i", scope: !2197, file: !2198, line: 31, type: !8)
!2201 = !DILocalVariable(name: "sum", scope: !2197, file: !2198, line: 32, type: !8)
!2202 = !DILocation(line: 0, scope: !2197)
!2203 = !DILocation(line: 33, column: 5, scope: !2204)
!2204 = distinct !DILexicalBlock(scope: !2197, file: !2198, line: 33, column: 5)
!2205 = !DILocation(line: 34, column: 22, scope: !2206)
!2206 = distinct !DILexicalBlock(scope: !2207, file: !2198, line: 33, column: 48)
!2207 = distinct !DILexicalBlock(scope: !2204, file: !2198, line: 33, column: 5)
!2208 = !DILocation(line: 34, column: 19, scope: !2206)
!2209 = !DILocation(line: 33, column: 17, scope: !2207)
!2210 = !DILocation(line: 33, column: 19, scope: !2207)
!2211 = distinct !{!2211, !2203, !2212, !312, !313}
!2212 = !DILocation(line: 35, column: 5, scope: !2204)
!2213 = !DILocation(line: 36, column: 5, scope: !2197)
!2214 = distinct !DISubprogram(name: "frame1_setPixel", scope: !2198, file: !2198, line: 40, type: !1509, scopeLine: 40, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2215)
!2215 = !{!2216, !2217, !2218, !2219, !2220}
!2216 = !DILocalVariable(name: "x", arg: 1, scope: !2214, file: !2198, line: 40, type: !8)
!2217 = !DILocalVariable(name: "y", arg: 2, scope: !2214, file: !2198, line: 40, type: !8)
!2218 = !DILocalVariable(name: "color", arg: 3, scope: !2214, file: !2198, line: 40, type: !5)
!2219 = !DILocalVariable(name: "byteIdx", scope: !2214, file: !2198, line: 41, type: !8)
!2220 = !DILocalVariable(name: "mask", scope: !2214, file: !2198, line: 42, type: !5)
!2221 = !DILocation(line: 0, scope: !2214)
!2222 = !DILocation(line: 44, column: 15, scope: !2223)
!2223 = distinct !DILexicalBlock(scope: !2214, file: !2198, line: 44, column: 9)
!2224 = !DILocation(line: 47, column: 18, scope: !2214)
!2225 = !DILocation(line: 47, column: 29, scope: !2214)
!2226 = !DILocation(line: 47, column: 24, scope: !2214)
!2227 = !DILocation(line: 48, column: 30, scope: !2214)
!2228 = !DILocation(line: 48, column: 24, scope: !2214)
!2229 = !DILocation(line: 50, column: 9, scope: !2230)
!2230 = distinct !DILexicalBlock(scope: !2214, file: !2198, line: 50, column: 9)
!2231 = !DILocation(line: 0, scope: !2230)
!2232 = !DILocation(line: 50, column: 9, scope: !2214)
!2233 = !DILocation(line: 54, column: 1, scope: !2214)
!2234 = distinct !DISubprogram(name: "frame1_fillRect", scope: !2198, file: !2198, line: 57, type: !2235, scopeLine: 57, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2237)
!2235 = !DISubroutineType(types: !2236)
!2236 = !{null, !8, !8, !8, !8, !5}
!2237 = !{!2238, !2239, !2240, !2241, !2242, !2243, !2244, !2245, !2246, !2247, !2248, !2249, !2250, !2251}
!2238 = !DILocalVariable(name: "x0", arg: 1, scope: !2234, file: !2198, line: 57, type: !8)
!2239 = !DILocalVariable(name: "y0", arg: 2, scope: !2234, file: !2198, line: 57, type: !8)
!2240 = !DILocalVariable(name: "x1", arg: 3, scope: !2234, file: !2198, line: 57, type: !8)
!2241 = !DILocalVariable(name: "y1", arg: 4, scope: !2234, file: !2198, line: 57, type: !8)
!2242 = !DILocalVariable(name: "color", arg: 5, scope: !2234, file: !2198, line: 57, type: !5)
!2243 = !DILocalVariable(name: "y", scope: !2234, file: !2198, line: 58, type: !8)
!2244 = !DILocalVariable(name: "rowBase", scope: !2234, file: !2198, line: 58, type: !8)
!2245 = !DILocalVariable(name: "startByte", scope: !2234, file: !2198, line: 59, type: !8)
!2246 = !DILocalVariable(name: "endByte", scope: !2234, file: !2198, line: 59, type: !8)
!2247 = !DILocalVariable(name: "middleBytes", scope: !2234, file: !2198, line: 59, type: !8)
!2248 = !DILocalVariable(name: "startMask", scope: !2234, file: !2198, line: 60, type: !5)
!2249 = !DILocalVariable(name: "endMask", scope: !2234, file: !2198, line: 60, type: !5)
!2250 = !DILocalVariable(name: "fillByte", scope: !2234, file: !2198, line: 60, type: !5)
!2251 = !DILocalVariable(name: "mask", scope: !2234, file: !2198, line: 60, type: !5)
!2252 = !DILocation(line: 0, scope: !2234)
!2253 = !DILocation(line: 62, column: 16, scope: !2254)
!2254 = distinct !DILexicalBlock(scope: !2234, file: !2198, line: 62, column: 9)
!2255 = !DILocation(line: 65, column: 9, scope: !2234)
!2256 = !DILocation(line: 67, column: 9, scope: !2234)
!2257 = !DILocation(line: 69, column: 9, scope: !2234)
!2258 = !DILocation(line: 71, column: 9, scope: !2234)
!2259 = !DILocation(line: 74, column: 20, scope: !2234)
!2260 = !DILocation(line: 75, column: 18, scope: !2234)
!2261 = !DILocation(line: 76, column: 36, scope: !2234)
!2262 = !DILocation(line: 76, column: 29, scope: !2234)
!2263 = !DILocation(line: 76, column: 17, scope: !2234)
!2264 = !DILocation(line: 77, column: 39, scope: !2234)
!2265 = !DILocation(line: 77, column: 33, scope: !2234)
!2266 = !DILocation(line: 77, column: 27, scope: !2234)
!2267 = !DILocation(line: 77, column: 15, scope: !2234)
!2268 = !DILocation(line: 78, column: 16, scope: !2234)
!2269 = !DILocation(line: 80, column: 12, scope: !2270)
!2270 = distinct !DILexicalBlock(scope: !2234, file: !2198, line: 80, column: 9)
!2271 = !DILocation(line: 80, column: 17, scope: !2270)
!2272 = !DILocation(line: 81, column: 9, scope: !2273)
!2273 = distinct !DILexicalBlock(scope: !2270, file: !2198, line: 80, column: 51)
!2274 = !DILocation(line: 82, column: 9, scope: !2273)
!2275 = !DILocation(line: 85, column: 19, scope: !2234)
!2276 = !DILocation(line: 85, column: 29, scope: !2234)
!2277 = !DILocation(line: 85, column: 39, scope: !2234)
!2278 = !DILocation(line: 87, column: 20, scope: !2279)
!2279 = distinct !DILexicalBlock(scope: !2280, file: !2198, line: 87, column: 5)
!2280 = distinct !DILexicalBlock(scope: !2234, file: !2198, line: 87, column: 5)
!2281 = !DILocation(line: 87, column: 5, scope: !2280)
!2282 = !DILocation(line: 88, column: 21, scope: !2283)
!2283 = distinct !DILexicalBlock(scope: !2279, file: !2198, line: 87, column: 38)
!2284 = !DILocation(line: 0, scope: !2285)
!2285 = distinct !DILexicalBlock(scope: !2283, file: !2198, line: 90, column: 13)
!2286 = !DILocation(line: 90, column: 13, scope: !2283)
!2287 = !DILocation(line: 92, column: 17, scope: !2288)
!2288 = distinct !DILexicalBlock(scope: !2285, file: !2198, line: 90, column: 35)
!2289 = !DILocation(line: 93, column: 48, scope: !2290)
!2290 = distinct !DILexicalBlock(scope: !2288, file: !2198, line: 92, column: 17)
!2291 = !DILocation(line: 93, column: 17, scope: !2290)
!2292 = !DILocation(line: 95, column: 48, scope: !2290)
!2293 = !DILocation(line: 97, column: 17, scope: !2294)
!2294 = distinct !DILexicalBlock(scope: !2285, file: !2198, line: 96, column: 16)
!2295 = !DILocation(line: 0, scope: !2296)
!2296 = distinct !DILexicalBlock(scope: !2294, file: !2198, line: 97, column: 17)
!2297 = !DILocation(line: 102, column: 17, scope: !2294)
!2298 = !DILocation(line: 103, column: 17, scope: !2299)
!2299 = distinct !DILexicalBlock(scope: !2300, file: !2198, line: 102, column: 34)
!2300 = distinct !DILexicalBlock(scope: !2294, file: !2198, line: 102, column: 17)
!2301 = !DILocation(line: 105, column: 13, scope: !2299)
!2302 = !DILocation(line: 0, scope: !2303)
!2303 = distinct !DILexicalBlock(scope: !2294, file: !2198, line: 107, column: 17)
!2304 = !DILocation(line: 107, column: 17, scope: !2294)
!2305 = !DILocation(line: 108, column: 46, scope: !2303)
!2306 = !DILocation(line: 108, column: 17, scope: !2303)
!2307 = !DILocation(line: 110, column: 46, scope: !2303)
!2308 = !DILocation(line: 87, column: 33, scope: !2279)
!2309 = distinct !{!2309, !2281, !2310, !312, !313}
!2310 = !DILocation(line: 112, column: 5, scope: !2280)
!2311 = !DILocation(line: 113, column: 1, scope: !2234)
!2312 = distinct !DISubprogram(name: "frame1_render_ready_screen", scope: !2198, file: !2198, line: 116, type: !624, scopeLine: 116, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2313)
!2313 = !{!2314, !2315, !2316}
!2314 = !DILocalVariable(name: "bird_y", scope: !2312, file: !2198, line: 117, type: !8)
!2315 = !DILocalVariable(name: "BIRD_X", scope: !2312, file: !2198, line: 118, type: !8)
!2316 = !DILocalVariable(name: "BIRD_WIDTH", scope: !2312, file: !2198, line: 119, type: !8)
!2317 = !DILocation(line: 0, scope: !2312)
!2318 = !DILocation(line: 0, scope: !2234, inlinedAt: !2319)
!2319 = distinct !DILocation(line: 122, column: 5, scope: !2312)
!2320 = !DILocation(line: 87, column: 5, scope: !2280, inlinedAt: !2319)
!2321 = !DILocation(line: 88, column: 21, scope: !2283, inlinedAt: !2319)
!2322 = !DILocation(line: 93, column: 35, scope: !2290, inlinedAt: !2319)
!2323 = !DILocation(line: 93, column: 17, scope: !2290, inlinedAt: !2319)
!2324 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2319)
!2325 = !DILocation(line: 87, column: 33, scope: !2279, inlinedAt: !2319)
!2326 = !DILocation(line: 87, column: 20, scope: !2279, inlinedAt: !2319)
!2327 = distinct !{!2327, !2320, !2328, !312, !313}
!2328 = !DILocation(line: 112, column: 5, scope: !2280, inlinedAt: !2319)
!2329 = !DILocation(line: 0, scope: !2214, inlinedAt: !2330)
!2330 = distinct !DILocation(line: 125, column: 5, scope: !2312)
!2331 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2330)
!2332 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2330)
!2333 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2330)
!2334 = !DILocation(line: 0, scope: !2214, inlinedAt: !2335)
!2335 = distinct !DILocation(line: 126, column: 5, scope: !2312)
!2336 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2335)
!2337 = !DILocation(line: 0, scope: !2214, inlinedAt: !2338)
!2338 = distinct !DILocation(line: 127, column: 5, scope: !2312)
!2339 = !DILocation(line: 0, scope: !2214, inlinedAt: !2340)
!2340 = distinct !DILocation(line: 128, column: 5, scope: !2312)
!2341 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2340)
!2342 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2340)
!2343 = !DILocation(line: 129, column: 1, scope: !2312)
!2344 = distinct !DISubprogram(name: "test_frame1", scope: !2198, file: !2198, line: 131, type: !142, scopeLine: 131, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2345)
!2345 = !{!2346, !2347, !2348, !2349, !2352, !2353, !2354, !2355, !2356, !2359, !2360, !2363, !2364, !2367, !2368, !2371, !2372, !2373}
!2346 = !DILocalVariable(name: "apdu", arg: 1, scope: !2344, file: !2198, line: 131, type: !102)
!2347 = !DILocalVariable(name: "buffer", arg: 2, scope: !2344, file: !2198, line: 131, type: !104)
!2348 = !DILocalVariable(name: "p1", arg: 3, scope: !2344, file: !2198, line: 131, type: !5)
!2349 = !DILocalVariable(name: "x0", scope: !2350, file: !2198, line: 261, type: !8)
!2350 = distinct !DILexicalBlock(scope: !2351, file: !2198, line: 260, column: 19)
!2351 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 260, column: 9)
!2352 = !DILocalVariable(name: "x1", scope: !2350, file: !2198, line: 261, type: !8)
!2353 = !DILocalVariable(name: "startMask", scope: !2350, file: !2198, line: 262, type: !5)
!2354 = !DILocalVariable(name: "endMask", scope: !2350, file: !2198, line: 263, type: !5)
!2355 = !DILocalVariable(name: "combined", scope: !2350, file: !2198, line: 264, type: !5)
!2356 = !DILocalVariable(name: "x0", scope: !2357, file: !2198, line: 279, type: !8)
!2357 = distinct !DILexicalBlock(scope: !2358, file: !2198, line: 278, column: 19)
!2358 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 278, column: 9)
!2359 = !DILocalVariable(name: "startByte", scope: !2357, file: !2198, line: 280, type: !8)
!2360 = !DILocalVariable(name: "x1", scope: !2361, file: !2198, line: 287, type: !8)
!2361 = distinct !DILexicalBlock(scope: !2362, file: !2198, line: 286, column: 19)
!2362 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 286, column: 9)
!2363 = !DILocalVariable(name: "endByte", scope: !2361, file: !2198, line: 288, type: !8)
!2364 = !DILocalVariable(name: "y", scope: !2365, file: !2198, line: 295, type: !8)
!2365 = distinct !DILexicalBlock(scope: !2366, file: !2198, line: 294, column: 19)
!2366 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 294, column: 9)
!2367 = !DILocalVariable(name: "rowBase", scope: !2365, file: !2198, line: 296, type: !8)
!2368 = !DILocalVariable(name: "y", scope: !2369, file: !2198, line: 304, type: !8)
!2369 = distinct !DILexicalBlock(scope: !2370, file: !2198, line: 303, column: 19)
!2370 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 303, column: 9)
!2371 = !DILocalVariable(name: "x0", scope: !2369, file: !2198, line: 305, type: !8)
!2372 = !DILocalVariable(name: "rowBase", scope: !2369, file: !2198, line: 306, type: !8)
!2373 = !DILocalVariable(name: "startByte", scope: !2369, file: !2198, line: 307, type: !8)
!2374 = !DILocation(line: 0, scope: !2344)
!2375 = !DILocation(line: 133, column: 9, scope: !2344)
!2376 = !DILocation(line: 134, column: 9, scope: !2377)
!2377 = distinct !DILexicalBlock(scope: !2378, file: !2198, line: 133, column: 18)
!2378 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 133, column: 9)
!2379 = !DILocation(line: 0, scope: !2312, inlinedAt: !2380)
!2380 = distinct !DILocation(line: 135, column: 9, scope: !2377)
!2381 = !DILocation(line: 0, scope: !2234, inlinedAt: !2382)
!2382 = distinct !DILocation(line: 122, column: 5, scope: !2312, inlinedAt: !2380)
!2383 = !DILocation(line: 87, column: 5, scope: !2280, inlinedAt: !2382)
!2384 = !DILocation(line: 88, column: 21, scope: !2283, inlinedAt: !2382)
!2385 = !DILocation(line: 93, column: 35, scope: !2290, inlinedAt: !2382)
!2386 = !DILocation(line: 93, column: 17, scope: !2290, inlinedAt: !2382)
!2387 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2382)
!2388 = !DILocation(line: 87, column: 33, scope: !2279, inlinedAt: !2382)
!2389 = !DILocation(line: 87, column: 20, scope: !2279, inlinedAt: !2382)
!2390 = distinct !{!2390, !2383, !2391, !312, !313}
!2391 = !DILocation(line: 112, column: 5, scope: !2280, inlinedAt: !2382)
!2392 = !DILocation(line: 0, scope: !2214, inlinedAt: !2393)
!2393 = distinct !DILocation(line: 125, column: 5, scope: !2312, inlinedAt: !2380)
!2394 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2393)
!2395 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2393)
!2396 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2393)
!2397 = !DILocation(line: 0, scope: !2214, inlinedAt: !2398)
!2398 = distinct !DILocation(line: 126, column: 5, scope: !2312, inlinedAt: !2380)
!2399 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2398)
!2400 = !DILocation(line: 0, scope: !2214, inlinedAt: !2401)
!2401 = distinct !DILocation(line: 127, column: 5, scope: !2312, inlinedAt: !2380)
!2402 = !DILocation(line: 0, scope: !2214, inlinedAt: !2403)
!2403 = distinct !DILocation(line: 128, column: 5, scope: !2312, inlinedAt: !2380)
!2404 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2403)
!2405 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2403)
!2406 = !DILocation(line: 0, scope: !2197, inlinedAt: !2407)
!2407 = distinct !DILocation(line: 136, column: 34, scope: !2377)
!2408 = !DILocation(line: 33, column: 5, scope: !2204, inlinedAt: !2407)
!2409 = !DILocation(line: 34, column: 22, scope: !2206, inlinedAt: !2407)
!2410 = !DILocation(line: 34, column: 19, scope: !2206, inlinedAt: !2407)
!2411 = !DILocation(line: 33, column: 17, scope: !2207, inlinedAt: !2407)
!2412 = !DILocation(line: 33, column: 19, scope: !2207, inlinedAt: !2407)
!2413 = distinct !{!2413, !2408, !2414, !312, !313}
!2414 = !DILocation(line: 35, column: 5, scope: !2204, inlinedAt: !2407)
!2415 = !DILocation(line: 0, scope: !99, inlinedAt: !2416)
!2416 = distinct !DILocation(line: 136, column: 9, scope: !2377)
!2417 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !2416)
!2418 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !2416)
!2419 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2416)
!2420 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !2416)
!2421 = !DILocation(line: 137, column: 9, scope: !2377)
!2422 = !DILocation(line: 142, column: 9, scope: !2423)
!2423 = distinct !DILexicalBlock(scope: !2424, file: !2198, line: 141, column: 18)
!2424 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 141, column: 9)
!2425 = !DILocation(line: 0, scope: !2197, inlinedAt: !2426)
!2426 = distinct !DILocation(line: 143, column: 34, scope: !2423)
!2427 = !DILocation(line: 33, column: 5, scope: !2204, inlinedAt: !2426)
!2428 = !DILocation(line: 34, column: 22, scope: !2206, inlinedAt: !2426)
!2429 = !DILocation(line: 34, column: 19, scope: !2206, inlinedAt: !2426)
!2430 = !DILocation(line: 33, column: 17, scope: !2207, inlinedAt: !2426)
!2431 = !DILocation(line: 33, column: 19, scope: !2207, inlinedAt: !2426)
!2432 = distinct !{!2432, !2427, !2433, !312, !313}
!2433 = !DILocation(line: 35, column: 5, scope: !2204, inlinedAt: !2426)
!2434 = !DILocation(line: 0, scope: !99, inlinedAt: !2435)
!2435 = distinct !DILocation(line: 143, column: 9, scope: !2423)
!2436 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !2435)
!2437 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !2435)
!2438 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2435)
!2439 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !2435)
!2440 = !DILocation(line: 144, column: 9, scope: !2423)
!2441 = !DILocation(line: 151, column: 9, scope: !2442)
!2442 = distinct !DILexicalBlock(scope: !2443, file: !2198, line: 150, column: 18)
!2443 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 150, column: 9)
!2444 = !DILocation(line: 0, scope: !2234, inlinedAt: !2445)
!2445 = distinct !DILocation(line: 152, column: 9, scope: !2442)
!2446 = !DILocation(line: 87, column: 5, scope: !2280, inlinedAt: !2445)
!2447 = !DILocation(line: 88, column: 21, scope: !2283, inlinedAt: !2445)
!2448 = !DILocation(line: 93, column: 35, scope: !2290, inlinedAt: !2445)
!2449 = !DILocation(line: 93, column: 17, scope: !2290, inlinedAt: !2445)
!2450 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2445)
!2451 = !DILocation(line: 87, column: 33, scope: !2279, inlinedAt: !2445)
!2452 = !DILocation(line: 87, column: 20, scope: !2279, inlinedAt: !2445)
!2453 = distinct !{!2453, !2446, !2454, !312, !313}
!2454 = !DILocation(line: 112, column: 5, scope: !2280, inlinedAt: !2445)
!2455 = !DILocation(line: 0, scope: !2197, inlinedAt: !2456)
!2456 = distinct !DILocation(line: 153, column: 34, scope: !2442)
!2457 = !DILocation(line: 34, column: 22, scope: !2206, inlinedAt: !2456)
!2458 = !DILocation(line: 34, column: 19, scope: !2206, inlinedAt: !2456)
!2459 = !DILocation(line: 33, column: 17, scope: !2207, inlinedAt: !2456)
!2460 = !DILocation(line: 33, column: 19, scope: !2207, inlinedAt: !2456)
!2461 = !DILocation(line: 33, column: 5, scope: !2204, inlinedAt: !2456)
!2462 = distinct !{!2462, !2461, !2463, !312, !313}
!2463 = !DILocation(line: 35, column: 5, scope: !2204, inlinedAt: !2456)
!2464 = !DILocation(line: 0, scope: !99, inlinedAt: !2465)
!2465 = distinct !DILocation(line: 153, column: 9, scope: !2442)
!2466 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !2465)
!2467 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !2465)
!2468 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2465)
!2469 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !2465)
!2470 = !DILocation(line: 154, column: 9, scope: !2442)
!2471 = !DILocation(line: 165, column: 9, scope: !2472)
!2472 = distinct !DILexicalBlock(scope: !2473, file: !2198, line: 164, column: 18)
!2473 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 164, column: 9)
!2474 = !DILocation(line: 0, scope: !2214, inlinedAt: !2475)
!2475 = distinct !DILocation(line: 166, column: 9, scope: !2472)
!2476 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2475)
!2477 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2475)
!2478 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2475)
!2479 = !DILocation(line: 0, scope: !2214, inlinedAt: !2480)
!2480 = distinct !DILocation(line: 167, column: 9, scope: !2472)
!2481 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2480)
!2482 = !DILocation(line: 0, scope: !2214, inlinedAt: !2483)
!2483 = distinct !DILocation(line: 168, column: 9, scope: !2472)
!2484 = !DILocation(line: 0, scope: !2214, inlinedAt: !2485)
!2485 = distinct !DILocation(line: 169, column: 9, scope: !2472)
!2486 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2485)
!2487 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2485)
!2488 = !DILocation(line: 0, scope: !2197, inlinedAt: !2489)
!2489 = distinct !DILocation(line: 170, column: 34, scope: !2472)
!2490 = !DILocation(line: 33, column: 5, scope: !2204, inlinedAt: !2489)
!2491 = !DILocation(line: 34, column: 22, scope: !2206, inlinedAt: !2489)
!2492 = !DILocation(line: 34, column: 19, scope: !2206, inlinedAt: !2489)
!2493 = !DILocation(line: 33, column: 17, scope: !2207, inlinedAt: !2489)
!2494 = !DILocation(line: 33, column: 19, scope: !2207, inlinedAt: !2489)
!2495 = distinct !{!2495, !2490, !2496, !312, !313}
!2496 = !DILocation(line: 35, column: 5, scope: !2204, inlinedAt: !2489)
!2497 = !DILocation(line: 0, scope: !99, inlinedAt: !2498)
!2498 = distinct !DILocation(line: 170, column: 9, scope: !2472)
!2499 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !2498)
!2500 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !2498)
!2501 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2498)
!2502 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !2498)
!2503 = !DILocation(line: 171, column: 9, scope: !2472)
!2504 = !DILocation(line: 176, column: 9, scope: !2505)
!2505 = distinct !DILexicalBlock(scope: !2506, file: !2198, line: 175, column: 18)
!2506 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 175, column: 9)
!2507 = !DILocation(line: 0, scope: !2312, inlinedAt: !2508)
!2508 = distinct !DILocation(line: 177, column: 9, scope: !2505)
!2509 = !DILocation(line: 0, scope: !2234, inlinedAt: !2510)
!2510 = distinct !DILocation(line: 122, column: 5, scope: !2312, inlinedAt: !2508)
!2511 = !DILocation(line: 87, column: 5, scope: !2280, inlinedAt: !2510)
!2512 = !DILocation(line: 88, column: 21, scope: !2283, inlinedAt: !2510)
!2513 = !DILocation(line: 93, column: 35, scope: !2290, inlinedAt: !2510)
!2514 = !DILocation(line: 93, column: 17, scope: !2290, inlinedAt: !2510)
!2515 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2510)
!2516 = !DILocation(line: 87, column: 33, scope: !2279, inlinedAt: !2510)
!2517 = !DILocation(line: 87, column: 20, scope: !2279, inlinedAt: !2510)
!2518 = distinct !{!2518, !2511, !2519, !312, !313}
!2519 = !DILocation(line: 112, column: 5, scope: !2280, inlinedAt: !2510)
!2520 = !DILocation(line: 0, scope: !2214, inlinedAt: !2521)
!2521 = distinct !DILocation(line: 125, column: 5, scope: !2312, inlinedAt: !2508)
!2522 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2521)
!2523 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2521)
!2524 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2521)
!2525 = !DILocation(line: 0, scope: !2214, inlinedAt: !2526)
!2526 = distinct !DILocation(line: 126, column: 5, scope: !2312, inlinedAt: !2508)
!2527 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2526)
!2528 = !DILocation(line: 0, scope: !2214, inlinedAt: !2529)
!2529 = distinct !DILocation(line: 127, column: 5, scope: !2312, inlinedAt: !2508)
!2530 = !DILocation(line: 0, scope: !2214, inlinedAt: !2531)
!2531 = distinct !DILocation(line: 128, column: 5, scope: !2312, inlinedAt: !2508)
!2532 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2531)
!2533 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2531)
!2534 = !DILocation(line: 0, scope: !99, inlinedAt: !2535)
!2535 = distinct !DILocation(line: 178, column: 9, scope: !2505)
!2536 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2535)
!2537 = !DILocation(line: 179, column: 9, scope: !2505)
!2538 = !DILocation(line: 184, column: 9, scope: !2539)
!2539 = distinct !DILexicalBlock(scope: !2540, file: !2198, line: 183, column: 18)
!2540 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 183, column: 9)
!2541 = !DILocation(line: 0, scope: !2312, inlinedAt: !2542)
!2542 = distinct !DILocation(line: 185, column: 9, scope: !2539)
!2543 = !DILocation(line: 0, scope: !2234, inlinedAt: !2544)
!2544 = distinct !DILocation(line: 122, column: 5, scope: !2312, inlinedAt: !2542)
!2545 = !DILocation(line: 87, column: 5, scope: !2280, inlinedAt: !2544)
!2546 = !DILocation(line: 88, column: 21, scope: !2283, inlinedAt: !2544)
!2547 = !DILocation(line: 93, column: 35, scope: !2290, inlinedAt: !2544)
!2548 = !DILocation(line: 93, column: 17, scope: !2290, inlinedAt: !2544)
!2549 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2544)
!2550 = !DILocation(line: 87, column: 33, scope: !2279, inlinedAt: !2544)
!2551 = !DILocation(line: 87, column: 20, scope: !2279, inlinedAt: !2544)
!2552 = distinct !{!2552, !2545, !2553, !312, !313}
!2553 = !DILocation(line: 112, column: 5, scope: !2280, inlinedAt: !2544)
!2554 = !DILocation(line: 0, scope: !2214, inlinedAt: !2555)
!2555 = distinct !DILocation(line: 125, column: 5, scope: !2312, inlinedAt: !2542)
!2556 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2555)
!2557 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2555)
!2558 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2555)
!2559 = !DILocation(line: 0, scope: !2214, inlinedAt: !2560)
!2560 = distinct !DILocation(line: 126, column: 5, scope: !2312, inlinedAt: !2542)
!2561 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2560)
!2562 = !DILocation(line: 0, scope: !2214, inlinedAt: !2563)
!2563 = distinct !DILocation(line: 127, column: 5, scope: !2312, inlinedAt: !2542)
!2564 = !DILocation(line: 0, scope: !2214, inlinedAt: !2565)
!2565 = distinct !DILocation(line: 128, column: 5, scope: !2312, inlinedAt: !2542)
!2566 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2565)
!2567 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2565)
!2568 = !DILocation(line: 0, scope: !99, inlinedAt: !2569)
!2569 = distinct !DILocation(line: 186, column: 9, scope: !2539)
!2570 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2569)
!2571 = !DILocation(line: 187, column: 9, scope: !2539)
!2572 = !DILocation(line: 192, column: 9, scope: !2573)
!2573 = distinct !DILexicalBlock(scope: !2574, file: !2198, line: 191, column: 18)
!2574 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 191, column: 9)
!2575 = !DILocation(line: 0, scope: !2312, inlinedAt: !2576)
!2576 = distinct !DILocation(line: 193, column: 9, scope: !2573)
!2577 = !DILocation(line: 0, scope: !2234, inlinedAt: !2578)
!2578 = distinct !DILocation(line: 122, column: 5, scope: !2312, inlinedAt: !2576)
!2579 = !DILocation(line: 87, column: 5, scope: !2280, inlinedAt: !2578)
!2580 = !DILocation(line: 88, column: 21, scope: !2283, inlinedAt: !2578)
!2581 = !DILocation(line: 93, column: 35, scope: !2290, inlinedAt: !2578)
!2582 = !DILocation(line: 93, column: 17, scope: !2290, inlinedAt: !2578)
!2583 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2578)
!2584 = !DILocation(line: 87, column: 33, scope: !2279, inlinedAt: !2578)
!2585 = !DILocation(line: 87, column: 20, scope: !2279, inlinedAt: !2578)
!2586 = distinct !{!2586, !2579, !2587, !312, !313}
!2587 = !DILocation(line: 112, column: 5, scope: !2280, inlinedAt: !2578)
!2588 = !DILocation(line: 0, scope: !2214, inlinedAt: !2589)
!2589 = distinct !DILocation(line: 125, column: 5, scope: !2312, inlinedAt: !2576)
!2590 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2589)
!2591 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2589)
!2592 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2589)
!2593 = !DILocation(line: 0, scope: !2214, inlinedAt: !2594)
!2594 = distinct !DILocation(line: 126, column: 5, scope: !2312, inlinedAt: !2576)
!2595 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2594)
!2596 = !DILocation(line: 0, scope: !2214, inlinedAt: !2597)
!2597 = distinct !DILocation(line: 127, column: 5, scope: !2312, inlinedAt: !2576)
!2598 = !DILocation(line: 0, scope: !2214, inlinedAt: !2599)
!2599 = distinct !DILocation(line: 128, column: 5, scope: !2312, inlinedAt: !2576)
!2600 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2599)
!2601 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2599)
!2602 = !DILocation(line: 194, column: 34, scope: !2573)
!2603 = !DILocation(line: 0, scope: !99, inlinedAt: !2604)
!2604 = distinct !DILocation(line: 194, column: 9, scope: !2573)
!2605 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2604)
!2606 = !DILocation(line: 195, column: 9, scope: !2573)
!2607 = !DILocation(line: 200, column: 9, scope: !2608)
!2608 = distinct !DILexicalBlock(scope: !2609, file: !2198, line: 199, column: 18)
!2609 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 199, column: 9)
!2610 = !DILocation(line: 0, scope: !2312, inlinedAt: !2611)
!2611 = distinct !DILocation(line: 201, column: 9, scope: !2608)
!2612 = !DILocation(line: 0, scope: !2234, inlinedAt: !2613)
!2613 = distinct !DILocation(line: 122, column: 5, scope: !2312, inlinedAt: !2611)
!2614 = !DILocation(line: 87, column: 5, scope: !2280, inlinedAt: !2613)
!2615 = !DILocation(line: 88, column: 21, scope: !2283, inlinedAt: !2613)
!2616 = !DILocation(line: 93, column: 35, scope: !2290, inlinedAt: !2613)
!2617 = !DILocation(line: 93, column: 17, scope: !2290, inlinedAt: !2613)
!2618 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2613)
!2619 = !DILocation(line: 87, column: 33, scope: !2279, inlinedAt: !2613)
!2620 = !DILocation(line: 87, column: 20, scope: !2279, inlinedAt: !2613)
!2621 = distinct !{!2621, !2614, !2622, !312, !313}
!2622 = !DILocation(line: 112, column: 5, scope: !2280, inlinedAt: !2613)
!2623 = !DILocation(line: 0, scope: !2214, inlinedAt: !2624)
!2624 = distinct !DILocation(line: 125, column: 5, scope: !2312, inlinedAt: !2611)
!2625 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2624)
!2626 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2624)
!2627 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2624)
!2628 = !DILocation(line: 0, scope: !2214, inlinedAt: !2629)
!2629 = distinct !DILocation(line: 126, column: 5, scope: !2312, inlinedAt: !2611)
!2630 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2629)
!2631 = !DILocation(line: 0, scope: !2214, inlinedAt: !2632)
!2632 = distinct !DILocation(line: 127, column: 5, scope: !2312, inlinedAt: !2611)
!2633 = !DILocation(line: 0, scope: !2214, inlinedAt: !2634)
!2634 = distinct !DILocation(line: 128, column: 5, scope: !2312, inlinedAt: !2611)
!2635 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2634)
!2636 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2634)
!2637 = !DILocation(line: 202, column: 34, scope: !2608)
!2638 = !DILocation(line: 0, scope: !99, inlinedAt: !2639)
!2639 = distinct !DILocation(line: 202, column: 9, scope: !2608)
!2640 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2639)
!2641 = !DILocation(line: 203, column: 9, scope: !2608)
!2642 = !DILocation(line: 208, column: 9, scope: !2643)
!2643 = distinct !DILexicalBlock(scope: !2644, file: !2198, line: 207, column: 18)
!2644 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 207, column: 9)
!2645 = !DILocation(line: 0, scope: !2312, inlinedAt: !2646)
!2646 = distinct !DILocation(line: 209, column: 9, scope: !2643)
!2647 = !DILocation(line: 0, scope: !2234, inlinedAt: !2648)
!2648 = distinct !DILocation(line: 122, column: 5, scope: !2312, inlinedAt: !2646)
!2649 = !DILocation(line: 87, column: 5, scope: !2280, inlinedAt: !2648)
!2650 = !DILocation(line: 88, column: 21, scope: !2283, inlinedAt: !2648)
!2651 = !DILocation(line: 93, column: 35, scope: !2290, inlinedAt: !2648)
!2652 = !DILocation(line: 93, column: 17, scope: !2290, inlinedAt: !2648)
!2653 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2648)
!2654 = !DILocation(line: 87, column: 33, scope: !2279, inlinedAt: !2648)
!2655 = !DILocation(line: 87, column: 20, scope: !2279, inlinedAt: !2648)
!2656 = distinct !{!2656, !2649, !2657, !312, !313}
!2657 = !DILocation(line: 112, column: 5, scope: !2280, inlinedAt: !2648)
!2658 = !DILocation(line: 0, scope: !2214, inlinedAt: !2659)
!2659 = distinct !DILocation(line: 125, column: 5, scope: !2312, inlinedAt: !2646)
!2660 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2659)
!2661 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2659)
!2662 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2659)
!2663 = !DILocation(line: 0, scope: !2214, inlinedAt: !2664)
!2664 = distinct !DILocation(line: 126, column: 5, scope: !2312, inlinedAt: !2646)
!2665 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2664)
!2666 = !DILocation(line: 0, scope: !2214, inlinedAt: !2667)
!2667 = distinct !DILocation(line: 127, column: 5, scope: !2312, inlinedAt: !2646)
!2668 = !DILocation(line: 0, scope: !2214, inlinedAt: !2669)
!2669 = distinct !DILocation(line: 128, column: 5, scope: !2312, inlinedAt: !2646)
!2670 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2669)
!2671 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2669)
!2672 = !DILocation(line: 210, column: 34, scope: !2643)
!2673 = !DILocation(line: 0, scope: !99, inlinedAt: !2674)
!2674 = distinct !DILocation(line: 210, column: 9, scope: !2643)
!2675 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2674)
!2676 = !DILocation(line: 211, column: 9, scope: !2643)
!2677 = !DILocation(line: 220, column: 9, scope: !2678)
!2678 = distinct !DILexicalBlock(scope: !2679, file: !2198, line: 219, column: 19)
!2679 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 219, column: 9)
!2680 = !DILocation(line: 0, scope: !2214, inlinedAt: !2681)
!2681 = distinct !DILocation(line: 221, column: 9, scope: !2678)
!2682 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2681)
!2683 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2681)
!2684 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2681)
!2685 = !DILocation(line: 0, scope: !99, inlinedAt: !2686)
!2686 = distinct !DILocation(line: 222, column: 9, scope: !2678)
!2687 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2686)
!2688 = !DILocation(line: 223, column: 9, scope: !2678)
!2689 = !DILocation(line: 230, column: 9, scope: !2690)
!2690 = distinct !DILexicalBlock(scope: !2691, file: !2198, line: 229, column: 19)
!2691 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 229, column: 9)
!2692 = !DILocation(line: 0, scope: !2214, inlinedAt: !2693)
!2693 = distinct !DILocation(line: 231, column: 9, scope: !2690)
!2694 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2693)
!2695 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2693)
!2696 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2693)
!2697 = !DILocation(line: 0, scope: !99, inlinedAt: !2698)
!2698 = distinct !DILocation(line: 232, column: 9, scope: !2690)
!2699 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2698)
!2700 = !DILocation(line: 233, column: 9, scope: !2690)
!2701 = !DILocation(line: 239, column: 9, scope: !2702)
!2702 = distinct !DILexicalBlock(scope: !2703, file: !2198, line: 238, column: 19)
!2703 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 238, column: 9)
!2704 = !DILocation(line: 0, scope: !2214, inlinedAt: !2705)
!2705 = distinct !DILocation(line: 240, column: 9, scope: !2702)
!2706 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2705)
!2707 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2705)
!2708 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2705)
!2709 = !DILocation(line: 0, scope: !99, inlinedAt: !2710)
!2710 = distinct !DILocation(line: 241, column: 9, scope: !2702)
!2711 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2710)
!2712 = !DILocation(line: 242, column: 9, scope: !2702)
!2713 = !DILocation(line: 248, column: 9, scope: !2714)
!2714 = distinct !DILexicalBlock(scope: !2715, file: !2198, line: 247, column: 19)
!2715 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 247, column: 9)
!2716 = !DILocation(line: 0, scope: !2214, inlinedAt: !2717)
!2717 = distinct !DILocation(line: 249, column: 9, scope: !2714)
!2718 = !DILocation(line: 51, column: 38, scope: !2230, inlinedAt: !2717)
!2719 = !DILocation(line: 51, column: 65, scope: !2230, inlinedAt: !2717)
!2720 = !DILocation(line: 51, column: 28, scope: !2230, inlinedAt: !2717)
!2721 = !DILocation(line: 0, scope: !99, inlinedAt: !2722)
!2722 = distinct !DILocation(line: 250, column: 9, scope: !2714)
!2723 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2722)
!2724 = !DILocation(line: 251, column: 9, scope: !2714)
!2725 = !DILocation(line: 0, scope: !2350)
!2726 = !DILocation(line: 0, scope: !99, inlinedAt: !2727)
!2727 = distinct !DILocation(line: 265, column: 9, scope: !2350)
!2728 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2727)
!2729 = !DILocation(line: 271, column: 9, scope: !2730)
!2730 = distinct !DILexicalBlock(scope: !2731, file: !2198, line: 270, column: 19)
!2731 = distinct !DILexicalBlock(scope: !2344, file: !2198, line: 270, column: 9)
!2732 = !DILocation(line: 0, scope: !2234, inlinedAt: !2733)
!2733 = distinct !DILocation(line: 272, column: 9, scope: !2730)
!2734 = !DILocation(line: 93, column: 48, scope: !2290, inlinedAt: !2733)
!2735 = !DILocation(line: 0, scope: !99, inlinedAt: !2736)
!2736 = distinct !DILocation(line: 273, column: 9, scope: !2730)
!2737 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2736)
!2738 = !DILocation(line: 274, column: 9, scope: !2730)
!2739 = !DILocation(line: 0, scope: !2357)
!2740 = !DILocation(line: 0, scope: !99, inlinedAt: !2741)
!2741 = distinct !DILocation(line: 281, column: 9, scope: !2357)
!2742 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2741)
!2743 = !DILocation(line: 0, scope: !2361)
!2744 = !DILocation(line: 0, scope: !99, inlinedAt: !2745)
!2745 = distinct !DILocation(line: 289, column: 9, scope: !2361)
!2746 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2745)
!2747 = !DILocation(line: 0, scope: !2365)
!2748 = !DILocation(line: 0, scope: !99, inlinedAt: !2749)
!2749 = distinct !DILocation(line: 297, column: 9, scope: !2365)
!2750 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2749)
!2751 = !DILocation(line: 0, scope: !2369)
!2752 = !DILocation(line: 0, scope: !99, inlinedAt: !2753)
!2753 = distinct !DILocation(line: 308, column: 9, scope: !2369)
!2754 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2753)
!2755 = !DILocation(line: 0, scope: !99, inlinedAt: !2756)
!2756 = distinct !DILocation(line: 312, column: 5, scope: !2344)
!2757 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2756)
!2758 = !DILocation(line: 313, column: 1, scope: !2344)
!2759 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !2374)
!2760 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !2374)
!2761 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !2374)
!2762 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !2374)
!2763 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !2374)
!2764 = distinct !DISubprogram(name: "test_arithmetic", scope: !3, file: !3, line: 124, type: !142, scopeLine: 124, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2765)
!2765 = !{!2766, !2767, !2768, !2769, !2770}
!2766 = !DILocalVariable(name: "apdu", arg: 1, scope: !2764, file: !3, line: 124, type: !102)
!2767 = !DILocalVariable(name: "buffer", arg: 2, scope: !2764, file: !3, line: 124, type: !104)
!2768 = !DILocalVariable(name: "p1", arg: 3, scope: !2764, file: !3, line: 124, type: !5)
!2769 = !DILocalVariable(name: "a", scope: !2764, file: !3, line: 125, type: !8)
!2770 = !DILocalVariable(name: "b", scope: !2764, file: !3, line: 126, type: !8)
!2771 = !DILocation(line: 0, scope: !2764)
!2772 = !DILocation(line: 128, column: 9, scope: !2764)
!2773 = !DILocation(line: 0, scope: !99, inlinedAt: !2774)
!2774 = distinct !DILocation(line: 129, column: 20, scope: !2775)
!2775 = distinct !DILexicalBlock(scope: !2776, file: !3, line: 129, column: 18)
!2776 = distinct !DILexicalBlock(scope: !2764, file: !3, line: 129, column: 9)
!2777 = !DILocation(line: 129, column: 53, scope: !2775)
!2778 = !DILocation(line: 0, scope: !99, inlinedAt: !2779)
!2779 = distinct !DILocation(line: 130, column: 20, scope: !2780)
!2780 = distinct !DILexicalBlock(scope: !2781, file: !3, line: 130, column: 18)
!2781 = distinct !DILexicalBlock(scope: !2764, file: !3, line: 130, column: 9)
!2782 = !DILocation(line: 130, column: 53, scope: !2780)
!2783 = !DILocation(line: 0, scope: !99, inlinedAt: !2784)
!2784 = distinct !DILocation(line: 131, column: 20, scope: !2785)
!2785 = distinct !DILexicalBlock(scope: !2786, file: !3, line: 131, column: 18)
!2786 = distinct !DILexicalBlock(scope: !2764, file: !3, line: 131, column: 9)
!2787 = !DILocation(line: 131, column: 53, scope: !2785)
!2788 = !DILocation(line: 0, scope: !99, inlinedAt: !2789)
!2789 = distinct !DILocation(line: 132, column: 20, scope: !2790)
!2790 = distinct !DILexicalBlock(scope: !2791, file: !3, line: 132, column: 18)
!2791 = distinct !DILexicalBlock(scope: !2764, file: !3, line: 132, column: 9)
!2792 = !DILocation(line: 132, column: 53, scope: !2790)
!2793 = !DILocation(line: 0, scope: !99, inlinedAt: !2794)
!2794 = distinct !DILocation(line: 133, column: 20, scope: !2795)
!2795 = distinct !DILexicalBlock(scope: !2796, file: !3, line: 133, column: 18)
!2796 = distinct !DILexicalBlock(scope: !2764, file: !3, line: 133, column: 9)
!2797 = !DILocation(line: 133, column: 50, scope: !2795)
!2798 = !DILocation(line: 0, scope: !99, inlinedAt: !2799)
!2799 = distinct !DILocation(line: 134, column: 20, scope: !2800)
!2800 = distinct !DILexicalBlock(scope: !2801, file: !3, line: 134, column: 18)
!2801 = distinct !DILexicalBlock(scope: !2764, file: !3, line: 134, column: 9)
!2802 = !DILocation(line: 134, column: 57, scope: !2800)
!2803 = !DILocation(line: 0, scope: !99, inlinedAt: !2804)
!2804 = distinct !DILocation(line: 135, column: 20, scope: !2805)
!2805 = distinct !DILexicalBlock(scope: !2806, file: !3, line: 135, column: 18)
!2806 = distinct !DILexicalBlock(scope: !2764, file: !3, line: 135, column: 9)
!2807 = !DILocation(line: 135, column: 59, scope: !2805)
!2808 = !DILocation(line: 0, scope: !99, inlinedAt: !2809)
!2809 = distinct !DILocation(line: 136, column: 5, scope: !2764)
!2810 = !DILocation(line: 137, column: 1, scope: !2764)
!2811 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !2771)
!2812 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2771)
!2813 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !2771)
!2814 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !2771)
!2815 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !2771)
!2816 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !2771)
!2817 = distinct !DISubprogram(name: "test_bitwise", scope: !3, file: !3, line: 143, type: !142, scopeLine: 143, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2818)
!2818 = !{!2819, !2820, !2821, !2822, !2823}
!2819 = !DILocalVariable(name: "apdu", arg: 1, scope: !2817, file: !3, line: 143, type: !102)
!2820 = !DILocalVariable(name: "buffer", arg: 2, scope: !2817, file: !3, line: 143, type: !104)
!2821 = !DILocalVariable(name: "p1", arg: 3, scope: !2817, file: !3, line: 143, type: !5)
!2822 = !DILocalVariable(name: "a", scope: !2817, file: !3, line: 144, type: !8)
!2823 = !DILocalVariable(name: "b", scope: !2817, file: !3, line: 145, type: !8)
!2824 = !DILocation(line: 0, scope: !2817)
!2825 = !DILocation(line: 147, column: 9, scope: !2817)
!2826 = !DILocation(line: 0, scope: !99, inlinedAt: !2827)
!2827 = distinct !DILocation(line: 148, column: 20, scope: !2828)
!2828 = distinct !DILexicalBlock(scope: !2829, file: !3, line: 148, column: 18)
!2829 = distinct !DILexicalBlock(scope: !2817, file: !3, line: 148, column: 9)
!2830 = !DILocation(line: 148, column: 53, scope: !2828)
!2831 = !DILocation(line: 0, scope: !99, inlinedAt: !2832)
!2832 = distinct !DILocation(line: 149, column: 20, scope: !2833)
!2833 = distinct !DILexicalBlock(scope: !2834, file: !3, line: 149, column: 18)
!2834 = distinct !DILexicalBlock(scope: !2817, file: !3, line: 149, column: 9)
!2835 = !DILocation(line: 149, column: 53, scope: !2833)
!2836 = !DILocation(line: 0, scope: !99, inlinedAt: !2837)
!2837 = distinct !DILocation(line: 150, column: 20, scope: !2838)
!2838 = distinct !DILexicalBlock(scope: !2839, file: !3, line: 150, column: 18)
!2839 = distinct !DILexicalBlock(scope: !2817, file: !3, line: 150, column: 9)
!2840 = !DILocation(line: 150, column: 54, scope: !2838)
!2841 = !DILocation(line: 0, scope: !99, inlinedAt: !2842)
!2842 = distinct !DILocation(line: 151, column: 20, scope: !2843)
!2843 = distinct !DILexicalBlock(scope: !2844, file: !3, line: 151, column: 18)
!2844 = distinct !DILexicalBlock(scope: !2817, file: !3, line: 151, column: 9)
!2845 = !DILocation(line: 151, column: 54, scope: !2843)
!2846 = !DILocation(line: 0, scope: !99, inlinedAt: !2847)
!2847 = distinct !DILocation(line: 152, column: 20, scope: !2848)
!2848 = distinct !DILexicalBlock(scope: !2849, file: !3, line: 152, column: 18)
!2849 = distinct !DILexicalBlock(scope: !2817, file: !3, line: 152, column: 9)
!2850 = !DILocation(line: 152, column: 57, scope: !2848)
!2851 = !DILocation(line: 0, scope: !99, inlinedAt: !2852)
!2852 = distinct !DILocation(line: 153, column: 5, scope: !2817)
!2853 = !DILocation(line: 154, column: 1, scope: !2817)
!2854 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !2824)
!2855 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2824)
!2856 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !2824)
!2857 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !2824)
!2858 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !2824)
!2859 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !2824)
!2860 = distinct !DISubprogram(name: "test_comparison", scope: !3, file: !3, line: 160, type: !142, scopeLine: 160, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2861)
!2861 = !{!2862, !2863, !2864, !2865, !2866}
!2862 = !DILocalVariable(name: "apdu", arg: 1, scope: !2860, file: !3, line: 160, type: !102)
!2863 = !DILocalVariable(name: "buffer", arg: 2, scope: !2860, file: !3, line: 160, type: !104)
!2864 = !DILocalVariable(name: "p1", arg: 3, scope: !2860, file: !3, line: 160, type: !5)
!2865 = !DILocalVariable(name: "a", scope: !2860, file: !3, line: 161, type: !8)
!2866 = !DILocalVariable(name: "b", scope: !2860, file: !3, line: 162, type: !8)
!2867 = !DILocation(line: 0, scope: !2860)
!2868 = !DILocation(line: 164, column: 9, scope: !2860)
!2869 = !DILocation(line: 0, scope: !99, inlinedAt: !2870)
!2870 = distinct !DILocation(line: 165, column: 20, scope: !2871)
!2871 = distinct !DILexicalBlock(scope: !2872, file: !3, line: 165, column: 18)
!2872 = distinct !DILexicalBlock(scope: !2860, file: !3, line: 165, column: 9)
!2873 = !DILocation(line: 165, column: 64, scope: !2871)
!2874 = !DILocation(line: 0, scope: !99, inlinedAt: !2875)
!2875 = distinct !DILocation(line: 166, column: 20, scope: !2876)
!2876 = distinct !DILexicalBlock(scope: !2877, file: !3, line: 166, column: 18)
!2877 = distinct !DILexicalBlock(scope: !2860, file: !3, line: 166, column: 9)
!2878 = !DILocation(line: 166, column: 63, scope: !2876)
!2879 = !DILocation(line: 0, scope: !99, inlinedAt: !2880)
!2880 = distinct !DILocation(line: 168, column: 20, scope: !2881)
!2881 = distinct !DILexicalBlock(scope: !2882, file: !3, line: 168, column: 18)
!2882 = distinct !DILexicalBlock(scope: !2860, file: !3, line: 168, column: 9)
!2883 = !DILocation(line: 168, column: 64, scope: !2881)
!2884 = !DILocation(line: 0, scope: !99, inlinedAt: !2885)
!2885 = distinct !DILocation(line: 170, column: 20, scope: !2886)
!2886 = distinct !DILexicalBlock(scope: !2887, file: !3, line: 170, column: 18)
!2887 = distinct !DILexicalBlock(scope: !2860, file: !3, line: 170, column: 9)
!2888 = !DILocation(line: 170, column: 65, scope: !2886)
!2889 = !DILocation(line: 0, scope: !99, inlinedAt: !2890)
!2890 = distinct !DILocation(line: 171, column: 20, scope: !2891)
!2891 = distinct !DILexicalBlock(scope: !2892, file: !3, line: 171, column: 18)
!2892 = distinct !DILexicalBlock(scope: !2860, file: !3, line: 171, column: 9)
!2893 = !DILocation(line: 171, column: 65, scope: !2891)
!2894 = !DILocation(line: 0, scope: !99, inlinedAt: !2895)
!2895 = distinct !DILocation(line: 172, column: 5, scope: !2860)
!2896 = !DILocation(line: 173, column: 1, scope: !2860)
!2897 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !2867)
!2898 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2867)
!2899 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !2867)
!2900 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !2867)
!2901 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !2867)
!2902 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !2867)
!2903 = distinct !DISubprogram(name: "test_logical", scope: !3, file: !3, line: 179, type: !142, scopeLine: 179, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2904)
!2904 = !{!2905, !2906, !2907, !2908, !2909}
!2905 = !DILocalVariable(name: "apdu", arg: 1, scope: !2903, file: !3, line: 179, type: !102)
!2906 = !DILocalVariable(name: "buffer", arg: 2, scope: !2903, file: !3, line: 179, type: !104)
!2907 = !DILocalVariable(name: "p1", arg: 3, scope: !2903, file: !3, line: 179, type: !5)
!2908 = !DILocalVariable(name: "t", scope: !2903, file: !3, line: 180, type: !8)
!2909 = !DILocalVariable(name: "f", scope: !2903, file: !3, line: 181, type: !8)
!2910 = !DILocation(line: 0, scope: !2903)
!2911 = !DILocation(line: 183, column: 9, scope: !2903)
!2912 = !DILocation(line: 0, scope: !99, inlinedAt: !2913)
!2913 = distinct !DILocation(line: 184, column: 20, scope: !2914)
!2914 = distinct !DILexicalBlock(scope: !2915, file: !3, line: 184, column: 18)
!2915 = distinct !DILexicalBlock(scope: !2903, file: !3, line: 184, column: 9)
!2916 = !DILocation(line: 184, column: 64, scope: !2914)
!2917 = !DILocation(line: 0, scope: !99, inlinedAt: !2918)
!2918 = distinct !DILocation(line: 185, column: 20, scope: !2919)
!2919 = distinct !DILexicalBlock(scope: !2920, file: !3, line: 185, column: 18)
!2920 = distinct !DILexicalBlock(scope: !2903, file: !3, line: 185, column: 9)
!2921 = !DILocation(line: 185, column: 64, scope: !2919)
!2922 = !DILocation(line: 0, scope: !99, inlinedAt: !2923)
!2923 = distinct !DILocation(line: 186, column: 20, scope: !2924)
!2924 = distinct !DILexicalBlock(scope: !2925, file: !3, line: 186, column: 18)
!2925 = distinct !DILexicalBlock(scope: !2903, file: !3, line: 186, column: 9)
!2926 = !DILocation(line: 186, column: 64, scope: !2924)
!2927 = !DILocation(line: 0, scope: !99, inlinedAt: !2928)
!2928 = distinct !DILocation(line: 190, column: 20, scope: !2929)
!2929 = distinct !DILexicalBlock(scope: !2930, file: !3, line: 190, column: 18)
!2930 = distinct !DILexicalBlock(scope: !2903, file: !3, line: 190, column: 9)
!2931 = !DILocation(line: 190, column: 64, scope: !2929)
!2932 = !DILocation(line: 0, scope: !99, inlinedAt: !2933)
!2933 = distinct !DILocation(line: 191, column: 20, scope: !2934)
!2934 = distinct !DILexicalBlock(scope: !2935, file: !3, line: 191, column: 18)
!2935 = distinct !DILexicalBlock(scope: !2903, file: !3, line: 191, column: 9)
!2936 = !DILocation(line: 191, column: 60, scope: !2934)
!2937 = !DILocation(line: 0, scope: !99, inlinedAt: !2938)
!2938 = distinct !DILocation(line: 193, column: 5, scope: !2903)
!2939 = !DILocation(line: 194, column: 1, scope: !2903)
!2940 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !2910)
!2941 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2910)
!2942 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !2910)
!2943 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !2910)
!2944 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !2910)
!2945 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !2910)
!2946 = distinct !DISubprogram(name: "test_incdec", scope: !3, file: !3, line: 200, type: !142, scopeLine: 200, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !2947)
!2947 = !{!2948, !2949, !2950, !2951}
!2948 = !DILocalVariable(name: "apdu", arg: 1, scope: !2946, file: !3, line: 200, type: !102)
!2949 = !DILocalVariable(name: "buffer", arg: 2, scope: !2946, file: !3, line: 200, type: !104)
!2950 = !DILocalVariable(name: "p1", arg: 3, scope: !2946, file: !3, line: 200, type: !5)
!2951 = !DILocalVariable(name: "x", scope: !2946, file: !3, line: 201, type: !8)
!2952 = !DILocation(line: 0, scope: !2946)
!2953 = !DILocation(line: 203, column: 9, scope: !2946)
!2954 = !DILocation(line: 0, scope: !99, inlinedAt: !2955)
!2955 = distinct !DILocation(line: 204, column: 27, scope: !2956)
!2956 = distinct !DILexicalBlock(scope: !2957, file: !3, line: 204, column: 18)
!2957 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 204, column: 9)
!2958 = !DILocation(line: 204, column: 58, scope: !2956)
!2959 = !DILocation(line: 0, scope: !99, inlinedAt: !2960)
!2960 = distinct !DILocation(line: 206, column: 27, scope: !2961)
!2961 = distinct !DILexicalBlock(scope: !2962, file: !3, line: 206, column: 18)
!2962 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 206, column: 9)
!2963 = !DILocation(line: 206, column: 58, scope: !2961)
!2964 = !DILocation(line: 0, scope: !99, inlinedAt: !2965)
!2965 = distinct !DILocation(line: 207, column: 27, scope: !2966)
!2966 = distinct !DILexicalBlock(scope: !2967, file: !3, line: 207, column: 18)
!2967 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 207, column: 9)
!2968 = !DILocation(line: 207, column: 58, scope: !2966)
!2969 = !DILocation(line: 0, scope: !99, inlinedAt: !2970)
!2970 = distinct !DILocation(line: 208, column: 32, scope: !2971)
!2971 = distinct !DILexicalBlock(scope: !2972, file: !3, line: 208, column: 18)
!2972 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 208, column: 9)
!2973 = !DILocation(line: 208, column: 61, scope: !2971)
!2974 = !DILocation(line: 0, scope: !99, inlinedAt: !2975)
!2975 = distinct !DILocation(line: 211, column: 39, scope: !2976)
!2976 = distinct !DILexicalBlock(scope: !2977, file: !3, line: 211, column: 18)
!2977 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 211, column: 9)
!2978 = !DILocation(line: 211, column: 68, scope: !2976)
!2979 = !DILocation(line: 0, scope: !99, inlinedAt: !2980)
!2980 = distinct !DILocation(line: 212, column: 39, scope: !2981)
!2981 = distinct !DILexicalBlock(scope: !2982, file: !3, line: 212, column: 18)
!2982 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 212, column: 9)
!2983 = !DILocation(line: 212, column: 68, scope: !2981)
!2984 = !DILocation(line: 0, scope: !99, inlinedAt: !2985)
!2985 = distinct !DILocation(line: 213, column: 38, scope: !2986)
!2986 = distinct !DILexicalBlock(scope: !2987, file: !3, line: 213, column: 18)
!2987 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 213, column: 9)
!2988 = !DILocation(line: 213, column: 67, scope: !2986)
!2989 = !DILocation(line: 0, scope: !99, inlinedAt: !2990)
!2990 = distinct !DILocation(line: 214, column: 41, scope: !2991)
!2991 = distinct !DILexicalBlock(scope: !2992, file: !3, line: 214, column: 18)
!2992 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 214, column: 9)
!2993 = !DILocation(line: 214, column: 70, scope: !2991)
!2994 = !DILocation(line: 0, scope: !99, inlinedAt: !2995)
!2995 = distinct !DILocation(line: 217, column: 38, scope: !2996)
!2996 = distinct !DILexicalBlock(scope: !2997, file: !3, line: 217, column: 19)
!2997 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 217, column: 9)
!2998 = !DILocation(line: 217, column: 67, scope: !2996)
!2999 = !DILocation(line: 0, scope: !99, inlinedAt: !3000)
!3000 = distinct !DILocation(line: 218, column: 38, scope: !3001)
!3001 = distinct !DILexicalBlock(scope: !3002, file: !3, line: 218, column: 19)
!3002 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 218, column: 9)
!3003 = !DILocation(line: 218, column: 67, scope: !3001)
!3004 = !DILocation(line: 0, scope: !99, inlinedAt: !3005)
!3005 = distinct !DILocation(line: 219, column: 40, scope: !3006)
!3006 = distinct !DILexicalBlock(scope: !3007, file: !3, line: 219, column: 19)
!3007 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 219, column: 9)
!3008 = !DILocation(line: 219, column: 69, scope: !3006)
!3009 = !DILocation(line: 0, scope: !99, inlinedAt: !3010)
!3010 = distinct !DILocation(line: 220, column: 40, scope: !3011)
!3011 = distinct !DILexicalBlock(scope: !3012, file: !3, line: 220, column: 19)
!3012 = distinct !DILexicalBlock(scope: !2946, file: !3, line: 220, column: 9)
!3013 = !DILocation(line: 220, column: 69, scope: !3011)
!3014 = !DILocation(line: 0, scope: !99, inlinedAt: !3015)
!3015 = distinct !DILocation(line: 221, column: 5, scope: !2946)
!3016 = !DILocation(line: 222, column: 1, scope: !2946)
!3017 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !2952)
!3018 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !2952)
!3019 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !2952)
!3020 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !2952)
!3021 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !2952)
!3022 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !2952)
!3023 = distinct !DISubprogram(name: "test_ternary", scope: !3, file: !3, line: 228, type: !142, scopeLine: 228, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3024)
!3024 = !{!3025, !3026, !3027, !3028, !3029}
!3025 = !DILocalVariable(name: "apdu", arg: 1, scope: !3023, file: !3, line: 228, type: !102)
!3026 = !DILocalVariable(name: "buffer", arg: 2, scope: !3023, file: !3, line: 228, type: !104)
!3027 = !DILocalVariable(name: "p1", arg: 3, scope: !3023, file: !3, line: 228, type: !5)
!3028 = !DILocalVariable(name: "a", scope: !3023, file: !3, line: 229, type: !8)
!3029 = !DILocalVariable(name: "b", scope: !3023, file: !3, line: 230, type: !8)
!3030 = !DILocation(line: 0, scope: !3023)
!3031 = !DILocation(line: 232, column: 9, scope: !3023)
!3032 = !DILocation(line: 0, scope: !99, inlinedAt: !3033)
!3033 = distinct !DILocation(line: 233, column: 20, scope: !3034)
!3034 = distinct !DILexicalBlock(scope: !3035, file: !3, line: 233, column: 18)
!3035 = distinct !DILexicalBlock(scope: !3023, file: !3, line: 233, column: 9)
!3036 = !DILocation(line: 233, column: 63, scope: !3034)
!3037 = !DILocation(line: 0, scope: !99, inlinedAt: !3038)
!3038 = distinct !DILocation(line: 234, column: 20, scope: !3039)
!3039 = distinct !DILexicalBlock(scope: !3040, file: !3, line: 234, column: 18)
!3040 = distinct !DILexicalBlock(scope: !3023, file: !3, line: 234, column: 9)
!3041 = !DILocation(line: 234, column: 65, scope: !3039)
!3042 = !DILocation(line: 0, scope: !99, inlinedAt: !3043)
!3043 = distinct !DILocation(line: 235, column: 20, scope: !3044)
!3044 = distinct !DILexicalBlock(scope: !3045, file: !3, line: 235, column: 18)
!3045 = distinct !DILexicalBlock(scope: !3023, file: !3, line: 235, column: 9)
!3046 = !DILocation(line: 235, column: 65, scope: !3044)
!3047 = !DILocation(line: 0, scope: !99, inlinedAt: !3048)
!3048 = distinct !DILocation(line: 236, column: 20, scope: !3049)
!3049 = distinct !DILexicalBlock(scope: !3050, file: !3, line: 236, column: 18)
!3050 = distinct !DILexicalBlock(scope: !3023, file: !3, line: 236, column: 9)
!3051 = !DILocation(line: 236, column: 80, scope: !3049)
!3052 = !DILocation(line: 0, scope: !99, inlinedAt: !3053)
!3053 = distinct !DILocation(line: 237, column: 5, scope: !3023)
!3054 = !DILocation(line: 238, column: 1, scope: !3023)
!3055 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3030)
!3056 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3030)
!3057 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3030)
!3058 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3030)
!3059 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3030)
!3060 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3030)
!3061 = distinct !DISubprogram(name: "test_casts", scope: !3, file: !3, line: 244, type: !142, scopeLine: 244, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3062)
!3062 = !{!3063, !3064, !3065, !3066, !3067, !3068}
!3063 = !DILocalVariable(name: "apdu", arg: 1, scope: !3061, file: !3, line: 244, type: !102)
!3064 = !DILocalVariable(name: "buffer", arg: 2, scope: !3061, file: !3, line: 244, type: !104)
!3065 = !DILocalVariable(name: "p1", arg: 3, scope: !3061, file: !3, line: 244, type: !5)
!3066 = !DILocalVariable(name: "i", scope: !3061, file: !3, line: 245, type: !20)
!3067 = !DILocalVariable(name: "s", scope: !3061, file: !3, line: 246, type: !8)
!3068 = !DILocalVariable(name: "b", scope: !3061, file: !3, line: 247, type: !5)
!3069 = !DILocation(line: 0, scope: !3061)
!3070 = !DILocation(line: 249, column: 9, scope: !3061)
!3071 = !DILocation(line: 0, scope: !99, inlinedAt: !3072)
!3072 = distinct !DILocation(line: 257, column: 9, scope: !3073)
!3073 = distinct !DILexicalBlock(scope: !3074, file: !3, line: 254, column: 18)
!3074 = distinct !DILexicalBlock(scope: !3061, file: !3, line: 254, column: 9)
!3075 = !DILocation(line: 258, column: 9, scope: !3073)
!3076 = !DILocation(line: 0, scope: !99, inlinedAt: !3077)
!3077 = distinct !DILocation(line: 263, column: 9, scope: !3078)
!3078 = distinct !DILexicalBlock(scope: !3079, file: !3, line: 260, column: 18)
!3079 = distinct !DILexicalBlock(scope: !3061, file: !3, line: 260, column: 9)
!3080 = !DILocation(line: 264, column: 9, scope: !3078)
!3081 = !DILocation(line: 0, scope: !99, inlinedAt: !3082)
!3082 = distinct !DILocation(line: 268, column: 9, scope: !3083)
!3083 = distinct !DILexicalBlock(scope: !3084, file: !3, line: 266, column: 18)
!3084 = distinct !DILexicalBlock(scope: !3061, file: !3, line: 266, column: 9)
!3085 = !DILocation(line: 269, column: 9, scope: !3083)
!3086 = !DILocation(line: 0, scope: !99, inlinedAt: !3087)
!3087 = distinct !DILocation(line: 271, column: 5, scope: !3061)
!3088 = !DILocation(line: 272, column: 1, scope: !3061)
!3089 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3069)
!3090 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3069)
!3091 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3069)
!3092 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3069)
!3093 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3069)
!3094 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3069)
!3095 = distinct !DISubprogram(name: "test_if_else", scope: !3, file: !3, line: 278, type: !142, scopeLine: 278, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3096)
!3096 = !{!3097, !3098, !3099, !3100}
!3097 = !DILocalVariable(name: "apdu", arg: 1, scope: !3095, file: !3, line: 278, type: !102)
!3098 = !DILocalVariable(name: "buffer", arg: 2, scope: !3095, file: !3, line: 278, type: !104)
!3099 = !DILocalVariable(name: "p1", arg: 3, scope: !3095, file: !3, line: 278, type: !5)
!3100 = !DILocalVariable(name: "x", scope: !3095, file: !3, line: 279, type: !8)
!3101 = !DILocation(line: 0, scope: !3095)
!3102 = !DILocation(line: 281, column: 9, scope: !3095)
!3103 = !DILocation(line: 0, scope: !99, inlinedAt: !3104)
!3104 = distinct !DILocation(line: 288, column: 9, scope: !3105)
!3105 = distinct !DILexicalBlock(scope: !3106, file: !3, line: 286, column: 18)
!3106 = distinct !DILexicalBlock(scope: !3095, file: !3, line: 286, column: 9)
!3107 = !DILocation(line: 289, column: 9, scope: !3105)
!3108 = !DILocation(line: 0, scope: !99, inlinedAt: !3109)
!3109 = distinct !DILocation(line: 292, column: 23, scope: !3110)
!3110 = distinct !DILexicalBlock(scope: !3111, file: !3, line: 292, column: 21)
!3111 = distinct !DILexicalBlock(scope: !3112, file: !3, line: 292, column: 13)
!3112 = distinct !DILexicalBlock(scope: !3113, file: !3, line: 291, column: 18)
!3113 = distinct !DILexicalBlock(scope: !3095, file: !3, line: 291, column: 9)
!3114 = !DILocation(line: 293, column: 9, scope: !3112)
!3115 = !DILocation(line: 0, scope: !99, inlinedAt: !3116)
!3116 = distinct !DILocation(line: 296, column: 63, scope: !3117)
!3117 = distinct !DILexicalBlock(scope: !3118, file: !3, line: 296, column: 61)
!3118 = distinct !DILexicalBlock(scope: !3119, file: !3, line: 296, column: 13)
!3119 = distinct !DILexicalBlock(scope: !3120, file: !3, line: 295, column: 18)
!3120 = distinct !DILexicalBlock(scope: !3095, file: !3, line: 295, column: 9)
!3121 = !DILocation(line: 297, column: 9, scope: !3119)
!3122 = !DILocation(line: 0, scope: !99, inlinedAt: !3123)
!3123 = distinct !DILocation(line: 301, column: 26, scope: !3124)
!3124 = distinct !DILexicalBlock(scope: !3125, file: !3, line: 301, column: 24)
!3125 = distinct !DILexicalBlock(scope: !3126, file: !3, line: 301, column: 17)
!3126 = distinct !DILexicalBlock(scope: !3127, file: !3, line: 300, column: 20)
!3127 = distinct !DILexicalBlock(scope: !3128, file: !3, line: 300, column: 13)
!3128 = distinct !DILexicalBlock(scope: !3129, file: !3, line: 299, column: 18)
!3129 = distinct !DILexicalBlock(scope: !3095, file: !3, line: 299, column: 9)
!3130 = !DILocation(line: 301, column: 56, scope: !3124)
!3131 = !DILocation(line: 0, scope: !99, inlinedAt: !3132)
!3132 = distinct !DILocation(line: 308, column: 5, scope: !3095)
!3133 = !DILocation(line: 309, column: 1, scope: !3095)
!3134 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3101)
!3135 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3101)
!3136 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3101)
!3137 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3101)
!3138 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3101)
!3139 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3101)
!3140 = distinct !DISubprogram(name: "test_loops", scope: !3, file: !3, line: 317, type: !142, scopeLine: 317, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3141)
!3141 = !{!3142, !3143, !3144, !3145, !3146}
!3142 = !DILocalVariable(name: "apdu", arg: 1, scope: !3140, file: !3, line: 317, type: !102)
!3143 = !DILocalVariable(name: "buffer", arg: 2, scope: !3140, file: !3, line: 317, type: !104)
!3144 = !DILocalVariable(name: "p1", arg: 3, scope: !3140, file: !3, line: 317, type: !5)
!3145 = !DILocalVariable(name: "sum", scope: !3140, file: !3, line: 318, type: !8)
!3146 = !DILocalVariable(name: "i", scope: !3140, file: !3, line: 319, type: !8)
!3147 = !DILocation(line: 0, scope: !3140)
!3148 = !DILocation(line: 321, column: 9, scope: !3140)
!3149 = !DILocation(line: 0, scope: !99, inlinedAt: !3150)
!3150 = distinct !DILocation(line: 346, column: 9, scope: !3151)
!3151 = distinct !DILexicalBlock(scope: !3152, file: !3, line: 339, column: 18)
!3152 = distinct !DILexicalBlock(scope: !3140, file: !3, line: 339, column: 9)
!3153 = !DILocation(line: 347, column: 9, scope: !3151)
!3154 = !DILocation(line: 0, scope: !99, inlinedAt: !3155)
!3155 = distinct !DILocation(line: 356, column: 9, scope: !3156)
!3156 = distinct !DILexicalBlock(scope: !3157, file: !3, line: 349, column: 18)
!3157 = distinct !DILexicalBlock(scope: !3140, file: !3, line: 349, column: 9)
!3158 = !DILocation(line: 357, column: 9, scope: !3156)
!3159 = !DILocation(line: 0, scope: !99, inlinedAt: !3160)
!3160 = distinct !DILocation(line: 359, column: 5, scope: !3140)
!3161 = !DILocation(line: 360, column: 1, scope: !3140)
!3162 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3147)
!3163 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3147)
!3164 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3147)
!3165 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3147)
!3166 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3147)
!3167 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3147)
!3168 = distinct !DISubprogram(name: "test_globals", scope: !3, file: !3, line: 366, type: !142, scopeLine: 366, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3169)
!3169 = !{!3170, !3171, !3172}
!3170 = !DILocalVariable(name: "apdu", arg: 1, scope: !3168, file: !3, line: 366, type: !102)
!3171 = !DILocalVariable(name: "buffer", arg: 2, scope: !3168, file: !3, line: 366, type: !104)
!3172 = !DILocalVariable(name: "p1", arg: 3, scope: !3168, file: !3, line: 366, type: !5)
!3173 = !DILocation(line: 0, scope: !3168)
!3174 = !DILocation(line: 367, column: 9, scope: !3168)
!3175 = !DILocation(line: 368, column: 16, scope: !3176)
!3176 = distinct !DILexicalBlock(scope: !3177, file: !3, line: 367, column: 18)
!3177 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 367, column: 9)
!3178 = !DILocation(line: 0, scope: !99, inlinedAt: !3179)
!3179 = distinct !DILocation(line: 369, column: 9, scope: !3176)
!3180 = !DILocation(line: 370, column: 9, scope: !3176)
!3181 = !DILocation(line: 373, column: 17, scope: !3182)
!3182 = distinct !DILexicalBlock(scope: !3183, file: !3, line: 372, column: 18)
!3183 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 372, column: 9)
!3184 = !{!666, !666, i64 0}
!3185 = !DILocation(line: 0, scope: !99, inlinedAt: !3186)
!3186 = distinct !DILocation(line: 374, column: 9, scope: !3182)
!3187 = !DILocation(line: 375, column: 9, scope: !3182)
!3188 = !DILocation(line: 378, column: 15, scope: !3189)
!3189 = distinct !DILexicalBlock(scope: !3190, file: !3, line: 377, column: 18)
!3190 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 377, column: 9)
!3191 = !{!3192, !3192, i64 0}
!3192 = !{!"int", !114, i64 0}
!3193 = !DILocation(line: 0, scope: !99, inlinedAt: !3194)
!3194 = distinct !DILocation(line: 379, column: 9, scope: !3189)
!3195 = !DILocation(line: 380, column: 9, scope: !3189)
!3196 = !DILocation(line: 384, column: 17, scope: !3197)
!3197 = distinct !DILexicalBlock(scope: !3198, file: !3, line: 382, column: 18)
!3198 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 382, column: 9)
!3199 = !DILocation(line: 0, scope: !99, inlinedAt: !3200)
!3200 = distinct !DILocation(line: 385, column: 9, scope: !3197)
!3201 = !DILocation(line: 386, column: 9, scope: !3197)
!3202 = !DILocation(line: 389, column: 16, scope: !3203)
!3203 = distinct !DILexicalBlock(scope: !3204, file: !3, line: 388, column: 18)
!3204 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 388, column: 9)
!3205 = !DILocation(line: 390, column: 17, scope: !3203)
!3206 = !DILocation(line: 0, scope: !99, inlinedAt: !3207)
!3207 = distinct !DILocation(line: 391, column: 9, scope: !3203)
!3208 = !DILocation(line: 392, column: 9, scope: !3203)
!3209 = !DILocation(line: 396, column: 34, scope: !3210)
!3210 = distinct !DILexicalBlock(scope: !3211, file: !3, line: 394, column: 18)
!3211 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 394, column: 9)
!3212 = !DILocation(line: 0, scope: !99, inlinedAt: !3213)
!3213 = distinct !DILocation(line: 396, column: 9, scope: !3210)
!3214 = !DILocation(line: 397, column: 9, scope: !3210)
!3215 = !DILocation(line: 401, column: 41, scope: !3216)
!3216 = distinct !DILexicalBlock(scope: !3217, file: !3, line: 399, column: 18)
!3217 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 399, column: 9)
!3218 = !DILocation(line: 0, scope: !99, inlinedAt: !3219)
!3219 = distinct !DILocation(line: 401, column: 9, scope: !3216)
!3220 = !DILocation(line: 402, column: 9, scope: !3216)
!3221 = !DILocation(line: 406, column: 16, scope: !3222)
!3222 = distinct !DILexicalBlock(scope: !3223, file: !3, line: 404, column: 18)
!3223 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 404, column: 9)
!3224 = !DILocation(line: 0, scope: !99, inlinedAt: !3225)
!3225 = distinct !DILocation(line: 407, column: 9, scope: !3222)
!3226 = !DILocation(line: 408, column: 9, scope: !3222)
!3227 = !DILocation(line: 412, column: 34, scope: !3228)
!3228 = distinct !DILexicalBlock(scope: !3229, file: !3, line: 410, column: 18)
!3229 = distinct !DILexicalBlock(scope: !3168, file: !3, line: 410, column: 9)
!3230 = !DILocation(line: 0, scope: !99, inlinedAt: !3231)
!3231 = distinct !DILocation(line: 412, column: 9, scope: !3228)
!3232 = !DILocation(line: 413, column: 9, scope: !3228)
!3233 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3173)
!3234 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3173)
!3235 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3173)
!3236 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3173)
!3237 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3173)
!3238 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3173)
!3239 = !DILocation(line: 416, column: 1, scope: !3168)
!3240 = distinct !DISubprogram(name: "test_arrays", scope: !3, file: !3, line: 422, type: !142, scopeLine: 422, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3241)
!3241 = !{!3242, !3243, !3244, !3245}
!3242 = !DILocalVariable(name: "apdu", arg: 1, scope: !3240, file: !3, line: 422, type: !102)
!3243 = !DILocalVariable(name: "buffer", arg: 2, scope: !3240, file: !3, line: 422, type: !104)
!3244 = !DILocalVariable(name: "p1", arg: 3, scope: !3240, file: !3, line: 422, type: !5)
!3245 = !DILocalVariable(name: "i", scope: !3240, file: !3, line: 423, type: !8)
!3246 = !DILocation(line: 0, scope: !3240)
!3247 = !DILocation(line: 425, column: 9, scope: !3240)
!3248 = !DILocation(line: 426, column: 20, scope: !3249)
!3249 = distinct !DILexicalBlock(scope: !3250, file: !3, line: 425, column: 18)
!3250 = distinct !DILexicalBlock(scope: !3240, file: !3, line: 425, column: 9)
!3251 = !DILocation(line: 427, column: 20, scope: !3249)
!3252 = !DILocation(line: 0, scope: !99, inlinedAt: !3253)
!3253 = distinct !DILocation(line: 428, column: 9, scope: !3249)
!3254 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3253)
!3255 = !DILocation(line: 429, column: 9, scope: !3249)
!3256 = !DILocation(line: 432, column: 21, scope: !3257)
!3257 = distinct !DILexicalBlock(scope: !3258, file: !3, line: 431, column: 18)
!3258 = distinct !DILexicalBlock(scope: !3240, file: !3, line: 431, column: 9)
!3259 = !DILocation(line: 433, column: 21, scope: !3257)
!3260 = !DILocation(line: 0, scope: !99, inlinedAt: !3261)
!3261 = distinct !DILocation(line: 434, column: 9, scope: !3257)
!3262 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3261)
!3263 = !DILocation(line: 435, column: 9, scope: !3257)
!3264 = !DILocation(line: 439, column: 21, scope: !3265)
!3265 = distinct !DILexicalBlock(scope: !3266, file: !3, line: 437, column: 18)
!3266 = distinct !DILexicalBlock(scope: !3240, file: !3, line: 437, column: 9)
!3267 = !DILocation(line: 0, scope: !99, inlinedAt: !3268)
!3268 = distinct !DILocation(line: 440, column: 9, scope: !3265)
!3269 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3268)
!3270 = !DILocation(line: 441, column: 9, scope: !3265)
!3271 = !DILocation(line: 445, column: 21, scope: !3272)
!3272 = distinct !DILexicalBlock(scope: !3273, file: !3, line: 443, column: 18)
!3273 = distinct !DILexicalBlock(scope: !3240, file: !3, line: 443, column: 9)
!3274 = !DILocation(line: 0, scope: !99, inlinedAt: !3275)
!3275 = distinct !DILocation(line: 446, column: 9, scope: !3272)
!3276 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3275)
!3277 = !DILocation(line: 447, column: 9, scope: !3272)
!3278 = !DILocation(line: 450, column: 20, scope: !3279)
!3279 = distinct !DILexicalBlock(scope: !3280, file: !3, line: 449, column: 18)
!3280 = distinct !DILexicalBlock(scope: !3240, file: !3, line: 449, column: 9)
!3281 = !DILocation(line: 451, column: 20, scope: !3279)
!3282 = !DILocation(line: 452, column: 20, scope: !3279)
!3283 = !DILocation(line: 453, column: 20, scope: !3279)
!3284 = !DILocation(line: 454, column: 17, scope: !3279)
!3285 = !DILocation(line: 455, column: 9, scope: !3286)
!3286 = distinct !DILexicalBlock(scope: !3279, file: !3, line: 455, column: 9)
!3287 = !DILocation(line: 456, column: 33, scope: !3288)
!3288 = distinct !DILexicalBlock(scope: !3289, file: !3, line: 455, column: 39)
!3289 = distinct !DILexicalBlock(scope: !3286, file: !3, line: 455, column: 9)
!3290 = !DILocation(line: 456, column: 31, scope: !3288)
!3291 = !DILocation(line: 455, column: 21, scope: !3289)
!3292 = !DILocation(line: 455, column: 23, scope: !3289)
!3293 = distinct !{!3293, !3285, !3294, !312, !313}
!3294 = !DILocation(line: 457, column: 9, scope: !3286)
!3295 = !DILocation(line: 456, column: 21, scope: !3288)
!3296 = !DILocation(line: 0, scope: !99, inlinedAt: !3297)
!3297 = distinct !DILocation(line: 458, column: 9, scope: !3279)
!3298 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !3297)
!3299 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !3297)
!3300 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3297)
!3301 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !3297)
!3302 = !DILocation(line: 459, column: 9, scope: !3279)
!3303 = !DILocation(line: 0, scope: !99, inlinedAt: !3304)
!3304 = distinct !DILocation(line: 461, column: 5, scope: !3240)
!3305 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3304)
!3306 = !DILocation(line: 462, column: 1, scope: !3240)
!3307 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3246)
!3308 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3246)
!3309 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3246)
!3310 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3246)
!3311 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3246)
!3312 = distinct !DISubprogram(name: "test_structs", scope: !3, file: !3, line: 468, type: !142, scopeLine: 468, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3313)
!3313 = !{!3314, !3315, !3316}
!3314 = !DILocalVariable(name: "apdu", arg: 1, scope: !3312, file: !3, line: 468, type: !102)
!3315 = !DILocalVariable(name: "buffer", arg: 2, scope: !3312, file: !3, line: 468, type: !104)
!3316 = !DILocalVariable(name: "p1", arg: 3, scope: !3312, file: !3, line: 468, type: !5)
!3317 = !DILocation(line: 0, scope: !3312)
!3318 = !DILocation(line: 469, column: 9, scope: !3312)
!3319 = !DILocation(line: 470, column: 24, scope: !3320)
!3320 = distinct !DILexicalBlock(scope: !3321, file: !3, line: 469, column: 18)
!3321 = distinct !DILexicalBlock(scope: !3312, file: !3, line: 469, column: 9)
!3322 = !{!3323, !666, i64 0}
!3323 = !{!"Item", !666, i64 0, !114, i64 2}
!3324 = !DILocation(line: 0, scope: !99, inlinedAt: !3325)
!3325 = distinct !DILocation(line: 471, column: 9, scope: !3320)
!3326 = !DILocation(line: 472, column: 9, scope: !3320)
!3327 = !DILocation(line: 475, column: 24, scope: !3328)
!3328 = distinct !DILexicalBlock(scope: !3329, file: !3, line: 474, column: 18)
!3329 = distinct !DILexicalBlock(scope: !3312, file: !3, line: 474, column: 9)
!3330 = !DILocation(line: 476, column: 23, scope: !3328)
!3331 = !{!3323, !114, i64 2}
!3332 = !DILocation(line: 0, scope: !99, inlinedAt: !3333)
!3333 = distinct !DILocation(line: 477, column: 9, scope: !3328)
!3334 = !DILocation(line: 478, column: 9, scope: !3328)
!3335 = !DILocation(line: 481, column: 24, scope: !3336)
!3336 = distinct !DILexicalBlock(scope: !3337, file: !3, line: 480, column: 18)
!3337 = distinct !DILexicalBlock(scope: !3312, file: !3, line: 480, column: 9)
!3338 = !DILocation(line: 482, column: 24, scope: !3336)
!3339 = !DILocation(line: 483, column: 24, scope: !3336)
!3340 = !DILocation(line: 0, scope: !99, inlinedAt: !3341)
!3341 = distinct !DILocation(line: 484, column: 9, scope: !3336)
!3342 = !DILocation(line: 485, column: 9, scope: !3336)
!3343 = !DILocation(line: 489, column: 24, scope: !3344)
!3344 = distinct !DILexicalBlock(scope: !3345, file: !3, line: 487, column: 18)
!3345 = distinct !DILexicalBlock(scope: !3312, file: !3, line: 487, column: 9)
!3346 = !DILocation(line: 0, scope: !99, inlinedAt: !3347)
!3347 = distinct !DILocation(line: 490, column: 9, scope: !3344)
!3348 = !DILocation(line: 491, column: 9, scope: !3344)
!3349 = !DILocation(line: 494, column: 17, scope: !3350)
!3350 = distinct !DILexicalBlock(scope: !3351, file: !3, line: 493, column: 18)
!3351 = distinct !DILexicalBlock(scope: !3312, file: !3, line: 493, column: 9)
!3352 = !DILocation(line: 495, column: 30, scope: !3350)
!3353 = !DILocation(line: 0, scope: !99, inlinedAt: !3354)
!3354 = distinct !DILocation(line: 496, column: 9, scope: !3350)
!3355 = !DILocation(line: 497, column: 9, scope: !3350)
!3356 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3317)
!3357 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3317)
!3358 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3317)
!3359 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3317)
!3360 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3317)
!3361 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3317)
!3362 = !DILocation(line: 500, column: 1, scope: !3312)
!3363 = distinct !DISubprogram(name: "multiply", scope: !3, file: !3, line: 506, type: !133, scopeLine: 506, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3364)
!3364 = !{!3365, !3366}
!3365 = !DILocalVariable(name: "a", arg: 1, scope: !3363, file: !3, line: 506, type: !8)
!3366 = !DILocalVariable(name: "b", arg: 2, scope: !3363, file: !3, line: 506, type: !8)
!3367 = !DILocation(line: 0, scope: !3363)
!3368 = !DILocation(line: 507, column: 14, scope: !3363)
!3369 = !DILocation(line: 507, column: 5, scope: !3363)
!3370 = distinct !DISubprogram(name: "factorial", scope: !3, file: !3, line: 510, type: !3371, scopeLine: 510, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3373)
!3371 = !DISubroutineType(types: !3372)
!3372 = !{!8, !8}
!3373 = !{!3374, !3375}
!3374 = !DILocalVariable(name: "n", arg: 1, scope: !3370, file: !3, line: 510, type: !8)
!3375 = !DILocalVariable(name: "result", scope: !3370, file: !3, line: 511, type: !8)
!3376 = !DILocation(line: 0, scope: !3370)
!3377 = !DILocation(line: 512, column: 14, scope: !3370)
!3378 = !DILocation(line: 512, column: 5, scope: !3370)
!3379 = !DILocation(line: 513, column: 25, scope: !3380)
!3380 = distinct !DILexicalBlock(scope: !3370, file: !3, line: 512, column: 19)
!3381 = !DILocation(line: 514, column: 15, scope: !3380)
!3382 = distinct !{!3382, !3378, !3383, !312, !313}
!3383 = !DILocation(line: 515, column: 5, scope: !3370)
!3384 = !DILocation(line: 516, column: 5, scope: !3370)
!3385 = distinct !DISubprogram(name: "test_functions", scope: !3, file: !3, line: 519, type: !142, scopeLine: 519, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3386)
!3386 = !{!3387, !3388, !3389}
!3387 = !DILocalVariable(name: "apdu", arg: 1, scope: !3385, file: !3, line: 519, type: !102)
!3388 = !DILocalVariable(name: "buffer", arg: 2, scope: !3385, file: !3, line: 519, type: !104)
!3389 = !DILocalVariable(name: "p1", arg: 3, scope: !3385, file: !3, line: 519, type: !5)
!3390 = !DILocation(line: 0, scope: !3385)
!3391 = !DILocation(line: 520, column: 9, scope: !3385)
!3392 = !DILocation(line: 0, scope: !99, inlinedAt: !3393)
!3393 = distinct !DILocation(line: 525, column: 9, scope: !3394)
!3394 = distinct !DILexicalBlock(scope: !3395, file: !3, line: 524, column: 18)
!3395 = distinct !DILexicalBlock(scope: !3385, file: !3, line: 524, column: 9)
!3396 = !DILocation(line: 526, column: 9, scope: !3394)
!3397 = !DILocation(line: 0, scope: !99, inlinedAt: !3398)
!3398 = distinct !DILocation(line: 529, column: 9, scope: !3399)
!3399 = distinct !DILexicalBlock(scope: !3400, file: !3, line: 528, column: 18)
!3400 = distinct !DILexicalBlock(scope: !3385, file: !3, line: 528, column: 9)
!3401 = !DILocation(line: 530, column: 9, scope: !3399)
!3402 = !DILocation(line: 0, scope: !99, inlinedAt: !3403)
!3403 = distinct !DILocation(line: 533, column: 9, scope: !3404)
!3404 = distinct !DILexicalBlock(scope: !3405, file: !3, line: 532, column: 18)
!3405 = distinct !DILexicalBlock(scope: !3385, file: !3, line: 532, column: 9)
!3406 = !DILocation(line: 534, column: 9, scope: !3404)
!3407 = !DILocation(line: 0, scope: !3370, inlinedAt: !3408)
!3408 = distinct !DILocation(line: 537, column: 34, scope: !3409)
!3409 = distinct !DILexicalBlock(scope: !3410, file: !3, line: 536, column: 18)
!3410 = distinct !DILexicalBlock(scope: !3385, file: !3, line: 536, column: 9)
!3411 = !DILocation(line: 0, scope: !99, inlinedAt: !3412)
!3412 = distinct !DILocation(line: 537, column: 9, scope: !3409)
!3413 = !DILocation(line: 538, column: 9, scope: !3409)
!3414 = !DILocation(line: 0, scope: !99, inlinedAt: !3415)
!3415 = distinct !DILocation(line: 540, column: 5, scope: !3385)
!3416 = !DILocation(line: 541, column: 1, scope: !3385)
!3417 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3390)
!3418 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3390)
!3419 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3390)
!3420 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3390)
!3421 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3390)
!3422 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3390)
!3423 = distinct !DISubprogram(name: "test_apdu", scope: !3, file: !3, line: 547, type: !3424, scopeLine: 547, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3426)
!3424 = !DISubroutineType(types: !3425)
!3425 = !{null, !102, !104, !5, !8}
!3426 = !{!3427, !3428, !3429, !3430}
!3427 = !DILocalVariable(name: "apdu", arg: 1, scope: !3423, file: !3, line: 547, type: !102)
!3428 = !DILocalVariable(name: "buffer", arg: 2, scope: !3423, file: !3, line: 547, type: !104)
!3429 = !DILocalVariable(name: "p1", arg: 3, scope: !3423, file: !3, line: 547, type: !5)
!3430 = !DILocalVariable(name: "len", arg: 4, scope: !3423, file: !3, line: 547, type: !8)
!3431 = !DILocation(line: 0, scope: !3423)
!3432 = !DILocation(line: 548, column: 9, scope: !3423)
!3433 = !DILocation(line: 549, column: 34, scope: !3434)
!3434 = distinct !DILexicalBlock(scope: !3435, file: !3, line: 548, column: 18)
!3435 = distinct !DILexicalBlock(scope: !3423, file: !3, line: 548, column: 9)
!3436 = !DILocation(line: 0, scope: !99, inlinedAt: !3437)
!3437 = distinct !DILocation(line: 549, column: 9, scope: !3434)
!3438 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !3437)
!3439 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3437)
!3440 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3437)
!3441 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3437)
!3442 = !DILocation(line: 550, column: 9, scope: !3434)
!3443 = !DILocation(line: 553, column: 34, scope: !3444)
!3444 = distinct !DILexicalBlock(scope: !3445, file: !3, line: 552, column: 18)
!3445 = distinct !DILexicalBlock(scope: !3423, file: !3, line: 552, column: 9)
!3446 = !DILocation(line: 0, scope: !99, inlinedAt: !3447)
!3447 = distinct !DILocation(line: 553, column: 9, scope: !3444)
!3448 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !3447)
!3449 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3447)
!3450 = !DILocation(line: 554, column: 9, scope: !3444)
!3451 = !DILocation(line: 557, column: 9, scope: !3452)
!3452 = distinct !DILexicalBlock(scope: !3453, file: !3, line: 556, column: 18)
!3453 = distinct !DILexicalBlock(scope: !3423, file: !3, line: 556, column: 9)
!3454 = !DILocation(line: 557, column: 19, scope: !3452)
!3455 = !DILocation(line: 0, scope: !99, inlinedAt: !3456)
!3456 = distinct !DILocation(line: 558, column: 9, scope: !3452)
!3457 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3456)
!3458 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3456)
!3459 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3456)
!3460 = !DILocation(line: 559, column: 9, scope: !3452)
!3461 = !DILocation(line: 0, scope: !99, inlinedAt: !3462)
!3462 = distinct !DILocation(line: 562, column: 9, scope: !3463)
!3463 = distinct !DILexicalBlock(scope: !3464, file: !3, line: 561, column: 18)
!3464 = distinct !DILexicalBlock(scope: !3423, file: !3, line: 561, column: 9)
!3465 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !3462)
!3466 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !3462)
!3467 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3462)
!3468 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !3462)
!3469 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3462)
!3470 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3462)
!3471 = !DILocation(line: 563, column: 9, scope: !3463)
!3472 = !DILocation(line: 0, scope: !99, inlinedAt: !3473)
!3473 = distinct !DILocation(line: 565, column: 5, scope: !3423)
!3474 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3473)
!3475 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3473)
!3476 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3473)
!3477 = !DILocation(line: 566, column: 1, scope: !3423)
!3478 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3431)
!3479 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3431)
!3480 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3431)
!3481 = distinct !DISubprogram(name: "test_int_ops", scope: !3, file: !3, line: 572, type: !142, scopeLine: 572, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3482)
!3482 = !{!3483, !3484, !3485, !3486, !3487, !3488}
!3483 = !DILocalVariable(name: "apdu", arg: 1, scope: !3481, file: !3, line: 572, type: !102)
!3484 = !DILocalVariable(name: "buffer", arg: 2, scope: !3481, file: !3, line: 572, type: !104)
!3485 = !DILocalVariable(name: "p1", arg: 3, scope: !3481, file: !3, line: 572, type: !5)
!3486 = !DILocalVariable(name: "a", scope: !3481, file: !3, line: 573, type: !20)
!3487 = !DILocalVariable(name: "b", scope: !3481, file: !3, line: 574, type: !20)
!3488 = !DILocalVariable(name: "r", scope: !3481, file: !3, line: 575, type: !20)
!3489 = !DILocation(line: 0, scope: !3481)
!3490 = !DILocation(line: 577, column: 9, scope: !3481)
!3491 = !DILocation(line: 0, scope: !99, inlinedAt: !3492)
!3492 = distinct !DILocation(line: 584, column: 9, scope: !3493)
!3493 = distinct !DILexicalBlock(scope: !3494, file: !3, line: 582, column: 18)
!3494 = distinct !DILexicalBlock(scope: !3481, file: !3, line: 582, column: 9)
!3495 = !DILocation(line: 585, column: 9, scope: !3493)
!3496 = !DILocation(line: 0, scope: !99, inlinedAt: !3497)
!3497 = distinct !DILocation(line: 589, column: 9, scope: !3498)
!3498 = distinct !DILexicalBlock(scope: !3499, file: !3, line: 587, column: 18)
!3499 = distinct !DILexicalBlock(scope: !3481, file: !3, line: 587, column: 9)
!3500 = !DILocation(line: 590, column: 9, scope: !3498)
!3501 = !DILocation(line: 0, scope: !99, inlinedAt: !3502)
!3502 = distinct !DILocation(line: 594, column: 9, scope: !3503)
!3503 = distinct !DILexicalBlock(scope: !3504, file: !3, line: 592, column: 18)
!3504 = distinct !DILexicalBlock(scope: !3481, file: !3, line: 592, column: 9)
!3505 = !DILocation(line: 595, column: 9, scope: !3503)
!3506 = !DILocation(line: 598, column: 17, scope: !3507)
!3507 = distinct !DILexicalBlock(scope: !3508, file: !3, line: 597, column: 18)
!3508 = distinct !DILexicalBlock(scope: !3481, file: !3, line: 597, column: 9)
!3509 = !DILocation(line: 0, scope: !99, inlinedAt: !3510)
!3510 = distinct !DILocation(line: 600, column: 9, scope: !3507)
!3511 = !DILocation(line: 601, column: 9, scope: !3507)
!3512 = !DILocation(line: 0, scope: !99, inlinedAt: !3513)
!3513 = distinct !DILocation(line: 603, column: 5, scope: !3481)
!3514 = !DILocation(line: 604, column: 1, scope: !3481)
!3515 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3489)
!3516 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3489)
!3517 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3489)
!3518 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3489)
!3519 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3489)
!3520 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3489)
!3521 = distinct !DISubprogram(name: "test_lshr", scope: !3, file: !3, line: 610, type: !142, scopeLine: 610, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3522)
!3522 = !{!3523, !3524, !3525, !3526}
!3523 = !DILocalVariable(name: "apdu", arg: 1, scope: !3521, file: !3, line: 610, type: !102)
!3524 = !DILocalVariable(name: "buffer", arg: 2, scope: !3521, file: !3, line: 610, type: !104)
!3525 = !DILocalVariable(name: "p1", arg: 3, scope: !3521, file: !3, line: 610, type: !5)
!3526 = !DILocalVariable(name: "i", scope: !3521, file: !3, line: 611, type: !20)
!3527 = !DILocation(line: 0, scope: !3521)
!3528 = !DILocation(line: 613, column: 9, scope: !3521)
!3529 = !DILocation(line: 615, column: 42, scope: !3530)
!3530 = distinct !DILexicalBlock(scope: !3531, file: !3, line: 613, column: 18)
!3531 = distinct !DILexicalBlock(scope: !3521, file: !3, line: 613, column: 9)
!3532 = !DILocation(line: 615, column: 57, scope: !3530)
!3533 = !DILocation(line: 0, scope: !99, inlinedAt: !3534)
!3534 = distinct !DILocation(line: 615, column: 9, scope: !3530)
!3535 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !3534)
!3536 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3534)
!3537 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !3534)
!3538 = !DILocation(line: 616, column: 9, scope: !3530)
!3539 = !DILocation(line: 620, column: 41, scope: !3540)
!3540 = distinct !DILexicalBlock(scope: !3541, file: !3, line: 618, column: 18)
!3541 = distinct !DILexicalBlock(scope: !3521, file: !3, line: 618, column: 9)
!3542 = !DILocation(line: 0, scope: !99, inlinedAt: !3543)
!3543 = distinct !DILocation(line: 620, column: 9, scope: !3540)
!3544 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !3543)
!3545 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3543)
!3546 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !3543)
!3547 = !DILocation(line: 621, column: 9, scope: !3540)
!3548 = !DILocation(line: 0, scope: !99, inlinedAt: !3549)
!3549 = distinct !DILocation(line: 623, column: 5, scope: !3521)
!3550 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3549)
!3551 = !DILocation(line: 624, column: 1, scope: !3521)
!3552 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3527)
!3553 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3527)
!3554 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3527)
!3555 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3527)
!3556 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3527)
!3557 = !DISubprogram(name: "lshr_int", scope: !6, file: !6, line: 150, type: !3558, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!3558 = !DISubroutineType(types: !3559)
!3559 = !{!20, !20, !20}
!3560 = distinct !DISubprogram(name: "test_hex_literals", scope: !3, file: !3, line: 630, type: !142, scopeLine: 630, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3561)
!3561 = !{!3562, !3563, !3564, !3565, !3566}
!3562 = !DILocalVariable(name: "apdu", arg: 1, scope: !3560, file: !3, line: 630, type: !102)
!3563 = !DILocalVariable(name: "buffer", arg: 2, scope: !3560, file: !3, line: 630, type: !104)
!3564 = !DILocalVariable(name: "p1", arg: 3, scope: !3560, file: !3, line: 630, type: !5)
!3565 = !DILocalVariable(name: "i", scope: !3560, file: !3, line: 631, type: !20)
!3566 = !DILocalVariable(name: "zero", scope: !3560, file: !3, line: 632, type: !20)
!3567 = !DILocation(line: 0, scope: !3560)
!3568 = !DILocation(line: 634, column: 9, scope: !3560)
!3569 = !DILocation(line: 0, scope: !99, inlinedAt: !3570)
!3570 = distinct !DILocation(line: 641, column: 9, scope: !3571)
!3571 = distinct !DILexicalBlock(scope: !3572, file: !3, line: 639, column: 18)
!3572 = distinct !DILexicalBlock(scope: !3560, file: !3, line: 639, column: 9)
!3573 = !DILocation(line: 642, column: 9, scope: !3571)
!3574 = !DILocation(line: 0, scope: !99, inlinedAt: !3575)
!3575 = distinct !DILocation(line: 660, column: 5, scope: !3560)
!3576 = !DILocation(line: 661, column: 1, scope: !3560)
!3577 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3567)
!3578 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3567)
!3579 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3567)
!3580 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3567)
!3581 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3567)
!3582 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3567)
!3583 = distinct !DISubprogram(name: "test_int_comparison", scope: !3, file: !3, line: 667, type: !142, scopeLine: 667, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3584)
!3584 = !{!3585, !3586, !3587, !3588, !3589}
!3585 = !DILocalVariable(name: "apdu", arg: 1, scope: !3583, file: !3, line: 667, type: !102)
!3586 = !DILocalVariable(name: "buffer", arg: 2, scope: !3583, file: !3, line: 667, type: !104)
!3587 = !DILocalVariable(name: "p1", arg: 3, scope: !3583, file: !3, line: 667, type: !5)
!3588 = !DILocalVariable(name: "big", scope: !3583, file: !3, line: 668, type: !20)
!3589 = !DILocalVariable(name: "zero", scope: !3583, file: !3, line: 669, type: !20)
!3590 = !DILocation(line: 0, scope: !3583)
!3591 = !DILocation(line: 673, column: 9, scope: !3583)
!3592 = !DILocation(line: 0, scope: !99, inlinedAt: !3593)
!3593 = distinct !DILocation(line: 675, column: 20, scope: !3594)
!3594 = distinct !DILexicalBlock(scope: !3595, file: !3, line: 675, column: 18)
!3595 = distinct !DILexicalBlock(scope: !3583, file: !3, line: 675, column: 9)
!3596 = !DILocation(line: 675, column: 68, scope: !3594)
!3597 = !DILocation(line: 0, scope: !99, inlinedAt: !3598)
!3598 = distinct !DILocation(line: 676, column: 20, scope: !3599)
!3599 = distinct !DILexicalBlock(scope: !3600, file: !3, line: 676, column: 18)
!3600 = distinct !DILexicalBlock(scope: !3583, file: !3, line: 676, column: 9)
!3601 = !DILocation(line: 676, column: 69, scope: !3599)
!3602 = !DILocation(line: 0, scope: !99, inlinedAt: !3603)
!3603 = distinct !DILocation(line: 677, column: 20, scope: !3604)
!3604 = distinct !DILexicalBlock(scope: !3605, file: !3, line: 677, column: 18)
!3605 = distinct !DILexicalBlock(scope: !3583, file: !3, line: 677, column: 9)
!3606 = !DILocation(line: 677, column: 69, scope: !3604)
!3607 = !DILocation(line: 0, scope: !99, inlinedAt: !3608)
!3608 = distinct !DILocation(line: 684, column: 20, scope: !3609)
!3609 = distinct !DILexicalBlock(scope: !3610, file: !3, line: 684, column: 18)
!3610 = distinct !DILexicalBlock(scope: !3583, file: !3, line: 684, column: 9)
!3611 = !DILocation(line: 684, column: 68, scope: !3609)
!3612 = !DILocation(line: 0, scope: !99, inlinedAt: !3613)
!3613 = distinct !DILocation(line: 685, column: 20, scope: !3614)
!3614 = distinct !DILexicalBlock(scope: !3615, file: !3, line: 685, column: 18)
!3615 = distinct !DILexicalBlock(scope: !3583, file: !3, line: 685, column: 9)
!3616 = !DILocation(line: 685, column: 69, scope: !3614)
!3617 = !DILocation(line: 0, scope: !99, inlinedAt: !3618)
!3618 = distinct !DILocation(line: 686, column: 21, scope: !3619)
!3619 = distinct !DILexicalBlock(scope: !3620, file: !3, line: 686, column: 19)
!3620 = distinct !DILexicalBlock(scope: !3583, file: !3, line: 686, column: 9)
!3621 = !DILocation(line: 686, column: 70, scope: !3619)
!3622 = !DILocation(line: 0, scope: !99, inlinedAt: !3623)
!3623 = distinct !DILocation(line: 689, column: 5, scope: !3583)
!3624 = !DILocation(line: 690, column: 1, scope: !3583)
!3625 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3590)
!3626 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3590)
!3627 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3590)
!3628 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3590)
!3629 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3590)
!3630 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3590)
!3631 = distinct !DISubprogram(name: "test_const_arrays", scope: !3, file: !3, line: 696, type: !142, scopeLine: 696, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3632)
!3632 = !{!3633, !3634, !3635, !3636, !3637}
!3633 = !DILocalVariable(name: "apdu", arg: 1, scope: !3631, file: !3, line: 696, type: !102)
!3634 = !DILocalVariable(name: "buffer", arg: 2, scope: !3631, file: !3, line: 696, type: !104)
!3635 = !DILocalVariable(name: "p1", arg: 3, scope: !3631, file: !3, line: 696, type: !5)
!3636 = !DILocalVariable(name: "i", scope: !3631, file: !3, line: 697, type: !8)
!3637 = !DILocalVariable(name: "sum", scope: !3631, file: !3, line: 698, type: !8)
!3638 = !DILocation(line: 0, scope: !3631)
!3639 = !DILocation(line: 700, column: 9, scope: !3631)
!3640 = !DILocation(line: 0, scope: !99, inlinedAt: !3641)
!3641 = distinct !DILocation(line: 701, column: 20, scope: !3642)
!3642 = distinct !DILexicalBlock(scope: !3643, file: !3, line: 701, column: 18)
!3643 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 701, column: 9)
!3644 = !DILocation(line: 701, column: 58, scope: !3642)
!3645 = !DILocation(line: 0, scope: !99, inlinedAt: !3646)
!3646 = distinct !DILocation(line: 702, column: 20, scope: !3647)
!3647 = distinct !DILexicalBlock(scope: !3648, file: !3, line: 702, column: 18)
!3648 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 702, column: 9)
!3649 = !DILocation(line: 702, column: 58, scope: !3647)
!3650 = !DILocation(line: 0, scope: !99, inlinedAt: !3651)
!3651 = distinct !DILocation(line: 703, column: 20, scope: !3652)
!3652 = distinct !DILexicalBlock(scope: !3653, file: !3, line: 703, column: 18)
!3653 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 703, column: 9)
!3654 = !DILocation(line: 703, column: 55, scope: !3652)
!3655 = !DILocation(line: 0, scope: !99, inlinedAt: !3656)
!3656 = distinct !DILocation(line: 704, column: 20, scope: !3657)
!3657 = distinct !DILexicalBlock(scope: !3658, file: !3, line: 704, column: 18)
!3658 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 704, column: 9)
!3659 = !DILocation(line: 704, column: 55, scope: !3657)
!3660 = !DILocation(line: 0, scope: !99, inlinedAt: !3661)
!3661 = distinct !DILocation(line: 710, column: 9, scope: !3662)
!3662 = distinct !DILexicalBlock(scope: !3663, file: !3, line: 705, column: 18)
!3663 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 705, column: 9)
!3664 = !DILocation(line: 711, column: 9, scope: !3662)
!3665 = !DILocation(line: 0, scope: !99, inlinedAt: !3666)
!3666 = distinct !DILocation(line: 713, column: 20, scope: !3667)
!3667 = distinct !DILexicalBlock(scope: !3668, file: !3, line: 713, column: 18)
!3668 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 713, column: 9)
!3669 = !DILocation(line: 713, column: 73, scope: !3667)
!3670 = !DILocation(line: 0, scope: !99, inlinedAt: !3671)
!3671 = distinct !DILocation(line: 714, column: 20, scope: !3672)
!3672 = distinct !DILexicalBlock(scope: !3673, file: !3, line: 714, column: 18)
!3673 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 714, column: 9)
!3674 = !DILocation(line: 714, column: 73, scope: !3672)
!3675 = !DILocation(line: 0, scope: !99, inlinedAt: !3676)
!3676 = distinct !DILocation(line: 717, column: 9, scope: !3677)
!3677 = distinct !DILexicalBlock(scope: !3678, file: !3, line: 715, column: 18)
!3678 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 715, column: 9)
!3679 = !DILocation(line: 718, column: 9, scope: !3677)
!3680 = !DILocation(line: 0, scope: !99, inlinedAt: !3681)
!3681 = distinct !DILocation(line: 721, column: 9, scope: !3682)
!3682 = distinct !DILexicalBlock(scope: !3683, file: !3, line: 720, column: 18)
!3683 = distinct !DILexicalBlock(scope: !3631, file: !3, line: 720, column: 9)
!3684 = !DILocation(line: 722, column: 9, scope: !3682)
!3685 = !DILocation(line: 0, scope: !99, inlinedAt: !3686)
!3686 = distinct !DILocation(line: 724, column: 5, scope: !3631)
!3687 = !DILocation(line: 725, column: 1, scope: !3631)
!3688 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3638)
!3689 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3638)
!3690 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3638)
!3691 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3638)
!3692 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3638)
!3693 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3638)
!3694 = distinct !DISubprogram(name: "test_zero_comparison", scope: !3, file: !3, line: 731, type: !142, scopeLine: 731, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3695)
!3695 = !{!3696, !3697, !3698, !3699, !3700}
!3696 = !DILocalVariable(name: "apdu", arg: 1, scope: !3694, file: !3, line: 731, type: !102)
!3697 = !DILocalVariable(name: "buffer", arg: 2, scope: !3694, file: !3, line: 731, type: !104)
!3698 = !DILocalVariable(name: "p1", arg: 3, scope: !3694, file: !3, line: 731, type: !5)
!3699 = !DILocalVariable(name: "x", scope: !3694, file: !3, line: 732, type: !8)
!3700 = !DILocalVariable(name: "b", scope: !3694, file: !3, line: 733, type: !5)
!3701 = !DILocation(line: 0, scope: !3694)
!3702 = !DILocation(line: 735, column: 9, scope: !3694)
!3703 = !DILocation(line: 0, scope: !99, inlinedAt: !3704)
!3704 = distinct !DILocation(line: 736, column: 27, scope: !3705)
!3705 = distinct !DILexicalBlock(scope: !3706, file: !3, line: 736, column: 18)
!3706 = distinct !DILexicalBlock(scope: !3694, file: !3, line: 736, column: 9)
!3707 = !DILocation(line: 736, column: 71, scope: !3705)
!3708 = !DILocation(line: 0, scope: !99, inlinedAt: !3709)
!3709 = distinct !DILocation(line: 738, column: 27, scope: !3710)
!3710 = distinct !DILexicalBlock(scope: !3711, file: !3, line: 738, column: 18)
!3711 = distinct !DILexicalBlock(scope: !3694, file: !3, line: 738, column: 9)
!3712 = !DILocation(line: 738, column: 71, scope: !3710)
!3713 = !DILocation(line: 0, scope: !99, inlinedAt: !3714)
!3714 = distinct !DILocation(line: 740, column: 27, scope: !3715)
!3715 = distinct !DILexicalBlock(scope: !3716, file: !3, line: 740, column: 18)
!3716 = distinct !DILexicalBlock(scope: !3694, file: !3, line: 740, column: 9)
!3717 = !DILocation(line: 740, column: 70, scope: !3715)
!3718 = !DILocation(line: 0, scope: !99, inlinedAt: !3719)
!3719 = distinct !DILocation(line: 742, column: 27, scope: !3720)
!3720 = distinct !DILexicalBlock(scope: !3721, file: !3, line: 742, column: 18)
!3721 = distinct !DILexicalBlock(scope: !3694, file: !3, line: 742, column: 9)
!3722 = !DILocation(line: 742, column: 70, scope: !3720)
!3723 = !DILocation(line: 0, scope: !99, inlinedAt: !3724)
!3724 = distinct !DILocation(line: 746, column: 28, scope: !3725)
!3725 = distinct !DILexicalBlock(scope: !3726, file: !3, line: 746, column: 19)
!3726 = distinct !DILexicalBlock(scope: !3694, file: !3, line: 746, column: 9)
!3727 = !DILocation(line: 746, column: 71, scope: !3725)
!3728 = !DILocation(line: 0, scope: !99, inlinedAt: !3729)
!3729 = distinct !DILocation(line: 750, column: 5, scope: !3694)
!3730 = !DILocation(line: 751, column: 1, scope: !3694)
!3731 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3701)
!3732 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3701)
!3733 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3701)
!3734 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3701)
!3735 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3701)
!3736 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3701)
!3737 = distinct !DISubprogram(name: "test_overflow", scope: !3, file: !3, line: 759, type: !142, scopeLine: 759, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3738)
!3738 = !{!3739, !3740, !3741, !3742, !3743}
!3739 = !DILocalVariable(name: "apdu", arg: 1, scope: !3737, file: !3, line: 759, type: !102)
!3740 = !DILocalVariable(name: "buffer", arg: 2, scope: !3737, file: !3, line: 759, type: !104)
!3741 = !DILocalVariable(name: "p1", arg: 3, scope: !3737, file: !3, line: 759, type: !5)
!3742 = !DILocalVariable(name: "s", scope: !3737, file: !3, line: 760, type: !8)
!3743 = !DILocalVariable(name: "i", scope: !3737, file: !3, line: 761, type: !20)
!3744 = !DILocation(line: 0, scope: !3737)
!3745 = !DILocation(line: 763, column: 9, scope: !3737)
!3746 = !DILocation(line: 0, scope: !99, inlinedAt: !3747)
!3747 = distinct !DILocation(line: 764, column: 35, scope: !3748)
!3748 = distinct !DILexicalBlock(scope: !3749, file: !3, line: 764, column: 18)
!3749 = distinct !DILexicalBlock(scope: !3737, file: !3, line: 764, column: 9)
!3750 = !DILocation(line: 764, column: 68, scope: !3748)
!3751 = !DILocation(line: 0, scope: !99, inlinedAt: !3752)
!3752 = distinct !DILocation(line: 765, column: 29, scope: !3753)
!3753 = distinct !DILexicalBlock(scope: !3754, file: !3, line: 765, column: 18)
!3754 = distinct !DILexicalBlock(scope: !3737, file: !3, line: 765, column: 9)
!3755 = !DILocation(line: 765, column: 62, scope: !3753)
!3756 = !DILocation(line: 0, scope: !99, inlinedAt: !3757)
!3757 = distinct !DILocation(line: 766, column: 33, scope: !3758)
!3758 = distinct !DILexicalBlock(scope: !3759, file: !3, line: 766, column: 18)
!3759 = distinct !DILexicalBlock(scope: !3737, file: !3, line: 766, column: 9)
!3760 = !DILocation(line: 766, column: 75, scope: !3758)
!3761 = !DILocation(line: 0, scope: !99, inlinedAt: !3762)
!3762 = distinct !DILocation(line: 767, column: 46, scope: !3763)
!3763 = distinct !DILexicalBlock(scope: !3764, file: !3, line: 767, column: 18)
!3764 = distinct !DILexicalBlock(scope: !3737, file: !3, line: 767, column: 9)
!3765 = !DILocation(line: 767, column: 75, scope: !3763)
!3766 = !DILocation(line: 0, scope: !99, inlinedAt: !3767)
!3767 = distinct !DILocation(line: 768, column: 38, scope: !3768)
!3768 = distinct !DILexicalBlock(scope: !3769, file: !3, line: 768, column: 18)
!3769 = distinct !DILexicalBlock(scope: !3737, file: !3, line: 768, column: 9)
!3770 = !DILocation(line: 768, column: 67, scope: !3768)
!3771 = !DILocation(line: 0, scope: !99, inlinedAt: !3772)
!3772 = distinct !DILocation(line: 769, column: 39, scope: !3773)
!3773 = distinct !DILexicalBlock(scope: !3774, file: !3, line: 769, column: 18)
!3774 = distinct !DILexicalBlock(scope: !3737, file: !3, line: 769, column: 9)
!3775 = !DILocation(line: 769, column: 68, scope: !3773)
!3776 = !DILocation(line: 0, scope: !99, inlinedAt: !3777)
!3777 = distinct !DILocation(line: 771, column: 5, scope: !3737)
!3778 = !DILocation(line: 772, column: 1, scope: !3737)
!3779 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3744)
!3780 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3744)
!3781 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3744)
!3782 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3744)
!3783 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3744)
!3784 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3744)
!3785 = distinct !DISubprogram(name: "test_negative_math", scope: !3, file: !3, line: 778, type: !142, scopeLine: 778, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3786)
!3786 = !{!3787, !3788, !3789, !3790, !3791, !3792}
!3787 = !DILocalVariable(name: "apdu", arg: 1, scope: !3785, file: !3, line: 778, type: !102)
!3788 = !DILocalVariable(name: "buffer", arg: 2, scope: !3785, file: !3, line: 778, type: !104)
!3789 = !DILocalVariable(name: "p1", arg: 3, scope: !3785, file: !3, line: 778, type: !5)
!3790 = !DILocalVariable(name: "a", scope: !3785, file: !3, line: 779, type: !8)
!3791 = !DILocalVariable(name: "b", scope: !3785, file: !3, line: 780, type: !8)
!3792 = !DILocalVariable(name: "i", scope: !3785, file: !3, line: 781, type: !20)
!3793 = !DILocation(line: 0, scope: !3785)
!3794 = !DILocation(line: 783, column: 9, scope: !3785)
!3795 = !DILocation(line: 0, scope: !99, inlinedAt: !3796)
!3796 = distinct !DILocation(line: 785, column: 37, scope: !3797)
!3797 = distinct !DILexicalBlock(scope: !3798, file: !3, line: 785, column: 18)
!3798 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 785, column: 9)
!3799 = !DILocation(line: 785, column: 70, scope: !3797)
!3800 = !DILocation(line: 0, scope: !99, inlinedAt: !3801)
!3801 = distinct !DILocation(line: 786, column: 36, scope: !3802)
!3802 = distinct !DILexicalBlock(scope: !3803, file: !3, line: 786, column: 18)
!3803 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 786, column: 9)
!3804 = !DILocation(line: 786, column: 69, scope: !3802)
!3805 = !DILocation(line: 0, scope: !99, inlinedAt: !3806)
!3806 = distinct !DILocation(line: 787, column: 36, scope: !3807)
!3807 = distinct !DILexicalBlock(scope: !3808, file: !3, line: 787, column: 18)
!3808 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 787, column: 9)
!3809 = !DILocation(line: 787, column: 69, scope: !3807)
!3810 = !DILocation(line: 0, scope: !99, inlinedAt: !3811)
!3811 = distinct !DILocation(line: 788, column: 37, scope: !3812)
!3812 = distinct !DILexicalBlock(scope: !3813, file: !3, line: 788, column: 18)
!3813 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 788, column: 9)
!3814 = !DILocation(line: 788, column: 70, scope: !3812)
!3815 = !DILocation(line: 0, scope: !99, inlinedAt: !3816)
!3816 = distinct !DILocation(line: 789, column: 28, scope: !3817)
!3817 = distinct !DILexicalBlock(scope: !3818, file: !3, line: 789, column: 18)
!3818 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 789, column: 9)
!3819 = !DILocation(line: 789, column: 62, scope: !3817)
!3820 = !DILocation(line: 0, scope: !99, inlinedAt: !3821)
!3821 = distinct !DILocation(line: 790, column: 30, scope: !3822)
!3822 = distinct !DILexicalBlock(scope: !3823, file: !3, line: 790, column: 18)
!3823 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 790, column: 9)
!3824 = !DILocation(line: 790, column: 64, scope: !3822)
!3825 = !DILocation(line: 0, scope: !99, inlinedAt: !3826)
!3826 = distinct !DILocation(line: 791, column: 28, scope: !3827)
!3827 = distinct !DILexicalBlock(scope: !3828, file: !3, line: 791, column: 18)
!3828 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 791, column: 9)
!3829 = !DILocation(line: 791, column: 72, scope: !3827)
!3830 = !DILocation(line: 0, scope: !99, inlinedAt: !3831)
!3831 = distinct !DILocation(line: 792, column: 35, scope: !3832)
!3832 = distinct !DILexicalBlock(scope: !3833, file: !3, line: 792, column: 18)
!3833 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 792, column: 9)
!3834 = !DILocation(line: 792, column: 68, scope: !3832)
!3835 = !DILocation(line: 0, scope: !99, inlinedAt: !3836)
!3836 = distinct !DILocation(line: 793, column: 40, scope: !3837)
!3837 = distinct !DILexicalBlock(scope: !3838, file: !3, line: 793, column: 19)
!3838 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 793, column: 9)
!3839 = !DILocation(line: 793, column: 73, scope: !3837)
!3840 = !DILocation(line: 0, scope: !99, inlinedAt: !3841)
!3841 = distinct !DILocation(line: 794, column: 29, scope: !3842)
!3842 = distinct !DILexicalBlock(scope: !3843, file: !3, line: 794, column: 19)
!3843 = distinct !DILexicalBlock(scope: !3785, file: !3, line: 794, column: 9)
!3844 = !DILocation(line: 794, column: 65, scope: !3842)
!3845 = !DILocation(line: 0, scope: !99, inlinedAt: !3846)
!3846 = distinct !DILocation(line: 795, column: 5, scope: !3785)
!3847 = !DILocation(line: 796, column: 1, scope: !3785)
!3848 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3793)
!3849 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3793)
!3850 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3793)
!3851 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3793)
!3852 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3793)
!3853 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3793)
!3854 = distinct !DISubprogram(name: "test_coercion", scope: !3, file: !3, line: 802, type: !142, scopeLine: 802, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3855)
!3855 = !{!3856, !3857, !3858, !3859, !3860, !3861}
!3856 = !DILocalVariable(name: "apdu", arg: 1, scope: !3854, file: !3, line: 802, type: !102)
!3857 = !DILocalVariable(name: "buffer", arg: 2, scope: !3854, file: !3, line: 802, type: !104)
!3858 = !DILocalVariable(name: "p1", arg: 3, scope: !3854, file: !3, line: 802, type: !5)
!3859 = !DILocalVariable(name: "b", scope: !3854, file: !3, line: 803, type: !5)
!3860 = !DILocalVariable(name: "s", scope: !3854, file: !3, line: 804, type: !8)
!3861 = !DILocalVariable(name: "i", scope: !3854, file: !3, line: 805, type: !20)
!3862 = !DILocation(line: 0, scope: !3854)
!3863 = !DILocation(line: 807, column: 9, scope: !3854)
!3864 = !DILocation(line: 0, scope: !99, inlinedAt: !3865)
!3865 = distinct !DILocation(line: 808, column: 38, scope: !3866)
!3866 = distinct !DILexicalBlock(scope: !3867, file: !3, line: 808, column: 18)
!3867 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 808, column: 9)
!3868 = !DILocation(line: 808, column: 80, scope: !3866)
!3869 = !DILocation(line: 0, scope: !99, inlinedAt: !3870)
!3870 = distinct !DILocation(line: 809, column: 28, scope: !3871)
!3871 = distinct !DILexicalBlock(scope: !3872, file: !3, line: 809, column: 18)
!3872 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 809, column: 9)
!3873 = !DILocation(line: 809, column: 57, scope: !3871)
!3874 = !DILocation(line: 0, scope: !99, inlinedAt: !3875)
!3875 = distinct !DILocation(line: 810, column: 28, scope: !3876)
!3876 = distinct !DILexicalBlock(scope: !3877, file: !3, line: 810, column: 18)
!3877 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 810, column: 9)
!3878 = !DILocation(line: 810, column: 64, scope: !3876)
!3879 = !DILocation(line: 0, scope: !99, inlinedAt: !3880)
!3880 = distinct !DILocation(line: 811, column: 38, scope: !3881)
!3881 = distinct !DILexicalBlock(scope: !3882, file: !3, line: 811, column: 18)
!3882 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 811, column: 9)
!3883 = !DILocation(line: 811, column: 71, scope: !3881)
!3884 = !DILocation(line: 0, scope: !99, inlinedAt: !3885)
!3885 = distinct !DILocation(line: 812, column: 37, scope: !3886)
!3886 = distinct !DILexicalBlock(scope: !3887, file: !3, line: 812, column: 18)
!3887 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 812, column: 9)
!3888 = !DILocation(line: 812, column: 79, scope: !3886)
!3889 = !DILocation(line: 0, scope: !99, inlinedAt: !3890)
!3890 = distinct !DILocation(line: 813, column: 35, scope: !3891)
!3891 = distinct !DILexicalBlock(scope: !3892, file: !3, line: 813, column: 18)
!3892 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 813, column: 9)
!3893 = !DILocation(line: 813, column: 71, scope: !3891)
!3894 = !DILocation(line: 0, scope: !99, inlinedAt: !3895)
!3895 = distinct !DILocation(line: 814, column: 45, scope: !3896)
!3896 = distinct !DILexicalBlock(scope: !3897, file: !3, line: 814, column: 18)
!3897 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 814, column: 9)
!3898 = !DILocation(line: 814, column: 74, scope: !3896)
!3899 = !DILocation(line: 0, scope: !99, inlinedAt: !3900)
!3900 = distinct !DILocation(line: 815, column: 34, scope: !3901)
!3901 = distinct !DILexicalBlock(scope: !3902, file: !3, line: 815, column: 18)
!3902 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 815, column: 9)
!3903 = !DILocation(line: 815, column: 67, scope: !3901)
!3904 = !DILocation(line: 0, scope: !99, inlinedAt: !3905)
!3905 = distinct !DILocation(line: 816, column: 34, scope: !3906)
!3906 = distinct !DILexicalBlock(scope: !3907, file: !3, line: 816, column: 18)
!3907 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 816, column: 9)
!3908 = !DILocation(line: 816, column: 67, scope: !3906)
!3909 = !DILocation(line: 0, scope: !99, inlinedAt: !3910)
!3910 = distinct !DILocation(line: 817, column: 37, scope: !3911)
!3911 = distinct !DILexicalBlock(scope: !3912, file: !3, line: 817, column: 19)
!3912 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 817, column: 9)
!3913 = !DILocation(line: 817, column: 80, scope: !3911)
!3914 = !DILocation(line: 0, scope: !99, inlinedAt: !3915)
!3915 = distinct !DILocation(line: 818, column: 39, scope: !3916)
!3916 = distinct !DILexicalBlock(scope: !3917, file: !3, line: 818, column: 19)
!3917 = distinct !DILexicalBlock(scope: !3854, file: !3, line: 818, column: 9)
!3918 = !DILocation(line: 818, column: 83, scope: !3916)
!3919 = !DILocation(line: 0, scope: !99, inlinedAt: !3920)
!3920 = distinct !DILocation(line: 819, column: 5, scope: !3854)
!3921 = !DILocation(line: 820, column: 1, scope: !3854)
!3922 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3862)
!3923 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3862)
!3924 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3862)
!3925 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3862)
!3926 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3862)
!3927 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3862)
!3928 = distinct !DISubprogram(name: "test_switch_dense", scope: !3, file: !3, line: 826, type: !142, scopeLine: 826, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3929)
!3929 = !{!3930, !3931, !3932, !3933}
!3930 = !DILocalVariable(name: "apdu", arg: 1, scope: !3928, file: !3, line: 826, type: !102)
!3931 = !DILocalVariable(name: "buffer", arg: 2, scope: !3928, file: !3, line: 826, type: !104)
!3932 = !DILocalVariable(name: "p1", arg: 3, scope: !3928, file: !3, line: 826, type: !5)
!3933 = !DILocalVariable(name: "result", scope: !3928, file: !3, line: 827, type: !8)
!3934 = !DILocation(line: 0, scope: !3928)
!3935 = !DILocation(line: 829, column: 5, scope: !3928)
!3936 = !DILocation(line: 831, column: 27, scope: !3937)
!3937 = distinct !DILexicalBlock(scope: !3928, file: !3, line: 829, column: 17)
!3938 = !DILocation(line: 832, column: 27, scope: !3937)
!3939 = !DILocation(line: 833, column: 27, scope: !3937)
!3940 = !DILocation(line: 834, column: 27, scope: !3937)
!3941 = !DILocation(line: 835, column: 27, scope: !3937)
!3942 = !DILocation(line: 836, column: 27, scope: !3937)
!3943 = !DILocation(line: 837, column: 27, scope: !3937)
!3944 = !DILocation(line: 839, column: 5, scope: !3937)
!3945 = !DILocation(line: 0, scope: !99, inlinedAt: !3946)
!3946 = distinct !DILocation(line: 840, column: 5, scope: !3928)
!3947 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3946)
!3948 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3946)
!3949 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3946)
!3950 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3946)
!3951 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3946)
!3952 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3946)
!3953 = !DILocation(line: 841, column: 1, scope: !3928)
!3954 = distinct !DISubprogram(name: "test_switch_sparse", scope: !3, file: !3, line: 847, type: !142, scopeLine: 847, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3955)
!3955 = !{!3956, !3957, !3958, !3959}
!3956 = !DILocalVariable(name: "apdu", arg: 1, scope: !3954, file: !3, line: 847, type: !102)
!3957 = !DILocalVariable(name: "buffer", arg: 2, scope: !3954, file: !3, line: 847, type: !104)
!3958 = !DILocalVariable(name: "p1", arg: 3, scope: !3954, file: !3, line: 847, type: !5)
!3959 = !DILocalVariable(name: "result", scope: !3954, file: !3, line: 848, type: !8)
!3960 = !DILocation(line: 0, scope: !3954)
!3961 = !DILocation(line: 850, column: 5, scope: !3954)
!3962 = !DILocation(line: 852, column: 28, scope: !3963)
!3963 = distinct !DILexicalBlock(scope: !3954, file: !3, line: 850, column: 17)
!3964 = !DILocation(line: 853, column: 28, scope: !3963)
!3965 = !DILocation(line: 854, column: 28, scope: !3963)
!3966 = !DILocation(line: 855, column: 28, scope: !3963)
!3967 = !DILocation(line: 857, column: 5, scope: !3963)
!3968 = !DILocation(line: 0, scope: !99, inlinedAt: !3969)
!3969 = distinct !DILocation(line: 858, column: 5, scope: !3954)
!3970 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3969)
!3971 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3969)
!3972 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3969)
!3973 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3969)
!3974 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3969)
!3975 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3969)
!3976 = !DILocation(line: 859, column: 1, scope: !3954)
!3977 = distinct !DISubprogram(name: "test_break_continue", scope: !3, file: !3, line: 865, type: !142, scopeLine: 865, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !3978)
!3978 = !{!3979, !3980, !3981, !3982, !3983, !3984}
!3979 = !DILocalVariable(name: "apdu", arg: 1, scope: !3977, file: !3, line: 865, type: !102)
!3980 = !DILocalVariable(name: "buffer", arg: 2, scope: !3977, file: !3, line: 865, type: !104)
!3981 = !DILocalVariable(name: "p1", arg: 3, scope: !3977, file: !3, line: 865, type: !5)
!3982 = !DILocalVariable(name: "i", scope: !3977, file: !3, line: 866, type: !8)
!3983 = !DILocalVariable(name: "sum", scope: !3977, file: !3, line: 867, type: !8)
!3984 = !DILocalVariable(name: "j", scope: !3985, file: !3, line: 905, type: !8)
!3985 = distinct !DILexicalBlock(scope: !3986, file: !3, line: 904, column: 39)
!3986 = distinct !DILexicalBlock(scope: !3987, file: !3, line: 904, column: 9)
!3987 = distinct !DILexicalBlock(scope: !3988, file: !3, line: 904, column: 9)
!3988 = distinct !DILexicalBlock(scope: !3989, file: !3, line: 901, column: 18)
!3989 = distinct !DILexicalBlock(scope: !3977, file: !3, line: 901, column: 9)
!3990 = !DILocation(line: 0, scope: !3977)
!3991 = !DILocation(line: 869, column: 9, scope: !3977)
!3992 = !DILocation(line: 0, scope: !99, inlinedAt: !3993)
!3993 = distinct !DILocation(line: 886, column: 9, scope: !3994)
!3994 = distinct !DILexicalBlock(scope: !3995, file: !3, line: 879, column: 18)
!3995 = distinct !DILexicalBlock(scope: !3977, file: !3, line: 879, column: 9)
!3996 = !DILocation(line: 887, column: 9, scope: !3994)
!3997 = !DILocation(line: 0, scope: !99, inlinedAt: !3998)
!3998 = distinct !DILocation(line: 898, column: 9, scope: !3999)
!3999 = distinct !DILexicalBlock(scope: !4000, file: !3, line: 889, column: 18)
!4000 = distinct !DILexicalBlock(scope: !3977, file: !3, line: 889, column: 9)
!4001 = !DILocation(line: 899, column: 9, scope: !3999)
!4002 = !DILocation(line: 0, scope: !99, inlinedAt: !4003)
!4003 = distinct !DILocation(line: 911, column: 9, scope: !3988)
!4004 = !DILocation(line: 912, column: 9, scope: !3988)
!4005 = !DILocation(line: 0, scope: !99, inlinedAt: !4006)
!4006 = distinct !DILocation(line: 914, column: 5, scope: !3977)
!4007 = !DILocation(line: 915, column: 1, scope: !3977)
!4008 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !3990)
!4009 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !3990)
!4010 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !3990)
!4011 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !3990)
!4012 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !3990)
!4013 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !3990)
!4014 = distinct !DISubprogram(name: "test_complex_boolean", scope: !3, file: !3, line: 921, type: !142, scopeLine: 921, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4015)
!4015 = !{!4016, !4017, !4018, !4019, !4020, !4021, !4022, !4023, !4026}
!4016 = !DILocalVariable(name: "apdu", arg: 1, scope: !4014, file: !3, line: 921, type: !102)
!4017 = !DILocalVariable(name: "buffer", arg: 2, scope: !4014, file: !3, line: 921, type: !104)
!4018 = !DILocalVariable(name: "p1", arg: 3, scope: !4014, file: !3, line: 921, type: !5)
!4019 = !DILocalVariable(name: "a", scope: !4014, file: !3, line: 922, type: !8)
!4020 = !DILocalVariable(name: "b", scope: !4014, file: !3, line: 923, type: !8)
!4021 = !DILocalVariable(name: "c", scope: !4014, file: !3, line: 924, type: !8)
!4022 = !DILocalVariable(name: "d", scope: !4014, file: !3, line: 925, type: !8)
!4023 = !DILocalVariable(name: "x", scope: !4024, file: !3, line: 959, type: !8)
!4024 = distinct !DILexicalBlock(scope: !4025, file: !3, line: 957, column: 18)
!4025 = distinct !DILexicalBlock(scope: !4014, file: !3, line: 957, column: 9)
!4026 = !DILocalVariable(name: "y", scope: !4024, file: !3, line: 960, type: !8)
!4027 = !DILocation(line: 0, scope: !4014)
!4028 = !DILocation(line: 927, column: 9, scope: !4014)
!4029 = !DILocation(line: 0, scope: !99, inlinedAt: !4030)
!4030 = distinct !DILocation(line: 939, column: 9, scope: !4031)
!4031 = distinct !DILexicalBlock(scope: !4032, file: !3, line: 937, column: 18)
!4032 = distinct !DILexicalBlock(scope: !4014, file: !3, line: 937, column: 9)
!4033 = !DILocation(line: 940, column: 9, scope: !4031)
!4034 = !DILocation(line: 0, scope: !99, inlinedAt: !4035)
!4035 = distinct !DILocation(line: 954, column: 9, scope: !4036)
!4036 = distinct !DILexicalBlock(scope: !4037, file: !3, line: 952, column: 18)
!4037 = distinct !DILexicalBlock(scope: !4014, file: !3, line: 952, column: 9)
!4038 = !DILocation(line: 955, column: 9, scope: !4036)
!4039 = !DILocation(line: 0, scope: !99, inlinedAt: !4040)
!4040 = distinct !DILocation(line: 969, column: 5, scope: !4014)
!4041 = !DILocation(line: 970, column: 1, scope: !4014)
!4042 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4027)
!4043 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4027)
!4044 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4027)
!4045 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4027)
!4046 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4027)
!4047 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4027)
!4048 = distinct !DISubprogram(name: "test_deep_nesting", scope: !3, file: !3, line: 978, type: !142, scopeLine: 978, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4049)
!4049 = !{!4050, !4051, !4052, !4053, !4054, !4055, !4058, !4059, !4062, !4063, !4064, !4067}
!4050 = !DILocalVariable(name: "apdu", arg: 1, scope: !4048, file: !3, line: 978, type: !102)
!4051 = !DILocalVariable(name: "buffer", arg: 2, scope: !4048, file: !3, line: 978, type: !104)
!4052 = !DILocalVariable(name: "p1", arg: 3, scope: !4048, file: !3, line: 978, type: !5)
!4053 = !DILocalVariable(name: "x", scope: !4048, file: !3, line: 979, type: !8)
!4054 = !DILocalVariable(name: "result", scope: !4048, file: !3, line: 980, type: !8)
!4055 = !DILocalVariable(name: "i", scope: !4056, file: !3, line: 998, type: !8)
!4056 = distinct !DILexicalBlock(scope: !4057, file: !3, line: 996, column: 18)
!4057 = distinct !DILexicalBlock(scope: !4048, file: !3, line: 996, column: 9)
!4058 = !DILocalVariable(name: "j", scope: !4056, file: !3, line: 999, type: !8)
!4059 = !DILocalVariable(name: "i", scope: !4060, file: !3, line: 1011, type: !8)
!4060 = distinct !DILexicalBlock(scope: !4061, file: !3, line: 1009, column: 18)
!4061 = distinct !DILexicalBlock(scope: !4048, file: !3, line: 1009, column: 9)
!4062 = !DILocalVariable(name: "j", scope: !4060, file: !3, line: 1012, type: !8)
!4063 = !DILocalVariable(name: "k", scope: !4060, file: !3, line: 1013, type: !8)
!4064 = !DILocalVariable(name: "i", scope: !4065, file: !3, line: 1027, type: !8)
!4065 = distinct !DILexicalBlock(scope: !4066, file: !3, line: 1025, column: 18)
!4066 = distinct !DILexicalBlock(scope: !4048, file: !3, line: 1025, column: 9)
!4067 = !DILocalVariable(name: "j", scope: !4065, file: !3, line: 1028, type: !8)
!4068 = !DILocation(line: 0, scope: !4048)
!4069 = !DILocation(line: 982, column: 9, scope: !4048)
!4070 = !DILocation(line: 0, scope: !99, inlinedAt: !4071)
!4071 = distinct !DILocation(line: 993, column: 9, scope: !4072)
!4072 = distinct !DILexicalBlock(scope: !4073, file: !3, line: 982, column: 18)
!4073 = distinct !DILexicalBlock(scope: !4048, file: !3, line: 982, column: 9)
!4074 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4071)
!4075 = !DILocation(line: 994, column: 9, scope: !4072)
!4076 = !DILocation(line: 0, scope: !4056)
!4077 = !DILocation(line: 0, scope: !99, inlinedAt: !4078)
!4078 = distinct !DILocation(line: 1006, column: 9, scope: !4056)
!4079 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4078)
!4080 = !DILocation(line: 0, scope: !4060)
!4081 = !DILocation(line: 0, scope: !99, inlinedAt: !4082)
!4082 = distinct !DILocation(line: 1022, column: 9, scope: !4060)
!4083 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4082)
!4084 = !DILocation(line: 1031, column: 19, scope: !4085)
!4085 = distinct !DILexicalBlock(scope: !4086, file: !3, line: 1031, column: 17)
!4086 = distinct !DILexicalBlock(scope: !4087, file: !3, line: 1030, column: 39)
!4087 = distinct !DILexicalBlock(scope: !4088, file: !3, line: 1030, column: 9)
!4088 = distinct !DILexicalBlock(scope: !4065, file: !3, line: 1030, column: 9)
!4089 = !DILocation(line: 1031, column: 17, scope: !4086)
!4090 = !DILocation(line: 1033, column: 37, scope: !4091)
!4091 = distinct !DILexicalBlock(scope: !4092, file: !3, line: 1032, column: 47)
!4092 = distinct !DILexicalBlock(scope: !4093, file: !3, line: 1032, column: 17)
!4093 = distinct !DILexicalBlock(scope: !4094, file: !3, line: 1032, column: 17)
!4094 = distinct !DILexicalBlock(scope: !4085, file: !3, line: 1031, column: 24)
!4095 = !DILocation(line: 1032, column: 42, scope: !4092)
!4096 = !DILocation(line: 0, scope: !4065)
!4097 = !DILocation(line: 1032, column: 29, scope: !4092)
!4098 = !DILocation(line: 1032, column: 31, scope: !4092)
!4099 = !DILocation(line: 1032, column: 17, scope: !4093)
!4100 = distinct !{!4100, !4099, !4101, !312, !313}
!4101 = !DILocation(line: 1034, column: 17, scope: !4093)
!4102 = !DILocation(line: 1029, column: 16, scope: !4065)
!4103 = !DILocation(line: 1030, column: 21, scope: !4087)
!4104 = !DILocation(line: 1030, column: 23, scope: !4087)
!4105 = !DILocation(line: 1030, column: 9, scope: !4088)
!4106 = distinct !{!4106, !4105, !4107, !312, !313}
!4107 = !DILocation(line: 1036, column: 9, scope: !4088)
!4108 = !DILocation(line: 0, scope: !99, inlinedAt: !4109)
!4109 = distinct !DILocation(line: 1037, column: 9, scope: !4065)
!4110 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4109)
!4111 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !4109)
!4112 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4109)
!4113 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !4109)
!4114 = !DILocation(line: 0, scope: !99, inlinedAt: !4115)
!4115 = distinct !DILocation(line: 1040, column: 5, scope: !4048)
!4116 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4115)
!4117 = !DILocation(line: 1041, column: 1, scope: !4048)
!4118 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4068)
!4119 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4068)
!4120 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4068)
!4121 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4068)
!4122 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4068)
!4123 = distinct !DISubprogram(name: "test_many_locals", scope: !3, file: !3, line: 1047, type: !142, scopeLine: 1047, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4124)
!4124 = !{!4125, !4126, !4127, !4128, !4129, !4130, !4131, !4132, !4133, !4134, !4135, !4136, !4137, !4138, !4139, !4140, !4141, !4142, !4143}
!4125 = !DILocalVariable(name: "apdu", arg: 1, scope: !4123, file: !3, line: 1047, type: !102)
!4126 = !DILocalVariable(name: "buffer", arg: 2, scope: !4123, file: !3, line: 1047, type: !104)
!4127 = !DILocalVariable(name: "p1", arg: 3, scope: !4123, file: !3, line: 1047, type: !5)
!4128 = !DILocalVariable(name: "a", scope: !4123, file: !3, line: 1048, type: !8)
!4129 = !DILocalVariable(name: "b", scope: !4123, file: !3, line: 1048, type: !8)
!4130 = !DILocalVariable(name: "c", scope: !4123, file: !3, line: 1048, type: !8)
!4131 = !DILocalVariable(name: "d", scope: !4123, file: !3, line: 1048, type: !8)
!4132 = !DILocalVariable(name: "e", scope: !4123, file: !3, line: 1048, type: !8)
!4133 = !DILocalVariable(name: "f", scope: !4123, file: !3, line: 1048, type: !8)
!4134 = !DILocalVariable(name: "g", scope: !4123, file: !3, line: 1048, type: !8)
!4135 = !DILocalVariable(name: "h", scope: !4123, file: !3, line: 1048, type: !8)
!4136 = !DILocalVariable(name: "i", scope: !4123, file: !3, line: 1049, type: !8)
!4137 = !DILocalVariable(name: "j", scope: !4123, file: !3, line: 1049, type: !8)
!4138 = !DILocalVariable(name: "k", scope: !4123, file: !3, line: 1049, type: !8)
!4139 = !DILocalVariable(name: "l", scope: !4123, file: !3, line: 1049, type: !8)
!4140 = !DILocalVariable(name: "m", scope: !4123, file: !3, line: 1049, type: !8)
!4141 = !DILocalVariable(name: "n", scope: !4123, file: !3, line: 1049, type: !8)
!4142 = !DILocalVariable(name: "o", scope: !4123, file: !3, line: 1049, type: !8)
!4143 = !DILocalVariable(name: "p", scope: !4123, file: !3, line: 1049, type: !8)
!4144 = !DILocation(line: 0, scope: !4123)
!4145 = !DILocation(line: 1056, column: 9, scope: !4123)
!4146 = !DILocation(line: 0, scope: !99, inlinedAt: !4147)
!4147 = distinct !DILocation(line: 1061, column: 9, scope: !4148)
!4148 = distinct !DILexicalBlock(scope: !4149, file: !3, line: 1060, column: 18)
!4149 = distinct !DILexicalBlock(scope: !4123, file: !3, line: 1060, column: 9)
!4150 = !DILocation(line: 1062, column: 9, scope: !4148)
!4151 = !DILocation(line: 0, scope: !99, inlinedAt: !4152)
!4152 = distinct !DILocation(line: 1065, column: 9, scope: !4153)
!4153 = distinct !DILexicalBlock(scope: !4154, file: !3, line: 1064, column: 18)
!4154 = distinct !DILexicalBlock(scope: !4123, file: !3, line: 1064, column: 9)
!4155 = !DILocation(line: 1066, column: 9, scope: !4153)
!4156 = !DILocation(line: 0, scope: !99, inlinedAt: !4157)
!4157 = distinct !DILocation(line: 1069, column: 9, scope: !4158)
!4158 = distinct !DILexicalBlock(scope: !4159, file: !3, line: 1068, column: 18)
!4159 = distinct !DILexicalBlock(scope: !4123, file: !3, line: 1068, column: 9)
!4160 = !DILocation(line: 1070, column: 9, scope: !4158)
!4161 = !DILocation(line: 0, scope: !99, inlinedAt: !4162)
!4162 = distinct !DILocation(line: 1073, column: 9, scope: !4163)
!4163 = distinct !DILexicalBlock(scope: !4164, file: !3, line: 1072, column: 18)
!4164 = distinct !DILexicalBlock(scope: !4123, file: !3, line: 1072, column: 9)
!4165 = !DILocation(line: 1074, column: 9, scope: !4163)
!4166 = !DILocation(line: 0, scope: !99, inlinedAt: !4167)
!4167 = distinct !DILocation(line: 1078, column: 9, scope: !4168)
!4168 = distinct !DILexicalBlock(scope: !4169, file: !3, line: 1076, column: 18)
!4169 = distinct !DILexicalBlock(scope: !4123, file: !3, line: 1076, column: 9)
!4170 = !DILocation(line: 1079, column: 9, scope: !4168)
!4171 = !DILocation(line: 0, scope: !99, inlinedAt: !4172)
!4172 = distinct !DILocation(line: 1083, column: 9, scope: !4173)
!4173 = distinct !DILexicalBlock(scope: !4174, file: !3, line: 1081, column: 18)
!4174 = distinct !DILexicalBlock(scope: !4123, file: !3, line: 1081, column: 9)
!4175 = !DILocation(line: 1084, column: 9, scope: !4173)
!4176 = !DILocation(line: 0, scope: !99, inlinedAt: !4177)
!4177 = distinct !DILocation(line: 1088, column: 9, scope: !4178)
!4178 = distinct !DILexicalBlock(scope: !4179, file: !3, line: 1086, column: 18)
!4179 = distinct !DILexicalBlock(scope: !4123, file: !3, line: 1086, column: 9)
!4180 = !DILocation(line: 1089, column: 9, scope: !4178)
!4181 = !DILocation(line: 0, scope: !99, inlinedAt: !4182)
!4182 = distinct !DILocation(line: 1091, column: 5, scope: !4123)
!4183 = !DILocation(line: 1092, column: 1, scope: !4123)
!4184 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4144)
!4185 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4144)
!4186 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4144)
!4187 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4144)
!4188 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4144)
!4189 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4144)
!4190 = distinct !DISubprogram(name: "test_int_arrays", scope: !3, file: !3, line: 1098, type: !142, scopeLine: 1098, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4191)
!4191 = !{!4192, !4193, !4194, !4195, !4196}
!4192 = !DILocalVariable(name: "apdu", arg: 1, scope: !4190, file: !3, line: 1098, type: !102)
!4193 = !DILocalVariable(name: "buffer", arg: 2, scope: !4190, file: !3, line: 1098, type: !104)
!4194 = !DILocalVariable(name: "p1", arg: 3, scope: !4190, file: !3, line: 1098, type: !5)
!4195 = !DILocalVariable(name: "i", scope: !4190, file: !3, line: 1099, type: !8)
!4196 = !DILocalVariable(name: "sum", scope: !4197, file: !3, line: 1136, type: !20)
!4197 = distinct !DILexicalBlock(scope: !4198, file: !3, line: 1134, column: 18)
!4198 = distinct !DILexicalBlock(scope: !4190, file: !3, line: 1134, column: 9)
!4199 = !DILocation(line: 0, scope: !4190)
!4200 = !DILocation(line: 1101, column: 9, scope: !4190)
!4201 = !DILocation(line: 1102, column: 19, scope: !4202)
!4202 = distinct !DILexicalBlock(scope: !4203, file: !3, line: 1101, column: 18)
!4203 = distinct !DILexicalBlock(scope: !4190, file: !3, line: 1101, column: 9)
!4204 = !DILocation(line: 0, scope: !99, inlinedAt: !4205)
!4205 = distinct !DILocation(line: 1103, column: 9, scope: !4202)
!4206 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4205)
!4207 = !DILocation(line: 1104, column: 9, scope: !4202)
!4208 = !DILocation(line: 1107, column: 19, scope: !4209)
!4209 = distinct !DILexicalBlock(scope: !4210, file: !3, line: 1106, column: 18)
!4210 = distinct !DILexicalBlock(scope: !4190, file: !3, line: 1106, column: 9)
!4211 = !DILocation(line: 1108, column: 19, scope: !4209)
!4212 = !DILocation(line: 0, scope: !99, inlinedAt: !4213)
!4213 = distinct !DILocation(line: 1109, column: 9, scope: !4209)
!4214 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4213)
!4215 = !DILocation(line: 1110, column: 9, scope: !4209)
!4216 = !DILocation(line: 1114, column: 19, scope: !4217)
!4217 = distinct !DILexicalBlock(scope: !4218, file: !3, line: 1112, column: 18)
!4218 = distinct !DILexicalBlock(scope: !4190, file: !3, line: 1112, column: 9)
!4219 = !DILocation(line: 0, scope: !99, inlinedAt: !4220)
!4220 = distinct !DILocation(line: 1115, column: 9, scope: !4217)
!4221 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4220)
!4222 = !DILocation(line: 1116, column: 9, scope: !4217)
!4223 = !DILocation(line: 1119, column: 19, scope: !4224)
!4224 = distinct !DILexicalBlock(scope: !4225, file: !3, line: 1118, column: 18)
!4225 = distinct !DILexicalBlock(scope: !4190, file: !3, line: 1118, column: 9)
!4226 = !DILocation(line: 0, scope: !99, inlinedAt: !4227)
!4227 = distinct !DILocation(line: 1120, column: 9, scope: !4224)
!4228 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4227)
!4229 = !DILocation(line: 1121, column: 9, scope: !4224)
!4230 = !DILocation(line: 1124, column: 19, scope: !4231)
!4231 = distinct !DILexicalBlock(scope: !4232, file: !3, line: 1123, column: 18)
!4232 = distinct !DILexicalBlock(scope: !4190, file: !3, line: 1123, column: 9)
!4233 = !DILocation(line: 0, scope: !99, inlinedAt: !4234)
!4234 = distinct !DILocation(line: 1125, column: 9, scope: !4231)
!4235 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4234)
!4236 = !DILocation(line: 1126, column: 9, scope: !4231)
!4237 = !DILocation(line: 1130, column: 19, scope: !4238)
!4238 = distinct !DILexicalBlock(scope: !4239, file: !3, line: 1128, column: 18)
!4239 = distinct !DILexicalBlock(scope: !4190, file: !3, line: 1128, column: 9)
!4240 = !DILocation(line: 0, scope: !99, inlinedAt: !4241)
!4241 = distinct !DILocation(line: 1131, column: 9, scope: !4238)
!4242 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4241)
!4243 = !DILocation(line: 1132, column: 9, scope: !4238)
!4244 = !DILocation(line: 1138, column: 28, scope: !4245)
!4245 = distinct !DILexicalBlock(scope: !4246, file: !3, line: 1137, column: 39)
!4246 = distinct !DILexicalBlock(scope: !4247, file: !3, line: 1137, column: 9)
!4247 = distinct !DILexicalBlock(scope: !4197, file: !3, line: 1137, column: 9)
!4248 = !DILocation(line: 1138, column: 33, scope: !4245)
!4249 = !DILocation(line: 1138, column: 13, scope: !4245)
!4250 = !DILocation(line: 1138, column: 23, scope: !4245)
!4251 = !DILocation(line: 1137, column: 21, scope: !4246)
!4252 = !DILocation(line: 1137, column: 23, scope: !4246)
!4253 = !DILocation(line: 1137, column: 9, scope: !4247)
!4254 = distinct !{!4254, !4253, !4255, !312, !313}
!4255 = !DILocation(line: 1139, column: 9, scope: !4247)
!4256 = !DILocation(line: 0, scope: !4197)
!4257 = !DILocation(line: 1141, column: 25, scope: !4258)
!4258 = distinct !DILexicalBlock(scope: !4259, file: !3, line: 1140, column: 39)
!4259 = distinct !DILexicalBlock(scope: !4260, file: !3, line: 1140, column: 9)
!4260 = distinct !DILexicalBlock(scope: !4197, file: !3, line: 1140, column: 9)
!4261 = !DILocation(line: 1141, column: 23, scope: !4258)
!4262 = !DILocation(line: 1140, column: 21, scope: !4259)
!4263 = !DILocation(line: 1140, column: 23, scope: !4259)
!4264 = !DILocation(line: 1140, column: 9, scope: !4260)
!4265 = distinct !{!4265, !4264, !4266, !312, !313}
!4266 = !DILocation(line: 1142, column: 9, scope: !4260)
!4267 = !DILocation(line: 1143, column: 46, scope: !4197)
!4268 = !DILocation(line: 0, scope: !99, inlinedAt: !4269)
!4269 = distinct !DILocation(line: 1143, column: 9, scope: !4197)
!4270 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !4269)
!4271 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4269)
!4272 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !4269)
!4273 = !DILocation(line: 0, scope: !99, inlinedAt: !4274)
!4274 = distinct !DILocation(line: 1146, column: 5, scope: !4190)
!4275 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4274)
!4276 = !DILocation(line: 1147, column: 1, scope: !4190)
!4277 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4199)
!4278 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4199)
!4279 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4199)
!4280 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4199)
!4281 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4199)
!4282 = distinct !DISubprogram(name: "test_phi_patterns", scope: !3, file: !3, line: 1153, type: !142, scopeLine: 1153, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4283)
!4283 = !{!4284, !4285, !4286, !4287, !4288, !4289, !4290, !4291, !4297, !4300, !4303}
!4284 = !DILocalVariable(name: "apdu", arg: 1, scope: !4282, file: !3, line: 1153, type: !102)
!4285 = !DILocalVariable(name: "buffer", arg: 2, scope: !4282, file: !3, line: 1153, type: !104)
!4286 = !DILocalVariable(name: "p1", arg: 3, scope: !4282, file: !3, line: 1153, type: !5)
!4287 = !DILocalVariable(name: "a", scope: !4282, file: !3, line: 1154, type: !8)
!4288 = !DILocalVariable(name: "b", scope: !4282, file: !3, line: 1155, type: !8)
!4289 = !DILocalVariable(name: "i", scope: !4282, file: !3, line: 1156, type: !8)
!4290 = !DILocalVariable(name: "sum", scope: !4282, file: !3, line: 1157, type: !8)
!4291 = !DILocalVariable(name: "tmp", scope: !4292, file: !3, line: 1172, type: !8)
!4292 = distinct !DILexicalBlock(scope: !4293, file: !3, line: 1171, column: 40)
!4293 = distinct !DILexicalBlock(scope: !4294, file: !3, line: 1171, column: 9)
!4294 = distinct !DILexicalBlock(scope: !4295, file: !3, line: 1171, column: 9)
!4295 = distinct !DILexicalBlock(scope: !4296, file: !3, line: 1168, column: 18)
!4296 = distinct !DILexicalBlock(scope: !4282, file: !3, line: 1168, column: 9)
!4297 = !DILocalVariable(name: "max", scope: !4298, file: !3, line: 1192, type: !8)
!4298 = distinct !DILexicalBlock(scope: !4299, file: !3, line: 1190, column: 18)
!4299 = distinct !DILexicalBlock(scope: !4282, file: !3, line: 1190, column: 9)
!4300 = !DILocalVariable(name: "sum1", scope: !4301, file: !3, line: 1215, type: !8)
!4301 = distinct !DILexicalBlock(scope: !4302, file: !3, line: 1213, column: 18)
!4302 = distinct !DILexicalBlock(scope: !4282, file: !3, line: 1213, column: 9)
!4303 = !DILocalVariable(name: "sum2", scope: !4301, file: !3, line: 1216, type: !8)
!4304 = !DILocation(line: 0, scope: !4282)
!4305 = !DILocation(line: 1159, column: 9, scope: !4282)
!4306 = !DILocation(line: 0, scope: !99, inlinedAt: !4307)
!4307 = distinct !DILocation(line: 1165, column: 9, scope: !4308)
!4308 = distinct !DILexicalBlock(scope: !4309, file: !3, line: 1159, column: 18)
!4309 = distinct !DILexicalBlock(scope: !4282, file: !3, line: 1159, column: 9)
!4310 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4307)
!4311 = !DILocation(line: 1166, column: 9, scope: !4308)
!4312 = !DILocation(line: 0, scope: !99, inlinedAt: !4313)
!4313 = distinct !DILocation(line: 1176, column: 9, scope: !4295)
!4314 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4313)
!4315 = !DILocation(line: 1177, column: 9, scope: !4295)
!4316 = !DILocation(line: 0, scope: !99, inlinedAt: !4317)
!4317 = distinct !DILocation(line: 1187, column: 9, scope: !4318)
!4318 = distinct !DILexicalBlock(scope: !4319, file: !3, line: 1179, column: 18)
!4319 = distinct !DILexicalBlock(scope: !4282, file: !3, line: 1179, column: 9)
!4320 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4317)
!4321 = !DILocation(line: 1188, column: 9, scope: !4318)
!4322 = !DILocation(line: 0, scope: !4298)
!4323 = !DILocation(line: 1193, column: 21, scope: !4298)
!4324 = !DILocation(line: 1193, column: 38, scope: !4298)
!4325 = !DILocation(line: 1193, column: 56, scope: !4298)
!4326 = !DILocation(line: 1193, column: 73, scope: !4298)
!4327 = !DILocation(line: 1194, column: 9, scope: !4328)
!4328 = distinct !DILexicalBlock(scope: !4298, file: !3, line: 1194, column: 9)
!4329 = !DILocation(line: 1195, column: 17, scope: !4330)
!4330 = distinct !DILexicalBlock(scope: !4331, file: !3, line: 1195, column: 17)
!4331 = distinct !DILexicalBlock(scope: !4332, file: !3, line: 1194, column: 39)
!4332 = distinct !DILexicalBlock(scope: !4328, file: !3, line: 1194, column: 9)
!4333 = !DILocation(line: 1195, column: 17, scope: !4331)
!4334 = !DILocation(line: 1194, column: 21, scope: !4332)
!4335 = !DILocation(line: 1194, column: 23, scope: !4332)
!4336 = distinct !{!4336, !4327, !4337, !312, !313}
!4337 = !DILocation(line: 1198, column: 9, scope: !4328)
!4338 = !DILocation(line: 0, scope: !99, inlinedAt: !4339)
!4339 = distinct !DILocation(line: 1199, column: 9, scope: !4298)
!4340 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4339)
!4341 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !4339)
!4342 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4339)
!4343 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !4339)
!4344 = !DILocation(line: 0, scope: !99, inlinedAt: !4345)
!4345 = distinct !DILocation(line: 1210, column: 9, scope: !4346)
!4346 = distinct !DILexicalBlock(scope: !4347, file: !3, line: 1202, column: 18)
!4347 = distinct !DILexicalBlock(scope: !4282, file: !3, line: 1202, column: 9)
!4348 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4345)
!4349 = !DILocation(line: 1211, column: 9, scope: !4346)
!4350 = !DILocation(line: 0, scope: !4301)
!4351 = !DILocation(line: 0, scope: !99, inlinedAt: !4352)
!4352 = distinct !DILocation(line: 1221, column: 9, scope: !4301)
!4353 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4352)
!4354 = !DILocation(line: 0, scope: !99, inlinedAt: !4355)
!4355 = distinct !DILocation(line: 1224, column: 5, scope: !4282)
!4356 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4355)
!4357 = !DILocation(line: 1225, column: 1, scope: !4282)
!4358 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4304)
!4359 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4304)
!4360 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4304)
!4361 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4304)
!4362 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4304)
!4363 = distinct !DISubprogram(name: "FixedMul", scope: !3, file: !3, line: 1231, type: !3558, scopeLine: 1231, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4364)
!4364 = !{!4365, !4366, !4367, !4368, !4369, !4370, !4371, !4372, !4373, !4374, !4375, !4376, !4377, !4378}
!4365 = !DILocalVariable(name: "a", arg: 1, scope: !4363, file: !3, line: 1231, type: !20)
!4366 = !DILocalVariable(name: "b", arg: 2, scope: !4363, file: !3, line: 1231, type: !20)
!4367 = !DILocalVariable(name: "ah", scope: !4363, file: !3, line: 1232, type: !8)
!4368 = !DILocalVariable(name: "bh", scope: !4363, file: !3, line: 1233, type: !8)
!4369 = !DILocalVariable(name: "al", scope: !4363, file: !3, line: 1234, type: !20)
!4370 = !DILocalVariable(name: "bl", scope: !4363, file: !3, line: 1235, type: !20)
!4371 = !DILocalVariable(name: "result", scope: !4363, file: !3, line: 1237, type: !20)
!4372 = !DILocalVariable(name: "al_hi", scope: !4363, file: !3, line: 1242, type: !20)
!4373 = !DILocalVariable(name: "al_lo", scope: !4363, file: !3, line: 1243, type: !20)
!4374 = !DILocalVariable(name: "bl_hi", scope: !4363, file: !3, line: 1244, type: !20)
!4375 = !DILocalVariable(name: "bl_lo", scope: !4363, file: !3, line: 1245, type: !20)
!4376 = !DILocalVariable(name: "mid", scope: !4363, file: !3, line: 1247, type: !20)
!4377 = !DILocalVariable(name: "low", scope: !4363, file: !3, line: 1248, type: !20)
!4378 = !DILocalVariable(name: "carry", scope: !4363, file: !3, line: 1249, type: !20)
!4379 = !DILocation(line: 0, scope: !4363)
!4380 = !DILocation(line: 1235, column: 16, scope: !4363)
!4381 = !DILocation(line: 1237, column: 19, scope: !4363)
!4382 = !DILocation(line: 1237, column: 24, scope: !4363)
!4383 = !DILocation(line: 1238, column: 26, scope: !4363)
!4384 = !DILocation(line: 1242, column: 21, scope: !4363)
!4385 = !DILocation(line: 1242, column: 27, scope: !4363)
!4386 = !DILocation(line: 1243, column: 20, scope: !4363)
!4387 = !DILocation(line: 1244, column: 21, scope: !4363)
!4388 = !DILocation(line: 1244, column: 27, scope: !4363)
!4389 = !DILocation(line: 1245, column: 20, scope: !4363)
!4390 = !DILocation(line: 1247, column: 21, scope: !4363)
!4391 = !DILocation(line: 1247, column: 37, scope: !4363)
!4392 = !DILocation(line: 1247, column: 29, scope: !4363)
!4393 = !DILocation(line: 1248, column: 21, scope: !4363)
!4394 = !DILocation(line: 1249, column: 24, scope: !4363)
!4395 = !DILocation(line: 1249, column: 39, scope: !4363)
!4396 = !DILocation(line: 1249, column: 32, scope: !4363)
!4397 = !DILocation(line: 1249, column: 46, scope: !4363)
!4398 = !DILocation(line: 1249, column: 17, scope: !4363)
!4399 = !DILocation(line: 1250, column: 29, scope: !4363)
!4400 = !DILocation(line: 1250, column: 44, scope: !4363)
!4401 = !DILocation(line: 1239, column: 21, scope: !4363)
!4402 = !DILocation(line: 1250, column: 21, scope: !4363)
!4403 = !DILocation(line: 1250, column: 37, scope: !4363)
!4404 = !DILocation(line: 1250, column: 50, scope: !4363)
!4405 = !DILocation(line: 1252, column: 5, scope: !4363)
!4406 = distinct !DISubprogram(name: "test_doom_math", scope: !3, file: !3, line: 1255, type: !142, scopeLine: 1255, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4407)
!4407 = !{!4408, !4409, !4410, !4411, !4412, !4413}
!4408 = !DILocalVariable(name: "apdu", arg: 1, scope: !4406, file: !3, line: 1255, type: !102)
!4409 = !DILocalVariable(name: "buffer", arg: 2, scope: !4406, file: !3, line: 1255, type: !104)
!4410 = !DILocalVariable(name: "p1", arg: 3, scope: !4406, file: !3, line: 1255, type: !5)
!4411 = !DILocalVariable(name: "a", scope: !4406, file: !3, line: 1256, type: !20)
!4412 = !DILocalVariable(name: "b", scope: !4406, file: !3, line: 1257, type: !20)
!4413 = !DILocalVariable(name: "r", scope: !4406, file: !3, line: 1258, type: !20)
!4414 = !DILocation(line: 0, scope: !4406)
!4415 = !DILocation(line: 1260, column: 9, scope: !4406)
!4416 = !DILocation(line: 0, scope: !99, inlinedAt: !4417)
!4417 = distinct !DILocation(line: 1273, column: 9, scope: !4418)
!4418 = distinct !DILexicalBlock(scope: !4419, file: !3, line: 1268, column: 18)
!4419 = distinct !DILexicalBlock(scope: !4406, file: !3, line: 1268, column: 9)
!4420 = !DILocation(line: 1274, column: 9, scope: !4418)
!4421 = !DILocation(line: 0, scope: !99, inlinedAt: !4422)
!4422 = distinct !DILocation(line: 1281, column: 9, scope: !4423)
!4423 = distinct !DILexicalBlock(scope: !4424, file: !3, line: 1276, column: 18)
!4424 = distinct !DILexicalBlock(scope: !4406, file: !3, line: 1276, column: 9)
!4425 = !DILocation(line: 1282, column: 9, scope: !4423)
!4426 = !DILocation(line: 0, scope: !99, inlinedAt: !4427)
!4427 = distinct !DILocation(line: 1289, column: 9, scope: !4428)
!4428 = distinct !DILexicalBlock(scope: !4429, file: !3, line: 1284, column: 18)
!4429 = distinct !DILexicalBlock(scope: !4406, file: !3, line: 1284, column: 9)
!4430 = !DILocation(line: 1290, column: 9, scope: !4428)
!4431 = !DILocation(line: 0, scope: !99, inlinedAt: !4432)
!4432 = distinct !DILocation(line: 1297, column: 9, scope: !4433)
!4433 = distinct !DILexicalBlock(scope: !4434, file: !3, line: 1292, column: 18)
!4434 = distinct !DILexicalBlock(scope: !4406, file: !3, line: 1292, column: 9)
!4435 = !DILocation(line: 1298, column: 9, scope: !4433)
!4436 = !DILocation(line: 0, scope: !99, inlinedAt: !4437)
!4437 = distinct !DILocation(line: 1300, column: 5, scope: !4406)
!4438 = !DILocation(line: 1301, column: 1, scope: !4406)
!4439 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4414)
!4440 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4414)
!4441 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4414)
!4442 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4414)
!4443 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4414)
!4444 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4414)
!4445 = distinct !DISubprogram(name: "test_memset", scope: !3, file: !3, line: 1307, type: !142, scopeLine: 1307, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4446)
!4446 = !{!4447, !4448, !4449, !4450, !4451}
!4447 = !DILocalVariable(name: "apdu", arg: 1, scope: !4445, file: !3, line: 1307, type: !102)
!4448 = !DILocalVariable(name: "buffer", arg: 2, scope: !4445, file: !3, line: 1307, type: !104)
!4449 = !DILocalVariable(name: "p1", arg: 3, scope: !4445, file: !3, line: 1307, type: !5)
!4450 = !DILocalVariable(name: "i", scope: !4445, file: !3, line: 1308, type: !8)
!4451 = !DILocalVariable(name: "ok", scope: !4452, file: !3, line: 1319, type: !8)
!4452 = distinct !DILexicalBlock(scope: !4453, file: !3, line: 1316, column: 18)
!4453 = distinct !DILexicalBlock(scope: !4445, file: !3, line: 1316, column: 9)
!4454 = !DILocation(line: 0, scope: !4445)
!4455 = !DILocation(line: 1310, column: 9, scope: !4445)
!4456 = !DILocation(line: 1312, column: 9, scope: !4457)
!4457 = distinct !DILexicalBlock(scope: !4458, file: !3, line: 1310, column: 18)
!4458 = distinct !DILexicalBlock(scope: !4445, file: !3, line: 1310, column: 9)
!4459 = !DILocation(line: 1313, column: 34, scope: !4457)
!4460 = !DILocation(line: 0, scope: !99, inlinedAt: !4461)
!4461 = distinct !DILocation(line: 1313, column: 9, scope: !4457)
!4462 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4461)
!4463 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4461)
!4464 = !DILocation(line: 1314, column: 9, scope: !4457)
!4465 = !DILocation(line: 1318, column: 9, scope: !4452)
!4466 = !DILocation(line: 0, scope: !4452)
!4467 = !DILocation(line: 1320, column: 9, scope: !4468)
!4468 = distinct !DILexicalBlock(scope: !4452, file: !3, line: 1320, column: 9)
!4469 = !DILocation(line: 1321, column: 17, scope: !4470)
!4470 = distinct !DILexicalBlock(scope: !4471, file: !3, line: 1321, column: 17)
!4471 = distinct !DILexicalBlock(scope: !4472, file: !3, line: 1320, column: 39)
!4472 = distinct !DILexicalBlock(scope: !4468, file: !3, line: 1320, column: 9)
!4473 = !DILocation(line: 1321, column: 28, scope: !4470)
!4474 = !DILocation(line: 1321, column: 17, scope: !4471)
!4475 = !DILocation(line: 1320, column: 21, scope: !4472)
!4476 = !DILocation(line: 1320, column: 23, scope: !4472)
!4477 = distinct !{!4477, !4467, !4478, !312, !313}
!4478 = !DILocation(line: 1322, column: 9, scope: !4468)
!4479 = !DILocation(line: 0, scope: !99, inlinedAt: !4480)
!4480 = distinct !DILocation(line: 1323, column: 9, scope: !4452)
!4481 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4480)
!4482 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !4480)
!4483 = !DILocation(line: 1328, column: 9, scope: !4484)
!4484 = distinct !DILexicalBlock(scope: !4485, file: !3, line: 1326, column: 18)
!4485 = distinct !DILexicalBlock(scope: !4445, file: !3, line: 1326, column: 9)
!4486 = !DILocation(line: 1329, column: 9, scope: !4484)
!4487 = !DILocation(line: 1330, column: 34, scope: !4484)
!4488 = !DILocation(line: 0, scope: !99, inlinedAt: !4489)
!4489 = distinct !DILocation(line: 1330, column: 9, scope: !4484)
!4490 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4489)
!4491 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4489)
!4492 = !DILocation(line: 1331, column: 9, scope: !4484)
!4493 = !DILocation(line: 1335, column: 9, scope: !4494)
!4494 = distinct !DILexicalBlock(scope: !4495, file: !3, line: 1333, column: 18)
!4495 = distinct !DILexicalBlock(scope: !4445, file: !3, line: 1333, column: 9)
!4496 = !DILocation(line: 1336, column: 9, scope: !4494)
!4497 = !DILocation(line: 1337, column: 34, scope: !4494)
!4498 = !DILocation(line: 0, scope: !99, inlinedAt: !4499)
!4499 = distinct !DILocation(line: 1337, column: 9, scope: !4494)
!4500 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4499)
!4501 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4499)
!4502 = !DILocation(line: 1338, column: 9, scope: !4494)
!4503 = !DILocation(line: 1342, column: 9, scope: !4504)
!4504 = distinct !DILexicalBlock(scope: !4505, file: !3, line: 1340, column: 18)
!4505 = distinct !DILexicalBlock(scope: !4445, file: !3, line: 1340, column: 9)
!4506 = !DILocation(line: 1343, column: 9, scope: !4504)
!4507 = !DILocation(line: 1344, column: 34, scope: !4504)
!4508 = !DILocation(line: 0, scope: !99, inlinedAt: !4509)
!4509 = distinct !DILocation(line: 1344, column: 9, scope: !4504)
!4510 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4509)
!4511 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4509)
!4512 = !DILocation(line: 1345, column: 9, scope: !4504)
!4513 = !DILocation(line: 1349, column: 9, scope: !4514)
!4514 = distinct !DILexicalBlock(scope: !4515, file: !3, line: 1347, column: 18)
!4515 = distinct !DILexicalBlock(scope: !4445, file: !3, line: 1347, column: 9)
!4516 = !DILocation(line: 1350, column: 9, scope: !4514)
!4517 = !DILocation(line: 1351, column: 34, scope: !4514)
!4518 = !DILocation(line: 0, scope: !99, inlinedAt: !4519)
!4519 = distinct !DILocation(line: 1351, column: 9, scope: !4514)
!4520 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4519)
!4521 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4519)
!4522 = !DILocation(line: 1352, column: 9, scope: !4514)
!4523 = !DILocation(line: 1356, column: 9, scope: !4524)
!4524 = distinct !DILexicalBlock(scope: !4525, file: !3, line: 1354, column: 18)
!4525 = distinct !DILexicalBlock(scope: !4445, file: !3, line: 1354, column: 9)
!4526 = !DILocation(line: 1357, column: 34, scope: !4524)
!4527 = !DILocation(line: 0, scope: !99, inlinedAt: !4528)
!4528 = distinct !DILocation(line: 1357, column: 9, scope: !4524)
!4529 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4528)
!4530 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4528)
!4531 = !DILocation(line: 1358, column: 9, scope: !4524)
!4532 = !DILocation(line: 1362, column: 9, scope: !4533)
!4533 = distinct !DILexicalBlock(scope: !4534, file: !3, line: 1360, column: 18)
!4534 = distinct !DILexicalBlock(scope: !4445, file: !3, line: 1360, column: 9)
!4535 = !DILocation(line: 1363, column: 34, scope: !4533)
!4536 = !DILocation(line: 0, scope: !99, inlinedAt: !4537)
!4537 = distinct !DILocation(line: 1363, column: 9, scope: !4533)
!4538 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !4537)
!4539 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4537)
!4540 = !DILocation(line: 1364, column: 9, scope: !4533)
!4541 = !DILocation(line: 0, scope: !99, inlinedAt: !4542)
!4542 = distinct !DILocation(line: 1366, column: 5, scope: !4445)
!4543 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4542)
!4544 = !DILocation(line: 1367, column: 1, scope: !4445)
!4545 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4454)
!4546 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4454)
!4547 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4454)
!4548 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4454)
!4549 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4454)
!4550 = distinct !DISubprogram(name: "test_shift_combinations", scope: !3, file: !3, line: 1375, type: !142, scopeLine: 1375, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4551)
!4551 = !{!4552, !4553, !4554, !4555, !4556, !4557, !4558}
!4552 = !DILocalVariable(name: "apdu", arg: 1, scope: !4550, file: !3, line: 1375, type: !102)
!4553 = !DILocalVariable(name: "buffer", arg: 2, scope: !4550, file: !3, line: 1375, type: !104)
!4554 = !DILocalVariable(name: "p1", arg: 3, scope: !4550, file: !3, line: 1375, type: !5)
!4555 = !DILocalVariable(name: "y", scope: !4550, file: !3, line: 1376, type: !8)
!4556 = !DILocalVariable(name: "x", scope: !4550, file: !3, line: 1377, type: !8)
!4557 = !DILocalVariable(name: "val", scope: !4550, file: !3, line: 1378, type: !8)
!4558 = !DILocalVariable(name: "b", scope: !4559, file: !3, line: 1389, type: !5)
!4559 = distinct !DILexicalBlock(scope: !4560, file: !3, line: 1387, column: 18)
!4560 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1387, column: 9)
!4561 = !DILocation(line: 0, scope: !4550)
!4562 = !DILocation(line: 1380, column: 9, scope: !4550)
!4563 = !DILocation(line: 0, scope: !99, inlinedAt: !4564)
!4564 = distinct !DILocation(line: 1381, column: 20, scope: !4565)
!4565 = distinct !DILexicalBlock(scope: !4566, file: !3, line: 1381, column: 18)
!4566 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1381, column: 9)
!4567 = !DILocation(line: 1381, column: 56, scope: !4565)
!4568 = !DILocation(line: 0, scope: !99, inlinedAt: !4569)
!4569 = distinct !DILocation(line: 1382, column: 20, scope: !4570)
!4570 = distinct !DILexicalBlock(scope: !4571, file: !3, line: 1382, column: 18)
!4571 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1382, column: 9)
!4572 = !DILocation(line: 1382, column: 58, scope: !4570)
!4573 = !DILocation(line: 0, scope: !99, inlinedAt: !4574)
!4574 = distinct !DILocation(line: 1383, column: 20, scope: !4575)
!4575 = distinct !DILexicalBlock(scope: !4576, file: !3, line: 1383, column: 18)
!4576 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1383, column: 9)
!4577 = !DILocation(line: 1383, column: 59, scope: !4575)
!4578 = !DILocation(line: 0, scope: !99, inlinedAt: !4579)
!4579 = distinct !DILocation(line: 1384, column: 20, scope: !4580)
!4580 = distinct !DILexicalBlock(scope: !4581, file: !3, line: 1384, column: 18)
!4581 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1384, column: 9)
!4582 = !DILocation(line: 1384, column: 59, scope: !4580)
!4583 = !DILocation(line: 0, scope: !99, inlinedAt: !4584)
!4584 = distinct !DILocation(line: 1385, column: 20, scope: !4585)
!4585 = distinct !DILexicalBlock(scope: !4586, file: !3, line: 1385, column: 18)
!4586 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1385, column: 9)
!4587 = !DILocation(line: 1385, column: 56, scope: !4585)
!4588 = !DILocation(line: 0, scope: !99, inlinedAt: !4589)
!4589 = distinct !DILocation(line: 1386, column: 20, scope: !4590)
!4590 = distinct !DILexicalBlock(scope: !4591, file: !3, line: 1386, column: 18)
!4591 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1386, column: 9)
!4592 = !DILocation(line: 1386, column: 57, scope: !4590)
!4593 = !DILocation(line: 0, scope: !4559)
!4594 = !DILocation(line: 0, scope: !99, inlinedAt: !4595)
!4595 = distinct !DILocation(line: 1390, column: 9, scope: !4559)
!4596 = !DILocation(line: 0, scope: !99, inlinedAt: !4597)
!4597 = distinct !DILocation(line: 1393, column: 20, scope: !4598)
!4598 = distinct !DILexicalBlock(scope: !4599, file: !3, line: 1393, column: 18)
!4599 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1393, column: 9)
!4600 = !DILocation(line: 1393, column: 66, scope: !4598)
!4601 = !DILocation(line: 0, scope: !99, inlinedAt: !4602)
!4602 = distinct !DILocation(line: 1394, column: 20, scope: !4603)
!4603 = distinct !DILexicalBlock(scope: !4604, file: !3, line: 1394, column: 18)
!4604 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1394, column: 9)
!4605 = !DILocation(line: 1394, column: 66, scope: !4603)
!4606 = !DILocation(line: 0, scope: !99, inlinedAt: !4607)
!4607 = distinct !DILocation(line: 1397, column: 9, scope: !4608)
!4608 = distinct !DILexicalBlock(scope: !4609, file: !3, line: 1395, column: 19)
!4609 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1395, column: 9)
!4610 = !DILocation(line: 1398, column: 9, scope: !4608)
!4611 = !DILocation(line: 0, scope: !99, inlinedAt: !4612)
!4612 = distinct !DILocation(line: 1402, column: 9, scope: !4613)
!4613 = distinct !DILexicalBlock(scope: !4614, file: !3, line: 1400, column: 19)
!4614 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1400, column: 9)
!4615 = !DILocation(line: 1403, column: 9, scope: !4613)
!4616 = !DILocation(line: 0, scope: !99, inlinedAt: !4617)
!4617 = distinct !DILocation(line: 1407, column: 9, scope: !4618)
!4618 = distinct !DILexicalBlock(scope: !4619, file: !3, line: 1405, column: 19)
!4619 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1405, column: 9)
!4620 = !DILocation(line: 1408, column: 9, scope: !4618)
!4621 = !DILocation(line: 0, scope: !99, inlinedAt: !4622)
!4622 = distinct !DILocation(line: 1413, column: 9, scope: !4623)
!4623 = distinct !DILexicalBlock(scope: !4624, file: !3, line: 1410, column: 19)
!4624 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1410, column: 9)
!4625 = !DILocation(line: 1414, column: 9, scope: !4623)
!4626 = !DILocation(line: 0, scope: !99, inlinedAt: !4627)
!4627 = distinct !DILocation(line: 1419, column: 9, scope: !4628)
!4628 = distinct !DILexicalBlock(scope: !4629, file: !3, line: 1416, column: 19)
!4629 = distinct !DILexicalBlock(scope: !4550, file: !3, line: 1416, column: 9)
!4630 = !DILocation(line: 1420, column: 9, scope: !4628)
!4631 = !DILocation(line: 0, scope: !99, inlinedAt: !4632)
!4632 = distinct !DILocation(line: 1422, column: 5, scope: !4550)
!4633 = !DILocation(line: 1423, column: 1, scope: !4550)
!4634 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4561)
!4635 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4561)
!4636 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4561)
!4637 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4561)
!4638 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4561)
!4639 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4561)
!4640 = distinct !DISubprogram(name: "test_pixel_masks", scope: !3, file: !3, line: 1429, type: !142, scopeLine: 1429, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4641)
!4641 = !{!4642, !4643, !4644, !4645, !4646}
!4642 = !DILocalVariable(name: "apdu", arg: 1, scope: !4640, file: !3, line: 1429, type: !102)
!4643 = !DILocalVariable(name: "buffer", arg: 2, scope: !4640, file: !3, line: 1429, type: !104)
!4644 = !DILocalVariable(name: "p1", arg: 3, scope: !4640, file: !3, line: 1429, type: !5)
!4645 = !DILocalVariable(name: "x", scope: !4640, file: !3, line: 1430, type: !8)
!4646 = !DILocalVariable(name: "y", scope: !4640, file: !3, line: 1431, type: !8)
!4647 = !DILocation(line: 0, scope: !4640)
!4648 = !DILocation(line: 1433, column: 9, scope: !4640)
!4649 = !DILocation(line: 0, scope: !99, inlinedAt: !4650)
!4650 = distinct !DILocation(line: 1434, column: 20, scope: !4651)
!4651 = distinct !DILexicalBlock(scope: !4652, file: !3, line: 1434, column: 18)
!4652 = distinct !DILexicalBlock(scope: !4640, file: !3, line: 1434, column: 9)
!4653 = !DILocation(line: 1434, column: 63, scope: !4651)
!4654 = !DILocation(line: 0, scope: !99, inlinedAt: !4655)
!4655 = distinct !DILocation(line: 1435, column: 20, scope: !4656)
!4656 = distinct !DILexicalBlock(scope: !4657, file: !3, line: 1435, column: 18)
!4657 = distinct !DILexicalBlock(scope: !4640, file: !3, line: 1435, column: 9)
!4658 = !DILocation(line: 1435, column: 63, scope: !4656)
!4659 = !DILocation(line: 0, scope: !99, inlinedAt: !4660)
!4660 = distinct !DILocation(line: 1437, column: 20, scope: !4661)
!4661 = distinct !DILexicalBlock(scope: !4662, file: !3, line: 1437, column: 18)
!4662 = distinct !DILexicalBlock(scope: !4640, file: !3, line: 1437, column: 9)
!4663 = !DILocation(line: 1437, column: 64, scope: !4661)
!4664 = !DILocation(line: 0, scope: !99, inlinedAt: !4665)
!4665 = distinct !DILocation(line: 1438, column: 20, scope: !4666)
!4666 = distinct !DILexicalBlock(scope: !4667, file: !3, line: 1438, column: 18)
!4667 = distinct !DILexicalBlock(scope: !4640, file: !3, line: 1438, column: 9)
!4668 = !DILocation(line: 1438, column: 67, scope: !4666)
!4669 = !DILocation(line: 0, scope: !99, inlinedAt: !4670)
!4670 = distinct !DILocation(line: 1441, column: 9, scope: !4671)
!4671 = distinct !DILexicalBlock(scope: !4672, file: !3, line: 1439, column: 18)
!4672 = distinct !DILexicalBlock(scope: !4640, file: !3, line: 1439, column: 9)
!4673 = !DILocation(line: 1442, column: 9, scope: !4671)
!4674 = !DILocation(line: 0, scope: !99, inlinedAt: !4675)
!4675 = distinct !DILocation(line: 1451, column: 9, scope: !4676)
!4676 = distinct !DILexicalBlock(scope: !4677, file: !3, line: 1449, column: 18)
!4677 = distinct !DILexicalBlock(scope: !4640, file: !3, line: 1449, column: 9)
!4678 = !DILocation(line: 1452, column: 9, scope: !4676)
!4679 = !DILocation(line: 0, scope: !99, inlinedAt: !4680)
!4680 = distinct !DILocation(line: 1454, column: 20, scope: !4681)
!4681 = distinct !DILexicalBlock(scope: !4682, file: !3, line: 1454, column: 18)
!4682 = distinct !DILexicalBlock(scope: !4640, file: !3, line: 1454, column: 9)
!4683 = !DILocation(line: 1454, column: 73, scope: !4681)
!4684 = !DILocation(line: 0, scope: !99, inlinedAt: !4685)
!4685 = distinct !DILocation(line: 1455, column: 21, scope: !4686)
!4686 = distinct !DILexicalBlock(scope: !4687, file: !3, line: 1455, column: 19)
!4687 = distinct !DILexicalBlock(scope: !4640, file: !3, line: 1455, column: 9)
!4688 = !DILocation(line: 1455, column: 83, scope: !4686)
!4689 = !DILocation(line: 0, scope: !99, inlinedAt: !4690)
!4690 = distinct !DILocation(line: 1457, column: 5, scope: !4640)
!4691 = !DILocation(line: 1458, column: 1, scope: !4640)
!4692 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4647)
!4693 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4647)
!4694 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4647)
!4695 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4647)
!4696 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4647)
!4697 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4647)
!4698 = distinct !DISubprogram(name: "test_fixed_point", scope: !3, file: !3, line: 1464, type: !142, scopeLine: 1464, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4699)
!4699 = !{!4700, !4701, !4702, !4703, !4704}
!4700 = !DILocalVariable(name: "apdu", arg: 1, scope: !4698, file: !3, line: 1464, type: !102)
!4701 = !DILocalVariable(name: "buffer", arg: 2, scope: !4698, file: !3, line: 1464, type: !104)
!4702 = !DILocalVariable(name: "p1", arg: 3, scope: !4698, file: !3, line: 1464, type: !5)
!4703 = !DILocalVariable(name: "val", scope: !4698, file: !3, line: 1465, type: !8)
!4704 = !DILocalVariable(name: "delta", scope: !4698, file: !3, line: 1466, type: !8)
!4705 = !DILocation(line: 0, scope: !4698)
!4706 = !DILocation(line: 1469, column: 9, scope: !4698)
!4707 = !DILocation(line: 0, scope: !99, inlinedAt: !4708)
!4708 = distinct !DILocation(line: 1472, column: 20, scope: !4709)
!4709 = distinct !DILexicalBlock(scope: !4710, file: !3, line: 1472, column: 18)
!4710 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1472, column: 9)
!4711 = !DILocation(line: 1472, column: 62, scope: !4709)
!4712 = !DILocation(line: 0, scope: !99, inlinedAt: !4713)
!4713 = distinct !DILocation(line: 1473, column: 20, scope: !4714)
!4714 = distinct !DILexicalBlock(scope: !4715, file: !3, line: 1473, column: 18)
!4715 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1473, column: 9)
!4716 = !DILocation(line: 1473, column: 70, scope: !4714)
!4717 = !DILocation(line: 0, scope: !99, inlinedAt: !4718)
!4718 = distinct !DILocation(line: 1474, column: 20, scope: !4719)
!4719 = distinct !DILexicalBlock(scope: !4720, file: !3, line: 1474, column: 18)
!4720 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1474, column: 9)
!4721 = !DILocation(line: 1474, column: 61, scope: !4719)
!4722 = !DILocation(line: 0, scope: !99, inlinedAt: !4723)
!4723 = distinct !DILocation(line: 1475, column: 20, scope: !4724)
!4724 = distinct !DILexicalBlock(scope: !4725, file: !3, line: 1475, column: 18)
!4725 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1475, column: 9)
!4726 = !DILocation(line: 1475, column: 72, scope: !4724)
!4727 = !DILocation(line: 0, scope: !99, inlinedAt: !4728)
!4728 = distinct !DILocation(line: 1476, column: 20, scope: !4729)
!4729 = distinct !DILexicalBlock(scope: !4730, file: !3, line: 1476, column: 18)
!4730 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1476, column: 9)
!4731 = !DILocation(line: 1476, column: 70, scope: !4729)
!4732 = !DILocation(line: 0, scope: !99, inlinedAt: !4733)
!4733 = distinct !DILocation(line: 1477, column: 20, scope: !4734)
!4734 = distinct !DILexicalBlock(scope: !4735, file: !3, line: 1477, column: 18)
!4735 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1477, column: 9)
!4736 = !DILocation(line: 1477, column: 64, scope: !4734)
!4737 = !DILocation(line: 0, scope: !99, inlinedAt: !4738)
!4738 = distinct !DILocation(line: 1480, column: 9, scope: !4739)
!4739 = distinct !DILexicalBlock(scope: !4740, file: !3, line: 1478, column: 18)
!4740 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1478, column: 9)
!4741 = !DILocation(line: 1481, column: 9, scope: !4739)
!4742 = !DILocation(line: 0, scope: !99, inlinedAt: !4743)
!4743 = distinct !DILocation(line: 1485, column: 9, scope: !4744)
!4744 = distinct !DILexicalBlock(scope: !4745, file: !3, line: 1483, column: 19)
!4745 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1483, column: 9)
!4746 = !DILocation(line: 1486, column: 9, scope: !4744)
!4747 = !DILocation(line: 0, scope: !99, inlinedAt: !4748)
!4748 = distinct !DILocation(line: 1488, column: 21, scope: !4749)
!4749 = distinct !DILexicalBlock(scope: !4750, file: !3, line: 1488, column: 19)
!4750 = distinct !DILexicalBlock(scope: !4698, file: !3, line: 1488, column: 9)
!4751 = !DILocation(line: 1488, column: 61, scope: !4749)
!4752 = !DILocation(line: 0, scope: !99, inlinedAt: !4753)
!4753 = distinct !DILocation(line: 1489, column: 5, scope: !4698)
!4754 = !DILocation(line: 1490, column: 1, scope: !4698)
!4755 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4705)
!4756 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4705)
!4757 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4705)
!4758 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4705)
!4759 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4705)
!4760 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4705)
!4761 = distinct !DISubprogram(name: "test_byte_array_index", scope: !3, file: !3, line: 1496, type: !142, scopeLine: 1496, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4762)
!4762 = !{!4763, !4764, !4765, !4766, !4767, !4768, !4769, !4770}
!4763 = !DILocalVariable(name: "apdu", arg: 1, scope: !4761, file: !3, line: 1496, type: !102)
!4764 = !DILocalVariable(name: "buffer", arg: 2, scope: !4761, file: !3, line: 1496, type: !104)
!4765 = !DILocalVariable(name: "p1", arg: 3, scope: !4761, file: !3, line: 1496, type: !5)
!4766 = !DILocalVariable(name: "y", scope: !4761, file: !3, line: 1499, type: !8)
!4767 = !DILocalVariable(name: "x", scope: !4761, file: !3, line: 1500, type: !8)
!4768 = !DILocalVariable(name: "base", scope: !4761, file: !3, line: 1501, type: !8)
!4769 = !DILocalVariable(name: "offset", scope: !4761, file: !3, line: 1502, type: !8)
!4770 = !DILocalVariable(name: "row", scope: !4771, file: !3, line: 1531, type: !8)
!4771 = distinct !DILexicalBlock(scope: !4772, file: !3, line: 1528, column: 18)
!4772 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1528, column: 9)
!4773 = !DILocation(line: 0, scope: !4761)
!4774 = !DILocation(line: 1504, column: 9, scope: !4761)
!4775 = !DILocation(line: 0, scope: !99, inlinedAt: !4776)
!4776 = distinct !DILocation(line: 1505, column: 20, scope: !4777)
!4777 = distinct !DILexicalBlock(scope: !4778, file: !3, line: 1505, column: 18)
!4778 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1505, column: 9)
!4779 = !DILocation(line: 1505, column: 68, scope: !4777)
!4780 = !DILocation(line: 0, scope: !99, inlinedAt: !4781)
!4781 = distinct !DILocation(line: 1506, column: 20, scope: !4782)
!4782 = distinct !DILexicalBlock(scope: !4783, file: !3, line: 1506, column: 18)
!4783 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1506, column: 9)
!4784 = !DILocation(line: 1506, column: 68, scope: !4782)
!4785 = !DILocation(line: 0, scope: !99, inlinedAt: !4786)
!4786 = distinct !DILocation(line: 1507, column: 20, scope: !4787)
!4787 = distinct !DILexicalBlock(scope: !4788, file: !3, line: 1507, column: 18)
!4788 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1507, column: 9)
!4789 = !DILocation(line: 1507, column: 69, scope: !4787)
!4790 = !DILocation(line: 0, scope: !99, inlinedAt: !4791)
!4791 = distinct !DILocation(line: 1508, column: 20, scope: !4792)
!4792 = distinct !DILexicalBlock(scope: !4793, file: !3, line: 1508, column: 18)
!4793 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1508, column: 9)
!4794 = !DILocation(line: 1508, column: 69, scope: !4792)
!4795 = !DILocation(line: 0, scope: !99, inlinedAt: !4796)
!4796 = distinct !DILocation(line: 1511, column: 9, scope: !4797)
!4797 = distinct !DILexicalBlock(scope: !4798, file: !3, line: 1509, column: 18)
!4798 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1509, column: 9)
!4799 = !DILocation(line: 1512, column: 9, scope: !4797)
!4800 = !DILocation(line: 1517, column: 38, scope: !4801)
!4801 = distinct !DILexicalBlock(scope: !4802, file: !3, line: 1514, column: 18)
!4802 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1514, column: 9)
!4803 = !DILocation(line: 0, scope: !99, inlinedAt: !4804)
!4804 = distinct !DILocation(line: 1518, column: 9, scope: !4801)
!4805 = !DILocation(line: 1519, column: 9, scope: !4801)
!4806 = !DILocation(line: 1523, column: 20, scope: !4807)
!4807 = distinct !DILexicalBlock(scope: !4808, file: !3, line: 1521, column: 18)
!4808 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1521, column: 9)
!4809 = !DILocation(line: 1524, column: 20, scope: !4807)
!4810 = !DILocation(line: 0, scope: !99, inlinedAt: !4811)
!4811 = distinct !DILocation(line: 1525, column: 9, scope: !4807)
!4812 = !DILocation(line: 1526, column: 9, scope: !4807)
!4813 = !DILocation(line: 0, scope: !4771)
!4814 = !DILocation(line: 0, scope: !99, inlinedAt: !4815)
!4815 = distinct !DILocation(line: 1532, column: 9, scope: !4771)
!4816 = !DILocation(line: 0, scope: !99, inlinedAt: !4817)
!4817 = distinct !DILocation(line: 1538, column: 9, scope: !4818)
!4818 = distinct !DILexicalBlock(scope: !4819, file: !3, line: 1535, column: 18)
!4819 = distinct !DILexicalBlock(scope: !4761, file: !3, line: 1535, column: 9)
!4820 = !DILocation(line: 1539, column: 9, scope: !4818)
!4821 = !DILocation(line: 0, scope: !99, inlinedAt: !4822)
!4822 = distinct !DILocation(line: 1541, column: 5, scope: !4761)
!4823 = !DILocation(line: 1542, column: 1, scope: !4761)
!4824 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4773)
!4825 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4773)
!4826 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4773)
!4827 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4773)
!4828 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4773)
!4829 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4773)
!4830 = distinct !DISubprogram(name: "test_bitwise_rmw", scope: !3, file: !3, line: 1548, type: !142, scopeLine: 1548, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4831)
!4831 = !{!4832, !4833, !4834, !4835, !4836, !4837, !4840}
!4832 = !DILocalVariable(name: "apdu", arg: 1, scope: !4830, file: !3, line: 1548, type: !102)
!4833 = !DILocalVariable(name: "buffer", arg: 2, scope: !4830, file: !3, line: 1548, type: !104)
!4834 = !DILocalVariable(name: "p1", arg: 3, scope: !4830, file: !3, line: 1548, type: !5)
!4835 = !DILocalVariable(name: "i", scope: !4830, file: !3, line: 1549, type: !8)
!4836 = !DILocalVariable(name: "bit", scope: !4830, file: !3, line: 1550, type: !8)
!4837 = !DILocalVariable(name: "tmp", scope: !4838, file: !3, line: 1633, type: !5)
!4838 = distinct !DILexicalBlock(scope: !4839, file: !3, line: 1630, column: 19)
!4839 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1630, column: 9)
!4840 = !DILocalVariable(name: "tmp", scope: !4841, file: !3, line: 1640, type: !5)
!4841 = distinct !DILexicalBlock(scope: !4842, file: !3, line: 1637, column: 19)
!4842 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1637, column: 9)
!4843 = !DILocation(line: 0, scope: !4830)
!4844 = !DILocation(line: 1552, column: 9, scope: !4830)
!4845 = !DILocation(line: 1554, column: 20, scope: !4846)
!4846 = distinct !DILexicalBlock(scope: !4847, file: !3, line: 1552, column: 18)
!4847 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1552, column: 9)
!4848 = !DILocation(line: 0, scope: !99, inlinedAt: !4849)
!4849 = distinct !DILocation(line: 1555, column: 9, scope: !4846)
!4850 = !DILocation(line: 1556, column: 9, scope: !4846)
!4851 = !DILocation(line: 1560, column: 20, scope: !4852)
!4852 = distinct !DILexicalBlock(scope: !4853, file: !3, line: 1558, column: 18)
!4853 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1558, column: 9)
!4854 = !DILocation(line: 0, scope: !99, inlinedAt: !4855)
!4855 = distinct !DILocation(line: 1561, column: 9, scope: !4852)
!4856 = !DILocation(line: 1562, column: 9, scope: !4852)
!4857 = !DILocation(line: 1566, column: 20, scope: !4858)
!4858 = distinct !DILexicalBlock(scope: !4859, file: !3, line: 1564, column: 18)
!4859 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1564, column: 9)
!4860 = !DILocation(line: 0, scope: !99, inlinedAt: !4861)
!4861 = distinct !DILocation(line: 1567, column: 9, scope: !4858)
!4862 = !DILocation(line: 1568, column: 9, scope: !4858)
!4863 = !DILocation(line: 1573, column: 20, scope: !4864)
!4864 = distinct !DILexicalBlock(scope: !4865, file: !3, line: 1570, column: 18)
!4865 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1570, column: 9)
!4866 = !DILocation(line: 0, scope: !99, inlinedAt: !4867)
!4867 = distinct !DILocation(line: 1574, column: 9, scope: !4864)
!4868 = !DILocation(line: 1575, column: 9, scope: !4864)
!4869 = !DILocation(line: 1579, column: 20, scope: !4870)
!4870 = distinct !DILexicalBlock(scope: !4871, file: !3, line: 1577, column: 18)
!4871 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1577, column: 9)
!4872 = !DILocation(line: 0, scope: !99, inlinedAt: !4873)
!4873 = distinct !DILocation(line: 1580, column: 9, scope: !4870)
!4874 = !DILocation(line: 1581, column: 9, scope: !4870)
!4875 = !DILocation(line: 1585, column: 20, scope: !4876)
!4876 = distinct !DILexicalBlock(scope: !4877, file: !3, line: 1583, column: 18)
!4877 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1583, column: 9)
!4878 = !DILocation(line: 0, scope: !99, inlinedAt: !4879)
!4879 = distinct !DILocation(line: 1586, column: 9, scope: !4876)
!4880 = !DILocation(line: 1587, column: 9, scope: !4876)
!4881 = !DILocation(line: 1593, column: 20, scope: !4882)
!4882 = distinct !DILexicalBlock(scope: !4883, file: !3, line: 1589, column: 18)
!4883 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1589, column: 9)
!4884 = !DILocation(line: 0, scope: !99, inlinedAt: !4885)
!4885 = distinct !DILocation(line: 1594, column: 9, scope: !4882)
!4886 = !DILocation(line: 1595, column: 9, scope: !4882)
!4887 = !DILocation(line: 1601, column: 20, scope: !4888)
!4888 = distinct !DILexicalBlock(scope: !4889, file: !3, line: 1597, column: 18)
!4889 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1597, column: 9)
!4890 = !DILocation(line: 0, scope: !99, inlinedAt: !4891)
!4891 = distinct !DILocation(line: 1602, column: 9, scope: !4888)
!4892 = !DILocation(line: 1603, column: 9, scope: !4888)
!4893 = !DILocation(line: 1608, column: 20, scope: !4894)
!4894 = distinct !DILexicalBlock(scope: !4895, file: !3, line: 1605, column: 18)
!4895 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1605, column: 9)
!4896 = !DILocation(line: 0, scope: !99, inlinedAt: !4897)
!4897 = distinct !DILocation(line: 1609, column: 9, scope: !4894)
!4898 = !DILocation(line: 1612, column: 9, scope: !4894)
!4899 = !DILocation(line: 1618, column: 24, scope: !4900)
!4900 = distinct !DILexicalBlock(scope: !4901, file: !3, line: 1617, column: 39)
!4901 = distinct !DILexicalBlock(scope: !4902, file: !3, line: 1617, column: 9)
!4902 = distinct !DILexicalBlock(scope: !4903, file: !3, line: 1617, column: 9)
!4903 = distinct !DILexicalBlock(scope: !4904, file: !3, line: 1614, column: 18)
!4904 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1614, column: 9)
!4905 = !DILocation(line: 0, scope: !99, inlinedAt: !4906)
!4906 = distinct !DILocation(line: 1620, column: 9, scope: !4903)
!4907 = !DILocation(line: 1621, column: 9, scope: !4903)
!4908 = !DILocation(line: 1626, column: 20, scope: !4909)
!4909 = distinct !DILexicalBlock(scope: !4910, file: !3, line: 1623, column: 19)
!4910 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1623, column: 9)
!4911 = !DILocation(line: 0, scope: !99, inlinedAt: !4912)
!4912 = distinct !DILocation(line: 1627, column: 9, scope: !4909)
!4913 = !DILocation(line: 1628, column: 9, scope: !4909)
!4914 = !DILocation(line: 1632, column: 20, scope: !4838)
!4915 = !DILocation(line: 0, scope: !4838)
!4916 = !DILocation(line: 0, scope: !99, inlinedAt: !4917)
!4917 = distinct !DILocation(line: 1634, column: 9, scope: !4838)
!4918 = !DILocation(line: 1639, column: 20, scope: !4841)
!4919 = !DILocation(line: 0, scope: !4841)
!4920 = !DILocation(line: 0, scope: !99, inlinedAt: !4921)
!4921 = distinct !DILocation(line: 1641, column: 9, scope: !4841)
!4922 = !DILocation(line: 1646, column: 20, scope: !4923)
!4923 = distinct !DILexicalBlock(scope: !4924, file: !3, line: 1644, column: 19)
!4924 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1644, column: 9)
!4925 = !DILocation(line: 1647, column: 20, scope: !4923)
!4926 = !DILocation(line: 1648, column: 20, scope: !4923)
!4927 = !DILocation(line: 1649, column: 20, scope: !4923)
!4928 = !DILocation(line: 0, scope: !99, inlinedAt: !4929)
!4929 = distinct !DILocation(line: 1650, column: 9, scope: !4923)
!4930 = !DILocation(line: 1651, column: 9, scope: !4923)
!4931 = !DILocation(line: 1655, column: 20, scope: !4932)
!4932 = distinct !DILexicalBlock(scope: !4933, file: !3, line: 1653, column: 19)
!4933 = distinct !DILexicalBlock(scope: !4830, file: !3, line: 1653, column: 9)
!4934 = !DILocation(line: 1656, column: 20, scope: !4932)
!4935 = !DILocation(line: 1657, column: 20, scope: !4932)
!4936 = !DILocation(line: 1658, column: 20, scope: !4932)
!4937 = !DILocation(line: 0, scope: !99, inlinedAt: !4938)
!4938 = distinct !DILocation(line: 1659, column: 9, scope: !4932)
!4939 = !DILocation(line: 1660, column: 9, scope: !4932)
!4940 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4843)
!4941 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4843)
!4942 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4843)
!4943 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4843)
!4944 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4843)
!4945 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4843)
!4946 = !DILocation(line: 1663, column: 1, scope: !4830)
!4947 = distinct !DISubprogram(name: "test_signed_shifts", scope: !3, file: !3, line: 1669, type: !142, scopeLine: 1669, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !4948)
!4948 = !{!4949, !4950, !4951, !4952, !4953, !4954}
!4949 = !DILocalVariable(name: "apdu", arg: 1, scope: !4947, file: !3, line: 1669, type: !102)
!4950 = !DILocalVariable(name: "buffer", arg: 2, scope: !4947, file: !3, line: 1669, type: !104)
!4951 = !DILocalVariable(name: "p1", arg: 3, scope: !4947, file: !3, line: 1669, type: !5)
!4952 = !DILocalVariable(name: "s", scope: !4947, file: !3, line: 1670, type: !8)
!4953 = !DILocalVariable(name: "i", scope: !4947, file: !3, line: 1671, type: !20)
!4954 = !DILocalVariable(name: "b", scope: !4947, file: !3, line: 1672, type: !5)
!4955 = !DILocation(line: 0, scope: !4947)
!4956 = !DILocation(line: 1674, column: 9, scope: !4947)
!4957 = !DILocation(line: 0, scope: !99, inlinedAt: !4958)
!4958 = distinct !DILocation(line: 1674, column: 28, scope: !4959)
!4959 = distinct !DILexicalBlock(scope: !4960, file: !3, line: 1674, column: 18)
!4960 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1674, column: 9)
!4961 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4958)
!4962 = !DILocation(line: 1674, column: 62, scope: !4959)
!4963 = !DILocation(line: 0, scope: !99, inlinedAt: !4964)
!4964 = distinct !DILocation(line: 1675, column: 28, scope: !4965)
!4965 = distinct !DILexicalBlock(scope: !4966, file: !3, line: 1675, column: 18)
!4966 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1675, column: 9)
!4967 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4964)
!4968 = !DILocation(line: 1675, column: 73, scope: !4965)
!4969 = !DILocation(line: 0, scope: !99, inlinedAt: !4970)
!4970 = distinct !DILocation(line: 1676, column: 30, scope: !4971)
!4971 = distinct !DILexicalBlock(scope: !4972, file: !3, line: 1676, column: 18)
!4972 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1676, column: 9)
!4973 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4970)
!4974 = !DILocation(line: 1676, column: 64, scope: !4971)
!4975 = !DILocation(line: 0, scope: !99, inlinedAt: !4976)
!4976 = distinct !DILocation(line: 1680, column: 9, scope: !4977)
!4977 = distinct !DILexicalBlock(scope: !4978, file: !3, line: 1677, column: 18)
!4978 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1677, column: 9)
!4979 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4976)
!4980 = !DILocation(line: 1681, column: 9, scope: !4977)
!4981 = !DILocation(line: 0, scope: !99, inlinedAt: !4982)
!4982 = distinct !DILocation(line: 1683, column: 28, scope: !4983)
!4983 = distinct !DILexicalBlock(scope: !4984, file: !3, line: 1683, column: 18)
!4984 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1683, column: 9)
!4985 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4982)
!4986 = !DILocation(line: 1683, column: 63, scope: !4983)
!4987 = !DILocation(line: 1687, column: 41, scope: !4988)
!4988 = distinct !DILexicalBlock(scope: !4989, file: !3, line: 1684, column: 18)
!4989 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1684, column: 9)
!4990 = !DILocation(line: 0, scope: !99, inlinedAt: !4991)
!4991 = distinct !DILocation(line: 1687, column: 9, scope: !4988)
!4992 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !4991)
!4993 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4991)
!4994 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !4991)
!4995 = !DILocation(line: 1688, column: 9, scope: !4988)
!4996 = !DILocation(line: 0, scope: !99, inlinedAt: !4997)
!4997 = distinct !DILocation(line: 1693, column: 9, scope: !4998)
!4998 = distinct !DILexicalBlock(scope: !4999, file: !3, line: 1690, column: 18)
!4999 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1690, column: 9)
!5000 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !4997)
!5001 = !DILocation(line: 1694, column: 9, scope: !4998)
!5002 = !DILocation(line: 0, scope: !99, inlinedAt: !5003)
!5003 = distinct !DILocation(line: 1699, column: 9, scope: !5004)
!5004 = distinct !DILexicalBlock(scope: !5005, file: !3, line: 1696, column: 18)
!5005 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1696, column: 9)
!5006 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5003)
!5007 = !DILocation(line: 1700, column: 9, scope: !5004)
!5008 = !DILocation(line: 0, scope: !99, inlinedAt: !5009)
!5009 = distinct !DILocation(line: 1705, column: 9, scope: !5010)
!5010 = distinct !DILexicalBlock(scope: !5011, file: !3, line: 1702, column: 18)
!5011 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1702, column: 9)
!5012 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5009)
!5013 = !DILocation(line: 1706, column: 9, scope: !5010)
!5014 = !DILocation(line: 0, scope: !99, inlinedAt: !5015)
!5015 = distinct !DILocation(line: 1711, column: 9, scope: !5016)
!5016 = distinct !DILexicalBlock(scope: !5017, file: !3, line: 1708, column: 18)
!5017 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1708, column: 9)
!5018 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5015)
!5019 = !DILocation(line: 1712, column: 9, scope: !5016)
!5020 = !DILocation(line: 0, scope: !99, inlinedAt: !5021)
!5021 = distinct !DILocation(line: 1717, column: 9, scope: !5022)
!5022 = distinct !DILexicalBlock(scope: !5023, file: !3, line: 1714, column: 19)
!5023 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1714, column: 9)
!5024 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5021)
!5025 = !DILocation(line: 1718, column: 9, scope: !5022)
!5026 = !DILocation(line: 1723, column: 42, scope: !5027)
!5027 = distinct !DILexicalBlock(scope: !5028, file: !3, line: 1720, column: 19)
!5028 = distinct !DILexicalBlock(scope: !4947, file: !3, line: 1720, column: 9)
!5029 = !DILocation(line: 1723, column: 57, scope: !5027)
!5030 = !DILocation(line: 0, scope: !99, inlinedAt: !5031)
!5031 = distinct !DILocation(line: 1723, column: 9, scope: !5027)
!5032 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !5031)
!5033 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5031)
!5034 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !5031)
!5035 = !DILocation(line: 1724, column: 9, scope: !5027)
!5036 = !DILocation(line: 0, scope: !99, inlinedAt: !5037)
!5037 = distinct !DILocation(line: 1726, column: 5, scope: !4947)
!5038 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5037)
!5039 = !DILocation(line: 1727, column: 1, scope: !4947)
!5040 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !4955)
!5041 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !4955)
!5042 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !4955)
!5043 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !4955)
!5044 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !4955)
!5045 = distinct !DISubprogram(name: "test_struct_arrays", scope: !3, file: !3, line: 1753, type: !142, scopeLine: 1753, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5046)
!5046 = !{!5047, !5048, !5049, !5050, !5051, !5052, !5055, !5058}
!5047 = !DILocalVariable(name: "apdu", arg: 1, scope: !5045, file: !3, line: 1753, type: !102)
!5048 = !DILocalVariable(name: "buffer", arg: 2, scope: !5045, file: !3, line: 1753, type: !104)
!5049 = !DILocalVariable(name: "p1", arg: 3, scope: !5045, file: !3, line: 1753, type: !5)
!5050 = !DILocalVariable(name: "i", scope: !5045, file: !3, line: 1754, type: !8)
!5051 = !DILocalVariable(name: "sum", scope: !5045, file: !3, line: 1755, type: !8)
!5052 = !DILocalVariable(name: "found", scope: !5053, file: !3, line: 1798, type: !8)
!5053 = distinct !DILexicalBlock(scope: !5054, file: !3, line: 1793, column: 18)
!5054 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1793, column: 9)
!5055 = !DILocalVariable(name: "tx", scope: !5056, file: !3, line: 1831, type: !8)
!5056 = distinct !DILexicalBlock(scope: !5057, file: !3, line: 1827, column: 18)
!5057 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1827, column: 9)
!5058 = !DILocalVariable(name: "ty", scope: !5056, file: !3, line: 1831, type: !8)
!5059 = !DILocation(line: 0, scope: !5045)
!5060 = !DILocation(line: 1757, column: 9, scope: !5045)
!5061 = !DILocation(line: 1758, column: 20, scope: !5062)
!5062 = distinct !DILexicalBlock(scope: !5063, file: !3, line: 1757, column: 18)
!5063 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1757, column: 9)
!5064 = !{!5065, !666, i64 0}
!5065 = !{!"point_s", !666, i64 0, !666, i64 2}
!5066 = !DILocation(line: 0, scope: !99, inlinedAt: !5067)
!5067 = distinct !DILocation(line: 1759, column: 9, scope: !5062)
!5068 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5067)
!5069 = !DILocation(line: 1760, column: 9, scope: !5062)
!5070 = !DILocation(line: 1763, column: 20, scope: !5071)
!5071 = distinct !DILexicalBlock(scope: !5072, file: !3, line: 1762, column: 18)
!5072 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1762, column: 9)
!5073 = !DILocation(line: 1764, column: 20, scope: !5071)
!5074 = !{!5065, !666, i64 2}
!5075 = !DILocation(line: 0, scope: !99, inlinedAt: !5076)
!5076 = distinct !DILocation(line: 1765, column: 9, scope: !5071)
!5077 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5076)
!5078 = !DILocation(line: 1766, column: 9, scope: !5071)
!5079 = !DILocation(line: 1769, column: 20, scope: !5080)
!5080 = distinct !DILexicalBlock(scope: !5081, file: !3, line: 1768, column: 18)
!5081 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1768, column: 9)
!5082 = !DILocation(line: 1770, column: 20, scope: !5080)
!5083 = !DILocation(line: 0, scope: !99, inlinedAt: !5084)
!5084 = distinct !DILocation(line: 1771, column: 9, scope: !5080)
!5085 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5084)
!5086 = !DILocation(line: 1772, column: 9, scope: !5080)
!5087 = !DILocation(line: 1777, column: 26, scope: !5088)
!5088 = distinct !DILexicalBlock(scope: !5089, file: !3, line: 1776, column: 39)
!5089 = distinct !DILexicalBlock(scope: !5090, file: !3, line: 1776, column: 9)
!5090 = distinct !DILexicalBlock(scope: !5091, file: !3, line: 1776, column: 9)
!5091 = distinct !DILexicalBlock(scope: !5092, file: !3, line: 1774, column: 18)
!5092 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1774, column: 9)
!5093 = !DILocation(line: 1777, column: 13, scope: !5088)
!5094 = !DILocation(line: 1777, column: 24, scope: !5088)
!5095 = !DILocation(line: 1776, column: 34, scope: !5089)
!5096 = !DILocation(line: 1776, column: 21, scope: !5089)
!5097 = !DILocation(line: 1776, column: 23, scope: !5089)
!5098 = !DILocation(line: 1776, column: 9, scope: !5090)
!5099 = distinct !{!5099, !5098, !5100, !312, !313}
!5100 = !DILocation(line: 1778, column: 9, scope: !5090)
!5101 = !DILocation(line: 1779, column: 43, scope: !5091)
!5102 = !DILocation(line: 0, scope: !99, inlinedAt: !5103)
!5103 = distinct !DILocation(line: 1779, column: 9, scope: !5091)
!5104 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !5103)
!5105 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !5103)
!5106 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5103)
!5107 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !5103)
!5108 = !DILocation(line: 1780, column: 9, scope: !5091)
!5109 = !DILocation(line: 1783, column: 22, scope: !5110)
!5110 = distinct !DILexicalBlock(scope: !5111, file: !3, line: 1782, column: 18)
!5111 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1782, column: 9)
!5112 = !{!5113, !666, i64 0}
!5113 = !{!"pipe_s", !666, i64 0, !666, i64 2, !114, i64 4, !114, i64 5}
!5114 = !DILocation(line: 1784, column: 26, scope: !5110)
!5115 = !{!5113, !666, i64 2}
!5116 = !DILocation(line: 0, scope: !99, inlinedAt: !5117)
!5117 = distinct !DILocation(line: 1785, column: 9, scope: !5110)
!5118 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5117)
!5119 = !DILocation(line: 1786, column: 9, scope: !5110)
!5120 = !DILocation(line: 1789, column: 27, scope: !5121)
!5121 = distinct !DILexicalBlock(scope: !5122, file: !3, line: 1788, column: 18)
!5122 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1788, column: 9)
!5123 = !{!5113, !114, i64 4}
!5124 = !DILocation(line: 0, scope: !99, inlinedAt: !5125)
!5125 = distinct !DILocation(line: 1790, column: 9, scope: !5121)
!5126 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5125)
!5127 = !DILocation(line: 1791, column: 9, scope: !5121)
!5128 = !DILocation(line: 1795, column: 27, scope: !5053)
!5129 = !DILocation(line: 1796, column: 27, scope: !5053)
!5130 = !DILocation(line: 1797, column: 27, scope: !5053)
!5131 = !DILocation(line: 0, scope: !5053)
!5132 = !DILocation(line: 1799, column: 9, scope: !5133)
!5133 = distinct !DILexicalBlock(scope: !5053, file: !3, line: 1799, column: 9)
!5134 = !DILocation(line: 1800, column: 28, scope: !5135)
!5135 = distinct !DILexicalBlock(scope: !5136, file: !3, line: 1800, column: 17)
!5136 = distinct !DILexicalBlock(scope: !5137, file: !3, line: 1799, column: 39)
!5137 = distinct !DILexicalBlock(scope: !5133, file: !3, line: 1799, column: 9)
!5138 = !DILocation(line: 1800, column: 35, scope: !5135)
!5139 = !DILocation(line: 1800, column: 40, scope: !5135)
!5140 = !DILocation(line: 1799, column: 34, scope: !5137)
!5141 = !DILocation(line: 1799, column: 23, scope: !5137)
!5142 = distinct !{!5142, !5132, !5143, !312, !313}
!5143 = !DILocation(line: 1803, column: 9, scope: !5133)
!5144 = !DILocation(line: 0, scope: !99, inlinedAt: !5145)
!5145 = distinct !DILocation(line: 1804, column: 9, scope: !5053)
!5146 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !5145)
!5147 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !5145)
!5148 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5145)
!5149 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !5145)
!5150 = !DILocation(line: 1809, column: 20, scope: !5151)
!5151 = distinct !DILexicalBlock(scope: !5152, file: !3, line: 1807, column: 18)
!5152 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1807, column: 9)
!5153 = !DILocation(line: 1810, column: 20, scope: !5151)
!5154 = !DILocation(line: 1811, column: 20, scope: !5151)
!5155 = !DILocation(line: 1812, column: 20, scope: !5151)
!5156 = !DILocation(line: 1814, column: 9, scope: !5157)
!5157 = distinct !DILexicalBlock(scope: !5151, file: !3, line: 1814, column: 9)
!5158 = !DILocation(line: 1815, column: 25, scope: !5159)
!5159 = distinct !DILexicalBlock(scope: !5160, file: !3, line: 1814, column: 39)
!5160 = distinct !DILexicalBlock(scope: !5157, file: !3, line: 1814, column: 9)
!5161 = !DILocation(line: 1815, column: 34, scope: !5159)
!5162 = !DILocation(line: 1815, column: 23, scope: !5159)
!5163 = !DILocation(line: 1814, column: 21, scope: !5160)
!5164 = !DILocation(line: 1814, column: 23, scope: !5160)
!5165 = distinct !{!5165, !5156, !5166, !312, !313}
!5166 = !DILocation(line: 1816, column: 9, scope: !5157)
!5167 = !DILocation(line: 0, scope: !99, inlinedAt: !5168)
!5168 = distinct !DILocation(line: 1817, column: 9, scope: !5151)
!5169 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !5168)
!5170 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !5168)
!5171 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5168)
!5172 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !5168)
!5173 = !DILocation(line: 1818, column: 9, scope: !5151)
!5174 = !DILocation(line: 1822, column: 27, scope: !5175)
!5175 = distinct !DILexicalBlock(scope: !5176, file: !3, line: 1820, column: 18)
!5176 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1820, column: 9)
!5177 = !DILocation(line: 1823, column: 20, scope: !5175)
!5178 = !DILocation(line: 0, scope: !99, inlinedAt: !5179)
!5179 = distinct !DILocation(line: 1824, column: 9, scope: !5175)
!5180 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5179)
!5181 = !DILocation(line: 1825, column: 9, scope: !5175)
!5182 = !DILocation(line: 1829, column: 20, scope: !5056)
!5183 = !DILocation(line: 1829, column: 37, scope: !5056)
!5184 = !DILocation(line: 1830, column: 20, scope: !5056)
!5185 = !DILocation(line: 1830, column: 37, scope: !5056)
!5186 = !DILocation(line: 0, scope: !5056)
!5187 = !DILocation(line: 1832, column: 20, scope: !5056)
!5188 = !DILocation(line: 1832, column: 45, scope: !5056)
!5189 = !DILocation(line: 1833, column: 20, scope: !5056)
!5190 = !DILocation(line: 1833, column: 37, scope: !5056)
!5191 = !DILocation(line: 0, scope: !99, inlinedAt: !5192)
!5192 = distinct !DILocation(line: 1834, column: 9, scope: !5056)
!5193 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5192)
!5194 = !DILocation(line: 1839, column: 20, scope: !5195)
!5195 = distinct !DILexicalBlock(scope: !5196, file: !3, line: 1837, column: 19)
!5196 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1837, column: 9)
!5197 = !DILocation(line: 1839, column: 38, scope: !5195)
!5198 = !DILocation(line: 1840, column: 20, scope: !5195)
!5199 = !DILocation(line: 1841, column: 20, scope: !5195)
!5200 = !DILocation(line: 0, scope: !99, inlinedAt: !5201)
!5201 = distinct !DILocation(line: 1842, column: 9, scope: !5195)
!5202 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5201)
!5203 = !DILocation(line: 1843, column: 9, scope: !5195)
!5204 = !DILocation(line: 1847, column: 20, scope: !5205)
!5205 = distinct !DILexicalBlock(scope: !5206, file: !3, line: 1845, column: 19)
!5206 = distinct !DILexicalBlock(scope: !5045, file: !3, line: 1845, column: 9)
!5207 = !DILocation(line: 1847, column: 36, scope: !5205)
!5208 = !DILocation(line: 1847, column: 52, scope: !5205)
!5209 = !DILocation(line: 1847, column: 68, scope: !5205)
!5210 = !DILocation(line: 0, scope: !99, inlinedAt: !5211)
!5211 = distinct !DILocation(line: 1849, column: 9, scope: !5205)
!5212 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5211)
!5213 = !DILocation(line: 1850, column: 9, scope: !5205)
!5214 = !DILocation(line: 0, scope: !99, inlinedAt: !5215)
!5215 = distinct !DILocation(line: 1852, column: 5, scope: !5045)
!5216 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5215)
!5217 = !DILocation(line: 1853, column: 1, scope: !5045)
!5218 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5059)
!5219 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5059)
!5220 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5059)
!5221 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5059)
!5222 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5059)
!5223 = distinct !DISubprogram(name: "test_high_local_count", scope: !3, file: !3, line: 1861, type: !142, scopeLine: 1861, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5224)
!5224 = !{!5225, !5226, !5227, !5228, !5229, !5230, !5231, !5232, !5233, !5234, !5235, !5236, !5239, !5240, !5243, !5246, !5247, !5250, !5251, !5252, !5255}
!5225 = !DILocalVariable(name: "apdu", arg: 1, scope: !5223, file: !3, line: 1861, type: !102)
!5226 = !DILocalVariable(name: "buffer", arg: 2, scope: !5223, file: !3, line: 1861, type: !104)
!5227 = !DILocalVariable(name: "p1", arg: 3, scope: !5223, file: !3, line: 1861, type: !5)
!5228 = !DILocalVariable(name: "a", scope: !5223, file: !3, line: 1863, type: !8)
!5229 = !DILocalVariable(name: "b", scope: !5223, file: !3, line: 1863, type: !8)
!5230 = !DILocalVariable(name: "c", scope: !5223, file: !3, line: 1863, type: !8)
!5231 = !DILocalVariable(name: "d", scope: !5223, file: !3, line: 1863, type: !8)
!5232 = !DILocalVariable(name: "e", scope: !5223, file: !3, line: 1863, type: !8)
!5233 = !DILocalVariable(name: "f", scope: !5223, file: !3, line: 1863, type: !8)
!5234 = !DILocalVariable(name: "g", scope: !5223, file: !3, line: 1863, type: !8)
!5235 = !DILocalVariable(name: "h", scope: !5223, file: !3, line: 1863, type: !8)
!5236 = !DILocalVariable(name: "i", scope: !5237, file: !3, line: 1873, type: !8)
!5237 = distinct !DILexicalBlock(scope: !5238, file: !3, line: 1871, column: 18)
!5238 = distinct !DILexicalBlock(scope: !5223, file: !3, line: 1871, column: 9)
!5239 = !DILocalVariable(name: "sum", scope: !5237, file: !3, line: 1874, type: !8)
!5240 = !DILocalVariable(name: "tmp", scope: !5241, file: !3, line: 1884, type: !8)
!5241 = distinct !DILexicalBlock(scope: !5242, file: !3, line: 1881, column: 18)
!5242 = distinct !DILexicalBlock(scope: !5223, file: !3, line: 1881, column: 9)
!5243 = !DILocalVariable(name: "i1", scope: !5244, file: !3, line: 1891, type: !20)
!5244 = distinct !DILexicalBlock(scope: !5245, file: !3, line: 1888, column: 18)
!5245 = distinct !DILexicalBlock(scope: !5223, file: !3, line: 1888, column: 9)
!5246 = !DILocalVariable(name: "i2", scope: !5244, file: !3, line: 1891, type: !20)
!5247 = !DILocalVariable(name: "i", scope: !5248, file: !3, line: 1897, type: !8)
!5248 = distinct !DILexicalBlock(scope: !5249, file: !3, line: 1895, column: 18)
!5249 = distinct !DILexicalBlock(scope: !5223, file: !3, line: 1895, column: 9)
!5250 = !DILocalVariable(name: "j", scope: !5248, file: !3, line: 1898, type: !8)
!5251 = !DILocalVariable(name: "sum", scope: !5248, file: !3, line: 1899, type: !8)
!5252 = !DILocalVariable(name: "i", scope: !5253, file: !3, line: 1921, type: !8)
!5253 = distinct !DILexicalBlock(scope: !5254, file: !3, line: 1919, column: 18)
!5254 = distinct !DILexicalBlock(scope: !5223, file: !3, line: 1919, column: 9)
!5255 = !DILocalVariable(name: "sum", scope: !5253, file: !3, line: 1922, type: !8)
!5256 = !DILocation(line: 0, scope: !5223)
!5257 = !DILocation(line: 1865, column: 9, scope: !5223)
!5258 = !DILocation(line: 0, scope: !5237)
!5259 = !DILocation(line: 0, scope: !99, inlinedAt: !5260)
!5260 = distinct !DILocation(line: 1878, column: 9, scope: !5237)
!5261 = !DILocation(line: 0, scope: !5241)
!5262 = !DILocation(line: 0, scope: !99, inlinedAt: !5263)
!5263 = distinct !DILocation(line: 1885, column: 9, scope: !5241)
!5264 = !DILocation(line: 0, scope: !5244)
!5265 = !DILocation(line: 0, scope: !99, inlinedAt: !5266)
!5266 = distinct !DILocation(line: 1892, column: 9, scope: !5244)
!5267 = !DILocation(line: 0, scope: !5248)
!5268 = !DILocation(line: 0, scope: !99, inlinedAt: !5269)
!5269 = distinct !DILocation(line: 1905, column: 9, scope: !5248)
!5270 = !DILocation(line: 0, scope: !99, inlinedAt: !5271)
!5271 = distinct !DILocation(line: 1916, column: 9, scope: !5272)
!5272 = distinct !DILexicalBlock(scope: !5273, file: !3, line: 1908, column: 18)
!5273 = distinct !DILexicalBlock(scope: !5223, file: !3, line: 1908, column: 9)
!5274 = !DILocation(line: 1917, column: 9, scope: !5272)
!5275 = !DILocation(line: 0, scope: !5253)
!5276 = !DILocation(line: 1924, column: 24, scope: !5277)
!5277 = distinct !DILexicalBlock(scope: !5278, file: !3, line: 1923, column: 41)
!5278 = distinct !DILexicalBlock(scope: !5279, file: !3, line: 1923, column: 9)
!5279 = distinct !DILexicalBlock(scope: !5253, file: !3, line: 1923, column: 9)
!5280 = !DILocation(line: 1924, column: 13, scope: !5277)
!5281 = !DILocation(line: 1924, column: 29, scope: !5277)
!5282 = !DILocation(line: 1923, column: 36, scope: !5278)
!5283 = !DILocation(line: 1923, column: 23, scope: !5278)
!5284 = !DILocation(line: 1923, column: 9, scope: !5279)
!5285 = distinct !{!5285, !5284, !5286, !312, !313}
!5286 = !DILocation(line: 1926, column: 9, scope: !5279)
!5287 = !DILocation(line: 0, scope: !99, inlinedAt: !5288)
!5288 = distinct !DILocation(line: 1933, column: 9, scope: !5289)
!5289 = distinct !DILexicalBlock(scope: !5290, file: !3, line: 1930, column: 18)
!5290 = distinct !DILexicalBlock(scope: !5223, file: !3, line: 1930, column: 9)
!5291 = !DILocation(line: 1934, column: 9, scope: !5289)
!5292 = !DILocation(line: 0, scope: !99, inlinedAt: !5293)
!5293 = distinct !DILocation(line: 1936, column: 5, scope: !5223)
!5294 = !DILocation(line: 1937, column: 1, scope: !5223)
!5295 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5256)
!5296 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5256)
!5297 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5256)
!5298 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5256)
!5299 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5256)
!5300 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5256)
!5301 = distinct !DISubprogram(name: "test_graphics_primitives", scope: !3, file: !3, line: 1945, type: !142, scopeLine: 1945, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5302)
!5302 = !{!5303, !5304, !5305, !5306, !5307, !5308}
!5303 = !DILocalVariable(name: "apdu", arg: 1, scope: !5301, file: !3, line: 1945, type: !102)
!5304 = !DILocalVariable(name: "buffer", arg: 2, scope: !5301, file: !3, line: 1945, type: !104)
!5305 = !DILocalVariable(name: "p1", arg: 3, scope: !5301, file: !3, line: 1945, type: !5)
!5306 = !DILocalVariable(name: "x", scope: !5301, file: !3, line: 1946, type: !8)
!5307 = !DILocalVariable(name: "i", scope: !5301, file: !3, line: 1947, type: !8)
!5308 = !DILocalVariable(name: "bit_set", scope: !5309, file: !3, line: 2020, type: !8)
!5309 = distinct !DILexicalBlock(scope: !5310, file: !3, line: 2016, column: 18)
!5310 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 2016, column: 9)
!5311 = !DILocation(line: 0, scope: !5301)
!5312 = !DILocation(line: 1949, column: 9, scope: !5301)
!5313 = !DILocation(line: 1952, column: 20, scope: !5314)
!5314 = distinct !DILexicalBlock(scope: !5315, file: !3, line: 1949, column: 18)
!5315 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 1949, column: 9)
!5316 = !DILocation(line: 0, scope: !99, inlinedAt: !5317)
!5317 = distinct !DILocation(line: 1953, column: 9, scope: !5314)
!5318 = !DILocation(line: 1954, column: 9, scope: !5314)
!5319 = !DILocation(line: 1959, column: 20, scope: !5320)
!5320 = distinct !DILexicalBlock(scope: !5321, file: !3, line: 1956, column: 18)
!5321 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 1956, column: 9)
!5322 = !DILocation(line: 0, scope: !99, inlinedAt: !5323)
!5323 = distinct !DILocation(line: 1960, column: 9, scope: !5320)
!5324 = !DILocation(line: 1961, column: 9, scope: !5320)
!5325 = !DILocation(line: 1966, column: 13, scope: !5326)
!5326 = distinct !DILexicalBlock(scope: !5327, file: !3, line: 1965, column: 39)
!5327 = distinct !DILexicalBlock(scope: !5328, file: !3, line: 1965, column: 9)
!5328 = distinct !DILexicalBlock(scope: !5329, file: !3, line: 1965, column: 9)
!5329 = distinct !DILexicalBlock(scope: !5330, file: !3, line: 1963, column: 18)
!5330 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 1963, column: 9)
!5331 = !DILocation(line: 1966, column: 24, scope: !5326)
!5332 = !DILocation(line: 1965, column: 21, scope: !5327)
!5333 = !DILocation(line: 1965, column: 23, scope: !5327)
!5334 = !DILocation(line: 1965, column: 9, scope: !5328)
!5335 = distinct !{!5335, !5334, !5336, !312, !313}
!5336 = !DILocation(line: 1967, column: 9, scope: !5328)
!5337 = !DILocation(line: 1968, column: 35, scope: !5329)
!5338 = !DILocation(line: 1968, column: 48, scope: !5329)
!5339 = !DILocation(line: 1968, column: 46, scope: !5329)
!5340 = !DILocation(line: 1968, column: 61, scope: !5329)
!5341 = !DILocation(line: 1968, column: 59, scope: !5329)
!5342 = !DILocation(line: 1968, column: 74, scope: !5329)
!5343 = !DILocation(line: 1968, column: 72, scope: !5329)
!5344 = !DILocation(line: 0, scope: !99, inlinedAt: !5345)
!5345 = distinct !DILocation(line: 1968, column: 9, scope: !5329)
!5346 = !DILocation(line: 1969, column: 9, scope: !5329)
!5347 = !DILocation(line: 1973, column: 36, scope: !5348)
!5348 = distinct !DILexicalBlock(scope: !5349, file: !3, line: 1971, column: 18)
!5349 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 1971, column: 9)
!5350 = !DILocation(line: 1974, column: 20, scope: !5348)
!5351 = !DILocation(line: 1975, column: 20, scope: !5348)
!5352 = !DILocation(line: 0, scope: !99, inlinedAt: !5353)
!5353 = distinct !DILocation(line: 1976, column: 9, scope: !5348)
!5354 = !DILocation(line: 1977, column: 9, scope: !5348)
!5355 = !DILocation(line: 1982, column: 20, scope: !5356)
!5356 = distinct !DILexicalBlock(scope: !5357, file: !3, line: 1979, column: 18)
!5357 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 1979, column: 9)
!5358 = !DILocation(line: 0, scope: !99, inlinedAt: !5359)
!5359 = distinct !DILocation(line: 1983, column: 9, scope: !5356)
!5360 = !DILocation(line: 1984, column: 9, scope: !5356)
!5361 = !DILocation(line: 1989, column: 20, scope: !5362)
!5362 = distinct !DILexicalBlock(scope: !5363, file: !3, line: 1986, column: 18)
!5363 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 1986, column: 9)
!5364 = !DILocation(line: 0, scope: !99, inlinedAt: !5365)
!5365 = distinct !DILocation(line: 1990, column: 9, scope: !5362)
!5366 = !DILocation(line: 1991, column: 9, scope: !5362)
!5367 = !DILocation(line: 1995, column: 20, scope: !5368)
!5368 = distinct !DILexicalBlock(scope: !5369, file: !3, line: 1993, column: 18)
!5369 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 1993, column: 9)
!5370 = !DILocation(line: 1995, column: 36, scope: !5368)
!5371 = !DILocation(line: 1995, column: 52, scope: !5368)
!5372 = !DILocation(line: 1996, column: 20, scope: !5368)
!5373 = !DILocation(line: 1997, column: 20, scope: !5368)
!5374 = !DILocation(line: 1998, column: 20, scope: !5368)
!5375 = !DILocation(line: 0, scope: !99, inlinedAt: !5376)
!5376 = distinct !DILocation(line: 1999, column: 9, scope: !5368)
!5377 = !DILocation(line: 2000, column: 9, scope: !5368)
!5378 = !DILocation(line: 2005, column: 20, scope: !5379)
!5379 = distinct !DILexicalBlock(scope: !5380, file: !3, line: 2002, column: 18)
!5380 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 2002, column: 9)
!5381 = !DILocation(line: 0, scope: !99, inlinedAt: !5382)
!5382 = distinct !DILocation(line: 2006, column: 9, scope: !5379)
!5383 = !DILocation(line: 2007, column: 9, scope: !5379)
!5384 = !DILocation(line: 2012, column: 20, scope: !5385)
!5385 = distinct !DILexicalBlock(scope: !5386, file: !3, line: 2009, column: 18)
!5386 = distinct !DILexicalBlock(scope: !5301, file: !3, line: 2009, column: 9)
!5387 = !DILocation(line: 0, scope: !99, inlinedAt: !5388)
!5388 = distinct !DILocation(line: 2013, column: 9, scope: !5385)
!5389 = !DILocation(line: 2014, column: 9, scope: !5385)
!5390 = !DILocation(line: 2018, column: 20, scope: !5309)
!5391 = !DILocation(line: 0, scope: !5309)
!5392 = !DILocation(line: 0, scope: !99, inlinedAt: !5393)
!5393 = distinct !DILocation(line: 2021, column: 9, scope: !5309)
!5394 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5311)
!5395 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5311)
!5396 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5311)
!5397 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5311)
!5398 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5311)
!5399 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5311)
!5400 = !DILocation(line: 2025, column: 1, scope: !5301)
!5401 = distinct !DISubprogram(name: "set_global_short", scope: !3, file: !3, line: 2034, type: !296, scopeLine: 2034, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!5402 = !DILocation(line: 2035, column: 13, scope: !5401)
!5403 = !DILocation(line: 2036, column: 5, scope: !5401)
!5404 = distinct !DISubprogram(name: "test_boolean_density", scope: !3, file: !3, line: 2039, type: !142, scopeLine: 2039, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5405)
!5405 = !{!5406, !5407, !5408, !5409, !5410, !5411, !5412, !5413, !5416, !5417, !5418, !5421, !5422, !5423, !5424, !5425, !5426, !5429, !5430, !5433, !5434}
!5406 = !DILocalVariable(name: "apdu", arg: 1, scope: !5404, file: !3, line: 2039, type: !102)
!5407 = !DILocalVariable(name: "buffer", arg: 2, scope: !5404, file: !3, line: 2039, type: !104)
!5408 = !DILocalVariable(name: "p1", arg: 3, scope: !5404, file: !3, line: 2039, type: !5)
!5409 = !DILocalVariable(name: "a", scope: !5404, file: !3, line: 2040, type: !8)
!5410 = !DILocalVariable(name: "b", scope: !5404, file: !3, line: 2041, type: !8)
!5411 = !DILocalVariable(name: "c", scope: !5404, file: !3, line: 2042, type: !8)
!5412 = !DILocalVariable(name: "d", scope: !5404, file: !3, line: 2043, type: !8)
!5413 = !DILocalVariable(name: "x", scope: !5414, file: !3, line: 2052, type: !8)
!5414 = distinct !DILexicalBlock(scope: !5415, file: !3, line: 2050, column: 18)
!5415 = distinct !DILexicalBlock(scope: !5404, file: !3, line: 2050, column: 9)
!5416 = !DILocalVariable(name: "y", scope: !5414, file: !3, line: 2052, type: !8)
!5417 = !DILocalVariable(name: "z", scope: !5414, file: !3, line: 2052, type: !8)
!5418 = !DILocalVariable(name: "x", scope: !5419, file: !3, line: 2060, type: !8)
!5419 = distinct !DILexicalBlock(scope: !5420, file: !3, line: 2058, column: 18)
!5420 = distinct !DILexicalBlock(scope: !5404, file: !3, line: 2058, column: 9)
!5421 = !DILocalVariable(name: "y", scope: !5419, file: !3, line: 2060, type: !8)
!5422 = !DILocalVariable(name: "x0", scope: !5419, file: !3, line: 2061, type: !8)
!5423 = !DILocalVariable(name: "x1", scope: !5419, file: !3, line: 2061, type: !8)
!5424 = !DILocalVariable(name: "y0", scope: !5419, file: !3, line: 2061, type: !8)
!5425 = !DILocalVariable(name: "y1", scope: !5419, file: !3, line: 2061, type: !8)
!5426 = !DILocalVariable(name: "cond1", scope: !5427, file: !3, line: 2075, type: !8)
!5427 = distinct !DILexicalBlock(scope: !5428, file: !3, line: 2073, column: 19)
!5428 = distinct !DILexicalBlock(scope: !5404, file: !3, line: 2073, column: 9)
!5429 = !DILocalVariable(name: "cond2", scope: !5427, file: !3, line: 2075, type: !8)
!5430 = !DILocalVariable(name: "flags", scope: !5431, file: !3, line: 2081, type: !8)
!5431 = distinct !DILexicalBlock(scope: !5432, file: !3, line: 2079, column: 19)
!5432 = distinct !DILexicalBlock(scope: !5404, file: !3, line: 2079, column: 9)
!5433 = !DILocalVariable(name: "MASK", scope: !5431, file: !3, line: 2082, type: !8)
!5434 = !DILocalVariable(name: "enabled", scope: !5431, file: !3, line: 2083, type: !8)
!5435 = !DILocation(line: 0, scope: !5404)
!5436 = !DILocation(line: 2045, column: 9, scope: !5404)
!5437 = !DILocation(line: 0, scope: !99, inlinedAt: !5438)
!5438 = distinct !DILocation(line: 2056, column: 20, scope: !5439)
!5439 = distinct !DILexicalBlock(scope: !5440, file: !3, line: 2056, column: 18)
!5440 = distinct !DILexicalBlock(scope: !5404, file: !3, line: 2056, column: 9)
!5441 = !DILocation(line: 2056, column: 67, scope: !5439)
!5442 = !DILocation(line: 0, scope: !99, inlinedAt: !5443)
!5443 = distinct !DILocation(line: 2057, column: 20, scope: !5444)
!5444 = distinct !DILexicalBlock(scope: !5445, file: !3, line: 2057, column: 18)
!5445 = distinct !DILexicalBlock(scope: !5404, file: !3, line: 2057, column: 9)
!5446 = !DILocation(line: 2057, column: 70, scope: !5444)
!5447 = !DILocation(line: 2068, column: 17, scope: !5448)
!5448 = distinct !DILexicalBlock(scope: !5449, file: !3, line: 2065, column: 18)
!5449 = distinct !DILexicalBlock(scope: !5404, file: !3, line: 2065, column: 9)
!5450 = !DILocation(line: 0, scope: !99, inlinedAt: !5451)
!5451 = distinct !DILocation(line: 2070, column: 9, scope: !5448)
!5452 = !DILocation(line: 2071, column: 9, scope: !5448)
!5453 = !DILocation(line: 0, scope: !99, inlinedAt: !5454)
!5454 = distinct !DILocation(line: 2087, column: 5, scope: !5404)
!5455 = !DILocation(line: 2088, column: 1, scope: !5404)
!5456 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5435)
!5457 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5435)
!5458 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5435)
!5459 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5435)
!5460 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5435)
!5461 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5435)
!5462 = distinct !DISubprogram(name: "test_loop_edge_cases", scope: !3, file: !3, line: 2096, type: !142, scopeLine: 2096, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5463)
!5463 = !{!5464, !5465, !5466, !5467, !5468, !5469}
!5464 = !DILocalVariable(name: "apdu", arg: 1, scope: !5462, file: !3, line: 2096, type: !102)
!5465 = !DILocalVariable(name: "buffer", arg: 2, scope: !5462, file: !3, line: 2096, type: !104)
!5466 = !DILocalVariable(name: "p1", arg: 3, scope: !5462, file: !3, line: 2096, type: !5)
!5467 = !DILocalVariable(name: "i", scope: !5462, file: !3, line: 2097, type: !8)
!5468 = !DILocalVariable(name: "sum", scope: !5462, file: !3, line: 2098, type: !8)
!5469 = !DILocalVariable(name: "j", scope: !5470, file: !3, line: 2169, type: !8)
!5470 = distinct !DILexicalBlock(scope: !5471, file: !3, line: 2167, column: 18)
!5471 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2167, column: 9)
!5472 = !DILocation(line: 0, scope: !5462)
!5473 = !DILocation(line: 2100, column: 9, scope: !5462)
!5474 = !DILocation(line: 0, scope: !99, inlinedAt: !5475)
!5475 = distinct !DILocation(line: 2115, column: 9, scope: !5476)
!5476 = distinct !DILexicalBlock(scope: !5477, file: !3, line: 2109, column: 18)
!5477 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2109, column: 9)
!5478 = !DILocation(line: 2116, column: 9, scope: !5476)
!5479 = !DILocation(line: 0, scope: !99, inlinedAt: !5480)
!5480 = distinct !DILocation(line: 2124, column: 9, scope: !5481)
!5481 = distinct !DILexicalBlock(scope: !5482, file: !3, line: 2118, column: 18)
!5482 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2118, column: 9)
!5483 = !DILocation(line: 2125, column: 9, scope: !5481)
!5484 = !DILocation(line: 0, scope: !99, inlinedAt: !5485)
!5485 = distinct !DILocation(line: 2133, column: 9, scope: !5486)
!5486 = distinct !DILexicalBlock(scope: !5487, file: !3, line: 2127, column: 18)
!5487 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2127, column: 9)
!5488 = !DILocation(line: 2134, column: 9, scope: !5486)
!5489 = !DILocation(line: 0, scope: !99, inlinedAt: !5490)
!5490 = distinct !DILocation(line: 2143, column: 9, scope: !5491)
!5491 = distinct !DILexicalBlock(scope: !5492, file: !3, line: 2136, column: 18)
!5492 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2136, column: 9)
!5493 = !DILocation(line: 2144, column: 9, scope: !5491)
!5494 = !DILocation(line: 0, scope: !99, inlinedAt: !5495)
!5495 = distinct !DILocation(line: 2153, column: 9, scope: !5496)
!5496 = distinct !DILexicalBlock(scope: !5497, file: !3, line: 2146, column: 18)
!5497 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2146, column: 9)
!5498 = !DILocation(line: 2154, column: 9, scope: !5496)
!5499 = !DILocation(line: 0, scope: !99, inlinedAt: !5500)
!5500 = distinct !DILocation(line: 2164, column: 9, scope: !5501)
!5501 = distinct !DILexicalBlock(scope: !5502, file: !3, line: 2156, column: 18)
!5502 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2156, column: 9)
!5503 = !DILocation(line: 2165, column: 9, scope: !5501)
!5504 = !DILocation(line: 0, scope: !5470)
!5505 = !DILocation(line: 0, scope: !99, inlinedAt: !5506)
!5506 = distinct !DILocation(line: 2176, column: 9, scope: !5470)
!5507 = !DILocation(line: 0, scope: !99, inlinedAt: !5508)
!5508 = distinct !DILocation(line: 2186, column: 9, scope: !5509)
!5509 = distinct !DILexicalBlock(scope: !5510, file: !3, line: 2179, column: 18)
!5510 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2179, column: 9)
!5511 = !DILocation(line: 2187, column: 9, scope: !5509)
!5512 = !DILocation(line: 0, scope: !99, inlinedAt: !5513)
!5513 = distinct !DILocation(line: 2196, column: 9, scope: !5514)
!5514 = distinct !DILexicalBlock(scope: !5515, file: !3, line: 2189, column: 18)
!5515 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2189, column: 9)
!5516 = !DILocation(line: 2197, column: 9, scope: !5514)
!5517 = !DILocation(line: 2202, column: 9, scope: !5518)
!5518 = distinct !DILexicalBlock(scope: !5519, file: !3, line: 2202, column: 9)
!5519 = distinct !DILexicalBlock(scope: !5520, file: !3, line: 2199, column: 19)
!5520 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2199, column: 9)
!5521 = !DILocation(line: 2205, column: 23, scope: !5522)
!5522 = distinct !DILexicalBlock(scope: !5523, file: !3, line: 2202, column: 40)
!5523 = distinct !DILexicalBlock(scope: !5518, file: !3, line: 2202, column: 9)
!5524 = !DILocation(line: 2202, column: 21, scope: !5523)
!5525 = !DILocation(line: 2202, column: 23, scope: !5523)
!5526 = distinct !{!5526, !5517, !5527, !312, !313}
!5527 = !DILocation(line: 2206, column: 9, scope: !5518)
!5528 = !DILocation(line: 0, scope: !99, inlinedAt: !5529)
!5529 = distinct !DILocation(line: 2219, column: 9, scope: !5530)
!5530 = distinct !DILexicalBlock(scope: !5531, file: !3, line: 2210, column: 19)
!5531 = distinct !DILexicalBlock(scope: !5462, file: !3, line: 2210, column: 9)
!5532 = !DILocation(line: 2220, column: 9, scope: !5530)
!5533 = !DILocation(line: 0, scope: !99, inlinedAt: !5534)
!5534 = distinct !DILocation(line: 2222, column: 5, scope: !5462)
!5535 = !DILocation(line: 2223, column: 1, scope: !5462)
!5536 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5472)
!5537 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5472)
!5538 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5472)
!5539 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5472)
!5540 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5472)
!5541 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5472)
!5542 = distinct !DISubprogram(name: "test_type_coercion_edge", scope: !3, file: !3, line: 2231, type: !142, scopeLine: 2231, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5543)
!5543 = !{!5544, !5545, !5546, !5547, !5548, !5549, !5550, !5553, !5556, !5557}
!5544 = !DILocalVariable(name: "apdu", arg: 1, scope: !5542, file: !3, line: 2231, type: !102)
!5545 = !DILocalVariable(name: "buffer", arg: 2, scope: !5542, file: !3, line: 2231, type: !104)
!5546 = !DILocalVariable(name: "p1", arg: 3, scope: !5542, file: !3, line: 2231, type: !5)
!5547 = !DILocalVariable(name: "b", scope: !5542, file: !3, line: 2232, type: !5)
!5548 = !DILocalVariable(name: "s", scope: !5542, file: !3, line: 2233, type: !8)
!5549 = !DILocalVariable(name: "i", scope: !5542, file: !3, line: 2234, type: !20)
!5550 = !DILocalVariable(name: "b2", scope: !5551, file: !3, line: 2295, type: !5)
!5551 = distinct !DILexicalBlock(scope: !5552, file: !3, line: 2292, column: 18)
!5552 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2292, column: 9)
!5553 = !DILocalVariable(name: "a", scope: !5554, file: !3, line: 2308, type: !8)
!5554 = distinct !DILexicalBlock(scope: !5555, file: !3, line: 2306, column: 19)
!5555 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2306, column: 9)
!5556 = !DILocalVariable(name: "bb", scope: !5554, file: !3, line: 2309, type: !8)
!5557 = !DILocalVariable(name: "result", scope: !5558, file: !3, line: 2331, type: !8)
!5558 = distinct !DILexicalBlock(scope: !5559, file: !3, line: 2328, column: 19)
!5559 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2328, column: 9)
!5560 = !DILocation(line: 0, scope: !5542)
!5561 = !DILocation(line: 2236, column: 9, scope: !5542)
!5562 = !DILocation(line: 0, scope: !99, inlinedAt: !5563)
!5563 = distinct !DILocation(line: 2247, column: 9, scope: !5564)
!5564 = distinct !DILexicalBlock(scope: !5565, file: !3, line: 2243, column: 18)
!5565 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2243, column: 9)
!5566 = !DILocation(line: 2248, column: 9, scope: !5564)
!5567 = !DILocation(line: 0, scope: !99, inlinedAt: !5568)
!5568 = distinct !DILocation(line: 2254, column: 9, scope: !5569)
!5569 = distinct !DILexicalBlock(scope: !5570, file: !3, line: 2250, column: 18)
!5570 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2250, column: 9)
!5571 = !DILocation(line: 2255, column: 9, scope: !5569)
!5572 = !DILocation(line: 0, scope: !99, inlinedAt: !5573)
!5573 = distinct !DILocation(line: 2261, column: 9, scope: !5574)
!5574 = distinct !DILexicalBlock(scope: !5575, file: !3, line: 2257, column: 18)
!5575 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2257, column: 9)
!5576 = !DILocation(line: 2262, column: 9, scope: !5574)
!5577 = !DILocation(line: 0, scope: !99, inlinedAt: !5578)
!5578 = distinct !DILocation(line: 2268, column: 9, scope: !5579)
!5579 = distinct !DILexicalBlock(scope: !5580, file: !3, line: 2264, column: 18)
!5580 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2264, column: 9)
!5581 = !DILocation(line: 2269, column: 9, scope: !5579)
!5582 = !DILocation(line: 0, scope: !99, inlinedAt: !5583)
!5583 = distinct !DILocation(line: 2275, column: 9, scope: !5584)
!5584 = distinct !DILexicalBlock(scope: !5585, file: !3, line: 2271, column: 18)
!5585 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2271, column: 9)
!5586 = !DILocation(line: 2276, column: 9, scope: !5584)
!5587 = !DILocation(line: 0, scope: !99, inlinedAt: !5588)
!5588 = distinct !DILocation(line: 2282, column: 9, scope: !5589)
!5589 = distinct !DILexicalBlock(scope: !5590, file: !3, line: 2278, column: 18)
!5590 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2278, column: 9)
!5591 = !DILocation(line: 2283, column: 9, scope: !5589)
!5592 = !DILocation(line: 0, scope: !99, inlinedAt: !5593)
!5593 = distinct !DILocation(line: 2289, column: 9, scope: !5594)
!5594 = distinct !DILexicalBlock(scope: !5595, file: !3, line: 2285, column: 18)
!5595 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2285, column: 9)
!5596 = !DILocation(line: 2290, column: 9, scope: !5594)
!5597 = !DILocation(line: 0, scope: !5551)
!5598 = !DILocation(line: 0, scope: !99, inlinedAt: !5599)
!5599 = distinct !DILocation(line: 2296, column: 9, scope: !5551)
!5600 = !DILocation(line: 0, scope: !99, inlinedAt: !5601)
!5601 = distinct !DILocation(line: 2303, column: 9, scope: !5602)
!5602 = distinct !DILexicalBlock(scope: !5603, file: !3, line: 2299, column: 18)
!5603 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2299, column: 9)
!5604 = !DILocation(line: 2304, column: 9, scope: !5602)
!5605 = !DILocation(line: 0, scope: !5554)
!5606 = !DILocation(line: 0, scope: !99, inlinedAt: !5607)
!5607 = distinct !DILocation(line: 2311, column: 9, scope: !5554)
!5608 = !DILocation(line: 0, scope: !99, inlinedAt: !5609)
!5609 = distinct !DILocation(line: 2318, column: 9, scope: !5610)
!5610 = distinct !DILexicalBlock(scope: !5611, file: !3, line: 2314, column: 19)
!5611 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2314, column: 9)
!5612 = !DILocation(line: 2319, column: 9, scope: !5610)
!5613 = !DILocation(line: 2324, column: 21, scope: !5614)
!5614 = distinct !DILexicalBlock(scope: !5615, file: !3, line: 2321, column: 19)
!5615 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2321, column: 9)
!5616 = !DILocation(line: 0, scope: !99, inlinedAt: !5617)
!5617 = distinct !DILocation(line: 2325, column: 9, scope: !5614)
!5618 = !DILocation(line: 2326, column: 9, scope: !5614)
!5619 = !DILocation(line: 0, scope: !5558)
!5620 = !DILocation(line: 0, scope: !99, inlinedAt: !5621)
!5621 = distinct !DILocation(line: 2332, column: 9, scope: !5558)
!5622 = !DILocation(line: 0, scope: !99, inlinedAt: !5623)
!5623 = distinct !DILocation(line: 2339, column: 9, scope: !5624)
!5624 = distinct !DILexicalBlock(scope: !5625, file: !3, line: 2335, column: 19)
!5625 = distinct !DILexicalBlock(scope: !5542, file: !3, line: 2335, column: 9)
!5626 = !DILocation(line: 2340, column: 9, scope: !5624)
!5627 = !DILocation(line: 0, scope: !99, inlinedAt: !5628)
!5628 = distinct !DILocation(line: 2342, column: 5, scope: !5542)
!5629 = !DILocation(line: 2343, column: 1, scope: !5542)
!5630 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5560)
!5631 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5560)
!5632 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5560)
!5633 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5560)
!5634 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5560)
!5635 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5560)
!5636 = distinct !DISubprogram(name: "test_array_bounds", scope: !3, file: !3, line: 2353, type: !142, scopeLine: 2353, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5637)
!5637 = !{!5638, !5639, !5640, !5641, !5642}
!5638 = !DILocalVariable(name: "apdu", arg: 1, scope: !5636, file: !3, line: 2353, type: !102)
!5639 = !DILocalVariable(name: "buffer", arg: 2, scope: !5636, file: !3, line: 2353, type: !104)
!5640 = !DILocalVariable(name: "p1", arg: 3, scope: !5636, file: !3, line: 2353, type: !5)
!5641 = !DILocalVariable(name: "i", scope: !5636, file: !3, line: 2354, type: !8)
!5642 = !DILocalVariable(name: "sum", scope: !5636, file: !3, line: 2355, type: !8)
!5643 = !DILocation(line: 0, scope: !5636)
!5644 = !DILocation(line: 2357, column: 9, scope: !5636)
!5645 = !DILocation(line: 2358, column: 20, scope: !5646)
!5646 = distinct !DILexicalBlock(scope: !5647, file: !3, line: 2357, column: 18)
!5647 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2357, column: 9)
!5648 = !DILocation(line: 0, scope: !99, inlinedAt: !5649)
!5649 = distinct !DILocation(line: 2359, column: 9, scope: !5646)
!5650 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5649)
!5651 = !DILocation(line: 2360, column: 9, scope: !5646)
!5652 = !DILocation(line: 2363, column: 20, scope: !5653)
!5653 = distinct !DILexicalBlock(scope: !5654, file: !3, line: 2362, column: 18)
!5654 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2362, column: 9)
!5655 = !DILocation(line: 0, scope: !99, inlinedAt: !5656)
!5656 = distinct !DILocation(line: 2364, column: 9, scope: !5653)
!5657 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5656)
!5658 = !DILocation(line: 2365, column: 9, scope: !5653)
!5659 = !DILocation(line: 2368, column: 21, scope: !5660)
!5660 = distinct !DILexicalBlock(scope: !5661, file: !3, line: 2367, column: 18)
!5661 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2367, column: 9)
!5662 = !DILocation(line: 0, scope: !99, inlinedAt: !5663)
!5663 = distinct !DILocation(line: 2369, column: 9, scope: !5660)
!5664 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5663)
!5665 = !DILocation(line: 2370, column: 9, scope: !5660)
!5666 = !DILocation(line: 2373, column: 21, scope: !5667)
!5667 = distinct !DILexicalBlock(scope: !5668, file: !3, line: 2372, column: 18)
!5668 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2372, column: 9)
!5669 = !DILocation(line: 0, scope: !99, inlinedAt: !5670)
!5670 = distinct !DILocation(line: 2374, column: 9, scope: !5667)
!5671 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5670)
!5672 = !DILocation(line: 2375, column: 9, scope: !5667)
!5673 = !DILocation(line: 2381, column: 28, scope: !5674)
!5674 = distinct !DILexicalBlock(scope: !5675, file: !3, line: 2380, column: 39)
!5675 = distinct !DILexicalBlock(scope: !5676, file: !3, line: 2380, column: 9)
!5676 = distinct !DILexicalBlock(scope: !5677, file: !3, line: 2380, column: 9)
!5677 = distinct !DILexicalBlock(scope: !5678, file: !3, line: 2377, column: 18)
!5678 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2377, column: 9)
!5679 = !DILocation(line: 2381, column: 26, scope: !5674)
!5680 = !DILocation(line: 2381, column: 13, scope: !5674)
!5681 = !DILocation(line: 2381, column: 24, scope: !5674)
!5682 = !DILocation(line: 2380, column: 21, scope: !5675)
!5683 = !DILocation(line: 2380, column: 23, scope: !5675)
!5684 = !DILocation(line: 2380, column: 9, scope: !5676)
!5685 = distinct !{!5685, !5684, !5686, !312, !313}
!5686 = !DILocation(line: 2382, column: 9, scope: !5676)
!5687 = !DILocation(line: 2384, column: 25, scope: !5688)
!5688 = distinct !DILexicalBlock(scope: !5689, file: !3, line: 2383, column: 39)
!5689 = distinct !DILexicalBlock(scope: !5690, file: !3, line: 2383, column: 9)
!5690 = distinct !DILexicalBlock(scope: !5677, file: !3, line: 2383, column: 9)
!5691 = !DILocation(line: 2384, column: 23, scope: !5688)
!5692 = !DILocation(line: 2383, column: 21, scope: !5689)
!5693 = !DILocation(line: 2383, column: 23, scope: !5689)
!5694 = !DILocation(line: 2383, column: 9, scope: !5690)
!5695 = distinct !{!5695, !5694, !5696, !312, !313}
!5696 = !DILocation(line: 2385, column: 9, scope: !5690)
!5697 = !DILocation(line: 0, scope: !99, inlinedAt: !5698)
!5698 = distinct !DILocation(line: 2386, column: 9, scope: !5677)
!5699 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !5698)
!5700 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !5698)
!5701 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5698)
!5702 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !5698)
!5703 = !DILocation(line: 2387, column: 9, scope: !5677)
!5704 = !DILocation(line: 2392, column: 26, scope: !5705)
!5705 = distinct !DILexicalBlock(scope: !5706, file: !3, line: 2391, column: 39)
!5706 = distinct !DILexicalBlock(scope: !5707, file: !3, line: 2391, column: 9)
!5707 = distinct !DILexicalBlock(scope: !5708, file: !3, line: 2391, column: 9)
!5708 = distinct !DILexicalBlock(scope: !5709, file: !3, line: 2389, column: 18)
!5709 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2389, column: 9)
!5710 = !DILocation(line: 2392, column: 13, scope: !5705)
!5711 = !DILocation(line: 2392, column: 24, scope: !5705)
!5712 = !DILocation(line: 2391, column: 34, scope: !5706)
!5713 = !DILocation(line: 2391, column: 23, scope: !5706)
!5714 = !DILocation(line: 2391, column: 9, scope: !5707)
!5715 = distinct !{!5715, !5714, !5716, !312, !313}
!5716 = !DILocation(line: 2393, column: 9, scope: !5707)
!5717 = !DILocation(line: 2396, column: 37, scope: !5718)
!5718 = distinct !DILexicalBlock(scope: !5719, file: !3, line: 2395, column: 39)
!5719 = distinct !DILexicalBlock(scope: !5720, file: !3, line: 2395, column: 9)
!5720 = distinct !DILexicalBlock(scope: !5708, file: !3, line: 2395, column: 9)
!5721 = !DILocation(line: 2396, column: 27, scope: !5718)
!5722 = !DILocation(line: 2396, column: 13, scope: !5718)
!5723 = !DILocation(line: 2396, column: 25, scope: !5718)
!5724 = !DILocation(line: 2395, column: 21, scope: !5719)
!5725 = !DILocation(line: 2395, column: 23, scope: !5719)
!5726 = !DILocation(line: 2395, column: 9, scope: !5720)
!5727 = distinct !{!5727, !5726, !5728, !312, !313}
!5728 = !DILocation(line: 2397, column: 9, scope: !5720)
!5729 = !DILocation(line: 2398, column: 34, scope: !5708)
!5730 = !DILocation(line: 2398, column: 48, scope: !5708)
!5731 = !DILocation(line: 2398, column: 46, scope: !5708)
!5732 = !DILocation(line: 0, scope: !99, inlinedAt: !5733)
!5733 = distinct !DILocation(line: 2398, column: 9, scope: !5708)
!5734 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !5733)
!5735 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !5733)
!5736 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5733)
!5737 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !5733)
!5738 = !DILocation(line: 2399, column: 9, scope: !5708)
!5739 = !DILocation(line: 2403, column: 21, scope: !5740)
!5740 = distinct !DILexicalBlock(scope: !5741, file: !3, line: 2401, column: 18)
!5741 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2401, column: 9)
!5742 = !DILocation(line: 2404, column: 21, scope: !5740)
!5743 = !DILocation(line: 2405, column: 9, scope: !5744)
!5744 = distinct !DILexicalBlock(scope: !5740, file: !3, line: 2405, column: 9)
!5745 = !DILocation(line: 2406, column: 37, scope: !5746)
!5746 = distinct !DILexicalBlock(scope: !5747, file: !3, line: 2405, column: 39)
!5747 = distinct !DILexicalBlock(scope: !5744, file: !3, line: 2405, column: 9)
!5748 = !DILocation(line: 2406, column: 27, scope: !5746)
!5749 = !DILocation(line: 2406, column: 53, scope: !5746)
!5750 = !DILocation(line: 2406, column: 43, scope: !5746)
!5751 = !DILocation(line: 2406, column: 41, scope: !5746)
!5752 = !DILocation(line: 2406, column: 13, scope: !5746)
!5753 = !DILocation(line: 2406, column: 25, scope: !5746)
!5754 = !DILocation(line: 2405, column: 21, scope: !5747)
!5755 = !DILocation(line: 2405, column: 23, scope: !5747)
!5756 = distinct !{!5756, !5743, !5757, !312, !313}
!5757 = !DILocation(line: 2407, column: 9, scope: !5744)
!5758 = !DILocation(line: 2408, column: 34, scope: !5740)
!5759 = !DILocation(line: 0, scope: !99, inlinedAt: !5760)
!5760 = distinct !DILocation(line: 2408, column: 9, scope: !5740)
!5761 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !5760)
!5762 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !5760)
!5763 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5760)
!5764 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !5760)
!5765 = !DILocation(line: 2409, column: 9, scope: !5740)
!5766 = !DILocation(line: 2414, column: 28, scope: !5767)
!5767 = distinct !DILexicalBlock(scope: !5768, file: !3, line: 2413, column: 39)
!5768 = distinct !DILexicalBlock(scope: !5769, file: !3, line: 2413, column: 9)
!5769 = distinct !DILexicalBlock(scope: !5770, file: !3, line: 2413, column: 9)
!5770 = distinct !DILexicalBlock(scope: !5771, file: !3, line: 2411, column: 18)
!5771 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2411, column: 9)
!5772 = !DILocation(line: 2414, column: 26, scope: !5767)
!5773 = !DILocation(line: 2414, column: 13, scope: !5767)
!5774 = !DILocation(line: 2414, column: 24, scope: !5767)
!5775 = !DILocation(line: 2413, column: 21, scope: !5768)
!5776 = !DILocation(line: 2413, column: 23, scope: !5768)
!5777 = !DILocation(line: 2413, column: 9, scope: !5769)
!5778 = distinct !{!5778, !5777, !5779, !312, !313}
!5779 = !DILocation(line: 2415, column: 9, scope: !5769)
!5780 = !DILocation(line: 2418, column: 28, scope: !5781)
!5781 = distinct !DILexicalBlock(scope: !5782, file: !3, line: 2417, column: 40)
!5782 = distinct !DILexicalBlock(scope: !5783, file: !3, line: 2417, column: 9)
!5783 = distinct !DILexicalBlock(scope: !5770, file: !3, line: 2417, column: 9)
!5784 = !DILocation(line: 2420, column: 34, scope: !5770)
!5785 = !DILocation(line: 0, scope: !99, inlinedAt: !5786)
!5786 = distinct !DILocation(line: 2420, column: 9, scope: !5770)
!5787 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !5786)
!5788 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5786)
!5789 = !DILocation(line: 2421, column: 9, scope: !5770)
!5790 = !DILocation(line: 2425, column: 20, scope: !5791)
!5791 = distinct !DILexicalBlock(scope: !5792, file: !3, line: 2423, column: 18)
!5792 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2423, column: 9)
!5793 = !DILocation(line: 2426, column: 20, scope: !5791)
!5794 = !DILocation(line: 0, scope: !99, inlinedAt: !5795)
!5795 = distinct !DILocation(line: 2427, column: 9, scope: !5791)
!5796 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5795)
!5797 = !DILocation(line: 2428, column: 9, scope: !5791)
!5798 = !DILocation(line: 2432, column: 21, scope: !5799)
!5799 = distinct !DILexicalBlock(scope: !5800, file: !3, line: 2430, column: 18)
!5800 = distinct !DILexicalBlock(scope: !5636, file: !3, line: 2430, column: 9)
!5801 = !DILocation(line: 2433, column: 9, scope: !5802)
!5802 = distinct !DILexicalBlock(scope: !5799, file: !3, line: 2433, column: 9)
!5803 = !DILocation(line: 2434, column: 37, scope: !5804)
!5804 = distinct !DILexicalBlock(scope: !5805, file: !3, line: 2433, column: 39)
!5805 = distinct !DILexicalBlock(scope: !5802, file: !3, line: 2433, column: 9)
!5806 = !DILocation(line: 2434, column: 27, scope: !5804)
!5807 = !DILocation(line: 2434, column: 41, scope: !5804)
!5808 = !DILocation(line: 2434, column: 13, scope: !5804)
!5809 = !DILocation(line: 2434, column: 25, scope: !5804)
!5810 = !DILocation(line: 2433, column: 21, scope: !5805)
!5811 = !DILocation(line: 2433, column: 23, scope: !5805)
!5812 = distinct !{!5812, !5801, !5813, !312, !313}
!5813 = !DILocation(line: 2435, column: 9, scope: !5802)
!5814 = !DILocation(line: 2436, column: 34, scope: !5799)
!5815 = !DILocation(line: 0, scope: !99, inlinedAt: !5816)
!5816 = distinct !DILocation(line: 2436, column: 9, scope: !5799)
!5817 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !5816)
!5818 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !5816)
!5819 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5816)
!5820 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !5816)
!5821 = !DILocation(line: 2437, column: 9, scope: !5799)
!5822 = !DILocation(line: 0, scope: !99, inlinedAt: !5823)
!5823 = distinct !DILocation(line: 2439, column: 5, scope: !5636)
!5824 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5823)
!5825 = !DILocation(line: 2440, column: 1, scope: !5636)
!5826 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5643)
!5827 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5643)
!5828 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5643)
!5829 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5643)
!5830 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5643)
!5831 = distinct !DISubprogram(name: "test_global_array_ops", scope: !3, file: !3, line: 2446, type: !142, scopeLine: 2446, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5832)
!5832 = !{!5833, !5834, !5835, !5836, !5837}
!5833 = !DILocalVariable(name: "apdu", arg: 1, scope: !5831, file: !3, line: 2446, type: !102)
!5834 = !DILocalVariable(name: "buffer", arg: 2, scope: !5831, file: !3, line: 2446, type: !104)
!5835 = !DILocalVariable(name: "p1", arg: 3, scope: !5831, file: !3, line: 2446, type: !5)
!5836 = !DILocalVariable(name: "i", scope: !5831, file: !3, line: 2447, type: !8)
!5837 = !DILocalVariable(name: "local", scope: !5838, file: !3, line: 2488, type: !8)
!5838 = distinct !DILexicalBlock(scope: !5839, file: !3, line: 2485, column: 18)
!5839 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2485, column: 9)
!5840 = !DILocation(line: 0, scope: !5831)
!5841 = !DILocation(line: 2449, column: 9, scope: !5831)
!5842 = !DILocation(line: 2450, column: 16, scope: !5843)
!5843 = distinct !DILexicalBlock(scope: !5844, file: !3, line: 2449, column: 18)
!5844 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2449, column: 9)
!5845 = !DILocation(line: 0, scope: !99, inlinedAt: !5846)
!5846 = distinct !DILocation(line: 2451, column: 9, scope: !5843)
!5847 = !DILocation(line: 2452, column: 9, scope: !5843)
!5848 = !DILocation(line: 2455, column: 17, scope: !5849)
!5849 = distinct !DILexicalBlock(scope: !5850, file: !3, line: 2454, column: 18)
!5850 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2454, column: 9)
!5851 = !DILocation(line: 0, scope: !99, inlinedAt: !5852)
!5852 = distinct !DILocation(line: 2456, column: 9, scope: !5849)
!5853 = !DILocation(line: 2457, column: 9, scope: !5849)
!5854 = !DILocation(line: 2460, column: 15, scope: !5855)
!5855 = distinct !DILexicalBlock(scope: !5856, file: !3, line: 2459, column: 18)
!5856 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2459, column: 9)
!5857 = !DILocation(line: 0, scope: !99, inlinedAt: !5858)
!5858 = distinct !DILocation(line: 2461, column: 9, scope: !5855)
!5859 = !DILocation(line: 2462, column: 9, scope: !5855)
!5860 = !DILocation(line: 2465, column: 20, scope: !5861)
!5861 = distinct !DILexicalBlock(scope: !5862, file: !3, line: 2464, column: 18)
!5862 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2464, column: 9)
!5863 = !DILocation(line: 0, scope: !99, inlinedAt: !5864)
!5864 = distinct !DILocation(line: 2466, column: 9, scope: !5861)
!5865 = !DILocation(line: 2467, column: 9, scope: !5861)
!5866 = !DILocation(line: 2473, column: 21, scope: !5867)
!5867 = distinct !DILexicalBlock(scope: !5868, file: !3, line: 2472, column: 40)
!5868 = distinct !DILexicalBlock(scope: !5869, file: !3, line: 2472, column: 9)
!5869 = distinct !DILexicalBlock(scope: !5870, file: !3, line: 2472, column: 9)
!5870 = distinct !DILexicalBlock(scope: !5871, file: !3, line: 2469, column: 18)
!5871 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2469, column: 9)
!5872 = !DILocation(line: 0, scope: !99, inlinedAt: !5873)
!5873 = distinct !DILocation(line: 2475, column: 9, scope: !5870)
!5874 = !DILocation(line: 2476, column: 9, scope: !5870)
!5875 = !DILocation(line: 2480, column: 24, scope: !5876)
!5876 = distinct !DILexicalBlock(scope: !5877, file: !3, line: 2478, column: 18)
!5877 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2478, column: 9)
!5878 = !DILocation(line: 2481, column: 23, scope: !5876)
!5879 = !DILocation(line: 0, scope: !99, inlinedAt: !5880)
!5880 = distinct !DILocation(line: 2482, column: 9, scope: !5876)
!5881 = !DILocation(line: 2483, column: 9, scope: !5876)
!5882 = !DILocation(line: 0, scope: !5838)
!5883 = !DILocation(line: 2489, column: 17, scope: !5838)
!5884 = !DILocation(line: 0, scope: !99, inlinedAt: !5885)
!5885 = distinct !DILocation(line: 2491, column: 9, scope: !5838)
!5886 = !DILocation(line: 2498, column: 25, scope: !5887)
!5887 = distinct !DILexicalBlock(scope: !5888, file: !3, line: 2497, column: 41)
!5888 = distinct !DILexicalBlock(scope: !5889, file: !3, line: 2497, column: 9)
!5889 = distinct !DILexicalBlock(scope: !5890, file: !3, line: 2497, column: 9)
!5890 = distinct !DILexicalBlock(scope: !5891, file: !3, line: 2494, column: 18)
!5891 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2494, column: 9)
!5892 = !DILocation(line: 0, scope: !99, inlinedAt: !5893)
!5893 = distinct !DILocation(line: 2500, column: 9, scope: !5890)
!5894 = !DILocation(line: 2501, column: 9, scope: !5890)
!5895 = !DILocation(line: 2505, column: 16, scope: !5896)
!5896 = distinct !DILexicalBlock(scope: !5897, file: !3, line: 2503, column: 18)
!5897 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2503, column: 9)
!5898 = !DILocation(line: 2506, column: 17, scope: !5896)
!5899 = !DILocation(line: 2507, column: 16, scope: !5896)
!5900 = !DILocation(line: 2508, column: 17, scope: !5896)
!5901 = !DILocation(line: 0, scope: !99, inlinedAt: !5902)
!5902 = distinct !DILocation(line: 2509, column: 9, scope: !5896)
!5903 = !DILocation(line: 2510, column: 9, scope: !5896)
!5904 = !DILocation(line: 2514, column: 19, scope: !5905)
!5905 = distinct !DILexicalBlock(scope: !5906, file: !3, line: 2512, column: 18)
!5906 = distinct !DILexicalBlock(scope: !5831, file: !3, line: 2512, column: 9)
!5907 = !DILocation(line: 0, scope: !99, inlinedAt: !5908)
!5908 = distinct !DILocation(line: 2515, column: 9, scope: !5905)
!5909 = !DILocation(line: 2516, column: 9, scope: !5905)
!5910 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5840)
!5911 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5840)
!5912 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5840)
!5913 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5840)
!5914 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5840)
!5915 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5840)
!5916 = !DILocation(line: 2519, column: 1, scope: !5831)
!5917 = distinct !DISubprogram(name: "ternary_func1", scope: !3, file: !3, line: 2525, type: !296, scopeLine: 2525, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!5918 = !DILocation(line: 2525, column: 29, scope: !5917)
!5919 = distinct !DISubprogram(name: "ternary_func2", scope: !3, file: !3, line: 2526, type: !296, scopeLine: 2526, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!5920 = !DILocation(line: 2526, column: 29, scope: !5919)
!5921 = distinct !DISubprogram(name: "test_ternary_patterns", scope: !3, file: !3, line: 2528, type: !142, scopeLine: 2528, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !5922)
!5922 = !{!5923, !5924, !5925, !5926, !5927, !5928, !5931, !5934, !5937, !5940, !5941, !5942, !5945, !5946, !5949, !5950, !5953, !5954, !5957, !5958}
!5923 = !DILocalVariable(name: "apdu", arg: 1, scope: !5921, file: !3, line: 2528, type: !102)
!5924 = !DILocalVariable(name: "buffer", arg: 2, scope: !5921, file: !3, line: 2528, type: !104)
!5925 = !DILocalVariable(name: "p1", arg: 3, scope: !5921, file: !3, line: 2528, type: !5)
!5926 = !DILocalVariable(name: "a", scope: !5921, file: !3, line: 2529, type: !8)
!5927 = !DILocalVariable(name: "b", scope: !5921, file: !3, line: 2530, type: !8)
!5928 = !DILocalVariable(name: "x", scope: !5929, file: !3, line: 2544, type: !8)
!5929 = distinct !DILexicalBlock(scope: !5930, file: !3, line: 2542, column: 18)
!5930 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2542, column: 9)
!5931 = !DILocalVariable(name: "x", scope: !5932, file: !3, line: 2550, type: !8)
!5932 = distinct !DILexicalBlock(scope: !5933, file: !3, line: 2548, column: 18)
!5933 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2548, column: 9)
!5934 = !DILocalVariable(name: "cond", scope: !5935, file: !3, line: 2556, type: !8)
!5935 = distinct !DILexicalBlock(scope: !5936, file: !3, line: 2554, column: 18)
!5936 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2554, column: 9)
!5937 = !DILocalVariable(name: "cond", scope: !5938, file: !3, line: 2564, type: !8)
!5938 = distinct !DILexicalBlock(scope: !5939, file: !3, line: 2560, column: 18)
!5939 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2560, column: 9)
!5940 = !DILocalVariable(name: "i", scope: !5938, file: !3, line: 2565, type: !8)
!5941 = !DILocalVariable(name: "j", scope: !5938, file: !3, line: 2565, type: !8)
!5942 = !DILocalVariable(name: "c", scope: !5943, file: !3, line: 2571, type: !8)
!5943 = distinct !DILexicalBlock(scope: !5944, file: !3, line: 2569, column: 18)
!5944 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2569, column: 9)
!5945 = !DILocalVariable(name: "d", scope: !5943, file: !3, line: 2571, type: !8)
!5946 = !DILocalVariable(name: "x", scope: !5947, file: !3, line: 2577, type: !8)
!5947 = distinct !DILexicalBlock(scope: !5948, file: !3, line: 2575, column: 18)
!5948 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2575, column: 9)
!5949 = !DILocalVariable(name: "max", scope: !5947, file: !3, line: 2578, type: !8)
!5950 = !DILocalVariable(name: "x", scope: !5951, file: !3, line: 2585, type: !8)
!5951 = distinct !DILexicalBlock(scope: !5952, file: !3, line: 2583, column: 18)
!5952 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2583, column: 9)
!5953 = !DILocalVariable(name: "min", scope: !5951, file: !3, line: 2586, type: !8)
!5954 = !DILocalVariable(name: "flag", scope: !5955, file: !3, line: 2593, type: !8)
!5955 = distinct !DILexicalBlock(scope: !5956, file: !3, line: 2591, column: 18)
!5956 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2591, column: 9)
!5957 = !DILocalVariable(name: "val", scope: !5955, file: !3, line: 2594, type: !8)
!5958 = !DILocalVariable(name: "MASK", scope: !5955, file: !3, line: 2595, type: !8)
!5959 = !DILocation(line: 0, scope: !5921)
!5960 = !DILocation(line: 2532, column: 9, scope: !5921)
!5961 = !DILocation(line: 0, scope: !99, inlinedAt: !5962)
!5962 = distinct !DILocation(line: 2539, column: 9, scope: !5963)
!5963 = distinct !DILexicalBlock(scope: !5964, file: !3, line: 2537, column: 18)
!5964 = distinct !DILexicalBlock(scope: !5921, file: !3, line: 2537, column: 9)
!5965 = !DILocation(line: 2540, column: 9, scope: !5963)
!5966 = !DILocation(line: 0, scope: !5929)
!5967 = !DILocation(line: 0, scope: !99, inlinedAt: !5968)
!5968 = distinct !DILocation(line: 2545, column: 9, scope: !5929)
!5969 = !DILocation(line: 0, scope: !5932)
!5970 = !DILocation(line: 0, scope: !99, inlinedAt: !5971)
!5971 = distinct !DILocation(line: 2551, column: 9, scope: !5932)
!5972 = !DILocation(line: 0, scope: !5935)
!5973 = !DILocation(line: 0, scope: !99, inlinedAt: !5974)
!5974 = distinct !DILocation(line: 2557, column: 9, scope: !5935)
!5975 = !DILocation(line: 2562, column: 21, scope: !5938)
!5976 = !DILocation(line: 2563, column: 21, scope: !5938)
!5977 = !DILocation(line: 0, scope: !5938)
!5978 = !DILocation(line: 0, scope: !99, inlinedAt: !5979)
!5979 = distinct !DILocation(line: 2566, column: 9, scope: !5938)
!5980 = !DILocation(line: 0, scope: !5943)
!5981 = !DILocation(line: 0, scope: !99, inlinedAt: !5982)
!5982 = distinct !DILocation(line: 2572, column: 9, scope: !5943)
!5983 = !DILocation(line: 0, scope: !5947)
!5984 = !DILocation(line: 0, scope: !99, inlinedAt: !5985)
!5985 = distinct !DILocation(line: 2580, column: 9, scope: !5947)
!5986 = !DILocation(line: 0, scope: !5951)
!5987 = !DILocation(line: 0, scope: !99, inlinedAt: !5988)
!5988 = distinct !DILocation(line: 2588, column: 9, scope: !5951)
!5989 = !DILocation(line: 0, scope: !5955)
!5990 = !DILocation(line: 0, scope: !99, inlinedAt: !5991)
!5991 = distinct !DILocation(line: 2597, column: 9, scope: !5955)
!5992 = !DILocation(line: 0, scope: !99, inlinedAt: !5993)
!5993 = distinct !DILocation(line: 2600, column: 5, scope: !5921)
!5994 = !DILocation(line: 2601, column: 1, scope: !5921)
!5995 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !5959)
!5996 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !5959)
!5997 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !5959)
!5998 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !5959)
!5999 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !5959)
!6000 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !5959)
!6001 = distinct !DISubprogram(name: "test_mul_div_edge", scope: !3, file: !3, line: 2607, type: !142, scopeLine: 2607, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !6002)
!6002 = !{!6003, !6004, !6005, !6006, !6007}
!6003 = !DILocalVariable(name: "apdu", arg: 1, scope: !6001, file: !3, line: 2607, type: !102)
!6004 = !DILocalVariable(name: "buffer", arg: 2, scope: !6001, file: !3, line: 2607, type: !104)
!6005 = !DILocalVariable(name: "p1", arg: 3, scope: !6001, file: !3, line: 2607, type: !5)
!6006 = !DILocalVariable(name: "a", scope: !6001, file: !3, line: 2608, type: !8)
!6007 = !DILocalVariable(name: "b", scope: !6001, file: !3, line: 2609, type: !8)
!6008 = !DILocation(line: 0, scope: !6001)
!6009 = !DILocation(line: 2611, column: 9, scope: !6001)
!6010 = !DILocation(line: 0, scope: !99, inlinedAt: !6011)
!6011 = distinct !DILocation(line: 2612, column: 20, scope: !6012)
!6012 = distinct !DILexicalBlock(scope: !6013, file: !3, line: 2612, column: 18)
!6013 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2612, column: 9)
!6014 = !DILocation(line: 2612, column: 57, scope: !6012)
!6015 = !DILocation(line: 0, scope: !99, inlinedAt: !6016)
!6016 = distinct !DILocation(line: 2613, column: 38, scope: !6017)
!6017 = distinct !DILexicalBlock(scope: !6018, file: !3, line: 2613, column: 18)
!6018 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2613, column: 9)
!6019 = !DILocation(line: 2613, column: 71, scope: !6017)
!6020 = !DILocation(line: 0, scope: !99, inlinedAt: !6021)
!6021 = distinct !DILocation(line: 2614, column: 36, scope: !6022)
!6022 = distinct !DILexicalBlock(scope: !6023, file: !3, line: 2614, column: 18)
!6023 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2614, column: 9)
!6024 = !DILocation(line: 2614, column: 69, scope: !6022)
!6025 = !DILocation(line: 0, scope: !99, inlinedAt: !6026)
!6026 = distinct !DILocation(line: 2615, column: 37, scope: !6027)
!6027 = distinct !DILexicalBlock(scope: !6028, file: !3, line: 2615, column: 18)
!6028 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2615, column: 9)
!6029 = !DILocation(line: 2615, column: 70, scope: !6027)
!6030 = !DILocation(line: 0, scope: !99, inlinedAt: !6031)
!6031 = distinct !DILocation(line: 2616, column: 20, scope: !6032)
!6032 = distinct !DILexicalBlock(scope: !6033, file: !3, line: 2616, column: 18)
!6033 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2616, column: 9)
!6034 = !DILocation(line: 2616, column: 55, scope: !6032)
!6035 = !DILocation(line: 0, scope: !99, inlinedAt: !6036)
!6036 = distinct !DILocation(line: 2617, column: 20, scope: !6037)
!6037 = distinct !DILexicalBlock(scope: !6038, file: !3, line: 2617, column: 18)
!6038 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2617, column: 9)
!6039 = !DILocation(line: 2617, column: 55, scope: !6037)
!6040 = !DILocation(line: 0, scope: !99, inlinedAt: !6041)
!6041 = distinct !DILocation(line: 2618, column: 37, scope: !6042)
!6042 = distinct !DILexicalBlock(scope: !6043, file: !3, line: 2618, column: 18)
!6043 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2618, column: 9)
!6044 = !DILocation(line: 2618, column: 70, scope: !6042)
!6045 = !DILocation(line: 0, scope: !99, inlinedAt: !6046)
!6046 = distinct !DILocation(line: 2619, column: 37, scope: !6047)
!6047 = distinct !DILexicalBlock(scope: !6048, file: !3, line: 2619, column: 18)
!6048 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2619, column: 9)
!6049 = !DILocation(line: 2619, column: 70, scope: !6047)
!6050 = !DILocation(line: 0, scope: !99, inlinedAt: !6051)
!6051 = distinct !DILocation(line: 2620, column: 20, scope: !6052)
!6052 = distinct !DILexicalBlock(scope: !6053, file: !3, line: 2620, column: 18)
!6053 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2620, column: 9)
!6054 = !DILocation(line: 2620, column: 53, scope: !6052)
!6055 = !DILocation(line: 0, scope: !99, inlinedAt: !6056)
!6056 = distinct !DILocation(line: 2621, column: 21, scope: !6057)
!6057 = distinct !DILexicalBlock(scope: !6058, file: !3, line: 2621, column: 19)
!6058 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2621, column: 9)
!6059 = !DILocation(line: 2621, column: 54, scope: !6057)
!6060 = !DILocation(line: 0, scope: !99, inlinedAt: !6061)
!6061 = distinct !DILocation(line: 2622, column: 32, scope: !6062)
!6062 = distinct !DILexicalBlock(scope: !6063, file: !3, line: 2622, column: 19)
!6063 = distinct !DILexicalBlock(scope: !6001, file: !3, line: 2622, column: 9)
!6064 = !DILocation(line: 2622, column: 65, scope: !6062)
!6065 = !DILocation(line: 0, scope: !99, inlinedAt: !6066)
!6066 = distinct !DILocation(line: 2623, column: 5, scope: !6001)
!6067 = !DILocation(line: 2624, column: 1, scope: !6001)
!6068 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !6008)
!6069 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6008)
!6070 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !6008)
!6071 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !6008)
!6072 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !6008)
!6073 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !6008)
!6074 = distinct !DISubprogram(name: "lcg_next", scope: !3, file: !3, line: 2632, type: !296, scopeLine: 2632, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2)
!6075 = !DILocation(line: 2634, column: 19, scope: !6074)
!6076 = !DILocation(line: 2634, column: 30, scope: !6074)
!6077 = !DILocation(line: 2634, column: 38, scope: !6074)
!6078 = !DILocation(line: 2634, column: 47, scope: !6074)
!6079 = !DILocation(line: 2634, column: 16, scope: !6074)
!6080 = !DILocation(line: 2635, column: 5, scope: !6074)
!6081 = distinct !DISubprogram(name: "test_rng", scope: !3, file: !3, line: 2638, type: !142, scopeLine: 2638, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !6082)
!6082 = !{!6083, !6084, !6085, !6086, !6087, !6090, !6093, !6096, !6097, !6098, !6101, !6104, !6107}
!6083 = !DILocalVariable(name: "apdu", arg: 1, scope: !6081, file: !3, line: 2638, type: !102)
!6084 = !DILocalVariable(name: "buffer", arg: 2, scope: !6081, file: !3, line: 2638, type: !104)
!6085 = !DILocalVariable(name: "p1", arg: 3, scope: !6081, file: !3, line: 2638, type: !5)
!6086 = !DILocalVariable(name: "i", scope: !6081, file: !3, line: 2639, type: !8)
!6087 = !DILocalVariable(name: "val", scope: !6088, file: !3, line: 2659, type: !8)
!6088 = distinct !DILexicalBlock(scope: !6089, file: !3, line: 2656, column: 18)
!6089 = distinct !DILexicalBlock(scope: !6081, file: !3, line: 2656, column: 9)
!6090 = !DILocalVariable(name: "val", scope: !6091, file: !3, line: 2666, type: !8)
!6091 = distinct !DILexicalBlock(scope: !6092, file: !3, line: 2663, column: 18)
!6092 = distinct !DILexicalBlock(scope: !6081, file: !3, line: 2663, column: 9)
!6093 = !DILocalVariable(name: "val", scope: !6094, file: !3, line: 2673, type: !8)
!6094 = distinct !DILexicalBlock(scope: !6095, file: !3, line: 2670, column: 18)
!6095 = distinct !DILexicalBlock(scope: !6081, file: !3, line: 2670, column: 9)
!6096 = !DILocalVariable(name: "min", scope: !6094, file: !3, line: 2674, type: !8)
!6097 = !DILocalVariable(name: "max", scope: !6094, file: !3, line: 2674, type: !8)
!6098 = !DILocalVariable(name: "val", scope: !6099, file: !3, line: 2681, type: !8)
!6099 = distinct !DILexicalBlock(scope: !6100, file: !3, line: 2678, column: 18)
!6100 = distinct !DILexicalBlock(scope: !6081, file: !3, line: 2678, column: 9)
!6101 = !DILocalVariable(name: "val", scope: !6102, file: !3, line: 2688, type: !8)
!6102 = distinct !DILexicalBlock(scope: !6103, file: !3, line: 2685, column: 18)
!6103 = distinct !DILexicalBlock(scope: !6081, file: !3, line: 2685, column: 9)
!6104 = !DILocalVariable(name: "v1", scope: !6105, file: !3, line: 2695, type: !8)
!6105 = distinct !DILexicalBlock(scope: !6106, file: !3, line: 2692, column: 18)
!6106 = distinct !DILexicalBlock(scope: !6081, file: !3, line: 2692, column: 9)
!6107 = !DILocalVariable(name: "v2", scope: !6105, file: !3, line: 2697, type: !8)
!6108 = !DILocation(line: 0, scope: !6081)
!6109 = !DILocation(line: 2641, column: 9, scope: !6081)
!6110 = !DILocation(line: 0, scope: !99, inlinedAt: !6111)
!6111 = distinct !DILocation(line: 2653, column: 9, scope: !6112)
!6112 = distinct !DILexicalBlock(scope: !6113, file: !3, line: 2647, column: 18)
!6113 = distinct !DILexicalBlock(scope: !6081, file: !3, line: 2647, column: 9)
!6114 = !DILocation(line: 2654, column: 9, scope: !6112)
!6115 = !DILocation(line: 0, scope: !6088)
!6116 = !DILocation(line: 0, scope: !99, inlinedAt: !6117)
!6117 = distinct !DILocation(line: 2660, column: 9, scope: !6088)
!6118 = !DILocation(line: 0, scope: !6091)
!6119 = !DILocation(line: 0, scope: !99, inlinedAt: !6120)
!6120 = distinct !DILocation(line: 2667, column: 9, scope: !6091)
!6121 = !DILocation(line: 0, scope: !6094)
!6122 = !DILocation(line: 0, scope: !99, inlinedAt: !6123)
!6123 = distinct !DILocation(line: 2675, column: 9, scope: !6094)
!6124 = !DILocation(line: 0, scope: !6099)
!6125 = !DILocation(line: 0, scope: !99, inlinedAt: !6126)
!6126 = distinct !DILocation(line: 2682, column: 9, scope: !6099)
!6127 = !DILocation(line: 0, scope: !6102)
!6128 = !DILocation(line: 0, scope: !99, inlinedAt: !6129)
!6129 = distinct !DILocation(line: 2689, column: 9, scope: !6102)
!6130 = !DILocation(line: 0, scope: !6105)
!6131 = !DILocation(line: 0, scope: !99, inlinedAt: !6132)
!6132 = distinct !DILocation(line: 2698, column: 9, scope: !6105)
!6133 = !DILocation(line: 2634, column: 16, scope: !6074, inlinedAt: !6108)
!6134 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6108)
!6135 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !6108)
!6136 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !6108)
!6137 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !6108)
!6138 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !6108)
!6139 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !6108)
!6140 = !DILocation(line: 2702, column: 1, scope: !6081)
!6141 = distinct !DISubprogram(name: "test_state_machine", scope: !3, file: !3, line: 2715, type: !142, scopeLine: 2715, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !6142)
!6142 = !{!6143, !6144, !6145, !6146, !6149, !6152, !6155, !6158}
!6143 = !DILocalVariable(name: "apdu", arg: 1, scope: !6141, file: !3, line: 2715, type: !102)
!6144 = !DILocalVariable(name: "buffer", arg: 2, scope: !6141, file: !3, line: 2715, type: !104)
!6145 = !DILocalVariable(name: "p1", arg: 3, scope: !6141, file: !3, line: 2715, type: !5)
!6146 = !DILocalVariable(name: "prev", scope: !6147, file: !3, line: 2743, type: !8)
!6147 = distinct !DILexicalBlock(scope: !6148, file: !3, line: 2740, column: 18)
!6148 = distinct !DILexicalBlock(scope: !6141, file: !3, line: 2740, column: 9)
!6149 = !DILocalVariable(name: "result", scope: !6150, file: !3, line: 2753, type: !8)
!6150 = distinct !DILexicalBlock(scope: !6151, file: !3, line: 2750, column: 18)
!6151 = distinct !DILexicalBlock(scope: !6141, file: !3, line: 2750, column: 9)
!6152 = !DILocalVariable(name: "result", scope: !6153, file: !3, line: 2763, type: !8)
!6153 = distinct !DILexicalBlock(scope: !6154, file: !3, line: 2760, column: 18)
!6154 = distinct !DILexicalBlock(scope: !6141, file: !3, line: 2760, column: 9)
!6155 = !DILocalVariable(name: "result", scope: !6156, file: !3, line: 2776, type: !8)
!6156 = distinct !DILexicalBlock(scope: !6157, file: !3, line: 2773, column: 18)
!6157 = distinct !DILexicalBlock(scope: !6141, file: !3, line: 2773, column: 9)
!6158 = !DILocalVariable(name: "i", scope: !6159, file: !3, line: 2793, type: !8)
!6159 = distinct !DILexicalBlock(scope: !6160, file: !3, line: 2789, column: 18)
!6160 = distinct !DILexicalBlock(scope: !6141, file: !3, line: 2789, column: 9)
!6161 = !DILocation(line: 0, scope: !6141)
!6162 = !DILocation(line: 2716, column: 9, scope: !6141)
!6163 = !DILocation(line: 2718, column: 17, scope: !6164)
!6164 = distinct !DILexicalBlock(scope: !6165, file: !3, line: 2716, column: 18)
!6165 = distinct !DILexicalBlock(scope: !6141, file: !3, line: 2716, column: 9)
!6166 = !DILocation(line: 0, scope: !99, inlinedAt: !6167)
!6167 = distinct !DILocation(line: 2719, column: 9, scope: !6164)
!6168 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6167)
!6169 = !DILocation(line: 2720, column: 9, scope: !6164)
!6170 = !DILocation(line: 0, scope: !6171)
!6171 = distinct !DILexicalBlock(scope: !6172, file: !3, line: 2722, column: 18)
!6172 = distinct !DILexicalBlock(scope: !6141, file: !3, line: 2722, column: 9)
!6173 = !DILocation(line: 0, scope: !99, inlinedAt: !6174)
!6174 = distinct !DILocation(line: 2728, column: 9, scope: !6171)
!6175 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6174)
!6176 = !DILocation(line: 2729, column: 9, scope: !6171)
!6177 = !DILocation(line: 0, scope: !6178)
!6178 = distinct !DILexicalBlock(scope: !6179, file: !3, line: 2731, column: 18)
!6179 = distinct !DILexicalBlock(scope: !6141, file: !3, line: 2731, column: 9)
!6180 = !DILocation(line: 0, scope: !99, inlinedAt: !6181)
!6181 = distinct !DILocation(line: 2737, column: 9, scope: !6178)
!6182 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6181)
!6183 = !DILocation(line: 2738, column: 9, scope: !6178)
!6184 = !DILocation(line: 2742, column: 17, scope: !6147)
!6185 = !DILocation(line: 0, scope: !6147)
!6186 = !DILocation(line: 0, scope: !99, inlinedAt: !6187)
!6187 = distinct !DILocation(line: 2747, column: 9, scope: !6147)
!6188 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6187)
!6189 = !DILocation(line: 2752, column: 17, scope: !6150)
!6190 = !DILocation(line: 0, scope: !6150)
!6191 = !DILocation(line: 0, scope: !99, inlinedAt: !6192)
!6192 = distinct !DILocation(line: 2757, column: 9, scope: !6150)
!6193 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6192)
!6194 = !DILocation(line: 2762, column: 17, scope: !6153)
!6195 = !DILocation(line: 0, scope: !6153)
!6196 = !DILocation(line: 0, scope: !99, inlinedAt: !6197)
!6197 = distinct !DILocation(line: 2770, column: 9, scope: !6153)
!6198 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6197)
!6199 = !DILocation(line: 2775, column: 17, scope: !6156)
!6200 = !DILocation(line: 0, scope: !6156)
!6201 = !DILocation(line: 0, scope: !99, inlinedAt: !6202)
!6202 = distinct !DILocation(line: 2786, column: 9, scope: !6156)
!6203 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6202)
!6204 = !DILocation(line: 2791, column: 17, scope: !6159)
!6205 = !DILocation(line: 2792, column: 17, scope: !6159)
!6206 = !DILocation(line: 0, scope: !6159)
!6207 = !DILocation(line: 2794, column: 9, scope: !6208)
!6208 = distinct !DILexicalBlock(scope: !6159, file: !3, line: 2794, column: 9)
!6209 = !DILocation(line: 2795, column: 31, scope: !6210)
!6210 = distinct !DILexicalBlock(scope: !6211, file: !3, line: 2794, column: 40)
!6211 = distinct !DILexicalBlock(scope: !6208, file: !3, line: 2794, column: 9)
!6212 = !DILocation(line: 2796, column: 25, scope: !6213)
!6213 = distinct !DILexicalBlock(scope: !6210, file: !3, line: 2796, column: 17)
!6214 = !DILocation(line: 2796, column: 17, scope: !6210)
!6215 = !DILocation(line: 2797, column: 25, scope: !6216)
!6216 = distinct !DILexicalBlock(scope: !6213, file: !3, line: 2796, column: 31)
!6217 = !DILocation(line: 2798, column: 13, scope: !6216)
!6218 = !DILocation(line: 2794, column: 21, scope: !6211)
!6219 = !DILocation(line: 2794, column: 23, scope: !6211)
!6220 = distinct !{!6220, !6207, !6221, !312, !313}
!6221 = !DILocation(line: 2799, column: 9, scope: !6208)
!6222 = !DILocation(line: 2795, column: 21, scope: !6210)
!6223 = !DILocation(line: 2800, column: 34, scope: !6159)
!6224 = !DILocation(line: 2800, column: 42, scope: !6159)
!6225 = !DILocation(line: 2800, column: 47, scope: !6159)
!6226 = !DILocation(line: 0, scope: !99, inlinedAt: !6227)
!6227 = distinct !DILocation(line: 2800, column: 9, scope: !6159)
!6228 = !DILocation(line: 92, column: 31, scope: !99, inlinedAt: !6227)
!6229 = !DILocation(line: 92, column: 17, scope: !99, inlinedAt: !6227)
!6230 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6227)
!6231 = !DILocation(line: 93, column: 17, scope: !99, inlinedAt: !6227)
!6232 = !DILocation(line: 0, scope: !99, inlinedAt: !6233)
!6233 = distinct !DILocation(line: 2803, column: 5, scope: !6141)
!6234 = !DILocation(line: 92, column: 15, scope: !99, inlinedAt: !6233)
!6235 = !DILocation(line: 2804, column: 1, scope: !6141)
!6236 = !DILocation(line: 93, column: 5, scope: !99, inlinedAt: !6161)
!6237 = !DILocation(line: 93, column: 15, scope: !99, inlinedAt: !6161)
!6238 = !DILocation(line: 94, column: 5, scope: !99, inlinedAt: !6161)
!6239 = !DILocation(line: 95, column: 5, scope: !99, inlinedAt: !6161)
!6240 = !DILocation(line: 96, column: 5, scope: !99, inlinedAt: !6161)
!6241 = distinct !DISubprogram(name: "process", scope: !3, file: !3, line: 2811, type: !127, scopeLine: 2811, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !2, retainedNodes: !6242)
!6242 = !{!6243, !6244, !6245, !6246, !6247}
!6243 = !DILocalVariable(name: "apdu", arg: 1, scope: !6241, file: !3, line: 2811, type: !102)
!6244 = !DILocalVariable(name: "len", arg: 2, scope: !6241, file: !3, line: 2811, type: !8)
!6245 = !DILocalVariable(name: "buffer", scope: !6241, file: !3, line: 2812, type: !104)
!6246 = !DILocalVariable(name: "ins", scope: !6241, file: !3, line: 2813, type: !5)
!6247 = !DILocalVariable(name: "p1", scope: !6241, file: !3, line: 2814, type: !5)
!6248 = !DILocation(line: 0, scope: !6241)
!6249 = !DILocation(line: 2812, column: 20, scope: !6241)
!6250 = !DILocation(line: 2813, column: 16, scope: !6241)
!6251 = !DILocation(line: 2814, column: 15, scope: !6241)
!6252 = !DILocation(line: 2818, column: 9, scope: !6241)
!6253 = !DILocation(line: 2818, column: 24, scope: !6254)
!6254 = distinct !DILexicalBlock(scope: !6255, file: !3, line: 2818, column: 22)
!6255 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2818, column: 9)
!6256 = !DILocation(line: 2818, column: 59, scope: !6254)
!6257 = !DILocation(line: 2819, column: 24, scope: !6258)
!6258 = distinct !DILexicalBlock(scope: !6259, file: !3, line: 2819, column: 22)
!6259 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2819, column: 9)
!6260 = !DILocation(line: 2819, column: 56, scope: !6258)
!6261 = !DILocation(line: 2820, column: 24, scope: !6262)
!6262 = distinct !DILexicalBlock(scope: !6263, file: !3, line: 2820, column: 22)
!6263 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2820, column: 9)
!6264 = !DILocation(line: 2820, column: 59, scope: !6262)
!6265 = !DILocation(line: 2821, column: 24, scope: !6266)
!6266 = distinct !DILexicalBlock(scope: !6267, file: !3, line: 2821, column: 22)
!6267 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2821, column: 9)
!6268 = !DILocation(line: 2821, column: 56, scope: !6266)
!6269 = !DILocation(line: 2822, column: 24, scope: !6270)
!6270 = distinct !DILexicalBlock(scope: !6271, file: !3, line: 2822, column: 22)
!6271 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2822, column: 9)
!6272 = !DILocation(line: 2822, column: 55, scope: !6270)
!6273 = !DILocation(line: 2823, column: 24, scope: !6274)
!6274 = distinct !DILexicalBlock(scope: !6275, file: !3, line: 2823, column: 22)
!6275 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2823, column: 9)
!6276 = !DILocation(line: 2823, column: 56, scope: !6274)
!6277 = !DILocation(line: 2824, column: 24, scope: !6278)
!6278 = distinct !DILexicalBlock(scope: !6279, file: !3, line: 2824, column: 22)
!6279 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2824, column: 9)
!6280 = !DILocation(line: 2824, column: 54, scope: !6278)
!6281 = !DILocation(line: 2825, column: 24, scope: !6282)
!6282 = distinct !DILexicalBlock(scope: !6283, file: !3, line: 2825, column: 22)
!6283 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2825, column: 9)
!6284 = !DILocation(line: 2825, column: 56, scope: !6282)
!6285 = !DILocation(line: 2830, column: 24, scope: !6286)
!6286 = distinct !DILexicalBlock(scope: !6287, file: !3, line: 2830, column: 22)
!6287 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2830, column: 9)
!6288 = !DILocation(line: 2830, column: 54, scope: !6286)
!6289 = !DILocation(line: 2831, column: 24, scope: !6290)
!6290 = distinct !DILexicalBlock(scope: !6291, file: !3, line: 2831, column: 22)
!6291 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2831, column: 9)
!6292 = !DILocation(line: 2831, column: 56, scope: !6290)
!6293 = !DILocation(line: 2832, column: 24, scope: !6294)
!6294 = distinct !DILexicalBlock(scope: !6295, file: !3, line: 2832, column: 22)
!6295 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2832, column: 9)
!6296 = !DILocation(line: 2832, column: 55, scope: !6294)
!6297 = !DILocation(line: 2833, column: 24, scope: !6298)
!6298 = distinct !DILexicalBlock(scope: !6299, file: !3, line: 2833, column: 22)
!6299 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2833, column: 9)
!6300 = !DILocation(line: 2833, column: 56, scope: !6298)
!6301 = !DILocation(line: 2834, column: 24, scope: !6302)
!6302 = distinct !DILexicalBlock(scope: !6303, file: !3, line: 2834, column: 22)
!6303 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2834, column: 9)
!6304 = !DILocation(line: 2834, column: 58, scope: !6302)
!6305 = !DILocation(line: 2835, column: 24, scope: !6306)
!6306 = distinct !DILexicalBlock(scope: !6307, file: !3, line: 2835, column: 22)
!6307 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2835, column: 9)
!6308 = !DILocation(line: 2835, column: 58, scope: !6306)
!6309 = !DILocation(line: 2836, column: 24, scope: !6310)
!6310 = distinct !DILexicalBlock(scope: !6311, file: !3, line: 2836, column: 22)
!6311 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2836, column: 9)
!6312 = !DILocation(line: 2836, column: 56, scope: !6310)
!6313 = !DILocation(line: 2837, column: 24, scope: !6314)
!6314 = distinct !DILexicalBlock(scope: !6315, file: !3, line: 2837, column: 22)
!6315 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2837, column: 9)
!6316 = !DILocation(line: 2837, column: 53, scope: !6314)
!6317 = !DILocation(line: 2838, column: 24, scope: !6318)
!6318 = distinct !DILexicalBlock(scope: !6319, file: !3, line: 2838, column: 22)
!6319 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2838, column: 9)
!6320 = !DILocation(line: 2838, column: 61, scope: !6318)
!6321 = !DILocation(line: 2839, column: 24, scope: !6322)
!6322 = distinct !DILexicalBlock(scope: !6323, file: !3, line: 2839, column: 22)
!6323 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2839, column: 9)
!6324 = !DILocation(line: 2839, column: 63, scope: !6322)
!6325 = !DILocation(line: 2840, column: 24, scope: !6326)
!6326 = distinct !DILexicalBlock(scope: !6327, file: !3, line: 2840, column: 22)
!6327 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2840, column: 9)
!6328 = !DILocation(line: 2840, column: 61, scope: !6326)
!6329 = !DILocation(line: 2841, column: 24, scope: !6330)
!6330 = distinct !DILexicalBlock(scope: !6331, file: !3, line: 2841, column: 22)
!6331 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2841, column: 9)
!6332 = !DILocation(line: 2841, column: 64, scope: !6330)
!6333 = !DILocation(line: 2846, column: 24, scope: !6334)
!6334 = distinct !DILexicalBlock(scope: !6335, file: !3, line: 2846, column: 22)
!6335 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2846, column: 9)
!6336 = !DILocation(line: 2846, column: 57, scope: !6334)
!6337 = !DILocation(line: 2847, column: 24, scope: !6338)
!6338 = distinct !DILexicalBlock(scope: !6339, file: !3, line: 2847, column: 22)
!6339 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2847, column: 9)
!6340 = !DILocation(line: 2847, column: 62, scope: !6338)
!6341 = !DILocation(line: 2848, column: 24, scope: !6342)
!6342 = distinct !DILexicalBlock(scope: !6343, file: !3, line: 2848, column: 22)
!6343 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2848, column: 9)
!6344 = !DILocation(line: 2848, column: 57, scope: !6342)
!6345 = !DILocation(line: 2849, column: 24, scope: !6346)
!6346 = distinct !DILexicalBlock(scope: !6347, file: !3, line: 2849, column: 22)
!6347 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2849, column: 9)
!6348 = !DILocation(line: 2849, column: 61, scope: !6346)
!6349 = !DILocation(line: 2850, column: 24, scope: !6350)
!6350 = distinct !DILexicalBlock(scope: !6351, file: !3, line: 2850, column: 22)
!6351 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2850, column: 9)
!6352 = !DILocation(line: 2850, column: 62, scope: !6350)
!6353 = !DILocation(line: 2851, column: 24, scope: !6354)
!6354 = distinct !DILexicalBlock(scope: !6355, file: !3, line: 2851, column: 22)
!6355 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2851, column: 9)
!6356 = !DILocation(line: 2851, column: 63, scope: !6354)
!6357 = !DILocation(line: 2852, column: 24, scope: !6358)
!6358 = distinct !DILexicalBlock(scope: !6359, file: !3, line: 2852, column: 22)
!6359 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2852, column: 9)
!6360 = !DILocation(line: 2852, column: 64, scope: !6358)
!6361 = !DILocation(line: 2857, column: 24, scope: !6362)
!6362 = distinct !DILexicalBlock(scope: !6363, file: !3, line: 2857, column: 22)
!6363 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2857, column: 9)
!6364 = !DILocation(line: 2857, column: 61, scope: !6362)
!6365 = !DILocation(line: 2858, column: 24, scope: !6366)
!6366 = distinct !DILexicalBlock(scope: !6367, file: !3, line: 2858, column: 22)
!6367 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2858, column: 9)
!6368 = !DILocation(line: 2858, column: 60, scope: !6366)
!6369 = !DILocation(line: 2859, column: 24, scope: !6370)
!6370 = distinct !DILexicalBlock(scope: !6371, file: !3, line: 2859, column: 22)
!6371 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2859, column: 9)
!6372 = !DILocation(line: 2859, column: 59, scope: !6370)
!6373 = !DILocation(line: 2860, column: 24, scope: !6374)
!6374 = distinct !DILexicalBlock(scope: !6375, file: !3, line: 2860, column: 22)
!6375 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2860, column: 9)
!6376 = !DILocation(line: 2860, column: 61, scope: !6374)
!6377 = !DILocation(line: 2861, column: 24, scope: !6378)
!6378 = distinct !DILexicalBlock(scope: !6379, file: !3, line: 2861, column: 22)
!6379 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2861, column: 9)
!6380 = !DILocation(line: 2861, column: 58, scope: !6378)
!6381 = !DILocation(line: 2862, column: 24, scope: !6382)
!6382 = distinct !DILexicalBlock(scope: !6383, file: !3, line: 2862, column: 22)
!6383 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2862, column: 9)
!6384 = !DILocation(line: 2862, column: 55, scope: !6382)
!6385 = !DILocation(line: 2867, column: 24, scope: !6386)
!6386 = distinct !DILexicalBlock(scope: !6387, file: !3, line: 2867, column: 22)
!6387 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2867, column: 9)
!6388 = !DILocation(line: 2867, column: 67, scope: !6386)
!6389 = !DILocation(line: 2868, column: 24, scope: !6390)
!6390 = distinct !DILexicalBlock(scope: !6391, file: !3, line: 2868, column: 22)
!6391 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2868, column: 9)
!6392 = !DILocation(line: 2868, column: 60, scope: !6390)
!6393 = !DILocation(line: 2869, column: 24, scope: !6394)
!6394 = distinct !DILexicalBlock(scope: !6395, file: !3, line: 2869, column: 22)
!6395 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2869, column: 9)
!6396 = !DILocation(line: 2869, column: 60, scope: !6394)
!6397 = !DILocation(line: 2870, column: 24, scope: !6398)
!6398 = distinct !DILexicalBlock(scope: !6399, file: !3, line: 2870, column: 22)
!6399 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2870, column: 9)
!6400 = !DILocation(line: 2870, column: 65, scope: !6398)
!6401 = !DILocation(line: 2871, column: 24, scope: !6402)
!6402 = distinct !DILexicalBlock(scope: !6403, file: !3, line: 2871, column: 22)
!6403 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2871, column: 9)
!6404 = !DILocation(line: 2871, column: 60, scope: !6402)
!6405 = !DILocation(line: 2872, column: 24, scope: !6406)
!6406 = distinct !DILexicalBlock(scope: !6407, file: !3, line: 2872, column: 22)
!6407 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2872, column: 9)
!6408 = !DILocation(line: 2872, column: 62, scope: !6406)
!6409 = !DILocation(line: 2878, column: 24, scope: !6410)
!6410 = distinct !DILexicalBlock(scope: !6411, file: !3, line: 2878, column: 22)
!6411 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2878, column: 9)
!6412 = !DILocation(line: 2878, column: 62, scope: !6410)
!6413 = !DILocation(line: 2881, column: 24, scope: !6414)
!6414 = distinct !DILexicalBlock(scope: !6415, file: !3, line: 2881, column: 22)
!6415 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2881, column: 9)
!6416 = !DILocation(line: 2881, column: 65, scope: !6414)
!6417 = !DILocation(line: 2884, column: 24, scope: !6418)
!6418 = distinct !DILexicalBlock(scope: !6419, file: !3, line: 2884, column: 22)
!6419 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2884, column: 9)
!6420 = !DILocation(line: 2884, column: 68, scope: !6418)
!6421 = !DILocation(line: 2887, column: 24, scope: !6422)
!6422 = distinct !DILexicalBlock(scope: !6423, file: !3, line: 2887, column: 22)
!6423 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2887, column: 9)
!6424 = !DILocation(line: 2887, column: 64, scope: !6422)
!6425 = !DILocation(line: 2890, column: 24, scope: !6426)
!6426 = distinct !DILexicalBlock(scope: !6427, file: !3, line: 2890, column: 22)
!6427 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2890, column: 9)
!6428 = !DILocation(line: 2890, column: 64, scope: !6426)
!6429 = !DILocation(line: 2893, column: 24, scope: !6430)
!6430 = distinct !DILexicalBlock(scope: !6431, file: !3, line: 2893, column: 22)
!6431 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2893, column: 9)
!6432 = !DILocation(line: 2893, column: 67, scope: !6430)
!6433 = !DILocation(line: 2899, column: 24, scope: !6434)
!6434 = distinct !DILexicalBlock(scope: !6435, file: !3, line: 2899, column: 22)
!6435 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2899, column: 9)
!6436 = !DILocation(line: 2899, column: 61, scope: !6434)
!6437 = !DILocation(line: 2900, column: 24, scope: !6438)
!6438 = distinct !DILexicalBlock(scope: !6439, file: !3, line: 2900, column: 22)
!6439 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2900, column: 9)
!6440 = !DILocation(line: 2900, column: 65, scope: !6438)
!6441 = !DILocation(line: 2901, column: 24, scope: !6442)
!6442 = distinct !DILexicalBlock(scope: !6443, file: !3, line: 2901, column: 22)
!6443 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2901, column: 9)
!6444 = !DILocation(line: 2901, column: 65, scope: !6442)
!6445 = !DILocation(line: 2902, column: 24, scope: !6446)
!6446 = distinct !DILexicalBlock(scope: !6447, file: !3, line: 2902, column: 22)
!6447 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2902, column: 9)
!6448 = !DILocation(line: 2902, column: 61, scope: !6446)
!6449 = !DILocation(line: 2903, column: 24, scope: !6450)
!6450 = distinct !DILexicalBlock(scope: !6451, file: !3, line: 2903, column: 22)
!6451 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2903, column: 9)
!6452 = !DILocation(line: 2903, column: 52, scope: !6450)
!6453 = !DILocation(line: 2904, column: 24, scope: !6454)
!6454 = distinct !DILexicalBlock(scope: !6455, file: !3, line: 2904, column: 22)
!6455 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2904, column: 9)
!6456 = !DILocation(line: 2904, column: 62, scope: !6454)
!6457 = !DILocation(line: 2909, column: 24, scope: !6458)
!6458 = distinct !DILexicalBlock(scope: !6459, file: !3, line: 2909, column: 22)
!6459 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2909, column: 9)
!6460 = !DILocation(line: 2909, column: 60, scope: !6458)
!6461 = !DILocation(line: 2910, column: 24, scope: !6462)
!6462 = distinct !DILexicalBlock(scope: !6463, file: !3, line: 2910, column: 22)
!6463 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2910, column: 9)
!6464 = !DILocation(line: 2910, column: 57, scope: !6462)
!6465 = !DILocation(line: 2911, column: 24, scope: !6466)
!6466 = distinct !DILexicalBlock(scope: !6467, file: !3, line: 2911, column: 22)
!6467 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2911, column: 9)
!6468 = !DILocation(line: 2911, column: 60, scope: !6466)
!6469 = !DILocation(line: 2912, column: 24, scope: !6470)
!6470 = distinct !DILexicalBlock(scope: !6471, file: !3, line: 2912, column: 22)
!6471 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2912, column: 9)
!6472 = !DILocation(line: 2912, column: 58, scope: !6470)
!6473 = !DILocation(line: 2913, column: 24, scope: !6474)
!6474 = distinct !DILexicalBlock(scope: !6475, file: !3, line: 2913, column: 22)
!6475 = distinct !DILexicalBlock(scope: !6241, file: !3, line: 2913, column: 9)
!6476 = !DILocation(line: 2913, column: 55, scope: !6474)
!6477 = !DILocation(line: 2916, column: 5, scope: !6241)
!6478 = !DILocation(line: 2917, column: 1, scope: !6241)
!6479 = !DISubprogram(name: "jc_APDU_getBuffer", scope: !6, file: !6, line: 94, type: !6480, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!6480 = !DISubroutineType(types: !6481)
!6481 = !{!104, !102}
!6482 = !DISubprogram(name: "jc_ISOException_throwIt", scope: !6, file: !6, line: 120, type: !6483, flags: DIFlagPrototyped, spFlags: DISPFlagOptimized)
!6483 = !DISubroutineType(types: !6484)
!6484 = !{null, !8}
