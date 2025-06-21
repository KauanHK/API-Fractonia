import os
import sys
from datetime import datetime, timezone

# Adiciona o diretório raiz ao path para importar os módulos da aplicação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.db import db
from app.models import (
    Player, Item, PlayerItem, Achievement, PlayerAchievement,
    Phase, Boss, PhaseProgress, Battle, ResultType
)

# Cria a instância do app para ter o contexto da aplicação
app = create_app()

def seed_database():
    """
    Limpa e popula o banco de dados com dados iniciais para teste e desenvolvimento.
    """
    with app.app_context():
        # Apaga todas as tabelas e as recria do zero. Use com cuidado.
        db.drop_all()
        db.create_all()

        # 1. Criar Bosses
        bosses = [
            Boss(name="Rei Goblin", health=1000),
            Boss(name="Lorde Dragão", health=2500),
            Boss(name="Demônio do Gelo", health=1800),
            Boss(name="Espectro da Sombra", health=3000)
        ]
        db.session.add_all(bosses)
        db.session.commit()

        # 2. Criar Itens
        items = [
            Item(name="Espada de Aço"),
            Item(name="Escudo de Ferro"),
            Item(name="Poção de Cura"),
            Item(name="Arco Élfico"),
            Item(name="Amuleto de Fogo")
        ]
        db.session.add_all(items)
        db.session.commit()

        # 3. Criar Fases com suas recompensas 
        phases = [
            Phase(name="Floresta Negra", boss_id=bosses[0].id, reward_coins=100, reward_experience=250),
            Phase(name="Montanha da Perdição", boss_id=bosses[1].id, reward_coins=250, reward_experience=700),
            Phase(name="Cavernas Gélidas", boss_id=bosses[2].id, reward_coins=180, reward_experience=500),
            Phase(name="Abismo Sombrio", boss_id=bosses[3].id, reward_coins=400, reward_experience=1200)
        ]
        db.session.add_all(phases)
        db.session.commit()

        # 4. Criar Conquistas com requisito de XP 
        achievements = [
            Achievement(name="Iniciante", xp_required=100, reward_coins=50),
            Achievement(name="Aventureiro", xp_required=500, reward_coins=150),
            Achievement(name="Veterano", xp_required=1500, reward_coins=300),
            Achievement(name="Lenda", xp_required=5000, reward_coins=1000)
        ]
        db.session.add_all(achievements)
        db.session.commit()

        # 5. Criar Jogadores
        players = [
            Player(username="admin", email="admin@game.com", password="123"),
            Player(username="jogador1", email="player1@mail.com", password="123"),
            Player(username="jogador2", email="player2@mail.com", password="123")
        ]
        db.session.add_all(players)
        db.session.commit()

        # 6. Adicionar Itens aos Jogadores
        player_items = [
            PlayerItem(player_id=players[1].id, item_id=items[0].id),
            PlayerItem(player_id=players[1].id, item_id=items[2].id),
            PlayerItem(player_id=players[2].id, item_id=items[3].id),
            PlayerItem(player_id=players[2].id, item_id=items[4].id)
        ]
        db.session.add_all(player_items)
        db.session.commit()

        # 7. Registrar Conquistas para jogadores (opcional, para teste)
        # A lógica agora concede conquistas automaticamente, mas podemos pré-popular para testes.
        # Ex: Dando experiência inicial ao jogador 2 e rodando a lógica
        player2 = players[2]
        player2.experience = 600 # XP suficiente para a conquista "Aventureiro"
        # A lógica de concessão será testada via API, não aqui no seed.
        
        # 8. Registrar Progresso de Fases para jogadores de exemplo
        phase_progress = [
            PhaseProgress(player_id=players[1].id, phase_id=phases[0].id, completed=True),
        ]
        db.session.add_all(phase_progress)
        db.session.commit()
        
        # 9. Registrar Batalhas com recompensas 
        battles = [
            Battle(
                player_id=players[1].id,
                boss_id=bosses[0].id,
                result=ResultType.WIN,
                reward_coins=20, # Recompensa pequena, já que a fase dá o prêmio principal
                reward_experience=50
            ),
            Battle(
                player_id=players[2].id,
                boss_id=bosses[2].id,
                result=ResultType.LOSS,
                created_at=datetime.now(timezone.utc)
            )
        ]
        db.session.add_all(battles)
        db.session.commit()

        print("Banco de dados populado com sucesso com o novo schema!")


if __name__ == "__main__":
    seed_database()
