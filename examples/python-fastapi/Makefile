all:
	python3 -m src.main

run:
	python3 -m src.main

generate-fernet-key:
	dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64
