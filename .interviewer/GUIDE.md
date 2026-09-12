# Interviewer guide — confidential

Do not share this directory, branch, commit history, diff, or branch name with a candidate. The candidate must receive a history-free export of commit `6d49822a441e69b14afdff2babe1290781fb638a` using `export-candidate.sh`.

## Signal and scope

This exercise asks whether a Senior DevSecOps candidate can:

1. trace untrusted input through unfamiliar product code;
2. independently discover and prioritize a material trust-boundary failure;
3. implement one focused Python improvement without breaking legitimate behavior;
4. add adversarial evidence and state what it cannot prove;
5. use AI critically and defend every material change; and
6. control scope under a 35-minute implementation budget.

Do not score issue count. The coherent primary problem is outbound-request safety. Product-code comprehension and coding are the primary evidence.

## Before the interview

1. Create a new private candidate repository using `./.interviewer/export-candidate.sh OUTPUT_DIR`. See “Candidate-copy process” below.
2. Open the candidate copy, never this branch, in the interview environment.
3. Run `make verify-env` and `make baseline` with the candidate before starting the timer.
4. Confirm screen sharing, editor, terminal, and AI tool availability. Offer the same approved AI tool to every candidate.
5. Tell the candidate that public documentation is allowed throughout, while AI is allowed only from minute 15 through minute 50.

Environment troubleshooting is outside the timer.

## Exact facilitation script

### 0–15 minutes — AI-free assessment

Read the Task paragraph in `CANDIDATE.md` verbatim. Say:

> Start with an independent assessment. Do not use AI for the first 15 minutes. Record prioritized risks and specific repository evidence in NOTES.md. You may run the existing checks and use public documentation. I will answer product-requirement questions but will not confirm security findings during this phase.

At minute 12, say: “Three minutes remain in the assessment phase. Please commit to a priority and proposed improvement.”

At minute 15 ask, without confirming correctness:

- What is the most material risk and why?
- Trace the relevant data from the API boundary to the outbound action.
- What would you change in the implementation window, and what behavior must remain?
- What evidence would convince you the change works?

Record whether the candidate independently found the central issue before any hint or AI use.

### 15–50 minutes — AI-enabled implementation

Say:

> You may now use AI and public documentation. Implement and validate one focused improvement. Keep NOTES.md current, including suggestions you accepted, rejected, or independently verified. Think aloud enough that I can distinguish your decisions from tool output.

Do not provide unsolicited implementation advice. Answer product questions consistently:

- public HTTP and HTTPS are supported;
- redirects are supported;
- broad hostname allowlisting is not a stated product constraint;
- the service runs in a cloud workload;
- tests must remain deterministic and must not contact real targets.

At minute 45, say: “Five minutes remain before the requirement update. Get your implementation and evidence into a reviewable state.”

### 50–60 minutes — standardized AI-free twist

Require the candidate to close AI tools. Read verbatim:

> Supported public sites use redirect chains, including redirects to a different public hostname. Show that your proposed control preserves legitimate redirects and applies to every outbound hop. Adapt the code or tests if needed, or record the exact follow-up if you cannot complete it in this window.

Do not name a protected redirect target unless using the hints ladder. At minute 58, ask the candidate to stop editing and prepare the walkthrough.

### 60–75 minutes — AI-free walkthrough and defense

Ask these questions in order:

1. What did you conclude was unsafe, and what repository evidence supports the priority?
2. Walk through every material code change. What legitimate behavior did you preserve?
3. Show the strongest positive and adversarial evidence you added.
4. What does this mocked evidence prove, and what can it not prove about production?
5. How could hostname resolution or a redirect undermine a naive check?
6. What should exist outside this application as defense in depth?
7. Which AI suggestions did you reject or independently verify, and why?
8. With another day, what would you do next and in what order?

Ask the candidate to create the final local commit before time expires. Do not help clean up code after minute 75.

## Bounded hints ladder

Use at most these three hints, in order, only when the candidate is blocked. Record the level and time. Pause briefly after each hint.

1. **Trust-boundary hint:** “Trace where caller-controlled data causes an action, and compare the caller's trust position with the workload's.”
2. **Request-flow hint:** “Consider both the first outbound request and any later outbound request caused by a response.”
3. **Concrete test hint:** “Try a destination available to the workload but not an external caller, directly and after a redirect.”

The candidate must discover the central finding during the AI-free assessment without hints for full assessment credit. Discovering it after hint 1 or 2 caps assessment at 3. Missing it after hint 3 is below bar and caps assessment at 2.

## Interviewer-only expected findings

### Central finding — gating

Untrusted `FetchRequest.url` reaches `HttpxTransport.get` after only scheme, hostname-presence, and user-info validation. From a cloud workload, this permits server-side requests to destinations the caller cannot reach directly.

Expected exploit paths:

- direct IPv4 loopback, RFC1918/private, link-local, and cloud service addresses;
- direct IPv6 loopback, unique-local, link-local, IPv4-mapped, and other non-global forms;
- a public-looking hostname that resolves to a protected address;
- a public initial URL that redirects to a protected literal or hostname;
- checks applied only to the first URL but not each redirect hop;
- checks that compare hostname text but do not classify all resolved addresses;
- DNS/check-use gaps where classification and the actual connection resolve separately.

Full credit does not require solving every DNS rebinding or connection-pinning problem in 35 minutes. It requires recognizing the limitation and not claiming a string check or application pre-resolution is perfect protection.

### Natural secondary concerns

- redirect chains are unbounded in the starter;
- response bodies are buffered without a service-owned byte/decompression limit;
- timeout behavior is inherited from `httpx`, not expressed as a product budget;
- full URLs and error context are logged and may contain secrets;
- redirect scheme/port/downgrade and content-type policy are not product-defined.

