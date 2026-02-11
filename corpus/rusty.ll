; ModuleID = 'lib.aea4d3df3642ec66-cgu.0'
source_filename = "lib.aea4d3df3642ec66-cgu.0"
target datalayout = "e-m:e-p:32:32-p10:8:8-p20:8:8-i64:64-i128:128-n32:64-S128-ni:1:10:20"
target triple = "wasm32-unknown-unknown"

%Pipe = type { i16, i16, i8, i8 }

@_ZN3lib10DIGIT_FONT17h568307813fef6c2aE = internal unnamed_addr constant [50 x i8] c"\07\05\05\05\07\02\06\02\02\07\07\01\07\04\07\07\01\07\01\07\05\05\07\01\01\07\04\07\01\07\07\04\07\05\07\07\01\01\01\01\07\05\07\05\07\07\05\07\01\07", align 1, !dbg !0
@_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E = internal global [80 x i8] zeroinitializer, align 1, !dbg !8
@_ZN3lib16GAME_INITIALIZED17hdc6bee963eb1f766E.0 = internal unnamed_addr global i1 false, align 1, !dbg !13
@_ZN3lib4BIRD17h571dc8b4c80d60d7E.0 = internal unnamed_addr global i16 0, align 2, !dbg !15
@_ZN3lib4BIRD17h571dc8b4c80d60d7E.1 = internal unnamed_addr global i16 0, align 2, !dbg !24
@_ZN3lib4GAME17hbf8763b2c745ccd8E.0 = internal unnamed_addr global i8 0, align 2, !dbg !25
@_ZN3lib4GAME17hbf8763b2c745ccd8E.1 = internal unnamed_addr global i16 0, align 2, !dbg !32
@_ZN3lib4GAME17hbf8763b2c745ccd8E.2 = internal unnamed_addr global i16 0, align 2, !dbg !33
@_ZN3lib5PIPES17h0b113f338cd5ae43E = internal unnamed_addr global [18 x i8] zeroinitializer, align 2, !dbg !34
@_ZN3lib6NUM_D017h603139fb0e00dad5E.0 = internal unnamed_addr global i16 0, align 2, !dbg !45
@_ZN3lib6NUM_D117hc6caecc785c50e8dE.0 = internal unnamed_addr global i16 0, align 2, !dbg !47
@_ZN3lib6NUM_D217hce061614100c2eebE.0 = internal unnamed_addr global i16 0, align 2, !dbg !49
@_ZN3lib9RNG_STATE17h0f6aa4bd50ad1b09E.0 = internal unnamed_addr global i16 12345, align 2, !dbg !51

; __rustc::rust_begin_unwind
; Function Attrs: nofree norecurse noreturn nosync nounwind memory(none)
define hidden void @_RNvCskdKJRKLKjqM_7___rustc17rust_begin_unwind(ptr noalias noundef readonly align 4 captures(none) dereferenceable(12) %_info) unnamed_addr #0 !dbg !70 {
start:
    #dbg_value(ptr %_info, !242, !DIExpression(), !243)
  br label %bb1, !dbg !244

bb1:                                              ; preds = %bb1, %start
  br label %bb1, !dbg !244
}

; lib::drawNumber
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib10drawNumber17h9e0b83d1ba77bfc9E(i16 noundef range(i16 2, 9) %y, i16 noundef %number) unnamed_addr #1 !dbg !245 {
start:
    #dbg_value(i16 16, !249, !DIExpression(), !263)
    #dbg_value(i16 %y, !250, !DIExpression(), !263)
    #dbg_value(i16 %number, !251, !DIExpression(), !263)
    #dbg_value(i8 1, !252, !DIExpression(), !263)
    #dbg_value(i16 %number, !253, !DIExpression(), !264)
    #dbg_value(i16 poison, !253, !DIExpression(), !264)
  %_8 = icmp sgt i16 %number, 999, !dbg !265
  br i1 %_8, label %bb4, label %bb5, !dbg !265

bb5:                                              ; preds = %start
  %spec.store.select = tail call i16 @llvm.smax.i16(i16 %number, i16 0), !dbg !266
    #dbg_value(i16 %spec.store.select, !253, !DIExpression(), !264)
  store i16 0, ptr @_ZN3lib6NUM_D017h603139fb0e00dad5E.0, align 2, !dbg !267
  store i16 0, ptr @_ZN3lib6NUM_D117hc6caecc785c50e8dE.0, align 2, !dbg !268
  store i16 0, ptr @_ZN3lib6NUM_D217hce061614100c2eebE.0, align 2, !dbg !269
    #dbg_value(i16 %spec.store.select, !257, !DIExpression(), !270)
  %0 = icmp slt i16 %number, 1, !dbg !271
  br i1 %0, label %bb6, label %bb7, !dbg !271

bb4:                                              ; preds = %start
    #dbg_value(i16 999, !253, !DIExpression(), !264)
  store i16 0, ptr @_ZN3lib6NUM_D017h603139fb0e00dad5E.0, align 2, !dbg !267
  store i16 0, ptr @_ZN3lib6NUM_D117hc6caecc785c50e8dE.0, align 2, !dbg !268
  store i16 0, ptr @_ZN3lib6NUM_D217hce061614100c2eebE.0, align 2, !dbg !269
    #dbg_value(i16 999, !257, !DIExpression(), !270)
  br label %bb7, !dbg !271

bb6:                                              ; preds = %bb5
  store i16 0, ptr @_ZN3lib6NUM_D017h603139fb0e00dad5E.0, align 2, !dbg !272
    #dbg_value(i16 1, !255, !DIExpression(), !273)
  br label %bb17, !dbg !274

bb7:                                              ; preds = %bb4, %bb5
  %temp.sroa.0.0 = phi i16 [ 999, %bb4 ], [ %spec.store.select, %bb5 ], !dbg !275
    #dbg_value(i16 %temp.sroa.0.0, !257, !DIExpression(), !270)
    #dbg_value(i16 0, !255, !DIExpression(), !273)
  %_16.not = icmp eq i16 %temp.sroa.0.0, 0, !dbg !276
  br i1 %_16.not, label %bb10, label %bb8, !dbg !276

bb17:                                             ; preds = %bb14, %bb13, %bb6
  %num_digits.sroa.0.0 = phi i16 [ 3, %bb14 ], [ %num_digits.sroa.0.2, %bb13 ], [ 1, %bb6 ], !dbg !270
    #dbg_value(i16 %num_digits.sroa.0.0, !255, !DIExpression(), !273)
  %_26 = shl nuw nsw i16 %num_digits.sroa.0.0, 2, !dbg !277
  %width = add nsw i16 %_26, -1, !dbg !277
    #dbg_value(i16 %width, !259, !DIExpression(), !278)
  %_29.neg = sdiv i16 %width, -2, !dbg !279
  %1 = add nsw i16 %_29.neg, 16, !dbg !280
    #dbg_value(i16 %1, !261, !DIExpression(), !281)
  %2 = icmp eq i16 %num_digits.sroa.0.0, 3, !dbg !282
  br i1 %2, label %bb18, label %bb21, !dbg !282

bb8:                                              ; preds = %bb7
  %3 = udiv i16 %temp.sroa.0.0, 10, !dbg !283
  %4 = mul i16 %3, 10, !dbg !284
  %.decomposed = sub i16 %temp.sroa.0.0, %4, !dbg !284
  store i16 %.decomposed, ptr @_ZN3lib6NUM_D017h603139fb0e00dad5E.0, align 2, !dbg !284
    #dbg_value(i16 %3, !257, !DIExpression(), !270)
    #dbg_value(i16 1, !255, !DIExpression(), !273)
  br label %bb10, !dbg !285

bb10:                                             ; preds = %bb7, %bb8
  %temp.sroa.0.1 = phi i16 [ %3, %bb8 ], [ %temp.sroa.0.0, %bb7 ], !dbg !273
  %num_digits.sroa.0.1 = phi i16 [ 1, %bb8 ], [ 0, %bb7 ], !dbg !270
    #dbg_value(i16 %num_digits.sroa.0.1, !255, !DIExpression(), !273)
    #dbg_value(i16 %temp.sroa.0.1, !257, !DIExpression(), !270)
  %_19.not = icmp eq i16 %temp.sroa.0.1, 0, !dbg !286
  br i1 %_19.not, label %bb13, label %bb11, !dbg !286

bb11:                                             ; preds = %bb10
  %5 = udiv i16 %temp.sroa.0.1, 10, !dbg !287
  %6 = mul i16 %5, 10, !dbg !288
  %.decomposed1 = sub i16 %temp.sroa.0.1, %6, !dbg !288
  store i16 %.decomposed1, ptr @_ZN3lib6NUM_D117hc6caecc785c50e8dE.0, align 2, !dbg !288
    #dbg_value(i16 %5, !257, !DIExpression(), !270)
    #dbg_value(i16 2, !255, !DIExpression(), !273)
  br label %bb13, !dbg !289

bb13:                                             ; preds = %bb10, %bb11
  %temp.sroa.0.2 = phi i16 [ %5, %bb11 ], [ %temp.sroa.0.1, %bb10 ], !dbg !270
  %num_digits.sroa.0.2 = phi i16 [ 2, %bb11 ], [ %num_digits.sroa.0.1, %bb10 ], !dbg !270
    #dbg_value(i16 %num_digits.sroa.0.2, !255, !DIExpression(), !273)
    #dbg_value(i16 %temp.sroa.0.2, !257, !DIExpression(), !270)
  %_22.not = icmp eq i16 %temp.sroa.0.2, 0, !dbg !290
  br i1 %_22.not, label %bb17, label %bb14, !dbg !290

bb14:                                             ; preds = %bb13
  %7 = urem i16 %temp.sroa.0.2, 10, !dbg !291
  store i16 %7, ptr @_ZN3lib6NUM_D217hce061614100c2eebE.0, align 2, !dbg !291
    #dbg_value(i16 3, !255, !DIExpression(), !273)
  br label %bb17, !dbg !292

bb18:                                             ; preds = %bb17
  %_33 = load i16, ptr @_ZN3lib6NUM_D217hce061614100c2eebE.0, align 2, !dbg !293, !noundef !23
; call lib::drawDigit
  tail call fastcc void @_ZN3lib9drawDigit17h0ebc745f1e2cb6a0E(i16 noundef %1, i16 noundef %y, i16 noundef %_33) #11, !dbg !294
  %8 = add nsw i16 %_29.neg, 20, !dbg !295
    #dbg_value(i16 %8, !261, !DIExpression(), !281)
  br label %bb21, !dbg !296

bb21:                                             ; preds = %bb17, %bb18
  %start_x.sroa.0.0 = phi i16 [ %8, %bb18 ], [ %1, %bb17 ], !dbg !278
    #dbg_value(i16 %start_x.sroa.0.0, !261, !DIExpression(), !281)
  %_34 = icmp sgt i16 %num_digits.sroa.0.0, 1, !dbg !297
  br i1 %_34, label %bb22, label %bb25, !dbg !297

bb22:                                             ; preds = %bb21
  %_38 = load i16, ptr @_ZN3lib6NUM_D117hc6caecc785c50e8dE.0, align 2, !dbg !298, !noundef !23
; call lib::drawDigit
  tail call fastcc void @_ZN3lib9drawDigit17h0ebc745f1e2cb6a0E(i16 noundef %start_x.sroa.0.0, i16 noundef %y, i16 noundef %_38) #11, !dbg !299
  %9 = add nuw nsw i16 %start_x.sroa.0.0, 4, !dbg !300
    #dbg_value(i16 %9, !261, !DIExpression(), !281)
  br label %bb25, !dbg !301

bb25:                                             ; preds = %bb21, %bb22
  %start_x.sroa.0.1 = phi i16 [ %9, %bb22 ], [ %start_x.sroa.0.0, %bb21 ], !dbg !281
    #dbg_value(i16 %start_x.sroa.0.1, !261, !DIExpression(), !281)
  %_41 = load i16, ptr @_ZN3lib6NUM_D017h603139fb0e00dad5E.0, align 2, !dbg !302, !noundef !23
; call lib::drawDigit
  tail call fastcc void @_ZN3lib9drawDigit17h0ebc745f1e2cb6a0E(i16 noundef %start_x.sroa.0.1, i16 noundef %y, i16 noundef %_41) #11, !dbg !303
  ret void, !dbg !304
}

; lib::reset_game
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(write, argmem: none, inaccessiblemem: none)
define internal fastcc void @_ZN3lib10reset_game17hd18b9fe9bf0032f6E() unnamed_addr #2 !dbg !305 {
start:
  store i16 2560, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.0, align 2, !dbg !311
  store i16 0, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.1, align 2, !dbg !312
    #dbg_value(i32 0, !309, !DIExpression(), !313)
    #dbg_value(i32 0, !309, !DIExpression(), !313)
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 4), align 2, !dbg !314
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 5), align 1, !dbg !315
    #dbg_value(i32 1, !309, !DIExpression(), !313)
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 10), align 2, !dbg !314
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 11), align 1, !dbg !315
    #dbg_value(i32 2, !309, !DIExpression(), !313)
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 16), align 2, !dbg !314
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 17), align 1, !dbg !315
    #dbg_value(i32 3, !309, !DIExpression(), !313)
  store i8 0, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.0, align 2, !dbg !316
  store i16 0, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.1, align 2, !dbg !317
  store i16 0, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.2, align 2, !dbg !318
  store i16 12345, ptr @_ZN3lib9RNG_STATE17h0f6aa4bd50ad1b09E.0, align 2, !dbg !319
  ret void, !dbg !320
}

; lib::spawn_pipe
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib10spawn_pipe17h6d0176eb64ed2057E(i16 noundef range(i16 32, 43) %x) unnamed_addr #1 !dbg !321 {
start:
    #dbg_value(i16 %x, !325, !DIExpression(), !328)
    #dbg_value(i32 0, !326, !DIExpression(), !329)
    #dbg_value(i32 0, !326, !DIExpression(), !329)
  %_5 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 4), align 2, !dbg !330, !noundef !23
  %0 = icmp eq i8 %_5, 0, !dbg !330
    #dbg_value(i32 0, !326, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !329)
  br i1 %0, label %bb5, label %bb1, !dbg !330

bb1:                                              ; preds = %start
    #dbg_value(i32 1, !326, !DIExpression(), !329)
  %_5.1 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 10), align 2, !dbg !330, !noundef !23
  %1 = icmp eq i8 %_5.1, 0, !dbg !330
    #dbg_value(i32 1, !326, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !329)
  br i1 %1, label %bb5, label %bb1.1, !dbg !330

bb1.1:                                            ; preds = %bb1
    #dbg_value(i32 2, !326, !DIExpression(), !329)
  %_5.2 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 16), align 2, !dbg !330, !noundef !23
  %2 = icmp eq i8 %_5.2, 0, !dbg !330
    #dbg_value(i32 2, !326, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !329)
  br i1 %2, label %bb5, label %bb12, !dbg !330

bb12:                                             ; preds = %bb1.1, %bb5
  ret void, !dbg !331

bb5:                                              ; preds = %bb1.1, %bb1, %start
  %.lcssa = phi ptr [ @_ZN3lib5PIPES17h0b113f338cd5ae43E, %start ], [ getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 6), %bb1 ], [ getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 12), %bb1.1 ], !dbg !330
  %3 = getelementptr inbounds nuw i8, ptr %.lcssa, i32 4
  store i16 %x, ptr %.lcssa, align 2, !dbg !332
; call lib::random_gap_y
  %_11 = tail call fastcc noundef i16 @_ZN3lib12random_gap_y17h6eff876945902f3aE() #11, !dbg !333
  %4 = getelementptr inbounds nuw i8, ptr %.lcssa, i32 2, !dbg !334
  store i16 %_11, ptr %4, align 2, !dbg !334
  store i8 1, ptr %3, align 2, !dbg !335
  %5 = getelementptr inbounds nuw i8, ptr %.lcssa, i32 5, !dbg !336
  store i8 0, ptr %5, align 1, !dbg !336
  br label %bb12, !dbg !331
}

; lib::render_game
; Function Attrs: nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib11render_game17h39ae85af2824aafbE() unnamed_addr #3 !dbg !337 {
start:
  %_2 = load i8, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.0, align 2, !dbg !338, !noundef !23
  switch i8 %_2, label %bb14 [
    i8 0, label %bb1
    i8 1, label %bb4
    i8 2, label %bb9
  ], !dbg !338

bb1:                                              ; preds = %start
; call lib::drawReadyScreen
  tail call fastcc void @_ZN3lib15drawReadyScreen17h28203f98bd85755bE() #11, !dbg !339
  br label %bb14, !dbg !340

bb4:                                              ; preds = %start
; call lib::drawPipes
  tail call fastcc void @_ZN3lib9drawPipes17hc093196a1ee1552cE() #11, !dbg !341
; call lib::drawBird
  tail call fastcc void @_ZN3lib8drawBird17hf8f2a7b43ff767a3E() #11, !dbg !342
; call lib::drawScore
  tail call fastcc void @_ZN3lib9drawScore17h21f5311f5325b862E() #11, !dbg !343
  br label %bb14, !dbg !340

bb9:                                              ; preds = %start
; call lib::drawPipes
  tail call fastcc void @_ZN3lib9drawPipes17hc093196a1ee1552cE() #11, !dbg !344
; call lib::drawBird
  tail call fastcc void @_ZN3lib8drawBird17hf8f2a7b43ff767a3E() #11, !dbg !345
; call lib::drawGameOver
  tail call fastcc void @_ZN3lib12drawGameOver17h668eec5f6df376c3E() #11, !dbg !346
  br label %bb14, !dbg !346

bb14:                                             ; preds = %start, %bb9, %bb1, %bb4
  ret void, !dbg !347
}

; lib::update_bird
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define internal fastcc void @_ZN3lib11update_bird17h3beb04e75e34aa8aE(i8 noundef range(i8 0, 2) %flap) unnamed_addr #4 !dbg !348 {
start:
    #dbg_value(i8 %flap, !352, !DIExpression(), !355)
    #dbg_value(i16 4352, !353, !DIExpression(), !356)
  %0 = icmp eq i8 %flap, 0, !dbg !357
  %1 = load i16, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.1, align 2, !dbg !357
  %2 = add i16 %1, 6, !dbg !357
  %spec.store.select = tail call i16 @llvm.smin.i16(i16 %2, i16 192), !dbg !357
  %storemerge = select i1 %0, i16 %spec.store.select, i16 -100, !dbg !357
  store i16 %storemerge, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.1, align 2, !dbg !355
  %3 = load i16, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.0, align 2, !dbg !358, !noundef !23
  %4 = add i16 %storemerge, %3, !dbg !358
  store i16 %4, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.0, align 2, !dbg !358
  %_8 = icmp slt i16 %4, 0, !dbg !359
  br i1 %_8, label %bb7, label %bb9, !dbg !359

bb7:                                              ; preds = %start
  store i16 0, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.0, align 2, !dbg !360
  store i16 0, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.1, align 2, !dbg !361
  br label %bb9, !dbg !362

bb9:                                              ; preds = %start, %bb7
  %_11 = load i16, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.0, align 2, !dbg !363, !noundef !23
  %_10 = icmp sgt i16 %_11, 4352, !dbg !363
  br i1 %_10, label %bb10, label %bb12, !dbg !363

bb10:                                             ; preds = %bb9
  store i16 4352, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.0, align 2, !dbg !364
  br label %bb12, !dbg !365

bb12:                                             ; preds = %bb9, %bb10
  ret void, !dbg !366
}

; lib::drawGameOver
; Function Attrs: nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib12drawGameOver17h668eec5f6df376c3E() unnamed_addr #3 !dbg !367 {
start:
    #dbg_value(i16 16, !369, !DIExpression(), !373)
    #dbg_value(i16 10, !371, !DIExpression(), !374)
; call lib::drawRect
  tail call fastcc void @_ZN3lib8drawRect17h579d1c66bf16d8b0E() #11, !dbg !375
  %_3 = load i16, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.1, align 2, !dbg !376, !noundef !23
; call lib::drawNumber
  tail call fastcc void @_ZN3lib10drawNumber17h9e0b83d1ba77bfc9E(i16 noundef 8, i16 noundef %_3) #11, !dbg !377
; call lib::setPixel
  tail call fastcc void @_ZN3lib8setPixel17h43bda99ce5e3fe75E(i16 noundef 15, i16 noundef 12) #11, !dbg !378
; call lib::setPixel
  tail call fastcc void @_ZN3lib8setPixel17h43bda99ce5e3fe75E(i16 noundef 16, i16 noundef 12) #11, !dbg !379
; call lib::setPixel
  tail call fastcc void @_ZN3lib8setPixel17h43bda99ce5e3fe75E(i16 noundef 17, i16 noundef 12) #11, !dbg !380
  ret void, !dbg !381
}

; lib::random_gap_y
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define internal fastcc noundef range(i16 6, 14) i16 @_ZN3lib12random_gap_y17h6eff876945902f3aE() unnamed_addr #1 !dbg !382 {
start:
    #dbg_value(i16 6, !386, !DIExpression(), !392)
    #dbg_value(i16 14, !388, !DIExpression(), !393)
    #dbg_value(i16 8, !390, !DIExpression(), !394)
; call lib::random_short
  %_2 = tail call fastcc noundef i16 @_ZN3lib12random_short17h8c52220c7d87c14aE() #11, !dbg !395
  %_1 = and i16 %_2, 7, !dbg !396
  %_0 = add nuw nsw i16 %_1, 6, !dbg !397
  ret i16 %_0, !dbg !398
}

