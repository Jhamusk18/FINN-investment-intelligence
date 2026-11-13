export default function MiniBars({ labels = [], series = [], h = 90 }) {
  // series: [{name, values, color}]
  const all = series.flatMap((s) => s.values).filter((v) => v != null)
  if (!all.length) return null
  const max = Math.max(...all.map((v) => Math.abs(v))) || 1
  const n = labels.length
  const gw = 100 / n
  const bw = (gw * 0.7) / series.length
  return (
    <div>
      <svg viewBox={`0 0 100 ${h}`} preserveAspectRatio="none" className="w-full" style={{ height: h }}>
        {series.map((s, si) => s.values.map((v, i) => {
          if (v == null) return null
          const bh = (Math.abs(v) / max) * (h - 6)
          return <rect key={`${si}-${i}`} x={i * gw + gw * 0.15 + si * bw} y={h - bh} width={bw * 0.92} height={bh} rx="0.8" fill={v < 0 ? '#E5484D' : s.color} />
        }))}
      </svg>
      <div className="mt-1 grid text-center text-[9.5px] text-slate2" style={{ gridTemplateColumns: `repeat(${n}, 1fr)` }}>
        {labels.map((l) => <span key={l}>{l}</span>)}
      </div>
      <div className="mt-1 flex gap-3 text-[11px] text-slate2">
        {series.map((s) => <span key={s.name} className="inline-flex items-center gap-1"><span className="h-2 w-2 rounded-sm" style={{ background: s.color }} />{s.name}</span>)}
      </div>
    </div>
  )
}
