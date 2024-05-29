CREATE TABLE "movies" (
	"movie_id"	INTEGER,
	"url"	TEXT,
	"movie_name"	TEXT,
	"release_year"	INTEGER,
	"release_date"	TEXT,
	"runtime_minutes"	INTEGER,
	"short_description"	TEXT,
	"poster"	TEXT,
	PRIMARY KEY("movie_id")
);

CREATE TABLE "vendors" (
	"vendor_id"	INTEGER,
	"vendor"	TEXT,
	PRIMARY KEY("vendor_id")
);

CREATE TABLE "prices" (
	"price_id"	INTEGER,
	"movie_id"	INTEGER,
	"date"	TEXT NOT NULL,
	"vendor_id"	INTEGER,
	"presentation_type"	TEXT,
	"price_value"	REAL,
	FOREIGN KEY("movie_id") REFERENCES "movies"("movie_id"),
	FOREIGN KEY("vendor_id") REFERENCES "vendors"("vendor_id"),
	PRIMARY KEY("price_id")
);

CREATE TABLE "purchases" (
	"purchase_id"	INTEGER,
	"purchase_date"	TEXT,
	"purchase_amount"	REAL,
	"movie_id"	INTEGER,
	"vendor_id"	INTEGER,
	FOREIGN KEY("movie_id") REFERENCES "movies"("movie_id"),
	FOREIGN KEY("vendor_id") REFERENCES "vendors"("vendor_id"),
	PRIMARY KEY("purchase_id")
);

-- DROP VIEW IF EXISTS movie_purchases;
CREATE VIEW movie_purchases
AS 
SELECT m.movie_id, m.movie_name, v.vendor, p.purchase_date, p.purchase_amount
FROM purchases p
INNER JOIN movies m
ON p.movie_id = m.movie_id
INNER JOIN vendors v
ON p.vendor_id = v.vendor_id
WHERE p.purchase_date is NOT NULL AND
p.purchase_amount is NOT NULL
ORDER BY m.movie_name;

-- DROP VIEW IF EXISTS movie_data;
CREATE VIEW movie_data
AS 
select p.date, m.movie_name, m.url, m.poster, 
case p.presentation_type when "_4K" then "4K" else p.presentation_type end presentation_type, 
p.price_value, v.vendor from movies m
INNER JOIN prices p
ON m.movie_id = p.movie_id
INNER JOIN vendors v
ON p.vendor_id = v.vendor_id
WHERE m.movie_id NOT IN (
	SELECT movie_id 
	FROM movie_purchases
);

--purchase update query
update purchases
set purchase_date = "", purchase_amount = 0, vendor_id = 0
where movie_id = (select movie_id FROM movies WHERE movie_name = "");
SELECT * FROM purchases
WHERE purchase_date is NOT NULL AND
purchase_amount is NOT NULL;