; lib::random_short
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define internal fastcc noundef range(i16 0, -32768) i16 @_ZN3lib12random_short17h8c52220c7d87c14aE() unnamed_addr #4 !dbg !399 {
start:
  %_5 = load i16, ptr @_ZN3lib9RNG_STATE17h0f6aa4bd50ad1b09E.0, align 2, !dbg !400, !noundef !23
  %_3 = mul i16 %_5, 25173, !dbg !401
  %_2 = add i16 %_3, 13849, !dbg !402
  %_1 = and i16 %_2, 32767, !dbg !403
  store i16 %_1, ptr @_ZN3lib9RNG_STATE17h0f6aa4bd50ad1b09E.0, align 2, !dbg !404
  ret i16 %_1, !dbg !405
}

; lib::update_pipes
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib12update_pipes17h766c122619250a74E() unnamed_addr #1 !dbg !406 {
start:
    #dbg_value(i32 0, !408, !DIExpression(), !412)
  %_ZN3lib4GAME17hbf8763b2c745ccd8E.1.promoted = load i16, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.1, align 2
    #dbg_value(i32 0, !408, !DIExpression(), !412)
    #dbg_value(i32 0, !408, !DIExpression(), !412)
  %_4 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 4), align 2, !dbg !413, !noundef !23
  %0 = icmp eq i8 %_4, 0, !dbg !413
  br i1 %0, label %bb20, label %bb5, !dbg !413

bb24:                                             ; preds = %bb23, %bb20.2
  ret void, !dbg !414

bb23:                                             ; preds = %bb20.2
; call lib::spawn_pipe
  tail call fastcc void @_ZN3lib10spawn_pipe17h6d0176eb64ed2057E(i16 noundef 32) #11, !dbg !415
  br label %bb24, !dbg !415

bb20:                                             ; preds = %bb16, %bb14, %start
  %1 = phi i16 [ %18, %bb16 ], [ %18, %bb14 ], [ %_ZN3lib4GAME17hbf8763b2c745ccd8E.1.promoted, %start ]
    #dbg_value(i32 1, !408, !DIExpression(), !412)
  %_4.1 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 10), align 2, !dbg !413, !noundef !23
  %2 = icmp eq i8 %_4.1, 0, !dbg !413
  br i1 %2, label %bb20.1, label %bb5.1, !dbg !413

bb5.1:                                            ; preds = %bb20
  %3 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 6), align 2, !dbg !416, !noundef !23
  %4 = add i16 %3, -1, !dbg !416
  store i16 %4, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 6), align 2, !dbg !416
  %_10.1 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 11), align 1, !dbg !417, !noundef !23
  %5 = icmp eq i8 %_10.1, 0, !dbg !417
  %_14.1 = add i16 %3, 3
  %_13.1 = icmp slt i16 %_14.1, 8
  %or.cond.1 = and i1 %_13.1, %5, !dbg !417
  br i1 %or.cond.1, label %bb10.1, label %bb14.1, !dbg !417

bb10.1:                                           ; preds = %bb5.1
  store i8 1, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 11), align 1, !dbg !418
  %6 = add i16 %1, 1, !dbg !419
  store i16 %6, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.1, align 2, !dbg !419
  br label %bb14.1, !dbg !420

bb14.1:                                           ; preds = %bb10.1, %bb5.1
  %7 = phi i16 [ %6, %bb10.1 ], [ %1, %bb5.1 ]
  %_23.1 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 6), align 2, !dbg !421, !noundef !23
  %_22.1 = add i16 %_23.1, 4, !dbg !421
  %_21.1 = icmp slt i16 %_22.1, 0, !dbg !421
  br i1 %_21.1, label %bb16.1, label %bb20.1, !dbg !421

bb16.1:                                           ; preds = %bb14.1
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 10), align 2, !dbg !422
  br label %bb20.1, !dbg !423

bb20.1:                                           ; preds = %bb16.1, %bb14.1, %bb20
  %8 = phi i16 [ %7, %bb16.1 ], [ %7, %bb14.1 ], [ %1, %bb20 ]
    #dbg_value(i32 2, !408, !DIExpression(), !412)
  %_4.2 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 16), align 2, !dbg !413, !noundef !23
  %9 = icmp eq i8 %_4.2, 0, !dbg !413
  br i1 %9, label %bb20.2, label %bb5.2, !dbg !413

bb5.2:                                            ; preds = %bb20.1
  %10 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 12), align 2, !dbg !416, !noundef !23
  %11 = add i16 %10, -1, !dbg !416
  store i16 %11, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 12), align 2, !dbg !416
  %_10.2 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 17), align 1, !dbg !417, !noundef !23
  %12 = icmp eq i8 %_10.2, 0, !dbg !417
  %_14.2 = add i16 %10, 3
  %_13.2 = icmp slt i16 %_14.2, 8
  %or.cond.2 = and i1 %_13.2, %12, !dbg !417
  br i1 %or.cond.2, label %bb10.2, label %bb14.2, !dbg !417

bb10.2:                                           ; preds = %bb5.2
  store i8 1, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 17), align 1, !dbg !418
  %13 = add i16 %8, 1, !dbg !419
  store i16 %13, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.1, align 2, !dbg !419
  br label %bb14.2, !dbg !420

bb14.2:                                           ; preds = %bb10.2, %bb5.2
  %_23.2 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 12), align 2, !dbg !421, !noundef !23
  %_22.2 = add i16 %_23.2, 4, !dbg !421
  %_21.2 = icmp slt i16 %_22.2, 0, !dbg !421
  br i1 %_21.2, label %bb16.2, label %bb20.2, !dbg !421

bb16.2:                                           ; preds = %bb14.2
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 16), align 2, !dbg !422
  br label %bb20.2, !dbg !423

bb20.2:                                           ; preds = %bb16.2, %bb14.2, %bb20.1
    #dbg_value(i32 3, !408, !DIExpression(), !412)
; call lib::find_rightmost_pipe_x
  %rightmost_x = tail call fastcc noundef i16 @_ZN3lib21find_rightmost_pipe_x17hadc4e3130a184b0aE() #11, !dbg !424
    #dbg_value(i16 %rightmost_x, !410, !DIExpression(), !425)
  %_29 = icmp slt i16 %rightmost_x, 18, !dbg !426
  br i1 %_29, label %bb23, label %bb24, !dbg !426

bb5:                                              ; preds = %start
  %14 = load i16, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, align 2, !dbg !416, !noundef !23
  %15 = add i16 %14, -1, !dbg !416
  store i16 %15, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, align 2, !dbg !416
  %_10 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 5), align 1, !dbg !417, !noundef !23
  %16 = icmp eq i8 %_10, 0, !dbg !417
  %_14 = add i16 %14, 3
  %_13 = icmp slt i16 %_14, 8
  %or.cond = and i1 %_13, %16, !dbg !417
  br i1 %or.cond, label %bb10, label %bb14, !dbg !417

bb10:                                             ; preds = %bb5
  store i8 1, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 5), align 1, !dbg !418
  %17 = add i16 %_ZN3lib4GAME17hbf8763b2c745ccd8E.1.promoted, 1, !dbg !419
  store i16 %17, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.1, align 2, !dbg !419
  br label %bb14, !dbg !420

bb14:                                             ; preds = %bb10, %bb5
  %18 = phi i16 [ %17, %bb10 ], [ %_ZN3lib4GAME17hbf8763b2c745ccd8E.1.promoted, %bb5 ]
  %_23 = load i16, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, align 2, !dbg !421, !noundef !23
  %_22 = add i16 %_23, 4, !dbg !421
  %_21 = icmp slt i16 %_22, 0, !dbg !421
  br i1 %_21, label %bb16, label %bb20, !dbg !421

bb16:                                             ; preds = %bb14
  store i8 0, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 4), align 2, !dbg !422
  br label %bb20, !dbg !423
}

; lib::check_collision
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(read, argmem: none, inaccessiblemem: none)
define internal fastcc noundef range(i8 0, 2) i8 @_ZN3lib15check_collision17h4f705c960de6c75bE() unnamed_addr #5 !dbg !427 {
start:
    #dbg_value(i16 8, !437, !DIExpression(), !451)
    #dbg_value(i16 11, !439, !DIExpression(), !452)
  %_2 = load i16, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.0, align 2, !dbg !453, !noundef !23
  %bird_screen_y = ashr i16 %_2, 8, !dbg !453
    #dbg_value(i16 %bird_screen_y, !431, !DIExpression(), !454)
    #dbg_value(i16 %bird_screen_y, !433, !DIExpression(), !455)
  %bird_bottom = add nsw i16 %bird_screen_y, 3, !dbg !456
    #dbg_value(i16 %bird_bottom, !435, !DIExpression(), !457)
  %0 = add nsw i16 %bird_screen_y, -17, !dbg !458
  %or.cond12 = icmp ult i16 %0, -16, !dbg !458
  br i1 %or.cond12, label %bb23, label %bb7, !dbg !458

bb23:                                             ; preds = %bb14, %bb14.1, %bb14.2, %bb20.2, %start
  %_0.sroa.0.0 = phi i8 [ 1, %start ], [ 1, %bb14 ], [ 1, %bb14.1 ], [ 1, %bb14.2 ], [ 0, %bb20.2 ], !dbg !452
  ret i8 %_0.sroa.0.0, !dbg !459

bb7:                                              ; preds = %start
    #dbg_value(i32 0, !441, !DIExpression(), !460)
  %_10 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 4), align 2, !dbg !461, !noundef !23
  %1 = icmp eq i8 %_10, 0, !dbg !461
  br i1 %1, label %bb20, label %bb9, !dbg !461

bb20:                                             ; preds = %bb14, %bb9, %bb7
    #dbg_value(i32 1, !441, !DIExpression(), !460)
  %_10.1 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 10), align 2, !dbg !461, !noundef !23
  %2 = icmp eq i8 %_10.1, 0, !dbg !461
  br i1 %2, label %bb20.1, label %bb9.1, !dbg !461

bb9.1:                                            ; preds = %bb20
  %pipe_left.1 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 6), align 2, !dbg !462, !noundef !23
    #dbg_value(i16 %pipe_left.1, !443, !DIExpression(), !463)
    #dbg_value(i16 %pipe_left.1, !445, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !464)
    #dbg_value(i16 poison, !447, !DIExpression(DW_OP_constu, 4, DW_OP_minus, DW_OP_stack_value), !465)
    #dbg_value(i16 poison, !449, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !466)
  %3 = add i16 %pipe_left.1, -5, !dbg !467
  %or.cond.1 = icmp ult i16 %3, 6, !dbg !467
  br i1 %or.cond.1, label %bb14.1, label %bb20.1, !dbg !467

bb14.1:                                           ; preds = %bb9.1
  %_22.1 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 8), align 2, !dbg !468, !noundef !23
    #dbg_value(i16 %_22.1, !449, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !466)
    #dbg_value(i16 %_22.1, !447, !DIExpression(DW_OP_constu, 4, DW_OP_minus, DW_OP_stack_value), !465)
  %gap_top.1 = add i16 %_22.1, -4, !dbg !468
    #dbg_value(i16 %gap_top.1, !447, !DIExpression(), !465)
  %gap_bottom.1 = add i16 %_22.1, 4, !dbg !469
    #dbg_value(i16 %gap_bottom.1, !449, !DIExpression(), !466)
  %_31.1 = icmp slt i16 %bird_screen_y, %gap_top.1, !dbg !470
  %_32.1 = icmp sgt i16 %bird_bottom, %gap_bottom.1
  %or.cond5.1 = or i1 %_31.1, %_32.1, !dbg !470
  br i1 %or.cond5.1, label %bb23, label %bb20.1, !dbg !470

bb20.1:                                           ; preds = %bb14.1, %bb9.1, %bb20
    #dbg_value(i32 2, !441, !DIExpression(), !460)
  %_10.2 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 16), align 2, !dbg !461, !noundef !23
  %4 = icmp eq i8 %_10.2, 0, !dbg !461
  br i1 %4, label %bb20.2, label %bb9.2, !dbg !461

bb9.2:                                            ; preds = %bb20.1
  %pipe_left.2 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 12), align 2, !dbg !462, !noundef !23
    #dbg_value(i16 %pipe_left.2, !443, !DIExpression(), !463)
    #dbg_value(i16 %pipe_left.2, !445, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !464)
    #dbg_value(i16 poison, !447, !DIExpression(DW_OP_constu, 4, DW_OP_minus, DW_OP_stack_value), !465)
    #dbg_value(i16 poison, !449, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !466)
  %5 = add i16 %pipe_left.2, -5, !dbg !467
  %or.cond.2 = icmp ult i16 %5, 6, !dbg !467
  br i1 %or.cond.2, label %bb14.2, label %bb20.2, !dbg !467

bb14.2:                                           ; preds = %bb9.2
  %_22.2 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 14), align 2, !dbg !468, !noundef !23
    #dbg_value(i16 %_22.2, !449, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !466)
    #dbg_value(i16 %_22.2, !447, !DIExpression(DW_OP_constu, 4, DW_OP_minus, DW_OP_stack_value), !465)
  %gap_top.2 = add i16 %_22.2, -4, !dbg !468
    #dbg_value(i16 %gap_top.2, !447, !DIExpression(), !465)
  %gap_bottom.2 = add i16 %_22.2, 4, !dbg !469
    #dbg_value(i16 %gap_bottom.2, !449, !DIExpression(), !466)
  %_31.2 = icmp slt i16 %bird_screen_y, %gap_top.2, !dbg !470
  %_32.2 = icmp sgt i16 %bird_bottom, %gap_bottom.2
  %or.cond5.2 = or i1 %_31.2, %_32.2, !dbg !470
  br i1 %or.cond5.2, label %bb23, label %bb20.2, !dbg !470

bb20.2:                                           ; preds = %bb14.2, %bb9.2, %bb20.1
    #dbg_value(i32 3, !441, !DIExpression(), !460)
  br label %bb23, !dbg !471

bb9:                                              ; preds = %bb7
  %pipe_left = load i16, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, align 2, !dbg !462, !noundef !23
    #dbg_value(i16 %pipe_left, !443, !DIExpression(), !463)
    #dbg_value(i16 %pipe_left, !445, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !464)
    #dbg_value(i16 poison, !447, !DIExpression(DW_OP_constu, 4, DW_OP_minus, DW_OP_stack_value), !465)
    #dbg_value(i16 poison, !449, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !466)
  %6 = add i16 %pipe_left, -5, !dbg !467
  %or.cond = icmp ult i16 %6, 6, !dbg !467
  br i1 %or.cond, label %bb14, label %bb20, !dbg !467

bb14:                                             ; preds = %bb9
  %_22 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 2), align 2, !dbg !468, !noundef !23
    #dbg_value(i16 %_22, !449, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !466)
    #dbg_value(i16 %_22, !447, !DIExpression(DW_OP_constu, 4, DW_OP_minus, DW_OP_stack_value), !465)
  %gap_top = add i16 %_22, -4, !dbg !468
    #dbg_value(i16 %gap_top, !447, !DIExpression(), !465)
  %gap_bottom = add i16 %_22, 4, !dbg !469
    #dbg_value(i16 %gap_bottom, !449, !DIExpression(), !466)
  %_31 = icmp slt i16 %bird_screen_y, %gap_top, !dbg !470
  %_32 = icmp sgt i16 %bird_bottom, %gap_bottom
  %or.cond5 = or i1 %_31, %_32, !dbg !470
  br i1 %or.cond5, label %bb23, label %bb20, !dbg !470
}

; lib::drawReadyScreen
; Function Attrs: nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib15drawReadyScreen17h28203f98bd85755bE() unnamed_addr #3 !dbg !472 {
start:
    #dbg_value(i16 10, !474, !DIExpression(), !476)
; call lib::fillRect
  tail call fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef 8, i16 noundef 9, i16 noundef 10, i16 noundef 11) #11, !dbg !477
; call lib::setPixel
  tail call fastcc void @_ZN3lib8setPixel17h43bda99ce5e3fe75E(i16 noundef 9, i16 noundef 6) #11, !dbg !478
; call lib::setPixel
  tail call fastcc void @_ZN3lib8setPixel17h43bda99ce5e3fe75E(i16 noundef 8, i16 noundef 7) #11, !dbg !479
; call lib::setPixel
  tail call fastcc void @_ZN3lib8setPixel17h43bda99ce5e3fe75E(i16 noundef 9, i16 noundef 7) #11, !dbg !480
; call lib::setPixel
  tail call fastcc void @_ZN3lib8setPixel17h43bda99ce5e3fe75E(i16 noundef 10, i16 noundef 7) #11, !dbg !481
  ret void, !dbg !482
}

; lib::spawn_initial_pipes
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib19spawn_initial_pipes17h2e23eac7186d6fd2E() unnamed_addr #1 !dbg !483 {
start:
; call lib::spawn_pipe
  tail call fastcc void @_ZN3lib10spawn_pipe17h6d0176eb64ed2057E(i16 noundef 42) #11, !dbg !484
  ret void, !dbg !485
}

; lib::find_rightmost_pipe_x
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(read, argmem: none, inaccessiblemem: none)
define internal fastcc noundef range(i16 -100, -32768) i16 @_ZN3lib21find_rightmost_pipe_x17hadc4e3130a184b0aE() unnamed_addr #5 !dbg !486 {
start:
    #dbg_value(i16 -100, !488, !DIExpression(), !492)
    #dbg_value(i32 0, !490, !DIExpression(), !493)
    #dbg_value(i16 -100, !488, !DIExpression(), !492)
    #dbg_value(i32 0, !490, !DIExpression(), !493)
  %_5 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 4), align 2, !dbg !494, !noundef !23
  %0 = icmp eq i8 %_5, 0, !dbg !494
  %_10 = load i16, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, align 2, !dbg !494
  %spec.select = tail call i16 @llvm.smax.i16(i16 %_10, i16 -100), !dbg !494
  %max_x.sroa.0.1 = select i1 %0, i16 -100, i16 %spec.select, !dbg !494
    #dbg_value(i16 %max_x.sroa.0.1, !488, !DIExpression(), !492)
    #dbg_value(i32 1, !490, !DIExpression(), !493)
  %_5.1 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 10), align 2, !dbg !494, !noundef !23
  %1 = icmp eq i8 %_5.1, 0, !dbg !494
  %_10.1 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 6), align 2, !dbg !494
  %spec.select.1 = tail call i16 @llvm.smax.i16(i16 %_10.1, i16 %max_x.sroa.0.1), !dbg !494
  %max_x.sroa.0.1.1 = select i1 %1, i16 %max_x.sroa.0.1, i16 %spec.select.1, !dbg !494
    #dbg_value(i16 %max_x.sroa.0.1.1, !488, !DIExpression(), !492)
    #dbg_value(i32 2, !490, !DIExpression(), !493)
  %_5.2 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 16), align 2, !dbg !494, !noundef !23
  %2 = icmp eq i8 %_5.2, 0, !dbg !494
  %_10.2 = load i16, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 12), align 2, !dbg !494
  %spec.select.2 = tail call i16 @llvm.smax.i16(i16 %_10.2, i16 %max_x.sroa.0.1.1), !dbg !494
  %max_x.sroa.0.1.2 = select i1 %2, i16 %max_x.sroa.0.1.1, i16 %spec.select.2, !dbg !494
    #dbg_value(i16 %max_x.sroa.0.1.2, !488, !DIExpression(), !492)
    #dbg_value(i32 3, !490, !DIExpression(), !493)
  ret i16 %max_x.sroa.0.1.2, !dbg !495
}

; lib::clearFB
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(write, argmem: none, inaccessiblemem: none)
define internal fastcc void @_ZN3lib7clearFB17hdd3e5919c5b634efE() unnamed_addr #2 !dbg !496 {
start:
    #dbg_value(i32 0, !498, !DIExpression(), !500)
  tail call void @llvm.memset.p0.i32(ptr noundef nonnull align 1 dereferenceable(80) @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i8 0, i32 80, i1 false), !dbg !501
    #dbg_value(i32 poison, !498, !DIExpression(), !500)
  ret void, !dbg !502
}

; lib::drawBird
; Function Attrs: nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib8drawBird17hf8f2a7b43ff767a3E() unnamed_addr #3 !dbg !503 {
start:
    #dbg_value(i16 8, !505, !DIExpression(), !509)
  %_2 = load i16, ptr @_ZN3lib4BIRD17h571dc8b4c80d60d7E.0, align 2, !dbg !510, !noundef !23
  %y = ashr i16 %_2, 8, !dbg !510
    #dbg_value(i16 %y, !507, !DIExpression(), !511)
  %_5 = add nsw i16 %y, 2, !dbg !512
; call lib::fillRect
  tail call fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef 8, i16 noundef %y, i16 noundef 10, i16 noundef %_5) #11, !dbg !513
  ret void, !dbg !514
}

; lib::drawPipe
; Function Attrs: nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib8drawPipe17hb26dbc7dfdbd4978E(i32 noundef range(i32 0, 3) %idx) unnamed_addr #3 !dbg !515 {
start:
    #dbg_value(i32 %idx, !519, !DIExpression(), !528)
  %0 = getelementptr inbounds nuw %Pipe, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 %idx, !dbg !529
  %x = load i16, ptr %0, align 2, !dbg !529, !noundef !23
    #dbg_value(i16 %x, !520, !DIExpression(), !530)
  %1 = getelementptr inbounds nuw i8, ptr %0, i32 2, !dbg !531
  %gap_y = load i16, ptr %1, align 2, !dbg !531, !noundef !23
    #dbg_value(i16 %gap_y, !522, !DIExpression(), !532)
  %gap_top = add i16 %gap_y, -4, !dbg !533
    #dbg_value(i16 %gap_top, !524, !DIExpression(), !534)
  %gap_bottom = add i16 %gap_y, 4, !dbg !535
    #dbg_value(i16 %gap_bottom, !526, !DIExpression(), !536)
  %_8 = icmp sgt i16 %gap_top, 0, !dbg !537
  br i1 %_8, label %bb3, label %bb5, !dbg !537

