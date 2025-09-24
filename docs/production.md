## Production Checklist
- Containerization: `docker build -t handprescribe:latest . && docker push <registry>/handprescribe`
- Model Registry: `huggingface-cli login && transformers-cli upload fine_tuned_trocr` (free HF Hub)
- CI/CD: See .github/workflows/ci.yml
- Hosting: Self-host with docker-compose or low-cost (e.g., Render free tier)
- Observability: Run Prometheus: `docker run -p 9090:9090 prom/prometheus`; Grafana: `docker run -p 3000:3000 grafana/grafana`. Sample exporter in src/utils.py.
- Security: Enable TLS with Let's Encrypt: `certbot --nginx`. Encrypt disk (LUKS on Linux). Use .env for secrets.
- Privacy: HIPAA/GDPR: Obtain consent, pseudonymize PHI (redact patient_identifier), audit logs in SQLite, retention 30 days, deletion endpoint.
- Targets: CER < 0.15, F1 > 0.85; Plan: Augment to 10k samples, active learning from corrections, retrain monthly.