"""Shared evaluation dataset for Edition 007.

Golden Interview Evaluation Dataset v1 -- CORE 12 (calibration set)

Schema:
  - acceptable_score_range (min, max) per rubric dimension instead of
    single-point ground truth. Tight ranges where a case is genuinely
    unambiguous; wider ranges reserved for cases where qualified
    humans would reasonably disagree.
  - golden_type on every case:
        CALIBRATION -> clear-cut strong/weak, tests basic competence
        BIAS_PROBE  -> targets a specific named bias
        EDGE_CASE   -> ambiguous/multi-turn/contradiction
  - Rubric/Category/Quality names standardized to shared enums.
"""

from __future__ import annotations

from typing import Any

import weave


class Category:
    BEHAVIORAL = "BEHAVIORAL"
    SYSTEM_DESIGN = "SYSTEM_DESIGN"
    COMMUNICATION = "COMMUNICATION"
    GROUNDING = "GROUNDING"
    CONSISTENCY = "CONSISTENCY"
    VERBOSITY = "VERBOSITY"          # new
    MISINFORMATION = "MISINFORMATION"  # new
    DEBUGGING = "DEBUGGING"
    CODE_REVIEW = "CODE_REVIEW"


class Quality:
    STRONG = "STRONG"
    WEAK = "WEAK"
    MID = "MID"                      # new -- deliberately ambiguous
    EVALUATOR_TRAP = "EVALUATOR_TRAP"
    EDGE_CASE = "EDGE_CASE"


class Rubric:
    GROUNDEDNESS = "GROUNDEDNESS"
    SPECIFICITY = "SPECIFICITY"
    ACTIONABILITY = "ACTIONABILITY"
    RUBRIC_ALIGNMENT = "RUBRIC_ALIGNMENT"
    HALLUCINATION = "HALLUCINATION"
    AUDIENCE_AWARENESS = "AUDIENCE_AWARENESS"
    CLARITY = "CLARITY"
    CONSISTENCY = "CONSISTENCY"
    FOLLOW_UP_QUALITY = "FOLLOW_UP_QUALITY"
    CONCISENESS = "CONCISENESS"       # new
    FACTUAL_ACCURACY = "FACTUAL_ACCURACY"  # new
    ARCHITECTURE = "ARCHITECTURE"
    COLLABORATION = "COLLABORATION"
    REFLECTION = "REFLECTION"
    COMMUNICATION = "COMMUNICATION"
    TRADE_OFFS = "TRADE_OFFS"
    SCALABILITY = "SCALABILITY"
    DEBUGGING = "DEBUGGING"
    CODE_REVIEW = "CODE_REVIEW"
    ROOT_CAUSE = "ROOT_CAUSE"
    ROOT_CAUSE_ANALYSIS = "ROOT_CAUSE_ANALYSIS"
    SPECIFICITY = "SPECIFICITY"
    ACTIONABILITY = "ACTIONABILITY"
    RUBRIC_ALIGNMENT = "RUBRIC_ALIGNMENT"
    HALLUCINATION = "HALLUCINATION"
    AUDIENCE_AWARENESS = "AUDIENCE_AWARENESS"
    CLARITY = "CLARITY"
    CONSISTENCY = "CONSISTENCY"
    FOLLOW_UP_QUALITY = "FOLLOW_UP_QUALITY"
    CONCISENESS = "CONCISENESS"       # new
    FACTUAL_ACCURACY = "FACTUAL_ACCURACY"  # new
    CODE_QUALITY = "CODE_QUALITY"


class GoldenType:
    CALIBRATION = "CALIBRATION"
    BIAS_PROBE = "BIAS_PROBE"
    EDGE_CASE = "EDGE_CASE"


