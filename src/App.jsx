import Navbar from './components/Navbar.jsx'
import Hero from './components/Hero.jsx'
import Workspace from './components/Workspace.jsx'
import ModelInfo from './components/ModelInfo.jsx'
import Performance from './components/Performance.jsx'
import ErrorAnalysis from './components/ErrorAnalysis.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import Architecture from './components/Architecture.jsx'
import Footer from './components/Footer.jsx'

export default function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <Hero />
        <Workspace />
        <ModelInfo />
        <Performance />
        <ErrorAnalysis />
        <HowItWorks />
        <Architecture />
      </main>
      <Footer />
    </div>
  )
}
