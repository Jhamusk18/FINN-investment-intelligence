const IN = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 })
const IN2 = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 })

export const inr = (v) => (v == null ? '—' : IN.format(v))
export const num2 = (v) => (v == null ? '—' : IN2.format(v))
export const pct = (v, d = 1) => (v == null ? '—' : `${v > 0 ? '+' : ''}${v.toFixed(d)}%`)
export const crore = (v) => (v == null ? '—' : `₹${IN.format(v)} Cr`)

export function timeAgo(iso, now = Date.now()) {
  const t = new Date(iso).getTime()
  const s = Math.max(0, (now - t) / 1000)
  if (s < 60) return 'just now'
  if (s < 3600) return `${Math.floor(s / 60)} min ago`
  if (s < 86400) return `${Math.floor(s / 3600)} hr ago`
  const d = Math.floor(s / 86400)
  if (d < 7) return `${d}d ago`
  return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

export function stamp(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' })
}

export const clamp = (v, a, b) => Math.max(a, Math.min(b, v))
