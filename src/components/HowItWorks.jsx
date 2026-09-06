import { Fragment } from 'react'
import { PIPELINE_STAGES } from '../data/content.js'
import { IconArrowRight } from './icons.jsx'

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="section">
      <h2 className="section-heading">How it works</h2>
      <p className="section-sub">Every clip moves through the same five stages, start to finish.</p>

      <div className="mt-10 flex flex-col items-stretch gap-0 lg:flex-row">
        {PIPELINE_STAGES.map((stage, i) => (
          <Fragment key={stage.title}>
            <div className="flex-1 rounded-xl border border-hairline/70 bg-panel p-5">
              <p className="font-display text-[15px] text-ivory">{stage.title}</p>
              <p className="mt-2 text-[13px] leading-relaxed text-mute">{stage.detail}</p>
            </div>
            {i < PIPELINE_STAGES.length - 1 && (
              <div className="flex h-8 items-center justify-center lg:h-auto lg:w-8">
                <IconArrowRight className="h-4 w-4 rotate-90 text-hairline lg:rotate-0" />
              </div>
            )}
          </Fragment>
        ))}
      </div>
    </section>
  )
}
