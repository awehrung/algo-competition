FROM golang:1.24

WORKDIR /usr/src/app

COPY go.mod ./
RUN go mod download

COPY src .
RUN go build -v -o /usr/local/bin/app ./...

ENTRYPOINT ["app"]
