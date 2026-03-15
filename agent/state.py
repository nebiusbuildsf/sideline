"""Game state management for Sideline."""

import time

TENNIS_POINTS = ["0", "15", "30", "40"]


class GameState:
    def __init__(self, sport: str = "tennis"):
        self.sport = sport
        self.players = {"p1": "Player 1", "p2": "Player 2"}
        self.points = {"p1": "0", "p2": "0"}
        self.games = {"p1": 0, "p2": 0}
        self.sets = {"p1": 0, "p2": 0}
        self.server = "p1"
        self.rally_active = False
        self.frame_count = 0
        self.last_call = None
        self.events = []

    def summary(self) -> str:
        if self.sport == "tennis":
            return (
                f"{self.points['p1']}-{self.points['p2']} "
                f"(Games: {self.games['p1']}-{self.games['p2']}, "
                f"Sets: {self.sets['p1']}-{self.sets['p2']}) "
                f"Server: {self.players[self.server]}"
            )
        return f"{self.sport} | Frame {self.frame_count}"

    def update_score(self, player: str, reason: str = ""):
        if self.sport == "tennis":
            self._tennis_point(player)
        self.last_call = reason
        self.events.append({
            "type": "score",
            "player": player,
            "reason": reason,
            "score": self.score_dict(),
            "time": time.time(),
        })

    def add_event(self, event: dict):
        event["time"] = time.time()
        event["frame"] = self.frame_count
        self.events.append(event)
        self.last_call = event.get("call_type", self.last_call)

    def score_dict(self) -> dict:
        return {
            "points": dict(self.points),
            "games": dict(self.games),
            "sets": dict(self.sets),
            "server": self.server,
        }

    def to_dict(self) -> dict:
        return {
            "sport": self.sport,
            "players": self.players,
            "score": self.score_dict(),
            "frame_count": self.frame_count,
            "last_call": self.last_call,
            "events": self.events[-20:],
        }

    def _tennis_point(self, winner: str):
        loser = "p2" if winner == "p1" else "p1"
        w = self.points[winner]
        l = self.points[loser]

        if w == "AD":
            self._win_game(winner)
        elif l == "AD":
            self.points[loser] = "40"
        elif w == "40" and l == "40":
            self.points[winner] = "AD"
        elif w == "40":
            self._win_game(winner)
        else:
            idx = TENNIS_POINTS.index(w)
            self.points[winner] = TENNIS_POINTS[idx + 1]

    def _win_game(self, winner: str):
        self.points = {"p1": "0", "p2": "0"}
        self.games[winner] += 1
        self.server = "p2" if self.server == "p1" else "p1"

        loser = "p2" if winner == "p1" else "p1"
        if self.games[winner] >= 6 and (self.games[winner] - self.games[loser]) >= 2:
            self._win_set(winner)

    def _win_set(self, winner: str):
        self.sets[winner] += 1
        self.games = {"p1": 0, "p2": 0}
