export default function Footer() {
  return (
    <footer className="border-t border-hairline/70">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4 px-6 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <div>
          <p className="font-display text-[15px] text-ivory">IndicASR</p>
          <p className="mt-1 text-[13px] text-mute">Built for multilingual Indian speech AI.</p>
        </div>
        <div className="flex items-center gap-6 text-[13px] text-mute">
          <a href="#" className="hover:text-ivory">
            GitHub
          </a>
          <a href="#" className="hover:text-ivory">
            Documentation
          </a>
        </div>
      </div>
    </footer>
  )
}
