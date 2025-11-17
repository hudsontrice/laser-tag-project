from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable, Dict, List, Literal, Optional, Tuple

Team = Literal["red", "green"]

@dataclass(frozen=True)
class PlayerRef:
    equipment_id: int
    name: str
    team: Team
    index: int  # row index within the team list


class GameState:
    """
    Central scoring state + UI bridge.
    - Tracks per-player and per-team totals
    - Emits callbacks so PlayAction can update labels immediately
    """

    def __init__(self) -> None:
        # Immutable roster map after register_rosters()
        self.players_by_eid: Dict[int, PlayerRef] = {}

        # Scores
        self.player_scores: Dict[int, int] = {}  # equipment_id -> score
        self.team_scores: Dict[Team, int] = {"red": 0, "green": 0}

        # UI callbacks (set by PlayAction)
        self._on_player_score: Optional[Callable[[PlayerRef, int], None]] = None
        self._on_team_scores: Optional[Callable[[int, int, Optional[Team]], None]] = None
        self._on_base_hit: Optional[Callable[[PlayerRef, Team], None]] = None

        # Thread-safety: scoring can be called from UDP listener thread
        self._lock = threading.Lock()

    # ---------- Wiring to UI ----------
    def bind_ui(
        self,
        *,
        on_player_score: Callable[[PlayerRef, int], None],
        on_team_scores: Callable[[int, int, Optional[Team]], None],
        on_base_hit: Callable[[PlayerRef, Team], None],
    ) -> None:
        self._on_player_score = on_player_score
        self._on_team_scores = on_team_scores
        self._on_base_hit = on_base_hit

    # ---------- Roster ----------
    def register_rosters(
        self,
        red_names: List[str],
        green_names: List[str],
        red_equipment_ids: List[int],
        green_equipment_ids: List[int],
    ) -> None:
        """
        Build a stable equipment_id -> (team, index, name) map.
        Index matches the on-screen row so UI updates are O(1).
        """
        with self._lock:
            self.players_by_eid.clear()
            self.player_scores.clear()
            self.team_scores = {"red": 0, "green": 0}

            for idx, (eid, nm) in enumerate(zip(red_equipment_ids, red_names)):
                self.players_by_eid[eid] = PlayerRef(equipment_id=eid, name=nm, team="red", index=idx)
                self.player_scores[eid] = 0

            for idx, (eid, nm) in enumerate(zip(green_equipment_ids, green_names)):
                self.players_by_eid[eid] = PlayerRef(equipment_id=eid, name=nm, team="green", index=idx)
                self.player_scores[eid] = 0

    # ---------- Scoring APIs (call these from scoring.Logic) ----------
    def add_points(self, equipment_id: int, points: int) -> None:
        with self._lock:
            pref = self.players_by_eid.get(equipment_id)
            if pref is None:
                # Unknown player; ignore silently
                return

            # Update player
            self.player_scores[pref.equipment_id] = self.player_scores.get(pref.equipment_id, 0) + points

            # Update team
            self.team_scores[pref.team] += points

            # Emit UI updates
            if self._on_player_score:
                self._on_player_score(pref, self.player_scores[pref.equipment_id])

            if self._on_team_scores:
                leader = self._leader_team()
                self._on_team_scores(self.team_scores["red"], self.team_scores["green"], leader)

    def friendly_fire_pair(self, a_eid: int, b_eid: int, penalty_each: int = 10) -> None:
        # both lose points
        self.add_points(a_eid, -penalty_each)
        self.add_points(b_eid, -penalty_each)

    def base_hit(self, hitter_eid: int, base_team: Team) -> None:
        """
        Award +100 to hitter if they destroyed the opposing BASE (base_team is the team whose base was hit).
        """
        with self._lock:
            pref = self.players_by_eid.get(hitter_eid)
            if pref is None:
                return

        # +100 to hitter (and his/her team)
        self.add_points(hitter_eid, +100)

        # Inform UI (for banner text / highlight row)
        if self._on_base_hit:
            self._on_base_hit(pref, base_team)

    # ---------- Helpers ----------
    def _leader_team(self) -> Optional[Team]:
        if self.team_scores["red"] == self.team_scores["green"]:
            return None
        return "red" if self.team_scores["red"] > self.team_scores["green"] else "green"
