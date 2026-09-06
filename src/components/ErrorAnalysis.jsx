import { ERROR_CATEGORIES } from '../data/content.js'

export default function ErrorAnalysis() {
  return (
    <section className="section">
      <h2 className="section-heading">Error analysis</h2>
      <p className="section-sub">
        Every transcription can be broken down into how it diverges from a reference — this
        structure is ready to bind to a backend breakdown once one is connected.
      </p>

      <div className="mt-8 divide-y divide-hairline/70 border-y border-hairline/70">
        {ERROR_CATEGORIES.map((category) => (
          <div
            key={category.id}
            className="grid grid-cols-1 gap-1 py-4 sm:grid-cols-[220px_1fr_auto] sm:items-center sm:gap-6"
          >
            <p className="text-[14px] text-ivory">{category.label}</p>
            <p className="text-[13px] text-mute">{category.detail}</p>
            <span className="w-fit rounded-full border border-hairline px-2.5 py-1 text-[11.5px] text-mute">
              Awaiting backend
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}
