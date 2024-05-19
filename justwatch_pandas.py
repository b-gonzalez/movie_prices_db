from simplejustwatchapi.justwatch import search
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import shutil
import sqlite3
from pathlib import Path

movie_db = "movies_db.db"

my_file = Path(movie_db)

if not my_file.is_file():
    conn = sqlite3.connect(movie_db)
    c = conn.cursor()
    
    fd = open('movies_db_queries.sql', 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    queries = sqlFile.split(';')

    for query in queries:
        try:
            c.execute(query)
        except Exception as e:
            print(f"Error: {e.message}")
            
    c.close()
    conn.close()

engine = create_engine(f'sqlite:///{movie_db}', echo=False)

movies = pd.read_sql('select movie_name, url from movies ORDER BY movie_name',engine)

movie_url = ""

movies_list = []

if len(movies.index) > 0:
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

    # Process if at least one movie was processed in previous step
    if len(movies_list) > 0:
        # code for pandas to create a dataframe and write to CSV

        df1 = pd.DataFrame.from_dict(movies_list)
        
        df2 = pd.read_sql('select movie_id, movie_name from movies', engine)

        df3 = pd.merge(df1, df2, left_on='movie', right_on='movie_name', how="inner")
        
        df4 = pd.read_sql('select vendor_id, vendor from vendors', engine)
        
        df5 = pd.merge(df3, df4, left_on='vendor', right_on='vendor', how="inner")

        df5 = df5.drop(['movie','movie_name','vendor'], axis=1)
        
        today = datetime.today().strftime('%Y-%m-%d')

        df5['date']= today

        df5.to_sql('prices', con=engine, if_exists='append',index=False)
        
        #backup database
        src = movie_db
        
        Path("db_backup").mkdir(exist_ok=True)
        
        dst = fr"db_backup\movies_db_backup_{today}.db"

        shutil.copyfile(src, dst)

        print("Finished!")
else:
    print("No movies in database to query from justwatch. Please use the add_movie_to_db script to add movies to the database")