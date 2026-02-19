import React, { useState, useEffect } from 'react'
import { videoApi, avatarApi } from './api/client'

const Sidebar = ({ view, setView, onLogout }) => {
  const [openSections, setOpenSections] = useState({
    avatars: true,
    videos: true
  })

  const toggleSection = (section) => {
    setOpenSections((prev) => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  return (
    <aside className="glass-sidebar fixed top-0 left-0 z-10 flex h-screen w-64 flex-col overflow-y-auto p-6">
      <div
        className="mb-8 flex cursor-pointer items-center gap-2"
        onClick={() => setView('library')}
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">
          T
        </div>
        <h1 className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-lg font-bold text-transparent">
          TalkFlow
        </h1>
      </div>

      <nav className="flex-1 space-y-6">
        <div>
          <div
            onClick={() => toggleSection('avatars')}
            className="mb-3 flex cursor-pointer items-center justify-between px-2 text-xs font-semibold tracking-widest text-slate-400 uppercase transition-colors hover:text-slate-600"
          >
            <span className="flex items-center gap-2">👤 AI Avatars</span>
            <span
              className={`text-[10px] transition-transform duration-300 ${openSections.avatars ? 'rotate-0' : '-rotate-90'}`}
            >
              ▼
            </span>
          </div>
          <div
            className={`space-y-1 overflow-hidden transition-all duration-300 ${openSections.avatars ? 'max-h-40 opacity-100' : 'max-h-0 opacity-0'}`}
          >
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
            className="mb-3 flex cursor-pointer items-center justify-between px-2 text-xs font-semibold tracking-widest text-slate-400 uppercase transition-colors hover:text-slate-600"
          >
            <span className="flex items-center gap-2">📹 Video Clips</span>
            <span
              className={`text-[10px] transition-transform duration-300 ${openSections.videos ? 'rotate-0' : '-rotate-90'}`}
            >
              ▼
            </span>
          </div>
          <div
            className={`space-y-1 overflow-hidden transition-all duration-300 ${openSections.videos ? 'max-h-40 opacity-100' : 'max-h-0 opacity-0'}`}
          >
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

        <div className="mt-4 border-t border-slate-100 pt-4">
          <button
            onClick={onLogout}
            className="flex w-full items-center justify-start gap-3 px-4 py-2.5 text-xs font-bold tracking-widest text-slate-400 uppercase transition-colors hover:text-red-500"
          >
            🔌 Logout
          </button>
        </div>
      </nav>

      <div className="mt-auto border-t border-white/20 pt-6">
        <div className="glass-card bg-blue-50/30 p-4 text-[13px]">
          <p className="font-semibold text-blue-800">Integration Guide</p>
          <p className="mt-1 leading-relaxed text-slate-500">Check our API SDK and GitHub demo</p>
          <button className="mt-2 font-medium text-blue-600 hover:underline">See Guide</button>
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
    <div className="animate-in fade-in fixed inset-0 z-[100] flex bg-white duration-500">
      <div className="relative flex w-full flex-col items-center justify-center p-12 lg:w-[450px]">
        <div className="w-full max-w-[320px] space-y-10">
          <div className="space-y-2 text-center">
            <div className="mb-6 flex items-center justify-center gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-lg font-bold text-white shadow-lg shadow-blue-200">
                T
              </div>
              <h1 className="text-2xl font-black text-slate-800">TalkFlow</h1>
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              Create Your Own Agent
            </h2>
            <p className="text-sm text-slate-500">
              Supported by personalized agents. Privacy first.
            </p>
          </div>

          <div className="glass-card space-y-6 border-slate-100 bg-white/40 p-8 shadow-2xl">
            <form onSubmit={handleLogin} className="space-y-4">
              <input
                type="email"
                placeholder="Email"
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-700 shadow-sm transition-all outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <button
                type="submit"
                className="w-full rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 py-3 font-bold text-white shadow-lg shadow-blue-200 transition-all hover:shadow-blue-300 active:scale-[0.98]"
              >
                Continue
              </button>
            </form>
            <div className="relative py-4">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-100"></div>
              </div>
              <span className="relative mx-auto flex w-fit bg-white/0 px-3 text-[10px] font-bold tracking-widest text-slate-400 uppercase">
                OR
              </span>
            </div>
            <div className="space-y-3">
              <button
                onClick={onLogin}
                className="group flex w-full items-center justify-center gap-3 rounded-xl border border-slate-200 bg-white py-3 text-sm font-bold text-slate-700 shadow-sm transition-all hover:bg-slate-50"
              >
                <span className="opacity-80 grayscale transition-all group-hover:grayscale-0">
                  🍎
                </span>
                Continue with Apple
              </button>
              <button
                onClick={onLogin}
                className="group flex w-full items-center justify-center gap-3 rounded-xl border border-slate-200 bg-white py-3 text-sm font-bold text-slate-700 shadow-sm transition-all hover:bg-slate-50"
              >
                <div className="flex h-4 w-4 items-center justify-center overflow-hidden opacity-80 transition-all group-hover:opacity-100">
                  <svg viewBox="0 0 24 24" className="h-4 w-4">
                    <path
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      fill="#4285F4"
                    />
                    <path
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      fill="#34A853"
                    />
                    <path
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                      fill="#FBBC05"
                    />
                    <path
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      fill="#EA4335"
                    />
                  </svg>
                </div>
                Continue with Google
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="hidden flex-1 items-center justify-center overflow-hidden bg-slate-50 p-20 lg:flex">
        <div className="animate-in slide-in-from-right w-full max-w-4xl space-y-8 duration-700">
          <div className="glass-card relative rounded-3xl bg-white p-10 shadow-2xl">
            <h3 className="mb-8 text-xs font-bold tracking-widest text-slate-400 uppercase">
              Observe extensive user analytics
            </h3>
            <div className="mb-12 grid grid-cols-4 gap-8">
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
            <div className="flex h-48 items-end gap-2">
              {[30, 50, 40, 70, 90, 60, 40, 80, 70].map((h, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t-lg bg-blue-600 transition-all hover:scale-105"
                  style={{ height: `${h}%` }}
                ></div>
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
      <div className="animate-in fade-in zoom-in relative w-full max-w-xl overflow-hidden rounded-2xl bg-white shadow-2xl duration-200">
        <div className="flex items-center justify-between border-b border-slate-100 p-6">
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

const AvatarCreateModal = ({ isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState({ name: '', type: 'Custom', image: null })
  const [preview, setPreview] = useState(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setFormData((prev) => ({ ...prev, image: file }))
      setPreview(URL.createObjectURL(file))
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const data = new FormData()
    data.append('name', formData.name)
    data.append('type', formData.type)
    data.append('image', formData.image)
    onSave(data)
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New AI Avatar">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="mb-6 flex flex-col items-center gap-4">
          <div className="group relative h-40 w-32 cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed border-slate-300 bg-slate-100">
            {preview ? (
              <img src={preview} alt="Preview" className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full flex-col items-center justify-center text-slate-400">
                <span className="text-2xl">📸</span>
                <span className="mt-1 text-[10px] font-bold">Upload Photo</span>
              </div>
            )}
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              required
              className="absolute inset-0 cursor-pointer opacity-0"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-700">Avatar Name</label>
          <input
            required
            className="w-full rounded-lg border border-slate-200 px-4 py-2.5 outline-none"
            placeholder="e.g. Einstein"
            value={formData.name}
            onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-700">Type</label>
          <select
            className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 outline-none"
            value={formData.type}
            onChange={(e) => setFormData((prev) => ({ ...prev, type: e.target.value }))}
          >
            <option value="Modern">Modern</option>
            <option value="Historic">Historic</option>
            <option value="Custom">Custom</option>
          </select>
        </div>

        <div className="-mx-8 -mb-4 flex justify-end gap-3 border-t border-slate-100 px-8 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-200 px-6 py-2.5 text-sm font-bold text-slate-500 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!formData.image}
            className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Create Avatar
          </button>
        </div>
      </form>
    </Modal>
  )
}

const PromptFormModal = ({ isOpen, onClose, prompt, onSave, categories }) => {
  const [formData, setFormData] = useState({ title: '', category: '', description: '' })
  useEffect(() => {
    if (isOpen) setFormData(prompt || { title: '', category: '', description: '' })
  }, [isOpen, prompt])
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }
  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(formData)
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={prompt ? 'Edit Prompt' : 'Add New Prompt'}>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-700">Title</label>
          <input
            name="title"
            required
            className="w-full rounded-lg border border-slate-200 px-4 py-2.5 outline-none"
            placeholder="Enter prompt title..."
            value={formData.title}
            onChange={handleChange}
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-700">Category</label>
          <select
            name="category"
            required
            className="w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 outline-none"
            value={formData.category}
            onChange={handleChange}
          >
            <option value="">Select a category</option>
            {categories
              .filter((c) => c !== 'All')
              .map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-700">Prompt Description</label>
          <textarea
            name="description"
            required
            className="min-h-[150px] w-full resize-none rounded-lg border border-slate-200 px-4 py-3 outline-none"
            placeholder="Enter the prompt description..."
            value={formData.description}
            onChange={handleChange}
          />
        </div>
        <div className="-mx-8 -mb-4 flex justify-end gap-3 border-t border-slate-100 px-8 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-200 px-6 py-2.5 text-sm font-bold text-slate-500 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-bold text-white hover:bg-blue-700"
          >
            {' '}
            {prompt ? 'Update Prompt' : 'Add Prompt'}{' '}
          </button>
        </div>
      </form>
    </Modal>
  )
}

const PromptGalleryView = ({ onUse }) => {
  const categories = [
    'All',
    'Instructional Designer',
    'AI Professors',
    'AI TAs',
    'Students',
    'AI University Roles',
    'Course Creators',
    'Other'
  ]
  const [activeCategory, setActiveCategory] = useState('All')
  const [prompts, setPrompts] = useState([
    {
      id: 1,
      title: 'Course Introduction Video',
      category: 'Instructional Designer',
      description:
        'Create a welcoming course introduction video featuring a professor in a modern classroom setting, explaining course objectives and expectations with engaging visual elements.'
    },
    {
      id: 2,
      title: 'Interactive Learning Module',
      category: 'Instructional Designer',
      description:
        'Design a video showing students actively participating in an interactive learning session with digital tools, collaborative activities, and real-time feedback mechanisms.'
    },
    {
      id: 3,
      title: 'Assessment Explanation Video',
      category: 'Instructional Designer',
      description:
        'Create a comprehensive video explaining different assessment methods, rubrics, and grading criteria with visual examples and clear demonstrations.'
    },
    {
      id: 4,
      title: 'Learning Objectives Presentation',
      category: 'Instructional Designer',
      description:
        "Generate a video presenting SMART learning objectives with visual aids, examples, and alignment with course outcomes and Bloom's taxonomy."
    },
    {
      id: 5,
      title: 'Lecture Delivery Video',
      category: 'AI Professors',
      description:
        'Create a professional lecture video with an AI professor explaining complex concepts using visual aids, diagrams, and real-world examples in an academic setting.'
    },
    {
      id: 6,
      title: 'Research Methodology Explanation',
      category: 'AI Professors',
      description:
        'Generate a video showing research methods and techniques with step-by-step demonstrations, data analysis examples, and academic best practices.'
    },
    {
      id: 7,
      title: 'Exam Review Session',
      category: 'AI Professors',
      description:
        'Create an engaging exam review video covering key topics, sample questions, and study strategies with clear explanations and helpful tips.'
    },
    {
      id: 8,
      title: 'Academic Writing Workshop',
      category: 'AI Professors',
      description:
        'Design a video workshop on academic writing techniques, citation methods, and research paper structure with practical examples and exercises.'
    }
  ])

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPrompt, setEditingPrompt] = useState(null)
  const handleAddPrompt = () => {
    setEditingPrompt(null)
    setIsModalOpen(true)
  }
  const handleEditPrompt = (prompt) => {
    setEditingPrompt(prompt)
    setIsModalOpen(true)
  }
  const handleSavePrompt = (data) => {
    if (editingPrompt) {
      setPrompts((prev) => prev.map((p) => (p.id === editingPrompt.id ? { ...data, id: p.id } : p)))
    } else {
      setPrompts((prev) => [...prev, { ...data, id: Date.now() }])
    }
  }
  const handleDeletePrompt = (id) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      setPrompts((prev) => prev.filter((p) => p.id !== id))
    }
  }

  const filteredGroups =
    activeCategory === 'All' ? [...new Set(prompts.map((p) => p.category))] : [activeCategory]

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Prompt Gallery</h1>
        <button
          onClick={handleAddPrompt}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white shadow-lg shadow-blue-200 transition-all hover:bg-blue-700"
        >
          + Add Prompt
        </button>
      </div>
      <div className="flex flex-wrap gap-2 pb-4">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`rounded-lg px-4 py-1.5 text-xs font-bold transition-all ${activeCategory === cat ? 'bg-blue-600 text-white shadow-md' : 'bg-white/60 text-slate-500 hover:bg-white hover:text-blue-600'}`}
          >
            {cat}
          </button>
        ))}
      </div>
      <div className="space-y-12">
        {filteredGroups.map((group) => (
          <div key={group} className="space-y-6">
            <h2 className="border-l-4 border-blue-600 pl-4 text-sm font-bold tracking-widest text-slate-800 uppercase">
              {group}
            </h2>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {prompts
                .filter((p) => p.category === group)
                .map((prompt) => (
                  <PromptCard
                    key={prompt.id}
                    prompt={prompt}
                    onEdit={() => handleEditPrompt(prompt)}
                    onDelete={() => handleDeletePrompt(prompt.id)}
                    onUse={() => onUse(prompt.description)}
                  />
                ))}
            </div>
          </div>
        ))}
      </div>
      <PromptFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        prompt={editingPrompt}
        onSave={handleSavePrompt}
        categories={categories}
      />
    </div>
  )
}

