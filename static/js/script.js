const inputArquivo = document.getElementById("arquivo");
const nomeArquivo = document.getElementById("nome-arquivo");
const imagemArquivo = document.getElementById("icone-arquivo");
const classeEscondida = document.getElementById("selecao-arquivo");
const imagemDelecao = document.getElementById("icone-delecao");
const formIndex = document.getElementById("form-index");
const botaoEnviar = document.getElementById("botao-enviar-analise");
const loading = document.getElementById("loading")

inputArquivo.addEventListener("change", function () {
  if (inputArquivo.files.length > 0) {
    nomeArquivo.textContent = inputArquivo.files[0].name;
    imagemArquivo.setAttribute(
      "src",
      "https://cdn-icons-png.flaticon.com/512/8422/8422251.png",
    );
    classeEscondida.style.display = "flex";

    imagemDelecao.setAttribute(
      "src",
      "https://www.pngall.com/wp-content/uploads/5/Delete-Red-X-Button-PNG-Image.png",
    );
  }
});

imagemDelecao.addEventListener("click", function () {
  inputArquivo.value = "";
  classeEscondida.style.display = "none";
});


botaoEnviar.addEventListener("click", function () {
  botaoEnviar.style.opacity = 0.6;
  botaoEnviar.style.pointerEvents = "Disable"
  loading.style.display = "flex";
});