bb5:                                              ; preds = %bb3, %start
  %_13 = icmp slt i16 %gap_bottom, 20, !dbg !538
  br i1 %_13, label %bb6, label %bb8, !dbg !538

bb3:                                              ; preds = %start
  %_10 = add i16 %x, 3, !dbg !539
  %_12 = add i16 %gap_y, -5, !dbg !540
; call lib::fillRect
  tail call fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef %x, i16 noundef 0, i16 noundef %_10, i16 noundef %_12) #11, !dbg !541
  br label %bb5, !dbg !542

bb8:                                              ; preds = %bb6, %bb5
  ret void, !dbg !543

bb6:                                              ; preds = %bb5
  %_15 = add i16 %x, 3, !dbg !544
; call lib::fillRect
  tail call fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef %x, i16 noundef %gap_bottom, i16 noundef %_15, i16 noundef 19) #11, !dbg !545
  br label %bb8, !dbg !546
}

; lib::drawRect
; Function Attrs: nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib8drawRect17h579d1c66bf16d8b0E() unnamed_addr #3 !dbg !547 {
start:
    #dbg_value(i16 8, !551, !DIExpression(), !556)
    #dbg_value(i16 5, !552, !DIExpression(), !556)
    #dbg_value(i16 23, !553, !DIExpression(), !556)
    #dbg_value(i16 14, !554, !DIExpression(), !556)
    #dbg_value(i8 1, !555, !DIExpression(), !556)
; call lib::fillRect
  tail call fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef 8, i16 noundef 5, i16 noundef 23, i16 noundef 5) #11, !dbg !557
; call lib::fillRect
  tail call fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef 23, i16 noundef 5, i16 noundef 23, i16 noundef 14) #11, !dbg !558
; call lib::fillRect
  tail call fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef 8, i16 noundef 14, i16 noundef 23, i16 noundef 14) #11, !dbg !559
; call lib::fillRect
  tail call fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef 8, i16 noundef 5, i16 noundef 8, i16 noundef 14) #11, !dbg !560
  ret void, !dbg !561
}

; lib::fillRect
; Function Attrs: nofree noinline norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none)
define internal fastcc void @_ZN3lib8fillRect17h4f9b61cc7fa27dcbE(i16 noundef %x0, i16 noundef range(i16 -32768, 128) %y0, i16 noundef %x1, i16 noundef range(i16 -126, 32767) %y1) unnamed_addr #6 !dbg !562 {
start:
    #dbg_value(i16 %x0, !564, !DIExpression(), !601)
    #dbg_value(i16 %y0, !565, !DIExpression(), !601)
    #dbg_value(i16 %x1, !566, !DIExpression(), !601)
    #dbg_value(i16 %y1, !567, !DIExpression(), !601)
    #dbg_value(i8 1, !568, !DIExpression(), !601)
    #dbg_value(i16 %x0, !569, !DIExpression(), !602)
    #dbg_value(i16 %y0, !571, !DIExpression(), !603)
    #dbg_value(i16 %x1, !573, !DIExpression(), !604)
    #dbg_value(i16 %y1, !575, !DIExpression(), !605)
  %0 = or i16 %y1, %x1, !dbg !606
  %or.cond = icmp slt i16 %0, 0, !dbg !606
  %_14 = icmp sgt i16 %x0, 31
  %or.cond5 = or i1 %_14, %or.cond, !dbg !606
  %_16 = icmp sgt i16 %y0, 19
  %or.cond6 = or i1 %_16, %or.cond5, !dbg !606
  br i1 %or.cond6, label %bb47, label %bb9, !dbg !606

bb9:                                              ; preds = %start
  %spec.store.select = tail call i16 @llvm.smax.i16(i16 %x0, i16 0), !dbg !607
    #dbg_value(i16 %spec.store.select, !569, !DIExpression(), !602)
  %spec.store.select8 = tail call i16 @llvm.smax.i16(i16 %y0, i16 0), !dbg !608
    #dbg_value(i16 %spec.store.select8, !571, !DIExpression(), !603)
  %spec.store.select7 = tail call i16 @llvm.smin.i16(i16 %x1, i16 31), !dbg !609
    #dbg_value(i16 %spec.store.select7, !573, !DIExpression(), !604)
  %spec.store.select9 = tail call i16 @llvm.smin.i16(i16 %y1, i16 19), !dbg !610
    #dbg_value(i16 %spec.store.select9, !575, !DIExpression(), !605)
  %_27 = lshr i16 %spec.store.select, 3, !dbg !611
  %start_byte = zext nneg i16 %_27 to i32, !dbg !611
    #dbg_value(i32 %start_byte, !577, !DIExpression(), !612)
  %_30 = lshr i16 %spec.store.select7, 3, !dbg !613
  %end_byte = zext nneg i16 %_30 to i32, !dbg !613
    #dbg_value(i32 %end_byte, !579, !DIExpression(), !614)
  %1 = trunc i16 %spec.store.select to i8, !dbg !615
  %_34 = and i8 %1, 7, !dbg !615
  %_33 = lshr i8 -1, %_34, !dbg !616
    #dbg_value(i8 %_33, !581, !DIExpression(), !617)
  %2 = trunc i16 %spec.store.select7 to i8, !dbg !618
  %3 = and i8 %2, 7, !dbg !618
  %_39 = xor i8 %3, 7, !dbg !618
  %_38 = shl nsw i8 -1, %_39, !dbg !619
    #dbg_value(i8 %_38, !583, !DIExpression(), !620)
    #dbg_value(i16 %spec.store.select8, !585, !DIExpression(), !621)
  %invariant.gep30 = getelementptr i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %start_byte, !dbg !622
  %invariant.gep32 = getelementptr i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %end_byte, !dbg !622
  %invariant.gep34 = getelementptr i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %start_byte, !dbg !622
    #dbg_value(i16 %spec.store.select8, !585, !DIExpression(), !621)
  %_44.not36 = icmp sgt i16 %spec.store.select8, %spec.store.select9, !dbg !623
  br i1 %_44.not36, label %bb47, label %bb23.lr.ph, !dbg !623

bb23.lr.ph:                                       ; preds = %bb9
  %_50 = icmp eq i16 %_27, %_30
  %b.sroa.0.027 = add nuw nsw i32 %start_byte, 1
  %_7528 = icmp samesign ult i32 %b.sroa.0.027, %end_byte
  %mask = and i8 %_38, %_33
  %4 = zext nneg i16 %spec.store.select8 to i32, !dbg !623
  %5 = shl nuw nsw i32 %4, 2, !dbg !623
  %6 = xor i32 %start_byte, -1, !dbg !623
  %7 = add nsw i32 %6, %end_byte, !dbg !623
  %8 = sext i16 %spec.store.select9 to i32, !dbg !623
  %9 = getelementptr i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %5
  %10 = getelementptr i8, ptr %9, i32 %start_byte
  %11 = getelementptr i8, ptr %10, i32 1
  br label %bb23, !dbg !623

bb23:                                             ; preds = %bb23.lr.ph, %bb45
  %indvars.iv = phi i32 [ %4, %bb23.lr.ph ], [ %indvars.iv.next, %bb45 ]
  %indvar = phi i32 [ 0, %bb23.lr.ph ], [ %indvar.next, %bb45 ]
  %12 = shl nuw nsw i32 %indvar, 2, !dbg !624
  %scevgep = getelementptr i8, ptr %11, i32 %12, !dbg !624
    #dbg_value(i32 %indvars.iv, !585, !DIExpression(), !621)
  %13 = shl i32 %indvars.iv, 2, !dbg !624
    #dbg_value(i32 %13, !587, !DIExpression(), !625)
  br i1 %_50, label %bb45, label %bb31, !dbg !626

bb47:                                             ; preds = %bb45, %bb9, %start
  ret void, !dbg !627

bb31:                                             ; preds = %bb23
    #dbg_value(!DIArgList(i32 %13, i32 %start_byte), !593, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus, DW_OP_stack_value), !628)
    #dbg_value(!DIArgList(i32 %13, i32 %start_byte), !593, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus, DW_OP_stack_value), !628)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !647)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !647)
    #dbg_value(!DIArgList(i32 %13, i32 %start_byte), !643, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus, DW_OP_stack_value), !647)
    #dbg_value(!DIArgList(i32 %13, i32 %start_byte), !649, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus, DW_OP_stack_value), !664)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !664)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !664)
  %gep31 = getelementptr i8, ptr %invariant.gep30, i32 %13, !dbg !666
  %14 = load i8, ptr %gep31, align 1, !dbg !667, !noundef !23
  %15 = or i8 %14, %_33, !dbg !667
  store i8 %15, ptr %gep31, align 1, !dbg !667
    #dbg_value(i8 -1, !595, !DIExpression(), !668)
    #dbg_value(i8 -1, !595, !DIExpression(), !668)
    #dbg_value(i32 %start_byte, !597, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !669)
  br i1 %_7528, label %bb37.preheader, label %bb45, !dbg !670

bb37.preheader:                                   ; preds = %bb31
  tail call void @llvm.memset.p0.i32(ptr align 1 %scevgep, i8 -1, i32 %7, i1 false), !dbg !671
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !672)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !672)
    #dbg_value(!DIArgList(i32 poison, i32 %13), !643, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus, DW_OP_stack_value), !672)
    #dbg_value(!DIArgList(i32 poison, i32 %13), !649, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_plus, DW_OP_stack_value), !674)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !674)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !674)
    #dbg_value(i32 poison, !597, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !669)
  br label %bb45, !dbg !676

bb45:                                             ; preds = %bb31, %bb37.preheader, %bb23
  %invariant.gep34.sink = phi ptr [ %invariant.gep34, %bb23 ], [ %invariant.gep32, %bb37.preheader ], [ %invariant.gep32, %bb31 ]
  %mask.sink = phi i8 [ %mask, %bb23 ], [ %_38, %bb37.preheader ], [ %_38, %bb31 ]
  %gep35 = getelementptr i8, ptr %invariant.gep34.sink, i32 %13, !dbg !679
  %16 = load i8, ptr %gep35, align 1, !dbg !625, !noundef !23
  %17 = or i8 %16, %mask.sink, !dbg !625
  store i8 %17, ptr %gep35, align 1, !dbg !625
  %indvars.iv.next = add nuw nsw i32 %indvars.iv, 1, !dbg !681
    #dbg_value(i32 %indvars.iv.next, !585, !DIExpression(), !621)
  %_44.not.not = icmp slt i32 %indvars.iv, %8, !dbg !623
  %indvar.next = add nuw nsw i32 %indvar, 1, !dbg !623
  br i1 %_44.not.not, label %bb23, label %bb47, !dbg !623
}

; lib::setPixel
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define internal fastcc void @_ZN3lib8setPixel17h43bda99ce5e3fe75E(i16 noundef range(i16 8, 18) %x, i16 noundef range(i16 6, 13) %y) unnamed_addr #4 !dbg !682 {
start:
    #dbg_value(i16 %x, !686, !DIExpression(), !693)
    #dbg_value(i16 %y, !687, !DIExpression(), !693)
    #dbg_value(i8 1, !688, !DIExpression(), !693)
    #dbg_value(!DIArgList(i16 %y, i16 %x), !689, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 2, DW_OP_shl, DW_OP_LLVM_arg, 1, DW_OP_constu, 3, DW_OP_shr, DW_OP_or, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_stack_value), !694)
    #dbg_value(!DIArgList(i8 -128, i16 %x), !691, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 8, DW_ATE_unsigned, DW_OP_constu, 7, DW_OP_and, DW_OP_shr, DW_OP_stack_value), !695)
  %0 = trunc nuw nsw i16 %x to i8, !dbg !696
    #dbg_value(!DIArgList(i8 -128, i8 %0), !691, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 7, DW_OP_and, DW_OP_shr, DW_OP_stack_value), !695)
  %_14 = and i8 %0, 7, !dbg !696
    #dbg_value(!DIArgList(i8 -128, i8 %_14), !691, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_stack_value), !695)
  %_13 = lshr exact i8 -128, %_14, !dbg !697
    #dbg_value(i8 %_13, !691, !DIExpression(), !695)
  %_10 = shl nuw nsw i16 %y, 2, !dbg !698
    #dbg_value(!DIArgList(i16 %_10, i16 %x), !689, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 3, DW_OP_shr, DW_OP_or, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_stack_value), !694)
  %_11 = lshr i16 %x, 3, !dbg !699
    #dbg_value(!DIArgList(i16 %_10, i16 %_11), !689, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_or, DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_stack_value), !694)
  %_9 = or disjoint i16 %_10, %_11, !dbg !700
    #dbg_value(i16 %_9, !689, !DIExpression(DW_OP_LLVM_convert, 16, DW_ATE_unsigned, DW_OP_LLVM_convert, 32, DW_ATE_unsigned, DW_OP_stack_value), !694)
  %byte_idx = zext nneg i16 %_9 to i32, !dbg !700
    #dbg_value(i32 %byte_idx, !689, !DIExpression(), !694)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !701)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !701)
    #dbg_value(i32 %byte_idx, !643, !DIExpression(), !701)
    #dbg_value(i32 %byte_idx, !649, !DIExpression(), !703)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !703)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !703)
  %_0.i.i = getelementptr inbounds nuw i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %byte_idx, !dbg !705
  %1 = load i8, ptr %_0.i.i, align 1, !dbg !706, !noundef !23
  %2 = or i8 %1, %_13, !dbg !706
  store i8 %2, ptr %_0.i.i, align 1, !dbg !706
  ret void, !dbg !707
}

; lib::drawDigit
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none)
define internal fastcc void @_ZN3lib9drawDigit17h0ebc745f1e2cb6a0E(i16 noundef %x, i16 noundef range(i16 2, 9) %y, i16 noundef %digit) unnamed_addr #4 !dbg !708 {
start:
    #dbg_value(i16 %x, !710, !DIExpression(), !732)
    #dbg_value(i16 %y, !711, !DIExpression(), !732)
    #dbg_value(i16 %digit, !712, !DIExpression(), !732)
    #dbg_value(i8 1, !713, !DIExpression(), !732)
  %or.cond = icmp ugt i16 %digit, 9, !dbg !733
  %or.cond5 = icmp ugt i16 %x, 29
  %or.cond11 = or i1 %or.cond5, %or.cond, !dbg !733
  br i1 %or.cond11, label %bb28, label %bb7, !dbg !733

bb7:                                              ; preds = %start
  %0 = trunc nuw i16 %x to i8, !dbg !734
  %x_bit = and i8 %0, 7, !dbg !734
    #dbg_value(i8 %x_bit, !714, !DIExpression(), !735)
    #dbg_value(i16 0, !716, !DIExpression(), !736)
  %_21 = mul nuw nsw i16 %digit, 5
  %_28 = lshr i16 %x, 3
  %_29 = icmp samesign ult i8 %x_bit, 6
    #dbg_value(i16 0, !716, !DIExpression(), !736)
  %_48 = sub nuw nsw i8 13, %x_bit
  %shift = add nsw i8 %x_bit, -5
  %shift1 = sub nuw nsw i8 5, %x_bit
  %1 = zext nneg i16 %_21 to i32, !dbg !737
  %2 = zext nneg i16 %y to i32, !dbg !737
  %3 = zext nneg i16 %_28 to i32, !dbg !737
    #dbg_value(i32 0, !716, !DIExpression(), !736)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !738, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !749)
    #dbg_value(i32 50, !738, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !749)
    #dbg_value(i32 %1, !748, !DIExpression(), !749)
    #dbg_value(i32 %1, !751, !DIExpression(), !762)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !761, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !762)
    #dbg_value(i32 50, !761, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !762)
  %_0.i.i = getelementptr inbounds nuw i8, ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, i32 %1, !dbg !764
  %font_row = load i8, ptr %_0.i.i, align 1, !dbg !765, !noundef !23
    #dbg_value(i8 %font_row, !718, !DIExpression(), !766)
  %4 = shl nuw nsw i32 %2, 2, !dbg !767
  %5 = or disjoint i32 %4, %3, !dbg !768
    #dbg_value(i32 %5, !720, !DIExpression(), !769)
  %_32 = and i8 %font_row, 7, !dbg !769
  br i1 %_29, label %bb26, label %bb19, !dbg !770

bb28.sink.split:                                  ; preds = %bb26.3, %bb19.4
  %.sink = phi ptr [ getelementptr inbounds nuw (i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 1), %bb19.4 ], [ @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, %bb26.3 ]
  %_48.pn = phi i8 [ %_48, %bb19.4 ], [ %shift1, %bb26.3 ]
  %_46.4.sink = shl i8 %_32.4, %_48.pn, !dbg !769
  %gep.4 = getelementptr inbounds nuw i8, ptr %.sink, i32 %39, !dbg !771
  %6 = load i8, ptr %gep.4, align 1, !dbg !769, !noundef !23
  %7 = or i8 %6, %_46.4.sink, !dbg !769
  store i8 %7, ptr %gep.4, align 1, !dbg !769
  br label %bb28, !dbg !773

bb28:                                             ; preds = %bb28.sink.split, %start
  ret void, !dbg !773

bb19:                                             ; preds = %bb7
    #dbg_value(i8 %x_bit, !726, !DIExpression(DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !774)
    #dbg_value(!DIArgList(i8 %font_row, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %font_row, i8 13, i8 %x_bit), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %_32, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(i8 %shift, !726, !DIExpression(), !774)
    #dbg_value(!DIArgList(i8 %_32, i8 %shift), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_stack_value), !775)
  %mask1 = lshr i8 %_32, %shift, !dbg !777
    #dbg_value(i8 %mask1, !728, !DIExpression(), !775)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !778)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !778)
    #dbg_value(i32 %5, !643, !DIExpression(), !778)
    #dbg_value(i32 %5, !649, !DIExpression(), !780)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !780)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !780)
  %_0.i.i12 = getelementptr inbounds nuw i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %5, !dbg !782
  %8 = load i8, ptr %_0.i.i12, align 1, !dbg !783, !noundef !23
  %9 = or i8 %8, %mask1, !dbg !783
  store i8 %9, ptr %_0.i.i12, align 1, !dbg !783
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !784)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !784)
    #dbg_value(i32 %5, !643, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !784)
    #dbg_value(i32 %5, !649, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !786)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !786)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !786)
  br label %bb26, !dbg !788

bb26:                                             ; preds = %bb7, %bb19
  %_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E.sink = phi ptr [ getelementptr inbounds nuw (i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 1), %bb19 ], [ @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, %bb7 ]
  %shift1.pn = phi i8 [ %_48, %bb19 ], [ %shift1, %bb7 ]
  %mask13.sink = shl i8 %_32, %shift1.pn, !dbg !769
  %_0.i.i14 = getelementptr inbounds nuw i8, ptr %_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E.sink, i32 %5, !dbg !771
  %10 = load i8, ptr %_0.i.i14, align 1, !dbg !769, !noundef !23
  %11 = or i8 %10, %mask13.sink, !dbg !769
  store i8 %11, ptr %_0.i.i14, align 1, !dbg !769
    #dbg_value(i32 1, !716, !DIExpression(), !736)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !738, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !749)
    #dbg_value(i32 50, !738, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !749)
    #dbg_value(i32 %1, !748, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !749)
    #dbg_value(i32 %1, !751, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !762)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !761, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !762)
    #dbg_value(i32 50, !761, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !762)
  %12 = getelementptr inbounds nuw i8, ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, i32 %1, !dbg !764
  %_0.i.i.1 = getelementptr inbounds nuw i8, ptr %12, i32 1, !dbg !764
  %font_row.1 = load i8, ptr %_0.i.i.1, align 1, !dbg !765, !noundef !23
    #dbg_value(i8 %font_row.1, !718, !DIExpression(), !766)
  %13 = shl nuw nsw i32 %2, 2, !dbg !767
  %14 = add nuw nsw i32 %13, 4, !dbg !767
  %15 = or disjoint i32 %14, %3, !dbg !768
    #dbg_value(i32 %15, !720, !DIExpression(), !769)
  %_32.1 = and i8 %font_row.1, 7, !dbg !769
  br i1 %_29, label %bb26.1, label %bb19.1, !dbg !770

bb19.1:                                           ; preds = %bb26
    #dbg_value(i8 %x_bit, !726, !DIExpression(DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !774)
    #dbg_value(!DIArgList(i8 %font_row.1, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %font_row.1, i8 13, i8 %x_bit), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32.1, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %_32.1, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32.1, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(i8 %shift, !726, !DIExpression(), !774)
    #dbg_value(!DIArgList(i8 %_32.1, i8 %shift), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_stack_value), !775)
  %mask1.1 = lshr i8 %_32.1, %shift, !dbg !777
    #dbg_value(i8 %mask1.1, !728, !DIExpression(), !775)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !778)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !778)
    #dbg_value(i32 %15, !643, !DIExpression(), !778)
    #dbg_value(i32 %15, !649, !DIExpression(), !780)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !780)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !780)
  %_0.i.i12.1 = getelementptr inbounds nuw i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %15, !dbg !782
  %16 = load i8, ptr %_0.i.i12.1, align 1, !dbg !783, !noundef !23
  %17 = or i8 %16, %mask1.1, !dbg !783
  store i8 %17, ptr %_0.i.i12.1, align 1, !dbg !783
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !784)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !784)
    #dbg_value(i32 %15, !643, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !784)
    #dbg_value(i32 %15, !649, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !786)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !786)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !786)
  br label %bb26.1, !dbg !788

