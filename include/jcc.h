// jcc.h - JCC JavaCard interface

#ifndef JCC_H
#define JCC_H

// Primitive types (matching JavaCard)
typedef signed char byte;
// short and int are built-in

// APDU object type (opaque reference)
typedef void* APDU;

// ===========================================================================
// Storage Classes (JCC-specific)
// ===========================================================================
//
// JCC provides three storage tiers optimized for JavaCard's constraints:
//
// (default):  JCVM stack - Fast access (1 instruction), limited space (64 slots).
//             Standard C behavior. Use for most variables.
//             Note: 'register' keyword is accepted but unnecessary (same as default).
//
// static:     Persistent storage - Values survive function calls. Medium speed
//             (3 instructions). Stored in dedicated MEM_B/S/I space.
//             Use for counters, state machines, function-scoped globals.
//
// offload:    Shared stack - Slow access (7 instructions), unlimited space.
//             Stored in shared STACK_B/S/I transient arrays.
//             Use when stack overflow occurs or for cold variables.
//
// Example:
//   void process(APDU apdu, short len) {
//       short i;              // Default - fast JCVM stack
//       offload int temp[50]; // Offload - saves stack space
//       static short calls;   // Static - persists across calls
//   }
//
// Stack Overflow:
//   If your function exceeds 64 slots, the compiler will error with the call
//   chain and slot usage. Mark large or infrequently-used variables as 'offload'.
//   Tip: int variables use 2 slots each - good candidates for offloading.
//

// offload keyword: maps to 'volatile' because C parsers don't recognize custom keywords.
// Semantically correct - offload storage is slower and external (like volatile semantics).
#define offload volatile

// APDU buffer offsets
#define APDU_CLA  0
#define APDU_INS  1
#define APDU_P1   2
#define APDU_P2   3
#define APDU_LC   4
#define APDU_DATA 5

// Status words (ISO 7816-4)
#define SW_OK                     0x9000
#define SW_WRONG_LENGTH           0x6700
#define SW_SECURITY_NOT_SATISFIED 0x6982
#define SW_CONDITIONS_NOT_SATISFIED 0x6985
#define SW_WRONG_DATA             0x6A80
#define SW_FUNC_NOT_SUPPORTED     0x6A81
#define SW_FILE_NOT_FOUND         0x6A82
#define SW_RECORD_NOT_FOUND       0x6A83
#define SW_WRONG_P1P2             0x6A86
#define SW_INCORRECT_P1P2         0x6B00
#define SW_WRONG_INS              0x6D00
#define SW_CLA_NOT_SUPPORTED      0x6E00
#define SW_UNKNOWN                0x6F00


// Helper macros for reading big-endian values from byte buffer
#define READ_SHORT(buf, off) \
    ((short)(((buf[(off)] & 0xFF) << 8) | (buf[(off)+1] & 0xFF)))

#define READ_INT(buf, off) \
    ((((buf[(off)] & 0xFF) << 24) | ((buf[(off)+1] & 0xFF) << 16) \
    | ((buf[(off)+2] & 0xFF) << 8) | (buf[(off)+3] & 0xFF)))

// Helper macros for writing big-endian values to byte buffer (increments off)
#define WRITE_SHORT(buf, off, val) \
    (buf)[off++] = (byte)((val) >> 8); \
    (buf)[off++] = (byte)(val)

#define WRITE_INT(buf, off, val) \
    (buf)[off++] = (byte)((val) >> 24); \
    (buf)[off++] = (byte)((val) >> 16); \
    (buf)[off++] = (byte)((val) >> 8); \
    (buf)[off++] = (byte)(val)


// APDU methods (compiler intrinsics)
// Get the APDU buffer for reading/writing data
// Maps to: apdu.getBuffer()
extern byte* apduGetBuffer(APDU apdu);

// Receive incoming data and return length
// Maps to: apdu.setIncomingAndReceive()
extern short apduReceive(APDU apdu);

// Prepare for sending response data
// Maps to: apdu.setOutgoing()
extern void apduSetOutgoing(APDU apdu);

// Set the length of outgoing data
// Maps to: apdu.setOutgoingLength(len)
extern void apduSetOutgoingLength(APDU apdu, short len);

// Send bytes from the APDU buffer
// Maps to: apdu.sendBytes(offset, len)
extern void apduSendBytes(APDU apdu, short offset, short len);

// Convenience macro: prepare and send response from buffer start
// Combines setOutgoing + setOutgoingLength + sendBytes(0, len)
#define APDU_SEND(apdu, len) do { \
    apduSetOutgoing(apdu); \
    apduSetOutgoingLength(apdu, (len)); \
    apduSendBytes(apdu, 0, (len)); \
} while(0)

// Throw an ISOException with the given status word
// This function never returns - it throws an exception
// Maps to: ISOException.throwIt(sw)
extern void throwError(short sw);

// Memory utility functions (compiler intrinsics)
// Fill a byte array with a specific byte value (5-10x faster than C loops)
// Maps to: Util.arrayFillNonAtomic(byte[] arr, short offset, short length, byte value)
extern void memset_byte(byte* dest, byte value, short length);

// Supports both arr and arr+offset syntax:
//   memset_byte(buffer, 0, 100);        // Fill buffer[0..99] with 0
//   memset_byte(buffer + 10, 0xFF, 20); // Fill buffer[10..29] with 0xFF

// Variant with explicit offset parameter (same underlying function)
extern void memset_at(byte* dest, short offset, byte value, short length);
//   memset_at(buffer, 10, 0xFF, 20);    // Fill buffer[10..29] with 0xFF

// Fill a short array with a specific short value
// Uses ArrayLogic.arrayFillGenericNonAtomic from javacardx.framework.util
extern void memset_short(short* dest, short value, short length);
//   memset_short(buffer, 0, 100);        // Fill buffer[0..99] with 0
//   memset_short(buffer + 10, 0x1234, 20); // Fill buffer[10..29] with 0x1234

// Logical right shift (zero-fill, not sign-extend)
// Use these instead of >> when you need zero-fill behavior.
// The standard >> operator always sign-extends (arithmetic shift).
extern short lshr_short(short value, short amount);
extern int lshr_int(int value, int amount);

// Unsigned comparison macro for int
// jcc has no unsigned types. XOR with 0x80000000 flips sign bit to convert
// unsigned ordering to signed ordering.
// Usage: UINT_CMP(a, >=, b)
#define UINT_CMP(a, op, b) (((a) ^ 0x80000000) op ((b) ^ 0x80000000))

// Raw sushr opcode for testing (may not work on all simulators)
extern short _raw_sushr(short value, short amount);

// Entry point - user implements this function
// apdu: the APDU object
// len: command data length (from setIncomingAndReceive)
void process(APDU apdu, short len);

#endif // JCC_H
