import { DEFAULT_FILTERS, CAT_LABEL } from './store'

export const WINDOWS = [['24h', 'Last 24 hours', 24], ['48h', '48 hours', 48], ['7d', '7 days', 168], ['30d', '30 days', 720], ['custom', 'Custom range', null]]

export function windowBounds(f, now = Date.now()) {
  if (f.window === 'custom') {
    const from = f.from ? new Date(f.from + 'T00:00:00+05:30').getTime() : now - 720 * 3600e3
    const to = f.to ? new Date(f.to + 'T23:59:59+05:30').getTime() : now
    return [from, to]
  }
  const h = (WINDOWS.find((w) => w[0] === f.window) || WINDOWS[0])[2]
  return [now - h * 3600e3, now + 60e3]
}

/** Single source of truth: every counter, list and label is derived from this. */
export function applyFilters(items, f, { followed, ignorePriority = false, text = '' } = {}) {
  const [from, to] = windowBounds(f)
  const comp = new Set(f.companies)
  const cats = new Set(f.categories)
  const q = text.trim().toLowerCase()
  return items.filter((i) => {
    const t = new Date(i.datetime).getTime()
    if (t < from || t > to) return false
    if (followed && !followed.has(i.symbol)) return false
    if (comp.size && !comp.has(i.symbol)) return false
    if (cats.size && !cats.has(i.category)) return false
    if (!ignorePriority && f.priority !== 'all' && i.priority !== f.priority) return false
    if (q && !`${i.symbol} ${i.company} ${i.title} ${i.summary || ''} ${i.category_label}`.toLowerCase().includes(q)) return false
    return true
  })
}

export function isDefault(f) {
  return f.priority === 'all' && !f.companies.length && f.window === DEFAULT_FILTERS.window && !f.categories.length
}

const fmtD = (s) => (s ? new Date(s + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) : '…')

export function labels(f) {
  const pr = f.priority === 'all' ? 'All' : f.priority[0].toUpperCase() + f.priority.slice(1)
  const co = !f.companies.length ? 'All Companies' : f.companies.length === 1 ? f.companies[0] : `${f.companies.length} companies`
  const tw = f.window === 'custom' ? `${fmtD(f.from)} – ${fmtD(f.to)}` : (WINDOWS.find((w) => w[0] === f.window) || WINDOWS[0])[1]
  const ca = !f.categories.length ? 'All Categories' : f.categories.length === 1 ? CAT_LABEL[f.categories[0]] : `${f.categories.length} categories`
  return { priority: `Priority: ${pr}`, companies: co, window: tw === '48 hours' || tw === '7 days' || tw === '30 days' ? `Last ${tw}` : tw, categories: ca }
}
