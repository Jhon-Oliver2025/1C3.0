import os
import sys

# Configurar encoding UTF-8 para o ambiente
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configurar stdout e stderr para UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

print("Encoding configurado para UTF-8")