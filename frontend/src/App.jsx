import React, { useState, useEffect } from 'react'
import { videoApi } from './api/client'

const Sidebar = ({ view, setView, onLogout }) => {
  const [openSections, setOpenSections] = useState({
    avatars: true,
    videos: true
  })

  const toggleSection = (section) => {
    setOpenSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 glass-sidebar p-6 flex flex-col z-10 overflow-y-auto">
      <div className="flex items-center gap-2 mb-8 cursor-pointer" onClick={() => setView('library')}>
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">T</div>
        <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">TalkFlow</h1>
      </div>

      <nav className="flex-1 space-y-6">
        <div>
          <div
            onClick={() => toggleSection('avatars')}
            className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3 px-2 cursor-pointer hover:text-slate-600 transition-colors"
          >
            <span className="flex items-center gap-2">👤 AI Avatars</span>
            <span className={`text-[10px] transition-transform duration-300 ${openSections.avatars ? 'rotate-0' : '-rotate-90'}`}>▼</span>
          </div>
          <div className={`space-y-1 transition-all duration-300 overflow-hidden ${openSections.avatars ? 'max-h-40 opacity-100' : 'max-h-0 opacity-0'}`}>
            <button
              onClick={() => setView('generate')}
              className={`nav-item ${view === 'generate' ? 'nav-item-active' : 'nav-item-inactive'}`}
            >
              <span className="text-sm">Generate</span>
            </button>
            <button
              onClick={() => setView('library')}
              className={`nav-item ${view === 'library' ? 'nav-item-active' : 'nav-item-inactive'}`}
            >
              <span className="text-sm">My AI Avatars</span>
            </button>
            <button
              onClick={() => setView('scripts')}
              className={`nav-item ${view === 'scripts' ? 'nav-item-active' : 'nav-item-inactive'}`}
            >
              <span className="text-sm">Scripts</span>
            </button>
          </div>
        </div>

        <div>
          <div
            onClick={() => toggleSection('videos')}
            className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3 px-2 cursor-pointer hover:text-slate-600 transition-colors"
          >
            <span className="flex items-center gap-2">📹 Video Clips</span>
            <span className={`text-[10px] transition-transform duration-300 ${openSections.videos ? 'rotate-0' : '-rotate-90'}`}>▼</span>
          </div>
          <div className={`space-y-1 transition-all duration-300 overflow-hidden ${openSections.videos ? 'max-h-40 opacity-100' : 'max-h-0 opacity-0'}`}>
            <button
              onClick={() => setView('video-generate')}
              className={`nav-item ${view === 'video-generate' ? 'nav-item-active' : 'nav-item-inactive'}`}
            >
              <span className="text-sm">Generate</span>
            </button>
            <button
              onClick={() => setView('video-library')}
              className={`nav-item ${view === 'video-library' ? 'nav-item-active' : 'nav-item-inactive'}`}
            >
              <span className="text-sm">My Video Clips</span>
            </button>
            <button
              onClick={() => setView('prompts')}
              className={`nav-item ${view === 'prompts' ? 'nav-item-active' : 'nav-item-inactive'}`}
            >
              <span className="text-sm">Prompts</span>
            </button>
          </div>
        </div>

        <div className="pt-4 mt-4 border-t border-slate-100">
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-start gap-3 px-4 py-2.5 text-xs font-bold text-slate-400 uppercase tracking-widest hover:text-red-500 transition-colors"
          >
            🔌 Logout
          </button>
        </div>
      </nav>

      <div className="mt-auto pt-6 border-t border-white/20">
        <div className="glass-card p-4 text-[13px] bg-blue-50/30">
          <p className="font-semibold text-blue-800">Integration Guide</p>
          <p className="text-slate-500 mt-1 leading-relaxed">Check our API SDK and GitHub demo</p>
          <button className="mt-2 text-blue-600 font-medium hover:underline">See Guide</button>
        </div>
      </div>
    </aside>
  )
}

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('')

  const handleLogin = (e) => {
    e.preventDefault()
    onLogin()
  }

  return (
    <div className="fixed inset-0 flex bg-white z-[100] animate-in fade-in duration-500">
      <div className="w-full lg:w-[450px] p-12 flex flex-col justify-center items-center relative">
        <div className="w-full max-w-[320px] space-y-10">
          <div className="text-center space-y-2">
            <div className="flex justify-center items-center gap-2 mb-6">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-blue-200">T</div>
              <h1 className="text-2xl font-black text-slate-800">TalkFlow</h1>
            </div>
            <h2 className="text-3xl font-bold text-slate-900 tracking-tight">Create Your Own Agent</h2>
            <p className="text-slate-500 text-sm">Supported by personalized agents. Privacy first.</p>
          </div>

          <div className="glass-card p-8 bg-white/40 border-slate-100 shadow-2xl space-y-6">
            <form onSubmit={handleLogin} className="space-y-4">
              <input
                type="email"
                placeholder="Email"
                className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none text-slate-700 transition-all shadow-sm"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <button type="submit" className="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-bold shadow-lg shadow-blue-200 hover:shadow-blue-300 transition-all active:scale-[0.98]">
                Continue
              </button>
            </form>
            <div className="relative py-4">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-100"></div></div>
              <span className="relative px-3 bg-white/0 text-[10px] uppercase font-bold text-slate-400 tracking-widest mx-auto flex w-fit">OR</span>
            </div>
            <div className="space-y-3">
              <button onClick={onLogin} className="w-full py-3 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 flex items-center justify-center gap-3 hover:bg-slate-50 transition-all shadow-sm group">
                <span className="grayscale group-hover:grayscale-0 transition-all opacity-80">🍎</span>
                Continue with Apple
              </button>
              <button onClick={onLogin} className="w-full py-3 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 flex items-center justify-center gap-3 hover:bg-slate-50 transition-all shadow-sm group">
                <div className="w-4 h-4 overflow-hidden flex items-center justify-center opacity-80 group-hover:opacity-100 transition-all">
                  <svg viewBox="0 0 24 24" className="w-4 h-4"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" /><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" /><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05" /><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" /></svg>
                </div>
                Continue with Google
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="hidden lg:flex flex-1 bg-slate-50 items-center justify-center p-20 overflow-hidden">
        <div className="w-full max-w-4xl space-y-8 animate-in slide-in-from-right duration-700">
          <div className="glass-card p-10 bg-white shadow-2xl rounded-3xl relative">
            <h3 className="text-slate-400 text-xs font-bold uppercase mb-8 tracking-widest">Observe extensive user analytics</h3>
            <div className="grid grid-cols-4 gap-8 mb-12">
              <div className="space-y-1">
                <p className="text-[10px] font-bold text-slate-400">UNIQUE USERS</p>
                <p className="text-2xl font-black text-slate-800">686</p>
                <p className="text-[10px] font-bold text-blue-500">↓ 23% vs last month</p>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] font-bold text-slate-400">NEW USERS</p>
                <p className="text-2xl font-black text-slate-800">87</p>
                <p className="text-[10px] font-bold text-blue-500">↓ 49% vs last month</p>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] font-bold text-slate-400">PLATFORM USERS</p>
                <p className="text-2xl font-black text-slate-800">8,957</p>
                <p className="text-[10px] font-bold text-blue-500">↑ 73% vs last month</p>
              </div>
              <div className="space-y-1">
                <p className="text-[10px] font-bold text-slate-400">VETERAN USERS</p>
                <p className="text-2xl font-black text-slate-800">619</p>
                <p className="text-[10px] font-bold text-purple-500">↑ 51% vs last month</p>
              </div>
            </div>
            <div className="h-48 flex items-end gap-2">
              {[30, 50, 40, 70, 90, 60, 40, 80, 70].map((h, i) => (
                <div key={i} className="flex-1 bg-blue-600 rounded-t-lg transition-all hover:scale-105" style={{ height: `${h}%` }}></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const Modal = ({ children, isOpen, onClose, title }) => {
  if (!isOpen) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative w-full max-w-xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="flex items-center justify-between p-6 border-b border-slate-100">
          <h2 className="text-xl font-bold text-slate-800">{title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <span className="text-sm font-bold opacity-60">✕</span>
          </button>
        </div>
        <div className="p-8">{children}</div>
      </div>
    </div>
  )
}

const PromptFormModal = ({ isOpen, onClose, prompt, onSave, categories }) => {
  const [formData, setFormData] = useState({ title: '', category: '', description: '' })
  useEffect(() => { if (isOpen) setFormData(prompt || { title: '', category: '', description: '' }) }, [isOpen, prompt])
  const handleChange = (e) => { const { name, value } = e.target; setFormData(prev => ({ ...prev, [name]: value })) }
  const handleSubmit = (e) => { e.preventDefault(); onSave(formData); onClose() }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={prompt ? 'Edit Prompt' : 'Add New Prompt'}>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-700">Title</label>
          <input name="title" required className="w-full px-4 py-2.5 border border-slate-200 rounded-lg outline-none" placeholder="Enter prompt title..." value={formData.title} onChange={handleChange} />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-700">Category</label>
          <select name="category" required className="w-full px-4 py-2.5 border border-slate-200 rounded-lg outline-none bg-white" value={formData.category} onChange={handleChange}>
            <option value="">Select a category</option>
            {categories.filter(c => c !== 'All').map(cat => (<option key={cat} value={cat}>{cat}</option>))}
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-700">Prompt Description</label>
          <textarea name="description" required className="w-full px-4 py-3 border border-slate-200 rounded-lg outline-none min-h-[150px] resize-none" placeholder="Enter the prompt description..." value={formData.description} onChange={handleChange} />
        </div>
        <div className="pt-4 flex gap-3 justify-end border-t border-slate-100 -mx-8 px-8 -mb-4">
          <button type="button" onClick={onClose} className="px-6 py-2.5 rounded-lg text-sm font-bold text-slate-500 border border-slate-200 hover:bg-slate-50">Cancel</button>
          <button type="submit" className="px-6 py-2.5 rounded-lg text-sm font-bold text-white bg-blue-600 hover:bg-blue-700"> {prompt ? 'Update Prompt' : 'Add Prompt'} </button>
        </div>
      </form>
    </Modal>
  )
}

const PromptGalleryView = ({ onUse }) => {
  const categories = ['All', 'Instructional Designer', 'AI Professors', 'AI TAs', 'Students', 'AI University Roles', 'Course Creators', 'Other']
  const [activeCategory, setActiveCategory] = useState('All')
  const [prompts, setPrompts] = useState([
    { id: 1, title: 'Course Introduction Video', category: 'Instructional Designer', description: 'Create a welcoming course introduction video featuring a professor in a modern classroom setting, explaining course objectives and expectations with engaging visual elements.' },
    { id: 2, title: 'Interactive Learning Module', category: 'Instructional Designer', description: 'Design a video showing students actively participating in an interactive learning session with digital tools, collaborative activities, and real-time feedback mechanisms.' },
    { id: 3, title: 'Assessment Explanation Video', category: 'Instructional Designer', description: 'Create a comprehensive video explaining different assessment methods, rubrics, and grading criteria with visual examples and clear demonstrations.' },
    { id: 4, title: 'Learning Objectives Presentation', category: 'Instructional Designer', description: "Generate a video presenting SMART learning objectives with visual aids, examples, and alignment with course outcomes and Bloom's taxonomy." },
    { id: 5, title: 'Lecture Delivery Video', category: 'AI Professors', description: 'Create a professional lecture video with an AI professor explaining complex concepts using visual aids, diagrams, and real-world examples in an academic setting.' },
    { id: 6, title: 'Research Methodology Explanation', category: 'AI Professors', description: 'Generate a video showing research methods and techniques with step-by-step demonstrations, data analysis examples, and academic best practices.' },
    { id: 7, title: 'Exam Review Session', category: 'AI Professors', description: 'Create an engaging exam review video covering key topics, sample questions, and study strategies with clear explanations and helpful tips.' },
    { id: 8, title: 'Academic Writing Workshop', category: 'AI Professors', description: 'Design a video workshop on academic writing techniques, citation methods, and research paper structure with practical examples and exercises.' },
  ])

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPrompt, setEditingPrompt] = useState(null)
  const handleAddPrompt = () => { setEditingPrompt(null); setIsModalOpen(true) }
  const handleEditPrompt = (prompt) => { setEditingPrompt(prompt); setIsModalOpen(true) }
  const handleSavePrompt = (data) => {
    if (editingPrompt) { setPrompts(prev => prev.map(p => p.id === editingPrompt.id ? { ...data, id: p.id } : p)) }
    else { setPrompts(prev => [...prev, { ...data, id: Date.now() }]) }
  }
  const handleDeletePrompt = (id) => { if (window.confirm('Are you sure you want to delete this prompt?')) { setPrompts(prev => prev.filter(p => p.id !== id)) } }

  const filteredGroups = activeCategory === 'All' ? [...new Set(prompts.map(p => p.category))] : [activeCategory]

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Prompt Gallery</h1>
        <button onClick={handleAddPrompt} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all">+ Add Prompt</button>
      </div>
      <div className="flex flex-wrap gap-2 pb-4">
        {categories.map(cat => (
          <button key={cat} onClick={() => setActiveCategory(cat)} className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeCategory === cat ? 'bg-blue-600 text-white shadow-md' : 'bg-white/60 text-slate-500 hover:bg-white hover:text-blue-600'}`}>{cat}</button>
        ))}
      </div>
      <div className="space-y-12">
        {filteredGroups.map(group => (
          <div key={group} className="space-y-6">
            <h2 className="text-sm font-bold text-slate-800 border-l-4 border-blue-600 pl-4 uppercase tracking-widest">{group}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {prompts.filter(p => p.category === group).map(prompt => (
                <PromptCard key={prompt.id} prompt={prompt} onEdit={() => handleEditPrompt(prompt)} onDelete={() => handleDeletePrompt(prompt.id)} onUse={() => onUse(prompt.description)} />
              ))}
            </div>
          </div>
        ))}
      </div>
      <PromptFormModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} prompt={editingPrompt} onSave={handleSavePrompt} categories={categories} />
    </div>
  )
}

const PromptCard = ({ prompt, onEdit, onDelete, onUse }) => (
  <div className="glass-card p-6 bg-white/70 hover:bg-white transition-all shadow-sm border-white/50 space-y-4">
    <h3 className="text-sm font-bold text-slate-800 leading-tight">{prompt.title}</h3>
    <p className="text-[11px] text-slate-500 leading-relaxed line-clamp-3">{prompt.description}</p>
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 pt-2">
      <button onClick={onEdit} className="text-[10px] font-bold text-slate-500 hover:text-blue-600 transition-colors">📝 Edit</button>
      <button onClick={onUse} className="text-[10px] font-bold text-slate-500 hover:text-blue-600 transition-colors">▶️ Use</button>
      <button className="text-[10px] font-bold text-slate-500 hover:text-blue-600 transition-colors">📄 Copy</button>
      <button onClick={onDelete} className="text-[10px] font-bold text-red-400 hover:text-red-600 transition-colors ml-auto">🗑️ Delete</button>
    </div>
  </div>
)

const ScriptsView = () => {
  const [activeTab, setActiveTab] = useState('text')
  const [script, setScript] = useState('')
  const [speed, setSpeed] = useState(1.0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Create Script</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card bg-white/70 overflow-hidden shadow-sm border-white/50">
            <div className="flex border-b border-slate-100/50">
              {['Text', 'Audio', 'Files'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab.toLowerCase())}
                  className={`px-8 py-4 text-xs font-bold transition-all border-b-2 ${activeTab === tab.toLowerCase()
                      ? 'text-blue-600 border-blue-600 bg-blue-50/20'
                      : 'text-slate-400 border-transparent hover:text-slate-600'
                    }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="p-8">
              <div className="relative group rounded-2xl border border-slate-100 bg-white/40 shadow-inner overflow-hidden">
                <textarea
                  className="w-full h-80 p-6 bg-transparent outline-none resize-none text-[15px] text-slate-700 placeholder:text-slate-300 leading-relaxed"
                  placeholder="Type your script"
                  value={script}
                  onChange={(e) => setScript(e.target.value)}
                />

                <div className="absolute bottom-6 right-6 flex items-center gap-6">
                  <button className="flex items-center gap-2 text-xs font-bold text-blue-600 bg-blue-50 px-4 py-2 rounded-xl border border-blue-100 hover:bg-blue-100 transition-all shadow-sm">
                    <span>✨</span> AI Help
                  </button>
                </div>

                <div className="absolute bottom-6 left-6 flex items-center gap-2">
                  <button className="w-10 h-10 rounded-full flex items-center justify-center bg-white border border-slate-100 shadow-sm text-slate-400 hover:text-blue-600 hover:border-blue-200 transition-all">
                    <span className="text-sm">▶️</span>
                  </button>
                  <span className="text-[11px] font-bold text-slate-300 tracking-wider">
                    {script.length}/3,875 AI avatars
                  </span>
                </div>
              </div>

              <div className="mt-8 space-y-6">
                <div className="flex items-center justify-between p-5 bg-white/60 border border-slate-100 rounded-2xl group cursor-pointer hover:border-blue-300 transition-all shadow-sm">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-xs font-black text-slate-400 shadow-inner group-hover:bg-blue-50">Aa</div>
                    <div>
                      <p className="text-sm font-bold text-slate-800">Emma</p>
                      <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">English (United States)</p>
                    </div>
                  </div>
                  <span className="text-slate-300 group-hover:text-blue-400 px-2 transition-colors">❯</span>
                </div>

                <div className="space-y-4 px-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Speed ({speed.toFixed(1)}x)</span>
                  </div>
                  <div className="relative h-1 bg-slate-100 rounded-full flex items-center group">
                    <div className="absolute h-full bg-blue-600 rounded-full group-hover:bg-blue-500" style={{ width: `${((speed - 0.5) / 1.5) * 100}%` }}></div>
                    <input
                      type="range" min="0.5" max="2.0" step="0.1" value={speed}
                      onChange={(e) => setSpeed(parseFloat(e.target.value))}
                      className="absolute w-full opacity-0 cursor-pointer z-10"
                    />
                    <div className="absolute w-4 h-4 bg-white border-2 border-blue-600 rounded-full shadow-md group-hover:scale-110 transition-transform pointer-events-none" style={{ left: `calc(${((speed - 0.5) / 1.5) * 100}% - 8px)` }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-card p-10 bg-white/60 text-center sticky top-8 shadow-sm border-white/50">
            <h2 className="text-xl font-bold text-slate-800 mb-2">AI Script</h2>
            <p className="text-[13px] text-slate-500 leading-relaxed mb-10">
              By describing imagined text or audio reference, you can obtain the desired script.
            </p>
            <div className="aspect-[3/4] rounded-3xl border-2 border-dashed border-slate-100 bg-slate-50/50 flex flex-col items-center justify-center p-8 space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-white border border-slate-100 shadow-sm flex items-center justify-center text-slate-200 text-3xl opacity-50">📜</div>
              <span className="text-slate-300 text-xs font-bold uppercase tracking-widest text-center">Previsualization panel</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const VideoClipGenerateView = ({ initialPrompt }) => {
  const [duration, setDuration] = useState(5)
  const [prompt, setPrompt] = useState(initialPrompt || '')
  useEffect(() => { if (initialPrompt) setPrompt(initialPrompt) }, [initialPrompt])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Generate Video Clip</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        <div className="space-y-6">
          <div className="glass-card p-6 bg-white/60">
            <h2 className="text-base font-bold text-slate-800 mb-4">Upload Reference Image</h2>
            <div className="upload-zone bg-white/40 border-slate-200 min-h-[180px]">
              <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center mb-3">📸</div>
              <p className="text-sm font-medium text-slate-600 mb-4 text-center px-4">Drag & drop an image or upload a file</p>
              <button className="bg-white border border-slate-200 px-4 py-2 rounded-lg text-sm font-semibold shadow-sm hover:bg-slate-50 transition-all">Upload File</button>
            </div>
          </div>
          <div className="glass-card p-4 bg-white/60 space-y-4">
            <div className="flex items-center justify-between p-3 bg-white/50 border border-slate-100 rounded-xl cursor-not-allowed opacity-80">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">🤖</div>
                <p className="text-sm font-bold text-slate-800">Sora 2</p>
              </div>
            </div>
            <textarea className="w-full p-4 bg-white/40 border border-slate-200 rounded-xl min-h-[120px] outline-none text-sm text-slate-700 resize-none" placeholder="Describe the video..." value={prompt} onChange={(e) => setPrompt(e.target.value)} />
            <button className="w-full btn-primary py-3">Generate</button>
          </div>
        </div>
        <div className="glass-card p-10 bg-white/60 text-center">
          <h2 className="text-xl font-bold text-slate-800 mb-2">AI Video Clips</h2>
          <div className="aspect-video rounded-3xl overflow-hidden bg-black relative shadow-2xl border-4 border-white/30">
            <img src="/avatars/monk.jpg" alt="Preview" className="w-full h-full object-cover opacity-90" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
          </div>
        </div>
      </div>
    </div>
  )
}

const MyVideoClipsView = ({ setView }) => {
  const videos = [
    { id: 1, title: 'Modern Classroom Environment', duration: '0:45', time: '2 days ago', image: '/avatars/monk.jpg' },
    { id: 2, title: 'University Library Study Area', duration: '1:12', time: '3 days ago', image: '/avatars/shakespeare.jpg' },
    { id: 3, title: 'Science Laboratory Setup', duration: '0:38', time: '5 days ago', image: '/avatars/marcus_aurelius.jpg' },
    { id: 4, title: 'Campus Outdoor Courtyard', duration: '1:05', time: '1 week ago', image: '/avatars/modern_male.png' },
    { id: 5, title: 'Conference Room Meeting Space', duration: '0:52', time: '1 week ago', image: '/avatars/monk.jpg' },
  ]
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">My Video Clips</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {videos.map(video => (
          <VideoClipCard key={video.id} video={video} />
        ))}
        <div onClick={() => setView('video-generate')} className="glass-card flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-200 bg-white/40 hover:bg-blue-50/50 transition-all cursor-pointer group min-h-[220px]">
          <div className="w-10 h-10 rounded-full border border-slate-300 flex items-center justify-center mb-3 group-hover:text-blue-600 group-hover:border-blue-300">+</div>
          <p className="text-xs font-bold text-slate-500 group-hover:text-blue-600">Generate Video Clip</p>
        </div>
      </div>
    </div>
  )
}

