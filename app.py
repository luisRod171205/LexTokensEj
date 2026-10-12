from flask import Flask, render_template, request
import re

app = Flask(__name__)

# Reglas léxicas (tokens y expresiones regulares)
TOKENS = [
    ('PRODUCTO',      r'[Pp]roducto'),
    ('CANTIDAD',      r'[Cc]antidad'),
    ('UNIDAD',        r'[Uu]nidad'),
    ('UNIDAD_MEDIDA', r'sacos|cajas|unidades'),
    ('NOMBRE',        r'[A-Za-záéíóúÁÉÍÓÚüÜñÑ]+(?:\s[A-Za-záéíóúÁÉÍÓÚüÜñÑ]+)*'),
    ('DESCRIPCION',   r'[a-záéíóúñ]+'),
    ('NUMERO_ENTERO', r'\d+'),
    ('COMA',          r','),
    ('DOS_PUNTOS',    r':'),
    ('ESPACIO',       r'\s+'),
]

def analizar_lexico(texto):
    resultado = []
    pos = 0
    while pos < len(texto):
        match = None
        for token, patron in TOKENS:
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

# Texto por defecto
TEXTO_DEFECTO = "Juan Pérez, Producto: arroz, Cantidad: 10, Unidad: sacos"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        texto = request.form.get('pedido', '')
    else:
        texto = TEXTO_DEFECTO  # Al cargar la página, usa el texto por defecto

    resultado = None
    if texto.strip():
        resultado = analizar_lexico(texto)

    return render_template('index.html', resultado=resultado, texto=texto)

if __name__ == '__main__':
    app.run(debug=True)