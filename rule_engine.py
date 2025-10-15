# rule_engine.py
import yaml
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class Treatment(BaseModel):
    med: str
    dose: Optional[str] = None
    duration_days: Optional[int] = None
    notes: Optional[str] = None

class Rule(BaseModel):
    id: str
    name: str
    priority: int
    conditions: Dict[str, Any]
    severity: str
    treatments: List[Treatment]

class RuleEngine:
    def __init__(self, rules_path: str = "rules.yaml"):
        self.rules_path = rules_path
        self.rules: List[Rule] = []
        self.load_rules()

    def load_rules(self):
        with open(self.rules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        rules_raw = data.get("rules", [])
        parsed = []
        for r in rules_raw:
            # Normalize: ensure priority present
            r.setdefault("priority", 0)
            # Convert treatments to Treatment models
            treatments = [Treatment(**t) for t in r.get("treatments", [])]
            rule = Rule(
                id=r["id"],
                name=r.get("name", ""),
                priority=r["priority"],
                conditions=r.get("conditions", {}),
                severity=r.get("severity", "unknown"),
                treatments=treatments
            )
            parsed.append(rule)
        # Sort by priority desc
        self.rules = sorted(parsed, key=lambda x: x.priority, reverse=True)

    def evaluate(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate submission (dict) against rules.
        submission expected shape:
        {
          "age": int,
          "symptoms": { "fever": "high"|"moderate"|"low"|"none", "abdominal_pain": bool, ... },
          "tests": { "blood_culture": "positive"|"negative"|null }
        }
        """
        matches = []
        for rule in self.rules:
            if self._rule_matches(rule, submission):
                matches.append(rule)

        if not matches:
            # default fallback
            return {
                "matched_rules": [],
                "diagnosis_label": "No rule matched - suspected/inconclusive",
                "severity": "unknown",
                "treatments": [{"med": "Supportive care", "dose": None, "duration_days": None, "notes": "Clinical assessment recommended"}]
            }

        # take top priority match (rules already sorted)
        top = matches[0]
        return {
            "matched_rules": [{"id": r.id, "name": r.name, "priority": r.priority} for r in matches],
            "diagnosis_label": top.name,
            "severity": top.severity,
            "treatments": [t.dict() for t in top.treatments]
        }

    def _rule_matches(self, rule: Rule, submission: Dict[str, Any]) -> bool:
        cond = rule.conditions or {}
        # Check age
        age = submission.get("age")
        if "min_age" in cond and age is not None:
            if age < cond["min_age"]:
                return False
        if "max_age" in cond and age is not None:
            if age > cond["max_age"]:
                return False

        # Symptoms matching
        submission_symptoms = submission.get("symptoms", {})
        required_symptoms = cond.get("symptoms", {})
        for s_name, s_val in required_symptoms.items():
            sub_val = submission_symptoms.get(s_name)
            # if rule expects boolean true/false
            if isinstance(s_val, bool):
                if bool(sub_val) != s_val:
                    return False
            # if rule expects list of allowed values (e.g. ["high","moderate"])
            elif isinstance(s_val, list):
                if sub_val not in s_val:
                    return False
            else:
                # other forms (equality)
                if sub_val != s_val:
                    return False

        # optional: test results
        test_reqs = cond.get("test_results", {})
        submission_tests = submission.get("tests", {})
        for t_name, t_val in test_reqs.items():
            if submission_tests.get(t_name) != t_val:
                return False

        # passed all checks
        return True
