.PHONY: api/build api/tag api/push

VERSION?=$(shell git rev-parse --short HEAD)
REGION=southamerica-east1
IMAGE_URL=${REGION}-docker.pkg.dev/mirai-454115/mirai-api/api

api/build:
	docker build -t mirai-api api

api/tag:
	docker tag mirai-api ${IMAGE_URL}:${VERSION}

api/push:
	docker push ${IMAGE_URL}:${VERSION}

api/deploy: api/build api/tag api/push
	gcloud run deploy mirai-api \
		--image ${IMAGE_URL}:${VERSION} \
		--region ${REGION} \
		--allow-unauthenticated \
		--env-vars-file api/env.yaml