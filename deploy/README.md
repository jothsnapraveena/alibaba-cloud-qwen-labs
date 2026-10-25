# Container and ACK teaching deployment

The capstone deploys the retrieval API, not hosted Qwen inference. Docker and Kubernetes execution have not been verified in this environment. Review costs and use only a cluster you are authorized to operate.

## Build and push

Build the root Dockerfile and push it to a registry accessible to your ACK cluster. Replace the image placeholder in ack.yaml with that exact image, preferably a digest. The cluster must have a suitable default StorageClass, or you must explicitly set one on the PVC. Provisioning cloud storage incurs charges.

## Configure the secret separately

Create the qwen-labs namespace before creating its secret. Set a fresh mapping in a local variable, then create a Kubernetes Secret from a temporary file or your secret-management workflow. The required shape is `{ "long-random-api-key": "alpha" }`. The Secret must be named api-keys and contain a key named mapping. Do not commit the actual mapping to git or include it in a shell command you plan to share.

This reference YAML does not create a Secret with default credentials. A missing Secret should prevent the application from starting. Environment-based secrets do not update inside existing containers until the workload restarts.

## Deploy and inspect

After replacing the image and configuring the namespace, secret and storage, apply ack.yaml using your normal approved deployment process. Check pod readiness, PVC binding and events. The deployment intentionally has one replica and uses Recreate so two pods do not concurrently mount and write the same teaching SQLite volume.

The ClusterIP Service does not create a public internet endpoint. Use a local port-forward to test. Run the HTTP load command with the correct API key in your environment and retain its report.

## Understand what persists

The PVC retains SQLite source documents, chunks, runs, events and local tickets. Container root storage is read-only and the process runs as UID 65534. The mounted data directory must allow that UID or fsGroup to write SQLite journal files. --seed-demo loads the synthetic corpus at startup. Remove it when replacing the corpus with your own ingestion process.

## Test before extending

Check readiness when storage is unavailable, behavior during restart, preservation of completed runs and overload responses. Do not add replicas until replacing the single-instance state architecture. No ingress, TLS, backup, cloud monitoring exporter, NetworkPolicy or production identity integration is included. Treat these as explicit engineering work, not implied capabilities.

## Cleanup

Delete only the resources you created for the exercise through your normal cluster process. Inspect the StorageClass reclaim policy before deleting the PVC. Deleting storage can destroy experiment data and does not always remove every billable cloud resource automatically.
