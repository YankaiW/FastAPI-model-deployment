docker-base:
	docker build --progress=plain --platform=linux/amd64 -f ./Dockerfile -t CONTAINER_REGISTRY:"$(shell poetry version -s)" .
	docker image push CONTAINER_REGISTRY:"$(shell poetry version -s)"