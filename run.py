import os
import sys
import ssl
from django.core.management.commands.runserver import Command as Runserver
from django.core.servers.basehttp import WSGIServer

class SecureHTTPServer(WSGIServer):
    def __init__(self, address, handler_cls, **kwargs):
        super().__init__(address, handler_cls, **kwargs)
        # Generate self-signed certificate if needed
        self.socket = ssl.wrap_socket(
            self.socket,
            certfile='./cert.pem',
            keyfile='./key.pem',
            server_side=True,
            ssl_version=ssl.PROTOCOL_TLS_SERVER,
        )

class Command(Runserver):
    def handle(self, *args, **options):
        # Generate self-signed certificate if it doesn't exist
        if not (os.path.exists('cert.pem') and os.path.exists('key.pem')):
            self.generate_self_signed_cert()
        
        # Use our custom HTTP server
        self.server_cls = SecureHTTPServer
        
        # Run the server
        super().handle(*args, **options)
    
    def generate_self_signed_cert(self):
        from OpenSSL import crypto
        
        # Create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)
        
        # Create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = 'US'
        cert.get_subject().ST = 'State'
        cert.get_subject().L = 'City'
        cert.get_subject().O = 'Organization'
        cert.get_subject().OU = 'Organizational Unit'
        cert.get_subject().CN = 'localhost'
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for 1 year
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')
        
        # Save certificate
        with open('cert.pem', 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open('key.pem', 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
