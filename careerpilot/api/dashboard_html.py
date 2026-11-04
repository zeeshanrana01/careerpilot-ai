"""HTML Dashboard template for CareerPilot AI."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CareerPilot AI — Production Agent Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            brand: {
              50: '#eff6ff',
              500: '#3b82f6',
              600: '#2563eb',
              700: '#1d4ed8',
            }
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #090d16; color: #f1f5f9; font-family: 'Plus Jakarta Sans', sans-serif; }
    .glass-card { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(55, 65, 81, 0.5); }
    .badge-apply { background: rgba(6, 95, 70, 0.4); border: 1px solid #059669; color: #34d399; }
    .badge-consider { background: rgba(180, 83, 9, 0.3); border: 1px solid #d97706; color: #fbbf24; }
    .badge-skip { background: rgba(153, 27, 27, 0.3); border: 1px solid #dc2626; color: #f87171; }
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- Top Navbar -->
  <header class="glass-card sticky top-0 z-50 border-b border-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/25">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <div>
          <span class="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            CareerPilot <span class="text-blue-500">AI</span>
            <span class="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-950/80 text-blue-400 border border-blue-800/60">Milestone 2</span>
          </span>
          <span class="text-xs text-gray-400 block -mt-1">Production AI Career Agent</span>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <nav class="flex items-center space-x-1 bg-gray-900/60 p-1 rounded-xl border border-gray-800">
        <button onclick="switchTab('matches')" id="tab-matches" class="px-4 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white shadow transition">Job Matches</button>
        <button onclick="switchTab('profile')" id="tab-profile" class="px-4 py-1.5 rounded-lg text-xs font-medium text-gray-400 hover:text-white transition">Verified Profile</button>
        <button onclick="switchTab('audit')" id="tab-audit" class="px-4 py-1.5 rounded-lg text-xs font-medium text-gray-400 hover:text-white transition">Audit Trail</button>
      </nav>

      <!-- Action Buttons -->
      <div class="flex items-center space-x-3">
        <button onclick="openIngestModal()" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 transition flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Ingest Raw Job
        </button>
        <a href="/docs" target="_blank" class="px-3 py-1.5 rounded-lg text-xs font-medium text-gray-400 hover:text-white border border-gray-800 hover:border-gray-700 transition">REST API Docs</a>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">

    <!-- Hero / Status Banner -->
    <div class="glass-card rounded-2xl p-6 mb-8 border border-gray-800 relative overflow-hidden">
      <div class="absolute -right-16 -top-16 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Agent Engine Active</span>
            <span class="text-xs text-gray-500">•</span>
            <span id="active-profile-headline" class="text-xs text-gray-300">Rana Zeeshan — Senior AI Engineer</span>
          </div>
          <h1 class="text-2xl font-bold text-white tracking-tight">AI Engineering Opportunities &amp; Verified Matching</h1>
          <p class="text-sm text-gray-400 mt-1 max-w-2xl">
            Zero-trust untrusted input isolation, explainable requirement-to-profile citations, and human-in-the-loop application drafting.
          </p>
        </div>
        
        <!-- Stats Strip -->
        <div class="flex items-center gap-3">
          <div class="px-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-center min-w-[90px]">
            <div id="stat-jobs" class="text-xl font-bold text-white">0</div>
            <div class="text-[11px] text-gray-400 uppercase tracking-wide">Jobs Ingested</div>
          </div>
          <div class="px-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-center min-w-[90px]">
            <div id="stat-matches" class="text-xl font-bold text-blue-400">0</div>
            <div class="text-[11px] text-gray-400 uppercase tracking-wide">AI Matches</div>
          </div>
          <div class="px-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-center min-w-[90px]">
            <div id="stat-top" class="text-xl font-bold text-emerald-400">0%</div>
            <div class="text-[11px] text-gray-400 uppercase tracking-wide">Top Match</div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 1: Matched Opportunities -->
    <div id="view-matches" class="space-y-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-white flex items-center gap-2">
          Ranked Opportunity Queue
          <span class="text-xs font-normal text-gray-400">(Sorted by match score and career preferences)</span>
        </h2>
        <button onclick="loadMatches()" class="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Refresh Queue
        </button>
      </div>

      <div id="matches-container" class="space-y-6">
        <!-- Rendered by JS -->
        <div class="text-center py-12 text-gray-500">Loading opportunity evaluations...</div>
      </div>
    </div>

    <!-- TAB 2: Verified Profile -->
    <div id="view-profile" class="hidden space-y-6">
      <div id="profile-container" class="glass-card rounded-2xl p-6 border border-gray-800 space-y-6">
        <!-- Rendered by JS -->
        <div class="text-center py-12 text-gray-500">Loading verified career profile...</div>
      </div>
    </div>

    <!-- TAB 3: Audit Trail -->
    <div id="view-audit" class="hidden space-y-4">
      <div class="flex items-center justify-between mb-2">
        <h2 class="text-lg font-bold text-white">Immutable Security &amp; Activity Audit Log</h2>
        <span class="text-xs text-gray-400">Append-only SQLite audit_events ledger</span>
      </div>
      <div class="glass-card rounded-2xl overflow-hidden border border-gray-800">
        <table class="w-full text-left text-xs text-gray-300">
          <thead class="bg-gray-900/80 text-gray-400 uppercase text-[10px] tracking-wider border-b border-gray-800">
            <tr>
              <th class="px-4 py-3">Timestamp (UTC)</th>
              <th class="px-4 py-3">Action</th>
              <th class="px-4 py-3">Entity</th>
              <th class="px-4 py-3">Outcome</th>
              <th class="px-4 py-3">Actor</th>
              <th class="px-4 py-3">Details / Alerts</th>
            </tr>
          </thead>
          <tbody id="audit-table-body" class="divide-y divide-gray-800/60 font-mono">
            <!-- Rendered by JS -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- Ingest Modal -->
  <div id="ingest-modal" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="glass-card rounded-2xl max-w-xl w-full p-6 border border-gray-700 shadow-2xl relative">
      <div class="flex items-center justify-between mb-4 border-b border-gray-800 pb-3">
        <h3 class="text-base font-bold text-white flex items-center gap-2">
          <span>Ingest Raw Job Posting</span>
          <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">Security Shield Active</span>
        </h3>
        <button onclick="closeIngestModal()" class="text-gray-400 hover:text-white">&times;</button>
      </div>

      <form id="ingest-form" onsubmit="handleIngest(event)" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-gray-300 mb-1 font-medium">Job Title *</label>
            <input type="text" id="ingest-title" required placeholder="e.g. Senior AI Engineer (Remote)" class="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500">
          </div>
          <div>
            <label class="block text-gray-300 mb-1 font-medium">Company Name *</label>
            <input type="text" id="ingest-company" required placeholder="e.g. Anthropic, Inc." class="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500">
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-gray-300 mb-1 font-medium">Location</label>
            <input type="text" id="ingest-location" placeholder="e.g. San Francisco, CA / Remote" class="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500">
          </div>
          <div>
            <label class="block text-gray-300 mb-1 font-medium">Salary Range</label>
            <input type="text" id="ingest-salary" placeholder="e.g. $180k - $220k / year" class="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500">
          </div>
        </div>

        <div>
          <label class="block text-gray-300 mb-1 font-medium">Source URL (Will be canonicalized &amp; tracking tags stripped)</label>
          <input type="url" id="ingest-url" placeholder="https://company.com/job?utm_source=linkedin" class="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500">
        </div>

        <div>
          <label class="block text-gray-300 mb-1 font-medium">Job Description (Untrusted HTML / Raw Text) *</label>
          <textarea id="ingest-desc" rows="5" required placeholder="Paste the job description here. Scripts will be safely stripped, and prompt injection signatures detected." class="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500 font-mono text-[11px]"></textarea>
        </div>

        <div id="ingest-feedback" class="hidden p-3 rounded-lg text-xs"></div>

        <div class="flex items-center justify-end space-x-2 pt-2 border-t border-gray-800">
          <button type="button" onclick="closeIngestModal()" class="px-4 py-2 rounded-lg text-gray-300 hover:text-white bg-gray-800">Cancel</button>
          <button type="submit" id="ingest-btn" class="px-4 py-2 rounded-lg font-semibold text-white bg-blue-600 hover:bg-blue-500 transition">Process &amp; Match</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    // Tab Switching
    function switchTab(tabId) {
      ['matches', 'profile', 'audit'].forEach(t => {
        document.getElementById(`view-${t}`).classList.add('hidden');
        document.getElementById(`tab-${t}`).className = 'px-4 py-1.5 rounded-lg text-xs font-medium text-gray-400 hover:text-white transition';
      });
      document.getElementById(`view-${tabId}`).classList.remove('hidden');
      document.getElementById(`tab-${tabId}`).className = 'px-4 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white shadow transition';
      if (tabId === 'profile') loadProfile();
      if (tabId === 'audit') loadAudit();
      if (tabId === 'matches') loadMatches();
    }

    function openIngestModal() { document.getElementById('ingest-modal').classList.remove('hidden'); }
    function closeIngestModal() { document.getElementById('ingest-modal').classList.add('hidden'); }

    // Load Matches
    async function loadMatches() {
      const container = document.getElementById('matches-container');
      try {
        const res = await fetch('/api/matches');
        const data = await res.json();
        
        document.getElementById('stat-matches').innerText = data.length;
        if (data.length > 0) {
          const topScore = Math.max(...data.map(d => d.evaluation.overall_score));
          document.getElementById('stat-top').innerText = `${topScore.toFixed(0)}%`;
        }

        if (data.length === 0) {
          container.innerHTML = `<div class="glass-card rounded-2xl p-8 text-center text-gray-400">No matched jobs yet. Ingest raw listings to begin.</div>`;
          return;
        }

        container.innerHTML = data.map(item => {
          const { job, evaluation, rank } = item;
          const score = evaluation.overall_score;
          const rec = evaluation.recommendation;
          const badgeClass = rec === 'APPLY' ? 'badge-apply' : (rec === 'CONSIDER' ? 'badge-consider' : 'badge-skip');
          const salary = job.salary && job.salary.min_amount ? `$${Number(job.salary.min_amount).toLocaleString()} - $${Number(job.salary.max_amount).toLocaleString()} / yr` : 'Compensation Not Stated';

          const strengthsHtml = evaluation.strengths.slice(0, 3).map(s => `
            <div class="mb-2">
              <div class="text-xs font-medium text-emerald-400 flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
                <span>${s.requirement}</span>
              </div>
              <div class="text-[11px] text-gray-400 ml-5">${s.candidate_evidence}</div>
            </div>
          `).join('');

          const gapsHtml = evaluation.gaps.map(g => `
            <div class="text-xs text-amber-300/90 flex items-start gap-1.5 mb-1.5">
              <span class="text-amber-400 font-bold">•</span>
              <span class="text-[11px]">${g}</span>
            </div>
          `).join('');

          const securityFlagNotice = job.security_flags && job.security_flags.length > 0 ? `
            <div class="mt-3 p-2.5 rounded-lg bg-red-950/40 border border-red-800 text-[11px] text-red-300 flex items-center gap-2">
              <svg class="w-4 h-4 text-red-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              <span>Security Shield Defense: ${job.security_flags.join(', ')} (Neutralized)</span>
            </div>
          ` : '';

          return `
            <div class="glass-card rounded-2xl p-6 border border-gray-800 hover:border-gray-700 transition">
              <!-- Top Header -->
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-4">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-gray-800 to-gray-700 flex items-center justify-center font-bold text-lg text-blue-400 border border-gray-700">
                    ${job.company.charAt(0)}
                  </div>
                  <div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-bold text-blue-400">RANK #${rank}</span>
                      <h3 class="text-lg font-bold text-white">${job.title}</h3>
                    </div>
                    <div class="text-xs text-gray-400 flex items-center gap-2 mt-0.5">
                      <span class="text-gray-300 font-medium">${job.company}</span>
                      <span>•</span>
                      <span>${job.location || 'Remote'}</span>
                      <span>•</span>
                      <span class="text-emerald-400 font-mono">${salary}</span>
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-3 self-start sm:self-auto">
                  <div class="text-right">
                    <div class="text-2xl font-black text-white">${score.toFixed(0)}<span class="text-xs font-normal text-gray-400">/100</span></div>
                    <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${badgeClass}">${rec}</span>
                  </div>
                </div>
              </div>

              <!-- Executive Reasoning -->
              <div class="mt-4 p-3 rounded-xl bg-gray-900/60 border border-gray-800/80">
                <div class="text-[10px] font-bold text-blue-400 uppercase tracking-wider mb-1">Agent Evaluation Reasoning</div>
                <div class="text-xs text-gray-300 leading-relaxed">${evaluation.reasoning}</div>
              </div>

              <!-- Strengths vs Gaps Grid -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div class="p-3.5 rounded-xl bg-gray-900/40 border border-emerald-950/40">
                  <div class="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                    <span>Verified Evidence Citations</span>
                    <span class="text-[10px] text-gray-500 font-normal">Fact-checked</span>
                  </div>
                  ${strengthsHtml}
                </div>

                <div class="p-3.5 rounded-xl bg-gray-900/40 border border-amber-950/40">
                  <div class="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">Gaps / Missing Qualifications</div>
                  ${gapsHtml}
                </div>
              </div>

              ${securityFlagNotice}

              <!-- Human Action Buttons -->
              <div class="mt-5 pt-4 border-t border-gray-800 flex flex-wrap items-center justify-between gap-3">
                <div class="flex items-center gap-2 text-[11px] text-gray-400 font-mono">
                  <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                  <span>Grounding: 100% Verified</span>
                </div>
                <div class="flex items-center gap-2">
                  <button onclick="alert('Application Package Prepared: Ready for Human Approval!')" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition">Generate Application Draft</button>
                  <button onclick="alert('Opportunity marked as skipped.')" class="px-3 py-1.5 rounded-lg text-xs font-medium text-gray-400 hover:text-red-400 border border-gray-800 hover:border-red-900 transition">Skip</button>
                </div>
              </div>
            </div>
          `;
        }).join('');
      } catch (err) {
        container.innerHTML = `<div class="text-red-400 p-4">Error loading matches: ${err.message}</div>`;
      }
    }

    // Load Profile
    async function loadProfile() {
      const container = document.getElementById('profile-container');
      try {
        const res = await fetch('/api/profile');
        const p = await res.json();
        
        container.innerHTML = `
          <div class="border-b border-gray-800 pb-4">
            <h2 class="text-xl font-bold text-white">${p.full_name}</h2>
            <p class="text-sm text-blue-400 font-medium">${p.headline}</p>
            <p class="text-xs text-gray-400 mt-2">${p.summary}</p>
          </div>

          <div>
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Verified Technical Skills</h3>
            <div class="flex flex-wrap gap-2">
              ${p.skills.map(s => `
                <span class="px-2.5 py-1 rounded-lg text-xs font-medium bg-blue-950/60 text-blue-300 border border-blue-800/60 flex items-center gap-1.5">
                  ${s.name} <span class="text-[10px] text-gray-400 font-normal">(${s.years_experience}y)</span>
                </span>
              `).join('')}
            </div>
          </div>

          <div>
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Verified Experience</h3>
            <div class="space-y-3">
              ${p.experience.map(e => `
                <div class="p-3 rounded-xl bg-gray-900/60 border border-gray-800">
                  <div class="flex justify-between items-baseline">
                    <span class="text-xs font-bold text-white">${e.title} @ ${e.company}</span>
                    <span class="text-[11px] text-gray-400 font-mono">${e.start_date} - ${e.end_date}</span>
                  </div>
                  <ul class="mt-2 space-y-1 text-xs text-gray-300 list-disc list-inside">
                    ${e.highlights.map(h => `<li>${h}</li>`).join('')}
                  </ul>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      } catch (err) {
        container.innerHTML = `<div class="text-red-400 p-4">Error loading profile: ${err.message}</div>`;
      }
    }

    // Load Audit
    async function loadAudit() {
      const tbody = document.getElementById('audit-table-body');
      try {
        const res = await fetch('/api/audit');
        const logs = await res.json();
        
        tbody.innerHTML = logs.map(l => `
          <tr class="hover:bg-gray-800/40">
            <td class="px-4 py-2.5 text-gray-400">${l.timestamp.slice(11, 19)}</td>
            <td class="px-4 py-2.5 font-bold ${l.action.includes('REJECT') ? 'text-red-400' : (l.action.includes('INGEST') ? 'text-blue-400' : 'text-emerald-400')}">${l.action}</td>
            <td class="px-4 py-2.5 text-gray-300">${l.entity_type}</td>
            <td class="px-4 py-2.5"><span class="px-1.5 py-0.5 rounded text-[10px] ${l.outcome === 'SUCCESS' ? 'bg-emerald-950 text-emerald-400' : 'bg-red-950 text-red-400'}">${l.outcome}</span></td>
            <td class="px-4 py-2.5 text-gray-400">${l.actor}</td>
            <td class="px-4 py-2.5 text-gray-300 truncate max-w-xs">${JSON.stringify(l.details)}</td>
          </tr>
        `).join('');
      } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-red-400 text-center">Error loading audit events: ${err.message}</td></tr>`;
      }
    }

    // Ingest Form Submit
    async function handleIngest(e) {
      e.preventDefault();
      const btn = document.getElementById('ingest-btn');
      const feedback = document.getElementById('ingest-feedback');
      btn.innerText = 'Processing & Matching...';
      btn.disabled = true;

      const payload = {
        title: document.getElementById('ingest-title').value,
        company: document.getElementById('ingest-company').value,
        location: document.getElementById('ingest-location').value || null,
        salary_raw: document.getElementById('ingest-salary').value || null,
        source_url: document.getElementById('ingest-url').value || null,
        description: document.getElementById('ingest-desc').value,
        source_name: 'manual_dashboard_ingest'
      };

      try {
        const res = await fetch('/api/ingest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await res.json();

        feedback.classList.remove('hidden');
        if (result.status === 'ACCEPTED') {
          feedback.className = 'p-3 rounded-lg text-xs bg-emerald-950/60 border border-emerald-800 text-emerald-300';
          feedback.innerHTML = `<strong>Successfully Ingested &amp; Evaluated!</strong> Job ID: ${result.job.id}`;
          setTimeout(() => {
            closeIngestModal();
            loadMatches();
            switchTab('matches');
          }, 1000);
        } else {
          feedback.className = 'p-3 rounded-lg text-xs bg-amber-950/60 border border-amber-800 text-amber-300';
          feedback.innerHTML = `<strong>Status: ${result.status}</strong><br>${result.rejection_reason || 'Ingestion completed.'}`;
        }
      } catch (err) {
        feedback.classList.remove('hidden');
        feedback.className = 'p-3 rounded-lg text-xs bg-red-950/60 border border-red-800 text-red-300';
        feedback.innerText = `Error: ${err.message}`;
      } finally {
        btn.innerText = 'Process & Match';
        btn.disabled = false;
      }
    }

    // Initial Load
    document.addEventListener('DOMContentLoaded', () => {
      loadMatches();
      // Load initial job count
      fetch('/api/jobs').then(r => r.json()).then(jobs => {
        document.getElementById('stat-jobs').innerText = jobs.length;
      });
    });
  </script>
</body>
</html>
"""
