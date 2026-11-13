import { createContext, useContext, useEffect, useState } from 'react'
import { useLocal, DEFAULT_THRESHOLDS } from './store'
import { api } from './api'

const Ctx = createContext(null)
export const useApp = () => useContext(Ctx)

export function AppProvider({ children }) {
  const [thresholds, setThresholds] = useLocal('thresholds', DEFAULT_THRESHOLDS)
  const [followed, setFollowed] = useLocal('followed', null) // null = all portfolio companies
  const [saved, setSaved] = useLocal('saved', [])
  const [prefs, setPrefs] = useLocal('prefs', { density: 'comfortable', showSummaries: true })
  const [companies, setCompanies] = useState({ portfolio: [], adhoc: [] })
  const [thresholdsOpen, setThresholdsOpen] = useState(false)

  useEffect(() => { api.companies().then(setCompanies).catch(() => {}) }, [])

  const portfolio = companies.portfolio
  const followedSet = new Set(followed ?? portfolio.map((c) => c.symbol))

  return (
    <Ctx.Provider value={{
      thresholds, setThresholds, followed, setFollowed, followedSet, saved, setSaved, prefs, setPrefs,
      companies, portfolio, thresholdsOpen, setThresholdsOpen,
    }}>
      {children}
    </Ctx.Provider>
  )
}
