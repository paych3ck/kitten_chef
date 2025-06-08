from auth import auth_pb2, auth_pb2_grpc
from auth.service import AuthService
import grpc

class AuthHandler(auth_pb2_grpc.AuthServicer):
    def __init__(self, service: AuthService):
        self.service = service

    def Register(self, request: auth_pb2.RegisterRequest, context: grpc.ServicerContext):
        try:
            user_id = self.service.register(request.login, request.password)
            return auth_pb2.RegisterResponse(user_id=user_id)
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def Login(self, request: auth_pb2.LoginRequest, context: grpc.ServicerContext):
        try:
            token = self.service.login(request.username, request.password)
            return auth_pb2.LoginResponse(token=token)
        except ValueError as ve:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, str(ve))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))