CREATE TABLE "factiva"."companies" (
  "gvkey" varchar(255),
  "name" varchar(255),
  "factiva_name" varchar(255),
  "factiva_code" varchar(255),
  PRIMARY KEY ("gvkey")
)
;

CREATE INDEX ON "factiva"."companies" (
  "gvkey"
);

CREATE TABLE "factiva"."company_articles" (
  "id" serial4,
  "gvkey" varchar(255) NOT NULL,
  "article_id" varchar(255) NOT NULL,
  "main_category" varchar(255),
  "sub_category" varchar(255),
  PRIMARY KEY ("id"),
  FOREIGN KEY ("gvkey") REFERENCES "factiva"."companies" ("gvkey"),
  FOREIGN KEY ("article_id") REFERENCES "factiva"."articles" ("id")
)
;

CREATE INDEX ON "factiva"."company_articles" (
  "gvkey"
);

CREATE INDEX ON "factiva"."company_articles" (
  "article_id"
);