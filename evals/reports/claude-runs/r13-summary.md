<!-- Claude-run evals, round thirteen, on 0.7.6 (caa70d3). Each agent ran the pulse skill end to end against the mock connectors, writing bundle.json by hand. Subagents may not write report files, so the main session saved this summary of their returned reports. -->

# Claude-run evals on 0.7.6: summary

| Run | Score (0.7.5) | Score (0.7.6) | Worst finding | Fixed in 0.7.7 |
| --- | --- | --- | --- | --- |
| Tara's nudge morning, Thu 29 Oct | 8.5 | 9 | A date Instinct chose was read as Tara's and kept after it passed | Yes: who set a date is stored on the draft, and a passed date always moves |
| Tara's Friday, Fri 23 Oct | 8 | 9 | The hero and prep sheet did not say which lines to take out of a shared email; Sent it on the page lost the promise's `sent` mark | Yes, both |
| Meera's Friday, Fri 23 Oct | 8 | 8 | A hand-typed CRM read that left out round and raise blanked them on 33 deals, with no warning | Yes: missing deal fields keep what Home knew, and the run warns |

Other findings fixed in 0.7.7: a reply that puts off its answer stays deferring when the morning finds it; "the call" and "pay a visit" are no answer about money.

Kept for later (low): the 50 KB directory is rewritten when only its date changed; the bundle shortcut ignores the pipeline-off read; a "hold" reply has no tap of its own; reslot entries carry no time-zone hint.
