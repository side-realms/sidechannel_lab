#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <inttypes.h>
#include <x86intrin.h>

#define THRESHOLD   200 // chech your env
#define WAIT_CYCLES 30000   // ≈100 μs

static inline uint64_t rdtscp64(void){
    unsigned aux; return __rdtscp(&aux);
}
static inline uint64_t timed_load(volatile uint8_t *p){
    _mm_mfence();
    uint64_t t0 = rdtscp64();
    (void)*p;
    _mm_mfence();
    return rdtscp64() - t0;
}
static inline void busy_wait(uint64_t cyc){
    uint64_t s = rdtscp64();
    while(rdtscp64() - s < cyc);
}
static void *map_first_page(const char *path){
    int fd = open(path, O_RDONLY);
    if(fd < 0){ perror("open"); return NULL; }
    size_t pg = sysconf(_SC_PAGESIZE);
    void *m = mmap(NULL, pg, PROT_READ, MAP_SHARED, fd, 0);
    close(fd);
    if(m == MAP_FAILED){ perror("mmap"); return NULL; }
    return m;
}

int main(int argc, char **argv){
    if(argc!=2){ fprintf(stderr,"Usage: %s <file>\n",argv[0]); return 1; }
    const char *file = argv[1];

    volatile uint8_t *addr = map_first_page(file);
    if(!addr) return 1;

    printf("Monitoring \"%s\"  (THRESH=%d cycles)\n\n", file, THRESHOLD);

    while(1){
        _mm_clflush((void*)addr);        // Flush
        busy_wait(WAIT_CYCLES);
        uint64_t dt = timed_load(addr);  // Reload
        if(dt < THRESHOLD){
            printf("[+] access detected (%" PRIu64 " cycles)\n", dt);
            fflush(stdout);
        }
    }
    return 0;
}