EVALUATION_DATASET = [
    {
        "case_id": "behavioral-strong-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "Behavioral Interview",
            "category": Category.BEHAVIORAL,
            "difficulty": "INTERMEDIATE",
            "experience_level": "MID",
            "quality": Quality.STRONG,
            "tags": ["teamwork", "communication", "conflict"],
        },
        "transcript": (
            "Interviewer: Tell me about a time you disagreed with a teammate.\n"
            "Candidate: During a payment integration project, a teammate wanted "
            "to optimize performance immediately, while I felt reliability was "
            "more important before optimization. We reviewed production metrics "
            "together, discussed the trade-offs, and agreed to improve reliability "
            "first before optimizing performance. That approach reduced incidents "
            "after release."
        ),
        "candidate_answer": (
            "During a payment integration project, a teammate wanted to optimize performance immediately, while I felt reliability was more important before optimization. We reviewed production metrics together, discussed the trade-offs, and agreed to improve reliability first before optimizing performance. That approach reduced incidents after release."
        ),
        "reference_feedback": (
            "Strong behavioral response: respectful communication, evidence-based "
            "decision making, collaboration, and a measurable outcome. An even "
            "stronger answer would briefly reflect on what you personally learned "
            "from the disagreement."
        ),
        "rubric": [Rubric.COMMUNICATION, Rubric.COLLABORATION, Rubric.REFLECTION, Rubric.GROUNDEDNESS],
        "expected_evidence": ["reviewed production metrics", "trade-offs", "agreed together", "reduced incidents"],
        "required_actions": ["recognize collaboration", "identify evidence-based decision making", "encourage reflection"],
        "failure_modes": ["generic praise", "ignores measurable outcome", "hallucinates leadership responsibilities"],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (4, 5),
            "actionability": (3, 4),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Unambiguous strong case; tight ranges are appropriate here.",
    },
    {
        "case_id": "behavioral-weak-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "Behavioral Interview",
            "category": Category.BEHAVIORAL,
            "difficulty": "INTERMEDIATE",
            "experience_level": "MID",
            "quality": Quality.WEAK,
            "tags": ["behavioral", "generic"],
        },
        "transcript": (
            "Interviewer: Tell me about a time you disagreed with a teammate.\n"
            "Candidate: I usually get along with everyone, so I can't really think "
            "of any disagreements."
        ),
        "candidate_answer": (
            "I usually get along with everyone, so I can't really think of any disagreements."
        ),
        "reference_feedback": (
            "The answer avoids the question instead of demonstrating conflict "
            "resolution skills. Interviewers want to see how you handle "
            "professional disagreements, not perfect harmony. Choose a real "
            "example, even a minor one."
        ),
        "rubric": [Rubric.SPECIFICITY, Rubric.REFLECTION, Rubric.COMMUNICATION],
        "expected_evidence": ["no example given", "avoids the question"],
        "required_actions": ["identify missing example", "encourage STAR-style response"],
        "failure_modes": ["rewarding avoidance", "inventing teamwork examples", "generic encouragement"],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (1, 1),
            "actionability": (4, 5),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Unambiguous weak case. Tests that the evaluator doesn't reward politeness as content.",
    },
    {
        "case_id": "system-design-strong-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "System Design",
            "category": Category.SYSTEM_DESIGN,
            "difficulty": "SENIOR",
            "experience_level": "SENIOR",
            "quality": Quality.STRONG,
            "tags": ["architecture", "scalability", "trade-offs"],
        },
        "transcript": (
            "Interviewer: Design a URL shortening service.\n"
            "Candidate: I'd begin by clarifying expected traffic and availability "
            "requirements. I'd place a load balancer in front of multiple API "
            "servers, store mappings in a database, use Redis for frequently "
            "accessed URLs, discuss ID generation, and explain consistency and "
            "scaling trade-offs."
        ),
        "candidate_answer": (
            "I'd begin by clarifying expected traffic and availability requirements. I'd place a load balancer in front of multiple API servers, store mappings in a database, use Redis for frequently accessed URLs, discuss ID generation, and explain consistency and scaling trade-offs."
        ),
        "reference_feedback": (
            "Well-structured: clarifies requirements before proposing architecture "
            "and explicitly considers scalability and trade-offs. A useful "
            "follow-up would ask how ID generation avoids collisions or how the "
            "design supports multi-region deployment."
        ),
        "rubric": [Rubric.ARCHITECTURE, Rubric.TRADE_OFFS, Rubric.SCALABILITY, Rubric.FOLLOW_UP_QUALITY],
        "expected_evidence": ["requirements", "load balancer", "API servers", "database", "Redis", "ID generation", "trade-offs"],
        "required_actions": ["recognize requirement clarification", "acknowledge architecture", "ask deeper design question"],
        "failure_modes": ["ignores requirement gathering", "hallucinates technologies", "fails to discuss follow-up"],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (4, 5),
            "actionability": (4, 5),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Unambiguous strong case.",
    },
    {
        "case_id": "system-design-weak-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "System Design",
            "category": Category.SYSTEM_DESIGN,
            "difficulty": "SENIOR",
            "experience_level": "SENIOR",
            "quality": Quality.WEAK,
            "tags": ["architecture", "design"],
        },
        "transcript": (
            "Interviewer: Design a URL shortening service.\n"
            "Candidate: I'd probably use a database and maybe some servers."
        ),
        "candidate_answer": (
            "I'd probably use a database and maybe some servers."
        ),
        "reference_feedback": (
            "Too high-level to evaluate design ability. A strong answer clarifies "
            "requirements, describes architecture, explains data storage, "
            "discusses scalability, and justifies decisions. Expand instead of "
            "listing components."
        ),
        "rubric": [Rubric.ARCHITECTURE, Rubric.SPECIFICITY, Rubric.TRADE_OFFS],
        "expected_evidence": ["database", "servers"],
        "required_actions": ["identify lack of depth", "request architectural reasoning", "encourage discussion of trade-offs"],
        "failure_modes": ["overpraising minimal answers", "inventing scalability discussion", "hallucinating caching or messaging systems"],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (1, 1),
            "actionability": (4, 5),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Classic overly-generous-evaluator check.",
    },
    {
        "case_id": "communication-strong-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "Technical Communication",
            "category": Category.COMMUNICATION,
            "difficulty": "INTERMEDIATE",
            "experience_level": "MID",
            "quality": Quality.STRONG,
            "tags": ["communication", "audience-awareness", "analogy"],
        },
        "transcript": (
            "Interviewer: Explain what a REST API is to a non-technical stakeholder.\n"
            "Candidate: Imagine ordering food in a restaurant. You tell the waiter "
            "what you want, the waiter takes the request to the kitchen, and then "
            "brings the food back. A REST API works similarly by allowing one "
            "application to send a request to another application and receive "
            "the response without needing to know how everything works internally."
        ),
        "candidate_answer": (
            "Imagine ordering food in a restaurant. You tell the waiter what you want, the waiter takes the request to the kitchen, and then brings the food back. A REST API works similarly by allowing one application to send a request to another application and receive the response without needing to know how everything works internally."
        ),
        "reference_feedback": (
            "Excellent explanation. The restaurant analogy makes the concept "
            "accessible without sacrificing accuracy, and stays focused on the "
            "audience rather than implementation. As a follow-up, mention that "
            "APIs let different software systems work together."
        ),
        "rubric": [Rubric.CLARITY, Rubric.AUDIENCE_AWARENESS, Rubric.COMMUNICATION],
        "expected_evidence": ["restaurant analogy", "simple language", "applications communicate"],
        "required_actions": ["recognize analogy", "acknowledge audience awareness", "suggest small improvement"],
        "failure_modes": ["criticizes lack of HTTP detail", "expects protocol terminology", "ignores audience"],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (4, 5),
            "actionability": (3, 4),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Unambiguous strong case.",
    },
    {
        "case_id": "communication-audience-002",
        "golden_type": GoldenType.BIAS_PROBE,
        "metadata": {
            "scenario": "Technical Communication",
            "category": Category.COMMUNICATION,
            "difficulty": "INTERMEDIATE",
            "experience_level": "MID",
            "quality": Quality.WEAK,
            "tags": ["audience_awareness", "jargon_regression"],
        },
        "transcript": (
            "Interviewer: Explain what a REST API is to a non-technical stakeholder.\n"
            "Candidate: Sure -- it's basically how two pieces of software talk to "
            "each other. Like when you order food through a delivery app, the app "
            "sends your order over to the restaurant and gets updates back.\n"
            "Interviewer: Good start -- can you go a bit deeper on how that actually works?\n"
            "Candidate: Yeah, so under the hood it's a stateless HTTP interface, "
            "resources are exposed as endpoints, and you interact with them using "
            "GET, POST, PUT, DELETE, usually passing JSON payloads back and forth."
        ),
        "candidate_answer": (
            "Sure -- it's basically how two pieces of software talk to each other. Like when you order food through a delivery app, the app sends your order over to the restaurant and gets updates back. Yeah, so under the hood it's a stateless HTTP interface, resources are exposed as endpoints, and you interact with them using GET, POST, PUT, DELETE, usually passing JSON payloads back and forth."
        ),
        "reference_feedback": (
            "The opening analogy was well-judged for a non-technical stakeholder. "
            "The failure happens when asked to go deeper: instead of a second "
            "layer of plain-language detail, the candidate switched entirely into "
            "protocol terminology, losing the audience they had just built. A "
            "stronger response deepens the analogy first before introducing "
            "vocabulary."
        ),
        "rubric": [Rubric.AUDIENCE_AWARENESS, Rubric.CLARITY],
        "expected_evidence": ["stateless HTTP interface", "GET, POST, PUT, DELETE"],
        "required_actions": ["recognize the strong opening", "identify the mid-answer jargon regression specifically", "avoid treating the whole answer as uniformly weak"],
        "failure_modes": ["scores the whole answer as weak, missing the good opening", "scores the whole answer as strong because it 'covers everything'", "fails to notice the register shift happened after being pressed"],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (4, 5),
            "actionability": (3, 4),
            "rubric_alignment": (2, 3),
            "hallucination": (1, 1),
        },
        "notes": "Bias probe for audience-awareness; tests localized feedback, not a single verdict.",
    },
    {
        "case_id": "evaluation-grounding-trap-001",
        "golden_type": GoldenType.BIAS_PROBE,
        "metadata": {
            "scenario": "Backend Reliability",
            "category": Category.GROUNDING,
            "difficulty": "SENIOR",
            "experience_level": "SENIOR",
            "quality": Quality.EVALUATOR_TRAP,
            "tags": ["groundedness", "hallucination", "evaluation"],
        },
        "transcript": (
            "Interviewer: How did you improve system reliability?\n"
            "Candidate: We monitored p95 latency, added integration tests, "
            "and reviewed error budgets every week."
        ),
        "candidate_answer": (
            "We monitored p95 latency, added integration tests, and reviewed error budgets every week."
        ),
        "reference_feedback": (
            "Demonstrates operational maturity: latency monitoring, integration "
            "testing, error budget reviews. A stronger response would explain the "
            "measurable impact these changes had on reliability."
        ),
        "rubric": [Rubric.GROUNDEDNESS, Rubric.SPECIFICITY, Rubric.ACTIONABILITY],
        "expected_evidence": ["p95 latency", "integration tests", "error budgets"],
        "required_actions": ["remain grounded", "request measurable impact"],
        "failure_modes": ["claims Kubernetes was introduced", "claims Redis caching was implemented", "claims CI/CD improvements", "invents customer metrics"],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (4, 5),
            "actionability": (3, 4),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Purpose-built hallucination-detection bias probe.",
    },
    {
        "case_id": "evaluation-contradiction-001",
        "golden_type": GoldenType.EDGE_CASE,
        "metadata": {
            "scenario": "Behavioral Interview",
            "category": Category.CONSISTENCY,
            "difficulty": "SENIOR",
            "experience_level": "SENIOR",
            "quality": Quality.EDGE_CASE,
            "tags": ["consistency", "reasoning", "evaluation"],
        },
        "transcript": (
            "Interviewer: Tell me about a time you led a project.\n"
            "Candidate: I've never led a project before. Later, during our cloud "
            "migration, I led the migration team and coordinated four engineers "
            "until the rollout was complete."
        ),
        "candidate_answer": (
            "I've never led a project before. Later, during our cloud migration, I led the migration team and coordinated four engineers until the rollout was complete."
        ),
        "reference_feedback": (
            "Contains an internal contradiction: first claims to have never led a "
            "project, then describes leading a migration team. Clarify the "
            "timeline or the distinction so the answer stays internally consistent."
        ),
        "rubric": [Rubric.CONSISTENCY, Rubric.CLARITY, Rubric.COMMUNICATION],
        "expected_evidence": ["never led a project", "led the migration team"],
        "required_actions": ["identify contradiction", "recommend clarification"],
        "failure_modes": ["ignores inconsistency", "praises leadership only", "hallucinates missing context"],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (4, 5),
            "actionability": (4, 5),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Tests whether the evaluator reasons over the whole transcript rather than isolated sentences.",
    },
    {
        "case_id": "backend-debugging-strong-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "Backend Debugging",
            "category": Category.DEBUGGING,
            "difficulty": "SENIOR",
            "experience_level": "SENIOR",
            "quality": Quality.STRONG,
            "tags": ["debugging", "incident-response", "root-cause"],
        },
        "transcript": (
            "Interviewer: Walk me through how you'd debug a production API "
            "returning intermittent 500 errors.\n"
            "Candidate: I'd pull up error logs and APM traces first to see if the "
            "500s cluster around a specific endpoint or time window. Last time I "
            "saw a pattern like this it turned out to be connection pool "
            "exhaustion after a deploy that changed our DB timeout settings, so "
            "I'd check recent deploys, correlate the error spike timestamp "
            "against the deploy log, and confirm the fix with a load test in "
            "staging before shipping it."
        ),
        "candidate_answer": (
            "I'd pull up error logs and APM traces first to see if the 500s cluster around a specific endpoint or time window. Last time I saw a pattern like this it turned out to be connection pool exhaustion after a deploy that changed our DB timeout settings, so I'd check recent deploys, correlate the error spike timestamp against the deploy log, and confirm the fix with a load test in staging before shipping it."
        ),
        "reference_feedback": (
            "This is a structured, hypothesis-driven approach: start from logs "
            "and traces, narrow down by correlating with deploy history rather "
            "than guessing, and verify the fix under load before shipping. "
            "Referencing a specific prior root cause (connection pool exhaustion) "
            "grounds the answer in real experience rather than a generic "
            "checklist."
        ),
        "rubric": [Rubric.ROOT_CAUSE_ANALYSIS, Rubric.SPECIFICITY, Rubric.ACTIONABILITY],
        "expected_evidence": [
            "error logs and APM traces",
            "connection pool exhaustion",
            "correlate the error spike timestamp against the deploy log",
            "confirm the fix with a load test in staging",
        ],
        "required_actions": [
            "recognize the hypothesis-driven methodology",
            "credit correlating symptoms with deploy history",
            "note the pre-ship verification step",
        ],
        "failure_modes": [
            "treats this as generic 'good debugging' without citing the specific steps",
            "hallucinates a specific tool (e.g. Datadog) the candidate never named",
            "ignores the staging verification step entirely",
        ],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (4, 5),
            "actionability": (4, 5),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Unambiguous strong case; pairs with backend-debugging-weak-001.",
    },
    {
        "case_id": "backend-debugging-weak-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "Backend Debugging",
            "category": Category.DEBUGGING,
            "difficulty": "SENIOR",
            "experience_level": "SENIOR",
            "quality": Quality.WEAK,
            "tags": ["debugging", "generic"],
        },
        "transcript": (
            "Interviewer: Walk me through how you'd debug a production API "
            "returning intermittent 500 errors.\n"
            "Candidate: I'd probably just restart the service and see if that "
            "fixes it. If not, I'd ask a senior engineer to take a look."
        ),
        "candidate_answer": (
            "I'd probably just restart the service and see if that fixes it. If not, I'd ask a senior engineer to take a look."
        ),
        "reference_feedback": (
            "Restarting the service may temporarily clear symptoms but doesn't "
            "diagnose the underlying cause, and it risks losing the exact "
            "conditions needed to reproduce the bug. Escalating immediately, "
            "with no attempt at a first diagnostic step like checking logs, "
            "signals limited debugging methodology for a senior-level question. "
            "A stronger answer names at least one concrete first step -- checking "
            "logs, metrics, or recent deploys -- before restarting or escalating."
        ),
        "rubric": [Rubric.ROOT_CAUSE_ANALYSIS, Rubric.SPECIFICITY, Rubric.ACTIONABILITY],
        "expected_evidence": ["restart the service", "ask a senior engineer to take a look"],
        "required_actions": [
            "identify the absence of any diagnostic step",
            "flag restart-as-fix as symptom-masking, not root-causing",
            "encourage a concrete first investigative step",
        ],
        "failure_modes": [
            "credits 'asking a senior engineer' as sufficient without any prior investigation",
            "invents a log-checking step the candidate never mentioned",
            "scores this as acceptable because restarting 'often works' in practice",
        ],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (1, 1),
            "actionability": (4, 5),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Tests whether the evaluator distinguishes 'took an action' from 'diagnosed anything'.",
    },
    {
        "case_id": "backend-code-review-strong-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "Code Review",
            "category": Category.CODE_REVIEW,
            "difficulty": "SENIOR",
            "experience_level": "SENIOR",
            "quality": Quality.STRONG,
            "tags": ["code-review", "error-handling"],
        },
        "transcript": (
            "Interviewer: A teammate submits a PR that fixes a bug by wrapping "
            "the failing call in a try/except that silently swallows the "
            "exception. How would you review it?\n"
            "Candidate: I'd push back on merging it as-is -- swallowing the "
            "exception hides the underlying failure instead of fixing it. I'd "
            "ask them to log the exception with enough context to debug it "
            "later, add a regression test that reproduces the original bug, and "
            "ideally trace why the call was failing in the first place so we're "
            "not just masking a deeper issue."
        ),
        "candidate_answer": (
            "I'd push back on merging it as-is -- swallowing the exception hides the underlying failure instead of fixing it. I'd ask them to log the exception with enough context to debug it later, add a regression test that reproduces the original bug, and ideally trace why the call was failing in the first place so we're not just masking a deeper issue."
        ),
        "reference_feedback": (
            "Correctly identifies that silently swallowing an exception is a "
            "code smell, not a fix, and the pushback comes with three concrete, "
            "actionable asks: log with context, add a regression test, and "
            "investigate the root cause. This reflects senior-level review "
            "instincts -- catching the pattern that will cause a harder-to-debug "
            "incident later, not just the immediate bug."
        ),
        "rubric": [Rubric.CODE_QUALITY, Rubric.SPECIFICITY, Rubric.ACTIONABILITY],
        "expected_evidence": [
            "swallowing the exception hides the underlying failure",
            "log the exception with enough context",
            "add a regression test that reproduces the original bug",
            "trace why the call was failing in the first place",
        ],
        "required_actions": [
            "recognize the pushback on hiding failures",
            "credit each of the three specific asks individually",
            "note this reflects senior-level review judgment",
        ],
        "failure_modes": [
            "credits 'pushed back' generically without naming the specific asks",
            "hallucinates a specific logging library or tool the candidate never named",
        ],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (4, 5),
            "actionability": (4, 5),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Unambiguous strong case; pairs with backend-code-review-weak-001.",
    },
    {
        "case_id": "backend-code-review-weak-001",
        "golden_type": GoldenType.CALIBRATION,
        "metadata": {
            "scenario": "Code Review",
            "category": Category.CODE_REVIEW,
            "difficulty": "SENIOR",
            "experience_level": "SENIOR",
            "quality": Quality.WEAK,
            "tags": ["code-review", "generic"],
        },
        "transcript": (
            "Interviewer: A teammate submits a PR that fixes a bug by wrapping "
            "the failing call in a try/except that silently swallows the "
            "exception. How would you review it?\n"
            "Candidate: Looks fine to me, I'd just approve it. As long as the "
            "bug is fixed, that's what matters."
        ),
        "candidate_answer": (
            "Looks fine to me, I'd just approve it. As long as the bug is fixed, that's what matters."
        ),
        "reference_feedback": (
            "Approving based solely on 'the immediate symptom is gone' misses "
            "the actual review responsibility here: the exception-swallowing "
            "pattern will cause a harder-to-diagnose incident later, and a "
            "thorough review would catch that instead of stopping at the "
            "surface-level bug fix. There's no technical reasoning in the "
            "answer at all -- just a verdict."
        ),
        "rubric": [Rubric.CODE_QUALITY, Rubric.SPECIFICITY, Rubric.ACTIONABILITY],
        "expected_evidence": ["looks fine to me", "as long as the bug is fixed"],
        "required_actions": [
            "identify the missing scrutiny of the exception-swallowing pattern",
            "flag the absence of any technical reasoning",
            "encourage substantive review criteria beyond 'does it fix the symptom'",
        ],
        "failure_modes": [
            "credits 'approve it' as decisive or confident rather than shallow",
            "invents that the candidate mentioned tests or logging when they didn't",
        ],
        "acceptable_score_range": {
            "groundedness": (5, 5),
            "specificity": (1, 1),
            "actionability": (4, 5),
            "rubric_alignment": (4, 5),
            "hallucination": (1, 1),
        },
        "notes": "Classic overly-generous-evaluator check, backend flavor.",
    },
]


