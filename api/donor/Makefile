VERSION=v1
DOCKERUSER=gautam018

build:
	docker build -f Dockerfile -t donorservice .

push:
	docker tag donorservice $(DOCKERUSER)/donorservice:$(VERSION)
	docker push $(DOCKERUSER)/donorservice:$(VERSION)
	docker tag donorservice $(DOCKERUSER)/donorservice:latest
	docker push $(DOCKERUSER)/donorservice