bb26.1:                                           ; preds = %bb26, %bb19.1
  %_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E.sink9 = phi ptr [ getelementptr inbounds nuw (i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 1), %bb19.1 ], [ @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, %bb26 ]
  %shift1.pn18 = phi i8 [ %_48, %bb19.1 ], [ %shift1, %bb26 ]
  %mask13.1.sink = shl i8 %_32.1, %shift1.pn18, !dbg !769
  %_0.i.i14.1 = getelementptr inbounds nuw i8, ptr %_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E.sink9, i32 %15, !dbg !771
  %18 = load i8, ptr %_0.i.i14.1, align 1, !dbg !769, !noundef !23
  %19 = or i8 %18, %mask13.1.sink, !dbg !769
  store i8 %19, ptr %_0.i.i14.1, align 1, !dbg !769
    #dbg_value(i32 2, !716, !DIExpression(), !736)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !738, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !749)
    #dbg_value(i32 50, !738, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !749)
    #dbg_value(i32 %1, !748, !DIExpression(DW_OP_plus_uconst, 2, DW_OP_stack_value), !749)
    #dbg_value(i32 %1, !751, !DIExpression(DW_OP_plus_uconst, 2, DW_OP_stack_value), !762)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !761, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !762)
    #dbg_value(i32 50, !761, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !762)
  %20 = getelementptr inbounds nuw i8, ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, i32 %1, !dbg !764
  %_0.i.i.2 = getelementptr inbounds nuw i8, ptr %20, i32 2, !dbg !764
  %font_row.2 = load i8, ptr %_0.i.i.2, align 1, !dbg !765, !noundef !23
    #dbg_value(i8 %font_row.2, !718, !DIExpression(), !766)
  %21 = shl nuw nsw i32 %2, 2, !dbg !767
  %22 = add nuw nsw i32 %21, 8, !dbg !767
  %23 = or disjoint i32 %22, %3, !dbg !768
    #dbg_value(i32 %23, !720, !DIExpression(), !769)
  %_32.2 = and i8 %font_row.2, 7, !dbg !769
  br i1 %_29, label %bb26.2, label %bb19.2, !dbg !770

bb19.2:                                           ; preds = %bb26.1
    #dbg_value(i8 %x_bit, !726, !DIExpression(DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !774)
    #dbg_value(!DIArgList(i8 %font_row.2, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %font_row.2, i8 13, i8 %x_bit), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32.2, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %_32.2, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32.2, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(i8 %shift, !726, !DIExpression(), !774)
    #dbg_value(!DIArgList(i8 %_32.2, i8 %shift), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_stack_value), !775)
  %mask1.2 = lshr i8 %_32.2, %shift, !dbg !777
    #dbg_value(i8 %mask1.2, !728, !DIExpression(), !775)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !778)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !778)
    #dbg_value(i32 %23, !643, !DIExpression(), !778)
    #dbg_value(i32 %23, !649, !DIExpression(), !780)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !780)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !780)
  %_0.i.i12.2 = getelementptr inbounds nuw i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %23, !dbg !782
  %24 = load i8, ptr %_0.i.i12.2, align 1, !dbg !783, !noundef !23
  %25 = or i8 %24, %mask1.2, !dbg !783
  store i8 %25, ptr %_0.i.i12.2, align 1, !dbg !783
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !784)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !784)
    #dbg_value(i32 %23, !643, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !784)
    #dbg_value(i32 %23, !649, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !786)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !786)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !786)
  br label %bb26.2, !dbg !788

bb26.2:                                           ; preds = %bb26.1, %bb19.2
  %_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E.sink13 = phi ptr [ getelementptr inbounds nuw (i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 1), %bb19.2 ], [ @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, %bb26.1 ]
  %shift1.pn19 = phi i8 [ %_48, %bb19.2 ], [ %shift1, %bb26.1 ]
  %mask13.2.sink = shl i8 %_32.2, %shift1.pn19, !dbg !769
  %_0.i.i14.2 = getelementptr inbounds nuw i8, ptr %_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E.sink13, i32 %23, !dbg !771
  %26 = load i8, ptr %_0.i.i14.2, align 1, !dbg !769, !noundef !23
  %27 = or i8 %26, %mask13.2.sink, !dbg !769
  store i8 %27, ptr %_0.i.i14.2, align 1, !dbg !769
    #dbg_value(i32 3, !716, !DIExpression(), !736)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !738, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !749)
    #dbg_value(i32 50, !738, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !749)
    #dbg_value(i32 %1, !748, !DIExpression(DW_OP_plus_uconst, 3, DW_OP_stack_value), !749)
    #dbg_value(i32 %1, !751, !DIExpression(DW_OP_plus_uconst, 3, DW_OP_stack_value), !762)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !761, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !762)
    #dbg_value(i32 50, !761, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !762)
  %28 = getelementptr inbounds nuw i8, ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, i32 %1, !dbg !764
  %_0.i.i.3 = getelementptr inbounds nuw i8, ptr %28, i32 3, !dbg !764
  %font_row.3 = load i8, ptr %_0.i.i.3, align 1, !dbg !765, !noundef !23
    #dbg_value(i8 %font_row.3, !718, !DIExpression(), !766)
  %29 = shl nuw nsw i32 %2, 2, !dbg !767
  %30 = add nuw nsw i32 %29, 12, !dbg !767
  %31 = or disjoint i32 %30, %3, !dbg !768
    #dbg_value(i32 %31, !720, !DIExpression(), !769)
  %_32.3 = and i8 %font_row.3, 7, !dbg !769
  br i1 %_29, label %bb26.3, label %bb19.3, !dbg !770

bb19.3:                                           ; preds = %bb26.2
    #dbg_value(i8 %x_bit, !726, !DIExpression(DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !774)
    #dbg_value(!DIArgList(i8 %font_row.3, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %font_row.3, i8 13, i8 %x_bit), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32.3, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %_32.3, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32.3, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(i8 %shift, !726, !DIExpression(), !774)
    #dbg_value(!DIArgList(i8 %_32.3, i8 %shift), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_stack_value), !775)
  %mask1.3 = lshr i8 %_32.3, %shift, !dbg !777
    #dbg_value(i8 %mask1.3, !728, !DIExpression(), !775)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !778)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !778)
    #dbg_value(i32 %31, !643, !DIExpression(), !778)
    #dbg_value(i32 %31, !649, !DIExpression(), !780)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !780)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !780)
  %_0.i.i12.3 = getelementptr inbounds nuw i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %31, !dbg !782
  %32 = load i8, ptr %_0.i.i12.3, align 1, !dbg !783, !noundef !23
  %33 = or i8 %32, %mask1.3, !dbg !783
  store i8 %33, ptr %_0.i.i12.3, align 1, !dbg !783
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !784)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !784)
    #dbg_value(i32 %31, !643, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !784)
    #dbg_value(i32 %31, !649, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !786)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !786)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !786)
  br label %bb26.3, !dbg !788

bb26.3:                                           ; preds = %bb26.2, %bb19.3
  %_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E.sink17 = phi ptr [ getelementptr inbounds nuw (i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 1), %bb19.3 ], [ @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, %bb26.2 ]
  %shift1.pn20 = phi i8 [ %_48, %bb19.3 ], [ %shift1, %bb26.2 ]
  %mask13.3.sink = shl i8 %_32.3, %shift1.pn20, !dbg !769
  %_0.i.i14.3 = getelementptr inbounds nuw i8, ptr %_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E.sink17, i32 %31, !dbg !771
  %34 = load i8, ptr %_0.i.i14.3, align 1, !dbg !769, !noundef !23
  %35 = or i8 %34, %mask13.3.sink, !dbg !769
  store i8 %35, ptr %_0.i.i14.3, align 1, !dbg !769
    #dbg_value(i32 4, !716, !DIExpression(), !736)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !738, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !749)
    #dbg_value(i32 50, !738, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !749)
    #dbg_value(i32 %1, !748, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !749)
    #dbg_value(i32 %1, !751, !DIExpression(DW_OP_plus_uconst, 4, DW_OP_stack_value), !762)
    #dbg_value(ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, !761, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !762)
    #dbg_value(i32 50, !761, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !762)
  %36 = getelementptr inbounds nuw i8, ptr @_ZN3lib10DIGIT_FONT17h568307813fef6c2aE, i32 %1, !dbg !764
  %_0.i.i.4 = getelementptr inbounds nuw i8, ptr %36, i32 4, !dbg !764
  %font_row.4 = load i8, ptr %_0.i.i.4, align 1, !dbg !765, !noundef !23
    #dbg_value(i8 %font_row.4, !718, !DIExpression(), !766)
  %37 = shl nuw nsw i32 %2, 2, !dbg !767
  %38 = add nuw nsw i32 %37, 16, !dbg !767
  %39 = or disjoint i32 %38, %3, !dbg !768
    #dbg_value(i32 %39, !720, !DIExpression(), !769)
  %_32.4 = and i8 %font_row.4, 7, !dbg !769
  br i1 %_29, label %bb28.sink.split, label %bb19.4, !dbg !770

bb19.4:                                           ; preds = %bb26.3
    #dbg_value(i8 %x_bit, !726, !DIExpression(DW_OP_constu, 5, DW_OP_minus, DW_OP_stack_value), !774)
    #dbg_value(!DIArgList(i8 %font_row.4, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %font_row.4, i8 13, i8 %x_bit), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_constu, 7, DW_OP_and, DW_OP_LLVM_arg, 1, DW_OP_LLVM_arg, 2, DW_OP_minus, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32.4, i8 %x_bit), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_constu, 5, DW_OP_minus, DW_OP_shr, DW_OP_stack_value), !775)
    #dbg_value(!DIArgList(i8 %_32.4, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(!DIArgList(i8 %_32.4, i8 %_48), !730, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shl, DW_OP_stack_value), !776)
    #dbg_value(i8 %shift, !726, !DIExpression(), !774)
    #dbg_value(!DIArgList(i8 %_32.4, i8 %shift), !728, !DIExpression(DW_OP_LLVM_arg, 0, DW_OP_LLVM_arg, 1, DW_OP_shr, DW_OP_stack_value), !775)
  %mask1.4 = lshr i8 %_32.4, %shift, !dbg !777
    #dbg_value(i8 %mask1.4, !728, !DIExpression(), !775)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !778)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !778)
    #dbg_value(i32 %39, !643, !DIExpression(), !778)
    #dbg_value(i32 %39, !649, !DIExpression(), !780)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !780)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !780)
  %_0.i.i12.4 = getelementptr inbounds nuw i8, ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i32 %39, !dbg !782
  %40 = load i8, ptr %_0.i.i12.4, align 1, !dbg !783, !noundef !23
  %41 = or i8 %40, %mask1.4, !dbg !783
  store i8 %41, ptr %_0.i.i12.4, align 1, !dbg !783
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !629, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !784)
    #dbg_value(i32 80, !629, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !784)
    #dbg_value(i32 %39, !643, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !784)
    #dbg_value(i32 %39, !649, !DIExpression(DW_OP_plus_uconst, 1, DW_OP_stack_value), !786)
    #dbg_value(ptr @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, !662, !DIExpression(DW_OP_LLVM_fragment, 0, 32), !786)
    #dbg_value(i32 80, !662, !DIExpression(DW_OP_LLVM_fragment, 32, 32), !786)
  br label %bb28.sink.split, !dbg !788
}

; lib::drawPipes
; Function Attrs: nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib9drawPipes17hc093196a1ee1552cE() unnamed_addr #3 !dbg !789 {
start:
    #dbg_value(i32 0, !791, !DIExpression(), !793)
    #dbg_value(i32 0, !791, !DIExpression(), !793)
  %_4 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 4), align 2, !dbg !794, !noundef !23
  %0 = icmp eq i8 %_4, 0, !dbg !794
  br i1 %0, label %bb7, label %bb4, !dbg !794

bb4:                                              ; preds = %start
; call lib::drawPipe
  tail call fastcc void @_ZN3lib8drawPipe17hb26dbc7dfdbd4978E(i32 noundef 0) #11, !dbg !795
  br label %bb7, !dbg !796

bb7:                                              ; preds = %start, %bb4
    #dbg_value(i32 1, !791, !DIExpression(), !793)
  %_4.1 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 10), align 2, !dbg !794, !noundef !23
  %1 = icmp eq i8 %_4.1, 0, !dbg !794
  br i1 %1, label %bb7.1, label %bb4.1, !dbg !794

bb4.1:                                            ; preds = %bb7
; call lib::drawPipe
  tail call fastcc void @_ZN3lib8drawPipe17hb26dbc7dfdbd4978E(i32 noundef 1) #11, !dbg !795
  br label %bb7.1, !dbg !796

bb7.1:                                            ; preds = %bb4.1, %bb7
    #dbg_value(i32 2, !791, !DIExpression(), !793)
  %_4.2 = load i8, ptr getelementptr inbounds nuw (i8, ptr @_ZN3lib5PIPES17h0b113f338cd5ae43E, i32 16), align 2, !dbg !794, !noundef !23
  %2 = icmp eq i8 %_4.2, 0, !dbg !794
  br i1 %2, label %bb7.2, label %bb4.2, !dbg !794

bb4.2:                                            ; preds = %bb7.1
; call lib::drawPipe
  tail call fastcc void @_ZN3lib8drawPipe17hb26dbc7dfdbd4978E(i32 noundef 2) #11, !dbg !795
  br label %bb7.2, !dbg !796

bb7.2:                                            ; preds = %bb4.2, %bb7.1
    #dbg_value(i32 3, !791, !DIExpression(), !793)
  ret void, !dbg !797
}

; lib::drawScore
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib9drawScore17h21f5311f5325b862E() unnamed_addr #1 !dbg !798 {
start:
  %_2 = load i16, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.1, align 2, !dbg !799, !noundef !23
; call lib::drawNumber
  tail call fastcc void @_ZN3lib10drawNumber17h9e0b83d1ba77bfc9E(i16 noundef 2, i16 noundef %_2) #11, !dbg !800
  ret void, !dbg !801
}

; lib::game_tick
; Function Attrs: mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define internal fastcc void @_ZN3lib9game_tick17h3339f306e2fb44f3E(i8 noundef range(i8 0, 2) %flap_input) unnamed_addr #1 !dbg !802 {
start:
    #dbg_value(i8 %flap_input, !804, !DIExpression(), !805)
  %_3 = load i8, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.0, align 2, !dbg !806, !noundef !23
  switch i8 %_3, label %bb7 [
    i8 0, label %bb1
    i8 1, label %bb6
  ], !dbg !806

bb1:                                              ; preds = %start
  %0 = icmp eq i8 %flap_input, 0, !dbg !807
  br i1 %0, label %bb19, label %bb2, !dbg !807

bb7:                                              ; preds = %start
  %_12 = icmp ne i8 %_3, 2, !dbg !808
  %1 = icmp eq i8 %flap_input, 0
  %or.cond = or i1 %1, %_12, !dbg !808
  br i1 %or.cond, label %bb19, label %bb16, !dbg !808

bb6:                                              ; preds = %start
; call lib::update_bird
  tail call fastcc void @_ZN3lib11update_bird17h3beb04e75e34aa8aE(i8 noundef %flap_input) #11, !dbg !809
; call lib::update_pipes
  tail call fastcc void @_ZN3lib12update_pipes17h766c122619250a74E() #11, !dbg !810
; call lib::check_collision
  %_11 = tail call fastcc noundef i8 @_ZN3lib15check_collision17h4f705c960de6c75bE() #11, !dbg !811
  %2 = icmp eq i8 %_11, 0, !dbg !811
  br i1 %2, label %bb13, label %bb11, !dbg !811

bb16:                                             ; preds = %bb7
; call lib::reset_game
  tail call fastcc void @_ZN3lib10reset_game17hd18b9fe9bf0032f6E() #11, !dbg !812
  br label %bb19, !dbg !812

bb19:                                             ; preds = %bb1, %bb2, %bb16, %bb7, %bb13
  ret void, !dbg !813

bb11:                                             ; preds = %bb6
  store i8 2, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.0, align 2, !dbg !814
  br label %bb13, !dbg !815

bb13:                                             ; preds = %bb6, %bb11
  %3 = load i16, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.2, align 2, !dbg !816, !noundef !23
  %4 = add i16 %3, 1, !dbg !816
  store i16 %4, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.2, align 2, !dbg !816
  br label %bb19, !dbg !805

bb2:                                              ; preds = %bb1
  store i8 1, ptr @_ZN3lib4GAME17hbf8763b2c745ccd8E.0, align 2, !dbg !817
; call lib::spawn_initial_pipes
  tail call fastcc void @_ZN3lib19spawn_initial_pipes17h2e23eac7186d6fd2E() #11, !dbg !818
; call lib::update_bird
  tail call fastcc void @_ZN3lib11update_bird17h3beb04e75e34aa8aE(i8 noundef 1) #11, !dbg !819
  br label %bb19, !dbg !819
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define dso_local void @_jcsl_method_cap_fix() unnamed_addr #7 !dbg !820 {
start:
  ret void, !dbg !821
}

; Function Attrs: nounwind
define dso_local void @process(ptr noundef %apdu, i16 noundef signext %apdu_len) unnamed_addr #8 !dbg !822 {
start:
    #dbg_value(ptr %apdu, !827, !DIExpression(), !835)
    #dbg_value(i16 %apdu_len, !828, !DIExpression(), !835)
  %buffer = tail call noundef ptr @jc_APDU_getBuffer(ptr noundef %apdu) #11, !dbg !836
    #dbg_value(ptr %buffer, !829, !DIExpression(), !837)
    #dbg_value(ptr %buffer, !838, !DIExpression(), !848)
    #dbg_value(i32 1, !847, !DIExpression(), !848)
  %_0.i1 = getelementptr inbounds nuw i8, ptr %buffer, i32 1, !dbg !850
  %ins = load i8, ptr %_0.i1, align 1, !dbg !851, !noundef !23
    #dbg_value(i8 %ins, !831, !DIExpression(), !852)
  %_6.b = load i1, ptr @_ZN3lib16GAME_INITIALIZED17hdc6bee963eb1f766E.0, align 1, !dbg !853
  br i1 %_6.b, label %bb6, label %bb3, !dbg !853

bb3:                                              ; preds = %start
; call lib::reset_game
  tail call fastcc void @_ZN3lib10reset_game17hd18b9fe9bf0032f6E() #11, !dbg !854
  store i1 true, ptr @_ZN3lib16GAME_INITIALIZED17hdc6bee963eb1f766E.0, align 1, !dbg !855
  br label %bb6, !dbg !856

bb6:                                              ; preds = %start, %bb3
  switch i8 %ins, label %bb13 [
    i8 2, label %bb7
    i8 1, label %bb12
  ], !dbg !857

bb7:                                              ; preds = %bb6
; call lib::reset_game
  tail call fastcc void @_ZN3lib10reset_game17hd18b9fe9bf0032f6E() #11, !dbg !858
  %_11 = tail call noundef signext i16 @jc_APDU_setOutgoing(ptr noundef %apdu) #11, !dbg !859
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %apdu, i16 noundef signext 0) #11, !dbg !860
  br label %bb25, !dbg !852

bb13:                                             ; preds = %bb6
  tail call void @jc_ISOException_throwIt(i16 noundef signext 27904) #11, !dbg !861
  br label %bb25, !dbg !861

bb12:                                             ; preds = %bb6
  %_15 = icmp sgt i16 %apdu_len, 0, !dbg !862
  br i1 %_15, label %bb14, label %bb17, !dbg !862

bb25:                                             ; preds = %bb7, %bb17, %bb13
  ret void, !dbg !863

bb14:                                             ; preds = %bb12
    #dbg_value(ptr %buffer, !838, !DIExpression(), !864)
    #dbg_value(i32 5, !847, !DIExpression(), !864)
  %_0.i = getelementptr inbounds nuw i8, ptr %buffer, i32 5, !dbg !866
  %_16 = load i8, ptr %_0.i, align 1, !dbg !867, !noundef !23
  %0 = and i8 %_16, 1, !dbg !867
    #dbg_value(i8 %0, !833, !DIExpression(), !868)
  br label %bb17, !dbg !869

bb17:                                             ; preds = %bb12, %bb14
  %flap.sroa.0.0 = phi i8 [ %0, %bb14 ], [ 0, %bb12 ], !dbg !852
    #dbg_value(i8 %flap.sroa.0.0, !833, !DIExpression(), !868)
; call lib::game_tick
  tail call fastcc void @_ZN3lib9game_tick17h3339f306e2fb44f3E(i8 noundef %flap.sroa.0.0) #11, !dbg !870
; call lib::clearFB
  tail call fastcc void @_ZN3lib7clearFB17hdd3e5919c5b634efE() #11, !dbg !871
; call lib::render_game
  tail call fastcc void @_ZN3lib11render_game17h39ae85af2824aafbE() #11, !dbg !872
  %_22 = tail call noundef signext i16 @jc_APDU_setOutgoing(ptr noundef %apdu) #11, !dbg !873
  tail call void @jc_APDU_setOutgoingLength(ptr noundef %apdu, i16 noundef signext 80) #11, !dbg !874
  tail call void @jc_APDU_sendBytesLong(ptr noundef %apdu, ptr noundef nonnull @_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E, i16 noundef signext 0, i16 noundef signext 80) #11, !dbg !875
  br label %bb25, !dbg !852
}

; Function Attrs: nounwind
declare dso_local noundef ptr @jc_APDU_getBuffer(ptr noundef) unnamed_addr #8

; Function Attrs: nounwind
declare dso_local void @jc_ISOException_throwIt(i16 noundef signext) unnamed_addr #8

; Function Attrs: nounwind
declare dso_local noundef signext i16 @jc_APDU_setOutgoing(ptr noundef) unnamed_addr #8

; Function Attrs: nounwind
declare dso_local void @jc_APDU_setOutgoingLength(ptr noundef, i16 noundef signext) unnamed_addr #8

; Function Attrs: nounwind
declare dso_local void @jc_APDU_sendBytesLong(ptr noundef, ptr noundef, i16 noundef signext, i16 noundef signext) unnamed_addr #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i16 @llvm.smax.i16(i16, i16) #9

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i16 @llvm.smin.i16(i16, i16) #9

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i32(ptr writeonly captures(none), i8, i32, i1 immarg) #10

