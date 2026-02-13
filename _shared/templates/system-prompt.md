# System Prompt Template (Contract Style)

Use this template to create clear, effective system prompts for AI agents.

---

## Template

```
You are: [Role - one line description]

Goal: [What success looks like - be specific]

## Success Criteria
- [Measurable criterion 1]
- [Measurable criterion 2]
- [Measurable criterion 3]

## Constraints
- [Hard limit 1]
- [Hard limit 2]
- [Hard limit 3]

## If Unsure
Say so explicitly. Do not guess or hallucinate.

## Output Format
[Exact structure expected - JSON schema, bullets, headers, etc.]

Example:
[One concrete example of the expected output]
```

---

## User Prompt Four-Block Pattern

When crafting user prompts, use these sections:

```
## INSTRUCTIONS
[Behavior and approach for this specific request]

## CONTEXT
[Background information and relevant data]

## TASK
[The specific request - what to do]

## OUTPUT FORMAT
[Exact structure expected for this response]
```

---

## Quick Reference Checklist

Before deploying a prompt, verify:

- [ ] Goal stated first
- [ ] Role defined (one line)
- [ ] Constraints explicit (bullets)
- [ ] Format specified (schema or example)
- [ ] 1-2 examples included
- [ ] Uncertainty rule added ("If unsure, say so")
- [ ] Sections clearly separated
- [ ] Evaluator checklist appended (for complex tasks)

---

## Self-Evaluator Append (For Complex Tasks)

Add this to the end of complex prompts:

```
Before responding, verify:
- Did you follow the output format exactly?
- Are uncertain claims marked as such?
- Are all steps actionable?
- Did you stay within stated constraints?
```

---

## Examples Over Adjectives

Replace vague language with demonstrations:

| Instead of... | Use... |
|---------------|--------|
| "Be concise" | "Reply in 3-5 bullet points, each under 15 words" |
| "Be professional" | [Include one example of the desired tone] |
| "Format nicely" | [Show the exact format structure] |

One solid example outperforms multiple descriptive phrases.

---

## Few-Shot Guidance

| Task Type | Examples Needed |
|-----------|-----------------|
| Format-specific (emails, JSON) | 1-2 examples |
| Tone calibration | 1 example |
| Complex classification | 2-3 examples |
| Simple Q&A | 0 examples |
