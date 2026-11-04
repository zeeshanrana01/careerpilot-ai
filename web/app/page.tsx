"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar";
import { OpportunityCard } from "@/components/OpportunityCard";
import { ApplicationModal } from "@/components/ApplicationModal";
import { IngestModal } from "@/components/IngestModal";
import { UploadCvModal } from "@/components/UploadCvModal";
import { fetchMatches, fetchProfile, fetchAudit, fetchSettings, updateSettings, draftApplication, fetchApplication } from "@/lib/api";
import { Shield, Sparkles, RefreshCw, Briefcase, FileCheck, Upload } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("matches");
  const [matches, setMatches] = useState<any[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [autoApplyEnabled, setAutoApplyEnabled] = useState(false);
  const [loading, setLoading] = useState(true);

  const [selectedAppPackage, setSelectedAppPackage] = useState<any>(null);
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [showUploadCvModal, setShowUploadCvModal] = useState(false);
  const [draftingJobId, setDraftingJobId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [m, p, a, s] = await Promise.all([
        fetchMatches(),
        fetchProfile(),
        fetchAudit(),
        fetchSettings().catch(() => ({ auto_apply_enabled: false })),
      ]);
      setMatches(m);
      setProfile(p);
      setAuditLogs(a);
      setAutoApplyEnabled(s?.auto_apply_enabled ?? false);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleAutoApply = async () => {
    try {
      const nextState = !autoApplyEnabled;
      const res = await updateSettings({ auto_apply_enabled: nextState });
      setAutoApplyEnabled(res.auto_apply_enabled);
    } catch (err: any) {
      alert("Failed to toggle Auto-Pilot: " + err.message);
    }
  };

  const handleOpenDraft = async (jobId: string) => {
    setDraftingJobId(jobId);
    try {
      let pkg = await fetchApplication(jobId);
      if (!pkg) {
        pkg = await draftApplication(jobId);
      }
      setSelectedAppPackage(pkg);
    } catch (err: any) {
      alert("Error generating application package: " + err.message);
    } finally {
      setDraftingJobId(null);
    }
  };

  const topScore = matches.length > 0 ? Math.max(...matches.map(m => m.evaluation.overall_score)) : 0;

  return (
    <div className="min-h-screen flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenIngest={() => setShowIngestModal(true)}
        onOpenUploadCv={() => setShowUploadCvModal(true)}
        autoApplyEnabled={autoApplyEnabled}
        onToggleAutoApply={handleToggleAutoApply}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-8">
        {/* Banner */}
        <div className="bg-[#111827]/70 backdrop-blur-md rounded-2xl p-6 border border-gray-800 relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                  AI Orchestration Active
                </span>
                <span className="text-xs text-gray-500">•</span>
                <span className="text-xs text-gray-300">
                  {profile ? `${profile.full_name} (${profile.headline})` : "Candidate Profile Active"}
                </span>
                {autoApplyEnabled && (
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-950 text-purple-400 border border-purple-800">
                    Auto-Pilot Active (≥85%)
                  </span>
                )}
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                AI Career Agent Dashboard
              </h1>
              <p className="text-xs text-gray-400 mt-1 max-w-2xl">
                Automated preparation, truthful claim verification, and instant 1-click application dispatch.
              </p>
            </div>

            {/* Quick Metrics */}
            <div className="flex items-center gap-3">
              <div className="px-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-center min-w-[90px]">
                <div className="text-xl font-bold text-white">{matches.length}</div>
                <div className="text-[10px] text-gray-400 uppercase tracking-wide">Opportunities</div>
              </div>
              <div className="px-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-center min-w-[90px]">
                <div className="text-xl font-bold text-emerald-400">{topScore.toFixed(0)}%</div>
                <div className="text-[10px] text-gray-400 uppercase tracking-wide">Top Match</div>
              </div>
              <div className="px-4 py-2.5 rounded-xl bg-gray-900/80 border border-gray-800 text-center min-w-[90px]">
                <div className="text-xl font-bold text-blue-400">{auditLogs.length}</div>
                <div className="text-[10px] text-gray-400 uppercase tracking-wide">Audit Events</div>
              </div>
            </div>
          </div>
        </div>

        {/* TAB 1: Opportunities */}
        {activeTab === "matches" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-blue-400" />
                Ranked Opportunity Queue
              </h2>
              <button
                onClick={loadData}
                className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1.5 font-medium"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                Refresh Opportunities
              </button>
            </div>

            {loading ? (
              <div className="text-center py-16 text-gray-400 text-sm">Evaluating opportunities...</div>
            ) : matches.length === 0 ? (
              <div className="bg-[#111827]/60 rounded-2xl p-12 text-center text-gray-400 border border-gray-800">
                No matched opportunities yet. Ingest raw listings to begin.
              </div>
            ) : (
              <div className="space-y-6">
                {matches.map((item: any) => (
                  <OpportunityCard
                    key={item.job.id}
                    item={item}
                    onDraft={handleOpenDraft}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Verified Profile */}
        {activeTab === "profile" && profile && (
          <div className="bg-[#111827]/70 backdrop-blur-md rounded-2xl p-6 border border-gray-800 space-y-6">
            <div className="border-b border-gray-800 pb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">{profile.full_name}</h2>
                <p className="text-sm text-blue-400 font-medium">{profile.headline}</p>
                <p className="text-xs text-gray-400 mt-2 max-w-3xl">{profile.summary}</p>
              </div>
              <button
                onClick={() => setShowUploadCvModal(true)}
                className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5 shadow"
              >
                <Upload className="w-3.5 h-3.5" />
                Update CV
              </button>
            </div>

            <div>
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                Verified Technical Skills ({profile.skills.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((s: any, idx: number) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg text-xs font-medium bg-blue-950/60 text-blue-300 border border-blue-800/60"
                  >
                    {s.name} <span className="text-[10px] text-gray-400">({s.years_experience}y)</span>
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                Verified Experience
              </h3>
              <div className="space-y-3">
                {profile.experience.map((e: any, idx: number) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                    <div className="flex justify-between items-baseline">
                      <span className="text-xs font-bold text-white">{e.title} @ {e.company}</span>
                      <span className="text-[11px] text-gray-400 font-mono">{e.start_date} - {e.end_date}</span>
                    </div>
                    <ul className="mt-2 space-y-1 text-xs text-gray-300 list-disc list-inside">
                      {e.highlights.map((h: string, j: number) => (
                        <li key={j}>{h}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                Verified Projects
              </h3>
              <div className="space-y-3">
                {profile.projects.map((proj: any, idx: number) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                    <div className="flex justify-between items-baseline">
                      <span className="text-xs font-bold text-blue-400">{proj.name} ({proj.role})</span>
                    </div>
                    <p className="text-xs text-gray-300 mt-1">{proj.description}</p>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {proj.technologies?.map((t: string, j: number) => (
                        <span key={j} className="text-[10px] px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: Audit Trail */}
        {activeTab === "audit" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-400" />
                Immutable Audit Log
              </h2>
              <span className="text-xs text-gray-400">Append-only SQLite Ledger</span>
            </div>

            <div className="bg-[#111827]/70 backdrop-blur-md rounded-2xl overflow-hidden border border-gray-800">
              <table className="w-full text-left text-xs text-gray-300">
                <thead className="bg-gray-900/80 text-gray-400 uppercase text-[10px] tracking-wider border-b border-gray-800">
                  <tr>
                    <th className="px-4 py-3">Timestamp (UTC)</th>
                    <th className="px-4 py-3">Action</th>
                    <th className="px-4 py-3">Entity</th>
                    <th className="px-4 py-3">Outcome</th>
                    <th className="px-4 py-3">Actor</th>
                    <th className="px-4 py-3">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60 font-mono">
                  {auditLogs.map((log: any) => (
                    <tr key={log.id} className="hover:bg-gray-800/30">
                      <td className="px-4 py-2.5 text-gray-400">{log.timestamp.slice(11, 19)}</td>
                      <td className={`px-4 py-2.5 font-bold ${
                        log.action.includes("REJECT")
                          ? "text-red-400"
                          : log.action.includes("INGEST")
                          ? "text-blue-400"
                          : log.action.includes("SUBMIT")
                          ? "text-purple-400"
                          : "text-emerald-400"
                      }`}>
                        {log.action}
                      </td>
                      <td className="px-4 py-2.5 text-gray-300">{log.entity_type}</td>
                      <td className="px-4 py-2.5">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                          log.outcome === "SUCCESS"
                            ? "bg-emerald-950 text-emerald-400"
                            : "bg-red-950 text-red-400"
                        }`}>
                          {log.outcome}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-gray-400">{log.actor}</td>
                      <td className="px-4 py-2.5 text-gray-300 truncate max-w-xs">
                        {JSON.stringify(log.details)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      {selectedAppPackage && (
        <ApplicationModal
          packageData={selectedAppPackage}
          onClose={() => setSelectedAppPackage(null)}
          onRefresh={loadData}
        />
      )}

      {showIngestModal && (
        <IngestModal
          onClose={() => setShowIngestModal(false)}
          onSuccess={loadData}
        />
      )}

      {showUploadCvModal && (
        <UploadCvModal
          isOpen={showUploadCvModal}
          onClose={() => setShowUploadCvModal(false)}
          onSuccess={loadData}
        />
      )}
    </div>
  );
}
