import socket 
from concurrent.futures import ThreadPoolExecutor
from scanner.banner_grabbing import obtener_banner, decodificar_banner, obtener_banner_http, determinar_http_service

def escanear_puerto(ip, puerto):
    banner_decoded = ""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # Reducimos el timeout para mayor velocidad

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
                try:
                    banner_raw = obtener_banner(sock)
                    banner_decoded = decodificar_banner(banner_raw)
                except:
                    banner_decoded = ""

            return (puerto, estado, banner_decoded)
        else:
            estado = 'cerrado'
            return (puerto, estado, banner_decoded)

    except (socket.timeout, socket.error) as e:
        estado = 'cerrado'
        return (puerto, estado, banner_decoded)

    finally:
        sock.close()

def escanear_puertos(ip, puertos):
    resultados = []
    max_workers = min(100, len(puertos))  # Limitamos el número máximo de hilos

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(escanear_puerto, ip, puerto) for puerto in puertos]
        for future in futures:
            try:
                resultado = future.result()
                if resultado:
                    resultados.append(resultado)
            except Exception as e:
                print(f"Error en el escaneo: {e}")

    return sorted(resultados, key=lambda x: x[0])  # Ordenamos por número de puerto
