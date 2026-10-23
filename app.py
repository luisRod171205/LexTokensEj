from flask import Flask, render_template, request, url_for
import re
import os
os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin"
from graphviz import Digraph

app = Flask(__name__)

# Carpeta para guardar las imágenes de los AFND
AFND_DIR = os.path.join('static', 'afnd')
os.makedirs(AFND_DIR, exist_ok=True)

# Reglas léxicas: cada lexema con su expresión regular
TOKENS = [
    ('NOMBRE',        r'[A-Za-záéíóúÁÉÍÓÚüÜñÑ]+(?:\s[A-Za-záéíóúÁÉÍÓÚüÜñÑ]+)*', 'Juan Pérez'),
    ('PRODUCTO',      r'[Pp]roducto', 'Producto'),
    ('DESCRIPCION',   r'[a-záéíóúñ]+', 'arroz'),
    ('CANTIDAD',      r'[Cc]antidad', 'Cantidad'),
    ('NUMERO_ENTERO', r'\d+', '10'),
    ('UNIDAD',        r'[Uu]nidad', 'Unidad'),
    ('UNIDAD_MEDIDA', r'sacos|cajas|unidades', 'sacos'),
    ('COMA',          r',', ','),
    ('DOS_PUNTOS',    r':', ':'),
]

def analizar_lexico(texto):
    resultado = []
    pos = 0
    while pos < len(texto):
        match = None
        for token, patron, _ in TOKENS:
            regex = re.compile(patron)
            match = regex.match(texto, pos)
            if match:
                lexema = match.group()
                if token != 'ESPACIO':
                    resultado.append((lexema, token))
                pos = match.end()
                break
        if not match:
            resultado.append((texto[pos], 'ERROR'))
            pos += 1
    return resultado

def generar_afnd(nombre, er):
    """Genera el AFND de una expresión regular simple y lo guarda como PNG."""
    ruta = os.path.join(AFND_DIR, f'afnd_{nombre}')
    
    # Si ya existe, no lo regenera
    if os.path.exists(ruta + '.png'):
        return f'afnd/afnd_{nombre}.png'
    
    dot = Digraph(comment=f'AFND de {nombre}')
    dot.attr(rankdir='LR')
    dot.attr('node', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='9')
    
    # Crear una cadena de estados para simular la ER
    # Para simplificar, usamos 3 estados: inicial, intermedio, final
    dot.node('q0', 'q0', shape='circle')
    dot.node('q1', 'q1', shape='circle')
    dot.node('q2', 'q2', shape='doublecircle')
    
    dot.edge('q0', 'q1', label=er)
    dot.edge('q1', 'q2', label='ε')
    
    dot.render(ruta, format='png', cleanup=True)
    return f'afnd/afnd_{nombre}.png'

# Texto por defecto
TEXTO_DEFECTO = "Juan Pérez, Producto: arroz, Cantidad: 10, Unidad: sacos"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        texto = request.form.get('pedido', '')
    else:
        texto = TEXTO_DEFECTO

    resultado = None
    if texto.strip():
        resultado = analizar_lexico(texto)

    # Generar los AFND de cada token
    afnds = []
    for token, er, ejemplo in TOKENS:
        ruta = generar_afnd(token, er)
        afnds.append({
            'token': token,
            'er': er,
            'ejemplo': ejemplo,
            'imagen': ruta
        })

    return render_template('index.html', resultado=resultado, texto=texto, afnds=afnds)

if __name__ == '__main__':
    app.run(debug=True)