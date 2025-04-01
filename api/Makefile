.PHONY: api/build api/tag api/push

VERSION?=$(shell git rev-parse --short HEAD)
REGION:=southamerica-east1
API_IMAGE_URL:=${REGION}-docker.pkg.dev/mirai-454115/mirai-api/api

api/build:
	docker build -t mirai-api api

api/tag:
	docker tag mirai-api ${API_IMAGE_URL}:${VERSION}

api/push:
	docker push ${API_IMAGE_URL}:${VERSION}

api/provision: api/build api/tag api/push
	gcloud run deploy mirai-api \
		--image ${API_IMAGE_URL}:${VERSION} \
		--region ${REGION} \
		--allow-unauthenticated \
		--env-vars-file api/env.yaml \
		--add-volume name=mirai-videos,type=cloud-storage,bucket=mirai-videos \
		--add-volume-mount volume=mirai-videos,mount-path=/app/output/videos/ \
		--memory 4Gi \
		--cpu 2 \
		--timeout 14m \

api/deploy: api/build api/tag api/push
	gcloud run deploy mirai-api \
		--image ${API_IMAGE_URL}:${VERSION} \
		--region ${REGION} \
		--env-vars-file api/env.yaml \