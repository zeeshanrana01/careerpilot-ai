"use client";

import React from "react";
import { Zap, Plus, Upload, Bot, CheckCircle2 } from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenIngest: () => void;
  onOpenUploadCv: () => void;
  autoApplyEnabled?: boolean;
  onToggleAutoApply?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenIngest,
  onOpenUploadCv,
  autoApplyEnabled = false,
  onToggleAutoApply,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-[#0b0f19]/80 backdrop-blur-md border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/25">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-white tracking-tight">
                CareerPilot <span className="text-blue-500">AI</span>
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-950/80 text-blue-400 border border-blue-800/60">
                Milestones 1–4
              </span>
            </div>
            <span className="text-xs text-gray-400 block -mt-0.5">Production AI Career Agent</span>
          </div>
        </div>

        <nav className="flex items-center space-x-1 bg-gray-900/60 p-1 rounded-xl border border-gray-800">
          <button
            onClick={() => setActiveTab("matches")}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "matches" ? "bg-blue-600 text-white shadow" : "text-gray-400 hover:text-white"
            }`}
          >
            Opportunities
          </button>
          <button
            onClick={() => setActiveTab("profile")}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "profile" ? "bg-blue-600 text-white shadow" : "text-gray-400 hover:text-white"
            }`}
          >
            Verified Profile
          </button>
          <button
            onClick={() => setActiveTab("audit")}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "audit" ? "bg-blue-600 text-white shadow" : "text-gray-400 hover:text-white"
            }`}
          >
            Security &amp; Audit
          </button>
        </nav>

        <div className="flex items-center space-x-2.5">
          {onToggleAutoApply && (
            <button
              onClick={onToggleAutoApply}
              title="Autonomous Auto-Apply for matches >= 85%"
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition ${
                autoApplyEnabled
                  ? "bg-purple-950/80 border-purple-700 text-purple-300"
                  : "bg-gray-900 border-gray-800 text-gray-400 hover:text-gray-200"
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
              <span>Auto-Pilot: {autoApplyEnabled ? "ON" : "OFF"}</span>
            </button>
          )}

          <button
            onClick={onOpenUploadCv}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-white flex items-center gap-1.5 border border-gray-700 shadow-sm transition"
          >
            <Upload className="w-3.5 h-3.5 text-blue-400" />
            Upload CV
          </button>

          <button
            onClick={onOpenIngest}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1.5 shadow transition"
          >
            <Plus className="w-3.5 h-3.5" />
            Ingest Raw Job
          </button>
        </div>
      </div>
    </header>
  );
};
