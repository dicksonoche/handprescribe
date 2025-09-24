## Human-in-the-Loop Rules
- Always display confidence; if <0.7, flag for review.
- UI: Allow inline corrections; log to corrections.log for retraining.
- Policy: Pharmacist must verify all outputs. Store logs: `python scripts/log_correction.py --input json`
- Retraining: When 100+ corrections, run scripts/retrain.sh