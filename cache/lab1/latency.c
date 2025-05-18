#include <stdio.h>
#include <stdint.h>
#include <x86intrin.h>
#include <stdlib.h>
#define L1_EVICT (48 * 1024)
#define L2_EVICT (3  * 1024 * 1024)
#define BUF_SIZE (4  * 1024 * 1024)

static uint8_t *buf;

static inline uint64_t tsc_load(void *p){
    uint32_t aux;
    uint64_t t0 = __rdtscp(&aux);
    (void)*(volatile uint8_t*)p;
    uint64_t t1 = __rdtscp(&aux);
    return t1 - t0;
}
static void evict(size_t bytes){
    for(size_t i=0;i<bytes;i+=64) buf[i]++;
}

int main(){
    posix_memalign((void**)&buf, 4096, BUF_SIZE);
    void *addr = &buf[0];

    /* L1 */
    (void)*(volatile uint8_t*)addr;
    uint64_t l1 = tsc_load(addr);

    /* L2 */
    evict(L1_EVICT);
    uint64_t l2 = tsc_load(addr);

    /* LLC/L3 */
    evict(L2_EVICT);
    uint64_t l3 = tsc_load(addr);

    /* DRAM */
    _mm_clflush(addr);
    uint64_t dram = tsc_load(addr);

    printf("L1  : %3lu cycles\n", l1);
    printf("L2  : %3lu cycles\n", l2);
    printf("L3  : %3lu cycles\n", l3);
    printf("DRAM: %3lu cycles\n", dram);
    return 0;
}
