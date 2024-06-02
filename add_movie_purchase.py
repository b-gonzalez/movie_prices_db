##Style guide for docstrings: https://numpydoc.readthedocs.io/en/latest/format.html

from sqlalchemy import create_engine, Table, MetaData
import pandas as pd
from enum import Enum

class Vendor(Enum):
    Apple = 1
    Amazon = 2
    Vudu = 3
    AMC = 4
    Mirosoft = 5
    
def add_movie_purchase_core(movie_db:str,movieName:str, purchaseDate:str, purchaseAmount:float, vendor:Vendor) -> None:
  """
  Adds a movie purchase to the database
  
  Parameters
  ----------
  movie_db
    the full path of the movie database
  
  movieName
    the name of the movie that was purchased
  
  purchaseDate
    the date that the movie was purchased
  
  purchaseAmount
    The amount the movie was purchased for
    
  vendor
    The enum value that represents the vendor
    
  Examples
  --------
  add_movie_purchase_core(movie_db="movies_db.db",movieName="Brazil", purchaseDate='2024-03-25',purchaseAmount="4.99", vendor=Vendor.Apple)
  """
  
  engine = create_engine(f'sqlite:///{movie_db}', echo=False)
  
  movie_id_query = "select movie_id from movies where movie_name = :movieName"
  
  params = {"movieName":movieName}
  
  movie_id_df = pd.read_sql(movie_id_query, engine, params=params)
  
  movieId = movie_id_df.values[0][0]

  meta_data = MetaData()

  purchases_table = Table('purchases', meta_data, autoload_with=engine)

  meta_data.create_all(engine)

  with engine.connect() as conn:
    update_statement = purchases_table.update().where(purchases_table.c.movie_id == movieId.item()).values(purchase_date=purchaseDate,purchase_amount=purchaseAmount, vendor_id=vendor.value)
    conn.execute(update_statement)
    conn.commit()
    print("Record updated!")