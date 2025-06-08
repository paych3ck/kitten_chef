import grpc
from concurrent import futures
from auth import auth_pb2, auth_pb2_grpc
from auth.handler import AuthHandler
from auth.repository import AuthRepository
from auth.service import AuthService
from grpc_reflection.v1alpha import reflection

def serve() -> None:
    repo = AuthRepository()
    service = AuthService(repo)
    handler = AuthHandler(service)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServicer_to_server(handler, server)

    SERVICE_NAMES = (
        auth_pb2.DESCRIPTOR.services_by_name["Auth"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port('[::]:50051')
    print("Starting AuthService on port 50051…")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()