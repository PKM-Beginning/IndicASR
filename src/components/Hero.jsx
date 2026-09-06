import HeroWaveform from './HeroWaveform.jsx'

export default function Hero() {
  return (
    <section id="top" className="relative overflow-hidden pt-20 sm:pt-28">
      <div className="mx-auto w-full max-w-4xl px-6 text-center sm:px-8">
        <span className="inline-block rounded-full border border-hairline px-3.5 py-1.5 text-[12.5px] text-mute">
          IndicConformer · Whisper-small · Hindi, Bengali, Telugu, Odia
        </span>

        <h1 className="mt-7 font-display text-[40px] font-medium leading-[1.08] tracking-tight text-ivory sm:text-6xl">
          Multilingual speech intelligence
          <br className="hidden sm:block" /> for Indian languages
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-[16px] leading-relaxed text-mute sm:text-[17px]">
          Transcribe Indian-language speech with modern multilingual ASR models, evaluate
          recognition quality, and analyze model performance.
        </p>

        <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <a href="#workspace" className="btn-primary">
            Try IndicASR
          </a>
          <a href="#performance" className="btn-secondary">
            View Performance
          </a>
        </div>
      </div>

      <div className="mt-16 sm:mt-20">
        <HeroWaveform />
      </div>
    </section>
  )
}
