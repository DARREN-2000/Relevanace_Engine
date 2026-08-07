# 🏗️ Architecture — Consentinel

## System Overview

Consentinel is a **consent-first, AI-powered next-best-action (NBA) platform** for marketing automation. Unlike traditional marketing tools that blast messages to segments, Consentinel evaluates each user individually and decides:

1. **Whether** to send anything at all
2. **What** message/action to take
3. **Where** (which channel) to deliver it
4. **When** to send it (respecting quiet hours and fatigue)
5. **How** to optimize (via experiments)

### Design Philosophy

- **Consent is non-negotiable**: Every action passes through consent verification
- **"Do nothing" is valid**: Suppression of irrelevant marketing is a feature
- **Explainability**: Every decision can be traced and explained
- **Compliance by design**: GDPR, CCPA, and regional regulations are built in
- **AI-augmented, human-governed**: AI agents suggest, governance gates approve

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (FastAPI)                     │
│  /users  /consents  /events  /decisions  /journeys  /analytics  │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Core Decision Engine                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   Scoring     │  │   Fatigue    │  │   Suppression Engine  │  │
│  │   Engine      │  │   Engine     │  │                       │  │
│  │              │  │              │  │  • Consent check       │  │
│  │  • Intent    │  │  • Volume    │  │  • Fatigue check       │  │
│  │  • Churn     │  │  • Engagement│  │  • Frequency cap       │  │
│  │  • Activation│  │  • Threshold │  │  • Quiet hours         │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────┘  │
│         │                 │                      │               │
│         ▼                 ▼                      ▼               │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              NextBestActionEngine                        │    │
│  │                                                          │    │
│  │  Input: user_id → Output: (channel, action, confidence) │    │
│  │                                                          │    │
│  │  Decision Flow:                                          │    │
│  │  1. Already activated? → none                            │    │
│  │  2. Fatigued? → pause                                    │    │
│  │  3. High intent + high value → CRM handoff               │    │
│  │  4. High intent + email consent → educate                │    │
│  │  5. High churn + email consent → remind                  │    │
│  │  6. Medium intent + push → educate                       │    │
│  │  7. Ad personalization → retarget                        │    │
│  │  8. No valid action → suppress                           │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              Consent Engine                              │    │
│  │                                                          │    │
│  │  • Channel consent verification                          │    │
│  │  • Quiet hours enforcement                               │    │
│  │  • Frequency cap management                              │    │
│  │  • Consent summary generation                            │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
       │                                    │
       ▼                                    ▼
┌──────────────────┐              ┌───────────────────┐
│   PostgreSQL     │              │   Redis           │
│                  │              │                   │
│  • Users         │              │  • Session cache  │
│  • Consents      │              │  • Rate limiting  │
│  • Events        │              │  • Score cache    │
│  • Decisions     │              │                   │
│  • Journeys      │              └───────────────────┘
│  • Experiments   │
│  • Audiences     │
│  • Audit logs    │
└──────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                        AI Agents Layer                            │
│                                                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │  Segment   │ │  Journey   │ │   Copy     │ │  Experiment  │  │
│  │  Agent     │ │  Agent     │ │   Agent    │ │  Agent       │  │
│  │            │ │            │ │            │ │              │  │
│  │  Generate  │ │  Design    │ │  Generate  │ │  Design A/B  │  │
│  │  audiences │ │  multi-step│ │  message   │ │  tests       │  │
│  │  from data │ │  journeys  │ │  copy      │ │              │  │
│  └────────────┘ └────────────┘ └────────────┘ └──────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                  Governance Agent                        │    │
│  │  • Compliance checking (GDPR, CCPA)                      │    │
│  │  • Content approval gates                                │    │
│  │  • Audit trail generation                                │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Model Overview

### Core Tables

| Table                 | Purpose                              | Key Fields                                                                        |
| --------------------- | ------------------------------------ | --------------------------------------------------------------------------------- |
| `users`               | User profiles with behavioral scores | email, lifecycle_stage, intent_score, churn_risk, activation_score, fatigue_score |
| `consents`            | Per-channel consent records          | user_id, channel, status (granted/denied), source, region                         |
| `channel_preferences` | User channel preferences             | frequency_cap_daily/weekly, quiet_hours_start/end                                 |
| `events`              | Behavioral event stream              | user_id, event_type, event_name, properties (JSON)                                |
| `message_decisions`   | Decision audit trail                 | channel, action, reason, consent_checked, suppressed, model_confidence            |
| `audiences`           | Segmentation definitions             | name, criteria (JSON), auto_refresh                                               |
| `journey_templates`   | Multi-step journey definitions       | name, goal, steps (JSON)                                                          |
| `journey_runs`        | User journey instances               | user_id, template_id, current_step, status                                        |
| `experiments`         | A/B test definitions                 | hypothesis, variants (JSON), status                                               |
| `audit_events`        | Compliance audit trail               | event_type, actor, details                                                        |
| `approval_requests`   | Content approval workflow            | content_type, status, reviewer                                                    |

### Entity Relationships

```
User ──┬── has many ──→ Consents
       ├── has many ──→ ChannelPreferences
       ├── has many ──→ Events
       ├── has many ──→ MessageDecisions
       └── has many ──→ JourneyRuns

JourneyTemplate ── has many ──→ JourneyRuns
Experiment ── referenced by ──→ MessageDecisions
```

