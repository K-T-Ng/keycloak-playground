all: create-ca create-cert launch-keycloak

clean: shutdown-keycloak clean-cert clean-ca

create-ca:
	# CA private key
	openssl genrsa -out ca.key 2048
	
	# CA certificate
	openssl req -x509 -new -nodes -key ca.key -days 3650 -out ca.crt \
		-subj "/C=TW/CN=localhost"

clean-ca:
	# Remove CA related files
	rm -f ca.*

create-cert:
	# Private key
	openssl genrsa -out tls.key 2048

	# Certificate Signing Request (CSR)
	openssl req -new -key tls.key -out tls.csr -config csr.conf

	# Signed by CA
	openssl x509 -req -in tls.csr -CA ca.crt -CAkey ca.key \
		-CAcreateserial -out tls.crt -days 3650 \
		-extensions v3_ext -extfile csr.conf -sha256

clean-cert:
	rm -f tls.*

launch-keycloak:
	docker compose up -d

shutdown-keycloak:
	docker compose down --remove-orphans --volumes
