import os

path = "./debug"

if os.path.exists(path):
    for filename in os.listdir(path):
        if filename.endswith(".log"):
            with open(os.path.join(path, filename), 'r') as file:
                lines = file.readlines()
                if not lines or lines[0].lower() == "[level: warning]\n":
                    continue

            with open(os.path.join(path, filename), 'w') as file:
                file.write('[Level: warning]\n')
                for line in lines:
                    if 'warning' in line:
                        file.write(line)