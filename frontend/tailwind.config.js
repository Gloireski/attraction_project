/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{ts,tsx}',
    './src/components/**/*.{ts,tsx}',
    './src/app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1E40AF',
        secondary: '#FBBF24',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
