# Speaker notes — read the night before

## Know your room

The five **archetypes** on slide 2 (batch classifier, source-grounded assistant,
fan-out analytics, high-stakes copilot, persona simulator) are the spine of the
talk — every module maps back to them. Before the session, map the teams/projects
in *your* audience onto these five so you can make eye contact with the right
people at the right slide.

If you're running this for a private cohort, keep client/project specifics off
the slides — speak in archetypes, and let participants self-identify ("that's
basically our project!"). Don't name anyone's confidential work from the stage.

Tech reality: most agent/LLM/ML work is Python; TypeScript usually owns the
frontend. That's why this is Python-only and the deployment-invoke slide is the
hook for the frontend folks (they call deployed flows over REST).

## Slides vs terminal — when to switch (presenter flow)

Default = stay on slides. Only switch to the terminal at the 🖥️ rows. The deck
shows the code/expected-output *on the slide* first; the terminal is where you
(and the room, for hands-on) actually run it.

| Deck section | Mode | What you do |
|---|---|---|
| Title → "What Kitaru is" (Module 0) | 📊 SLIDES | Theory: agents vs workflows, what breaks, retry/resume/replay/regress |
| "Setup — do this now" | 📊 SLIDES | Room runs setup in *their* terminals; you stay on the slide |
| **Module 1** "Flows and checkpoints" + "run it twice" | 📊 SLIDES | Walk the code + expected cached output on-slide |
| → run Exercise 1 | 🖥️ TERMINAL (room) | `python exercises/01_first_flow/flow.py`, run twice → caching |
| **Module 2** "wrap YOUR agent" | 📊 → 🖥️ | Slide first, then `python exercises/02_wrap_agent/agent.py` (or theirs) |
| "Now you: replay with overrides" ★ | 📊 → 🖥️ (room) | Slide, then `exercises/03_replay_overrides` — baseline then `--replay` |
| "Honest slide" + "regression scenario" | 📊 SLIDES | No terminal — framing + discussion |
| **Module 3** stacks / deployments / invoking | 📊 SLIDES | Concepts only |
| "Demo: the durable chatbot" | 🖥️ TERMINAL/UI (you) | Deployed flow + `python ui.py` → Gradio; kill-tab-resume demo |
| **Module 4** "Replay Factory" + "the loop" | 📊 → 🖥️ | Slide, then `python exercises/07_replay_factory/factory.py` |
| "verdict" + eval slides | 📊 SLIDES | The eval Q&A armory (see EVALS_PRIMER) |
| "Map Kitaru onto your PoC" | 📊 SLIDES + worksheet | `team_mapping/MAPPING_WORKSHEET.md` |

Take-home only (not shown live): Exercises 4 (HITL) and 5 (fan-out). Mention,
don't run.

## Strategic framing (calibrated, not salesy)

- **Cost narrative**: "AI spend is the new headcount" is *industry mood*, not a
  competitor dunk. Teams will hit cost asks within a year; you're handing them
  the answer pattern (replay a cheaper model, prove it, ship it).
- **The replay honesty slide is non-negotiable.** Sophisticated people will probe
  exactly where replay validity breaks (stochasticity, divergence, mocked tools).
  Co-opt the critique before they raise it: replay = cheap offline filter on the
  right distribution; cost deltas are hard numbers, quality deltas are evidence;
  confirm winners live. You gain more credibility here than from any feature.
- **"Why not just LangGraph time-travel?"** Fair question. Time-travel is a great
  primitive — fork one checkpoint interactively, framework-locked. Kitaru's claim
  is the *product around it*: batch replay over history, cost reports,
  framework-neutral, deployments. Differentiate, don't trash-talk.
- **LangSmith / Langfuse experiments?** Dataset-mediated re-execution, good for CI
  regression on curated sets; replay works on raw execution history with
  step-level injection. Both have a place.
- **Multi-turn evals**: the `instructor/EVALS_PRIMER.md` is your Q&A armory — the
  user-simulator validity crisis, the LLM-judge cross-turn blind spot, pass^k,
  and the off-policy/divergence-gated-replay frontier. Read it before the day.

## Demo-risk management

- The chatbot (deployed on k8s) and the MCP finale are the highest-risk demos.
  Record a 60-second screen capture of each as backup the day before.
- **Exercise 1 is the only thing guaranteed to work without keys/network.** If
  wifi dies, extend Modules 1–2 (the replay hands-on works on the canned flow)
  and narrate the rest from recordings.
- Workshop API key: set a hard spend cap and delete it the same evening.
- Keep `kitaru executions list` open in a dedicated terminal the whole time —
  it's your live "what just happened" view for every module.
- First-turn cold-pod latency on the deployed chatbot is ~30–60s. Narrate it
  ("that pause is Kubernetes scheduling a pod — which then dies the moment the
  bot waits for you") rather than hiding it.

## Roadmap honesty (don't promise dates)

- Live trace-import from observability tools (LangFuse/Datadog) is the **frontier**,
  not a shipped button — present it as where this goes.
- Streaming combined with the chatbot's flow-scope wait tool is a known
  limitation; stream a regular agent, keep the chat demo non-streaming. (Tracking
  upstream; may be fixed in a newer release — re-test before you present.)

## Timing discipline (2h / 120 min)

Module 2 (wrap + replay) is the one that converts — protect its hands-on time.
If running late: trim the capstone to a 3-minute report demo + "go build it";
then eat the Module 3 buffer. **Never cut** the replay hands-on, the honesty
slide, or the mapping exercise — the mapping is where people internalize it, and
the shared insights tell *you* which archetype resonated most.

## Follow-ups to capture on the day

- Which teams got a flow running → offer office hours / a follow-up.
- Photos of the mapping worksheets (with permission).
- Anyone asking about trace import or cost reports unprompted → strong
  design-partner / adoption signal; follow up.