attributes #0 = { nofree norecurse noreturn nosync nounwind memory(none) "target-cpu"="generic" }
attributes #1 = { mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) "target-cpu"="generic" }
attributes #2 = { mustprogress nofree noinline norecurse nosync nounwind willreturn memory(write, argmem: none, inaccessiblemem: none) "target-cpu"="generic" }
attributes #3 = { nofree noinline norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) "target-cpu"="generic" }
attributes #4 = { mustprogress nofree noinline norecurse nosync nounwind willreturn memory(readwrite, argmem: none, inaccessiblemem: none) "target-cpu"="generic" }
attributes #5 = { mustprogress nofree noinline norecurse nosync nounwind willreturn memory(read, argmem: none, inaccessiblemem: none) "target-cpu"="generic" }
attributes #6 = { nofree noinline norecurse nosync nounwind memory(readwrite, argmem: none, inaccessiblemem: none) "target-cpu"="generic" }
attributes #7 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) "target-cpu"="generic" }
attributes #8 = { nounwind "target-cpu"="generic" }
attributes #9 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #10 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #11 = { nounwind }

!llvm.ident = !{!53}
!llvm.dbg.cu = !{!54}
!llvm.module.flags = !{!68, !69}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "DIGIT_FONT", linkageName: "_ZN3lib10DIGIT_FONT17h568307813fef6c2aE", scope: !2, file: !3, line: 112, type: !4, isLocal: true, isDefinition: true, align: 8)
!2 = !DINamespace(name: "lib", scope: null)
!3 = !DIFile(filename: "src/lib.rs", directory: "/home/user/jcc/examples/rusty", checksumkind: CSK_MD5, checksum: "97a2aa2f02ad7713f15c58b923dba752")
!4 = !DICompositeType(tag: DW_TAG_array_type, baseType: !5, size: 400, align: 8, elements: !6)
!5 = !DIBasicType(name: "i8", size: 8, encoding: DW_ATE_signed)
!6 = !{!7}
!7 = !DISubrange(count: 50, lowerBound: 0)
!8 = !DIGlobalVariableExpression(var: !9, expr: !DIExpression())
!9 = distinct !DIGlobalVariable(name: "FRAMEBUFFER", linkageName: "_ZN3lib11FRAMEBUFFER17h74699d2c84f1a332E", scope: !2, file: !3, line: 100, type: !10, isLocal: true, isDefinition: true, align: 8)
!10 = !DICompositeType(tag: DW_TAG_array_type, baseType: !5, size: 640, align: 8, elements: !11)
!11 = !{!12}
!12 = !DISubrange(count: 80, lowerBound: 0)
!13 = !DIGlobalVariableExpression(var: !14, expr: !DIExpression(DW_OP_deref_size, 1, DW_OP_constu, 1, DW_OP_mul, DW_OP_constu, 0, DW_OP_plus, DW_OP_stack_value))
!14 = distinct !DIGlobalVariable(name: "GAME_INITIALIZED", linkageName: "_ZN3lib16GAME_INITIALIZED17hdc6bee963eb1f766E", scope: !2, file: !3, line: 109, type: !5, isLocal: true, isDefinition: true, align: 8)
!15 = !DIGlobalVariableExpression(var: !16, expr: !DIExpression(DW_OP_LLVM_fragment, 0, 16))
!16 = distinct !DIGlobalVariable(name: "BIRD", linkageName: "_ZN3lib4BIRD17h571dc8b4c80d60d7E", scope: !2, file: !3, line: 101, type: !17, isLocal: true, isDefinition: true, align: 16)
!17 = !DICompositeType(tag: DW_TAG_structure_type, name: "Bird", scope: !2, file: !18, size: 32, align: 16, flags: DIFlagPrivate, elements: !19, templateParams: !23, identifier: "4d267c232a4299c9512818aa1ecfdaa8")
!18 = !DIFile(filename: "<unknown>", directory: "")
!19 = !{!20, !22}
!20 = !DIDerivedType(tag: DW_TAG_member, name: "y", scope: !17, file: !18, baseType: !21, size: 16, align: 16, flags: DIFlagPrivate)
!21 = !DIBasicType(name: "i16", size: 16, encoding: DW_ATE_signed)
!22 = !DIDerivedType(tag: DW_TAG_member, name: "velocity", scope: !17, file: !18, baseType: !21, size: 16, align: 16, offset: 16, flags: DIFlagPrivate)
!23 = !{}
!24 = !DIGlobalVariableExpression(var: !16, expr: !DIExpression(DW_OP_LLVM_fragment, 16, 16))
!25 = !DIGlobalVariableExpression(var: !26, expr: !DIExpression(DW_OP_LLVM_fragment, 0, 8))
!26 = distinct !DIGlobalVariable(name: "GAME", linkageName: "_ZN3lib4GAME17hbf8763b2c745ccd8E", scope: !2, file: !3, line: 107, type: !27, isLocal: true, isDefinition: true, align: 16)
!27 = !DICompositeType(tag: DW_TAG_structure_type, name: "GameState", scope: !2, file: !18, size: 48, align: 16, flags: DIFlagPrivate, elements: !28, templateParams: !23, identifier: "21a0107c8c04da0614a4af45594ab4c8")
!28 = !{!29, !30, !31}
!29 = !DIDerivedType(tag: DW_TAG_member, name: "state", scope: !27, file: !18, baseType: !5, size: 8, align: 8, flags: DIFlagPrivate)
!30 = !DIDerivedType(tag: DW_TAG_member, name: "score", scope: !27, file: !18, baseType: !21, size: 16, align: 16, offset: 16, flags: DIFlagPrivate)
!31 = !DIDerivedType(tag: DW_TAG_member, name: "frame_count", scope: !27, file: !18, baseType: !21, size: 16, align: 16, offset: 32, flags: DIFlagPrivate)
!32 = !DIGlobalVariableExpression(var: !26, expr: !DIExpression(DW_OP_LLVM_fragment, 16, 16))
!33 = !DIGlobalVariableExpression(var: !26, expr: !DIExpression(DW_OP_LLVM_fragment, 32, 16))
!34 = !DIGlobalVariableExpression(var: !35, expr: !DIExpression())
!35 = distinct !DIGlobalVariable(name: "PIPES", linkageName: "_ZN3lib5PIPES17h0b113f338cd5ae43E", scope: !2, file: !3, line: 102, type: !36, isLocal: true, isDefinition: true, align: 16)
!36 = !DICompositeType(tag: DW_TAG_array_type, baseType: !37, size: 144, align: 16, elements: !43)
!37 = !DICompositeType(tag: DW_TAG_structure_type, name: "Pipe", scope: !2, file: !18, size: 48, align: 16, flags: DIFlagPrivate, elements: !38, templateParams: !23, identifier: "c66b226787126367a1df6a88f6cca50e")
!38 = !{!39, !40, !41, !42}
!39 = !DIDerivedType(tag: DW_TAG_member, name: "x", scope: !37, file: !18, baseType: !21, size: 16, align: 16, flags: DIFlagPrivate)
!40 = !DIDerivedType(tag: DW_TAG_member, name: "gap_y", scope: !37, file: !18, baseType: !21, size: 16, align: 16, offset: 16, flags: DIFlagPrivate)
!41 = !DIDerivedType(tag: DW_TAG_member, name: "active", scope: !37, file: !18, baseType: !5, size: 8, align: 8, offset: 32, flags: DIFlagPrivate)
!42 = !DIDerivedType(tag: DW_TAG_member, name: "scored", scope: !37, file: !18, baseType: !5, size: 8, align: 8, offset: 40, flags: DIFlagPrivate)
!43 = !{!44}
!44 = !DISubrange(count: 3, lowerBound: 0)
!45 = !DIGlobalVariableExpression(var: !46, expr: !DIExpression())
!46 = distinct !DIGlobalVariable(name: "NUM_D0", linkageName: "_ZN3lib6NUM_D017h603139fb0e00dad5E", scope: !2, file: !3, line: 126, type: !21, isLocal: true, isDefinition: true, align: 16)
!47 = !DIGlobalVariableExpression(var: !48, expr: !DIExpression())
!48 = distinct !DIGlobalVariable(name: "NUM_D1", linkageName: "_ZN3lib6NUM_D117hc6caecc785c50e8dE", scope: !2, file: !3, line: 127, type: !21, isLocal: true, isDefinition: true, align: 16)
!49 = !DIGlobalVariableExpression(var: !50, expr: !DIExpression())
!50 = distinct !DIGlobalVariable(name: "NUM_D2", linkageName: "_ZN3lib6NUM_D217hce061614100c2eebE", scope: !2, file: !3, line: 128, type: !21, isLocal: true, isDefinition: true, align: 16)
!51 = !DIGlobalVariableExpression(var: !52, expr: !DIExpression())
!52 = distinct !DIGlobalVariable(name: "RNG_STATE", linkageName: "_ZN3lib9RNG_STATE17h0f6aa4bd50ad1b09E", scope: !2, file: !3, line: 108, type: !21, isLocal: true, isDefinition: true, align: 16)
!53 = !{!"rustc version 1.91.1 (ed61e7d7e 2025-11-07)"}
!54 = distinct !DICompileUnit(language: DW_LANG_Rust, file: !55, producer: "clang LLVM (rustc version 1.91.1 (ed61e7d7e 2025-11-07))", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, enums: !56, globals: !64, splitDebugInlining: false, nameTableKind: None)
!55 = !DIFile(filename: "src/lib.rs/@/lib.aea4d3df3642ec66-cgu.0", directory: "/home/user/jcc/examples/rusty")
!56 = !{!57}
!57 = !DICompositeType(tag: DW_TAG_enumeration_type, name: "c_void", scope: !58, file: !18, baseType: !60, size: 8, align: 8, flags: DIFlagEnumClass, elements: !61)
!58 = !DINamespace(name: "ffi", scope: !59)
!59 = !DINamespace(name: "core", scope: null)
!60 = !DIBasicType(name: "u8", size: 8, encoding: DW_ATE_unsigned)
!61 = !{!62, !63}
!62 = !DIEnumerator(name: "__variant1", value: 0, isUnsigned: true)
!63 = !DIEnumerator(name: "__variant2", value: 1, isUnsigned: true)
!64 = !{!0, !8, !65, !66, !67, !34, !45, !47, !49, !51}
!65 = !DIGlobalVariableExpression(var: !14, expr: !DIExpression())
!66 = !DIGlobalVariableExpression(var: !16, expr: !DIExpression())
!67 = !DIGlobalVariableExpression(var: !26, expr: !DIExpression())
!68 = !{i32 7, !"Dwarf Version", i32 4}
!69 = !{i32 2, !"Debug Info Version", i32 3}
!70 = distinct !DISubprogram(name: "panic", linkageName: "_RNvCskdKJRKLKjqM_7___rustc17rust_begin_unwind", scope: !2, file: !3, line: 11, type: !71, scopeLine: 11, flags: DIFlagPrototyped | DIFlagNoReturn, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !241)
!71 = !DISubroutineType(types: !72)
!72 = !{null, !73}
!73 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "&core::panic::panic_info::PanicInfo", baseType: !74, size: 32, align: 32, dwarfAddressSpace: 0)
!74 = !DICompositeType(tag: DW_TAG_structure_type, name: "PanicInfo", scope: !75, file: !18, size: 96, align: 32, flags: DIFlagPublic, elements: !77, templateParams: !23, identifier: "a7ff27c311cec15ceec6eeaaf30073e")
!75 = !DINamespace(name: "panic_info", scope: !76)
!76 = !DINamespace(name: "panic", scope: !59)
!77 = !{!78, !217, !238, !240}
!78 = !DIDerivedType(tag: DW_TAG_member, name: "message", scope: !74, file: !18, baseType: !79, size: 32, align: 32, flags: DIFlagPrivate)
!79 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "&core::fmt::Arguments", baseType: !80, size: 32, align: 32, dwarfAddressSpace: 0)
!80 = !DICompositeType(tag: DW_TAG_structure_type, name: "Arguments", scope: !81, file: !18, size: 192, align: 32, flags: DIFlagPublic, elements: !82, templateParams: !23, identifier: "b43f68f3d6a0fbeec53e7b4ab54eab3e")
!81 = !DINamespace(name: "fmt", scope: !59)
!82 = !{!83, !95, !139}
!83 = !DIDerivedType(tag: DW_TAG_member, name: "pieces", scope: !80, file: !18, baseType: !84, size: 64, align: 32, flags: DIFlagPrivate)
!84 = !DICompositeType(tag: DW_TAG_structure_type, name: "&[&str]", file: !18, size: 64, align: 32, elements: !85, templateParams: !23, identifier: "4e66b00a376d6af5b8765440fb2839f")
!85 = !{!86, !94}
!86 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !84, file: !18, baseType: !87, size: 32, align: 32)
!87 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !88, size: 32, align: 32, dwarfAddressSpace: 0)
!88 = !DICompositeType(tag: DW_TAG_structure_type, name: "&str", file: !18, size: 64, align: 32, elements: !89, templateParams: !23, identifier: "9277eecd40495f85161460476aacc992")
!89 = !{!90, !92}
!90 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !88, file: !18, baseType: !91, size: 32, align: 32)
!91 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !60, size: 32, align: 32, dwarfAddressSpace: 0)
!92 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !88, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!93 = !DIBasicType(name: "usize", size: 32, encoding: DW_ATE_unsigned)
!94 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !84, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!95 = !DIDerivedType(tag: DW_TAG_member, name: "fmt", scope: !80, file: !18, baseType: !96, size: 64, align: 32, offset: 128, flags: DIFlagPrivate)
!96 = !DICompositeType(tag: DW_TAG_structure_type, name: "Option<&[core::fmt::rt::Placeholder]>", scope: !97, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !98, templateParams: !23, identifier: "91cea1cb081a6bd35ffc0ad84c7da3fa")
!97 = !DINamespace(name: "option", scope: !59)
!98 = !{!99}
!99 = !DICompositeType(tag: DW_TAG_variant_part, scope: !96, file: !18, size: 64, align: 32, elements: !100, templateParams: !23, identifier: "25cb8c087eed993241ce3e8a29dcad0c", discriminator: !138)
!100 = !{!101, !134}
!101 = !DIDerivedType(tag: DW_TAG_member, name: "None", scope: !99, file: !18, baseType: !102, size: 64, align: 32, extraData: i32 0)
!102 = !DICompositeType(tag: DW_TAG_structure_type, name: "None", scope: !96, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !23, templateParams: !103, identifier: "59aedc9e429d88f25401f6fa44bedea0")
!103 = !{!104}
!104 = !DITemplateTypeParameter(name: "T", type: !105)
!105 = !DICompositeType(tag: DW_TAG_structure_type, name: "&[core::fmt::rt::Placeholder]", file: !18, size: 64, align: 32, elements: !106, templateParams: !23, identifier: "b793286bbd338247c0a1d931db267129")
!106 = !{!107, !133}
!107 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !105, file: !18, baseType: !108, size: 32, align: 32)
!108 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !109, size: 32, align: 32, dwarfAddressSpace: 0)
!109 = !DICompositeType(tag: DW_TAG_structure_type, name: "Placeholder", scope: !110, file: !18, size: 192, align: 32, flags: DIFlagPublic, elements: !111, templateParams: !23, identifier: "a4ab11d2ee165f8b88862ee3b9974263")
!110 = !DINamespace(name: "rt", scope: !81)
!111 = !{!112, !113, !115, !132}
!112 = !DIDerivedType(tag: DW_TAG_member, name: "position", scope: !109, file: !18, baseType: !93, size: 32, align: 32, offset: 128, flags: DIFlagPublic)
!113 = !DIDerivedType(tag: DW_TAG_member, name: "flags", scope: !109, file: !18, baseType: !114, size: 32, align: 32, offset: 160, flags: DIFlagPublic)
!114 = !DIBasicType(name: "u32", size: 32, encoding: DW_ATE_unsigned)
!115 = !DIDerivedType(tag: DW_TAG_member, name: "precision", scope: !109, file: !18, baseType: !116, size: 64, align: 32, flags: DIFlagPublic)
!116 = !DICompositeType(tag: DW_TAG_structure_type, name: "Count", scope: !110, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !117, templateParams: !23, identifier: "1553706adb59700b130002cd212bb18a")
!117 = !{!118}
!118 = !DICompositeType(tag: DW_TAG_variant_part, scope: !116, file: !18, size: 64, align: 32, elements: !119, templateParams: !23, identifier: "e271c4a5eb96dfb1f33b87c04530c59b", discriminator: !131)
!119 = !{!120, !125, !129}
!120 = !DIDerivedType(tag: DW_TAG_member, name: "Is", scope: !118, file: !18, baseType: !121, size: 64, align: 32, extraData: i16 0)
!121 = !DICompositeType(tag: DW_TAG_structure_type, name: "Is", scope: !116, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !122, templateParams: !23, identifier: "867c86a849d0187f79ccd18abd9f618b")
!122 = !{!123}
!123 = !DIDerivedType(tag: DW_TAG_member, name: "__0", scope: !121, file: !18, baseType: !124, size: 16, align: 16, offset: 16, flags: DIFlagPublic)
!124 = !DIBasicType(name: "u16", size: 16, encoding: DW_ATE_unsigned)
!125 = !DIDerivedType(tag: DW_TAG_member, name: "Param", scope: !118, file: !18, baseType: !126, size: 64, align: 32, extraData: i16 1)
!126 = !DICompositeType(tag: DW_TAG_structure_type, name: "Param", scope: !116, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !127, templateParams: !23, identifier: "d95fdc54b6c675a077064cc8ea25da51")
!127 = !{!128}
!128 = !DIDerivedType(tag: DW_TAG_member, name: "__0", scope: !126, file: !18, baseType: !93, size: 32, align: 32, offset: 32, flags: DIFlagPublic)
!129 = !DIDerivedType(tag: DW_TAG_member, name: "Implied", scope: !118, file: !18, baseType: !130, size: 64, align: 32, extraData: i16 2)
!130 = !DICompositeType(tag: DW_TAG_structure_type, name: "Implied", scope: !116, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !23, identifier: "afb7b4ce4a245ceff3fc0e027c3ef154")
!131 = !DIDerivedType(tag: DW_TAG_member, scope: !116, file: !18, baseType: !124, size: 16, align: 16, flags: DIFlagArtificial)
!132 = !DIDerivedType(tag: DW_TAG_member, name: "width", scope: !109, file: !18, baseType: !116, size: 64, align: 32, offset: 64, flags: DIFlagPublic)
!133 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !105, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!134 = !DIDerivedType(tag: DW_TAG_member, name: "Some", scope: !99, file: !18, baseType: !135, size: 64, align: 32)
!135 = !DICompositeType(tag: DW_TAG_structure_type, name: "Some", scope: !96, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !136, templateParams: !103, identifier: "59ba6634ed1e651771f6e92d6a1e53f3")
!136 = !{!137}
!137 = !DIDerivedType(tag: DW_TAG_member, name: "__0", scope: !135, file: !18, baseType: !105, size: 64, align: 32, flags: DIFlagPublic)
!138 = !DIDerivedType(tag: DW_TAG_member, scope: !96, file: !18, baseType: !114, size: 32, align: 32, flags: DIFlagArtificial)
!139 = !DIDerivedType(tag: DW_TAG_member, name: "args", scope: !80, file: !18, baseType: !140, size: 64, align: 32, offset: 64, flags: DIFlagPrivate)
!140 = !DICompositeType(tag: DW_TAG_structure_type, name: "&[core::fmt::rt::Argument]", file: !18, size: 64, align: 32, elements: !141, templateParams: !23, identifier: "3197e7226de03c76ed82787246f4cdf5")
!141 = !{!142, !216}
!142 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !140, file: !18, baseType: !143, size: 32, align: 32)
!143 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !144, size: 32, align: 32, dwarfAddressSpace: 0)
!144 = !DICompositeType(tag: DW_TAG_structure_type, name: "Argument", scope: !110, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !145, templateParams: !23, identifier: "69447bf69f4c3810ed91632cf66cf04f")
!145 = !{!146}
!146 = !DIDerivedType(tag: DW_TAG_member, name: "ty", scope: !144, file: !18, baseType: !147, size: 64, align: 32, flags: DIFlagPrivate)
!147 = !DICompositeType(tag: DW_TAG_structure_type, name: "ArgumentType", scope: !110, file: !18, size: 64, align: 32, flags: DIFlagPrivate, elements: !148, templateParams: !23, identifier: "1ac5fba2f994c544d6684607133e9be5")
!148 = !{!149}
!149 = !DICompositeType(tag: DW_TAG_variant_part, scope: !147, file: !18, size: 64, align: 32, elements: !150, templateParams: !23, identifier: "f48a230561e2ccc9413d2b0333582cad", discriminator: !215)
!150 = !{!151, !211}
!151 = !DIDerivedType(tag: DW_TAG_member, name: "Placeholder", scope: !149, file: !18, baseType: !152, size: 64, align: 32)
!152 = !DICompositeType(tag: DW_TAG_structure_type, name: "Placeholder", scope: !147, file: !18, size: 64, align: 32, flags: DIFlagPrivate, elements: !153, templateParams: !23, identifier: "a12230d4ea805859231be27929e2ea16")
!153 = !{!154, !164, !205}
!154 = !DIDerivedType(tag: DW_TAG_member, name: "value", scope: !152, file: !18, baseType: !155, size: 32, align: 32, flags: DIFlagPrivate)
!155 = !DICompositeType(tag: DW_TAG_structure_type, name: "NonNull<()>", scope: !156, file: !18, size: 32, align: 32, flags: DIFlagPublic, elements: !158, templateParams: !162, identifier: "d5d6b83a02cc9ee44bee6a531d8fd030")
!156 = !DINamespace(name: "non_null", scope: !157)
!157 = !DINamespace(name: "ptr", scope: !59)
!158 = !{!159}
!159 = !DIDerivedType(tag: DW_TAG_member, name: "pointer", scope: !155, file: !18, baseType: !160, size: 32, align: 32, flags: DIFlagPrivate)
!160 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "*const ()", baseType: !161, size: 32, align: 32, dwarfAddressSpace: 0)
!161 = !DIBasicType(name: "()", encoding: DW_ATE_unsigned)
!162 = !{!163}
!163 = !DITemplateTypeParameter(name: "T", type: !161)
!164 = !DIDerivedType(tag: DW_TAG_member, name: "formatter", scope: !152, file: !18, baseType: !165, size: 32, align: 32, offset: 32, flags: DIFlagPrivate)
!165 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "unsafe fn(core::ptr::non_null::NonNull<()>, &mut core::fmt::Formatter) -> core::result::Result<(), core::fmt::Error>", baseType: !166, size: 32, align: 32, dwarfAddressSpace: 0)
!166 = !DISubroutineType(types: !167)
!167 = !{!168, !155, !185}
!168 = !DICompositeType(tag: DW_TAG_structure_type, name: "Result<(), core::fmt::Error>", scope: !169, file: !18, size: 8, align: 8, flags: DIFlagPublic, elements: !170, templateParams: !23, identifier: "7519c61b67b9b2ba245c8d84b3ec0a5")
!169 = !DINamespace(name: "result", scope: !59)
!170 = !{!171}
!171 = !DICompositeType(tag: DW_TAG_variant_part, scope: !168, file: !18, size: 8, align: 8, elements: !172, templateParams: !23, identifier: "8e984bcaaceae27fc0c7863d29fa5ba9", discriminator: !184)
!172 = !{!173, !180}
!173 = !DIDerivedType(tag: DW_TAG_member, name: "Ok", scope: !171, file: !18, baseType: !174, size: 8, align: 8, extraData: i8 0)
!174 = !DICompositeType(tag: DW_TAG_structure_type, name: "Ok", scope: !168, file: !18, size: 8, align: 8, flags: DIFlagPublic, elements: !175, templateParams: !177, identifier: "cf7f1922b1a3ef4c1fc65f8e95e927e2")
!175 = !{!176}
!176 = !DIDerivedType(tag: DW_TAG_member, name: "__0", scope: !174, file: !18, baseType: !161, align: 8, offset: 8, flags: DIFlagPublic)
!177 = !{!163, !178}
!178 = !DITemplateTypeParameter(name: "E", type: !179)
!179 = !DICompositeType(tag: DW_TAG_structure_type, name: "Error", scope: !81, file: !18, align: 8, flags: DIFlagPublic, elements: !23, identifier: "e1b5868c30e0732b4cd40bb11404154a")
!180 = !DIDerivedType(tag: DW_TAG_member, name: "Err", scope: !171, file: !18, baseType: !181, size: 8, align: 8, extraData: i8 1)
!181 = !DICompositeType(tag: DW_TAG_structure_type, name: "Err", scope: !168, file: !18, size: 8, align: 8, flags: DIFlagPublic, elements: !182, templateParams: !177, identifier: "be64f4dd65841bc64d2b624e00508c8")
!182 = !{!183}
!183 = !DIDerivedType(tag: DW_TAG_member, name: "__0", scope: !181, file: !18, baseType: !179, align: 8, offset: 8, flags: DIFlagPublic)
!184 = !DIDerivedType(tag: DW_TAG_member, scope: !168, file: !18, baseType: !60, size: 8, align: 8, flags: DIFlagArtificial)
!185 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "&mut core::fmt::Formatter", baseType: !186, size: 32, align: 32, dwarfAddressSpace: 0)
!186 = !DICompositeType(tag: DW_TAG_structure_type, name: "Formatter", scope: !81, file: !18, size: 128, align: 32, flags: DIFlagPublic, elements: !187, templateParams: !23, identifier: "678d10f925fbeb24dc345403b140a3fb")
!187 = !{!188, !194}
!188 = !DIDerivedType(tag: DW_TAG_member, name: "options", scope: !186, file: !18, baseType: !189, size: 64, align: 32, offset: 64, flags: DIFlagPrivate)
!189 = !DICompositeType(tag: DW_TAG_structure_type, name: "FormattingOptions", scope: !81, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !190, templateParams: !23, identifier: "b8357171a05d10b375efe9576f18142d")
!190 = !{!191, !192, !193}
!191 = !DIDerivedType(tag: DW_TAG_member, name: "flags", scope: !189, file: !18, baseType: !114, size: 32, align: 32, flags: DIFlagPrivate)
!192 = !DIDerivedType(tag: DW_TAG_member, name: "width", scope: !189, file: !18, baseType: !124, size: 16, align: 16, offset: 32, flags: DIFlagPrivate)
!193 = !DIDerivedType(tag: DW_TAG_member, name: "precision", scope: !189, file: !18, baseType: !124, size: 16, align: 16, offset: 48, flags: DIFlagPrivate)
!194 = !DIDerivedType(tag: DW_TAG_member, name: "buf", scope: !186, file: !18, baseType: !195, size: 64, align: 32, flags: DIFlagPrivate)
!195 = !DICompositeType(tag: DW_TAG_structure_type, name: "&mut dyn core::fmt::Write", file: !18, size: 64, align: 32, elements: !196, templateParams: !23, identifier: "e676b90f86a1b75be2e2d0f7d5ffd4e")
!196 = !{!197, !200}
!197 = !DIDerivedType(tag: DW_TAG_member, name: "pointer", scope: !195, file: !18, baseType: !198, size: 32, align: 32)
!198 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !199, size: 32, align: 32, dwarfAddressSpace: 0)
!199 = !DICompositeType(tag: DW_TAG_structure_type, name: "dyn core::fmt::Write", file: !18, align: 8, elements: !23, identifier: "99c8eb6ca70d5f42d6b20755d8b42af6")
!200 = !DIDerivedType(tag: DW_TAG_member, name: "vtable", scope: !195, file: !18, baseType: !201, size: 32, align: 32, offset: 32)
!201 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "&[usize; 6]", baseType: !202, size: 32, align: 32, dwarfAddressSpace: 0)
!202 = !DICompositeType(tag: DW_TAG_array_type, baseType: !93, size: 192, align: 32, elements: !203)
!203 = !{!204}
!204 = !DISubrange(count: 6, lowerBound: 0)
!205 = !DIDerivedType(tag: DW_TAG_member, name: "_lifetime", scope: !152, file: !18, baseType: !206, align: 8, offset: 64, flags: DIFlagPrivate)
!206 = !DICompositeType(tag: DW_TAG_structure_type, name: "PhantomData<&()>", scope: !207, file: !18, align: 8, flags: DIFlagPublic, elements: !23, templateParams: !208, identifier: "7bc474ee408d5350975fca11ed5e512b")
!207 = !DINamespace(name: "marker", scope: !59)
!208 = !{!209}
!209 = !DITemplateTypeParameter(name: "T", type: !210)
!210 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "&()", baseType: !161, size: 32, align: 32, dwarfAddressSpace: 0)
!211 = !DIDerivedType(tag: DW_TAG_member, name: "Count", scope: !149, file: !18, baseType: !212, size: 64, align: 32, extraData: i32 0)
!212 = !DICompositeType(tag: DW_TAG_structure_type, name: "Count", scope: !147, file: !18, size: 64, align: 32, flags: DIFlagPrivate, elements: !213, templateParams: !23, identifier: "7d86f628fe399e923a7ce3d3ebcccc54")
!213 = !{!214}
!214 = !DIDerivedType(tag: DW_TAG_member, name: "__0", scope: !212, file: !18, baseType: !124, size: 16, align: 16, offset: 32, flags: DIFlagPrivate)
!215 = !DIDerivedType(tag: DW_TAG_member, scope: !147, file: !18, baseType: !114, size: 32, align: 32, flags: DIFlagArtificial)
!216 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !140, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!217 = !DIDerivedType(tag: DW_TAG_member, name: "location", scope: !74, file: !18, baseType: !218, size: 32, align: 32, offset: 32, flags: DIFlagPrivate)
!218 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "&core::panic::location::Location", baseType: !219, size: 32, align: 32, dwarfAddressSpace: 0)
!219 = !DICompositeType(tag: DW_TAG_structure_type, name: "Location", scope: !220, file: !18, size: 128, align: 32, flags: DIFlagPublic, elements: !221, templateParams: !23, identifier: "99be5f1473c641f16871c31c71f62ecf")
!220 = !DINamespace(name: "location", scope: !76)
!221 = !{!222, !232, !233, !234}
!222 = !DIDerivedType(tag: DW_TAG_member, name: "filename", scope: !219, file: !18, baseType: !223, size: 64, align: 32, flags: DIFlagPrivate)
!223 = !DICompositeType(tag: DW_TAG_structure_type, name: "NonNull<str>", scope: !156, file: !18, size: 64, align: 32, flags: DIFlagPublic, elements: !224, templateParams: !230, identifier: "48e5e0aee0f2f8c6996d674e9386f432")
!224 = !{!225}
!225 = !DIDerivedType(tag: DW_TAG_member, name: "pointer", scope: !223, file: !18, baseType: !226, size: 64, align: 32, flags: DIFlagPrivate)
!226 = !DICompositeType(tag: DW_TAG_structure_type, name: "*const str", file: !18, size: 64, align: 32, elements: !227, templateParams: !23, identifier: "238a44609877474087c05adf26cd41fa")
!227 = !{!228, !229}
!228 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !226, file: !18, baseType: !91, size: 32, align: 32)
!229 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !226, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!230 = !{!231}
!231 = !DITemplateTypeParameter(name: "T", type: !60)
!232 = !DIDerivedType(tag: DW_TAG_member, name: "line", scope: !219, file: !18, baseType: !114, size: 32, align: 32, offset: 64, flags: DIFlagPrivate)
!233 = !DIDerivedType(tag: DW_TAG_member, name: "col", scope: !219, file: !18, baseType: !114, size: 32, align: 32, offset: 96, flags: DIFlagPrivate)
!234 = !DIDerivedType(tag: DW_TAG_member, name: "_filename", scope: !219, file: !18, baseType: !235, align: 8, offset: 128, flags: DIFlagPrivate)
!235 = !DICompositeType(tag: DW_TAG_structure_type, name: "PhantomData<&str>", scope: !207, file: !18, align: 8, flags: DIFlagPublic, elements: !23, templateParams: !236, identifier: "41bedb8054ca60e029ceabcec56f9978")
!236 = !{!237}
!237 = !DITemplateTypeParameter(name: "T", type: !88)
!238 = !DIDerivedType(tag: DW_TAG_member, name: "can_unwind", scope: !74, file: !18, baseType: !239, size: 8, align: 8, offset: 64, flags: DIFlagPrivate)
!239 = !DIBasicType(name: "bool", size: 8, encoding: DW_ATE_boolean)
!240 = !DIDerivedType(tag: DW_TAG_member, name: "force_no_backtrace", scope: !74, file: !18, baseType: !239, size: 8, align: 8, offset: 72, flags: DIFlagPrivate)
!241 = !{!242}
!242 = !DILocalVariable(name: "_info", arg: 1, scope: !70, file: !3, line: 11, type: !73)
!243 = !DILocation(line: 0, scope: !70)
!244 = !DILocation(line: 12, column: 5, scope: !70)
!245 = distinct !DISubprogram(name: "drawNumber", linkageName: "_ZN3lib10drawNumber17h9e0b83d1ba77bfc9E", scope: !2, file: !3, line: 481, type: !246, scopeLine: 481, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !248)
!246 = !DISubroutineType(cc: DW_CC_nocall, types: !247)
!247 = !{null, !21, !21, !21, !5}
!248 = !{!249, !250, !251, !252, !253, !255, !257, !259, !261}
!249 = !DILocalVariable(name: "center_x", arg: 1, scope: !245, file: !3, line: 481, type: !21)
!250 = !DILocalVariable(name: "y", arg: 2, scope: !245, file: !3, line: 481, type: !21)
!251 = !DILocalVariable(name: "number", arg: 3, scope: !245, file: !3, line: 481, type: !21)
!252 = !DILocalVariable(name: "color", arg: 4, scope: !245, file: !3, line: 481, type: !5)
!253 = !DILocalVariable(name: "number", scope: !254, file: !3, line: 482, type: !21, align: 16)
!254 = distinct !DILexicalBlock(scope: !245, file: !3, line: 482, column: 5)
!255 = !DILocalVariable(name: "num_digits", scope: !256, file: !3, line: 492, type: !21, align: 16)
!256 = distinct !DILexicalBlock(scope: !254, file: !3, line: 492, column: 5)
!257 = !DILocalVariable(name: "temp", scope: !258, file: !3, line: 493, type: !21, align: 16)
!258 = distinct !DILexicalBlock(scope: !256, file: !3, line: 493, column: 5)
!259 = !DILocalVariable(name: "width", scope: !260, file: !3, line: 517, type: !21, align: 16)
!260 = distinct !DILexicalBlock(scope: !258, file: !3, line: 517, column: 9)
!261 = !DILocalVariable(name: "start_x", scope: !262, file: !3, line: 518, type: !21, align: 16)
!262 = distinct !DILexicalBlock(scope: !260, file: !3, line: 518, column: 9)
!263 = !DILocation(line: 0, scope: !245)
!264 = !DILocation(line: 0, scope: !254)
!265 = !DILocation(line: 484, column: 8, scope: !254)
!266 = !DILocation(line: 483, column: 8, scope: !254)
!267 = !DILocation(line: 487, column: 9, scope: !254)
!268 = !DILocation(line: 488, column: 9, scope: !254)
!269 = !DILocation(line: 489, column: 9, scope: !254)
!270 = !DILocation(line: 0, scope: !258)
!271 = !DILocation(line: 496, column: 12, scope: !258)
!272 = !DILocation(line: 497, column: 13, scope: !258)
!273 = !DILocation(line: 0, scope: !256)
!274 = !DILocation(line: 496, column: 9, scope: !258)
!275 = !DILocation(line: 493, column: 20, scope: !256)
!276 = !DILocation(line: 501, column: 16, scope: !258)
!277 = !DILocation(line: 517, column: 21, scope: !258)
!278 = !DILocation(line: 0, scope: !260)
!279 = !DILocation(line: 518, column: 38, scope: !260)
!280 = !DILocation(line: 518, column: 27, scope: !260)
!281 = !DILocation(line: 0, scope: !262)
!282 = !DILocation(line: 520, column: 12, scope: !262)
!283 = !DILocation(line: 503, column: 17, scope: !258)
!284 = !DILocation(line: 502, column: 17, scope: !258)
!285 = !DILocation(line: 501, column: 13, scope: !258)
!286 = !DILocation(line: 506, column: 16, scope: !258)
!287 = !DILocation(line: 508, column: 17, scope: !258)
!288 = !DILocation(line: 507, column: 17, scope: !258)
!289 = !DILocation(line: 506, column: 13, scope: !258)
!290 = !DILocation(line: 511, column: 16, scope: !258)
!291 = !DILocation(line: 512, column: 17, scope: !258)
!292 = !DILocation(line: 511, column: 13, scope: !258)
!293 = !DILocation(line: 521, column: 35, scope: !262)
!294 = !DILocation(line: 521, column: 13, scope: !262)
!295 = !DILocation(line: 522, column: 13, scope: !262)
!296 = !DILocation(line: 520, column: 9, scope: !262)
!297 = !DILocation(line: 524, column: 12, scope: !262)
!298 = !DILocation(line: 525, column: 35, scope: !262)
!299 = !DILocation(line: 525, column: 13, scope: !262)
!300 = !DILocation(line: 526, column: 13, scope: !262)
!301 = !DILocation(line: 524, column: 9, scope: !262)
!302 = !DILocation(line: 528, column: 31, scope: !262)
!303 = !DILocation(line: 528, column: 9, scope: !262)
!304 = !DILocation(line: 530, column: 2, scope: !245)
!305 = distinct !DISubprogram(name: "reset_game", linkageName: "_ZN3lib10reset_game17hd18b9fe9bf0032f6E", scope: !2, file: !3, line: 256, type: !306, scopeLine: 256, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !308)
!306 = !DISubroutineType(types: !307)
!307 = !{null}
!308 = !{!309}
!309 = !DILocalVariable(name: "i", scope: !310, file: !3, line: 261, type: !93, align: 32)
!310 = distinct !DILexicalBlock(scope: !305, file: !3, line: 261, column: 9)
!311 = !DILocation(line: 258, column: 9, scope: !305)
!312 = !DILocation(line: 259, column: 9, scope: !305)
!313 = !DILocation(line: 0, scope: !310)
!314 = !DILocation(line: 263, column: 13, scope: !310)
!315 = !DILocation(line: 264, column: 13, scope: !310)
!316 = !DILocation(line: 268, column: 9, scope: !310)
!317 = !DILocation(line: 269, column: 9, scope: !310)
!318 = !DILocation(line: 270, column: 9, scope: !310)
!319 = !DILocation(line: 271, column: 9, scope: !310)
!320 = !DILocation(line: 273, column: 2, scope: !305)
!321 = distinct !DISubprogram(name: "spawn_pipe", linkageName: "_ZN3lib10spawn_pipe17h6d0176eb64ed2057E", scope: !2, file: !3, line: 291, type: !322, scopeLine: 291, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !324)
!322 = !DISubroutineType(types: !323)
!323 = !{null, !21}
!324 = !{!325, !326}
!325 = !DILocalVariable(name: "x", arg: 1, scope: !321, file: !3, line: 291, type: !21)
!326 = !DILocalVariable(name: "i", scope: !327, file: !3, line: 293, type: !93, align: 32)
!327 = distinct !DILexicalBlock(scope: !321, file: !3, line: 293, column: 9)
!328 = !DILocation(line: 0, scope: !321)
!329 = !DILocation(line: 0, scope: !327)
!330 = !DILocation(line: 295, column: 16, scope: !327)
!331 = !DILocation(line: 305, column: 2, scope: !321)
!332 = !DILocation(line: 296, column: 17, scope: !327)
!333 = !DILocation(line: 297, column: 34, scope: !327)
!334 = !DILocation(line: 297, column: 17, scope: !327)
!335 = !DILocation(line: 298, column: 17, scope: !327)
!336 = !DILocation(line: 299, column: 17, scope: !327)
!337 = distinct !DISubprogram(name: "render_game", linkageName: "_ZN3lib11render_game17h39ae85af2824aafbE", scope: !2, file: !3, line: 606, type: !306, scopeLine: 606, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23)
!338 = !DILocation(line: 608, column: 12, scope: !337)
!339 = !DILocation(line: 609, column: 13, scope: !337)
!340 = !DILocation(line: 0, scope: !337)
!341 = !DILocation(line: 614, column: 13, scope: !337)
!342 = !DILocation(line: 615, column: 13, scope: !337)
!343 = !DILocation(line: 616, column: 13, scope: !337)
!344 = !DILocation(line: 621, column: 13, scope: !337)
!345 = !DILocation(line: 622, column: 13, scope: !337)
!346 = !DILocation(line: 623, column: 13, scope: !337)
!347 = !DILocation(line: 626, column: 2, scope: !337)
!348 = distinct !DISubprogram(name: "update_bird", linkageName: "_ZN3lib11update_bird17h3beb04e75e34aa8aE", scope: !2, file: !3, line: 340, type: !349, scopeLine: 340, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !351)
!349 = !DISubroutineType(types: !350)
!350 = !{null, !5}
!351 = !{!352, !353}
!352 = !DILocalVariable(name: "flap", arg: 1, scope: !348, file: !3, line: 340, type: !5)
!353 = !DILocalVariable(name: "max_y", scope: !354, file: !3, line: 357, type: !21, align: 16)
!354 = distinct !DILexicalBlock(scope: !348, file: !3, line: 357, column: 9)
!355 = !DILocation(line: 0, scope: !348)
!356 = !DILocation(line: 0, scope: !354)
!357 = !DILocation(line: 342, column: 12, scope: !348)
!358 = !DILocation(line: 351, column: 9, scope: !348)
!359 = !DILocation(line: 353, column: 12, scope: !348)
!360 = !DILocation(line: 354, column: 13, scope: !348)
!361 = !DILocation(line: 355, column: 13, scope: !348)
!362 = !DILocation(line: 353, column: 9, scope: !348)
!363 = !DILocation(line: 358, column: 12, scope: !354)
!364 = !DILocation(line: 359, column: 13, scope: !354)
!365 = !DILocation(line: 358, column: 9, scope: !354)
!366 = !DILocation(line: 362, column: 2, scope: !348)
!367 = distinct !DISubprogram(name: "drawGameOver", linkageName: "_ZN3lib12drawGameOver17h668eec5f6df376c3E", scope: !2, file: !3, line: 592, type: !306, scopeLine: 592, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !368)
!368 = !{!369, !371}
!369 = !DILocalVariable(name: "cx", scope: !370, file: !3, line: 593, type: !21, align: 16)
!370 = distinct !DILexicalBlock(scope: !367, file: !3, line: 593, column: 5)
!371 = !DILocalVariable(name: "cy", scope: !372, file: !3, line: 594, type: !21, align: 16)
!372 = distinct !DILexicalBlock(scope: !370, file: !3, line: 594, column: 5)
!373 = !DILocation(line: 0, scope: !370)
!374 = !DILocation(line: 0, scope: !372)
!375 = !DILocation(line: 596, column: 5, scope: !372)
!376 = !DILocation(line: 597, column: 28, scope: !372)
!377 = !DILocation(line: 597, column: 5, scope: !372)
!378 = !DILocation(line: 600, column: 5, scope: !372)
!379 = !DILocation(line: 601, column: 5, scope: !372)
!380 = !DILocation(line: 602, column: 5, scope: !372)
!381 = !DILocation(line: 603, column: 2, scope: !367)
!382 = distinct !DISubprogram(name: "random_gap_y", linkageName: "_ZN3lib12random_gap_y17h6eff876945902f3aE", scope: !2, file: !3, line: 244, type: !383, scopeLine: 244, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !385)
!383 = !DISubroutineType(types: !384)
!384 = !{!21}
!385 = !{!386, !388, !390}
!386 = !DILocalVariable(name: "min_y", scope: !387, file: !3, line: 245, type: !21, align: 16)
!387 = distinct !DILexicalBlock(scope: !382, file: !3, line: 245, column: 5)
!388 = !DILocalVariable(name: "max_y", scope: !389, file: !3, line: 246, type: !21, align: 16)
!389 = distinct !DILexicalBlock(scope: !387, file: !3, line: 246, column: 5)
!390 = !DILocalVariable(name: "range", scope: !391, file: !3, line: 247, type: !21, align: 16)
!391 = distinct !DILexicalBlock(scope: !389, file: !3, line: 247, column: 5)
!392 = !DILocation(line: 0, scope: !387)
!393 = !DILocation(line: 0, scope: !389)
!394 = !DILocation(line: 0, scope: !391)
!395 = !DILocation(line: 248, column: 14, scope: !391)
!396 = !DILocation(line: 248, column: 13, scope: !391)
!397 = !DILocation(line: 248, column: 5, scope: !391)
!398 = !DILocation(line: 249, column: 2, scope: !382)
!399 = distinct !DISubprogram(name: "random_short", linkageName: "_ZN3lib12random_short17h8c52220c7d87c14aE", scope: !2, file: !3, line: 236, type: !383, scopeLine: 236, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23)
!400 = !DILocation(line: 238, column: 35, scope: !399)
!401 = !DILocation(line: 238, column: 23, scope: !399)
!402 = !DILocation(line: 238, column: 22, scope: !399)
!403 = !DILocation(line: 238, column: 21, scope: !399)
!404 = !DILocation(line: 238, column: 9, scope: !399)
!405 = !DILocation(line: 241, column: 2, scope: !399)
!406 = distinct !DISubprogram(name: "update_pipes", linkageName: "_ZN3lib12update_pipes17h766c122619250a74E", scope: !2, file: !3, line: 313, type: !306, scopeLine: 313, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !407)
!407 = !{!408, !410}
!408 = !DILocalVariable(name: "i", scope: !409, file: !3, line: 315, type: !93, align: 32)
!409 = distinct !DILexicalBlock(scope: !406, file: !3, line: 315, column: 9)
!410 = !DILocalVariable(name: "rightmost_x", scope: !411, file: !3, line: 332, type: !21, align: 16)
!411 = distinct !DILexicalBlock(scope: !409, file: !3, line: 332, column: 9)
!412 = !DILocation(line: 0, scope: !409)
!413 = !DILocation(line: 317, column: 16, scope: !409)
!414 = !DILocation(line: 337, column: 2, scope: !406)
!415 = !DILocation(line: 334, column: 13, scope: !411)
!416 = !DILocation(line: 318, column: 17, scope: !409)
!417 = !DILocation(line: 320, column: 20, scope: !409)
!418 = !DILocation(line: 321, column: 21, scope: !409)
!419 = !DILocation(line: 322, column: 21, scope: !409)
!420 = !DILocation(line: 320, column: 17, scope: !409)
!421 = !DILocation(line: 325, column: 20, scope: !409)
!422 = !DILocation(line: 326, column: 21, scope: !409)
!423 = !DILocation(line: 325, column: 17, scope: !409)
!424 = !DILocation(line: 332, column: 27, scope: !409)
!425 = !DILocation(line: 0, scope: !411)
!426 = !DILocation(line: 333, column: 12, scope: !411)
!427 = distinct !DISubprogram(name: "check_collision", linkageName: "_ZN3lib15check_collision17h4f705c960de6c75bE", scope: !2, file: !3, line: 365, type: !428, scopeLine: 365, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !430)
!428 = !DISubroutineType(types: !429)
!429 = !{!5}
!430 = !{!431, !433, !435, !437, !439, !441, !443, !445, !447, !449}
!431 = !DILocalVariable(name: "bird_screen_y", scope: !432, file: !3, line: 367, type: !21, align: 16)
!432 = distinct !DILexicalBlock(scope: !427, file: !3, line: 367, column: 9)
!433 = !DILocalVariable(name: "bird_top", scope: !434, file: !3, line: 368, type: !21, align: 16)
!434 = distinct !DILexicalBlock(scope: !432, file: !3, line: 368, column: 9)
!435 = !DILocalVariable(name: "bird_bottom", scope: !436, file: !3, line: 369, type: !21, align: 16)
!436 = distinct !DILexicalBlock(scope: !434, file: !3, line: 369, column: 9)
!437 = !DILocalVariable(name: "bird_left", scope: !438, file: !3, line: 370, type: !21, align: 16)
!438 = distinct !DILexicalBlock(scope: !436, file: !3, line: 370, column: 9)
!439 = !DILocalVariable(name: "bird_right", scope: !440, file: !3, line: 371, type: !21, align: 16)
!440 = distinct !DILexicalBlock(scope: !438, file: !3, line: 371, column: 9)
!441 = !DILocalVariable(name: "i", scope: !442, file: !3, line: 380, type: !93, align: 32)
!442 = distinct !DILexicalBlock(scope: !440, file: !3, line: 380, column: 9)
!443 = !DILocalVariable(name: "pipe_left", scope: !444, file: !3, line: 383, type: !21, align: 16)
!444 = distinct !DILexicalBlock(scope: !442, file: !3, line: 383, column: 17)
!445 = !DILocalVariable(name: "pipe_right", scope: !446, file: !3, line: 384, type: !21, align: 16)
!446 = distinct !DILexicalBlock(scope: !444, file: !3, line: 384, column: 17)
!447 = !DILocalVariable(name: "gap_top", scope: !448, file: !3, line: 385, type: !21, align: 16)
!448 = distinct !DILexicalBlock(scope: !446, file: !3, line: 385, column: 17)
!449 = !DILocalVariable(name: "gap_bottom", scope: !450, file: !3, line: 386, type: !21, align: 16)
!450 = distinct !DILexicalBlock(scope: !448, file: !3, line: 386, column: 17)
!451 = !DILocation(line: 0, scope: !438)
!452 = !DILocation(line: 0, scope: !440)
!453 = !DILocation(line: 367, column: 29, scope: !427)
!454 = !DILocation(line: 0, scope: !432)
!455 = !DILocation(line: 0, scope: !434)
!456 = !DILocation(line: 369, column: 27, scope: !434)
!457 = !DILocation(line: 0, scope: !436)
!458 = !DILocation(line: 373, column: 12, scope: !440)
!459 = !DILocation(line: 399, column: 2, scope: !427)
!460 = !DILocation(line: 0, scope: !442)
!461 = !DILocation(line: 382, column: 16, scope: !442)
!462 = !DILocation(line: 383, column: 33, scope: !442)
!463 = !DILocation(line: 0, scope: !444)
!464 = !DILocation(line: 0, scope: !446)
!465 = !DILocation(line: 0, scope: !448)
!466 = !DILocation(line: 0, scope: !450)
!467 = !DILocation(line: 388, column: 20, scope: !450)
!468 = !DILocation(line: 385, column: 31, scope: !446)
!469 = !DILocation(line: 386, column: 34, scope: !448)
!470 = !DILocation(line: 389, column: 24, scope: !450)
!471 = !DILocation(line: 381, column: 15, scope: !442)
!472 = distinct !DISubprogram(name: "drawReadyScreen", linkageName: "_ZN3lib15drawReadyScreen17h28203f98bd85755bE", scope: !2, file: !3, line: 579, type: !306, scopeLine: 579, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !473)
!473 = !{!474}
!474 = !DILocalVariable(name: "bird_y", scope: !475, file: !3, line: 580, type: !21, align: 16)
!475 = distinct !DILexicalBlock(scope: !472, file: !3, line: 580, column: 5)
!476 = !DILocation(line: 0, scope: !475)
!477 = !DILocation(line: 582, column: 5, scope: !475)
!478 = !DILocation(line: 585, column: 5, scope: !475)
!479 = !DILocation(line: 586, column: 5, scope: !475)
!480 = !DILocation(line: 587, column: 5, scope: !475)
!481 = !DILocation(line: 588, column: 5, scope: !475)
!482 = !DILocation(line: 589, column: 2, scope: !472)
!483 = distinct !DISubprogram(name: "spawn_initial_pipes", linkageName: "_ZN3lib19spawn_initial_pipes17h2e23eac7186d6fd2E", scope: !2, file: !3, line: 308, type: !306, scopeLine: 308, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23)
!484 = !DILocation(line: 309, column: 5, scope: !483)
!485 = !DILocation(line: 310, column: 2, scope: !483)
!486 = distinct !DISubprogram(name: "find_rightmost_pipe_x", linkageName: "_ZN3lib21find_rightmost_pipe_x17hadc4e3130a184b0aE", scope: !2, file: !3, line: 276, type: !383, scopeLine: 276, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !487)
!487 = !{!488, !490}
!488 = !DILocalVariable(name: "max_x", scope: !489, file: !3, line: 278, type: !21, align: 16)
!489 = distinct !DILexicalBlock(scope: !486, file: !3, line: 278, column: 9)
!490 = !DILocalVariable(name: "i", scope: !491, file: !3, line: 279, type: !93, align: 32)
!491 = distinct !DILexicalBlock(scope: !489, file: !3, line: 279, column: 9)
!492 = !DILocation(line: 0, scope: !489)
!493 = !DILocation(line: 0, scope: !491)
!494 = !DILocation(line: 281, column: 16, scope: !491)
!495 = !DILocation(line: 288, column: 2, scope: !486)
!496 = distinct !DISubprogram(name: "clearFB", linkageName: "_ZN3lib7clearFB17hdd3e5919c5b634efE", scope: !2, file: !3, line: 135, type: !306, scopeLine: 135, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !497)
!497 = !{!498}
!498 = !DILocalVariable(name: "i", scope: !499, file: !3, line: 136, type: !93, align: 32)
!499 = distinct !DILexicalBlock(scope: !496, file: !3, line: 136, column: 5)
!500 = !DILocation(line: 0, scope: !499)
!501 = !DILocation(line: 138, column: 9, scope: !499)
!502 = !DILocation(line: 141, column: 2, scope: !496)
!503 = distinct !DISubprogram(name: "drawBird", linkageName: "_ZN3lib8drawBird17hf8f2a7b43ff767a3E", scope: !2, file: !3, line: 533, type: !306, scopeLine: 533, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !504)
!504 = !{!505, !507}
!505 = !DILocalVariable(name: "x", scope: !506, file: !3, line: 535, type: !21, align: 16)
!506 = distinct !DILexicalBlock(scope: !503, file: !3, line: 535, column: 9)
!507 = !DILocalVariable(name: "y", scope: !508, file: !3, line: 536, type: !21, align: 16)
!508 = distinct !DILexicalBlock(scope: !506, file: !3, line: 536, column: 9)
!509 = !DILocation(line: 0, scope: !506)
!510 = !DILocation(line: 536, column: 17, scope: !506)
!511 = !DILocation(line: 0, scope: !508)
!512 = !DILocation(line: 537, column: 44, scope: !508)
!513 = !DILocation(line: 537, column: 9, scope: !508)
!514 = !DILocation(line: 539, column: 2, scope: !503)
!515 = distinct !DISubprogram(name: "drawPipe", linkageName: "_ZN3lib8drawPipe17hb26dbc7dfdbd4978E", scope: !2, file: !3, line: 542, type: !516, scopeLine: 542, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !518)
!516 = !DISubroutineType(types: !517)
!517 = !{null, !93}
!518 = !{!519, !520, !522, !524, !526}
!519 = !DILocalVariable(name: "idx", arg: 1, scope: !515, file: !3, line: 542, type: !93)
!520 = !DILocalVariable(name: "x", scope: !521, file: !3, line: 544, type: !21, align: 16)
!521 = distinct !DILexicalBlock(scope: !515, file: !3, line: 544, column: 9)
!522 = !DILocalVariable(name: "gap_y", scope: !523, file: !3, line: 545, type: !21, align: 16)
!523 = distinct !DILexicalBlock(scope: !521, file: !3, line: 545, column: 9)
!524 = !DILocalVariable(name: "gap_top", scope: !525, file: !3, line: 546, type: !21, align: 16)
!525 = distinct !DILexicalBlock(scope: !523, file: !3, line: 546, column: 9)
!526 = !DILocalVariable(name: "gap_bottom", scope: !527, file: !3, line: 547, type: !21, align: 16)
!527 = distinct !DILexicalBlock(scope: !525, file: !3, line: 547, column: 9)
!528 = !DILocation(line: 0, scope: !515)
!529 = !DILocation(line: 544, column: 17, scope: !515)
!530 = !DILocation(line: 0, scope: !521)
!531 = !DILocation(line: 545, column: 21, scope: !521)
!532 = !DILocation(line: 0, scope: !523)
!533 = !DILocation(line: 546, column: 23, scope: !523)
!534 = !DILocation(line: 0, scope: !525)
!535 = !DILocation(line: 547, column: 26, scope: !525)
!536 = !DILocation(line: 0, scope: !527)
!537 = !DILocation(line: 549, column: 12, scope: !527)
!538 = !DILocation(line: 552, column: 12, scope: !527)
!539 = !DILocation(line: 550, column: 28, scope: !527)
!540 = !DILocation(line: 550, column: 48, scope: !527)
!541 = !DILocation(line: 550, column: 13, scope: !527)
!542 = !DILocation(line: 549, column: 9, scope: !527)
!543 = !DILocation(line: 556, column: 2, scope: !515)
!544 = !DILocation(line: 553, column: 37, scope: !527)
!545 = !DILocation(line: 553, column: 13, scope: !527)
!546 = !DILocation(line: 552, column: 9, scope: !527)
!547 = distinct !DISubprogram(name: "drawRect", linkageName: "_ZN3lib8drawRect17h579d1c66bf16d8b0E", scope: !2, file: !3, line: 224, type: !548, scopeLine: 224, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !550)
!548 = !DISubroutineType(cc: DW_CC_nocall, types: !549)
!549 = !{null, !21, !21, !21, !21, !5}
!550 = !{!551, !552, !553, !554, !555}
!551 = !DILocalVariable(name: "x0", arg: 1, scope: !547, file: !3, line: 224, type: !21)
!552 = !DILocalVariable(name: "y0", arg: 2, scope: !547, file: !3, line: 224, type: !21)
!553 = !DILocalVariable(name: "x1", arg: 3, scope: !547, file: !3, line: 224, type: !21)
!554 = !DILocalVariable(name: "y1", arg: 4, scope: !547, file: !3, line: 224, type: !21)
!555 = !DILocalVariable(name: "color", arg: 5, scope: !547, file: !3, line: 224, type: !5)
!556 = !DILocation(line: 0, scope: !547)
!557 = !DILocation(line: 225, column: 5, scope: !547)
!558 = !DILocation(line: 226, column: 5, scope: !547)
!559 = !DILocation(line: 227, column: 5, scope: !547)
!560 = !DILocation(line: 228, column: 5, scope: !547)
!561 = !DILocation(line: 229, column: 2, scope: !547)
!562 = distinct !DISubprogram(name: "fillRect", linkageName: "_ZN3lib8fillRect17h4f9b61cc7fa27dcbE", scope: !2, file: !3, line: 160, type: !548, scopeLine: 160, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !563)
!563 = !{!564, !565, !566, !567, !568, !569, !571, !573, !575, !577, !579, !581, !583, !585, !587, !589, !591, !593, !595, !597, !599}
!564 = !DILocalVariable(name: "x0", arg: 1, scope: !562, file: !3, line: 160, type: !21)
!565 = !DILocalVariable(name: "y0", arg: 2, scope: !562, file: !3, line: 160, type: !21)
!566 = !DILocalVariable(name: "x1", arg: 3, scope: !562, file: !3, line: 160, type: !21)
!567 = !DILocalVariable(name: "y1", arg: 4, scope: !562, file: !3, line: 160, type: !21)
!568 = !DILocalVariable(name: "color", arg: 5, scope: !562, file: !3, line: 160, type: !5)
!569 = !DILocalVariable(name: "x0", scope: !570, file: !3, line: 162, type: !21, align: 16)
!570 = distinct !DILexicalBlock(scope: !562, file: !3, line: 162, column: 5)
!571 = !DILocalVariable(name: "y0", scope: !572, file: !3, line: 163, type: !21, align: 16)
!572 = distinct !DILexicalBlock(scope: !570, file: !3, line: 163, column: 5)
!573 = !DILocalVariable(name: "x1", scope: !574, file: !3, line: 164, type: !21, align: 16)
!574 = distinct !DILexicalBlock(scope: !572, file: !3, line: 164, column: 5)
!575 = !DILocalVariable(name: "y1", scope: !576, file: !3, line: 165, type: !21, align: 16)
!576 = distinct !DILexicalBlock(scope: !574, file: !3, line: 165, column: 5)
!577 = !DILocalVariable(name: "start_byte", scope: !578, file: !3, line: 176, type: !93, align: 32)
!578 = distinct !DILexicalBlock(scope: !576, file: !3, line: 176, column: 5)
!579 = !DILocalVariable(name: "end_byte", scope: !580, file: !3, line: 177, type: !93, align: 32)
!580 = distinct !DILexicalBlock(scope: !578, file: !3, line: 177, column: 5)
!581 = !DILocalVariable(name: "start_mask", scope: !582, file: !3, line: 178, type: !5, align: 8)
!582 = distinct !DILexicalBlock(scope: !580, file: !3, line: 178, column: 5)
!583 = !DILocalVariable(name: "end_mask", scope: !584, file: !3, line: 179, type: !5, align: 8)
!584 = distinct !DILexicalBlock(scope: !582, file: !3, line: 179, column: 5)
!585 = !DILocalVariable(name: "y", scope: !586, file: !3, line: 181, type: !21, align: 16)
!586 = distinct !DILexicalBlock(scope: !584, file: !3, line: 181, column: 5)
!587 = !DILocalVariable(name: "row_base", scope: !588, file: !3, line: 183, type: !93, align: 32)
!588 = distinct !DILexicalBlock(scope: !586, file: !3, line: 183, column: 9)
!589 = !DILocalVariable(name: "mask", scope: !590, file: !3, line: 186, type: !5, align: 8)
!590 = distinct !DILexicalBlock(scope: !588, file: !3, line: 186, column: 13)
!591 = !DILocalVariable(name: "idx", scope: !592, file: !3, line: 187, type: !93, align: 32)
!592 = distinct !DILexicalBlock(scope: !590, file: !3, line: 187, column: 13)
!593 = !DILocalVariable(name: "idx_start", scope: !594, file: !3, line: 195, type: !93, align: 32)
!594 = distinct !DILexicalBlock(scope: !588, file: !3, line: 195, column: 13)
!595 = !DILocalVariable(name: "fill_byte", scope: !596, file: !3, line: 203, type: !5, align: 8)
!596 = distinct !DILexicalBlock(scope: !594, file: !3, line: 203, column: 13)
!597 = !DILocalVariable(name: "b", scope: !598, file: !3, line: 204, type: !93, align: 32)
!598 = distinct !DILexicalBlock(scope: !596, file: !3, line: 204, column: 13)
!599 = !DILocalVariable(name: "idx_end", scope: !600, file: !3, line: 211, type: !93, align: 32)
!600 = distinct !DILexicalBlock(scope: !598, file: !3, line: 211, column: 13)
!601 = !DILocation(line: 0, scope: !562)
!602 = !DILocation(line: 0, scope: !570)
!603 = !DILocation(line: 0, scope: !572)
!604 = !DILocation(line: 0, scope: !574)
!605 = !DILocation(line: 0, scope: !576)
!606 = !DILocation(line: 167, column: 8, scope: !576)
!607 = !DILocation(line: 171, column: 8, scope: !576)
!608 = !DILocation(line: 172, column: 8, scope: !576)
!609 = !DILocation(line: 173, column: 8, scope: !576)
!610 = !DILocation(line: 174, column: 8, scope: !576)
!611 = !DILocation(line: 176, column: 22, scope: !576)
!612 = !DILocation(line: 0, scope: !578)
!613 = !DILocation(line: 177, column: 20, scope: !578)
!614 = !DILocation(line: 0, scope: !580)
!615 = !DILocation(line: 178, column: 39, scope: !580)
!616 = !DILocation(line: 178, column: 28, scope: !580)
!617 = !DILocation(line: 0, scope: !582)
!618 = !DILocation(line: 179, column: 37, scope: !582)
!619 = !DILocation(line: 179, column: 26, scope: !582)
!620 = !DILocation(line: 0, scope: !584)
!621 = !DILocation(line: 0, scope: !586)
!622 = !DILocation(line: 182, column: 5, scope: !586)
!623 = !DILocation(line: 182, column: 11, scope: !586)
!624 = !DILocation(line: 183, column: 24, scope: !586)
!625 = !DILocation(line: 0, scope: !588)
!626 = !DILocation(line: 185, column: 12, scope: !588)
!627 = !DILocation(line: 221, column: 2, scope: !562)
!628 = !DILocation(line: 0, scope: !594)
!629 = !DILocalVariable(name: "self", arg: 1, scope: !630, file: !631, line: 682, type: !637)
!630 = distinct !DISubprogram(name: "get_unchecked_mut<i8, usize>", linkageName: "_ZN4core5slice29_$LT$impl$u20$$u5b$T$u5d$$GT$17get_unchecked_mut17h4cafa0213b7c8b52E", scope: !632, file: !631, line: 682, type: !634, scopeLine: 682, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !644, retainedNodes: !642)
!631 = !DIFile(filename: "/rustlib/src/rust/library/core/src/slice/mod.rs", directory: "", checksumkind: CSK_MD5, checksum: "3a151d8ad3401591df12e651dca32afb")
!632 = !DINamespace(name: "{impl#0}", scope: !633)
!633 = !DINamespace(name: "slice", scope: !59)
!634 = !DISubroutineType(types: !635)
!635 = !{!636, !637, !93, !218}
!636 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "&mut i8", baseType: !5, size: 32, align: 32, dwarfAddressSpace: 0)
!637 = !DICompositeType(tag: DW_TAG_structure_type, name: "&mut [i8]", file: !18, size: 64, align: 32, elements: !638, templateParams: !23, identifier: "ada2f5e14ad166ff25ebe72e9356385f")
!638 = !{!639, !641}
!639 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !637, file: !18, baseType: !640, size: 32, align: 32)
!640 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !5, size: 32, align: 32, dwarfAddressSpace: 0)
!641 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !637, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!642 = !{!629, !643}
!643 = !DILocalVariable(name: "index", arg: 2, scope: !630, file: !631, line: 682, type: !93)
!644 = !{!645, !646}
!645 = !DITemplateTypeParameter(name: "T", type: !5)
!646 = !DITemplateTypeParameter(name: "I", type: !93)
!647 = !DILocation(line: 0, scope: !630, inlinedAt: !648)
!648 = distinct !DILocation(line: 197, column: 30, scope: !594)
!649 = !DILocalVariable(name: "self", arg: 1, scope: !650, file: !651, line: 254, type: !93)
!650 = distinct !DISubprogram(name: "get_unchecked_mut<i8>", linkageName: "_ZN75_$LT$usize$u20$as$u20$core..slice..index..SliceIndex$LT$$u5b$T$u5d$$GT$$GT$17get_unchecked_mut17h96bc0c6ea2bafeceE", scope: !652, file: !651, line: 254, type: !654, scopeLine: 254, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !663, retainedNodes: !661)
!651 = !DIFile(filename: "/rustlib/src/rust/library/core/src/slice/index.rs", directory: "", checksumkind: CSK_MD5, checksum: "1a82fa3b7b71e0e3e5ba9928c742ba5b")
!652 = !DINamespace(name: "{impl#2}", scope: !653)
!653 = !DINamespace(name: "index", scope: !633)
!654 = !DISubroutineType(types: !655)
!655 = !{!656, !93, !657, !218}
!656 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "*mut i8", baseType: !5, size: 32, align: 32, dwarfAddressSpace: 0)
!657 = !DICompositeType(tag: DW_TAG_structure_type, name: "*mut [i8]", file: !18, size: 64, align: 32, elements: !658, templateParams: !23, identifier: "8765094cbca83adceff7d19f7e339034")
!658 = !{!659, !660}
!659 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !657, file: !18, baseType: !640, size: 32, align: 32)
!660 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !657, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!661 = !{!649, !662}
!662 = !DILocalVariable(name: "slice", arg: 2, scope: !650, file: !651, line: 254, type: !657)
!663 = !{!645}
!664 = !DILocation(line: 0, scope: !650, inlinedAt: !665)
!665 = distinct !DILocation(line: 689, column: 30, scope: !630, inlinedAt: !648)
!666 = !DILocation(line: 261, column: 18, scope: !650, inlinedAt: !665)
!667 = !DILocation(line: 197, column: 17, scope: !594)
!668 = !DILocation(line: 0, scope: !596)
!669 = !DILocation(line: 0, scope: !598)
!670 = !DILocation(line: 205, column: 19, scope: !598)
!671 = !DILocation(line: 206, column: 17, scope: !598)
!672 = !DILocation(line: 0, scope: !630, inlinedAt: !673)
!673 = distinct !DILocation(line: 206, column: 30, scope: !598)
!674 = !DILocation(line: 0, scope: !650, inlinedAt: !675)
!675 = distinct !DILocation(line: 689, column: 30, scope: !630, inlinedAt: !673)
!676 = !DILocation(line: 261, column: 18, scope: !650, inlinedAt: !677)
!677 = distinct !DILocation(line: 689, column: 30, scope: !630, inlinedAt: !678)
!678 = distinct !DILocation(line: 213, column: 30, scope: !600)
!679 = !DILocation(line: 261, column: 18, scope: !650, inlinedAt: !680)
!680 = !DILocation(line: 689, column: 30, scope: !630, inlinedAt: !625)
!681 = !DILocation(line: 219, column: 9, scope: !588)
!682 = distinct !DISubprogram(name: "setPixel", linkageName: "_ZN3lib8setPixel17h43bda99ce5e3fe75E", scope: !2, file: !3, line: 144, type: !683, scopeLine: 144, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !685)
!683 = !DISubroutineType(cc: DW_CC_nocall, types: !684)
!684 = !{null, !21, !21, !5}
!685 = !{!686, !687, !688, !689, !691}
!686 = !DILocalVariable(name: "x", arg: 1, scope: !682, file: !3, line: 144, type: !21)
!687 = !DILocalVariable(name: "y", arg: 2, scope: !682, file: !3, line: 144, type: !21)
!688 = !DILocalVariable(name: "color", arg: 3, scope: !682, file: !3, line: 144, type: !5)
!689 = !DILocalVariable(name: "byte_idx", scope: !690, file: !3, line: 149, type: !93, align: 32)
!690 = distinct !DILexicalBlock(scope: !682, file: !3, line: 149, column: 5)
!691 = !DILocalVariable(name: "mask", scope: !692, file: !3, line: 150, type: !5, align: 8)
!692 = distinct !DILexicalBlock(scope: !690, file: !3, line: 150, column: 5)
!693 = !DILocation(line: 0, scope: !682)
!694 = !DILocation(line: 0, scope: !690)
!695 = !DILocation(line: 0, scope: !692)
!696 = !DILocation(line: 150, column: 33, scope: !690)
!697 = !DILocation(line: 150, column: 22, scope: !690)
!698 = !DILocation(line: 149, column: 21, scope: !682)
!699 = !DILocation(line: 149, column: 32, scope: !682)
!700 = !DILocation(line: 149, column: 20, scope: !682)
!701 = !DILocation(line: 0, scope: !630, inlinedAt: !702)
!702 = distinct !DILocation(line: 153, column: 22, scope: !692)
!703 = !DILocation(line: 0, scope: !650, inlinedAt: !704)
!704 = distinct !DILocation(line: 689, column: 30, scope: !630, inlinedAt: !702)
!705 = !DILocation(line: 261, column: 18, scope: !650, inlinedAt: !704)
!706 = !DILocation(line: 153, column: 9, scope: !692)
!707 = !DILocation(line: 157, column: 2, scope: !682)
!708 = distinct !DISubprogram(name: "drawDigit", linkageName: "_ZN3lib9drawDigit17h0ebc745f1e2cb6a0E", scope: !2, file: !3, line: 438, type: !246, scopeLine: 438, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !709)
!709 = !{!710, !711, !712, !713, !714, !716, !718, !720, !722, !724, !726, !728, !730}
!710 = !DILocalVariable(name: "x", arg: 1, scope: !708, file: !3, line: 438, type: !21)
!711 = !DILocalVariable(name: "y", arg: 2, scope: !708, file: !3, line: 438, type: !21)
!712 = !DILocalVariable(name: "digit", arg: 3, scope: !708, file: !3, line: 438, type: !21)
!713 = !DILocalVariable(name: "color", arg: 4, scope: !708, file: !3, line: 438, type: !5)
!714 = !DILocalVariable(name: "x_bit", scope: !715, file: !3, line: 446, type: !60, align: 8)
!715 = distinct !DILexicalBlock(scope: !708, file: !3, line: 446, column: 5)
!716 = !DILocalVariable(name: "row", scope: !717, file: !3, line: 448, type: !21, align: 16)
!717 = distinct !DILexicalBlock(scope: !715, file: !3, line: 448, column: 5)
!718 = !DILocalVariable(name: "font_row", scope: !719, file: !3, line: 450, type: !5, align: 8)
!719 = distinct !DILexicalBlock(scope: !717, file: !3, line: 450, column: 9)
!720 = !DILocalVariable(name: "byte_idx", scope: !721, file: !3, line: 451, type: !93, align: 32)
!721 = distinct !DILexicalBlock(scope: !719, file: !3, line: 451, column: 9)
!722 = !DILocalVariable(name: "shift", scope: !723, file: !3, line: 455, type: !60, align: 8)
!723 = distinct !DILexicalBlock(scope: !721, file: !3, line: 455, column: 13)
!724 = !DILocalVariable(name: "mask1", scope: !725, file: !3, line: 456, type: !5, align: 8)
!725 = distinct !DILexicalBlock(scope: !723, file: !3, line: 456, column: 13)
!726 = !DILocalVariable(name: "shift", scope: !727, file: !3, line: 464, type: !60, align: 8)
!727 = distinct !DILexicalBlock(scope: !721, file: !3, line: 464, column: 13)
!728 = !DILocalVariable(name: "mask1", scope: !729, file: !3, line: 465, type: !5, align: 8)
!729 = distinct !DILexicalBlock(scope: !727, file: !3, line: 465, column: 13)
!730 = !DILocalVariable(name: "mask2", scope: !731, file: !3, line: 466, type: !5, align: 8)
!731 = distinct !DILexicalBlock(scope: !729, file: !3, line: 466, column: 13)
!732 = !DILocation(line: 0, scope: !708)
!733 = !DILocation(line: 439, column: 8, scope: !708)
!734 = !DILocation(line: 446, column: 17, scope: !708)
!735 = !DILocation(line: 0, scope: !715)
!736 = !DILocation(line: 0, scope: !717)
!737 = !DILocation(line: 449, column: 11, scope: !717)
!738 = !DILocalVariable(name: "self", arg: 1, scope: !739, file: !631, line: 637, type: !743)
!739 = distinct !DISubprogram(name: "get_unchecked<i8, usize>", linkageName: "_ZN4core5slice29_$LT$impl$u20$$u5b$T$u5d$$GT$13get_unchecked17h823336c082fef02cE", scope: !632, file: !631, line: 637, type: !740, scopeLine: 637, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !644, retainedNodes: !747)
!740 = !DISubroutineType(types: !741)
!741 = !{!742, !743, !93, !218}
!742 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "&i8", baseType: !5, size: 32, align: 32, dwarfAddressSpace: 0)
!743 = !DICompositeType(tag: DW_TAG_structure_type, name: "&[i8]", file: !18, size: 64, align: 32, elements: !744, templateParams: !23, identifier: "323dc304adbca782d453d94ce0d24f97")
!744 = !{!745, !746}
!745 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !743, file: !18, baseType: !640, size: 32, align: 32)
!746 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !743, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!747 = !{!738, !748}
!748 = !DILocalVariable(name: "index", arg: 2, scope: !739, file: !631, line: 637, type: !93)
!749 = !DILocation(line: 0, scope: !739, inlinedAt: !750)
!750 = distinct !DILocation(line: 450, column: 36, scope: !717)
!751 = !DILocalVariable(name: "self", arg: 1, scope: !752, file: !651, line: 234, type: !93)
!752 = distinct !DISubprogram(name: "get_unchecked<i8>", linkageName: "_ZN75_$LT$usize$u20$as$u20$core..slice..index..SliceIndex$LT$$u5b$T$u5d$$GT$$GT$13get_unchecked17h4855f446705aafb2E", scope: !652, file: !651, line: 234, type: !753, scopeLine: 234, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !663, retainedNodes: !760)
!753 = !DISubroutineType(types: !754)
!754 = !{!755, !93, !756, !218}
!755 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "*const i8", baseType: !5, size: 32, align: 32, dwarfAddressSpace: 0)
!756 = !DICompositeType(tag: DW_TAG_structure_type, name: "*const [i8]", file: !18, size: 64, align: 32, elements: !757, templateParams: !23, identifier: "fa066b6ee6cdd9ae6154fbc57a99506a")
!757 = !{!758, !759}
!758 = !DIDerivedType(tag: DW_TAG_member, name: "data_ptr", scope: !756, file: !18, baseType: !640, size: 32, align: 32)
!759 = !DIDerivedType(tag: DW_TAG_member, name: "length", scope: !756, file: !18, baseType: !93, size: 32, align: 32, offset: 32)
!760 = !{!751, !761}
!761 = !DILocalVariable(name: "slice", arg: 2, scope: !752, file: !651, line: 234, type: !756)
!762 = !DILocation(line: 0, scope: !752, inlinedAt: !763)
!763 = distinct !DILocation(line: 644, column: 26, scope: !739, inlinedAt: !750)
!764 = !DILocation(line: 248, column: 13, scope: !752, inlinedAt: !763)
!765 = !DILocation(line: 450, column: 24, scope: !717)
!766 = !DILocation(line: 0, scope: !719)
!767 = !DILocation(line: 451, column: 25, scope: !719)
!768 = !DILocation(line: 451, column: 24, scope: !719)
!769 = !DILocation(line: 0, scope: !721)
!770 = !DILocation(line: 453, column: 12, scope: !721)
!771 = !DILocation(line: 261, column: 18, scope: !650, inlinedAt: !772)
!772 = !DILocation(line: 689, column: 30, scope: !630, inlinedAt: !769)
!773 = !DILocation(line: 478, column: 2, scope: !708)
!774 = !DILocation(line: 0, scope: !727)
!775 = !DILocation(line: 0, scope: !729)
!776 = !DILocation(line: 0, scope: !731)
!777 = !DILocation(line: 465, column: 25, scope: !727)
!778 = !DILocation(line: 0, scope: !630, inlinedAt: !779)
!779 = distinct !DILocation(line: 468, column: 30, scope: !731)
!780 = !DILocation(line: 0, scope: !650, inlinedAt: !781)
!781 = distinct !DILocation(line: 689, column: 30, scope: !630, inlinedAt: !779)
!782 = !DILocation(line: 261, column: 18, scope: !650, inlinedAt: !781)
!783 = !DILocation(line: 468, column: 17, scope: !731)
!784 = !DILocation(line: 0, scope: !630, inlinedAt: !785)
!785 = distinct !DILocation(line: 469, column: 30, scope: !731)
!786 = !DILocation(line: 0, scope: !650, inlinedAt: !787)
!787 = distinct !DILocation(line: 689, column: 30, scope: !630, inlinedAt: !785)
!788 = !DILocation(line: 467, column: 13, scope: !731)
!789 = distinct !DISubprogram(name: "drawPipes", linkageName: "_ZN3lib9drawPipes17hc093196a1ee1552cE", scope: !2, file: !3, line: 559, type: !306, scopeLine: 559, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !790)
!790 = !{!791}
!791 = !DILocalVariable(name: "i", scope: !792, file: !3, line: 561, type: !93, align: 32)
!792 = distinct !DILexicalBlock(scope: !789, file: !3, line: 561, column: 9)
!793 = !DILocation(line: 0, scope: !792)
!794 = !DILocation(line: 563, column: 16, scope: !792)
!795 = !DILocation(line: 564, column: 17, scope: !792)
!796 = !DILocation(line: 563, column: 13, scope: !792)
!797 = !DILocation(line: 569, column: 2, scope: !789)
!798 = distinct !DISubprogram(name: "drawScore", linkageName: "_ZN3lib9drawScore17h21f5311f5325b862E", scope: !2, file: !3, line: 572, type: !306, scopeLine: 572, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23)
!799 = !DILocation(line: 574, column: 41, scope: !798)
!800 = !DILocation(line: 574, column: 9, scope: !798)
!801 = !DILocation(line: 576, column: 2, scope: !798)
!802 = distinct !DISubprogram(name: "game_tick", linkageName: "_ZN3lib9game_tick17h3339f306e2fb44f3E", scope: !2, file: !3, line: 402, type: !349, scopeLine: 402, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !803)
!803 = !{!804}
!804 = !DILocalVariable(name: "flap_input", arg: 1, scope: !802, file: !3, line: 402, type: !5)
!805 = !DILocation(line: 0, scope: !802)
!806 = !DILocation(line: 404, column: 12, scope: !802)
!807 = !DILocation(line: 405, column: 16, scope: !802)
!808 = !DILocation(line: 425, column: 12, scope: !802)
!809 = !DILocation(line: 414, column: 13, scope: !802)
!810 = !DILocation(line: 415, column: 13, scope: !802)
!811 = !DILocation(line: 417, column: 16, scope: !802)
!812 = !DILocation(line: 427, column: 17, scope: !802)
!813 = !DILocation(line: 431, column: 2, scope: !802)
!814 = !DILocation(line: 418, column: 17, scope: !802)
!815 = !DILocation(line: 417, column: 13, scope: !802)
!816 = !DILocation(line: 421, column: 13, scope: !802)
!817 = !DILocation(line: 406, column: 17, scope: !802)
!818 = !DILocation(line: 407, column: 17, scope: !802)
!819 = !DILocation(line: 408, column: 17, scope: !802)
!820 = distinct !DISubprogram(name: "_jcsl_method_cap_fix", scope: !2, file: !3, line: 674, type: !306, scopeLine: 674, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23)
!821 = !DILocation(line: 674, column: 44, scope: !820)
!822 = distinct !DISubprogram(name: "process", scope: !2, file: !3, line: 633, type: !823, scopeLine: 633, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !23, retainedNodes: !826)
!823 = !DISubroutineType(types: !824)
!824 = !{null, !825, !21}
!825 = !DIDerivedType(tag: DW_TAG_pointer_type, name: "*mut core::ffi::c_void", baseType: !57, size: 32, align: 32, dwarfAddressSpace: 0)
!826 = !{!827, !828, !829, !831, !833}
!827 = !DILocalVariable(name: "apdu", arg: 1, scope: !822, file: !3, line: 633, type: !825)
!828 = !DILocalVariable(name: "apdu_len", arg: 2, scope: !822, file: !3, line: 633, type: !21)
!829 = !DILocalVariable(name: "buffer", scope: !830, file: !3, line: 635, type: !656, align: 32)
!830 = distinct !DILexicalBlock(scope: !822, file: !3, line: 635, column: 9)
!831 = !DILocalVariable(name: "ins", scope: !832, file: !3, line: 636, type: !5, align: 8)
!832 = distinct !DILexicalBlock(scope: !830, file: !3, line: 636, column: 9)
!833 = !DILocalVariable(name: "flap", scope: !834, file: !3, line: 652, type: !5, align: 8)
!834 = distinct !DILexicalBlock(scope: !832, file: !3, line: 652, column: 13)
!835 = !DILocation(line: 0, scope: !822)
!836 = !DILocation(line: 635, column: 22, scope: !822)
!837 = !DILocation(line: 0, scope: !830)
!838 = !DILocalVariable(name: "self", arg: 1, scope: !839, file: !840, line: 352, type: !656)
!839 = distinct !DISubprogram(name: "offset<i8>", linkageName: "_ZN4core3ptr7mut_ptr31_$LT$impl$u20$$BP$mut$u20$T$GT$6offset17h71140a0f10bd66b7E", scope: !841, file: !840, line: 352, type: !843, scopeLine: 352, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !54, templateParams: !663, retainedNodes: !846)
!840 = !DIFile(filename: "/rustlib/src/rust/library/core/src/ptr/mut_ptr.rs", directory: "", checksumkind: CSK_MD5, checksum: "5eabb6ee07ba6a1444cb81cb6a2d22ef")
!841 = !DINamespace(name: "{impl#0}", scope: !842)
!842 = !DINamespace(name: "mut_ptr", scope: !157)
!843 = !DISubroutineType(types: !844)
!844 = !{!656, !656, !845, !218}
!845 = !DIBasicType(name: "isize", size: 32, encoding: DW_ATE_signed)
!846 = !{!838, !847}
!847 = !DILocalVariable(name: "count", arg: 2, scope: !839, file: !840, line: 352, type: !845)
!848 = !DILocation(line: 0, scope: !839, inlinedAt: !849)
!849 = distinct !DILocation(line: 636, column: 27, scope: !830)
!850 = !DILocation(line: 389, column: 18, scope: !839, inlinedAt: !849)
!851 = !DILocation(line: 636, column: 19, scope: !830)
!852 = !DILocation(line: 0, scope: !832)
!853 = !DILocation(line: 639, column: 12, scope: !832)
!854 = !DILocation(line: 640, column: 13, scope: !832)
!855 = !DILocation(line: 641, column: 13, scope: !832)
!856 = !DILocation(line: 639, column: 9, scope: !832)
!857 = !DILocation(line: 644, column: 12, scope: !832)
!858 = !DILocation(line: 645, column: 13, scope: !832)
!859 = !DILocation(line: 646, column: 13, scope: !832)
!860 = !DILocation(line: 647, column: 13, scope: !832)
!861 = !DILocation(line: 668, column: 9, scope: !832)
!862 = !DILocation(line: 652, column: 33, scope: !832)
!863 = !DILocation(line: 670, column: 2, scope: !822)
!864 = !DILocation(line: 0, scope: !839, inlinedAt: !865)
!865 = distinct !DILocation(line: 653, column: 26, scope: !832)
!866 = !DILocation(line: 389, column: 18, scope: !839, inlinedAt: !865)
!867 = !DILocation(line: 653, column: 17, scope: !832)
!868 = !DILocation(line: 0, scope: !834)
!869 = !DILocation(line: 652, column: 30, scope: !832)
!870 = !DILocation(line: 658, column: 13, scope: !834)
!871 = !DILocation(line: 659, column: 13, scope: !834)
!872 = !DILocation(line: 660, column: 13, scope: !834)
!873 = !DILocation(line: 662, column: 13, scope: !834)
!874 = !DILocation(line: 663, column: 13, scope: !834)
!875 = !DILocation(line: 664, column: 13, scope: !834)
