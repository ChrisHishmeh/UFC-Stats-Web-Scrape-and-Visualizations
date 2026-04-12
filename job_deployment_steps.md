1. Once code is finalized, create local docker image using command
    `docker build -t {local-image-name} .`

2. Ensure that the artifact repo already exists in gcp. If it doesn't exist, create repo using:
    `gcloud artifacts repositories create {repo name} --repository-format=docker --location={region}`


3. Tag image with gcp region and artifact repository name. Run command
    `docker tag {local-image-name} {REGION-docker.pkg.dev/PROJECT ID/ARTIFACT REPO/NAME}`
    ensure that the artifact repo already exists in gcp.

4. Authenticate docker to allow push to GCP (modifies docker config)
    `gcloud auth configure-docker {REGION-docker.pkg.dev}`   

5. Push container to GCP artifact registry
    `docker push {longer rename from step 3}`

6. Ensure that service account has correct IAM permissions for buckets. Ensure right files are in bucket to read and write
