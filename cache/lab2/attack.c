#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <x86intrin.h>
#include <inttypes.h>

#define BUF_SIZE    (4 * 1024 * 1024)
#define L1_EVICT    (48 * 1024) 
#define L2_EVICT    (3  * 1024 * 1024)
#define THRESHOLD   200
#define WAIT_US     500

static uint8_t *buf;

static inline uint64_t tsc_load(void *p) {
    uint32_t aux;
    uint64_t t0 = __rdtscp(&aux);
    (void)*(volatile uint8_t*)p;
    uint64_t t1 = __rdtscp(&aux);
    return t1 - t0;
}

static void evict(size_t bytes) {
    for (size_t i = 0; i < bytes; i += 64) {
        buf[i]++;
    }
}

static void *map_first_page(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror("open"); return NULL; }
    size_t pg = sysconf(_SC_PAGESIZE);
    void *m = mmap(NULL, pg, PROT_READ, MAP_SHARED, fd, 0);
    close(fd);
    if (m == MAP_FAILED) { perror("mmap"); return NULL; }
    return m;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        return EXIT_FAILURE;
    }
    if (posix_memalign((void**)&buf, 4096, BUF_SIZE)) {
        perror("posix_memalign");
        return EXIT_FAILURE;
    }
    buf[0] = 0;


    volatile uint8_t *target = map_first_page(argv[1]);
    if (!target) return EXIT_FAILURE;

    printf("Monitoring \"%s\" (THRESH=%d cycles)\n\n",
           argv[1], THRESHOLD);

    while (1) {
        _mm_clflush((void*)target);
        evict(L1_EVICT);
        evict(L2_EVICT);
        usleep(WAIT_US);
        uint64_t dt = tsc_load((void*)target);

        if (dt < THRESHOLD) {
            printf("[+] access detected (%" PRIu64 " cycles)\n", dt);
            fflush(stdout);
        }
    }

    return 0;
}
