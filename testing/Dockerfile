FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
        curl \
        python3 \
        python3-pip \
        unzip

RUN curl -L -o vault.zip https://releases.hashicorp.com/vault/0.9.3/vault_0.9.3_linux_amd64.zip && \
        unzip -d /usr/local/bin vault.zip && \
        rm -f vault.zip

RUN groupadd docker