These show depth and prioritization. They do not compensate for missing the central finding, and candidates should not be rewarded for enumerating them without evidence.

## Acceptable implementation families

Accept designs based on observable safety and reasoning, not patch shape:

- resolve and classify every address before each hop, rejecting when any answer is non-global;
- a transport or connector that pins a validated address while preserving hostname/TLS semantics;
- a trusted egress proxy boundary plus application enforcement that can be demonstrated locally;
- a product-justified allowlist if the candidate explicitly surfaces its product cost;
- an equivalent standard library or well-maintained URL/network policy library.

A focused direct-IP plus per-hop mitigation can meet implementation level 3 if tests are strong and DNS/check-use limitations are explicit. A hostname-string blocklist, first-hop-only check, or reliance on parser normalization alone does not.

## Hard red flags

- misses the central issue after all three hints;
- allows the initial or redirected protected destination to reach the transport while claiming it is fixed;
- copies AI output that they cannot explain;
- removes redirect support or public HTTP/HTTPS behavior without acknowledging the product regression;
- tests against live internal, metadata, cloud, or external targets;
- claims local mocked tests prove production network safety or perfect rebinding prevention;
- disables tests, suppresses errors broadly, adds credentials, or creates external side effects;
- rewrites the service wholesale without understanding the existing flow.

## Scoring

Score each dimension 1–4 using observed evidence. Do not average away a gating weakness.

### 1. Assessment and prioritization

- **1:** Does not identify a meaningful trust-boundary risk; unsafe prioritization.
- **2:** Finds secondary issues or finds the central issue only after the full hints ladder; weak repository evidence.
- **3:** Independently finds the central issue, traces direct and redirect paths, prioritizes by impact/exploitability, and controls scope.
- **4:** Level 3 plus nuanced IPv4/IPv6, DNS/check-use, resource-abuse, and deployment-layer reasoning without turning the task into a finding count.

### 2. Chosen improvement and execution

- **1:** Change is ineffective, unsafe, unexplained, or breaks core legitimate behavior.
- **2:** Partial mitigation with a material bypass the candidate does not recognize, or code requires substantial interviewer correction.
- **3:** Focused, readable Python materially blocks the chosen abuse path, applies to every relevant hop, preserves public redirects, and handles errors coherently.
- **4:** Level 3 plus a strong abstraction or connection-level design, careful edge handling, and production-ready maintainability within scope.

### 3. Adversarial validation and security reasoning

- **1:** No meaningful evidence, live unsafe tests, or false claims from passing happy-path tests.
- **2:** Basic positive/negative tests but misses obvious bypasses or cannot state evidence limits.
- **3:** Deterministic positive and adversarial tests cover direct and redirected behavior; candidate clearly states mocked and production limits.
- **4:** Level 3 plus high-value IPv4/IPv6, mixed-answer, redirect, and check-use reasoning with proportionate defense-in-depth proposals.

### 4. Communication and AI judgment

- **1:** Cannot explain material changes or treats AI/scanner output as authority.
- **2:** Reasoning is incomplete, notes are weak, or AI verification is mostly asserted.
- **3:** Evidence-based notes, clear tradeoffs and residual risks, and specific accepted/rejected/verified AI suggestions.
- **4:** Level 3 plus exceptionally concise risk communication, disciplined scope, and active detection/correction of flawed tool suggestions.

Passing requires overall judgment of **3 or higher**, no dimension at 1, and both assessment/prioritization and chosen improvement/execution at least 3. Do not calculate a simple average as a substitute for this rule.

## Calibration

Before using the exercise broadly:

1. Have at least two engineers independently complete the candidate copy under the exact timing and tools policy.
2. Score independently before discussion, then compare evidence by dimension.
3. Confirm a sound focused implementation is achievable in 35 minutes after the 15-minute assessment.
4. Remove accidental environment or framework trivia that consumes time without producing a deliberate signal.
5. Review the first three real interviews together. Adjust hints or anchors prospectively; never change a completed candidate's rubric.

Current limitation: the reference implementation was dry-run functionally and reviewed qualitatively, but no independent human completed a timed 75-minute pilot during repository construction. Treat the first internal runs as calibration, not proof of timing fairness.

## Confidential evaluator

`.interviewer/evaluator.py` is supporting interviewer evidence, not the rubric and not an undisclosed candidate gate. It demonstrates that the frozen starter permits four representative request paths and that this worked solution denies them while preserving a public redirect chain. Run it only against a controlled checkout.

The evaluator knows how to construct the starter and this reference solution. It will not automatically recognize every acceptable candidate design—for example, enforcement entirely inside a custom transport, connector, or egress-proxy adapter. Evaluate alternate designs from behavior, tests, and reasoning; adapt the confidential scenarios manually when the constructor or policy boundary differs. Never tell a candidate that an otherwise sound design must match the evaluator's classes, files, or patch shape.

## Candidate-copy process

Run from this reference branch:

```bash
./.interviewer/export-candidate.sh /absolute/path/to/new-candidate-copy
```

The script exports only the fixed candidate commit's tree, creates a new repository with one root commit on `main`, and verifies that interviewer paths, branches, commits, and unreachable blobs are absent.

To publish a copy, create a new private empty GitHub repository and push only this new root:

```bash
gh repo create OWNER/PRIVATE-CANDIDATE-REPO --private --source /absolute/path/to/new-candidate-copy --remote origin --push
gh repo view OWNER/PRIVATE-CANDIDATE-REPO --json visibility --jq .visibility
```

The second command must print `PRIVATE`. Never add this reference repository as a remote in the candidate copy, and never fork it through GitHub.
