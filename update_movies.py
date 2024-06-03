##Style guide for docstrings: https://numpydoc.readthedocs.io/en/latest/format.html

import pandas as pd
from sqlalchemy import create_engine

def update_movies_enum(movies_db:str, movies_file:str, excludePurchasedMovies:bool = False):
  """
  creates an updated Movies enum in the movies file
  
  Parameters
  ----------
  movie_db
    The full path of the movie database
  
  movies_file
    The file name that contains the movies enum.
    This is movies.py by default.
  
  excludePurchasedMovies: optional
    If this is set to true, the movies enum will
    excldue movies that have been purchased.
    
  Examples
  --------
  update_movies_enum("movies_db.db", "movies.py")
  update_movies_enum("movies_db.db", "movies.py",excludePurchasedMovies=True)
  """
  
  #Create file if it does not exist
  file = open(movies_file, 'w+')

  #Delete all content from file
  open(movies_file, 'w').close()

  engine = create_engine(f'sqlite:///{movies_db}', echo=False)
  
  query = ""
  
  if excludePurchasedMovies:
      query = """
        SELECT DISTINCT movie_name, movie_id 
        FROM movies
        WHERE movie_id NOT IN (
          SELECT movie_id
          FROM purchases
          WHERE
            purchase_date IS NOT NULL AND
            purchase_amount IS NOT NULL
        )
    """
  else:
      query = """
        SELECT DISTINCT movie_name, movie_id 
        FROM movies
    """

  movies = pd.read_sql(query, engine)

  tfile = open('movies.py', 'a')

  tfile.write("from enum import Enum\n")

  tfile.write("\n")

  tfile.write("class Movies(Enum):\n")

  for index, row in movies.iterrows():
    line = f"""\t{
      str(row['movie_name'])
      .replace(":","")
      .replace(",","")
      .replace("?","")
      .replace("-","_")
      .replace(" ","_")
      } = {row['movie_id']}\n"""
    tfile.write(line)

  tfile.close()