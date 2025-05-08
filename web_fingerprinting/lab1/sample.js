(async function(){
  const btn = document.getElementById('run');
  const out = document.getElementById('results');
  const Ns = [1e3, 1e4, 1e5, 1e6, 1e7];
  btn.addEventListener('click', async ()=>{
    btn.disabled = true;
    out.textContent = 'Measuring...\n';

    const buf = new Uint8Array(10 * 1024 * 1024);
    const idx = [...buf.keys()].filter(i=>i%64===0);

    let lines = [['N','run','time_ms']];
    for(const N of Ns){
      for(let run=1; run<=10; run++){
        const t0 = performance.now();
        for(let i=0; i< N; i++){

          const j = idx[i % idx.length];
          //buf[j] ^= 1;
        }
        const dt = performance.now() - t0;
        lines.push([N, run, dt.toFixed(3)]);
        out.textContent += `N=${N}, run=${run}, ${dt.toFixed(3)} ms\n`;

        await new Promise(r=>setTimeout(r, 200));
      }
    }
    out.textContent += '\nDone. Copy & save as CSV if needed.';
    btn.disabled = false;
  });
})();
