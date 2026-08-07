import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.engine.consent_engine import ConsentEngine
from app.engine.fatigue import FatigueEngine
from app.engine.next_best_action import NextBestActionEngine
from app.engine.suppression import SuppressionEngine
from app.models.user import User


class MockDB:
    def __init__(self, user_state):
        self.user_state = user_state

    def query(self, model):
        class QueryStub:
            def __init__(self, items):
                self.items = items

            def filter(self, *args, **kwargs):
                return self

            def order_by(self, *args, **kwargs):
                return self

            def first(self):
                return self.items[0] if self.items else None

            def all(self):
                return self.items

            def count(self):
                return len(self.items)

        if model.__name__ == "Consent":

            class DummyConsent:
                def __init__(self, c):
                    self.user_id = self.c = c
                    self.channel = c.get("channel")
                    self.status = c.get("status")
                    self.created_at = datetime.now()
                    self.expires_at = None

            consents = [DummyConsent(c) for c in self.user_state.get("consents", [])]
            return QueryStub(consents)

        if model.__name__ == "ChannelPreference":
            return QueryStub([])
        if model.__name__ == "MessageDecision":
            return QueryStub([])
        return QueryStub([])


class MockFatigueEngine(FatigueEngine):
    def __init__(self, user_states):
        self.user_states = user_states

    def calculate_fatigue_score(self, user_id, db):
        state = self.user_states.get(user_id, {})
        return state.get("fatigue_score", 0.0)


def run_eval():
    dataset_path = os.path.join(os.path.dirname(__file__), "golden_dataset.json")
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    user_states = {row["user_state"]["id"]: row["user_state"] for row in dataset}

    consent_engine = ConsentEngine()
    fatigue_engine = MockFatigueEngine(user_states)
    suppression_engine = SuppressionEngine(consent_engine, fatigue_engine)
    nba_engine = NextBestActionEngine(
        consent_engine, fatigue_engine, suppression_engine
    )

    total = len(dataset)
    correct = 0
    suppression_true_positives = 0
    suppression_false_negatives = 0

    print("--- Evaluating Next Best Action Engine ---")
    for row in dataset:
        u_state = row["user_state"]
        user = User(
            id=u_state["id"],
            lifecycle_stage=u_state["lifecycle_stage"],
            fatigue_score=u_state["fatigue_score"],
            intent_score=u_state["intent_score"],
            churn_risk=u_state.get("churn_risk", 0.0),
        )
        db = MockDB(u_state)

        decision = nba_engine.decide(user, db)

        expected_action = row.get("expected_action")
        expected_channel = row.get("expected_channel")
        expected_suppressed = row.get("expected_suppressed")

        is_correct = (
            decision.action == expected_action
            and decision.channel == expected_channel
            and decision.suppressed == expected_suppressed
        )
        if is_correct:
            correct += 1

        if expected_suppressed:
            if decision.suppressed:
                suppression_true_positives += 1
            else:
                suppression_false_negatives += 1

        print(
            f"User {user.id} -> Action: {decision.action}, Suppressed: {decision.suppressed} | Expected: {expected_action}, {expected_suppressed} | Correct: {is_correct}"
        )

    accuracy = correct / total
    recall = (
        suppression_true_positives
        / (suppression_true_positives + suppression_false_negatives)
        if (suppression_true_positives + suppression_false_negatives) > 0
        else 1.0
    )

    print("\n--- Metrics Report ---")
    print(f"Decision Accuracy: {accuracy * 100:.2f}%")
    print(f"Suppression Recall: {recall * 100:.2f}%")

    print("LLM-as-judge copy evaluation: SKIPPED (Requires valid OPENAI_API_KEY)")


if __name__ == "__main__":
    run_eval()
