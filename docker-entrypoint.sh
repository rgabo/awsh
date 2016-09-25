#!/bin/bash
# Usage: docker run awsh [options]
#
# There are no options currently supported.
#
# Environment variables:
#
#   * AWS_ACCESS_KEY_ID
#   * AWS_SECRET_ACCESS_KEY

set -e

configure_s3cmd() {
    if [ -z "${AWS_ACCESS_KEY_ID}" ]; then
        echo "AWS_ACCESS_KEY_ID is not set."
        exit 1
    fi
    if [ -z "${AWS_SECRET_ACCESS_KEY}" ]; then
        echo "AWS_SECRET_ACCESS_KEY is not set."
        exit 1
    fi

    echo "access_key=${AWS_ACCESS_KEY_ID}" >> /root/.s3cfg
    echo "secret_key=${AWS_SECRET_ACCESS_KEY}" >> /root/.s3cfg
    echo "gpg_passphrase=$(openssl rand -base64 32)" >> /root/.s3cfg
}

main() {
    configure_s3cmd
    exec awsh "$@"
}

main "$@"