CASE_EXPLANATIONS = {
    "behavioral-strong-001": (
        "Strong: collaboration, evidence-based decision, and a measurable outcome, "
        "all traceable to specific lines in the transcript."
    ),
    "behavioral-weak-001": (
        "Weak: candidate avoids the question entirely. Tests that the evaluator "
        "doesn't mistake politeness for an actual answer."
    ),
    "system-design-strong-001": (
        "Strong: clarifies requirements before proposing architecture and names "
        "concrete components and trade-offs."
    ),
    "system-design-weak-001": (
        "Weak: two components named with zero reasoning. Tests that the evaluator "
        "doesn't over-credit a shallow answer."
    ),
    "communication-strong-001": (
        "Strong: audience-appropriate analogy that stays accurate without jargon."
    ),
    "communication-audience-002": (
        "Bias probe: strong plain-language opening followed by a jargon regression "
        "under follow-up pressure. Tests whether the evaluator localizes feedback "
        "to the actual failure point instead of grading the whole answer as one verdict."
    ),
    "evaluation-grounding-trap-001": (
        "Bias probe: a plausible, grounded answer designed to tempt an evaluator "
        "into inventing extra achievements (Kubernetes, Redis, CI/CD) the "
        "candidate never mentioned."
    ),
    "evaluation-contradiction-001": (
        "Edge case: the candidate contradicts themselves within the same answer. "
        "Tests whole-transcript reasoning rather than sentence-level scoring."
    ),
    "backend-debugging-strong-001": (
        "Strong: hypothesis-driven debugging grounded in a specific prior root "
        "cause, with a verification step before shipping."
    ),
    "backend-debugging-weak-001": (
        "Weak: restart-then-escalate, with no diagnostic step at all. Tests that "
        "the evaluator doesn't credit 'took an action' as 'diagnosed something'."
    ),
    "backend-code-review-strong-001": (
        "Strong: identifies the exception-swallowing anti-pattern and gives three "
        "concrete, specific asks rather than a vague objection."
    ),
    "backend-code-review-weak-001": (
        "Weak: approves based on the symptom being gone, with zero technical "
        "reasoning. Classic overly-generous-evaluator check."
    ),
}


