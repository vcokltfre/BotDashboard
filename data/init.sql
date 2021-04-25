CREATE TABLE IF NOT EXISTS Bots (
    bot_id              BIGINT NOT NULL PRIMARY KEY,
    bot_name            VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Configs (
    guild_id            BIGINT NOT NULL,
    guild_name          VARCHAR(255) NOT NULL,
    bot_id              BIGINT NOT NULL REFERENCES Bots (bot_id) ON DELETE CASCADE,
    config              TEXT NOT NULL,
    PRIMARY KEY (guild_id, bot_id)
);

CREATE TABLE IF NOT EXISTS ConfigAccess (
    guild_id            BIGINT NOT NULL,
    bot_id              BIGINT NOT NULL REFERENCES Bots (bot_id) ON DELETE CASCADE,
    member_id           BIGINT NOT NULL,
    PRIMARY KEY (guild_id, bot_id, member_id)
);

CREATE TABLE IF NOT EXISTS DiscordSessions (
    id                  VARCHAR(255) NOT NULL PRIMARY KEY,
    member_id           BIGINT NOT NULL,
    valid_until         TIMESTAMP NOT NULL
);
