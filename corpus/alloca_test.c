// Test file for alloca debug info extraction
// Compile with: clang -g -S -emit-llvm -target wasm32 alloca_test.c -o alloca_test_with_dbg.ll

struct Point {
    short x;
    short y;
    char flags;
};

void test(void) {
    struct Point local_point;
    short local_array[5];
    int local_scalar;

    local_point.x = 1;
    local_point.y = 2;
    local_point.flags = 3;

    local_array[0] = 10;
    local_array[4] = 50;

    local_scalar = 100;
}
