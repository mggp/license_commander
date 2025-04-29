import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import ApplicationsByType from './pages/ApplicationsByType'

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/type/:type" element={<ApplicationsByType />} />
        </Routes>
      </div>
    </div>
  )
}

export default App 