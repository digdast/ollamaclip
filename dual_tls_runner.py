import os
import socket
import ssl
import threading
import time
import uvicorn


def _pipe(src: socket.socket, dst: socket.socket):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s.close()
            except Exception:
                pass


def _handle_client(client_sock: socket.socket, internal_port: int, ssl_ctx):
    try:
        client_sock.settimeout(10.0)
        first = client_sock.recv(1, socket.MSG_PEEK)
        if not first:
            client_sock.close()
            return
        if first == b"\x16" and ssl_ctx is not None:
            client_sock = ssl_ctx.wrap_socket(client_sock, server_side=True)
        client_sock.settimeout(300.0)
        upstream = socket.create_connection(("127.0.0.1", internal_port), timeout=10.0)
        upstream.settimeout(300.0)
    except Exception:
        try:
            client_sock.close()
        except Exception:
            pass
        return

    t1 = threading.Thread(target=_pipe, args=(client_sock, upstream), daemon=True)
    t2 = threading.Thread(target=_pipe, args=(upstream, client_sock), daemon=True)
    t1.start()
    t2.start()


def run_dual_http_https(app, port: int, cert_dir: str = "/app/certs"):
    internal_port = port + 10000
    cert_file = os.path.join(cert_dir, "fullchain.pem")
    key_file = os.path.join(cert_dir, "privkey.pem")

    ssl_ctx = None
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)

    uv_thread = threading.Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": "127.0.0.1", "port": internal_port, "log_level": "info"},
        daemon=True,
    )
    uv_thread.start()
    time.sleep(0.8)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(256)
    print(f"[Dual-HTTP/HTTPS] Listening on 0.0.0.0:{port} (TLS={'enabled' if ssl_ctx else 'disabled'}) -> 127.0.0.1:{internal_port}", flush=True)

    while True:
        try:
            c_sock, _ = srv.accept()
            threading.Thread(target=_handle_client, args=(c_sock, internal_port, ssl_ctx), daemon=True).start()
        except Exception:
            pass
