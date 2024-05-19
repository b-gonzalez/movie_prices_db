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