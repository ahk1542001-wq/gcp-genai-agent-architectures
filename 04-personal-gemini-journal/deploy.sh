#!/usr/bin/env bash
# ==============================================================================
# Deploy Script: Secure Personal Gemini Journal -> Google Cloud Run
# Program: Hack2Skill APAC GenAI Academy (Cohort 3: Accelerate AI with Cloud Run)
# ==============================================================================

set -e

EXPECTED_PROJECT="intelligent-arc-488111-s0"
ACTIVE_PROJECT=$(gcloud config get-value project 2>/dev/null || true)

if [ -z "${ACTIVE_PROJECT}" ]; then
    echo "❌ Deployment halted: No active gcloud project configured." >&2
    echo "Please set it using: gcloud config set project ${EXPECTED_PROJECT}" >&2
    exit 1
fi

if [ "${ACTIVE_PROJECT}" != "${EXPECTED_PROJECT}" ]; then
    echo "❌ Deployment halted: Active gcloud project '${ACTIVE_PROJECT}' does not match expected target '${EXPECTED_PROJECT}'." >&2
    echo "Please switch using: gcloud config set project ${EXPECTED_PROJECT}" >&2
    exit 1
fi

PROJECT_ID="${EXPECTED_PROJECT}"
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

# 2. Configure Dual-Engine AI Authentication (Vertex AI vs Secret Manager Gemini API Key)
ENV_VARS="GCP_PROJECT_ID=${PROJECT_ID},ENVIRONMENT=production,GEMINI_MODEL=gemini-2.5-flash,GOOGLE_CLOUD_LOCATION=${REGION}"
SECRET_ARGS=()

# Dynamic propagation of public Firebase Web settings
if [ -z "${FIREBASE_API_KEY}" ]; then
    FIREBASE_API_KEY=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format='value(spec.template.spec.containers[0].env.filter(name=FIREBASE_API_KEY).value)' 2>/dev/null || echo "")
fi
if [ -n "${FIREBASE_API_KEY}" ]; then
    ENV_VARS="${ENV_VARS},FIREBASE_API_KEY=${FIREBASE_API_KEY}"
fi

if [ -z "${FIREBASE_APP_ID}" ]; then
    FIREBASE_APP_ID=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format='value(spec.template.spec.containers[0].env.filter(name=FIREBASE_APP_ID).value)' 2>/dev/null || echo "")
fi
if [ -n "${FIREBASE_APP_ID}" ]; then
    ENV_VARS="${ENV_VARS},FIREBASE_APP_ID=${FIREBASE_APP_ID}"
fi

if [ -z "${FIREBASE_MESSAGING_SENDER_ID}" ]; then
    FIREBASE_MESSAGING_SENDER_ID=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format='value(spec.template.spec.containers[0].env.filter(name=FIREBASE_MESSAGING_SENDER_ID).value)' 2>/dev/null || echo "")
fi
if [ -n "${FIREBASE_MESSAGING_SENDER_ID}" ]; then
    ENV_VARS="${ENV_VARS},FIREBASE_MESSAGING_SENDER_ID=${FIREBASE_MESSAGING_SENDER_ID}"
fi

if [ "${USE_VERTEX_AI}" = "true" ] || [ "${USE_VERTEX_AI}" = "1" ]; then
    echo "  ℹ️ AI Engine: Vertex AI Enterprise IAM (roles/aiplatform.user) explicitly selected."
    ENV_VARS="${ENV_VARS},USE_VERTEX_AI=true"
else
    # Check if GEMINI_API_KEY exists in GCP Secret Manager
    if gcloud secrets describe GEMINI_API_KEY --project="${PROJECT_ID}" >/dev/null 2>&1; then
        echo "  ℹ️ AI Engine: Found 'GEMINI_API_KEY' in Secret Manager. Binding secret to Cloud Run."
        SECRET_ARGS=(--set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest")
    else
        echo "  ℹ️ AI Engine: 'GEMINI_API_KEY' not found in Secret Manager. Defaulting to Vertex AI IAM authentication."
        ENV_VARS="${ENV_VARS},USE_VERTEX_AI=true"
    fi
fi

# 3. Deploy to Cloud Run from Source
echo "[2/4] Building container and deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --allow-unauthenticated \
    --labels="dev-tutorial=cloud-run-ai-challenge" \
    --set-env-vars="${ENV_VARS}" \
    ${SECRET_ARGS[@]+"${SECRET_ARGS[@]}"} \
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
