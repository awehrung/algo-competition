FROM golang:1.27

WORKDIR /usr/src/app

COPY go.mod ./
RUN go mod download

COPY src .
RUN go build -v -o /usr/local/bin/app ./...

ENTRYPOINT ["app"]
