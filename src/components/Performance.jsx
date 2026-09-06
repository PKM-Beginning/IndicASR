import benchmarks from '../data/benchmarks.json'

const METRICS = [
  { key: 'wer', label: 'Word Error Rate', suffix: '%' },
  { key: 'cer', label: 'Character Error Rate', suffix: '%' },
  { key: 'rtf', label: 'Real-Time Factor', suffix: 'x' }
]

// Reasonable upper bound per metric, purely to scale bar widths visually.
const SCALE_MAX = { wer: 40, cer: 20, rtf: 2 }

export default function Performance() {
  const { models, datasets, languages, updated_at } = benchmarks

  return (
    <section id="performance" className="section">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="section-heading">Benchmark results</h2>
          <p className="section-sub">
            Measured on {datasets.join(' and ')} across {languages.length} languages
            {updated_at ? ` · last updated ${updated_at}` : ''}.
          </p>
        </div>
        <span className="mt-1 inline-block w-fit rounded-full border border-hairline px-3 py-1 text-[12px] text-mute">
          {updated_at ? 'Benchmark results' : 'Awaiting evaluation run'}
        </span>
      </div>

      <div className="mt-10 space-y-10">
        {METRICS.map((metric) => (
          <div key={metric.key}>
            <p className="mb-4 text-[13.5px] font-medium text-ivory">{metric.label}</p>
            <div className="space-y-3">
              {models.map((model) => {
                const value = model.metrics[metric.key]
                const pct = value != null ? Math.min(100, (value / SCALE_MAX[metric.key]) * 100) : 0
                return (
                  <div key={model.id} className="flex items-center gap-4">
                    <span className="w-36 shrink-0 text-[13px] text-mute sm:w-44">{model.name}</span>
                    <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-raised">
                      {value != null ? (
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${pct}%`,
                            background:
                              model.id === 'indicconformer'
                                ? 'linear-gradient(90deg, #7C6CF0, #A79BFF)'
                                : 'linear-gradient(90deg, #45E6D6, #9BF3E9)'
                          }}
                        />
                      ) : (
                        <div className="h-full w-full border-y border-dashed border-hairline" />
                      )}
                    </div>
                    <span className="w-24 shrink-0 text-right text-[13px] text-mute">
                      {value != null ? `${value}${metric.suffix}` : 'pending'}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      <p className="mt-8 text-[12.5px] text-mute">
        Values are read from a benchmark JSON so they can be replaced with real evaluation
        output, or served live from a <code className="text-signal-soft">/benchmarks</code> API
        endpoint, without touching this page.
      </p>
    </section>
  )
}
