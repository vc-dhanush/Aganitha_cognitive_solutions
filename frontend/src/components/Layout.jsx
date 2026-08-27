import {
  Activity,
  Beaker,
  Box,
  ChartBar,
  CircleDot,
  Download,
  FileImage,
  FlaskConical,
  ExternalLink,
  History,
  Image,
  Layers,
  Microscope,
  Play,
  Settings,
  Shapes,
  Table2,
  Upload,
} from 'lucide-react';

export const NAV_SECTIONS = [
  {
    title: 'WORKSPACE',
    items: [
      { id: 'analysis', label: 'Analysis', icon: Microscope },
      { id: 'batch', label: 'Batch Analysis', icon: Layers },
      { id: 'history', label: 'History', icon: History },
    ],
  },
  {
    title: 'PIPELINE',
    items: [
      { id: 'input', label: 'Input', icon: Upload },
      { id: 'preprocessing', label: 'Preprocessing', icon: FlaskConical },
      { id: 'segmentation', label: 'Segmentation', icon: CircleDot },
      { id: 'morphology', label: 'Morphology', icon: Shapes },
      { id: 'tracking', label: 'Tracking', icon: Activity },
    ],
  },
  {
    title: 'RESULTS',
    items: [
      { id: 'measurements', label: 'Measurements', icon: Table2 },
      { id: 'visualizations', label: 'Visualizations', icon: ChartBar },
      { id: 'export', label: 'Export', icon: Download },
    ],
  },
  {
    title: 'SYSTEM',
    items: [
      { id: 'model', label: 'Model', icon: Box },
      { id: 'settings', label: 'Settings', icon: Settings },
      { id: 'about', label: 'About', icon: Beaker },
    ],
  },
];

export function Header({ workflowStatus, backendStatus, isDemoConfigured }) {
  const statusColor =
    workflowStatus === 'COMPLETE'
      ? 'text-emerald-400'
      : workflowStatus === 'ANALYZING'
        ? 'text-cyan-400'
        : 'text-slate-400';

  const systemLabel =
    backendStatus === 'live'
      ? isDemoConfigured
        ? 'Demo / Live'
        : 'Live'
      : isDemoConfigured
        ? 'Demo'
        : 'Offline';

  return (
    <header className="h-14 border-b border-[#243044] bg-[#0b1117]/95 backdrop-blur flex items-center justify-between px-4 shrink-0">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center">
          <Microscope className="w-5 h-5 text-teal-400" />
        </div>
        <div>
          <div className="font-semibold text-sm tracking-wide">MicroscopyAI</div>
          <div className="text-[11px] text-slate-400">Cell Analysis Platform</div>
        </div>
      </div>

      <div className={`text-xs font-mono tracking-widest uppercase ${statusColor}`}>
        {workflowStatus}
      </div>

      <div className="flex items-center gap-2 text-xs text-slate-400">
        <span className="hidden sm:inline">Documentation</span>
        <a
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
          className="p-2 rounded hover:text-teal-400"
          aria-label="GitHub"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
        <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-[#243044]">
          <span
            className={`w-2 h-2 rounded-full ${
              backendStatus === 'live' ? 'bg-emerald-400' : 'bg-orange-400'
            }`}
          />
          <span>{systemLabel}</span>
        </div>
      </div>
    </header>
  );
}

export function Sidebar({ collapsed, onToggle, activeNav, onNavChange }) {
  return (
    <aside
      className={`${collapsed ? 'w-14' : 'w-52'} shrink-0 border-r border-[#243044] bg-[#0d1520] flex flex-col transition-all`}
    >
      <div className="p-2 flex justify-end">
        <button type="button" className="btn-ghost text-xs" onClick={onToggle}>
          {collapsed ? '»' : '«'}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto px-2 pb-4 space-y-4">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title}>
            {!collapsed && (
              <div className="text-[10px] uppercase tracking-wider text-slate-500 px-2 mb-1">
                {section.title}
              </div>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                const active = activeNav === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => onNavChange(item.id)}
                    className={`w-full flex items-center gap-2 px-2 py-2 rounded text-sm ${
                      active
                        ? 'bg-teal-500/10 text-teal-300 border border-teal-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                    }`}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    {!collapsed && <span>{item.label}</span>}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}

export function Footer({ backendStatus, isDemoConfigured }) {
  const mode =
    backendStatus === 'live'
      ? isDemoConfigured
        ? 'Demo / Live'
        : 'Live'
      : isDemoConfigured
        ? 'Demo'
        : 'Local';

  return (
    <footer className="h-10 border-t border-[#243044] px-4 flex items-center justify-between text-[11px] text-slate-500 shrink-0">
      <div>
        MicroscopyAI · Computer Vision · Quantitative Cell Analysis · Python · OpenCV ·
        scikit-image · Cellpose · React
      </div>
      <div className="flex items-center gap-3">
        <span>{mode}</span>
        <a href="https://github.com" className="hover:text-teal-400">GitHub</a>
        <span>Documentation</span>
      </div>
    </footer>
  );
}

export function ProgressSteps({ steps, currentStep, isDemo }) {
  if (currentStep < 0) return null;
  return (
    <div className="panel p-3 space-y-1">
      <div className="text-[10px] uppercase tracking-wider text-slate-500 mb-2">
        {isDemo ? 'DEMO ANALYSIS' : 'Analysis Progress'}
      </div>
      {steps.map((step, index) => {
        const done = index < currentStep;
        const active = index === currentStep;
        return (
          <div key={step} className="flex items-center gap-2 text-sm">
            <span className={done ? 'text-emerald-400' : active ? 'text-cyan-400' : 'text-slate-600'}>
              {done ? '✓' : active ? '●' : '○'}
            </span>
            <span className={active ? 'text-slate-200' : 'text-slate-500'}>{step}</span>
          </div>
        );
      })}
    </div>
  );
}
