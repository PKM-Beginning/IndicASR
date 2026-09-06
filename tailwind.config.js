/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#07060B',
        panel: '#100E17',
        raised: '#17141F',
        hairline: '#2A2635',
        signal: {
          DEFAULT: '#7C6CF0',
          soft: '#A79BFF',
          dim: '#463A8F'
        },
        wave: {
          DEFAULT: '#45E6D6',
          soft: '#9BF3E9'
        },
        ivory: '#F3F1F8',
        mute: '#948FA3'
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"IBM Plex Sans"', 'sans-serif']
      },
      maxWidth: {
        prose: '62ch'
      }
    }
  },
  plugins: []
}
