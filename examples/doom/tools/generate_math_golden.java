/**
 * Generate golden data for FixedMul tests.
 * Uses JDOOM's 64-bit FixedMul implementation as reference.
 *
 * Compile: javac generate_math_golden.java
 * Run: java generate_math_golden
 */
public class generate_math_golden {

    // JDOOM's FixedMul - uses 64-bit intermediate
    public static int FixedMul(int a, int b) {
        return (int) (((long) a * (long) b) >> 16);
    }

    public static void main(String[] args) {
        System.out.println("FixedMul Golden Test Cases:");
        System.out.println("===========================");
        System.out.println();

        // Test cases: [a, b, expected]
        int[][] testCases = {
            // Existing cases (verify they're correct)
            {65536, 65536},           // 1.0 * 1.0 = 1.0
            {131072, 196608},         // 2.0 * 3.0 = 6.0
            {32768, 32768},           // 0.5 * 0.5 = 0.25
            {-65536, 65536},          // -1.0 * 1.0 = -1.0
            {0, 65536},               // 0 * 1.0 = 0
            {6553600, 6553600},       // 100.0 * 100.0 = 10000.0
            {12345678, 87654321},     // Large * large (overflow test)

            // Sprite projection (THE FAILING CASE)
            {1048576, 5958},          // radius (16 << 16) * xscale
            {16777216, 5958},         // tx (256 << 16) * xscale

            // Large al * large bl (tests 8-bit split)
            {65535, 65535},           // max al * max bl
            {65536, 65535},           // 1.0 * 0.9999
            {65535, 65536},           // 0.9999 * 1.0
            {0x0000FFFF, 0x0000FFFF}, // Pure fractional parts

            // Large values where naive 32-bit overflows
            {2097152, 65536},         // 32 << 16 * 1.0
            {100663296, 5958},        // 1536 << 16 * xscale (large tx)
            {0x7FFF0000, 2},          // Large integer part * small
            {0x00010000, 0x7FFF0000}, // 1.0 * large

            // Sign edge cases
            {-1048576, 5958},         // -radius * xscale
            {1048576, -5958},         // radius * -xscale
            {-1048576, -5958},        // -radius * -xscale
            {-16777216, 5958},        // -tx * xscale
            {-65536, -65536},         // -1.0 * -1.0

            // Boundary values
            {0x7FFFFFFF, 1},          // INT_MAX * tiny
            {1, 0x7FFFFFFF},          // tiny * INT_MAX
            {0x80000000, 1},          // INT_MIN * 1 (signed)
            {0x40000000, 2},          // Large * 2

            // Mixed high/low bits
            {0x12340000, 0x00005678}, // High a * low b
            {0x00001234, 0x56780000}, // Low a * high b
            {0x12345678, 0x87654321}, // Both mixed

            // Values from actual sprite rendering
            {23068672, 65536},        // tz = 352 << 16, sin = 1.0
            {1048576, 5974},          // radius * xscale (variant)
        };

        System.out.println("  \"fixedmul\": [");
        for (int i = 0; i < testCases.length; i++) {
            int a = testCases[i][0];
            int b = testCases[i][1];
            int result = FixedMul(a, b);

            String comma = (i < testCases.length - 1) ? "," : "";
            System.out.printf("    [%d, %d, %d]%s%n", a, b, result, comma);
        }
        System.out.println("  ]");

        System.out.println();
        System.out.println("Key test explanations:");
        System.out.println("- [1048576, 5958, ...]: barrel radius (16 map units) * xscale");
        System.out.println("- [16777216, 5958, ...]: barrel tx offset (256 map units) * xscale");
        System.out.println("- xscale ~5958 corresponds to distance ~351 map units");
    }
}
