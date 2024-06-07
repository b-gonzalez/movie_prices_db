##Style guide for docstrings: https://numpydoc.readthedocs.io/en/latest/format.html

from simplejustwatchapi.justwatch import search
import pandas as pd
import sqlalchemy as sa
from datetime import datetime
import shutil
import sqlite3
from pathlib import Path
import sys

def create_db(db_name:str, query_file_name:str) -> None:
    """
    Creates a sqlite database file and executes a few queries
    on this new file
    
    Parameters
    ----------
    
    db_name
        The file name for the database to be created
        
    query_file_name
        The file name for the sql file containing the queries to be executed
    """
    movie_db = db_name

    conn = sqlite3.connect(movie_db)
    c = conn.cursor()
    
    fd = open(query_file_name, 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    queries = sqlFile.split(';--')

    for query in queries:
        try:
            c.execute(query)
            conn.commit()
        except Exception as e:
            print(f"Error: {e.message}")
            
    c.close()
    conn.close()
    
def get_justwatch_data_from_movies(movies:pd.DataFrame) -> list[str]:
    """
    Returns a list containing movie data from a dataframe input
    
    Parameters
    ----------
    
    movies
        A dataframe containing movie data
        
    Returns
    -------
    movies_list
        A list containing movie data
    """
    movies_list = []
    
    for index, row in movies.iterrows():
        movie = row['movie_name']

        movie_url = row['url']

        # need to remove "www."" because url in media entry will not contain it
        temp_url = movie_url.replace("www.", "")

        MediaEntries = search(movie, "US", "en", 15, False)

        media_entry = None

        for me in MediaEntries:

            # check if media entry matches URL and exit loop once you have a match
            if me.url == temp_url:
                media_entry = me
                break

        # process media entry if you found a match in the previous step
        if media_entry != None:
            movie = media_entry.title

            offers = media_entry.offers

            # filter for offers that have a price value, are available to buy, and are either HD or 4k
            filtered_offers = [
                o
                for o in offers
                if o.price_value != None
                and o.monetization_type == "BUY"
                and o.presentation_type in ["HD", "_4K"]
            ]

            # add movie name, vendor name, video quality, justwatch url, and price from the filtered offers to a dictionary
            df_list = [
                {
                    "movie": movie,
                    "vendor": fo.package.name,
                    "presentation_type": fo.presentation_type,
                    "price_value": fo.price_value,
                }
                for fo in filtered_offers
            ]

            movies_list += df_list
    
    return movies_list

def add_movies_to_db(movies_list:list[str], engine:sa.engine.base.Engine, today:str) -> None:
    """
    Adds movie data to the database
    
    Parameters
    ----------
    
    movies_list
        A list containing movie data
        
    engine
        SQLAlchemy engine
        
    today
        a string containing today's date
    """
    # Process if at least one movie was processed in previous step
    if len(movies_list) > 0:
        # code for pandas to create a dataframe and write to CSV

        df1 = pd.DataFrame.from_dict(movies_list)
        
        df2 = pd.read_sql('select movie_id, movie_name from movies', engine)

        df3 = pd.merge(df1, df2, left_on='movie', right_on='movie_name', how="inner")
        
        df4 = pd.read_sql('select vendor_id, vendor from vendors', engine)
        
        df5 = pd.merge(df3, df4, left_on='vendor', right_on='vendor', how="inner")

        df5 = df5.drop(['movie','movie_name','vendor'], axis=1)

        df5['date']= today

        df5.to_sql('prices', con=engine, if_exists='append',index=False)
        
def backup_db(src:str, today:str) -> None:
    """
    Creates a copy of the current database in a backup folder
    
    Parameters
    ----------
    
    src
        The source path of the database
        
    today
        a string containing today's date
    """
        #backup database
        
    Path("db_backup").mkdir(exist_ok=True)
    
    dst = fr"db_backup\movies_db_backup_{today}.db"

    shutil.copyfile(src, dst)

def main(movie_db:str) -> None:
    """
    Main function that calls all of the other functions.
    
    Parameters
    ----------
    
    movie_db
        The name of the movie database
        
    Examples
    --------
    main("movies_db.db")
    """

    my_file = Path(movie_db)

    if not my_file.is_file():
        create_db(movie_db, "src/movies_db_queries.sql")
        print(f"{movie_db} is now created. Use add_movie_to_db to add movies to the database. After, rerun this script to query data for those movies.")
        sys.exit()
        
    engine = sa.create_engine(f'sqlite:///{movie_db}', echo=False)
    
    movies_query = """
        SELECT DISTINCT movie_name, url 
        FROM movie_data
        ORDER BY movie_name
    """

    movies = pd.read_sql(movies_query, engine)

    movies_list = []

    if len(movies.index) > 0:
        movies_list = get_justwatch_data_from_movies(movies)
    
        # Process if at least one movie was processed in previous step
        
        today = datetime.today().strftime('%Y-%m-%d')
        
        if len(movies_list) > 0:
            add_movies_to_db(movies_list, engine, today)
            backup_db(movie_db, today)
            print("Finished!")
    else:
        print("No movies in database to query from justwatch. Please use the add_movie_to_db script to add movies to the database")
        
main("movies_db.db")