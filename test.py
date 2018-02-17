import subprocess
procs = [subprocess.Popen(['python', 'server.py', '-i', str(i)]) for i in range(5) ]
for i in procs:
    i.wait()


