.PHONY: ui/build ui/tag ui/push

VERSION?=$(shell git rev-parse --short HEAD)
REGION:=southamerica-east1
UI_IMAGE_URL=${REGION}-docker.pkg.dev/mirai-454115/mirai-ui/ui
UI_PORT="5173"

ui/build:
	docker build -t mirai-ui ui

ui/tag:
	docker tag mirai-ui ${UI_IMAGE_URL}:${VERSION}

ui/push:
	docker push ${UI_IMAGE_URL}:${VERSION}

ui/provision: ui/build ui/tag ui/push
	gcloud run deploy mirai-ui \
		--image ${UI_IMAGE_URL}:${VERSION} \
		--region ${REGION} \
		--allow-unauthenticated \
		--env-vars-file ui/env.yaml \
		--port=${UI_PORT} \
		--memory 2Gi \
		--cpu 1 \
		--timeout 14m \

ui/deploy: ui/build ui/tag ui/push
	gcloud run deploy mirai-ui \
		--image ${UI_IMAGE_URL}:${VERSION} \
		--region ${REGION} \
		--env-vars-file ui/env.yaml \