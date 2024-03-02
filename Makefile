build-and-upload:
	git checkout $(tag)
	docker build . --platform linux/amd64 -t ghcr.io/dmi-feo/canada:$(tag)
	docker push ghcr.io/dmi-feo/canada:$(tag)
