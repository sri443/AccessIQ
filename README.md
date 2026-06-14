# AccessIQ

> Making Identity Risk Visible, Explainable, and Actionable

AccessIQ is an Identity Risk Intelligence platform that identifies identity sprawl, excessive privileges, dormant accounts, and hidden access risks through graph analytics, behavioral baselines, and blast-radius modeling.

## Problem

Organizations struggle with:

- Stale and dormant accounts
- Excessive privileges
- Identity sprawl
- Lack of contextual risk visibility
- Compliance audit complexity

## Solution

AccessIQ transforms raw identity and event data into actionable security intelligence by combining:

- Identity Graph Analytics
- Behavioral Anomaly Detection
- Context-Aware Risk Scoring
- Blast Radius Analysis
- Compliance Framework Mapping

## Architecture

```text
Identity Data + Event Logs
            │
            ▼
      Data Ingestion
            │
            ▼
      Identity Graph
            │
            ▼
      Risk Analysis
            │
            ▼
    Context Evaluation
            │
            ▼
 Compliance Mapping
            │
            ▼
 Executive Dashboard
```

## Key Features

### Identity Graph Intelligence

- Detect hidden access relationships
- Identify privilege concentrations
- Surface cross-department access

### Behavioral Analytics

- Role-based baselines
- Z-score anomaly detection
- Login and activity analysis

### Blast Radius Modeling

Evaluates potential breach impact using:

- Asset sensitivity
- Privilege concentration
- Lateral movement potential

### Compliance Mapping

Automatically maps findings to:

- SOC 2
- NIST 800-53
- ISO 27001

## Example Findings

- Stale Accounts
- Over-Privileged Users
- Orphaned Service Accounts
- Cross-Department Access Violations

## Technology Stack

| Layer | Technology |
|---------|------------|
| Backend | FastAPI, Python, Pandas |
| Graph Engine | NetworkX |
| Analytics | Statistical Baselines, Heuristics |
| Frontend | HTML, CSS, JavaScript |

## Benefits

- Faster risk triage
- Reduced investigation effort
- Explainable security findings
- Audit-ready compliance reporting

## Future Enhancements

- Active Directory Integration
- Azure AD Integration
- AWS IAM Integration
- Real-Time Risk Monitoring
- Automated Remediation

## Repository

```bash
git clone https://github.com/sri443/AccessIQ.git
```

## Team

**TEAM XYZ**  
Hackathon 2026  
Identity Sprawl & Privilege Abuse Track

---

### AccessIQ

**Transforming Identity Data into Actionable Security Intelligence**
