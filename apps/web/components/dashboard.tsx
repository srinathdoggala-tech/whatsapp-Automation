"use client";
import { useQuery } from "@tanstack/react-query";
import { Phone, MessageSquare, Clock, AlertTriangle, CheckCircle2, XCircle, PauseCircle, PlayCircle } from "lucide-react";

async function fetchJSON(url: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed");
  return res.json();
}

function StatusPill({ label, color }: { label: string; color: string }) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${color}`}>
      <span className="h-2 w-2 rounded-full bg-current" />
      {label}
    </span>
  );
}

export default function Dashboard() {
  const overview = useQuery({ queryKey: ["overview"], queryFn: () => fetchJSON("/api/overview") });
  const conversations = useQuery({ queryKey: ["conversations"], queryFn: () => fetchJSON("/api/conversations") });
  const approvals = useQuery({ queryKey: ["approvals"], queryFn: () => fetchJSON("/api/approvals") });

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">WhatsApp AI Assistant</h1>
          <p className="mt-1 text-sm text-gray-400">Reliability-first conversational assistant</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusPill label="Autopilot" color="bg-emerald-500/10 text-emerald-300" />
          <StatusPill label="Connected" color="bg-blue-500/10 text-blue-300" />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Metric title="Messages Today" value={overview.data?.messages_today ?? "—"} icon={<MessageSquare className="h-4 w-4" />} />
        <Metric title="Pending Approvals" value={overview.data?.pending_approvals ?? "—"} icon={<Clock className="h-4 w-4" />} />
        <Metric title="Failed Jobs" value={overview.data?.failed_jobs ?? "—"} icon={<AlertTriangle className="h-4 w-4" />} />
        <Metric title="Mode" value="Approval" icon={<PauseCircle className="h-4 w-4" />} />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="lg:col-span-2 rounded-xl border border-white/10 bg-white/5 p-4">
          <h2 className="mb-4 text-lg font-medium">Conversations</h2>
          <div className="space-y-3">
            {(conversations.data ?? []).slice(0, 20).map((c: any) => (
              <div key={c.id} className="flex items-center justify-between rounded-lg border border-white/5 bg-black/20 p-3">
                <div>
                  <div className="text-sm font-medium">Conversation {c.id.slice(0, 8)}</div>
                  <div className="text-xs text-gray-400">{c.messages?.length ?? 0} messages</div>
                </div>
                <div className="text-xs text-gray-400">{c.last_message_at ? new Date(c.last_message_at).toLocaleString() : "—"}</div>
              </div>
            ))}
            {!conversations.data && <p className="text-sm text-gray-400">Loading conversations…</p>}
            {(conversations.data ?? []).length === 0 && <p className="text-sm text-gray-400">No conversations yet.</p>}
          </div>
        </section>

        <section className="rounded-xl border border-white/10 bg-white/5 p-4">
          <h2 className="mb-4 text-lg font-medium">Approval Queue</h2>
          <div className="space-y-3">
            {(approvals.data ?? []).slice(0, 20).map((a: any) => (
              <div key={a.id} className="rounded-lg border border-white/5 bg-black/20 p-3">
                <div className="text-sm font-medium">Approval {a.id.slice(0, 8)}</div>
                <div className="mt-1 text-xs text-gray-300 line-clamp-2">{a.suggested_response}</div>
                <div className="mt-2 flex gap-2 text-xs text-gray-400">
                  <button className="rounded-md bg-emerald-500/20 px-2 py-1 text-emerald-200">Approve</button>
                  <button className="rounded-md bg-red-500/20 px-2 py-1 text-red-200">Reject</button>
                </div>
              </div>
            ))}
            {!approvals.data && <p className="text-sm text-gray-400">Loading approvals…</p>}
            {(approvals.data ?? []).length === 0 && <p className="text-sm text-gray-400">No pending approvals.</p>}
          </div>
        </section>
      </div>
    </div>
  );
}

function Metric({ title, value, icon }: { title: string; value: any; icon: any }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center justify-between text-gray-400">
        <span className="text-xs uppercase tracking-wide">{title}</span>
        {icon}
      </div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}
