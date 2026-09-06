import { ARCHITECTURE_STAGES } from '../data/content.js'

export default function Architecture() {
  return (
    <section className="section">
      <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr]">
        <div>
          <h2 className="section-heading">Signal path</h2>
          <p className="section-sub">
            A compact view of what happens between a raw recording and a scored transcript,
            without exposing implementation detail that belongs in the repo, not the UI.
          </p>
        </div>

        <div className="flex flex-col items-stretch">
          {ARCHITECTURE_STAGES.map((stage, i) => (
            <div key={stage} className="flex flex-col items-center">
              <div className="w-full rounded-lg border border-hairline/70 bg-panel px-5 py-3 text-center text-[13.5px] text-ivory sm:w-80">
                {stage}
              </div>
              {i < ARCHITECTURE_STAGES.length - 1 && (
                <div className="h-6 w-px bg-hairline" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
