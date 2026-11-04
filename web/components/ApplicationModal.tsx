"use client";

import React, { useState } from "react";
import { X, CheckCircle, AlertCircle, Hash, Send, ThumbsDown, Mail, Loader2, Sparkles } from "lucide-react";
import { approveApplication, rejectApplication, sendApplication } from "@/lib/api";

interface ApplicationModalProps {
  packageData: any;
  onClose: () => void;
  onRefresh: () => void;
}

export const ApplicationModal: React.FC<ApplicationModalProps> = ({
  packageData,
  onClose,
  onRefresh,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<"cv" | "email">("cv");
  const [actionStatus, setActionStatus] = useState<string | null>(packageData.status);
  const [isSending, setIsSending] = useState(false);
  const [sendResult, setSendResult] = useState<any>(null);
  const [recipientOverride, setRecipientOverride] = useState("");

  const cv = packageData.cv_variant;
  const email = packageData.cover_email;
  const grounding = packageData.grounding_report;

  const handleApprove = async () => {
    try {
      await approveApplication(packageData.id);
      setActionStatus("APPROVED");
      onRefresh();
    } catch (err: any) {
      alert("Error approving: " + err.message);
    }
  };

  const handleSend = async () => {
    setIsSending(true);
    try {
      const res = await sendApplication(packageData.id, recipientOverride || undefined);
      setSendResult(res);
      setActionStatus("SUBMITTED");
      onRefresh();
    } catch (err: any) {
      alert("Error dispatching email: " + err.message);
    } finally {
      setIsSending(false);
    }
  };

  const handleReject = async () => {
    try {
      await rejectApplication(packageData.id);
      setActionStatus("REJECTED");
      onRefresh();
    } catch (err: any) {
      alert("Error rejecting: " + err.message);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#111827] border border-gray-700 rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="p-5 border-b border-gray-800 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white">Tailored Application Package</h2>
              <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                actionStatus === "SUBMITTED"
                  ? "bg-purple-950 text-purple-400 border border-purple-800"
                  : actionStatus === "APPROVED"
                  ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                  : "bg-blue-950 text-blue-400 border border-blue-800"
              }`}>
                {actionStatus || packageData.status}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Human-in-the-Loop Review Gate · Exact draft cryptographic verification
            </p>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Subtabs */}
        <div className="px-5 pt-3 bg-gray-900/60 flex items-center justify-between border-b border-gray-800 text-xs">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveSubTab("cv")}
              className={`px-3 py-1.5 border-b-2 font-medium transition ${
                activeSubTab === "cv" ? "border-blue-500 text-white" : "border-transparent text-gray-400"
              }`}
            >
              Tailored CV Variant
            </button>
            <button
              onClick={() => setActiveSubTab("email")}
              className={`px-3 py-1.5 border-b-2 font-medium transition ${
                activeSubTab === "email" ? "border-blue-500 text-white" : "border-transparent text-gray-400"
              }`}
            >
              Cover Email Draft
            </button>
          </div>

          <div className="flex items-center gap-1.5 text-[11px] text-gray-400 font-mono">
            <Hash className="w-3.5 h-3.5 text-blue-400" />
            <span className="truncate max-w-[180px]">{packageData.draft_hash}</span>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1 text-xs">
          {sendResult && (
            <div className="p-3.5 rounded-xl bg-purple-950/60 border border-purple-800 text-purple-200 flex items-center gap-2.5">
              <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />
              <div>
                <p className="font-semibold text-white">Application Dispatched Successfully!</p>
                <p className="text-[11px] text-purple-300">
                  Recipient: <span className="font-mono text-white">{sendResult.recipient}</span> ({sendResult.status})
                </p>
              </div>
            </div>
          )}

          {activeSubTab === "cv" ? (
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-bold text-white">{cv.tailored_headline}</h4>
                <p className="text-xs text-gray-300 mt-1 leading-relaxed bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                  {cv.tailored_summary}
                </p>
              </div>

              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1.5">
                  Highlighted Verified Skills
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {cv.highlighted_skills.map((sk: string, i: number) => (
                    <span key={i} className="px-2.5 py-1 rounded bg-blue-950/70 text-blue-300 border border-blue-800/60 font-mono text-[11px]">
                      {sk}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1.5">
                  Highlighted Relevant Experience
                </span>
                <div className="space-y-2">
                  {cv.highlighted_experience.map((exp: any, i: number) => (
                    <div key={i} className="p-3 rounded-lg bg-gray-900/40 border border-gray-800">
                      <div className="font-semibold text-white">{exp.title} @ {exp.company}</div>
                      <ul className="mt-1 list-disc list-inside text-gray-300 space-y-0.5">
                        {exp.highlights.map((h: string, j: number) => (
                          <li key={j}>{h}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-1.5">
                  Relevant Portfolio Projects
                </span>
                <div className="space-y-2">
                  {cv.highlighted_projects.map((proj: any, i: number) => (
                    <div key={i} className="p-3 rounded-lg bg-gray-900/40 border border-gray-800">
                      <div className="font-semibold text-blue-400">{proj.name} ({proj.role})</div>
                      <ul className="mt-1 list-disc list-inside text-gray-300">
                        {proj.highlights.map((h: string, j: number) => (
                          <li key={j}>{h}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4 font-sans">
              <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-800 space-y-3 font-mono text-[11px]">
                <div>
                  <span className="text-gray-500 uppercase tracking-wide">Subject:</span>
                  <span className="ml-2 text-white font-semibold">{email.subject}</span>
                </div>
                <div className="border-t border-gray-800 pt-3 text-gray-300 space-y-3 font-sans text-xs">
                  <p>{email.salutation}</p>
                  {email.body_paragraphs.map((p: string, i: number) => (
                    <p key={i} className="leading-relaxed">{p}</p>
                  ))}
                  <p className="font-medium text-blue-300">{email.call_to_action}</p>
                  <p className="whitespace-pre-line text-gray-400 pt-2">{email.sign_off}</p>
                </div>
              </div>

              {/* Recruiter Email Input */}
              <div className="p-3 rounded-xl bg-gray-900/40 border border-gray-800 flex items-center gap-3">
                <Mail className="w-4 h-4 text-gray-400 shrink-0" />
                <div className="flex-1">
                  <label className="text-[10px] uppercase font-bold text-gray-400 block mb-0.5">
                    Destination Email (Optional Override)
                  </label>
                  <input
                    type="email"
                    placeholder="recruiter@company.com (leave blank for default careers@company.com)"
                    value={recipientOverride}
                    onChange={(e) => setRecipientOverride(e.target.value)}
                    className="w-full bg-gray-950 border border-gray-700 rounded-lg px-2.5 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Grounding Report Box */}
          <div className="p-3 rounded-xl bg-gray-900/80 border border-gray-800 flex items-start gap-3">
            {grounding.is_strictly_grounded ? (
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="font-bold text-white text-[11px]">
                Grounding Verification: {grounding.is_strictly_grounded ? "100% Verified Truthful" : "Discrepancy Detected"}
              </div>
              <p className="text-[10px] text-gray-400 mt-0.5">
                Supported Verified Skills Cited: {grounding.supported_claims.join(", ")}
              </p>
              {grounding.unsupported_claims.length > 0 && (
                <p className="text-[10px] text-amber-400 mt-0.5">
                  Unsupported Claims Flagged: {grounding.unsupported_claims.join(", ")}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-gray-800 bg-gray-900/40 flex items-center justify-between">
          <div className="text-[11px] text-gray-400">
            Cryptographic Payload: <code>{packageData.draft_hash.slice(0, 12)}...</code>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleReject}
              className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-gray-300 hover:text-red-400 bg-gray-800 border border-gray-700 flex items-center gap-1.5"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
              Reject Draft
            </button>
            <button
              onClick={handleApprove}
              className="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-emerald-300 hover:text-white bg-emerald-950 hover:bg-emerald-900 border border-emerald-800/80 shadow flex items-center gap-1.5"
            >
              <CheckCircle className="w-3.5 h-3.5" />
              Approve Only
            </button>
            <button
              onClick={handleSend}
              disabled={isSending}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow flex items-center gap-1.5 disabled:opacity-50"
            >
              {isSending ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              {actionStatus === "SUBMITTED" ? "Re-Send Application" : "Approve & Send Email"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
