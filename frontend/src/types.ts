// Chatita Mail v3.0 - shared types (mirror backend schemas)

export type EmailCategory =
  | "CRITICAL"
  | "IMPORTANT"
  | "MEDIUM"
  | "LOW"
  | "SPAM"
  | "NOISE"
  | "UNCLASSIFIED";

export type EmailStatus =
  | "INBOX"
  | "ARCHIVED"
  | "QUARANTINED"
  | "BLOCKED"
  | "DELETED";

export type RiskLevel = "safe" | "suspicious" | "dangerous";

export interface EmailListItem {
  id: string;
  from_address: string;
  from_name: string | null;
  subject: string | null;
  snippet: string | null;
  status: EmailStatus;
  is_read: boolean;
  received_at: string | null;
  category: EmailCategory | null;
  confidence: number | null;
  risk_level: RiskLevel | null;
  risk_score: number | null;
}

export interface ClassificationDetail {
  category: EmailCategory;
  confidence: number;
  stage: string;
  reasoning: string | null;
}

export interface SecurityDetail {
  risk_score: number;
  risk_level: RiskLevel;
  explanation: string | null;
  risk_factors: string[];
  recommended_action: string;
}

export interface EmailDetail {
  id: string;
  from_address: string;
  from_name: string | null;
  subject: string | null;
  body_text: string | null;
  status: EmailStatus;
  received_at: string | null;
  classification: ClassificationDetail | null;
  security: SecurityDetail | null;
}
