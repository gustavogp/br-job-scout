# br-job-scout
Job search in Brazil in juridical area

## Deploy to Google Cloud Run

### Prerequisites

Authenticate with Google Cloud:

```bash
gcloud auth login
```

### Deploy

```bash
gcloud run jobs deploy br-job-scouter --source . --tasks 1 --max-retries 0 --region us-central1
```

### Inject environment variables

```bash
gcloud run jobs update br-job-scouter \
  --set-env-vars="GEMINI_API_KEY=<your-gemini-api-key>" \
  --set-env-vars="SMTP_USER=<sender-email>" \
  --set-env-vars="SMTP_PASSWORD=<16-digit-app-password>" \
  --set-env-vars="RECIPIENT_EMAIL=<recipient-email>"
```

### Run

```bash
gcloud run jobs execute br-job-scouter
```
