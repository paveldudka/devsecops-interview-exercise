# Candidate instructions

## Task

This repository models a production service that retrieves content from user-supplied URLs. Assess whether the service is safe to operate, document and prioritize the material risks you find, then implement and validate one focused improvement. Explain what your validation proves, the risks that remain, and what you would address next. You are not expected to find or fix every issue; evaluation is based on judgment, prioritization, implementation, validation, and communication rather than finding count or lines changed.

The intended product behavior is:

- accept public HTTP and HTTPS URLs;
- follow normal redirect chains;
- run from a cloud workload; and
- return fetched content to the caller.

Preserve legitimate behavior while improving the service. Multiple coherent designs are acceptable.

## Before the timer

Use the supplied devcontainer, then run:

```bash
make verify-env
make baseline
```

Tell the interviewer if either command fails. Environment setup is not part of the timed exercise.

## Live exercise: 75 minutes

### 0–15 minutes — independent assessment

- Do not use AI tools.
- Public documentation is allowed.
- Read the code and architecture notes.
- Record prioritized risks and repository evidence in `NOTES.md`.
- Explain which improvement you would implement and why.

### 15–50 minutes — implementation and validation

- AI tools and public documentation are allowed.
- Implement one focused improvement.
- Add or update tests that demonstrate the behavior you rely on.
- Keep `NOTES.md` current, including how you used and verified AI suggestions.

### 50–60 minutes — requirement update

- Stop using AI tools.
- The interviewer will provide the same standardized requirement update used for all candidates.
- Assess your current design and adapt the implementation or record the exact follow-up needed under “Requirement update” in `NOTES.md`.

### 60–75 minutes — walkthrough and defense

- Do not use AI tools.
- Walk through the risks, implementation, tests, limitations, and next actions.
- Be prepared to explain every material change.

## Submission

Create a local commit containing your final result; you do not need to push it. One or more commits are acceptable. Your final result should include:

- completed `NOTES.md`;
- the focused implementation change; and
- the tests or other validation evidence you added.

There is no undisclosed automated pass/fail gate. Candidate-visible checks exercise the documented product behavior and repository quality boundaries; assessment also considers your reasoning and discussion.