const PromptCard = ({ prompt, onEdit, onDelete, onUse }) => (
  <div className="glass-card space-y-4 border-white/50 bg-white/70 p-6 shadow-sm transition-all hover:bg-white">
    <h3 className="text-sm leading-tight font-bold text-slate-800">{prompt.title}</h3>
    <p className="line-clamp-3 text-[11px] leading-relaxed text-slate-500">{prompt.description}</p>
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 pt-2">
      <button
        onClick={onEdit}
        className="text-[10px] font-bold text-slate-500 transition-colors hover:text-blue-600"
      >
        📝 Edit
      </button>
      <button
        onClick={onUse}
        className="text-[10px] font-bold text-slate-500 transition-colors hover:text-blue-600"
      >
        ▶️ Use
      </button>
      <button className="text-[10px] font-bold text-slate-500 transition-colors hover:text-blue-600">
        📄 Copy
      </button>
      <button
        onClick={onDelete}
        className="ml-auto text-[10px] font-bold text-red-400 transition-colors hover:text-red-600"
      >
        🗑️ Delete
      </button>
    </div>
  </div>
)

const ScriptsView = ({ script, setScript }) => {
  const [activeTab, setActiveTab] = useState('text')
  const [speed, setSpeed] = useState(1.0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Create Script</h1>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="glass-card overflow-hidden border-white/50 bg-white/70 shadow-sm">
            <div className="flex border-b border-slate-100/50">
              {['Text', 'Audio', 'Files'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab.toLowerCase())}
                  className={`border-b-2 px-8 py-4 text-xs font-bold transition-all ${
                    activeTab === tab.toLowerCase()
                      ? 'border-blue-600 bg-blue-50/20 text-blue-600'
                      : 'border-transparent text-slate-400 hover:text-slate-600'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            <div className="p-8">
              <div className="group relative overflow-hidden rounded-2xl border border-slate-100 bg-white/40 shadow-inner">
                <textarea
                  className="h-80 w-full resize-none bg-transparent p-6 text-[15px] leading-relaxed text-slate-700 outline-none placeholder:text-slate-300"
                  placeholder="Type your script"
                  value={script}
                  onChange={(e) => setScript(e.target.value)}
                />

                <div className="absolute right-6 bottom-6 flex items-center gap-6">
                  <button className="flex items-center gap-2 rounded-xl border border-blue-100 bg-blue-50 px-4 py-2 text-xs font-bold text-blue-600 shadow-sm transition-all hover:bg-blue-100">
                    <span>✨</span> AI Help
                  </button>
                </div>

                <div className="absolute bottom-6 left-6 flex items-center gap-2">
                  <button className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-100 bg-white text-slate-400 shadow-sm transition-all hover:border-blue-200 hover:text-blue-600">
                    <span className="text-sm">▶️</span>
                  </button>
                  <span className="text-[11px] font-bold tracking-wider text-slate-300">
                    {script.length}/3,875 AI avatars
                  </span>
                </div>
              </div>

              <div className="mt-8 space-y-6">
                <div className="group flex cursor-pointer items-center justify-between rounded-2xl border border-slate-100 bg-white/60 p-5 shadow-sm transition-all hover:border-blue-300">
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-xs font-black text-slate-400 shadow-inner group-hover:bg-blue-50">
                      Aa
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-800">Emma</p>
                      <p className="text-[11px] font-bold tracking-widest text-slate-400 uppercase">
                        English (United States)
                      </p>
                    </div>
                  </div>
                  <span className="px-2 text-slate-300 transition-colors group-hover:text-blue-400">
                    ❯
                  </span>
                </div>

                <div className="space-y-4 px-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold tracking-widest text-slate-500 uppercase">
                      Speed ({speed.toFixed(1)}x)
                    </span>
                  </div>
                  <div className="group relative flex h-1 items-center rounded-full bg-slate-100">
                    <div
                      className="absolute h-full rounded-full bg-blue-600 group-hover:bg-blue-500"
                      style={{ width: `${((speed - 0.5) / 1.5) * 100}%` }}
                    ></div>
                    <input
                      type="range"
                      min="0.5"
                      max="2.0"
                      step="0.1"
                      value={speed}
                      onChange={(e) => setSpeed(parseFloat(e.target.value))}
                      className="absolute z-10 w-full cursor-pointer opacity-0"
                    />
                    <div
                      className="pointer-events-none absolute h-4 w-4 rounded-full border-2 border-blue-600 bg-white shadow-md transition-transform group-hover:scale-110"
                      style={{ left: `calc(${((speed - 0.5) / 1.5) * 100}% - 8px)` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-card sticky top-8 border-white/50 bg-white/60 p-10 text-center shadow-sm">
            <h2 className="mb-2 text-xl font-bold text-slate-800">AI Script</h2>
            <p className="mb-10 text-[13px] leading-relaxed text-slate-500">
              By describing imagined text or audio reference, you can obtain the desired script.
            </p>
            <div className="flex aspect-[3/4] flex-col items-center justify-center space-y-4 rounded-3xl border-2 border-dashed border-slate-100 bg-slate-50/50 p-8">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-slate-100 bg-white text-3xl text-slate-200 opacity-50 shadow-sm">
                📜
              </div>
              <span className="text-center text-xs font-bold tracking-widest text-slate-300 uppercase">
                Previsualization panel
              </span>
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
  useEffect(() => {
    if (initialPrompt) setPrompt(initialPrompt)
  }, [initialPrompt])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Generate Video Clip</h1>
      <div className="grid grid-cols-1 items-start gap-8 lg:grid-cols-2">
        <div className="space-y-6">
          <div className="glass-card bg-white/60 p-6">
            <h2 className="mb-4 text-base font-bold text-slate-800">Upload Reference Image</h2>
            <div className="upload-zone min-h-[180px] border-slate-200 bg-white/40">
              <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-lg bg-slate-100">
                📸
              </div>
              <p className="mb-4 px-4 text-center text-sm font-medium text-slate-600">
                Drag & drop an image or upload a file
              </p>
              <button className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold shadow-sm transition-all hover:bg-slate-50">
                Upload File
              </button>
            </div>
          </div>
          <div className="glass-card space-y-4 bg-white/60 p-4">
            <div className="flex cursor-not-allowed items-center justify-between rounded-xl border border-slate-100 bg-white/50 p-3 opacity-80">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100">
                  🤖
                </div>
                <p className="text-sm font-bold text-slate-800">Sora 2</p>
              </div>
            </div>
            <textarea
              className="min-h-[120px] w-full resize-none rounded-xl border border-slate-200 bg-white/40 p-4 text-sm text-slate-700 outline-none"
              placeholder="Describe the video..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <button className="btn-primary w-full py-3">Generate</button>
          </div>
        </div>
        <div className="glass-card bg-white/60 p-10 text-center">
          <h2 className="mb-2 text-xl font-bold text-slate-800">AI Video Clips</h2>
          <div className="relative aspect-video overflow-hidden rounded-3xl border-4 border-white/30 bg-black shadow-2xl">
            <img
              src="/avatars/monk.jpg"
              alt="Preview"
              className="h-full w-full object-cover opacity-90"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
          </div>
        </div>
      </div>
    </div>
  )
}

const VideoPlayerModal = ({ isOpen, onClose, videoUrl, title }) => {
  if (!isOpen) return null
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div className="space-y-4">
        <div className="aspect-video overflow-hidden rounded-xl bg-black shadow-2xl">
          <video controls autoPlay className="h-full w-full">
            <source src={`http://localhost:8000${videoUrl}`} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
        <div className="flex justify-end">
          <a
            href={`http://localhost:8000${videoUrl}`}
            download
            className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-blue-200 hover:bg-blue-700"
          >
            Download Video
          </a>
        </div>
      </div>
    </Modal>
  )
}

const MyVideoClipsView = ({ setView, jobs, avatarList }) => {
  const [selectedVideo, setSelectedVideo] = useState(null)

  const displayJobs =
    jobs.length > 0
      ? jobs
      : [
          {
            id: 1,
            title: 'Demo Classroom',
            params: { avatar_id: 1 },
            status: 'completed',
            duration: '0:45',
            created_at: new Date().toISOString()
          }
        ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">My Video Clips</h1>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {displayJobs.map((job) => {
          const jobAvatarId = job.params?.avatar_id
          const avatar = avatarList.find((a) => String(a.id) === String(jobAvatarId))
          const avatarImage = avatar
            ? avatar.image_url || avatar.image
            : '/avatars/marcus_aurelius.jpg'

          return (
            <VideoClipCard
              key={job.job_id || job.id}
              onClick={() => job.status === 'completed' && setSelectedVideo(job)}
              video={{
                id: job.job_id || job.id,
                title:
                  job.status === 'completed'
                    ? `TalkFlow Video ${String(job.job_id || job.id).slice(0, 8)}`
                    : `Job ${job.status}`,
                duration: '0:10',
                time: new Date(job.created_at || Date.now()).toLocaleDateString(),
                image: jobAvatarId === 'custom' ? '/avatars/monk.jpg' : avatarImage,
                url: job.result_url,
                status: job.status
              }}
            />
          )
        })}
        <div
          onClick={() => setView('video-generate')}
          className="glass-card group flex min-h-[220px] cursor-pointer flex-col items-center justify-center border-2 border-dashed border-slate-200 bg-white/40 p-6 transition-all hover:bg-blue-50/50"
        >
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full border border-slate-300 group-hover:border-blue-300 group-hover:text-blue-600">
            +
          </div>
          <p className="text-xs font-bold text-slate-500 group-hover:text-blue-600">
            Generate Video Clip
          </p>
        </div>
      </div>

      <VideoPlayerModal
        isOpen={!!selectedVideo}
        onClose={() => setSelectedVideo(null)}
        videoUrl={selectedVideo?.result_url}
        title={selectedVideo ? `TalkFlow Video ${selectedVideo.job_id?.slice(0, 8)}` : ''}
      />
    </div>
  )
}

