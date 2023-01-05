VERSION=v1
DOCKERUSER=gautam018

build:
	docker build -f Dockerfile -t emailconsumer .

push:
	docker tag emailconsumer $(DOCKERUSER)/emailconsumer:$(VERSION)
	docker push $(DOCKERUSER)/emailconsumer:$(VERSION)
	docker tag emailconsumer $(DOCKERUSER)/emailconsumer:latest
	docker push $(DOCKERUSER)/emailconsumer