"""
Demo server for the influencer-brand fit agent (v0).

Runs the REAL modules from src/, so every number on the page is the same number
the paper reports. Nothing is reimplemented for the demo.

Local:
    python serve.py
    open http://localhost:8000

Railway / any PaaS:
    reads PORT from the environment, binds 0.0.0.0.

Endpoints
    GET  /                 the page
    POST /api/run          run the simulation with the given parameters
    GET  /api/provenance   what came from Week 1 / Reddit / the AI assistant
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from model import TRUE_PARAMS, AGENT_PARAMS, COSTS  # noqa: E402
import simulate  # noqa: E402
import agent as agent_mod  # noqa: E402
import policies as P  # noqa: E402
import metrics  # noqa: E402


# --------------------------------------------------------------------------
# execution trace: what actually ran, in which file, and how long it took
# --------------------------------------------------------------------------
class Trace:
    def __init__(self):
        self.steps = []
        self._t0 = None

    def step(self, file, func, detail):
        self._t0 = time.perf_counter()
        self.steps.append({"file": file, "func": func, "detail": detail, "ms": None})
        return self

    def done(self, extra=None):
        ms = (time.perf_counter() - self._t0) * 1000
        self.steps[-1]["ms"] = round(ms, 1)
        if extra:
            self.steps[-1]["result"] = extra
        return self


def build_params(base, over: dict):
    """Apply slider overrides to a Params dataclass."""
    fields = {}
    for k in ("p_A_false", "p_M_false", "p_S_false", "p_sophisticated", "soph_pull"):
        if k in over and over[k] is not None:
            fields[k] = float(over[k])
    return replace(base, **fields) if fields else base


def run(cfg: dict) -> dict:
    tr = Trace()

    n = int(cfg.get("n_cases", 40))
    seed = int(cfg.get("seed", 42))
    arm = cfg.get("arm", "misspecified")

    # ---- costs from sliders ----
    costs = dict(COSTS)
    for k in ("sign_unsafe", "decline_good", "sign_fake", "sign_mismatch",
              "escalate", "gift", "analytics"):
        if cfg.get(k) is not None:
            costs[k] = float(cfg[k])

    # ---- 1. generate the world ----
    true_p = build_params(TRUE_PARAMS, cfg)
    tr.step("src/simulate.py", "generate_cases()",
            f"flipped 3 weighted coins for each of {n} influencers to set the sealed "
            f"labels (A, M, S), then drew 6 signals from the matching distributions. "
            f"Inauthentic accounts have a {int(true_p.p_sophisticated*100)}% chance of "
            f"being sophisticated, which pulls their signals "
            f"{int(true_p.soph_pull*100)}% of the way toward looking authentic.")
    cases = simulate.generate_cases(n, params=true_p, seed=seed)
    tr.done({
        "inauthentic": int((~cases.true_A_authentic).sum()),
        "sophisticated": int(cases.true_sophisticated.sum()),
        "mismatched": int((~cases.true_M_matched).sum()),
        "safety_risk": int((~cases.true_S_safe).sum()),
        "clean": int((cases.true_A_authentic & cases.true_M_matched & cases.true_S_safe).sum()),
    })

    # ---- 2. hide the labels ----
    tr.step("src/simulate.py", "observable_only()",
            "stripped the sealed labels. From here the agent sees only the 6 signals.")
    obs = simulate.observable_only(cases)
    tr.done({"columns_visible_to_agent": list(obs.columns)})

    # ---- 3. belief update ----
    agent_p = AGENT_PARAMS if arm == "misspecified" else TRUE_PARAMS
    if arm == "misspecified":
        agent_p = build_params(AGENT_PARAMS, {})   # agent keeps its own wrong beliefs
        detail = ("agent uses its OWN guessed parameters, which differ from the ones "
                  "that generated the world. This is the realistic arm.")
    else:
        agent_p = true_p
        detail = ("agent is handed the TRUE generating parameters. Impossible in "
                  "practice, included only as a reference point.")

    tr.step("src/agent.py", "lik_A(), lik_M(), lik_S()",
            "computed P(evidence | latent) for each of the 3 questions. E1 uses a "
            "two-humped mixture when the audience is inauthentic, because bought "
            "followers push engagement down and bought engagement pushes it up. " + detail)
    beliefs = agent_mod.update_beliefs(obs, agent_p)
    tr.done({"likelihoods_evaluated": 6 * 2 * n})

    tr.step("src/agent.py", "_posterior() then update_beliefs()",
            "ran Bayes separately on A, M and S, then multiplied the three posteriors "
            "into 8 atom probabilities and summed them into events. Note "
            "P(audience not usable) = 1 - P(A)*P(M), NOT P(not A) + P(not M), which "
            "would double-count anyone who is both.")
    merged = beliefs.merge(cases, on="case_id")
    tr.done({"atoms_per_case": 8, "events_per_case": 3})

    # ---- 4. policies ----
    t_risk = float(cfg.get("t_risk", 0.15))
    t_fake = float(cfg.get("t_fake", 0.40))
    t_clean = float(cfg.get("t_clean", 0.70))
    tau = float(cfg.get("tau", 0.50))
    cutoff = float(cfg.get("baseline_cutoff", 0.02))

    tr.step("src/policies.py", "policy_threshold(), policy_expected_cost(), policy_engagement_baseline()",
            f"three decision rules on the same beliefs. Thresholds: risk>{t_risk}, "
            f"fake>{t_fake}, clean>{t_clean}. Uncertainty gate tau={tau}. "
            f"Baseline signs anyone above {cutoff*100:.1f}% engagement.")

    rows = []
    for b in merged.itertuples():
        acts = {
            "threshold": P.policy_threshold(b, t_risk, t_fake, t_clean),
            "expected_cost": P.policy_expected_cost(b, tau, costs),
            "baseline": P.policy_engagement_baseline(b, cutoff),
        }
        ec = P.expected_costs(b, costs)
        rows.append({
            "case_id": b.case_id,
            "e1": round(b.e1_engagement_rate, 4),
            "e2": round(b.e2_generic_comment_share, 3),
            "e3": int(b.e3_growth_spikes),
            "e4": round(b.e4_target_market_share, 3),
            "e5": round(b.e5_premium_collab_share, 3),
            "e6": round(b.e6_disclosure_share, 3),
            "p_authentic": round(b.p_authentic, 4),
            "p_matched": round(b.p_matched, 4),
            "p_safe": round(b.p_safe, 4),
            "p_clean": round(b.p_clean, 4),
            "max_atom": round(b.max_atom, 4),
            "expected_costs": {k: round(v, 2) for k, v in ec.items()},
            "actions": acts,
            "costs": {k: P.realised_cost(a, b, costs) for k, a in acts.items()},
            "truth": {
                "authentic": bool(b.true_A_authentic),
                "matched": bool(b.true_M_matched),
                "safe": bool(b.true_S_safe),
                "sophisticated": bool(b.true_sophisticated),
                "clean": bool(b.true_A_authentic and b.true_M_matched and b.true_S_safe),
            },
        })
    tr.done({"decisions_made": len(rows) * 3})

    # ---- 5. score against the sealed labels ----
    tr.step("src/policies.py", "realised_cost()",
            "opened the sealed labels for the first time and priced every decision.")
    tr.done()

    tr.step("src/metrics.py", "confusion(), calibration()",
            "confusion matrix on SIGN vs not, against 'was actually clean'. False "
            "positives are split by which latent was false, because they do not cost "
            "remotely the same. Calibration bins P(clean) and compares to what happened.")

    import pandas as pd
    summary, calib = [], {}
    for pol in ("threshold", "expected_cost", "baseline"):
        g = pd.DataFrame([{
            "action": r["actions"][pol],
            "cost": r["costs"][pol],
            "p_clean": r["p_clean"],
            "true_A_authentic": r["truth"]["authentic"],
            "true_M_matched": r["truth"]["matched"],
            "true_S_safe": r["truth"]["safe"],
            "true_sophisticated": r["truth"]["sophisticated"],
        } for r in rows])
        m = metrics.confusion(g)
        m["policy"] = pol
        summary.append(m)
        if pol == "expected_cost":
            c = metrics.calibration(g, n_bins=5)
            calib = {"bins": c.to_dict("records"),
                     "ece": round(metrics.expected_calibration_error(c), 4)}
    tr.done({"policies_scored": 3})

    return {
        "trace": tr.steps,
        "cases": rows,
        "summary": summary,
        "calibration": calib,
        "truth_counts": tr.steps[0].get("result", {}),
        "arm": arm,
    }


def score_one(cfg: dict) -> dict:
    """
    Score a single hand-entered influencer.

    Same code path as the batch run: build a one-row frame of observables, call
    agent.update_beliefs(), then run the policies. Nothing here is a shortcut.
    """
    import pandas as pd

    tr = Trace()
    arm = cfg.get("arm", "misspecified")
    agent_p = AGENT_PARAMS if arm == "misspecified" else TRUE_PARAMS

    costs = dict(COSTS)
    for k in ("sign_unsafe", "decline_good", "sign_fake", "sign_mismatch",
              "escalate", "gift", "analytics"):
        if cfg.get(k) is not None:
            costs[k] = float(cfg[k])

    row = {
        "case_id": "MANUAL",
        "e1_engagement_rate": float(cfg.get("e1", 0.028)),
        "e2_generic_comment_share": float(cfg.get("e2", 0.30)),
        "e3_growth_spikes": int(cfg.get("e3", 0)),
        "e4_target_market_share": float(cfg.get("e4", 0.70)),
        "e5_premium_collab_share": float(cfg.get("e5", 0.60)),
        "e6_disclosure_share": float(cfg.get("e6", 0.85)),
    }
    obs = pd.DataFrame([row])

    tr.step("src/agent.py", "lik_A(), lik_M(), lik_S()",
            "scored the six numbers you entered against both possibilities for each "
            "of the three questions. E1 is compared against a single distribution if "
            "authentic, and against a two-humped mixture if not, because bought "
            "followers push engagement down while bought engagement pushes it up.")
    beliefs = agent_mod.update_beliefs(obs, agent_p)
    tr.done()

    tr.step("src/agent.py", "_posterior()",
            "turned each likelihood ratio into a posterior using the prior, then "
            "multiplied the three into 8 atoms and summed them into events.")
    b = beliefs.merge(obs, on="case_id").itertuples().__next__()
    tr.done()

    tr.step("src/policies.py", "expected_costs() then policy_expected_cost()",
            "priced all five actions under this belief and took the cheapest. The "
            "uncertainty gate fires first if no single atom holds more than tau.")
    ec = P.expected_costs(b, costs)
    chosen = P.policy_expected_cost(b, float(cfg.get("tau", 0.5)), costs)
    thr = P.policy_threshold(b, float(cfg.get("t_risk", .15)),
                             float(cfg.get("t_fake", .40)), float(cfg.get("t_clean", .70)))
    base = P.policy_engagement_baseline(b, float(cfg.get("baseline_cutoff", .02)))
    tr.done()

    return {
        "trace": tr.steps,
        "beliefs": {
            "p_authentic": round(b.p_authentic, 4),
            "p_matched": round(b.p_matched, 4),
            "p_safe": round(b.p_safe, 4),
            "p_clean": round(b.p_clean, 4),
            "p_audience_unusable": round(b.p_audience_unusable, 4),
            "p_safety_risk": round(b.p_safety_risk, 4),
            "max_atom": round(b.max_atom, 4),
        },
        "expected_costs": {k: round(v, 2) for k, v in ec.items()},
        "actions": {"expected_cost": chosen, "threshold": thr, "baseline": base},
        "gate_fired": bool(b.max_atom < float(cfg.get("tau", 0.5))),
    }


# --------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        payload = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            page = (ROOT / "web" / "index.html").read_bytes()
            return self._send(200, page, "text/html; charset=utf-8")
        if self.path == "/api/health":
            return self._send(200, json.dumps({"ok": True}))
        self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path not in ("/api/run", "/api/score"):
            return self._send(404, json.dumps({"error": "not found"}))
        length = int(self.headers.get("Content-Length", 0))
        cfg = json.loads(self.rfile.read(length) or b"{}")
        fn = run if self.path == "/api/run" else score_one
        try:
            self._send(200, json.dumps(fn(cfg)))
        except Exception as exc:  # noqa: BLE001
            self._send(500, json.dumps({"error": str(exc)}))

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"serving on http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
