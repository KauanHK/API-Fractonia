INSERT INTO rarity (name, color, description) VALUES
    ('Comum', 'Cinza', 'Itens comuns de baixo valor'),
    ('Raro', 'Azul', 'Itens raros com boas habilidades'),
    ('Épico', 'Roxo', 'Itens épicos, muito poderosos');


INSERT INTO item (name, description, power, acquired_at, rarity_id) VALUES
    ('Espada de Madeira', 'Uma espada simples de madeira.', 5, CURRENT_TIMESTAMP, 1),
    ('Armadura de Ferro', 'Proteção básica contra inimigos.', 15, CURRENT_TIMESTAMP, 2),
    ('Anel Mágico', 'Aumenta os poderes mágicos.', 25, CURRENT_TIMESTAMP, 3);


INSERT INTO boss (name) VALUES
    ('Metadius'),
    ('Boss2'),
    ('Boss3'),
    ('Boss4'),
    ('Boss5');


INSERT INTO phase (name, description, boss_id) VALUES
    ('Floresta Sombria', 'Uma floresta densa cheia de perigos.', 1),
    ('Caverna do Dragão', 'Lar do temível Dragão Vermelho.', 2),
    ('Castelo Assombrado', 'Fortaleza do Rei Esqueleto.', 3);


INSERT INTO player_item (player_id, item_id) VALUES
    (1, 1),
    (1, 2),
    (2, 3);


INSERT INTO level_progress (player_id, phase_number, time_spent, completed_at) VALUES
    (1, 1, 60.0, CURRENT_TIMESTAMP),
    (1, 2, 30.5, CURRENT_TIMESTAMP),
    (2, 1, 90.0, CURRENT_TIMESTAMP);
