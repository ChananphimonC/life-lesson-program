# Product Specification: Life Lesson Program

## 1. Product Vision
An AI-assisted content generation system that creates original, 3-5 minute Thai "life reflection" audio-visual episodes. It provides a calm, non-judgmental space for listeners to process their daily experiences, acting as a mirror for their thoughts rather than a guide telling them what to do.

## 2. Target Audience
- Thai-speaking Millennials and Gen Z (18–40 years old).
- Individuals navigating urban life, career burnout, relationship complexities, and quarter-life crises.
- People seeking comfort, validation, and a moment of pause, not lectures or toxic positivity.

## 3. Content Philosophy (Core Principle)

### 3.1 Definition: LIFE REFLECTION vs. LIFE ADVICE
The product's entire value proposition rests on staying on the "reflection" side of this line. Every prompt, Critic rule, and QA checklist item must be traceable back to it.

**LIFE REFLECTION (what we make):**
- Observes an experience or feeling without resolving it.
- Explores *why* something feels the way it feels.
- Offers a perspective or a different angle — never a fix.
- Leaves interpretation to the listener; the ending stays open.
- Trusts the listener to draw their own conclusion.

**LIFE ADVICE / MOTIVATIONAL CONTENT (what we explicitly avoid):**
- Tells the listener what to do, feel, or believe.
- Promises that adopting a mindset, habit, or perspective will resolve the problem.
- Closes with a resolution, a lesson "learned," or a call to action.
- Borrows authority from a teacher, book, or tradition instead of standing on its own observation.

### 3.2 The System DOES NOT
- Teach religion or quote religious texts (e.g., no Buddha quotes, no dharma teachings).
- Quote or attribute statements to famous people, books, or public figures — including paraphrased or recognizably derivative versions of well-known quotes.
- Reproduce or lightly reword existing motivational content ("copied or derivative motivational content").
- Give therapy, diagnose mental health conditions, or make clinical/medical claims.
- Give prescriptive life advice or tell the listener what they "should," "must," or "need to" do.
- Promise that a particular mindset, habit, or perspective will solve the listener's problem.
- Rely on generic motivational clichés (e.g., "Don't give up," "Tomorrow is a new day").
- Use manipulative or preachy language (guilt-tripping, faux-inspirational urgency, rhetorical pressure to change).

### 3.3 The System SHOULD
- Observe everyday human experiences (loneliness, failure, self-worth, comparison).
- Explore emotions and situations deeply, without rushing to resolve them.
- Tell relatable, grounded stories or observations.
- Offer perspectives rather than instructions.
- Leave room for the listener to interpret and reflect.
- Feel calm, intimate, conversational, and human.
- End with an open-ended reflection rather than a motivational conclusion.

### 3.4 Originality: Two Distinct Concerns
The system must guard against two different kinds of "not original," and they are solved differently:

- **A. Repetition against the project's own back catalog** — the same angle or observation reused across episodes. Solved with an in-project similarity check (see ARCHITECTURE.md, deferred to the milestone where it becomes necessary).
- **B. Resemblance to external/copyrighted/attributed material** — quoting or closely paraphrasing religious texts, famous quotes, published authors, or existing motivational content. Solved primarily through generation constraints and the Critic's explicit quote/attribution checks (see AI_DESIGN.md), not through a large external plagiarism-detection system. MVP does not build a full external corpus-matching system; the Critic's job is to catch recognizable copied phrasing and attributed statements before they reach a human.

## 4. Human-in-the-Loop Requirement
The AI is an engine, not the final decision-maker.
- AI generates topics, scripts, and media.
- The automated Critic performs the first pass of tone/content-philosophy QA (see AI_DESIGN.md).
- **MVP assumption: a single human reviewer (the project owner)** performs final QA on script tone, anti-advice/anti-quote compliance, and approves the final video before publishing. The Streamlit dashboard is designed as a single-user review tool for this stage of the product; multi-reviewer workflows are out of scope for MVP.
- Any episode that fails automated Critic review after the maximum rewrite attempts is routed to the human reviewer for manual handling rather than being discarded or force-published (see AI_DESIGN.md §4 for the FAILED_REVIEW state).

## 5. Sensitive Topics Policy
Because the target emotional territory (loneliness, burnout, self-worth, comparison) sits near topics that require care, the product explicitly does not attempt to handle:
- Self-harm or suicidal ideation.
- Severe mental-health crisis.
- Abuse.
- Any topic requiring medical/clinical claims or professional diagnosis.

The system must never generate instructions, encouragement, or narrative detail related to these topics, must never imply it is providing professional/clinical help, and must not attempt to diagnose. Detection and handling of these topics is a pipeline-level safeguard, not a purely stylistic Critic concern — see AI_DESIGN.md §6 and ARCHITECTURE.md for where this sits in the pipeline.
