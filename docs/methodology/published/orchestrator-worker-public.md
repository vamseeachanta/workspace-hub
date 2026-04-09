# Orchestrator-Worker: Separating Planning from Execution

> Why context isolation is a prerequisite for reliable complex engineering.
> Based on 12+ months of production multi-discipline project delivery.

---

## The Problem: Context Overload

Complex engineering projects degrade predictably when a single team member or workflow tries to plan, implement, review, and deliver in one continuous session. As work progresses, the accumulated detail overwhelms the original plan:

```
Single-Session Workflow (4+ hours)
  Hour 1: Plans the analysis (reads specifications, creates approach)
      --> Plan is clear, context is fresh
  Hour 2: Begins implementation (modeling, debugging, reading references)
      --> Plan details start to fade under operational detail
  Hour 3: Continues work (error resolution, refinement, iteration)
      --> Working from current state, not from original specification
  Hour 4: Reviews own work (checks what was built, not what was planned)
      --> Cannot recall original requirements clearly
  Result: Drift between specification and deliverable, self-review is ineffective
```

This pattern is not about individual capability. It is a property of bounded attention applied over extended periods. The more complex the project, the faster context overload sets in.

### Why Self-Review Fails

An engineer reviewing their own analysis is like a developer reviewing their own code. They built it, so it looks correct. The reasoning that justified each decision is still fresh. Blind spots are invisible precisely because they are the analyst's blind spots.

Independent review catches what self-review cannot -- not because the reviewer is smarter, but because they approach the work without the accumulated assumptions of the person who created it.

---

## The Solution: Orchestrator + Workers

**Orchestrator**: Maintains the master plan, delegates focused tasks, verifies results against specification.

**Workers**: Execute focused tasks with fresh context, return results without accumulated baggage.

```
Orchestrator
  ├── Reads requirements, creates detailed plan
  ├── Designs focused task briefs (each self-contained)
  ├── Assigns Worker 1: Mooring analysis with relevant specs only
  ├── Assigns Worker 2: Riser assessment with relevant specs only
  ├── Collects results from both workers
  ├── Verifies each result against the original specification
  └── Delivers or sends back with specific feedback

Worker 1 (fresh context)
  ├── Receives: Analysis scope + relevant specifications
  ├── Executes only what the brief specifies
  ├── Validates results against acceptance criteria
  └── Returns: Analysis results + summary of findings

Worker 2 (fresh context)
  ├── Receives: Assessment scope + relevant specifications
  ├── Executes only what the brief specifies
  ├── Validates results against acceptance criteria
  └── Returns: Assessment results + summary of findings
```

### Why This Works

| Challenge | Single Session | Orchestrator-Worker |
|-----------|---------------|-------------------|
| Context overload | Grows with project duration | Each worker starts fresh |
| Plan drift | Specification forgotten as details accumulate | Orchestrator maintains specification throughout |
| Parallel work | Sequential only | Workers proceed in parallel |
| Self-review bias | Same person reviews their own work | Independent review by different team members |
| Failure recovery | Must reconstruct lost context | Restart worker with the same brief |
| Session duration | 4+ hours with degrading quality | 1-2 hours per worker with sustained quality |

---

## How We Apply This in Practice

### Multi-Discipline Project Delivery

For projects involving multiple engineering disciplines -- mooring analysis, riser assessment, structural evaluation -- the orchestrator-worker pattern is essential.

The orchestrator:
1. **Triages the project scope** into independent analysis packages
2. **Designs self-contained briefs** for each discipline, with full context embedded (no cross-references that require chasing)
3. **Maps deliverable boundaries** to ensure no two workers modify the same output
4. **Launches workers in parallel** across disciplines
5. **Reviews results** against the original project specification, not against what was convenient to produce

### Provider and Tool Allocation

Different analysis tools and team members have different strengths. Our allocation pattern emerged from hundreds of project deliveries:

