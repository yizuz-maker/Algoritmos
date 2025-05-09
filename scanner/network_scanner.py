import socket 
from scanner.banner_grabbing import obtener_banner, decodificar_banner, obtener_banner_http, determinar_http_service
"""
Escanea los puertos de una IP para determinar su estado y obtener el banner del servicio si está abierto.

@param ip La dirección IP a escanear.
@param puertos Una lista de números de puertos a comprobar.
@return Una lista de tuplas con el formato (puerto, estado, banner), donde:
        - estado es 'abierto' o 'cerrado'
        - banner contiene una cadena con información del servicio (vacía si está cerrado)
"""
def escanear_puertos(ip, puertos):
    resultados = []
    banner_decoded = ""

    for puerto in puertos:
        banner_decoded = ""

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        try:
            resultado = sock.connect_ex((ip, puerto))  

            if resultado == 0:
                estado = 'abierto'

                if puerto == 80:
                    sock = obtener_banner_http(ip, sock)
                    banner_raw = obtener_banner(sock)
                    banner_dirty = decodificar_banner(banner_raw)
                    banner_decoded = determinar_http_service(banner_dirty)
                else:
                    banner_raw = obtener_banner(sock)
                    banner_decoded = decodificar_banner(banner_raw)

                resultados.append((puerto, estado, banner_decoded))
            else:
                estado = 'cerrado'
                resultados.append((puerto, estado, banner_decoded))

        except socket.timeout:

            estado = 'cerrado'
            resultados.append((puerto, estado, banner_decoded))
            print(f"Timeout al intentar conectar al puerto {puerto} en {ip}")

        except socket.error as e:

            estado = 'cerrado'
            resultados.append((puerto, estado, banner_decoded))
            print(f"Error de socket al intentar conectar al puerto {puerto} en {ip}: {e}")

        finally:
            sock.close()  # Cerrar el socket

    return resultados