---

## Core Engine: Next-Best-Action Flow

The NBA engine is the heart of Consentinel. For each user, it executes this decision tree:

```
                    ┌─────────────────┐
                    │   User Request   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Already         │──── Yes ──→ action: none
                    │  Activated?      │            reason: "already activated"
                    └────────┬────────┘
                             │ No
                    ┌────────▼────────┐
                    │  Fatigued?       │──── Yes ──→ action: pause
                    │  (score > 0.8)   │            reason: "user fatigued"
                    └────────┬────────┘
                             │ No
                    ┌────────▼────────┐
                    │  High Intent +   │──── Yes ──→ channel: crm_task
                    │  High Value?     │            action: handoff
                    └────────┬────────┘             confidence: 0.9
                             │ No
                    ┌────────▼────────┐
                    │  High Intent +   │──── Yes ──→ channel: email
                    │  Email Consent?  │            action: educate
                    └────────┬────────┘             confidence: 0.85
                             │ No
                    ┌────────▼────────┐
                    │  High Churn +    │──── Yes ──→ channel: email
                    │  Email Consent?  │            action: remind
                    └────────┬────────┘             confidence: 0.8
                             │ No
                    ┌────────▼────────┐
                    │  Medium Intent + │──── Yes ──→ channel: push
                    │  Push Consent?   │            action: educate
                    └────────┬────────┘             confidence: 0.7
                             │ No
                    ┌────────▼────────┐
                    │  Ad Consent?     │──── Yes ──→ channel: ad_audience
                    └────────┬────────┘             action: offer
                             │ No                   confidence: 0.6
                    ┌────────▼────────┐
                    │  In-App          │──── Yes ──→ channel: in_app
                    │  Consent?        │            action: educate
                    └────────┬────────┘             confidence: 0.5
                             │ No
                    ┌────────▼────────┐
                    │   No Valid       │──────────→ channel: none
                    │   Action         │            action: none
                    └─────────────────┘            reason: "no compliant action"
```

---

## AI Agents Architecture

The agents layer provides AI-powered capabilities. Currently implemented as mock/placeholder services, designed for future LLM integration:

| Agent               | Purpose                                       | Interface                                       |
| ------------------- | --------------------------------------------- | ----------------------------------------------- |
| **SegmentAgent**    | Generate audience segments from data patterns | `generate_segment(data_points, goal)`           |
| **JourneyAgent**    | Design multi-step journey sequences           | `design_journey(audience, goal)`                |
| **CopyAgent**       | Generate message copy per channel/action      | `generate_copy(channel, action, audience)`      |
| **ExperimentAgent** | Design A/B experiments with variants          | `design_experiment(hypothesis, audience, goal)` |
| **GovernanceAgent** | Check compliance against rules                | `check_compliance(decision, rules, user_data)`  |

### Future Integration Points

Each agent is designed to be swapped with a real LLM-backed implementation:

- OpenAI GPT-4 / Claude for copy generation
- Custom ML models for scoring refinement
- RAG-based agents for compliance checking against regulation documents

---

## Channel Connectors

The platform supports these communication channels:

| Channel       | Type        | Consent Required                 |
| ------------- | ----------- | -------------------------------- |
| `email`       | Outbound    | Yes — explicit opt-in            |
| `sms`         | Outbound    | Yes — explicit opt-in            |
| `push`        | Outbound    | Yes — device permission          |
| `crm_task`    | Internal    | No — internal handoff            |
| `ad_audience` | Retargeting | Yes — ad personalization consent |
| `in_app`      | In-product  | Yes — in-app messaging consent   |
| `none`        | Suppression | N/A — no action taken            |

---

## Integration with ConsentHub (B2B_Consent_Personalization)

Consentinel is designed to work alongside the **ConsentHub** project (`B2B_Consent_Personalization`). The integration provides:

1. **Consent Data Sync**: ConsentHub serves as the authoritative source for user consent preferences
2. **Preference Management**: Channel preferences and quiet hours flow from ConsentHub
3. **Compliance Verification**: ConsentHub's compliance engine validates decisions before execution
4. **Audit Trail**: Both systems maintain linked audit trails for regulatory compliance

### Integration Configuration

```env
CONSENTHUB_API_URL=https://consenthub.example.com/api
CONSENTHUB_API_KEY=your-api-key
```

When configured, Consentinel will:

- Fetch consent data from ConsentHub before making decisions
- Push decision audit events to ConsentHub
- Respect ConsentHub's preference center configurations
- Honor ConsentHub's suppression lists

When not configured, Consentinel operates standalone using its own consent tables.

---

## Security Architecture

- **Non-root containers**: All Docker images run as unprivileged users
- **Read-only filesystem**: Kubernetes pods use read-only root filesystem
- **Secret management**: Sensitive values stored in Kubernetes Secrets, never in code
- **CORS**: Configurable allowed origins
- **JWT Authentication**: Token-based API authentication (configurable expiry)
- **Audit logging**: All consent changes and decisions are logged
- **Pod security**: RunAsNonRoot, no privilege escalation
