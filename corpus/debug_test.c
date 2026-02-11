// Test file for debug info extraction
// Compile with: clang -g -S -emit-llvm -target wasm32 debug_test.c -o debug_test_with_dbg.ll

struct Point {
    short x;
    short y;
    char flags;
};

struct Point points[10];
short values[8];
int counter;

void test(void) {
    points[0].x = 1;
    values[0] = 2;
    counter = 3;
}