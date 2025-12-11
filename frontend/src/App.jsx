import { useState } from 'react'
import { HeroPattern } from './components/HeroPattern'

function App() {
  const [darkMode, setDarkMode] = useState(false)

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="bg-base-100 min-h-screen">
        <HeroPattern />
        
        {/* Navbar moderna */}
        <div className="navbar bg-primary text-primary-content shadow-xl">
          <div className="flex-1">
            <a className="btn btn-ghost text-2xl font-bold">Sentinela</a>
          </div>
          <div className="flex-none gap-4">
            <button className="btn btn-ghost">Dashboard</button>
            <button className="btn btn-ghost">Contratos</button>
            <label className="swap swap-rotate">
              <input type="checkbox" onChange={() => setDarkMode(!darkMode)} />
              <div className="swap-on">🌙</div>
              <div className="swap-off">☀️</div>
            </label>
          </div>
        </div>

        {/* Hero com call to action */}
        <div className="hero min-h-screen bg-base-200">
          <div className="hero-content text-center">
            <div className="max-w-md">
              <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Vigilância total, risco zero.
              </h1>
              <p className="py-6 text-xl">
                O sistema que acabou com rejeição de contas no TCU.
              </p>
              <button className="btn btn-primary btn-lg">Começar agora →</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App