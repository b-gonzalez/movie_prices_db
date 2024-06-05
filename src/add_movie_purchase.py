##Style guide for docstrings: https://numpydoc.readthedocs.io/en/latest/format.html

from sqlalchemy import create_engine, Table, MetaData
    
def add_movie_purchase_core(movie_db:str, purchaseDate:str, purchaseAmount:float, movieId:int, vendorId:int) -> None:
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
    
  movieId
    The id value that represents the movie
    in the movies table
    
  vendorId
    The id value that represents the vendor
    in the movies table
    
  Examples
  --------
  add_movie_purchase_core(movie_db="movies_db.db", purchaseDate='2024-03-25',purchaseAmount="4.99", 1, 1)
  """
  
  engine = create_engine(f'sqlite:///{movie_db}', echo=False)

  meta_data = MetaData()

  purchases_table = Table('purchases', meta_data, autoload_with=engine)

  meta_data.create_all(engine)

  with engine.connect() as conn:
    update_statement = purchases_table.update().where(purchases_table.c.movie_id == movieId)\
    .values(
      purchase_date=purchaseDate,
      purchase_amount=purchaseAmount, 
      vendor_id=vendorId
    )
    conn.execute(update_statement)
    conn.commit()
    print("Record updated!")