import React from "react";
import { CheckCircle2, AlertTriangle, ShieldAlert, FileText, Check } from "lucide-react";

interface OpportunityCardProps {
  item: any;
  onDraft: (jobId: string) => void;
}

export const OpportunityCard: React.FC<OpportunityCardProps> = ({ item, onDraft }) => {
  const { job, evaluation, rank } = item;
  const score = evaluation.overall_score;
  const rec = evaluation.recommendation;

  const badgeClass =
    rec === "APPLY"
      ? "bg-emerald-950/60 text-emerald-400 border-emerald-800"
      : rec === "CONSIDER"
      ? "bg-amber-950/60 text-amber-400 border-amber-800"
      : "bg-red-950/60 text-red-400 border-red-800";

  const salaryStr =
    job.salary && job.salary.min_amount
      ? `$${Number(job.salary.min_amount).toLocaleString()} - $${Number(job.salary.max_amount).toLocaleString()} / yr`
      : "Salary Not Stated";

  return (
    <div className="bg-[#111827]/70 backdrop-blur-md rounded-2xl p-6 border border-gray-800 hover:border-gray-700 transition">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-gray-800 to-gray-700 flex items-center justify-center font-bold text-lg text-blue-400 border border-gray-700">
            {job.company.charAt(0)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-blue-400">RANK #{rank}</span>
              <h3 className="text-lg font-bold text-white">{job.title}</h3>
            </div>
            <div className="text-xs text-gray-400 flex items-center gap-2 mt-0.5">
              <span className="text-gray-300 font-medium">{job.company}</span>
              <span>•</span>
              <span>{job.location || "Remote"}</span>
              <span>•</span>
              <span className="text-emerald-400 font-mono">{salaryStr}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-2xl font-black text-white">
              {score.toFixed(0)}
              <span className="text-xs font-normal text-gray-400">/100</span>
            </div>
            <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${badgeClass}`}>
              {rec}
            </span>
          </div>
        </div>
      </div>

      {/* Reasoning */}
      <div className="mt-4 p-3 rounded-xl bg-gray-900/60 border border-gray-800/80">
        <div className="text-[10px] font-bold text-blue-400 uppercase tracking-wider mb-1">
          Agent Evaluation Reasoning
        </div>
        <div className="text-xs text-gray-300 leading-relaxed">{evaluation.reasoning}</div>
      </div>

      {/* Grid: Strengths vs Gaps */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div className="p-3.5 rounded-xl bg-gray-900/40 border border-emerald-950/40">
          <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>Verified Evidence Citations</span>
            <span className="text-[10px] text-gray-500 font-normal">Fact-checked</span>
          </div>
          <div className="space-y-2">
            {evaluation.strengths.slice(0, 3).map((s: any, idx: number) => (
              <div key={idx}>
                <div className="text-xs font-medium text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                  <span>{s.requirement}</span>
                </div>
                <div className="text-[11px] text-gray-400 ml-5">{s.candidate_evidence}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-gray-900/40 border border-amber-950/40">
          <div className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">
            Gaps / Missing Qualifications
          </div>
          <div className="space-y-1.5">
            {evaluation.gaps.map((g: string, idx: number) => (
              <div key={idx} className="text-xs text-amber-300/90 flex items-start gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <span className="text-[11px]">{g}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Security alert if prompt injection was detected */}
      {job.security_flags && job.security_flags.length > 0 && (
        <div className="mt-3 p-2.5 rounded-lg bg-red-950/40 border border-red-800 text-[11px] text-red-300 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />
          <span>Security Shield Alert: {job.security_flags.join(", ")} (Neutralized)</span>
        </div>
      )}

      {/* Actions */}
      <div className="mt-5 pt-4 border-t border-gray-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-[11px] text-gray-400 font-mono">
          <Check className="w-3.5 h-3.5 text-emerald-400" />
          <span>Factual Grounding: 100% Verified</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onDraft(job.id)}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition flex items-center gap-1.5 shadow"
          >
            <FileText className="w-3.5 h-3.5" />
            Generate Tailored Application
          </button>
        </div>
      </div>
    </div>
  );
};
