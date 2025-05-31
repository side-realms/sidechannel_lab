#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <x86intrin.h>
#include <inttypes.h>

#define THRESHOLD 300
#define WAIT_US 10000

static inline uint64_t tsc_load(void *p) {
    uint32_t aux;
    uint64_t t0 = __rdtscp(&aux);
    (void)*(volatile uint8_t *)p;
    uint64_t t1 = __rdtscp(&aux);
    return t1 - t0;
}

static inline void busy_wait(unsigned us) {
    usleep(us);
}

static void *map_offset(const char *file, off_t offset) {
    int fd = open(file, O_RDONLY);
    if (fd < 0) { perror("open"); return NULL; }
    size_t pg = sysconf(_SC_PAGESIZE);
    off_t base = offset & ~(pg - 1);
    void *m = mmap(NULL, pg, PROT_READ, MAP_PRIVATE, fd, base);
    close(fd);
    if (m == MAP_FAILED) { perror("mmap"); return NULL; }
    return (char*)m + (offset & (pg - 1));
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <lib_path> <offset_hex> <label>\n", argv[0]);
        return EXIT_FAILURE;
    }
    const char *lib = argv[1];
    off_t offset = strtoul(argv[2], NULL, 0);
    const char *label = argv[3];

    void *ptr = map_offset(lib, offset);
    if (!ptr) return EXIT_FAILURE;

    printf("Monitoring %s+0x%" PRIxPTR " (%s)\n", lib, offset, label);
    printf("Threshold = %d cycles, wait = %u µs\n\n", THRESHOLD, WAIT_US);

    while (1) {
        // Flush
        _mm_clflush(ptr);

        busy_wait(WAIT_US);

        // Reload
        uint64_t dt = tsc_load(ptr);

        if (dt < THRESHOLD) {
            printf("[+] %s accessed (@0x%" PRIxPTR ") : %3" PRIu64 " cycles\n",
                   label, offset, dt);
            fflush(stdout);
        }
    }
    return 0;
}

