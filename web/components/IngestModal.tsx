import React, { useState } from "react";
import { X, ShieldAlert, CheckCircle, ArrowRight } from "lucide-react";
import { ingestJob } from "@/lib/api";

interface IngestModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const IngestModal: React.FC<IngestModalProps> = ({ onClose, onSuccess }) => {
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [salaryRaw, setSalaryRaw] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const res = await ingestJob({
        title,
        company,
        location: location || null,
        salary_raw: salaryRaw || null,
        source_url: sourceUrl || null,
        description,
        source_name: "nextjs_dashboard",
      });
      setResult(res);
      if (res.status === "ACCEPTED") {
        setTimeout(() => {
          onSuccess();
          onClose();
        }, 1200);
      }
    } catch (err: any) {
      setResult({ status: "ERROR", rejection_reason: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#111827] border border-gray-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-gray-800">
          <div>
            <h3 className="text-base font-bold text-white">Ingest Raw Job Posting</h3>
            <span className="text-[11px] text-emerald-400 font-mono">Zero-Trust Untrusted Input Shield</span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3.5 mt-4 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-gray-300 font-medium mb-1">Job Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Senior AI Engineer"
                className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-gray-300 font-medium mb-1">Company Name *</label>
              <input
                type="text"
                required
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="Anthropic, Inc."
                className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-gray-300 font-medium mb-1">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="San Francisco, CA / Remote"
                className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-gray-300 font-medium mb-1">Salary Range</label>
              <input
                type="text"
                value={salaryRaw}
                onChange={(e) => setSalaryRaw(e.target.value)}
                placeholder="$185k - $240k / year"
                className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-gray-300 font-medium mb-1">Source URL (Tracking tags stripped automatically)</label>
            <input
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://company.com/jobs/123?utm_source=linkedin&ref=aggregator"
              className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500 font-mono text-[11px]"
            />
          </div>

          <div>
            <label className="block text-gray-300 font-medium mb-1">Job Description (Untrusted HTML / Raw Text) *</label>
            <textarea
              required
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Paste job description. Active scripts (<script>) will be neutralized and prompt injections intercepted."
              className="w-full px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-blue-500 font-mono text-[11px]"
            />
          </div>

          {result && (
            <div className={`p-3 rounded-lg text-xs border ${
              result.status === "ACCEPTED"
                ? "bg-emerald-950/60 border-emerald-800 text-emerald-300"
                : "bg-amber-950/60 border-amber-800 text-amber-300"
            }`}>
              <div className="font-bold flex items-center gap-1.5">
                {result.status === "ACCEPTED" ? <CheckCircle className="w-4 h-4" /> : <ShieldAlert className="w-4 h-4" />}
                Status: {result.status}
              </div>
              {result.rejection_reason && <div className="mt-1 text-[11px]">{result.rejection_reason}</div>}
              {result.security_warnings && result.security_warnings.length > 0 && (
                <div className="mt-1 text-[11px] text-red-300 font-mono">
                  Alert: {result.security_warnings.join(", ")}
                </div>
              )}
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-2 border-t border-gray-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-1.5 shadow"
            >
              {loading ? "Processing..." : "Process & Match"}
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
