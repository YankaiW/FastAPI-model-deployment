test:
	poetry run pytest $(OPT)

coding_standards:
	poetry run isort .
	poetry run black .
	poetry run flake8 .

docker-ci-test:
	docker build --progress=plain --platform=linux/amd64 -f ./docker-ci/test_3.9 -t CONTAINER_REGISTRY/model_deployment_app:test_3.9 .
	docker image push CONTAINER_REGISTRY/model_deployment_app:test_3.9

docker-base:
	docker build --progress=plain --platform=linux/amd64 -f ./Dockerfile -t CONTAINER_REGISTRY/model_deployment_app:"$(shell poetry version -s)" .
	docker image push CONTAINER_REGISTRY/model_deployment_app:"$(shell poetry version -s)"

k8s-deploy:
	helm upgrade --install EXAMPLE k8s_dev/EXAMPLE --values k8s_dev/EXAMPLE/values.yaml

k8s-fashion-inbound-conversion-undeploy:
	helm uninstall EXAMPLE