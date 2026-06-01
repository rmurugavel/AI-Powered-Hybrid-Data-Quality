# AI-Powered-Hybrid-Data-Quality

# AI Hybrid Data Quality Sentinel

A production-grade data quality validation framework combining
traditional SQL rule-based validation with AI semantic validation
for unstructured enterprise data fields.

## The Problem It Solves

SQL-based data quality tools validate structured fields well —
null checks, referential integrity, range validation. But they
cannot evaluate whether a free-text field is *meaningful*.

In enterprise financial systems, fields like commission adjustment
notes and dispute reasons are critical for audit compliance — but
their quality cannot be measured with SQL alone.

This system solves that by combining:
- **Great Expectations** for structured CDE validation
- **Ollama (local LLM)** for semantic validation of sensitive
  text fields — no data leaves the governance boundary
- **Unified HTML quality dashboard** showing results across
  both validation layers

## Architecture
[See diagram in /docs/architecture.png]

## CDE Coverage
- Consultant ID — referential integrity
- Commission Amount — null, zero, variance threshold
- Payment Period — valid open period
- Adjustment Note — AI: business justification completeness
- Dispute Reason — AI: specificity and traceability

## Output
HTML quality report with pass/fail per CDE, severity rating,
AI finding summary, and remediation flags.

## Governance Design Principles
- Sensitive data validated locally (Ollama) — never transmitted
  externally
- AI findings are advisory — human data owner approval required
  for remediation
- CDE registry in version-controlled JSON — governance rules
  are auditable
- Run history logged for audit trail

## Built With
Python · Great Expectations · Ollama · Gemini API · BigQuery · GCP

---
Designed by Rasmi Murugavel | linkedin.com/in/mrasmi
