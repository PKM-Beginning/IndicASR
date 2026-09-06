const LIVE_BAR_COUNT = 40

export default function WaveformDisplay({ peaks, isLive, level = 0, isProcessing }) {
  if (isProcessing) {
    return (
      <div className="flex h-16 w-full items-end justify-center gap-[3px]">
        {Array.from({ length: 48 }).map((_, i) => (
          <span
            key={i}
            className="w-[3px] flex-1 rounded-full bg-signal-soft/70"
            style={{
              height: '100%',
              transformOrigin: 'bottom',
              animation: `pulseBar ${0.9 + (i % 6) * 0.08}s ease-in-out ${(i % 10) * 0.05}s infinite`
            }}
          />
        ))}
      </div>
    )
  }

  if (isLive) {
    return (
      <div className="flex h-16 w-full items-center justify-center gap-[3px]">
        {Array.from({ length: LIVE_BAR_COUNT }).map((_, i) => {
          const distance = Math.abs(i - LIVE_BAR_COUNT / 2) / (LIVE_BAR_COUNT / 2)
          const bar = Math.max(0.06, level * (1 - distance * 0.6))
          return (
            <span
              key={i}
              className="w-[3px] flex-1 rounded-full bg-wave transition-[height] duration-75"
              style={{ height: `${8 + bar * 92}%` }}
            />
          )
        })}
      </div>
    )
  }

  if (peaks && peaks.length) {
    return (
      <div className="flex h-16 w-full items-center justify-center gap-[2px]">
        {peaks.map((v, i) => (
          <span
            key={i}
            className="w-[2.5px] flex-1 rounded-full bg-signal-soft/80"
            style={{ height: `${8 + v * 92}%` }}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="flex h-16 w-full items-center justify-center gap-[3px]">
      {Array.from({ length: 40 }).map((_, i) => (
        <span key={i} className="h-[8%] w-[3px] flex-1 rounded-full bg-hairline" />
      ))}
    </div>
  )
}
