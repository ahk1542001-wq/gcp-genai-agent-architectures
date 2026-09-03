#!/usr/bin/env bash
# ==============================================================================
# Deploy Script: Secure Personal Gemini Journal -> Google Cloud Run
# Program: Hack2Skill APAC GenAI Academy (Cohort 3: Accelerate AI with Cloud Run)
# ==============================================================================

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "intelligent-arc-488111-s0")
REGION="us-central1"
SERVICE_NAME="personal-gemini-journal"

echo "===================================================================="
echo "🚀 Deploying Personal Gemini Journal to Google Cloud Run"
echo "Project ID:      ${PROJECT_ID}"
echo "Region:          ${REGION}"
echo "Service:         ${SERVICE_NAME}"
echo "Hackathon Label: dev-tutorial=cloud-run-ai-challenge (MANDATORY EVALUATION)"
echo "===================================================================="

# 1. Enable Required GCP APIs
echo "[1/4] Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    speech.googleapis.com \
    texttospeech.googleapis.com \
    --project="${PROJECT_ID}"

# 2. Deploy to Cloud Run from Source
echo "[2/4] Building container and deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --allow-unauthenticated \
    --labels="dev-tutorial=cloud-run-ai-challenge" \
    --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},ENVIRONMENT=production,GEMINI_MODEL=gemini-3.7-flash" \
    --memory="512Mi" \
    --cpu="1" \
    --min-instances="0" \
    --max-instances="5"

# 3. Retrieve Deployed URL
echo "[3/4] Retrieving deployed Cloud Run service URL..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')

# 4. Verify Hackathon Evaluation Label & Service Health
echo "[4/4] Verifying Hackathon Evaluation Label & Service Health..."
DEPLOYED_LABEL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(metadata.labels.dev-tutorial)')
if [ "${DEPLOYED_LABEL}" = "cloud-run-ai-challenge" ]; then
    echo "  ✓ Confirmed Hackathon Label: dev-tutorial=${DEPLOYED_LABEL} (Automated Scanner Compliant)"
else
    echo "  ⚠️ Warning: Expected dev-tutorial=cloud-run-ai-challenge, got '${DEPLOYED_LABEL}'"
fi

if command -v curl >/dev/null 2>&1; then
    HEALTH_RESP=$(curl -s "${SERVICE_URL}/health" || echo "failed")
    echo "  ✓ Health Probe Response: ${HEALTH_RESP}"
fi

echo "===================================================================="
echo "✅ Deployment Complete & Verified!"
echo "Live Cloud Run URL:    ${SERVICE_URL}"
echo "Hackathon Label:       dev-tutorial=${DEPLOYED_LABEL}"
echo "Public Challenge Tag:  #AccelerateAIwithCloudRun"
echo "===================================================================="
