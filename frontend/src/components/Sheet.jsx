import { useEffect } from 'react'
import { X } from 'lucide-react'

export default function Sheet({ open, onClose, title, right, children, footer, maxH = '88%' }) {
  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])
  if (!open) return null
  return (
    <div className="absolute inset-0 z-50 flex flex-col justify-end" role="dialog" aria-modal="true">
      <div className="absolute inset-0 bg-[#0B2A20]/45 backdrop-blur-[1px] animate-fadein" onClick={onClose} />
      <div className="relative flex flex-col rounded-t-[26px] bg-white shadow-sheet animate-slideup" style={{ maxHeight: maxH }}>
        <div className="flex justify-center pt-2.5"><div className="h-1.5 w-12 rounded-full bg-[#D5DDDA]" /></div>
        <div className="flex items-center justify-between px-5 pb-3 pt-3 border-b border-line">
          <h2 className="text-[20px] font-bold text-navy">{title}</h2>
          <div className="flex items-center gap-3">
            {right}
            <button onClick={onClose} aria-label="Close" className="grid h-8 w-8 place-items-center rounded-full border border-line bg-offwhite text-navy">
              <X size={16} />
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto no-scrollbar">{children}</div>
        {footer ? <div className="border-t border-line px-5 py-3 pb-[max(12px,env(safe-area-inset-bottom))]">{footer}</div> : null}
      </div>
    </div>
  )
}