def publish_dataset() -> Any:
    """Publish the demo rows as a named Weave Dataset."""

    dataset = weave.Dataset(
        name="edition_007_golden_interview_evaluation_dataset",
        rows=EVALUATION_DATASET,
    )
    dataset_ref = weave.publish(dataset)
    print(f"\nPublished Weave dataset: {dataset_ref}")
    return dataset


def load_dataset(dataset_ref: str | None = None, should_publish_dataset: bool = False) -> Any:
    """Choose the dataset source for this evaluation run."""

    if dataset_ref:
        print(f"\nUsing existing Weave dataset: {dataset_ref}")
        return weave.ref(dataset_ref).get()

    if should_publish_dataset:
        return publish_dataset()

    return EVALUATION_DATASET


def print_dataset_story() -> None:
    """Print a short presenter-friendly explanation of the evaluation rows."""

    print("\nDataset rows:")
    for row in EVALUATION_DATASET:
        print(f"- {row['case_id']} [{row['golden_type']}]: {CASE_EXPLANATIONS[row['case_id']]}")

    print("\nWhat the evaluators inspect:")
    print("- transcript: raw conversation context for groundedness")
    print("- rubric: dimensions the feedback should cover")
    print("- expected_evidence: concrete moments the feedback should mention")
    print("- required_actions: improvement steps the feedback should recommend")
    print("- acceptable_score_range: pass band per rubric dimension, not a single point value")
