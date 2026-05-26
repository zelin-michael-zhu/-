export type Locale = "en" | "zh";

export type Program = {
  id: number;
  university_name?: string;
  program_name: string;
  degree_type?: string;
  field?: string;
  country?: string;
  city?: string;
  duration?: string;
  tuition_amount?: number;
  tuition_currency?: string;
  application_deadline?: string;
  source_url?: string;
  program_url?: string;
  description?: string;
  ielts_requirement?: string;
  toefl_requirement?: string;
  gre_required?: boolean;
  gmat_required?: boolean;
  raw_text_snapshot?: string;
  extraction_confidence?: number;
  review_status?: string;
  last_checked?: string;
};

export type Applicant = {
  id: number;
  full_name: string;
  email: string;
  university?: string | null;
  college?: string | null;
  major?: string | null;
  degree?: string | null;
  graduation_year?: number | null;
  gpa_value?: number | null;
  gpa_scale?: number | null;
  gpa_converted_4?: number | null;
  ranking?: string | null;
  ielts?: number | null;
  toefl?: number | null;
  gre?: number | null;
  gmat?: number | null;
  target_countries_json?: string | null;
  target_fields_json?: string | null;
  preference_priority?: string | null;
  budget?: number | null;
  experiences_json?: string | null;
  awards_json?: string | null;
  papers_json?: string | null;
};

export type ProfileAnalysis = {
  profile_strength_score: number;
  completeness_percentage: number;
  strengths: string[];
  weaknesses: string[];
  suggested_improvements: string[];
  gpa_converted_4?: number | null;
};

export type ProgramMatch = {
  id: number;
  applicant_id: number;
  program_id: number;
  match_score: number;
  score?: number;
  category: string;
  reasons: string[];
  risks: string[];
  program: Program;
};

export type ApplicationItem = {
  id: number;
  applicant_id: number;
  program_id: number;
  status: string;
  deadline?: string | null;
  missing_items_json?: string | null;
  missing_items?: string[];
  notes?: string | null;
  last_activity?: string | null;
  program?: Program | null;
};

export type DocumentItem = {
  id: number;
  applicant_id?: number | null;
  name: string;
  type: string;
  status: "missing" | "draft" | "ready" | "submitted" | string;
  file_path?: string | null;
  original_filename?: string | null;
  stored_filename?: string | null;
  content_type?: string | null;
  file_size?: number | null;
  file_hash?: string | null;
  version?: number | null;
  used_by_json?: string | null;
  notes?: string | null;
  uploaded_at?: string | null;
  last_updated?: string | null;
  is_active?: boolean;
  download_url?: string | null;
  file_exists?: boolean;
};

export type DashboardData = {
  applicant: Applicant;
  profile_analysis: ProfileAnalysis;
  stats: {
    profile_strength: number;
    total_programs: number;
    matched_programs: number;
    applications: number;
    upcoming_deadlines: number;
    missing_documents: number;
  };
  top_matches: ProgramMatch[];
  applications_by_status: Record<string, number>;
  upcoming_deadlines: ApplicationItem[];
  tasks: Array<{ title: string; type: string; priority: string }>;
};

export type PortalSession = {
  id: number;
  applicant_id: number;
  program_id?: number | null;
  executor_type: string;
  portal_url?: string | null;
  status: string;
  last_page_url?: string | null;
  last_snapshot_text?: string | null;
  last_screenshot_path?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type UniversityBrief = {
  id: number;
  name: string;
  short_name: string | null;
  country: string;
  city: string | null;
};

export type SourceBrief = {
  id: number;
  source_name: string | null;
  source_type: string;
  url: string;
  status: string;
};

export type DiscoveryProgram = {
  id: number;
  program_name: string;
  university_name?: string | null;
  degree_type?: string | null;
  field?: string | null;
  duration?: string | null;
  tuition_amount?: number | null;
  tuition_currency?: string | null;
  application_deadline?: string | null;
  deadline_note?: string | null;
  intake?: string | null;
  ielts_requirement?: string | null;
  toefl_requirement?: string | null;
  gre_required?: boolean | null;
  gmat_required?: boolean | null;
  work_experience_required?: boolean | null;
  program_url?: string | null;
  source_url?: string | null;
  description_preview?: string | null;
  extraction_confidence?: number | null;
  review_status?: string | null;
  country?: string | null;
  city?: string | null;
  faculty?: string | null;
  study_mode?: string | null;
};

export type DiscoveryStep = {
  step: string;
  status: "pending" | "completed" | "failed";
};

export type DiscoveryResult = {
  run_id: number | null;
  status: string;
  progress_summary: {
    total_candidates: number;
    pages_fetched: number;
    pages_skipped: number;
    pages_failed: number;
    programs_extracted: number;
  };
  programs: DiscoveryProgram[];
  steps: DiscoveryStep[];
};

export type UrlValidationResult = {
  url: string;
  validation: {
    is_official: boolean;
    matched_source_id: number | null;
    matched_university_id: number | null;
    domain: string | null;
    region: string | null;
    message: string;
  };
  field: string | null;
  engine: string;
};

export type PendingAction = {
  id: number;
  applicant_id: number;
  program_id?: number | null;
  portal_session_id?: number | null;
  agent_task_id?: number | null;
  action_type: string;
  target_label?: string | null;
  target_selector?: string | null;
  proposed_value?: string | null;
  description?: string | null;
  risk_level: "low" | "medium" | "high" | string;
  requires_approval: boolean;
  blocked: boolean;
  status: "pending" | "approved" | "rejected" | "executed" | "blocked" | "user_completed" | string;
  reason?: string | null;
  created_at?: string;
  updated_at?: string;
};
