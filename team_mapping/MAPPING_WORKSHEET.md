# Map Kitaru onto YOUR PoC — team worksheet (20 min)

Work as a team. Sketch on paper or in this file. Be concrete — names, not
concepts. You'll share **one insight** out loud at the end.

## 1. Flow boundaries (3 min)

What is *one execution* of your system? (One email batch? One user question?
One scenario simulation? One negotiation?)

> Our flow: `____________________` runs when `____________________`
> and is finished when `____________________`.

## 2. Checkpoint seams (4 min)

Where are the natural steps? Good seams: external API calls, LLM calls,
expensive computation, anything you'd hate to re-pay for.

> Checkpoints: `____________` → `____________` → `____________` → `____________`
>
> The step most likely to fail: `____________`
> The step most expensive to repeat: `____________`

## 3. The wait() point (3 min)

Where must a human (or an external system) sign off or provide input?
If your answer is "nowhere" — what's the most expensive mistake your agent
could make unsupervised? Reconsider.

> `kitaru.wait(name="________")` goes between `____________` and `____________`.

## 4. Your replay-regression scenario (5 min) — the important one

What change are you most afraid to ship? (A prompt? The model? A re-index?
A taxonomy update?) Design the replay that would give you evidence:

> Change under test: `____________________`
> Replay from checkpoint: `____________`
> Override: `checkpoint.____________ = ____________`
> We compare: `____________________` (cost / labels / citations / distribution)
> We'd run it on `______` historical executions before shipping.

## 5. One artifact worth versioning (2 min)

> `kitaru.save("____________", ...)` — because next month we'll need to know
> exactly which version produced `____________________`.

## 6. The insight (3 min)

Complete this sentence for the room:

> "The thing we were going to build by hand that we now don't have to is ______."

---

*Stuck? Flag an instructor. Done early? Start coding it — `pip install kitaru`
is right there, and office hours go to the first teams with a running flow.*
