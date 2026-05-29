from flask import Flask, render_template, send_file, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from ia.main import analisar_arquivo, numerar_linhas, analisarCodigo, gerar_readme_arquivo
resultado_global = None
# imports
app = Flask(__name__)
app.secret_key = "segredo"

# Rota Home, página principal
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():

    arquivo = request.files.get("arquivo")

    codigo = request.form.get("codigo")

    if (
        arquivo and arquivo.filename != ""
        and
        codigo and codigo.strip() != ""
    ):

        flash("Envie apenas um método de análise")
        return redirect(url_for("index"))


    if arquivo and arquivo.filename != "":

        pasta_uploads = os.path.join(os.getcwd(), "temp")

        os.makedirs(
            pasta_uploads,
            exist_ok=True
        )

        # CAMINHO DO ARQUIVO
        caminho = os.path.join(
            pasta_uploads,
            "arquivo_analise.py"
        )

        arquivo.save(caminho)
        resultado_ia = analisar_arquivo(caminho)
        gerar_readme_arquivo(caminho)

        global resultado_global
        resultado_global = resultado_ia

        # ENVIA PARA O HTML
        return render_template(
            "analise.html",
            dados= resultado_ia
        )

    elif codigo and codigo.strip() != "":

        pasta_uploads = os.path.join(os.getcwd(), "temp")
        os.makedirs(
            pasta_uploads,
            exist_ok=True
        )

        caminho = os.path.join(
            pasta_uploads,
            "arquivo_analise.py"
        )

        with open(caminho, "w", encoding="utf-8") as f:
            f.write(codigo)

        codigo_numerado = numerar_linhas(codigo)
        resultado_ia = analisarCodigo(codigo_numerado)
        gerar_readme_arquivo(caminho)


        resultado_global = resultado_ia

        # ENVIA PARA O HTML
        return render_template(
            "analise.html",
            dados= resultado_ia
        )

    else:
        flash("Envie algum documento para realizar a análise")
        return redirect(url_for("index"))
    

@app.route("/analise")
def analise():
    return render_template(
        "analise.html", 
        dados = resultado_global
    )


# Rota para tela de documentação e envio dos dados criados pela IA
@app.route("/documentacao")
def documentacao():
    return render_template("documentacao.html")


# Rota para baixar o documento README gerado pela IA
@app.route("/downloadReadme")
def downloadReadme():
    caminho_arquivo = "docs/README.md"

    return send_file(
        caminho_arquivo,
        as_attachment=True
    )


# Inicio do programa
if __name__ == "__main__":
    app.run(debug=True, 
            use_reloader=False
            )