const VideoClipCard = ({ video, onClick }) => (
  <div
    onClick={onClick}
    className={`glass-card group cursor-pointer overflow-hidden bg-white/70 shadow-sm transition-all hover:scale-[1.02] ${video.status === 'failed' ? 'opacity-60 grayscale' : ''}`}
  >
    <div className="relative aspect-video overflow-hidden bg-slate-100">
      <img
        src={video.image.startsWith('http') ? video.image : `http://localhost:8000${video.image}`}
        alt={video.title}
        className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
      />
      <div className="absolute right-2 bottom-2 rounded bg-black/60 px-1.5 py-0.5 text-[10px] font-bold text-white">
        {' '}
        {video.duration}{' '}
      </div>
      {video.status === 'completed' && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 transition-opacity group-hover:opacity-100">
          <span className="rounded-full bg-white/90 p-2 text-blue-600 shadow-lg">▶️</span>
        </div>
      )}
      {video.status === 'processing' && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/30">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-white/30 border-t-white"></div>
        </div>
      )}
    </div>
    <div className="space-y-1 p-3">
      <h3 className="truncate text-[12px] leading-snug font-bold text-slate-800">{video.title}</h3>
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-medium tracking-tighter text-slate-400 uppercase">
          {video.time}
        </p>
        {video.status === 'failed' && (
          <span className="text-[9px] font-bold text-red-500 uppercase">Failed</span>
        )}
      </div>
    </div>
  </div>
)

