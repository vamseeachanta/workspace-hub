Parent: #2

## Objective
Create the smallest callable Q&A service that can answer Oil & Gas questions from the approved repo knowledge pack and produce a Teams-ready response schema.

## Scope
- Implement a local CLI or HTTP endpoint that accepts a question.
- Retrieve relevant knowledge-pack chunks and call Hermes/model path for a grounded answer.
- Return a structured response with:
  - concise answer,
  - citations/source IDs,
  - confidence/limitations,
  - follow-up suggestions,
  - redaction/safety status.
- Keep runtime repo access read-only or use pinned knowledge-pack files.

## Deliverable
- Minimal service/CLI implementation.
- HTML demo transcript showing sample questions and answers.
- Test fixture for at least 3 representative Oil & Gas questions.

## Acceptance criteria
- [ ] Runs locally without Teams dependency.
- [ ] Produces citations/source IDs for every substantive answer.
- [ ] Does not log prompts, raw retrieved snippets, model answers, credentials, or raw Teams payloads by default.
- [ ] Fails closed when no approved source is found.
- [ ] Output can be wrapped by Teams bot/tab/webhook routes.
