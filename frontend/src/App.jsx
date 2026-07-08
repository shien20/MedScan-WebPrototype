import { useState } from "react"
import Navbar from "./components/Navbar"
import Home from "./pages/Home"
import Analysis from "./pages/Analysis"
import About from "./pages/About"
import "./App.css"

export default function App() {
  const [page, setPage] = useState("home")

  const navigate = (p) => {
    setPage(p)
    window.scrollTo(0, 0)
  }

  return (
    <div className="app-root">
      <Navbar currentPage={page} navigate={navigate} />
      {page === "home"     && <Home     navigate={navigate} />}
      {page === "analysis" && <Analysis navigate={navigate} />}
      {page === "about"    && <About    navigate={navigate} />}
    </div>
  )
}
