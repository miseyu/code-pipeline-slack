.phony: clean
clean:
	rm -f -r tmp/*

docker-build: clean ## build docker
	docker build -f Dockerfile -t code-pipeline-slack ./

build: docker-build
	docker run -v $(shell pwd)/vendor:/app/vendor code-pipeline-slack:latest pip3.7 install -r requirements.txt -t ./vendor
	cp -Rf src/* tmp
	mv vendor tmp/vendor
	cd tmp && zip -r lambda.zip * && mv lambda.zip ../