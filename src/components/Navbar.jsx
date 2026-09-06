const LINKS = [
  { href: '#workspace', label: 'Workspace' },
  { href: '#model', label: 'Model' },
  { href: '#performance', label: 'Performance' },
  { href: '#how-it-works', label: 'How it works' }
]

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-hairline/70 bg-ink/80 backdrop-blur">
      <nav className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4 sm:px-8">
        <a href="#top" className="flex items-center gap-2.5">
          <img
  src="/favicon.svg"
  alt="IndicASR logo"
  className="h-7 w-7"
/>
          <span className="font-display text-[15px] font-medium tracking-tight text-ivory">IndicASR</span>
        </a>

        <div className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[13.5px] text-mute transition-colors hover:text-ivory"
            >
              {link.label}
            </a>
          ))}
        </div>

        <a href="#workspace" className="btn-secondary !px-4 !py-2 text-[13px]">
          Try IndicASR
        </a>
      </nav>
    </header>
  )
}
