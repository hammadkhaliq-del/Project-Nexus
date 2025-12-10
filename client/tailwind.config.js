/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        github: {
          dark: '#0d1117',
          border: '#30363d',
          highlight: '#161b22',
          text: '#e6edf3',
          muted: '#7d8590',
          primary: '#2d7dd2',
          success: '#3fb950',
          danger: '#f85149',
          warning: '#d29922',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}