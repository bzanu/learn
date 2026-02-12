#include "stdio.h"
#include "string.h"
#include "stdint.h"

// 联合体所有成员共享同一块内存，大小等于最大成员
typedef union {
    int i;
    float f;
    uint8_t bytes[4];
} Data;

Data d;
int main() {
d.f = 3.14f;

printf("%x\n", d.i);           // 12345678
printf("%f\n", d.f);           // 解释同一内存为浮点数（无意义值）
printf("%x %x %x %x\n", 
       d.bytes[0], d.bytes[1], 
       d.bytes[2], d.bytes[3]); // 查看字节序：78 56 34 12（小端）


return 0;
}