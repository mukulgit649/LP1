"use client"

import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, Settings, Brain, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { SkillRadarChart } from '@/components/RadarChart';
import { Heatmap } from '@/components/Heatmap';

export default function Home() {
  const [apiKey, setApiKey] = useState('');
  const [modelName, setModelName] = useState('gemini-2.0-flash-exp');
  const [file, setFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!file || !jdText || !apiKey) {
      setError("Please provide Resume, Job Description, and API Key.");
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('resume_file', file);
    formData.append('jd_text', jdText);
    formData.append('api_key', apiKey);
    formData.append('model_name', modelName);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${apiUrl}/api/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred during analysis.");
    } finally {
      setLoading(false);
    }
  };

  const radarData = results ? [
    { subject: 'Hard Skills', A: results.sub_scores['Hard Skills'], fullMark: 100 },
    { subject: 'Soft Skills', A: results.sub_scores['Soft Skills'], fullMark: 100 },
    { subject: 'Experience', A: results.sub_scores['Experience'], fullMark: 100 },
    { subject: 'Education', A: results.sub_scores['Education'], fullMark: 100 },
  ] : [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans flex">

      {/* Sidebar */}
      <aside className="w-80 bg-slate-900 border-r border-slate-800 flex-shrink-0 p-6 flex flex-col gap-8 fixed h-full overflow-y-auto">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Brain className="text-blue-500" />
            AI Role Fit Engine
          </h1>
          <p className="text-xs text-slate-500 mt-1">Context-Aware Resume Analysis</p>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <Settings className="w-4 h-4" /> Gemini API Key
            </label>
            <input
              type="password"
              className="w-full bg-slate-950 border border-slate-800 rounded-md p-2.5 text-sm text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              placeholder="Enter your API Key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <p className="text-xs text-slate-500">Required for AI analysis.</p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Model Selection</label>
            <select
              className="w-full bg-slate-950 border border-slate-800 rounded-md p-2.5 text-sm text-white focus:ring-2 focus:ring-blue-500 outline-none"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
            >
              <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash (Fast)</option>
              <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite (New)</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro (Reasoning)</option>
            </select>
          </div>
        </div>

        {results && (
          <div className="space-y-4 pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Recruiter Metrics</h3>
            <div className="space-y-3">
              <div className="bg-slate-950 p-3 rounded-md border border-slate-800">
                <p className="text-xs text-slate-500">Reading Time</p>
                <p className="text-lg font-mono text-blue-400">{results.recruiter_metrics.reading_time}</p>
              </div>
              <div className="bg-slate-950 p-3 rounded-md border border-slate-800">
                <p className="text-xs text-slate-500">Buzzwords</p>
                <p className="text-lg font-mono text-orange-400">{results.recruiter_metrics.buzzword_count}</p>
              </div>
              <div className="bg-slate-950 p-3 rounded-md border border-slate-800">
                <p className="text-xs text-slate-500">Action Verbs</p>
                <p className="text-lg font-mono text-green-400">{results.recruiter_metrics.action_verb_count}</p>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-80 p-8 max-w-5xl mx-auto space-y-8">

        {/* Header */}
        <div className="space-y-2 mb-8">
          <h2 className="text-3xl font-bold text-white">AI Role Fit Engine 🧠</h2>
          <p className="text-slate-400">Analyzes resumes by context, not just keywords. Checks if you have the mindset of the role.</p>
        </div>

        {/* Input Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Resume Upload */}
          <Card className="bg-slate-900 border-slate-800 lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-white">Resume</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-slate-700 rounded-lg p-6 text-center hover:bg-slate-800/50 transition cursor-pointer relative group">
                <input
                  type="file"
                  accept=".pdf"
                  className="absolute inset-0 opacity-0 cursor-pointer z-10"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                <div className="flex flex-col items-center gap-2">
                  <div className="p-3 bg-slate-800 rounded-full group-hover:bg-slate-700 transition">
                    <Upload className="w-6 h-6 text-blue-400" />
                  </div>
                  <p className="text-sm text-slate-300 font-medium">{file ? file.name : "Upload PDF"}</p>
                  <p className="text-xs text-slate-500">Drag & drop or click</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* JD Input */}
          <Card className="bg-slate-900 border-slate-800 lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-white">Job Description</CardTitle>
            </CardHeader>
            <CardContent>
              <textarea
                className="w-full h-32 bg-slate-950 border border-slate-800 rounded-md p-3 text-sm text-slate-300 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                placeholder="Paste the full Job Description here..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
              />
              <div className="mt-4 flex justify-between items-center">
                {error && <p className="text-red-400 text-sm flex items-center gap-1"><AlertCircle className="w-4 h-4" /> {error}</p>}
                <Button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="ml-auto bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Analyzing...</> : "Analyze Resume"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Results Section */}
        {results && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Score Card */}
            <Card className="bg-gradient-to-r from-blue-900/20 to-slate-900 border-blue-900/50">
              <CardContent className="p-8 flex items-center justify-between">
                <div>
                  <p className="text-blue-400 font-medium mb-1">Overall Role Fit Score</p>
                  <h2 className="text-5xl font-bold text-white tracking-tight">{results.score}%</h2>
                  <p className="text-slate-400 text-sm mt-2">Based on semantic analysis of {results.sentence_scores.length} sentences.</p>
                </div>
                <div className="h-24 w-24 rounded-full border-4 border-blue-500/30 flex items-center justify-center bg-blue-500/10">
                  <CheckCircle className="w-10 h-10 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Radar Chart */}
              <Card className="bg-slate-900 border-slate-800 lg:col-span-1">
                <CardHeader>
                  <CardTitle className="text-white">Skill Profile</CardTitle>
                </CardHeader>
                <CardContent>
                  <SkillRadarChart data={radarData} />
                </CardContent>
              </Card>

              {/* Missing Skills */}
              <Card className="bg-slate-900 border-slate-800 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-white">Missing Skills</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {results.missing_skills.length > 0 ? (
                      results.missing_skills.map((skill: string, i: number) => (
                        <span key={i} className="px-3 py-1 bg-red-900/30 text-red-300 rounded-full text-sm font-medium border border-red-900/50 hover:bg-red-900/50 transition cursor-default">
                          {skill}
                        </span>
                      ))
                    ) : (
                      <div className="flex items-center text-green-400 gap-2 p-4 bg-green-900/20 rounded-lg border border-green-900/30 w-full">
                        <CheckCircle className="h-5 w-5" />
                        <span>No critical skills missing! You are a strong match.</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Heatmap */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white">Resume Heatmap</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 mb-4 text-sm">
                  <span className="flex items-center gap-1 text-green-400"><span className="w-2 h-2 rounded-full bg-green-400"></span> Strong Match</span>
                  <span className="flex items-center gap-1 text-orange-400"><span className="w-2 h-2 rounded-full bg-orange-400"></span> Weak Match</span>
                </div>
                <Heatmap sentenceScores={results.sentence_scores} />
              </CardContent>
            </Card>

          </div>
        )}
      </main>
    </div>
  );
}