const GenerateAvatarView = ({
  script,
  setScript,
  selectedAvatarId,
  setSelectedAvatarId,
  avatarList,
  setView
}) => {
  const [method, setMethod] = useState('photo')
  const [file, setFile] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [status, setStatus] = useState(null) // 'queued', 'error', 'success'

  const selectedAvatar =
    avatarList.find((a) => String(a.id) === String(selectedAvatarId)) || avatarList[0]

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setStatus(null)
    }
  }

  const handleGenerate = async () => {
    let currentFile = file

    // Use selected avatar image if no manual file is uploaded
    if (!currentFile && selectedAvatar) {
      // Create a dummy blob to satisfy MultiPart file requirement if we're using a preset
      currentFile = new File([''], 'preset_avatar.jpg', { type: 'image/jpeg' })
    }

    if (!currentFile || !script.trim()) {
      alert('Please enter a script and select an avatar/upload a photo!')
      return
    }

    setIsGenerating(true)
    setStatus('queued')

    try {
      const formData = new FormData()
      let result

      if (method === 'photo') {
        formData.append('avatar_id', selectedAvatarId)
        formData.append('avatar_image', currentFile)
        formData.append('text', script)
        // If it's a preset avatar, we should ideally tell the backend which one,
        // but for now, the backend stubs just use the uploaded image.
        result = await videoApi.generateTextToVideo(formData)
      } else if (method === 'audio') {
        formData.append('avatar_id', selectedAvatarId)
        formData.append('avatar_image', currentFile)
        formData.append('audio_file', file)
        result = await videoApi.generateAudioToVideo(formData)
      } else if (method === 'video') {
        formData.append('avatar_id', selectedAvatarId)
        formData.append('reference_video', file)
        result = await videoApi.generateVideoToVideo(formData)
      }

      console.log('Generation started:', result)
      setStatus('success')
      setTimeout(() => setView('video-library'), 2000)
    } catch (error) {
      console.error('Generation failed:', error)
      setStatus('error')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight text-slate-800">Generate AI Avatar</h1>
        {status === 'success' && (
          <div className="animate-pulse rounded-xl bg-emerald-100 px-4 py-2 text-sm font-bold text-emerald-700">
            ✅ Job Queued Successfully!
          </div>
        )}
        {status === 'error' && (
          <div className="rounded-xl bg-red-100 px-4 py-2 text-sm font-bold text-red-700">
            ❌ Error starting generation.
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 items-start gap-8 lg:grid-cols-2">
        <div className="space-y-4">
          {/* Photo Option */}
          <div
            onClick={() => {
              setMethod('photo')
              setFile(null)
            }}
            className={`glass-card cursor-pointer border-2 p-6 transition-all ${method === 'photo' ? 'border-blue-500 bg-blue-50/30' : 'border-transparent bg-white/60 hover:bg-white/80'}`}
          >
            <div className="mb-3 flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-600 shadow-sm">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-800">Start with a photo</h2>
                <p className="text-xs font-medium text-slate-500">
                  Create a talking avatar from a single static image
                </p>
              </div>
            </div>
            {method === 'photo' && (
              <div className="relative">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 cursor-pointer opacity-0"
                />
                <div
                  className={`upload-zone flex flex-col items-center justify-center border-2 border-dashed py-8 ${file ? 'border-blue-400 bg-blue-50/50' : 'border-slate-200 bg-white/40'}`}
                >
                  <p className="text-sm font-bold text-slate-600">
                    {file ? file.name : 'Upload or Drag & Drop Photo'}
                  </p>
                  <p className="mt-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                    JPG, PNG up to 10MB
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Audio Cloner Option */}
          <div
            onClick={() => {
              setMethod('audio')
              setFile(null)
            }}
            className={`glass-card cursor-pointer border-2 p-6 transition-all ${method === 'audio' ? 'border-purple-500 bg-purple-50/30' : 'border-transparent bg-white/60 hover:bg-white/80'}`}
          >
            <div className="mb-3 flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-600 shadow-sm">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-800">Audio Cloner</h2>
                <p className="text-xs font-medium text-slate-500">
                  Clone your voice from a 30s audio sample
                </p>
              </div>
            </div>
            {method === 'audio' && (
              <div className="relative">
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 cursor-pointer opacity-0"
                />
                <div
                  className={`upload-zone flex flex-col items-center justify-center border-2 border-dashed py-8 ${file ? 'border-purple-400 bg-purple-50/50' : 'border-slate-200 bg-white/40'}`}
                >
                  <p className="text-sm font-bold text-slate-600">
                    {file ? file.name : 'Upload Voice Sample'}
                  </p>
                  <p className="mt-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                    MP3, WAV, M4A
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Video Clone Option */}
          <div
            onClick={() => {
              setMethod('video')
              setFile(null)
            }}
            className={`glass-card cursor-pointer border-2 p-6 transition-all ${method === 'video' ? 'border-emerald-500 bg-emerald-50/30' : 'border-transparent bg-white/60 hover:bg-white/80'}`}
          >
            <div className="mb-3 flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 shadow-sm">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 00-2 2z"
                  />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-800">Video Clone</h2>
                <p className="text-xs font-medium text-slate-500">
                  Create a digital twin from a 1-min video
                </p>
              </div>
            </div>
            {method === 'video' && (
              <div className="relative">
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 cursor-pointer opacity-0"
                />
                <div
                  className={`upload-zone flex flex-col items-center justify-center border-2 border-dashed py-8 ${file ? 'border-emerald-400 bg-emerald-50/50' : 'border-slate-200 bg-white/40'}`}
                >
                  <p className="text-sm font-bold text-slate-600">
                    {file ? file.name : 'Upload Reference Video'}
                  </p>
                  <p className="mt-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                    MP4, MOV up to 100MB
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="glass-card sticky top-8 bg-white/60 p-8">
          <div className="group relative aspect-video overflow-hidden rounded-3xl bg-black shadow-2xl">
            <img
              src={
                selectedAvatar?.image_url || selectedAvatar?.image || '/avatars/marcus_aurelius.jpg'
              }
              alt="Preview"
              className="h-full w-full object-cover opacity-80"
            />
            {(isGenerating || status === 'queued') && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/40 text-white backdrop-blur-sm">
                <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-blue-400 border-t-white"></div>
                <p className="animate-pulse text-lg font-bold">Initializing IA Model...</p>
                <p className="mt-2 text-xs text-white/70">Uploading file and queuing task</p>
              </div>
            )}
          </div>
          <div className="mt-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-800">Script Content</h3>
              <span className="text-[10px] font-bold tracking-widest text-slate-400 uppercase">
                {script.length} characters
              </span>
            </div>
            <textarea
              value={script}
              onChange={(e) => setScript(e.target.value)}
              placeholder="Enter the text you want the avatar to speak..."
              className="h-32 w-full resize-none rounded-2xl border border-slate-200 bg-white/40 p-4 text-sm transition-all outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100"
            />
          </div>
          <div className="mt-8 flex items-center justify-between">
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-6">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold tracking-widest text-white/70 uppercase">
                  {selectedAvatar?.name || 'Awaiting Input'}
                </span>
                <span className="h-2 w-2 rounded-full bg-blue-400"></span>
              </div>
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="font-bold text-slate-800">Live Preview</h3>
            <p className="text-xs font-bold tracking-widest text-slate-400 uppercase">
              Selected: {selectedAvatar?.name || method.toUpperCase()}
            </p>
          </div>
          <button
            disabled={isGenerating || (!file && !selectedAvatarId) || !script.trim()}
            onClick={handleGenerate}
            className={`btn-primary flex items-center gap-3 rounded-2xl px-8 py-3 shadow-lg transition-all ${isGenerating || (!file && !selectedAvatarId) || !script.trim() ? 'cursor-not-allowed opacity-50 shadow-none grayscale' : 'shadow-blue-500/20 active:scale-95'}`}
          >
            {isGenerating ? 'Deploying Model...' : 'Generate Avatar'}
          </button>
        </div>
      </div>
    </div>
  )
}

const AvatarLibraryView = ({ setView, avatarList, setSelectedAvatarId, onAddAvatar }) => (
  <div className="space-y-8 px-4">
    <div className="glass-card flex flex-col items-center border-blue-200/50 bg-gradient-to-br from-blue-600/10 to-purple-600/10 p-10">
      <h1 className="mb-2 text-3xl font-bold text-slate-800">AI Video Avatar</h1>
      <p className="max-w-lg text-center text-slate-600">
        Elevate your communication with talking AI avatars
      </p>
    </div>
    <div className="flex items-center justify-between">
      <h2 className="text-2xl font-bold text-slate-800">Public Avatars</h2>
      <button onClick={onAddAvatar} className="btn-primary">
        + Create New
      </button>
    </div>
    <div className="grid grid-cols-2 gap-6 md:grid-cols-3 lg:grid-cols-4">
      {avatarList.map((avatar) => (
        <div
          key={avatar.id}
          onClick={() => {
            setSelectedAvatarId(avatar.id)
            setView('generate')
          }}
        >
          <AvatarCard
            name={avatar.name}
            type={avatar.type}
            image={avatar.image_url || avatar.image}
          />
        </div>
      ))}
    </div>
  </div>
)

const AvatarCard = ({ name, type, image, isActive }) => (
  <div
    className={`glass-card group cursor-pointer overflow-hidden border-2 transition-all hover:scale-[1.02] ${isActive ? 'border-blue-500 shadow-lg shadow-blue-200' : 'border-transparent'}`}
  >
    <div className="relative aspect-[3/4] overflow-hidden bg-slate-200">
      {image && (
        <img
          src={image}
          alt={name}
          className="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
      )}
      <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/80 p-4">
        <p className="font-medium text-white">{name}</p>
        <p className="text-sm text-white/70">{type}</p>
      </div>
    </div>
  </div>
)

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [view, setView] = useState('library')
  const [pendingVideoPrompt, setPendingVideoPrompt] = useState('')
  const [script, setScript] = useState('')
  const [selectedAvatarId, setSelectedAvatarId] = useState(1)
  const [jobs, setJobs] = useState([])
  const [avatars, setAvatars] = useState([])
  const [isAvatarModalOpen, setIsAvatarModalOpen] = useState(false)

  const fetchAvatars = async () => {
    try {
      const data = await avatarApi.listAvatars()
      setAvatars(data)
    } catch (error) {
      console.error('Failed to fetch avatars:', error)
    }
  }

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await videoApi.listJobs()
        setJobs(data)
      } catch (error) {
        console.error('Failed to fetch jobs:', error)
      }
    }
    if (isAuthenticated) {
      fetchJobs()
      fetchAvatars()
      const interval = setInterval(fetchJobs, 10000) // Poll every 10s
      return () => clearInterval(interval)
    }
  }, [isAuthenticated, view])

  const handleCreateAvatar = async (formData) => {
    try {
      await avatarApi.createAvatar(formData)
      fetchAvatars()
    } catch (error) {
      console.error('Failed to create avatar:', error)
    }
  }

  const handleUsePrompt = (promptText) => {
    setPendingVideoPrompt(promptText)
    setScript(promptText)
    setView('generate')
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setView('library')
  }

  if (!isAuthenticated) return <LoginPage onLogin={() => setIsAuthenticated(true)} />

  return (
    <div className="flex min-h-screen bg-slate-50/50">
      <Sidebar view={view} setView={setView} onLogout={handleLogout} />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          {view === 'library' && (
            <AvatarLibraryView
              avatarList={avatars}
              setSelectedAvatarId={setSelectedAvatarId}
              setView={setView}
              onAddAvatar={() => setIsAvatarModalOpen(true)}
            />
          )}
          {view === 'generate' && (
            <GenerateAvatarView
              script={script}
              setScript={setScript}
              selectedAvatarId={selectedAvatarId}
              setSelectedAvatarId={setSelectedAvatarId}
              avatarList={avatars}
              setView={setView}
            />
          )}
          {view === 'scripts' && <ScriptsView script={script} setScript={setScript} />}
          {view === 'video-generate' && (
            <VideoClipGenerateView initialPrompt={pendingVideoPrompt} />
          )}
          {view === 'video-library' && (
            <MyVideoClipsView setView={setView} jobs={jobs} avatarList={avatars} />
          )}
          {view === 'prompts' && <PromptGalleryView onUse={handleUsePrompt} />}
        </div>
      </main>
      <AvatarCreateModal
        isOpen={isAvatarModalOpen}
        onClose={() => setIsAvatarModalOpen(false)}
        onSave={handleCreateAvatar}
      />
    </div>
  )
}

export default App
