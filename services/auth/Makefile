PROTO_DIR := protos
OUT_DIR   := src/auth
PROTO     := auth.proto

proto-auth:
	poetry run python -m grpc_tools.protoc \
	  --proto_path=$(PROTO_DIR) \
	  --python_out=$(OUT_DIR) \
	  --grpc_python_out=$(OUT_DIR) \
	  --pyi_out=$(OUT_DIR) \
	  $(PROTO_DIR)/$(PROTO)

install: proto-auth	
	poetry install

run:
	poetry run python src/auth/server.py
