import Mathlib

/-!
# GeneratedAfterFreeze

Module **B** of the contamination-resistant evaluation track.

We model a checkpoint (`Model`) by two timestamps — its training cutoff and its
freeze time — and an evaluation scenario by its generation timestamp.  The
membership predicate `InTrainingData` is abstract; the *only* property we assume
about it is that a model's training data contains scenarios generated at or
before the model's training cutoff.

Under that assumption we prove that a scenario generated strictly after a
checkpoint's freeze time cannot be in the checkpoint's training data, i.e. it is
*clean* for that checkpoint.

This is a leakage-*reduction* statement for a single checkpoint, not a claim
that contamination is eliminated globally.
-/

namespace Verifiable.GeneratedAfterFreeze

/-- A frozen checkpoint, described by two timestamps. -/
structure Model where
  training_cutoff : ℝ
  freeze_time : ℝ

/-- An evaluation scenario, described by its generation timestamp. -/
structure EvalScenario where
  generated_at : ℝ

variable (InTrainingData : Model → EvalScenario → Prop)

/-- A scenario is *clean* for a model when it is not in the model's training
data. -/
def Clean (m : Model) (s : EvalScenario) : Prop := ¬ InTrainingData m s

/-- **B.1** If a scenario was generated strictly after a checkpoint's freeze
time, and the checkpoint's training cutoff is at or before its freeze time, then
the scenario is not in the checkpoint's training data.

The hypothesis `hContains` is the only assumed property of `InTrainingData`:
training data only contains scenarios generated at or before the training
cutoff. -/
theorem generated_after_freeze_not_in_training
    (m : Model) (s : EvalScenario)
    (hContains : ∀ {m' : Model} {s' : EvalScenario},
      InTrainingData m' s' → s'.generated_at ≤ m'.training_cutoff)
    (hGen : s.generated_at > m.freeze_time)
    (hFreeze : m.training_cutoff ≤ m.freeze_time) :
    ¬ InTrainingData m s := by
  intro hIn
  have hle : s.generated_at ≤ m.training_cutoff := hContains hIn
  linarith

/-- **B.2** A hidden-evaluation scenario generated after the checkpoint freeze
time is clean with respect to that checkpoint's training data. -/
theorem post_freeze_hidden_eval_clean_for_model
    (m : Model) (s : EvalScenario)
    (hContains : ∀ {m' : Model} {s' : EvalScenario},
      InTrainingData m' s' → s'.generated_at ≤ m'.training_cutoff)
    (hGen : s.generated_at > m.freeze_time)
    (hFreeze : m.training_cutoff ≤ m.freeze_time) :
    Clean InTrainingData m s :=
  generated_after_freeze_not_in_training InTrainingData m s hContains hGen hFreeze

end Verifiable.GeneratedAfterFreeze