const VideoClipCard = ({ video }) => (
  <div className="glass-card overflow-hidden bg-white/70 group hover:scale-[1.02] transition-all cursor-pointer shadow-sm">
    <div className="aspect-video bg-slate-100 relative overflow-hidden">
      <img src={video.image} alt={video.title} className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
      <div className="absolute bottom-2 right-2 bg-black/60 px-1.5 py-0.5 rounded text-[10px] font-bold text-white"> {video.duration} </div>
    </div>
    <div className="p-3 space-y-1">
      <h3 className="text-[12px] font-bold text-slate-800 truncate leading-snug">{video.title}</h3>
      <p className="text-[10px] font-medium text-slate-400 uppercase tracking-tighter">{video.time}</p>
    </div>
  </div>
)

const GenerateAvatarView = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-slate-800">Generate AI Avatar</h1>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
      <div className="glass-card p-8 bg-white/60">
        <h2 className="text-lg font-bold text-slate-800 mb-1">Start with a photo</h2>
        <div className="upload-zone bg-white/40 border-slate-200 min-h-[200px] flex items-center justify-center">
          <p className="text-sm font-medium text-slate-600">Upload or Drag & Drop</p>
        </div>
      </div>
      <div className="glass-card p-8 bg-white/60">
        <div className="aspect-video rounded-2xl overflow-hidden bg-black relative shadow-2xl">
          <img src="/avatars/marcus_aurelius.jpg" alt="Preview" className="w-full h-full object-cover opacity-80" />
        </div>
      </div>
    </div>
  </div>
)

