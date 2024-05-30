import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Chave de API da OMDb
API_KEY = 'e4e2b0d9'

# Variável para controlar se a análise foi feita ou não
analise_feita = False


# Função para obter detalhes do filme a partir da OMDb
def get_movie_details(movie_name):
  url = f'http://www.omdbapi.com/?apikey={API_KEY}&t={movie_name}'
  response = requests.get(url)
  data = response.json()
  if data['Response'] == 'True':
    # Obter a classificação (rating) da fonte "Internet Movie Database"
    imdb_rating = next((rating['Value'] for rating in data['Ratings']
                        if rating['Source'] == 'Internet Movie Database'),
                       None)
    movie_details = {
        'Title': data['Title'],
        'Year': data['Year'],
        'Rated': imdb_rating,
        'Actors': data['Actors'],
        'Genre': data['Genre'],
        'Awards': data['Awards'],
        'Director': data['Director'],
        'Runtime': data['Runtime'],
        'BoxOffice': data['BoxOffice'],
        'Poster': data['Poster']  # Adicionando o pôster do filme
    }
    return movie_details
  else:
    return None


# Função para obter filmes por categoria (exceto o filme fornecido)
def get_movies_by_category(category, exclude_movie):
  url = f'http://www.omdbapi.com/?apikey={API_KEY}&type=movie&s={category}'
  response = requests.get(url)
  data = response.json()
  if data['Response'] == 'True':
    movies = []
    for movie in data['Search']:
      if movie['Title'] != exclude_movie:
        movie_details = get_movie_details(movie['Title'])
        if movie_details:
          movies.append(movie_details)
        if len(movies) >= 3:
          break  # Parar após encontrar 3 filmes
    return movies
  else:
    return None


# Rota para a página inicial
@app.route('/', methods=['GET', 'POST'])
def index():
  global analise_feita
  if request.method == 'POST':
    analise_feita = True
    movie_name = request.form['movie']  # Obter o nome do filme do formulário
    return redirect(url_for('result', movie=movie_name))
  else:
    return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Análise de Filmes</title>

                <style>
                   body, html {
                       margin: 0;
                       height: 100%;
                       background-image: url("https://help.nflxext.com/0af6ce3e-b27a-4722-a5f0-e32af4df3045_what_is_netflix_5_en.png");
                       background-size: cover; /* Garante que a imagem de fundo cubra todo o corpo */
                       background-position: center; /* Centraliza a imagem de fundo */
                       background-attachment: fixed; /* Fixa a imagem de fundo */
                   }
                   .outro-container {
                       display: flex;
                       justify-content: center;
                       align-items: center;
                       height: 100vh;
                   }

                   .container {
                       background-color: black;
                       color: red;
                       border: 2px solid white; /* Adiciona uma borda branca */
                       padding: 20px; /* Adiciona um espaçamento interno */
                       max-width: 400px; /* Define a largura máxima */
                       height: 150px;
                   }

                   input[type="text"],
                   button {
                       border-radius: 10px;
                       padding: 5px 10px;
                       margin: 5px;
                       border: none;
                   }
                </style>
            </head>
            <body>
              <div class="outro-container">
                <div class="container">
                     <h1>Análise de Filmes</h1>
                    <form action="/" method="post">
                        <label for="movie">Digite o nome do filme:</label>
                        <input type="text" id="movie" name="movie">
                        <button type="submit">Analisar</button>
                    </form>
                </div>
              </div>
            </body>
            </html>
            """


# Rota para a página de resultados
@app.route('/result')
def result():
  global analise_feita
  if analise_feita:
    movie_name = request.args.get(
        'movie')  # Obter o nome do filme dos parâmetros da URL
    movie_data = get_movie_details(movie_name)
    if movie_data:
      # Exibir detalhes do filme dentro de uma caixa destacada
      result_html = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Resultado</title>
                    <style>
                        body {{
                            background-color: black;
                            color: white;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        }}

                    </style>
                </head>
                <body>
                    <div style="background-color: black; padding: 20px;">
                    <h1 style="display: flex; flex-direction: column; 
                    align-items: center;
                    color: white; border-radius: 10px; justify-content: center;">
                    {movie_data['Title']}
                    </h1>
                    <img src="{movie_data['Poster']}" style="float:left; margin-right:20px;">
                    <div style="color: red; display: inline-block; flex-direction: column;
                    flex-wrap: wrap; align-items: baseline; padding: 10px; font-size: 20px;
                     align-content: space-between;">
                        <p><strong>Ano de Lançamento:</strong> {movie_data['Year']}</p>
                        <p><strong>Classificação IMDb:</strong> {movie_data['Rated']}</p>
                        <p><strong>Diretor:</strong> {movie_data['Director']}</p>
                        <p><strong>Elenco:</strong> {movie_data['Actors']}</p>
                        <p><strong>Gênero:</strong> {movie_data['Genre']}</p>
                        <p><strong>Duração:</strong> {movie_data['Runtime']}</p>
                        <p><strong>Prêmios:</strong> {movie_data['Awards']}</p>
                        <p><strong>Bilheteria:</strong> {movie_data['BoxOffice']}</p>
                    </div>
                
                <div style="align-self: flex-start;">
                <form action="/" method="get">
                    <button style="display: flex; background-color: black; color: white;
                    border-radius: 10px; font-size: 15px;" 
                    type="submit">
                      Voltar ao menu!
                    </button>
                </form>
                </div>
                </div>
                </body>
                </html>
                """

      # Adicionar análise de filmes por categoria
      category = movie_data['Genre'].split(',')[
          0]  # Obter a primeira categoria listada
      movies_by_category = get_movies_by_category(category,
                                                  movie_data['Title'])
      if movies_by_category:
        result_html += "<h2>Outros filmes na mesma categoria:</h2>"
        for movie in movies_by_category:
          result_html += f"""
                        <div style="background-color: black; padding: 20px; margin-top: 20px; 
                        justify-content: space-between; align-items: stretch;">
                        <h2 style="color: white;">{movie['Title']}</h2>
                        <img src="{movie['Poster']}" style="float:left; margin-right:20px;">
                        <div style="color: red; display: inline-block; flex-direction: column;
                        flex-wrap: wrap; align-items: baseline; padding: 10px; font-size: 20px;
                         align-content: space-between;">
                            <p><strong>Ano de Lançamento:</strong> {movie['Year']}</p>
                            <p><strong>Classificação IMDb:</strong> {movie['Rated']}</p>
                            <p><strong>Diretor:</strong> {movie['Director']}</p>
                            <p><strong>Elenco:</strong> {movie['Actors']}</p>
                            <p><strong>Gênero:</strong> {movie['Genre']}</p>
                            <p><strong>Duração:</strong> {movie['Runtime']}</p>
                            <p><strong>Prêmios:</strong> {movie['Awards']}</p>
                            <p><strong>Bilheteria:</strong> {movie['BoxOffice']}</p>
                        </div>
                        </div>
                    """
      return result_html
    else:
      return '<h1>Filme não encontrado</h1>'
  else:
    return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
