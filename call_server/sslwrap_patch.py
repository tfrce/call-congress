# Re-add sslwrap to Python 2.7.9+
# https://github.com/gevent/gevent/issues/477

import inspect
__ssl__ = __import__('ssl')

try:
    _ssl = __ssl__._ssl
except AttributeError:
    _ssl = __ssl__._ssl2


OldSSLSocket = __ssl__.SSLSocket


class NewSSLSocket(OldSSLSocket):
    """Fix SSLSocket constructor."""
    def __init__(
        self, sock, keyfile=None, certfile=None, server_side=False,
        cert_reqs=__ssl__.CERT_REQUIRED, ssl_version=2, ca_certs=None,
        do_handshake_on_connect=True, suppress_ragged_eofs=True, ciphers=None,
        server_hostname=None, _context=None
    ):
        OldSSLSocket.__init__(
            self, sock, keyfile=keyfile, certfile=certfile,
            server_side=server_side, cert_reqs=cert_reqs,
            ssl_version=ssl_version, ca_certs=ca_certs,
            do_handshake_on_connect=do_handshake_on_connect,
            suppress_ragged_eofs=suppress_ragged_eofs, ciphers=ciphers
        )


def new_sslwrap(
    sock, server_side=False, keyfile=None, certfile=None,
    cert_reqs=__ssl__.CERT_NONE, ssl_version=__ssl__.PROTOCOL_SSLv23,
    ca_certs=None, ciphers=None
):
    context = __ssl__.SSLContext(ssl_version)
    context.verify_mode = cert_reqs or __ssl__.CERT_NONE
    if ca_certs:
        context.load_verify_locations(ca_certs)
    if certfile:
        context.load_cert_chain(certfile, keyfile)
    if ciphers:
        context.set_ciphers(ciphers)

    caller_self = inspect.currentframe().f_back.f_locals['self']
    return context._wrap_socket(sock, server_side=server_side, ssl_sock=caller_self)

if not hasattr(_ssl, 'sslwrap'):
    _ssl.sslwrap = new_sslwrap
    __ssl__.SSLSocket = NewSSLSocket
