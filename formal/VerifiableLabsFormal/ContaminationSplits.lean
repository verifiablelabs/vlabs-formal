import Mathlib

/-!
# ContaminationSplits

Module **A** of the contamination-resistant evaluation track.

This file formalizes a minimal *split / release policy* for evaluation
scenarios and proves that hidden-evaluation scenarios cannot, under a valid
policy, simultaneously play the role of training or publicly released
scenarios.

These are honest *policy-consistency* statements: they say that **if** the
recorded flags of a scenario are consistent with the split policy, **then**
hidden evaluations are kept disjoint from training/public usage.  They do not
claim anything about the surrounding software implementation.
-/

namespace Verifiable.ContaminationSplits

/-- The role a scenario plays in the evaluation lifecycle. -/
inductive Split where
  | Train
  | Validation
  | HiddenEval
  | PublicDemo
deriving DecidableEq, Repr

/-- A minimal scenario abstraction.  `generated_at` is a timestamp; the three
boolean flags record the *recorded* permissions/state of the scenario. -/
structure Scenario where
  id : Nat
  split : Split
  generated_at : Nat
  public_release : Bool
  train_allowed : Bool
  hidden_eval_allowed : Bool
deriving Repr

/-- A scenario is *trainable* when its recorded `train_allowed` flag is set. -/
def Trainable (s : Scenario) : Prop := s.train_allowed = true

/-- A *valid policy* for a scenario: the recorded flags are consistent with the
declared split.  We only require the two constraints needed downstream:

* a `HiddenEval` scenario must not be trainable;
* a `HiddenEval` scenario must not be publicly released. -/
structure ValidPolicy (s : Scenario) : Prop where
  hidden_not_trainable : s.split = Split.HiddenEval → s.train_allowed = false
  hidden_not_public : s.split = Split.HiddenEval → s.public_release = false

/-- **A.1** A hidden-evaluation scenario under a valid policy is not trainable. -/
theorem hidden_eval_not_trainable {s : Scenario}
    (hpol : ValidPolicy s) (hsplit : s.split = Split.HiddenEval) :
    ¬ Trainable s := by
  unfold Trainable
  rw [hpol.hidden_not_trainable hsplit]
  simp

/-- **A.2** A hidden-evaluation scenario under a valid release policy is not
publicly released. -/
theorem hidden_eval_not_public_release {s : Scenario}
    (hpol : ValidPolicy s) (hsplit : s.split = Split.HiddenEval) :
    s.public_release = false :=
  hpol.hidden_not_public hsplit

/-- **A.3** If a scenario is publicly released under a valid release policy then
it is not a hidden-evaluation scenario. -/
theorem public_release_not_hidden {s : Scenario}
    (hpol : ValidPolicy s) (hpub : s.public_release = true) :
    s.split ≠ Split.HiddenEval := by
  intro hsplit
  have := hpol.hidden_not_public hsplit
  rw [this] at hpub
  exact Bool.noConfusion hpub

/-- **A.4** A scenario cannot be both `HiddenEval` and `Train`: the split is a
single value. -/
theorem split_disjoint_hidden_train {s : Scenario}
    (hsplit : s.split = Split.HiddenEval) :
    s.split ≠ Split.Train := by
  rw [hsplit]; decide

/-- **A.5** A scenario cannot be both `PublicDemo` and `HiddenEval`. -/
theorem split_disjoint_public_hidden {s : Scenario}
    (hsplit : s.split = Split.PublicDemo) :
    s.split ≠ Split.HiddenEval := by
  rw [hsplit]; decide

end Verifiable.ContaminationSplits
