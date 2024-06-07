#Style guide for docstrings: https://numpydoc.readthedocs.io/en/latest/format.html

from simplejustwatchapi.justwatch import search
import pandas as pd
from sqlalchemy import create_engine
import errno
import os

def add_movie_to_db(movie_db:str ,movie:str, url:str, excludePurchasedMovies:bool=False) -> None:
  """
  Adds a movie to the database
  
  Parameters
  ----------
  movie_db
    the full path of the movie database
  
  movie
    The name of the movie to be searched. This should correspond to the movie name on JustWatch.com
  
  url
    The url of the movie to be searched. This should correspond to the url on JustWatch.com
    
  excludePurchasedMovies: optional
    If this is set to true, the movies enum will
    excldue movies that have been purchased.
    
  Examples
  --------
  add_movie_to_db("movies_db.db","The Matrix", "https://www.justwatch.com/us/movie/the-matrix")
  """

  if not os.path.isfile(movie_db):
    raise FileNotFoundError(
    errno.ENOENT, os.strerror(errno.ENOENT), movie_db)

  engine = create_engine(f'sqlite:///{movie_db}', echo=False)
  
  query = "select distinct movie_id from movies where url = :url"

  movies = pd.read_sql(query, engine, params={"url":url})
  
  if movies.empty:
    movie_url = ""
 
    movies_list = []
        
    movie_name = movie

    movie_url = url

    # need to remove "www."" because url in media entry will not contain it
    temp_url = movie_url.replace("www.", "")

    MediaEntries = search(movie_name, "US", "en", 15, False)

    media_entry = None

    for me in MediaEntries:

        # check if media entry matches URL and exit loop once you have a match
        if me.url == temp_url:
            media_entry = me
            break
    
    if media_entry != None:
        movie_name = media_entry.title
        
        release_year = media_entry.release_year
        
        release_date = media_entry.release_date
        
        runtime_minutes = media_entry.runtime_minutes
        
        short_description = media_entry.short_description
        
        poster = media_entry.poster

        # add movie name, vendor name, video quality, justwatch url, and price from the filtered offers to a dictionary
        df_list = [{
          "movie_name": movie_name,
          "poster":poster,
          "release_date":release_date,
          "release_year": release_year,
          "runtime_minutes":runtime_minutes,
          "short_description":short_description,
          "url":movie_url
        }]

        movies_list += df_list

    # Process if at least one movie was processed in previous step
    if len(movies_list) > 0:
      print("")
        # code for pandas to create a dataframe and write to CSV

      df1 = pd.DataFrame.from_dict(movies_list)
      df1.to_sql('movies', con=engine, if_exists='append',index=False)
      
      movie_ids = pd.read_sql(query, engine, params={"url":url})
      movie_ids.to_sql('purchases', con=engine, if_exists='append',index=False)
      
      print(f"{movie_name} added to {movie_db}")