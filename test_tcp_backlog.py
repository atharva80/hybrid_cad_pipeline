import socket, time
import threading

# Test that 30 rapid connections do not fail
success = 0
failed = 0

def send_req(i):
    global success, failed
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(('127.0.0.1', 5050))
        s.sendall(b'{"test": 1}')
        s.close()
        success += 1
    except Exception as e:
        failed += 1

threads = []
for i in range(30):
    t = threading.Thread(target=send_req, args=(i,))
    threads.append(t)
    t.start()
    time.sleep(0.01) # fast dispatch

for t in threads:
    t.join()

print(f"TCP Test: {success} succeeded, {failed} failed.")
