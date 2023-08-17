FROM alpine:latest

RUN apk update && \
    apk add spamassassin && \
    sa-update

EXPOSE 783

CMD ["spamd", "--ip-address", "--allowed-ips=0.0.0.0/0", "--allow-tell"]
