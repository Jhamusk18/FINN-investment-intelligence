/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        forest: 'rgb(var(--c-forest) / <alpha-value>)',
        emerald: { DEFAULT: 'rgb(var(--c-emerald) / <alpha-value>)', 600: 'rgb(var(--c-emerald) / <alpha-value>)', 700: 'rgb(var(--c-emerald-700) / <alpha-value>)' },
        mint: 'rgb(var(--c-mint) / <alpha-value>)',
        offwhite: 'rgb(var(--c-offwhite) / <alpha-value>)',
        surface: 'rgb(var(--c-surface) / <alpha-value>)',
        navy: 'rgb(var(--c-navy) / <alpha-value>)',
        slate2: 'rgb(var(--c-slate) / <alpha-value>)',
        line: 'rgb(var(--c-line) / <alpha-value>)',
        hi: { bg: '#FDECEC', fg: '#C81E1E', bd: '#F5B5B5', bar: '#E5484D' },
        md: { bg: '#FFF6E0', fg: '#A35F00', bd: '#F5D58A', bar: '#F2B01E' },
        rt: { bg: '#E9F7EF', fg: '#0A7C57', bd: '#BFE6D0', bar: '#2FB57F' },
      },
      fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'] },
      boxShadow: {
        card: '0 1px 2px rgba(20,43,58,0.04), 0 4px 14px rgba(20,43,58,0.05)',
        sheet: '0 -10px 40px rgba(20,43,58,0.18)',
      },
      keyframes: {
        slideup: { from: { transform: 'translateY(100%)' }, to: { transform: 'translateY(0)' } },
        fadein: { from: { opacity: 0 }, to: { opacity: 1 } },
        pulseDot: { '0%,100%': { opacity: 0.35 }, '50%': { opacity: 1 } },
      },
      animation: {
        slideup: 'slideup 280ms cubic-bezier(.2,.8,.2,1)',
        fadein: 'fadein 200ms ease-out',
        pulsedot: 'pulseDot 1.2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
