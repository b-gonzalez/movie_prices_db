##Style guide for docstrings: https://numpydoc.readthedocs.io/en/latest/format.html

from sqlalchemy import create_engine, Table, MetaData

from vendors import Vendor
from movies import Movies
    
def add_movie_purchase_core(movie_db:str, purchaseDate:str, purchaseAmount:float, movieName:Movies, vendor:Vendor):
  """
  Adds a movie purchase to the database
  
  Parameters
  ----------
  movie_db
    the full path of the movie database
  
  purchaseDate
    the date that the movie was purchased
  
  purchaseAmount
    The amount the movie was purchased for
    
  movieName
    The enum value that represents the movie
    
  vendor
    The enum value that represents the vendor
    
  Examples
  --------
  add_movie_purchase_core(movie_db="movies_db.db", purchaseDate='2024-03-25',purchaseAmount="4.99", Movies.Brazil, Vendor.Apple vendor=Vendor.Apple)
  """
  
  engine = create_engine(f'sqlite:///{movie_db}', echo=False)

  meta_data = MetaData()

  purchases_table = Table('purchases', meta_data, autoload_with=engine)

  meta_data.create_all(engine)

  with engine.connect() as conn:
    update_statement = purchases_table.update().where(purchases_table.c.movie_id == movieName.value).values(purchase_date=purchaseDate,purchase_amount=purchaseAmount, vendor_id=vendor.value)
    conn.execute(update_statement)
    conn.commit()
    print("Record updated!")