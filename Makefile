SERVICE := python-scripts
PORT := 22
DOCKER_PORT := 2222
RUNTIME := python314
PLATFORM := linux/amd64
GCP_REGION := us-central1
GCP_HOST := us-docker.pkg.dev
GCP_REPO := cloudbuild
GCP_PROJECT_ID := your-project-id
GCP_EMAIL := my-account@your-project-id.iam.gserviceaccount.com
GCP_KEYFILE := /home/mykeyfile.json

include Makefile.env

GCP_IMAGE = $(GCP_HOST)/$(GCP_PROJECT_ID)/$(GCP_REPO)/$(SERVICE):latest

all: docker
docker: docker-build docker-run
gcp: gcp-auth gcp-config gcp-build

docker-build:
	docker build --tag $(SERVICE) --platform $(PLATFORM) .

docker-run:
	docker run -p $(DOCKER_PORT)\:$(PORT) $(SERVICE)

docker-push:
	docker push $(SERVICE)

gcp-config:
	gcloud config set project $(GCP_PROJECT_ID)
	gcloud config set core/project $(GCP_PROJECT_ID)
	gcloud config set compute/region $(GCP_REGION)

gcp-auth:
	gcloud auth activate-service-account $(GCP_EMAIL) --key-file="$(GCP_KEYFILE)"
	export GOOGLE_APPLICATION_CREDENTIALS="$(GCP_KEYFILE)"
#	gcloud auth application-default set-quota-project $(GCP_PROJECT_ID)

gcp-build:
	gcloud builds submit --tag $(GCP_IMAGE) .

gcp-cloudrun:
	gcloud config set run/region $(GCP_REGION)
	gcloud run deploy $(SERVICE) --image $(GCP_IMAGE) --port $(PORT) --platform=managed --allow-unauthenticated
