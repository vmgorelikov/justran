CREATE TABLE "users" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "username" varchar(32) NOT NULL,
  "display_name" varchar(160),
  "password_hash" text NOT NULL,
  "created_at" timestamp NOT NULL
);

CREATE TABLE "translations" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "initated_by" integer NOT NULL,
  "full_text" text NOT NULL,
  "properties" text, 
  "previous" integer,
  "created_at" timestamp NOT NULL,
  
  CONSTRAINT fk_initiated_by
    FOREIGN KEY ("initated_by")
    REFERENCES "users" ("id")
    ON DELETE NO ACTION, -- для разбирательств

  CONSTRAINT fk_previous_for_translation
    FOREIGN KEY ("previous")
    REFERENCES "translation_patches" ("id")
    ON DELETE SET NULL -- ну не будет истории — и не будет
);

CREATE TABLE "translation_patches" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "for_translation" integer NOT NULL,
  "delta" text NOT NULL,
  "previous" integer,
  "created_at" timestamp NOT NULL,

  CONSTRAINT fk_for_translation
    FOREIGN KEY ("for_translation")
    REFERENCES "translations" ("id")
    ON DELETE CASCADE, -- а вот хранить orphaned относительно перевода 
    -- патчи нам не надо

  CONSTRAINT fk_previous_for_patch
    FOREIGN KEY ("previous")
    REFERENCES "translation_patches" ("id")
    ON DELETE SET NULL -- то, что где-то там удалился патч, не должно -- нам мешать
);

