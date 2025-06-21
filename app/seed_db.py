import os
import sys
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash


# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.db import db
from app.models import (
    Player, Item, PlayerItem, Achievement, PlayerAchievement,
    Phase, Boss, PhaseProgress, Battle, ResultType
)

app = create_app()

def seed_database():
    with app.app_context():
        # Limpar dados existentes (opcional - usar com cuidado!)
        db.drop_all()
        db.create_all()

        # 1. Criar Bosses
        bosses = [
            Boss(name="Goblin King", health=1000),
            Boss(name="Dragon Lord", health=2500),
            Boss(name="Ice Demon", health=1800),
            Boss(name="Shadow Wraith", health=3000)
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

        # 3. Criar Fases (vinculadas a bosses)
        phases = [
            Phase(name="Floresta Negra", boss_id=bosses[0].id),
            Phase(name="Montanha da Perdição", boss_id=bosses[1].id),
            Phase(name="Cavernas Gélidas", boss_id=bosses[2].id),
            Phase(name="Abismo Sombrío", boss_id=bosses[3].id)
        ]
        db.session.add_all(phases)
        db.session.commit()

        # 4. Criar Conquistas
        achievements = [
            Achievement(name="Primeiros Passos", reward_coins=50),
            Achievement(name="Caçador de Bosses", reward_coins=200),
            Achievement(name="Colecionador", reward_coins=150),
            Achievement(name="Lenda Viva", reward_coins=500)
        ]
        db.session.add_all(achievements)
        db.session.commit()

        # 5. Criar Jogadores
        players = [
            Player(username="admin", email="admin@game.com", password="admin123"),
            Player(username="player1", email="player1@mail.com", password="pass123"),
            Player(username="player2", email="player2@mail.com", password="pass456")
        ]
        # Definir senhas com hash
        for player in players:
            player.set_password(player.password)
        db.session.add_all(players)
        db.session.commit()

        # 6. Adicionar Itens aos Jogadores
        player_items = [
            PlayerItem(player_id=players[1].id, item_id=items[0].id, is_equipped=True),
            PlayerItem(player_id=players[1].id, item_id=items[2].id, quantity=5),
            PlayerItem(player_id=players[2].id, item_id=items[3].id, is_equipped=True),
            PlayerItem(player_id=players[2].id, item_id=items[4].id)
        ]
        db.session.add_all(player_items)
        db.session.commit()

        # 7. Registrar Conquistas dos Jogadores
        player_achievements = [
            PlayerAchievement(player_id=players[1].id, achievement_id=achievements[0].id),
            PlayerAchievement(player_id=players[1].id, achievement_id=achievements[1].id),
            PlayerAchievement(player_id=players[2].id, achievement_id=achievements[0].id)
        ]
        db.session.add_all(player_achievements)
        db.session.commit()

        # 8. Registrar Progresso nas Fases
        phase_progress = [
            PhaseProgress(player_id=players[1].id, phase_id=phases[0].id, completed=True),
            PhaseProgress(player_id=players[1].id, phase_id=phases[1].id, completed=True),
            PhaseProgress(player_id=players[2].id, phase_id=phases[0].id, completed=True)
        ]
        db.session.add_all(phase_progress)
        db.session.commit()

        # 9. Registrar Batalhas
        battles = [
            Battle(
                player_id=players[1].id,
                boss_id=bosses[0].id,
                result=ResultType.WIN,
                created_at=datetime.now(timezone.utc)
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

        print("Banco de dados populado com sucesso!")


if __name__ == "__main__":
    seed_database()
