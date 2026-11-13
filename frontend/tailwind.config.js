/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        forest: '#075B43',
        emerald: { DEFAULT: '#0D9367', 600: '#0D9367', 700: '#0A7C57' },
        mint: '#E7F5EF',
        offwhite: '#F6F9F8',
        navy: '#142B3A',
        slate2: '#536273',
        line: '#E2E9E6',
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
