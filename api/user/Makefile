VERSION=v1
DOCKERUSER=gautam018

build:
	docker build -f Dockerfile -t userservice .

push:
	docker tag userservice $(DOCKERUSER)/userservice:$(VERSION)
	docker push $(DOCKERUSER)/userservice:$(VERSION)
	docker tag userservice $(DOCKERUSER)/userservice:latest
	docker push $(DOCKERUSER)/userservice