const AvatarLibraryView = ({ setView }) => (
  <div className="space-y-8 px-4">
    <div className="glass-card p-10 bg-gradient-to-br from-blue-600/10 to-purple-600/10 border-blue-200/50 flex flex-col items-center">
      <h1 className="text-3xl font-bold text-slate-800 mb-2">AI Video Avatar</h1>
      <p className="text-slate-600 text-center max-w-lg">Elevate your communication with talking AI avatars</p>
    </div>
    <div className="flex justify-between items-center">
      <h2 className="text-2xl font-bold text-slate-800">Public Avatars</h2>
      <button onClick={() => setView('generate')} className="btn-primary">+ Create New</button>
    </div>
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <AvatarCard name="Shakespeare" type="Historic" image="/avatars/shakespeare.jpg" />
      <AvatarCard name="Thomas Aquinas" type="Historic" image="/avatars/monk.jpg" />
      <AvatarCard name="Marcus Aurelius" type="Historic" image="/avatars/marcus_aurelius.jpg" />
      <AvatarCard name="Tech CEO" type="Modern" image="/avatars/modern_male.png" />
    </div>
  </div>
)

const AvatarCard = ({ name, type, image }) => (
  <div className="glass-card overflow-hidden group hover:scale-[1.02] transition-transform cursor-pointer">
    <div className="aspect-[3/4] bg-slate-200 relative overflow-hidden">
      {image && <img src={image} alt={name} className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />}
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 flex flex-col justify-end p-4">
        <p className="text-white font-medium">{name}</p>
        <p className="text-white/70 text-sm">{type}</p>
      </div>
    </div>
  </div>
)

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [view, setView] = useState('library')
  const [pendingVideoPrompt, setPendingVideoPrompt] = useState('')

  const handleUsePrompt = (promptText) => {
    setPendingVideoPrompt(promptText)
    setView('video-generate')
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setView('library')
  }

  if (!isAuthenticated) return <LoginPage onLogin={() => setIsAuthenticated(true)} />

  return (
    <div className="flex min-h-screen bg-slate-50/50">
      <Sidebar view={view} setView={setView} onLogout={handleLogout} />
      <main className="flex-1 ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          {view === 'library' && <AvatarLibraryView setView={setView} />}
          {view === 'generate' && <GenerateAvatarView />}
          {view === 'scripts' && <ScriptsView />}
          {view === 'video-generate' && <VideoClipGenerateView initialPrompt={pendingVideoPrompt} />}
          {view === 'video-library' && <MyVideoClipsView setView={setView} />}
          {view === 'prompts' && <PromptGalleryView onUse={handleUsePrompt} />}
        </div>
      </main>
    </div>
  )
}

export default App
