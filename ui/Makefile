.PHONY: ui/build ui/tag ui/push

VERSION?=$(shell git rev-parse --short HEAD)
REGION=southamerica-east1
IMAGE_URL=${REGION}-docker.pkg.dev/mirai-454115/mirai-ui/ui
PORT="5173"

ui/build:
	docker build -t mirai-ui ui

ui/tag:
	docker tag mirai-ui ${IMAGE_URL}:${VERSION}

ui/push:
	docker push ${IMAGE_URL}:${VERSION}

ui/deploy: ui/build ui/tag ui/push
	gcloud run deploy mirai-ui \
		--image ${IMAGE_URL}:${VERSION} \
		--region ${REGION} \
		--allow-unauthenticated \
		--env-vars-file ui/env.yaml \
		--port=${PORT}