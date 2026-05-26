"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { deleteDocument, downloadDocument, generateDocumentChecklist, getDefaultApplicant, getDocuments, getPrograms, updateDocumentStatus, uploadDocument } from "@/lib/api";
import { documentName, tValue } from "@/lib/display";
import type { Applicant, DocumentItem, Program } from "@/lib/types";

const documentTypes = ["CV", "Personal Statement", "Transcript", "Degree Certificate", "IELTS", "TOEFL", "GRE", "GMAT", "Recommendation Letter", "Passport", "Research Proposal", "Writing Sample", "Portfolio", "Other"];
const statusOptions = ["draft", "ready", "submitted"];

function formatBytes(size?: number | null) {
  if (!size) return "--";
  if (size < 1024 * 1024) return `${Math.round(size / 1024)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

export default function Documents({ params }: { params: Promise<{ locale: string }> }) {
  const [locale, setLocale] = useState("en");
  const zh = locale === "zh";
  const [applicant, setApplicant] = useState<Applicant | null>(null);
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [programId, setProgramId] = useState<number | null>(null);
  const [documentType, setDocumentType] = useState("CV");
  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState("");
  const [checklist, setChecklist] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ locale }) => setLocale(locale));
  }, [params]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const current = await getDefaultApplicant();
      const [documentItems, programItems] = await Promise.all([getDocuments(current.id), getPrograms({ limit: 30 })]);
      setApplicant(current);
      setDocs(documentItems);
      setPrograms(programItems);
      setProgramId((currentProgramId) => currentProgramId || programItems[0]?.id || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const sortedDocs = useMemo(() => [...docs].sort((a, b) => a.type.localeCompare(b.type)), [docs]);

  async function submitUpload() {
    if (!applicant || !file) return;
    setUploading(true);
    setError(null);
    setMessage(null);
    try {
      await uploadDocument(applicant.id, documentType, file, notes);
      setMessage(zh ? "文件上传成功" : "File uploaded successfully");
      setFile(null);
      setNotes("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
    }
  }

  async function setStatus(doc: DocumentItem, status: string) {
    setError(null);
    try {
      const updated = await updateDocumentStatus(doc.id, status);
      setDocs((current) => current.map((item) => item.id === doc.id ? updated : item));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function remove(doc: DocumentItem) {
    setError(null);
    try {
      await deleteDocument(doc.id);
      setDocs((current) => current.filter((item) => item.id !== doc.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function buildChecklist() {
    if (!applicant || !programId) return;
    setError(null);
    try {
      setChecklist(await generateDocumentChecklist(applicant.id, programId));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <AppShell locale={locale}>
      <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-bold">{zh ? "材料中心" : "Materials Hub"}</h1>
          <p className="mt-2 text-sm text-muted">{applicant ? `${applicant.full_name} · ${applicant.email}` : (zh ? "正在加载申请人" : "Loading applicant")}</p>
        </div>
        <Button onClick={load}>{zh ? "刷新" : "Refresh"}</Button>
      </div>

      <div className="mb-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        {zh ? "当前 MVP 文件保存在本地环境。除非你信任当前本地环境，否则不要上传真实敏感官方文件。" : "Files are stored locally in this MVP. Do not upload sensitive official documents unless you trust your local environment."}
      </div>

      {message && <Card className="mb-4 p-4 text-sm text-emerald-700">{message}</Card>}
      {error && <Card className="mb-4 p-4 text-sm text-rose-700">{error}</Card>}

      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <div className="space-y-6">
          <Card className="p-5">
            <h3 className="font-semibold">{zh ? "上传材料" : "Upload Document"}</h3>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <label className="text-sm font-medium">
                {zh ? "材料类型" : "Document Type"}
                <select value={documentType} onChange={(event) => setDocumentType(event.target.value)} className="mt-2 w-full rounded-xl border border-line px-3 py-2 text-sm">
                  {documentTypes.map((type) => <option key={type} value={type}>{documentName(type, locale)}</option>)}
                </select>
              </label>
              <label className="text-sm font-medium">
                {zh ? "选择文件" : "Choose File"}
                <input type="file" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" onChange={(event) => setFile(event.target.files?.[0] || null)} className="mt-2 w-full rounded-xl border border-line px-3 py-2 text-sm" />
              </label>
              <label className="text-sm font-medium md:col-span-2">
                {zh ? "备注" : "Notes"}
                <textarea value={notes} onChange={(event) => setNotes(event.target.value)} className="mt-2 h-24 w-full rounded-xl border border-line px-3 py-2 text-sm outline-none focus:border-brand" />
              </label>
            </div>
            <Button className="mt-4" disabled={!file || uploading} onClick={submitUpload}>{uploading ? (zh ? "上传中..." : "Uploading...") : (zh ? "上传" : "Upload")}</Button>
          </Card>

          {loading ? <Card className="p-5 text-sm text-muted">{zh ? "正在加载材料..." : "Loading documents..."}</Card> : null}
          {!loading && sortedDocs.length === 0 ? (
            <Card className="p-8 text-sm text-muted">{zh ? "还没有上传材料。你可以先上传 CV、成绩单或个人陈述。" : "No documents uploaded yet. Upload your CV, transcript, or personal statement to get started."}</Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {sortedDocs.map((doc) => (
                <Card key={doc.id} className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-semibold">{documentName(doc.type, locale)}</div>
                      <p className="mt-1 break-all text-xs text-muted">{doc.original_filename || doc.name}</p>
                    </div>
                    <Badge tone={doc.status === "ready" || doc.status === "submitted" ? "success" : doc.status === "draft" ? "warning" : "danger"}>{tValue(doc.status, locale)}</Badge>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-muted">
                    <div>{zh ? "大小" : "Size"}<br /><b className="text-ink">{formatBytes(doc.file_size)}</b></div>
                    <div>{zh ? "版本" : "Version"}<br /><b className="text-ink">v{doc.version || 1}</b></div>
                    <div>{zh ? "类型" : "Content type"}<br /><b className="break-all text-ink">{doc.content_type || "--"}</b></div>
                    <div>{zh ? "上传时间" : "Uploaded"}<br /><b className="text-ink">{doc.uploaded_at?.slice(0, 10) || "--"}</b></div>
                  </div>
                  {doc.notes && <p className="mt-3 text-sm text-muted">{doc.notes}</p>}
                  <div className="mt-4 flex flex-wrap gap-2">
                    {doc.download_url && <a className="rounded-xl border border-line px-3 py-2 text-xs font-semibold" href={downloadDocument(doc.id)}>{zh ? "下载" : "Download"}</a>}
                    {statusOptions.map((status) => <button key={status} onClick={() => setStatus(doc, status)} className="rounded-xl border border-line px-3 py-2 text-xs font-semibold">{status === "draft" ? (zh ? "标记为草稿" : "Mark Draft") : status === "ready" ? (zh ? "标记为已准备" : "Mark Ready") : (zh ? "标记为已提交" : "Mark Submitted")}</button>)}
                    <button onClick={() => remove(doc)} className="rounded-xl bg-rose-600 px-3 py-2 text-xs font-semibold text-white">{zh ? "删除" : "Delete"}</button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        <Card className="p-5">
          <h3 className="font-semibold">{zh ? "项目材料清单" : "Application Checklist"}</h3>
          <p className="mt-2 text-sm text-muted">{zh ? "选择一个项目，根据项目要求和你的本地材料状态生成清单。" : "Choose a program to compare requirements with your local document status."}</p>
          <select value={programId || ""} onChange={(event) => setProgramId(Number(event.target.value))} className="mt-4 w-full rounded-xl border border-line px-3 py-2 text-sm">
            {programs.map((program) => <option key={program.id} value={program.id}>{program.program_name}</option>)}
          </select>
          <Button className="mt-4 w-full" onClick={buildChecklist}>{zh ? "生成材料清单" : "Generate Checklist"}</Button>
          {checklist ? (
            <div className="mt-5 space-y-4 text-sm">
              <ChecklistGroup title={zh ? "必需材料" : "Required Documents"} items={checklist.required_documents?.map((item: any) => item.document_type) || []} tone="brand" />
              <ChecklistGroup title={zh ? "已准备材料" : "Ready Documents"} items={checklist.ready_documents?.map((item: any) => item.required.document_type) || []} tone="success" />
              <ChecklistGroup title={zh ? "已提交材料" : "Submitted Documents"} items={checklist.submitted_documents?.map((item: any) => item.required.document_type) || []} tone="success" />
              <ChecklistGroup title={zh ? "缺失材料" : "Missing Documents"} items={checklist.missing_documents?.map((item: any) => item.required.document_type) || []} tone="danger" />
              {checklist.warnings?.map((warning: string) => <p key={warning} className="rounded-xl bg-amber-50 p-3 text-xs text-amber-800">{warning}</p>)}
            </div>
          ) : <p className="mt-4 text-sm text-muted">{zh ? "生成后会显示缺失、已准备和已提交材料。" : "Generated checklist will show missing, ready, and submitted documents."}</p>}
        </Card>
      </div>
    </AppShell>
  );
}

function ChecklistGroup({ title, items, tone }: { title: string; items: string[]; tone: "brand" | "success" | "danger" }) {
  return (
    <div>
      <div className="mb-2 font-semibold">{title}</div>
      <div className="flex flex-wrap gap-2">
        {items.length ? items.map((item) => <Badge key={item} tone={tone}>{item}</Badge>) : <span className="text-xs text-muted">--</span>}
      </div>
    </div>
  );
}
