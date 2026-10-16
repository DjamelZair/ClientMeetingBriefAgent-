"""one place that knows every figure module, so main.py makes all of them in one call."""
from client_brief_agent.report import figures_data, figures_models


def make_all(frames, layer, seg, metrics, calibration, importance):
    # the agent figures (guardrail, reviews) are made inside export, because they need the curve it builds
    paths = figures_data.make_all(frames, layer)
    paths.update(figures_models.make_all(seg, metrics, calibration, importance))
    return paths
