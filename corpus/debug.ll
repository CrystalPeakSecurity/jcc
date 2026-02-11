; ModuleID = 'examples/debug/build/main.ll.raw'
source_filename = "examples/debug/main.c"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-i128:128-n32:64-S128-ni:1:10:20"
target triple = "wasm32-unknown-unknown"

@values = hidden global [8 x i16] zeroinitializer, align 16

; Function Attrs: nounwind
define hidden void @process(ptr noundef %0, i16 noundef signext %1) #0 {
  %3 = call ptr @jcc_apdu_get_buffer(ptr noundef %0) #3
  %4 = getelementptr inbounds nuw i8, ptr %3, i32 1
  %5 = load i8, ptr %4, align 1, !tbaa !2
  %6 = getelementptr inbounds nuw i8, ptr %3, i32 2
  %7 = load i8, ptr %6, align 1, !tbaa !2
  %8 = getelementptr inbounds nuw i8, ptr %3, i32 3
  %9 = load i8, ptr %8, align 1, !tbaa !2
  switch i8 %5, label %53 [
    i8 1, label %10
    i8 2, label %18
    i8 3, label %26
    i8 4, label %39
  ]

10:                                               ; preds = %2
  %11 = icmp slt i8 %7, 8
  br i1 %11, label %12, label %16

12:                                               ; preds = %10
  %13 = sext i8 %9 to i16
  %14 = sext i8 %7 to i32
  %15 = getelementptr inbounds [8 x i16], ptr @values, i32 0, i32 %14
  store i16 %13, ptr %15, align 2, !tbaa !5
  br label %16

16:                                               ; preds = %12, %10
  store i8 %7, ptr %3, align 1, !tbaa !2
  %17 = getelementptr inbounds nuw i8, ptr %3, i32 1
  store i8 %9, ptr %17, align 1, !tbaa !2
  call void @jcc_apdu_set_outgoing(ptr noundef %0) #3
  call void @jcc_apdu_set_outgoing_length(ptr noundef %0, i16 noundef signext 2) #3
  call void @jcc_apdu_send_bytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #3
  br label %54

18:                                               ; preds = %2
  %19 = icmp slt i8 %7, 8
  br i1 %19, label %20, label %24

20:                                               ; preds = %18
  %21 = sext i8 %7 to i32
  %22 = getelementptr inbounds [8 x i16], ptr @values, i32 0, i32 %21
  %23 = load i16, ptr %22, align 2, !tbaa !5
  %extract.t = trunc i16 %23 to i8
  %extract = lshr i16 %23, 8
  %extract.t5 = trunc nuw i16 %extract to i8
  br label %24

24:                                               ; preds = %20, %18
  %.04.off0 = phi i8 [ %extract.t, %20 ], [ 0, %18 ]
  %.04.off8 = phi i8 [ %extract.t5, %20 ], [ 0, %18 ]
  store i8 %.04.off8, ptr %3, align 1, !tbaa !2
  %25 = getelementptr inbounds nuw i8, ptr %3, i32 1
  store i8 %.04.off0, ptr %25, align 1, !tbaa !2
  call void @jcc_apdu_set_outgoing(ptr noundef %0) #3
  call void @jcc_apdu_set_outgoing_length(ptr noundef %0, i16 noundef signext 2) #3
  call void @jcc_apdu_send_bytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #3
  br label %54

26:                                               ; preds = %2, %28
  %.03 = phi i16 [ %32, %28 ], [ 0, %2 ]
  %.02 = phi i16 [ %33, %28 ], [ 0, %2 ]
  %27 = icmp slt i16 %.02, 8
  br i1 %27, label %28, label %34

28:                                               ; preds = %26
  %29 = sext i16 %.02 to i32
  %30 = getelementptr inbounds [8 x i16], ptr @values, i32 0, i32 %29
  %31 = load i16, ptr %30, align 2, !tbaa !5
  %32 = add i16 %.03, %31
  %33 = add i16 %.02, 1
  br label %26, !llvm.loop !7

34:                                               ; preds = %26
  %35 = lshr i16 %.03, 8
  %36 = trunc nuw i16 %35 to i8
  store i8 %36, ptr %3, align 1, !tbaa !2
  %37 = trunc i16 %.03 to i8
  %38 = getelementptr inbounds nuw i8, ptr %3, i32 1
  store i8 %37, ptr %38, align 1, !tbaa !2
  call void @jcc_apdu_set_outgoing(ptr noundef %0) #3
  call void @jcc_apdu_set_outgoing_length(ptr noundef %0, i16 noundef signext 2) #3
  call void @jcc_apdu_send_bytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #3
  br label %54

39:                                               ; preds = %2, %41
  %.01 = phi i16 [ %45, %41 ], [ 0, %2 ]
  %.0 = phi i16 [ %46, %41 ], [ 0, %2 ]
  %40 = icmp slt i16 %.0, 8
  br i1 %40, label %41, label %47

41:                                               ; preds = %39
  %42 = sext i16 %.0 to i32
  %43 = getelementptr inbounds [8 x i16], ptr @values, i32 0, i32 %42
  %44 = load i16, ptr %43, align 2, !tbaa !5
  %45 = add i16 %.01, %44
  %46 = add i16 %.0, 1
  br label %39, !llvm.loop !10

47:                                               ; preds = %39
  %48 = sdiv i16 %.01, 8
  %49 = lshr i16 %48, 8
  %50 = trunc nuw i16 %49 to i8
  store i8 %50, ptr %3, align 1, !tbaa !2
  %51 = trunc i16 %48 to i8
  %52 = getelementptr inbounds nuw i8, ptr %3, i32 1
  store i8 %51, ptr %52, align 1, !tbaa !2
  call void @jcc_apdu_set_outgoing(ptr noundef %0) #3
  call void @jcc_apdu_set_outgoing_length(ptr noundef %0, i16 noundef signext 2) #3
  call void @jcc_apdu_send_bytes(ptr noundef %0, i16 noundef signext 0, i16 noundef signext 2) #3
  br label %54

53:                                               ; preds = %2
  call void @jcc_throw(i16 noundef signext 27904) #3
  br label %54

54:                                               ; preds = %53, %47, %34, %24, %16
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr captures(none)) #1

declare ptr @jcc_apdu_get_buffer(ptr noundef) #2

declare void @jcc_apdu_set_outgoing(ptr noundef) #2

declare void @jcc_apdu_set_outgoing_length(ptr noundef, i16 noundef signext) #2

declare void @jcc_apdu_send_bytes(ptr noundef, i16 noundef signext, i16 noundef signext) #2

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr captures(none)) #1

declare void @jcc_throw(i16 noundef signext) #2

attributes #0 = { nounwind "no-jump-tables"="true" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+bulk-memory,+bulk-memory-opt,+call-indirect-overlong,+multivalue,+mutable-globals,+nontrapping-fptoint,+reference-types,+sign-ext" }
attributes #1 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+bulk-memory,+bulk-memory-opt,+call-indirect-overlong,+multivalue,+mutable-globals,+nontrapping-fptoint,+reference-types,+sign-ext" }
attributes #3 = { nounwind }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"Homebrew clang version 21.1.8"}
!2 = !{!3, !3, i64 0}
!3 = !{!"omnipotent char", !4, i64 0}
!4 = !{!"Simple C/C++ TBAA"}
!5 = !{!6, !6, i64 0}
!6 = !{!"short", !3, i64 0}
!7 = distinct !{!7, !8, !9}
!8 = !{!"llvm.loop.mustprogress"}
!9 = !{!"llvm.loop.unroll.disable"}
!10 = distinct !{!10, !8, !9}