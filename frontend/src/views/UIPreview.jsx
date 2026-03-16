import React from 'react';
import { tokens } from '../theme/tokens';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Badge from '../components/ui/Badge';

const UIPreview = () => {
  const [modalOpen, setModalOpen] = React.useState(false);

  return (
    <div className="min-h-screen p-8 lg:p-12 space-y-16 animate-fade-up">
      {/* Header */}
      <section className="space-y-4">
        <h1 className="text-4xl font-black text-slate-900">Design System — TalkFlow</h1>
        <p className="text-lg text-slate-500 max-w-2xl">
          Core design language, components, and interactive patterns used across the TalkFlow platform.
        </p>
      </section>

      {/* Color Palette */}
      <section className="space-y-6">
        <h2 className="text-xs font-black tracking-widest text-slate-400 uppercase">01. Color Palette</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {Object.entries(tokens.colors).flatMap(([name, pack]) => 
            Object.entries(pack).map(([shade, hex]) => (
              <div key={`${name}-${shade}`} className="space-y-2">
                <div 
                  className="h-24 w-full rounded-2xl shadow-inner border border-black/5" 
                  style={{ backgroundColor: hex }}
                />
                <div>
                  <p className="text-[10px] font-black uppercase text-slate-900">{name} {shade}</p>
                  <p className="text-[10px] font-mono text-slate-400 uppercase">{hex}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Typography */}
      <section className="space-y-6">
        <h2 className="text-xs font-black tracking-widest text-slate-400 uppercase">02. Typography</h2>
        <Card className="p-8 space-y-6 bg-white/60">
          <div className="space-y-1">
            <p className="text-[10px] font-black text-blue-600 uppercase">Heading 1 / Black</p>
            <h1 className="text-4xl font-black">Design the future of agents</h1>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-black text-blue-600 uppercase">Heading 2 / Bold</p>
            <h2 className="text-2xl font-bold">Interactive Video Avatars</h2>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-black text-blue-600 uppercase">Body / Regular</p>
            <p className="text-sm text-slate-500 leading-relaxed">
              Synthesize high-quality video avatars with synchronized lipsync using our custom MuseTalk pipeline. 
              Deploy anywhere with our API-first architecture.
            </p>
          </div>
        </Card>
      </section>

      {/* Buttons */}
      <section className="space-y-6">
        <h2 className="text-xs font-black tracking-widest text-slate-400 uppercase">03. Interactive Buttons</h2>
        <Card className="p-8 bg-white/60">
          <div className="flex flex-wrap gap-4">
            <Button variant="primary">Primary Action</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="danger">Delete Object</Button>
            <Button variant="ghost">Ghost Button</Button>
            <Button variant="primary" icon="🎙️">With Icon</Button>
            <Button variant="primary" disabled>Disabled State</Button>
          </div>
        </Card>
      </section>

      {/* Inputs & Forms */}
      <section className="space-y-6">
        <h2 className="text-xs font-black tracking-widest text-slate-400 uppercase">04. Form Controls</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Card className="p-8 space-y-4 bg-white/60">
            <Input label="Avatar Name" placeholder="e.g. My AI Marcus" />
            <Input label="Email Address" defaultValue="admin@ibl.ai" />
            <Input label="Error State" error="This field is required" defaultValue="Invalid Input" />
          </Card>
          <Card className="p-8 space-y-6 bg-white/60">
            <div className="space-y-2">
              <label className="input-label">Range / Speed Slider</label>
              <input type="range" className="speed-slider" />
            </div>
            <div className="space-y-2">
              <label className="input-label">Badges & Tags</label>
              <div className="flex gap-2">
                <Badge variant="primary">Processing</Badge>
                <Badge variant="success">Completed</Badge>
                <Badge variant="danger">Failed</Badge>
                <Badge variant="warning">Queued</Badge>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Cards & Lists */}
      <section className="space-y-6">
        <h2 className="text-xs font-black tracking-widest text-slate-400 uppercase">05. Cards & Interactivity</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card interactive className="p-6 space-y-3">
            <div className="h-40 w-full rounded-xl bg-slate-100 overflow-hidden">
               <div className="h-full w-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center text-4xl">👤</div>
            </div>
            <h3 className="font-bold text-slate-800">Historical Avatar #1</h3>
            <p className="text-xs text-slate-500">Portrait 9:16 Scale</p>
          </Card>
          
          <Card className="p-6 flex flex-col justify-between">
            <div className="space-y-2">
              <Badge variant="primary">New Feature</Badge>
              <h3 className="text-lg font-bold">Voice Cloning (XTTS)</h3>
              <p className="text-xs text-slate-500 leading-normal">
                Clone any voice using just 3 seconds of audio reference. High fidelity and low latency.
              </p>
            </div>
            <Button variant="secondary" className="mt-6">Explore Voice Lab</Button>
          </Card>

          <Card className="p-6 bg-blue-600 text-white space-y-4 border-none">
            <h3 className="text-xl font-bold">Live Call Active</h3>
            <p className="text-xs opacity-80">Connected to low-latency WebRTC signaling server.</p>
            <Button variant="ghost" className="bg-white/20 text-white hover:bg-white/30 border-none w-full">Join Room</Button>
          </Card>
        </div>
      </section>

      {/* Design System Metadata */}
      <section className="pt-12 border-t border-slate-200">
        <div className="flex flex-col md:flex-row justify-between items-start gap-8">
          <div className="space-y-2">
            <p className="text-[10px] font-black text-slate-400 uppercase">Version</p>
            <p className="text-sm font-bold text-slate-900">TalkFlow v2.0 Design Handoff</p>
          </div>
          <div className="space-y-2">
            <p className="text-[10px] font-black text-slate-400 uppercase">Layout System</p>
            <p className="text-sm font-bold text-slate-900">Tailwind 4.0 + CSS Layers</p>
          </div>
          <div className="space-y-2">
            <p className="text-[10px] font-black text-slate-400 uppercase">Last Updated</p>
            <p className="text-sm font-bold text-slate-900">2026-03-16</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default UIPreview;
