self.onmessage = () => {
  const CACHE_MB = 6; 
  const WINDOW_MS = 10;
  const SAMPLES   = 1000;

  const buf = new Uint8Array(CACHE_MB * 1024 * 1024);
  const idx = [];
  for (let i = 0; i < buf.length; i += 64) idx.push(i);
  idx.sort(() => Math.random() - 0.5);

  const trace = [];
  for (let s = 0; s < SAMPLES; s++) {
    const t0 = performance.now();
    let count = 0;
    while (performance.now() - t0 < WINDOW_MS) {
      for (const j of idx) buf[j] ^= 1;
      count++;
    }
    trace.push(count);
  }
  self.postMessage(trace);
};
