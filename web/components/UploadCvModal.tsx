"use client";

import React, { useState, useRef } from "react";
import { X, Upload, FileText, CheckCircle2, AlertTriangle, Loader2 } from "lucide-react";
import { uploadResume } from "../lib/api";

interface UploadCvModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const UploadCvModal: React.FC<UploadCvModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setSuccessMsg(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF or JSON resume file.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await uploadResume(file);
      setSuccessMsg(res.message || "Resume loaded and parsed successfully!");
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || "Failed to process resume file.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#111827] border border-gray-800 rounded-2xl w-full max-w-lg shadow-2xl p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Upload className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Upload Your CV / Resume</h3>
            <p className="text-xs text-gray-400">
              Upload your PDF or JSON resume to establish your verified career profile.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-200 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="mb-4 p-3 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-200 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>{successMsg}</span>
          </div>
        )}

        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-700 hover:border-blue-500/80 rounded-xl p-8 text-center cursor-pointer transition bg-gray-900/40 hover:bg-gray-900/80 mb-6"
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.json,.txt"
            className="hidden"
          />
          <FileText className="w-10 h-10 text-gray-400 mx-auto mb-3" />
          {file ? (
            <div>
              <p className="text-sm font-semibold text-white">{file.name}</p>
              <p className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB • Click to choose another</p>
            </div>
          ) : (
            <div>
              <p className="text-sm font-medium text-gray-300">
                Click to browse or drag & drop your resume
              </p>
              <p className="text-xs text-gray-500 mt-1">Supported formats: PDF, JSON, TXT</p>
            </div>
          )}
        </div>

        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3 mb-6">
          <p className="text-xs text-gray-400 leading-relaxed">
            <strong className="text-gray-300">Zero-Hallucination Guarantee:</strong> CareerPilot strictly extracts verified skills, work experiences, and projects from your uploaded document. Tailored application drafts will only cite facts present in this document.
          </p>
        </div>

        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-gray-300 hover:bg-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={loading || !file}
            className="px-5 py-2 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white flex items-center gap-2 shadow"
          >
            {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            {loading ? "Parsing & Re-Evaluating..." : "Parse & Update Profile"}
          </button>
        </div>
      </div>
    </div>
  );
};
