"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Send, Check, X, ShieldAlert } from "lucide-react";
import { api, getSession, UserSession } from "../../lib/api";


export default function LeavesPage() {
  const router = useRouter();
  const [session, setSession] = useState<UserSession | null>(null);
  const [leaves, setLeaves] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Student apply form states
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");
  const [submitSuccess, setSubmitSuccess] = useState("");
  const [submitError, setSubmitError] = useState("");

  // Faculty comments review state
  const [comments, setComments] = useState<{ [key: number]: string }>({});

  const fetchLeaves = () => {
    api.getLeaves()
      .then((data) => setLeaves(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.push("/login");
      return;
    }
    setSession(s);
    fetchLeaves();
  }, [router]);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitSuccess("");
    setSubmitError("");
    try {
      await api.createLeave(startDate, endDate, reason);
      setSubmitSuccess("Leave request submitted successfully!");
      setStartDate("");
      setEndDate("");
      setReason("");
      fetchLeaves();
    } catch (err: any) {
      setSubmitError(err.message || "Failed to submit leave request.");
    }
  };

  const handleReview = async (leaveId: number, status: 'approved' | 'rejected') => {
    try {
      const reviewComment = comments[leaveId] || "";
      await api.reviewLeave(leaveId, status, reviewComment);
      fetchLeaves();
    } catch (err: any) {
      alert(`Error updating leave status: ${err.message}`);
    }
  };

  if (loading || !session) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="w-6 h-6 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl w-full mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Leave Requests</h1>
        <p className="text-slate-500 mt-1">
          {session.role === "student"
            ? "Submit and track status of your medical or duty leaves."
            : "Review, approve, or reject student leave requests."}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Student Application Form */}
        {session.role === "student" && (
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-md h-fit">
            <h3 className="text-lg font-bold text-slate-850 mb-6 flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-600" />
              <span>Apply for Leave</span>
            </h3>

            {submitSuccess && <p className="mb-4 text-xs font-bold text-emerald-600 bg-emerald-50 border border-emerald-100 p-3 rounded-2xl">{submitSuccess}</p>}
            {submitError && <p className="mb-4 text-xs font-bold text-red-600 bg-red-50 border border-red-100 p-3 rounded-2xl">{submitError}</p>}

            <form onSubmit={handleApply} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Start Date</label>
                <input
                  type="date"
                  required
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">End Date</label>
                <input
                  type="date"
                  required
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Reason</label>
                <textarea
                  required
                  rows={4}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="State the reason for your leave request..."
                  className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none focus:border-indigo-500 placeholder-slate-400 resize-none"
                />
              </div>

              <button
                type="submit"
                className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-semibold text-sm transition-colors duration-200 shadow-md shadow-indigo-100"
              >
                <span>Submit Request</span>
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        )}

        {/* Leaves Table */}
        <div className={`bg-white rounded-3xl border border-slate-200/80 shadow-md overflow-hidden ${
          session.role === "student" ? "lg:col-span-2" : "lg:col-span-3"
        }`}>
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-400 uppercase tracking-wider">
                {session.role === "faculty" && <th className="px-6 py-4">Student</th>}
                <th className="px-6 py-4">Duration</th>
                <th className="px-6 py-4">Reason</th>
                <th className="px-6 py-4">Status</th>
                {session.role === "faculty" && <th className="px-6 py-4">Review Action</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm font-medium text-slate-700">
              {leaves.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-400">
                    No leave requests found.
                  </td>
                </tr>
              ) : (
                leaves.map((l) => (
                  <tr key={l.leave_id} className="hover:bg-slate-50/50 transition-colors">
                    {session.role === "faculty" && (
                      <td className="px-6 py-4">
                        <p className="font-bold text-slate-800">{l.student_name}</p>
                        <p className="text-[10px] text-slate-400 font-mono mt-0.5">{l.student_id}</p>
                      </td>
                    )}
                    <td className="px-6 py-4">
                      <p className="font-bold text-slate-800">{l.start_date}</p>
                      <p className="text-[10px] text-slate-400 font-medium mt-0.5">to {l.end_date}</p>
                    </td>
                    <td className="px-6 py-4 max-w-xs truncate">{l.reason}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                        l.status === "approved"
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                          : l.status === "rejected"
                          ? "bg-red-50 text-red-700 border border-red-100"
                          : "bg-amber-50 text-amber-700 border border-amber-100"
                      }`}>
                        <span className="capitalize">{l.status}</span>
                      </span>
                      {l.review_comments && (
                        <p className="text-[10px] text-slate-400 font-medium italic mt-1 max-w-xs break-words">
                          "{l.review_comments}"
                        </p>
                      )}
                    </td>
                    {session.role === "faculty" && (
                      <td className="px-6 py-4">
                        {l.status === "pending" ? (
                          <div className="flex flex-col gap-2">
                            <input
                              type="text"
                              placeholder="Review comment..."
                              value={comments[l.leave_id] || ""}
                              onChange={(e) => setComments({ ...comments, [l.leave_id]: e.target.value })}
                              className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-medium text-slate-700 focus:outline-none focus:border-indigo-500"
                            />
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleReview(l.leave_id, "approved")}
                                className="flex-1 flex items-center justify-center gap-1 py-1.5 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold"
                              >
                                <Check className="w-3.5 h-3.5" />
                                <span>Approve</span>
                              </button>
                              <button
                                onClick={() => handleReview(l.leave_id, "rejected")}
                                className="flex-1 flex items-center justify-center gap-1 py-1.5 px-3 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold"
                              >
                                <X className="w-3.5 h-3.5" />
                                <span>Reject</span>
                              </button>
                            </div>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400 italic">Reviewed</span>
                        )}
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
