import { LANGUAGES } from '../data/content.js'

export default function LanguageSelector({ value, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      {LANGUAGES.map((lang) => {
        const active = value === lang.code
        return (
          <button
            key={lang.code}
            type="button"
            onClick={() => onChange(lang.code)}
            className={`rounded-full border px-3.5 py-1.5 text-[13px] transition-colors ${
              active
                ? 'border-signal bg-signal/15 text-ivory'
                : 'border-hairline text-mute hover:border-signal-dim hover:text-ivory'
            }`}
          >
            {lang.label}
          </button>
        )
      })}
    </div>
  )
}
