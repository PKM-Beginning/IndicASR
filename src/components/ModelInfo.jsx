import { MODEL_FACTS } from '../data/content.js'

export default function ModelInfo() {
  return (
    <section id="model" className="section">
      <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr]">
        <div>
          <h2 className="section-heading">Under the hood</h2>
          <p className="section-sub">
            IndicASR runs on AI4Bharat's IndicConformer alongside an OpenAI Whisper-small
            baseline, so recognition quality can be compared directly across models rather
            than taken on faith.
          </p>
        </div>

        <dl className="divide-y divide-hairline/70 border-y border-hairline/70">
          {MODEL_FACTS.map((fact) => (
            <div key={fact.label} className="grid grid-cols-[1fr_1.2fr] gap-4 py-4 sm:grid-cols-[1fr_1.5fr]">
              <dt className="text-[13.5px] text-mute">{fact.label}</dt>
              <dd className="text-[14.5px] text-ivory">{fact.value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  )
}
