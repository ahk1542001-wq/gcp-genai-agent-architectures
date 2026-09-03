# 🚀 Sanctuary OS — Production Deployment & Rollback Runbook

**Target Platform:** Google Cloud Run (Fully Managed Serverless Container)  
**Security Standard:** Google AI Studio Enterprise Security Constitution  
**Zero-Downtime Target:** 100% Traffic Shift with Automated Revision Rollback  

---

## 1. Prerequisites & Environment Variables

### Required Google Cloud APIs
Ensure the following APIs are enabled on your GCP project:
```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  cloudbuild.googleapis.com
```

### Environment Variables Matrix

| Variable | Scope | Production Value / Source | Description |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | Cloud Run Env | `production` | Enables fail-closed security gates & disables test auth |
| `ALLOW_TEST_AUTH` | Cloud Run Env | `false` | Explicitly forbids deterministic tokens |
| `USE_MOCK_DB` | Cloud Run Env | `false` | Connects directly to Cloud Firestore in Datastore mode |
| `SECRET_MANAGER_PROJECT_ID` | Cloud Run Env | `$GCP_PROJECT_ID` | Enables keyless ADC retrieval from Secret Manager |
| `FIREBASE_PROJECT_ID` | Cloud Run Env | `$FIREBASE_PROJECT_ID` | Required for Firebase Admin token signature verification |
| `GEMINI_API_KEY` | Secret Manager | Stored in Secret Manager as `GEMINI_API_KEY` | Google AI Studio Gemini Flash API Key |

---

## 2. Keyless Secret Setup via Google Secret Manager

Never store API keys in environment variables, Dockerfiles, or git repositories:

```bash
# 1. Create the Secret Manager secret
gcloud secrets create GEMINI_API_KEY --replication-policy="automatic"

# 2. Add secret version (paste your Google AI Studio API key)
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=-

# 3. Grant the Cloud Run Service Account Secret Accessor permission
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 3. Container Build via Artifact Registry

Create an Artifact Registry repository and build the container hermetically:

```bash
# 1. Create Docker repository if not exists
gcloud artifacts repositories create apac-sanctuary \
  --repository-format=docker \
  --location=asia-southeast1 \
  --description="Sanctuary OS Container Images"

# 2. Build and submit container image via Cloud Build
REGION="asia-southeast1"
PROJECT_ID=$(gcloud config get-value project)
IMAGE_TAG="asia-southeast1-docker.pkg.dev/${PROJECT_ID}/apac-sanctuary/sanctuary-os:$(git rev-parse --short HEAD)"

gcloud builds submit --tag "${IMAGE_TAG}" 04-personal-gemini-journal/
```

---

## 4. Production Cloud Run Deployment

Deploy with automatic scale-to-zero, minimum 1 replica during peak, and 1 GiB memory:

```bash
gcloud run deploy sanctuary-os \
  --image="${IMAGE_TAG}" \
  --platform=managed \
  --region=asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production,ALLOW_TEST_AUTH=false,USE_MOCK_DB=false,SECRET_MANAGER_PROJECT_ID=${PROJECT_ID},FIREBASE_PROJECT_ID=${PROJECT_ID}" \
  --cpu=1 \
  --memory=1Gi \
  --min-instances=0 \
  --max-instances=10 \
  --port=8080 \
  --timeout=60s
```

---

## 5. Post-Deployment Verification & Smoke Tests

Run smoke tests against the live production Cloud Run URL:

```bash
SERVICE_URL=$(gcloud run services describe sanctuary-os --region=asia-southeast1 --format='value(status.url)')

# 1. Health Probe
curl -f -s "${SERVICE_URL}/health" | jq .

# 2. Public Configuration Check
curl -f -s "${SERVICE_URL}/api/public-config" | jq .

# 3. Security Gate Check: Must return 401 Unauthorized for test token
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer test-token:guest:guest@test.com" "${SERVICE_URL}/api/settings")
if [ "${HTTP_CODE}" -eq 401 ]; then
  echo "✓ PASS: Production rejected test token (HTTP 401)"
else
  echo "✗ FAIL: Expected 401, got ${HTTP_CODE}"
  exit 1
fi
```

---

## 6. Zero-Downtime Rollback Procedure

If any anomaly or failure is detected in production, rollback traffic immediately to the previous stable revision:

```bash
# 1. List recent revisions
gcloud run revisions list --service=sanctuary-os --region=asia-southeast1

# 2. Shift 100% traffic back to previous stable revision
PREVIOUS_REVISION="sanctuary-os-PREVIOUS-REVISION-NAME"
gcloud run services update-traffic sanctuary-os \
  --region=asia-southeast1 \
  --to-revisions="${PREVIOUS_REVISION}=100"

# 3. Verify traffic allocation
gcloud run services describe sanctuary-os --region=asia-southeast1 --format='value(status.traffic)'
```
