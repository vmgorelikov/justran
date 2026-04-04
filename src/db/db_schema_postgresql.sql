-- DROP TABLE IF EXISTS "users", "translations", "translation_patches";

CREATE TABLE "users" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "username" varchar(32) NOT NULL UNIQUE,
  "display_name" varchar(160),
  "password_hash" text NOT NULL,
  "created_at" timestamp with time zone NOT NULL
);

CREATE TABLE "translations" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "initiated_by" integer NOT NULL,
  "source_text" text NOT NULL,
  "full_text" text NOT NULL,
  "properties" text, 
  "previous" integer,
  "created_at" timestamp with time zone NOT NULL,
  
  CONSTRAINT fk_initiated_by
    FOREIGN KEY ("initiated_by")
    REFERENCES "users" ("id")
    ON DELETE NO ACTION -- для разбирательств
);

CREATE TABLE "translation_patches" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "for_translation" integer NOT NULL,
  "delta" text NOT NULL,
  "previous" integer,
  "created_at" timestamp with time zone NOT NULL,

  CONSTRAINT fk_for_translation
    FOREIGN KEY ("for_translation")
    REFERENCES "translations" ("id")
    ON DELETE CASCADE -- а вот хранить orphaned относительно перевода 
    -- патчи нам не надо
);

ALTER TABLE "translations"
  ADD CONSTRAINT fk_previous_for_translation
    FOREIGN KEY ("previous")
    REFERENCES "translation_patches" ("id")
    ON DELETE SET NULL; -- ну не будет истории — и не будет

ALTER TABLE "translation_patches"
  ADD CONSTRAINT fk_previous_for_patch
    FOREIGN KEY ("previous")
    REFERENCES "translation_patches" ("id")
    ON DELETE SET NULL; -- то, что где-то там удалился патч, не должно -- нам мешать