| Workstream | Best Suited For |
|------------|----------------|
| High-context synthesis | Architecture review, cross-discipline coordination, specification development |
| Bounded analysis | Focused numerical analysis with defined inputs and outputs |
| Documentation and audit | Staleness scanning, report generation, compliance documentation |
| Pipeline development | Automation scripts, data integration, toolchain work |

This allocation is not arbitrary. It emerged from observing which approaches succeed at which tasks across extensive production experience.

### Contention Avoidance

When multiple workstreams operate on the same project simultaneously, coordination failures are the primary risk. Our contention avoidance rules:

1. **No two workers modify the same deliverable.** No exceptions.
2. **No two workers operate in the same output directory** when possible.
3. **Negative boundaries**: Each worker brief includes explicit lists of deliverables they must NOT produce (owned by other workers).
4. **Synchronization checkpoints** before integration points.
5. **Staggered delivery** if output overlap is unavoidable.

---

## Pattern Variants

### Variant 1: Delegated Subtasks

For work that can be subdivided within a single session:

```
Lead engineer (orchestrator role)
  ├── Subtask: "Complete the metocean data analysis"
  │   Context: Project spec section 2.1 + relevant data files
  ├── Subtask: "Run the fatigue assessment for riser section 3"
  │   Context: Project spec section 2.2 + structural model
  └── Lead verifies each subtask result against master specification
```

### Variant 2: Isolated Workspaces

For work that cannot share a single project environment:

```
Each worker gets an independent workspace
  - Complete isolation from other workstreams
  - Orchestrator reviews outputs from each workspace
  - Integration happens at defined merge points
```

### Variant 3: Staged Cascade

For projects with mandatory approval gates:

1. **Planning workers** (stage 1): Each produces one analysis plan or assessment brief. No implementation.
2. **Approval gate**: Plans reviewed and approved before execution begins.
3. **Execution workers** (stage 2): Convert approved plans into deliverables.
4. **Review workers** (stage 3): Independent review of each deliverable.

This cascade respects hard-stop workflow gates while maximizing parallel throughput.

---

## Common Pitfalls

1. **Workers creating their own plans.** This defeats the purpose. Workers should receive plans, not create them. Plan-approval enforcement prevents this.

2. **Orchestrator implementing directly.** Context overload returns immediately. If the orchestrator starts doing analysis work, they stop being an orchestrator.

3. **No verification step.** The orchestrator must verify worker output against the specification, not trust it. Workers optimize for task completion, not specification adherence.

4. **Stale context in worker briefs.** Workers must get the current specification version. If the spec was updated after the brief was written, the worker produces the wrong deliverable.

5. **Missing handoff documentation.** If a worker cannot complete their task, the next person must pick up from where work stopped. Handoffs require explicit status documentation.

---

## Performance Comparison

| Metric | Single Session | Orchestrator-Worker |
|--------|---------------|-------------------|
| Time to complete complex project | 4+ hours | 1-2 hours per worker |
| Attention span utilization | Degrades linearly | Flat per worker |
| Plan drift frequency | Common after hour 2 | Rare (orchestrator maintains plan) |
| Review effectiveness | Low (self-review) | High (independent review) |
| Parallel throughput | 1x | 3-5x (limited by available workers) |

---

## Key Takeaway

Context isolation is not a nice-to-have. It is a prerequisite for reliable complex engineering. The orchestrator-worker pattern works because it converts one hard problem -- maintaining coherence over a 4+ hour project session -- into multiple easier problems: focused workers executing well-defined tasks in 30-90 minutes each. Every complex project we deliver uses some variant of this pattern.

The result for our clients: faster delivery, higher quality, and better adherence to original project specifications. The orchestrator always knows the plan. The workers always have fresh attention. The deliverable always gets independent review.

**Our AI-augmented orchestrator-worker workflow delivers better results for complex engineering projects.** [Contact ACE Engineering](https://aceengineer.com/contact) to learn how this methodology applies to your offshore, structural, or pipeline engineering challenges.
