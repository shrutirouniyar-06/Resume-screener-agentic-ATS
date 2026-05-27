import { useState, useEffect } from 'react';
import { CheckCircle, Eye, EyeOff, ExternalLink } from 'lucide-react';
import './SettingsPage.css';

const MODELS = [
  { id: 'mistralai/Mistral-7B-Instruct-v0.3',   label: 'Mistral 7B Instruct v0.3',   note: 'Recommended · fast' },
  { id: 'mistralai/Mixtral-8x7B-Instruct-v0.1', label: 'Mixtral 8x7B Instruct',       note: 'Larger · slower · more accurate' },
  { id: 'meta-llama/llama-3-8b-instruct',       label: 'Llama 3 8B Instruct',         note: 'Meta · balanced' },
  { id: 'Qwen/Qwen2.5-72B-Instruct',            label: 'Qwen 2.5 72B Instruct',       note: 'Large · highest quality' },
];

export default function SettingsPage() {
  const [token, setToken] = useState('');
  const [model, setModel] = useState(MODELS[0].id);
  const [showToken, setShowToken] = useState(false);
  const [threshold, setThreshold] = useState(75);
  const [saved, setSaved] = useState(false);

  // Persist to localStorage so the user doesn't re-enter each session
  useEffect(() => {
    setToken(localStorage.getItem('hf_token') || '');
    setModel(localStorage.getItem('hf_model') || MODELS[0].id);
    setThreshold(Number(localStorage.getItem('default_threshold') || 75));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    localStorage.setItem('hf_token', token);
    localStorage.setItem('hf_model', model);
    localStorage.setItem('default_threshold', threshold);

    // Push to backend so it takes effect without restart
    try {
      await fetch('http://localhost:5000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hf_token: token, hf_model: model }),
      });
    } catch (_) {}

    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="page">
      <div className="topbar">
        <div className="page-title">Settings</div>
      </div>
      <div className="content" style={{ maxWidth: 600 }}>
        <form onSubmit={handleSave} className="settings-form">

          <div className="settings-section">
            <div className="settings-sec-title">AI / LLM configuration</div>
            <div className="settings-sec-desc">
              Screen-U uses the HuggingFace Inference API via the OpenAI-compatible endpoint.
              Get your free token at{' '}
              <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noreferrer" className="link">
                huggingface.co/settings/tokens <ExternalLink size={11} style={{verticalAlign:'middle'}}/>
              </a>
            </div>

            <div className="field">
              <label>HuggingFace API token</label>
              <div className="token-row">
                <input
                  type={showToken ? 'text' : 'password'}
                  value={token}
                  onChange={e => setToken(e.target.value)}
                  placeholder="hf_…"
                  className="field-input"
                />
                <button type="button" className="btn" onClick={() => setShowToken(s => !s)}>
                  {showToken ? <EyeOff size={14}/> : <Eye size={14}/>}
                </button>
              </div>
              <div className="field-hint">Stored in your browser only — never sent to any server except HuggingFace.</div>
            </div>

            <div className="field">
              <label>Model</label>
              <div className="model-grid">
                {MODELS.map(m => (
                  <div key={m.id} className={`model-card${model === m.id ? ' selected' : ''}`} onClick={() => setModel(m.id)}>
                    <div className="model-label">{m.label}</div>
                    <div className="model-note">{m.note}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="settings-section">
            <div className="settings-sec-title">Screening defaults</div>
            <div className="field">
              <label>Default auto-shortlist threshold</label>
              <div className="threshold-row">
                <input type="range" min={50} max={95} step={1} value={threshold} onChange={e => setThreshold(Number(e.target.value))} style={{ flex:1 }} />
                <span className="threshold-val">{threshold}%</span>
              </div>
              <div className="field-hint">New roles are pre-configured with this threshold. Can be overridden per role.</div>
            </div>
          </div>

          <div className="settings-section">
            <div className="settings-sec-title">About Screen-U</div>
            <div className="about-grid">
              {[
                ['Version',    '1.0.0'],
                ['Backend',    'Flask + Python'],
                ['Frontend',   'React'],
                ['LLM runtime','HuggingFace Inference API'],
                ['Auth',       'None (add your own)'],
                ['Storage',    'In-memory (add DB for persistence)'],
              ].map(([k,v]) => (
                <div key={k} className="about-row">
                  <span className="about-key">{k}</span>
                  <span className="about-val">{v}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="settings-footer">
            <button type="submit" className="btn btn-primary">
              {saved ? <><CheckCircle size={14}/> Saved!</> : 'Save settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}