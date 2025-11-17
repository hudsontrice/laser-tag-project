'''
After the game start count down timer finishes, the software will broadcast code 202
When the game ends, the software will broadcast code 221 three times
When data is received, software will broadcast equipment id of player that was hit
if player tags another player on their own team, broadcast their own equipment id as well of the equipment id of who they hit (two transmissions)
If code 53 is received, the red base has been scored. If the player is on the green team, they will receive 100 points and the base icon (from the instructor's github) will be added to the left of their codename.
if code 43 is received, the green base has been scored. If the player is on the red team, they will receive 100 points and the base icon (from the instructor's github) will be added to the left of their codename.

Individual scores will be constantly updating (10 points awarded per opposing team player tag, -10 for same team player tag)
If a player tags a member of his/her own team, the player tagged as well as the player doing the tagging both lose 10 points.
Individual scores will be displayed from highest to lowest on each team
High team score will be flashing during play
'''

from typing import Optional, TYPE_CHECKING
from src.logic.game_state import GameState
from src.net.udp_sender import UDPSender
from src.net.udp_receiver import UDPServer

if TYPE_CHECKING:
    from src.ui.play_action import PlayAction


class Logic:
    def __init__(self, game_state: Optional[GameState] = None):
        # Team scores
        self.redTeamScore = 0
        self.greenTeamScore = 0
        
        # Player scores dictionary
        self.scores = {}  # equipment_id -> score
        
        # Track base hitters for icon display
        self.base_hitters = set()
        
        # Game state flag
        self.game_active = False
        
        # UDP connections
        self.udp_sender = UDPSender()
        self.udp_receiver = UDPServer()
        # Optional GameState instance (central scoring + UI bridge)
        self.game_state = game_state

        # UI reference (set by app.py later)
        self.play_action_screen: Optional['PlayAction'] = None

    def process_data(self, data: str, red_roster: list[int], green_roster: list[int]) -> None:
        #transform data into usable
        try:
            equipment_id_1, equipment_id_2 = map(int, data.split(":"))
        except (ValueError, AttributeError):
            print(f"Invalid UDP message format: {data}")
            return
        # equipment 1 tags equipment 2
        # Debug: report team membership for tracing friendly-fire vs valid hit
        try:
            attacker_is_red = self.is_red_team(equipment_id_1)
            victim_is_red = self.is_red_team(equipment_id_2)
            attacker_is_green = self.is_green_team(equipment_id_1)
            victim_is_green = self.is_green_team(equipment_id_2)
        except Exception:
            attacker_is_red = attacker_is_green = victim_is_red = victim_is_green = False

        #base hit logging
        if equipment_id_2 == 43 : #green base hit
            if self.is_red_team(equipment_id_1):
                # If GameState is present, delegate base scoring + UI callback
                if self.game_state:
                    self.game_state.base_hit(equipment_id_1, "green")
                else:
                    self.award_base_points(equipment_id_1, 43)
                    if self.play_action_screen:
                        player_name = self.get_player_name(equipment_id_1)
                        self.play_action_screen.log_base_hit(player_name, "green")
                self.udp_sender.send_message(f"{equipment_id_1}")  # Acknowledge base hit
            return  # Don't process as regular tag
        elif equipment_id_2 == 53: #red base hit
            if self.is_green_team(equipment_id_1):
                if self.game_state:
                    self.game_state.base_hit(equipment_id_1, "red")
                else:
                    self.award_base_points(equipment_id_1, 53)
                    if self.play_action_screen:
                        player_name = self.get_player_name(equipment_id_1)
                        self.play_action_screen.log_base_hit(player_name, "red")
                self.udp_sender.send_message(f"{equipment_id_1}")  # Acknowledge base hit
            return  # Don't process as regular tag 

        # individual tag logic - check if same team (both odd or both even)
        elif (self.is_red_team(equipment_id_1) and self.is_red_team(equipment_id_2)) or \
             (self.is_green_team(equipment_id_1) and self.is_green_team(equipment_id_2)):
            # Friendly fire - both lose points
            print(f"FRIENDLY FIRE! Player {equipment_id_1} hit teammate {equipment_id_2}")
            # Extra debug: print team membership
            print(f"Teams -> attacker red:{attacker_is_red} green:{attacker_is_green}; victim red:{victim_is_red} green:{victim_is_green}")
            if self.game_state:
                self.game_state.friendly_fire_pair(equipment_id_1, equipment_id_2, penalty_each=10)
            else:
                self.deduct_points(equipment_id_1, 10)
                self.deduct_points(equipment_id_2, 10)
            # Send each equipment ID as its own transmission per hardware contract
            self.udp_sender.send_message(f"{equipment_id_1}")
            self.udp_sender.send_message(f"{equipment_id_2}")
            # Log to UI
            if self.play_action_screen:
                attacker_name = self.get_player_name(equipment_id_1)
                victim_name = self.get_player_name(equipment_id_2)
                self.play_action_screen.log_friendly_fire(attacker_name, victim_name)
        
        else:
            # Opposing teams - valid hit, attacker gets points
            if self.game_state:
                self.game_state.add_points(equipment_id_1, 10)
            else:
                self.award_points(equipment_id_1, 10)
            self.udp_sender.send_message(f"{equipment_id_2}") #send back victim equipment id
            # Log to UI
            if self.play_action_screen:
                attacker_name = self.get_player_name(equipment_id_1)
                victim_name = self.get_player_name(equipment_id_2)
                self.play_action_screen.log_tag_event(attacker_name, victim_name)
        
        
        
    def is_red_team(self, equipment_id: int) -> bool:
        """Red team = odd equipment IDs."""
        try:
            return equipment_id in self.red_equipment_ids
        except AttributeError:
            return equipment_id % 2 == 1  # fallback
            

    def is_green_team(self, equipment_id: int) -> bool:
        """Green team = even equipment IDs."""
        try:
            return equipment_id in self.green_equipment_ids
        except AttributeError:
            return equipment_id % 2 == 0 #fallback
    
    def get_player_name(self, equipment_id: int) -> str:
        """Get player name from equipment ID using roster lookup."""
        # Check red team first
        if equipment_id in self.red_equipment_ids:
            index = self.red_equipment_ids.index(equipment_id)
            return self.red_names[index]
        # Check green team
        elif equipment_id in self.green_equipment_ids:
            index = self.green_equipment_ids.index(equipment_id)
            return self.green_names[index]
        # Fallback if not found
        return f"Player {equipment_id}"
    


    def main_loop(self, red_equipment_ids: list[int], green_equipment_ids: list[int], 
                  red_names: list[str], green_names: list[str]) -> None:
        # Main game logic loop to handle scoring and UDP communication
        # Store rosters for name lookups
        self.red_equipment_ids = red_equipment_ids
        self.green_equipment_ids = green_equipment_ids
        self.red_names = red_names
        self.green_names = green_names
        
        print("Scoring main loop started. Listening for UDP events...")
        # Register rosters with GameState if present so UI updates can be emitted
        if self.game_state:
            try:
                self.game_state.register_rosters(red_names, green_names, red_equipment_ids, green_equipment_ids)
            except Exception:
                pass
        while self.game_active:
            message, addr = self.udp_receiver.listener()  # Unpack tuple properly
            if message:
                self.process_data(message, red_equipment_ids, green_equipment_ids)
        
        print("Scoring main loop stopped. Game ended.")
    
    # DATA HANDLING METHODS
    def award_points(self, equipment_id: int, points: int) -> None:
        """Award points to a player and update team score."""
        if equipment_id not in self.scores:
            self.scores[equipment_id] = 0
        self.scores[equipment_id] += points
        print(f"Player {equipment_id} awarded {points} points. Total: {self.scores[equipment_id]}")
        
    def deduct_points(self, equipment_id: int, points: int) -> None:
        """Deduct points from a player."""
        self.award_points(equipment_id, -points)
        
    def award_base_points(self, equipment_id: int, base_code: int) -> None:
        """Award 100 points for hitting a base."""
        self.award_points(equipment_id, 100)
        self.base_hitters.add(equipment_id)
        base_name = "green" if base_code == 43 else "red"
        print(f"Player {equipment_id} hit {base_name} base! +100 points")
        
    def start_game(self) -> None:
        """Broadcast game start code 202 and activate game loop."""
        self.game_active = True
        self.udp_sender.send_message("202")
        print("Game started! Broadcast code 202")
        
    def end_game(self) -> None:
        """Broadcast game end code 221 three times and stop game loop."""
        self.game_active = False
        for _ in range(3):
            self.udp_sender.send_message("221")
        print("Game ended! Broadcast code 221 (3x)")