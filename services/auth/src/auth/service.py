from auth import auth_pb2, auth_pb2_grpc
import grpc

class AuthService(auth_pb2_grpc.AuthServicer):
    def __init__(self, repo):
        self.repo = repo
    
    def register(self, username, password):
        return len(username) + len(password)