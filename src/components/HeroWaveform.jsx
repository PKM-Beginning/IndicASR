import { useMemo } from 'react'

const BAR_COUNT = 64

export default function HeroWaveform() {
  const bars = useMemo(
    () =>
      Array.from({ length: BAR_COUNT }, (_, i) => {
        const base = 0.25 + Math.abs(Math.sin(i * 0.35)) * 0.6
        const jitter = (i % 5) * 0.05
        return {
          height: Math.min(1, base + jitter),
          delay: (i % 12) * 0.09,
          duration: 1.6 + (i % 7) * 0.12,
          accent: i % 9 === 0
        }
      }),
    []
  )

  return (
    <div
      aria-hidden="true"
      className="mx-auto flex h-24 w-full max-w-3xl items-end justify-center gap-[3px] sm:h-28"
    >
      {bars.map((bar, i) => (
        <span
          key={i}
          className="w-[3px] flex-1 rounded-full sm:w-1"
          style={{
            height: `${bar.height * 100}%`,
            background: bar.accent
              ? 'linear-gradient(180deg, #9BF3E9, #45E6D6)'
              : 'linear-gradient(180deg, #A79BFF, #7C6CF0)',
            opacity: 0.85,
            transformOrigin: 'bottom',
            animation: `pulseBar ${bar.duration}s ease-in-out ${bar.delay}s infinite`
          }}
        />
      ))}
    </div>
  )
}
