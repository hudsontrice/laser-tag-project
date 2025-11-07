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

from src.net.udp_sender import UDPSender
from src.net.udp_receiver import UDPServer


class Logic:
    def __init__(self):
        # Team scores
        self.redTeamScore = 0
        self.greenTeamScore = 0
        
        # Player scores dictionary
        self.scores = {}  # equipment_id -> score
        
        # Track base hitters for icon display
        self.base_hitters = set()
        
        # UDP connections
        self.udp_sender = UDPSender()
        self.udp_receiver = UDPServer()
        
        # UI reference (set by app.py later)
        self.play_action_screen = None

    def process_data(self, data: str, red_roster: list[int], green_roster: list[int]) -> None:
        #transform data into usable
        try:
            equipment_id_1, equipment_id_2 = map(int, data.split(":"))
        except (ValueError, AttributeError):
            print(f"Invalid UDP message format: {data}")
            return
        # equipment 1 tags equipment 2

        #base hit logig
        if equipment_id_2 == 43 : #green base hit
            if self.is_red_team(equipment_id_1): 
                self.award_base_points(equipment_id_1, 43) 
        elif equipment_id_2 == 53: #red base hit
            if self.is_green_team(equipment_id_1): 
                self.award_base_points(equipment_id_1, 53) 

        # individual tag logic - check if same team (both odd or both even)
        elif (self.is_red_team(equipment_id_1) and self.is_red_team(equipment_id_2)) or \
             (self.is_green_team(equipment_id_1) and self.is_green_team(equipment_id_2)):
            # Friendly fire - both lose points
            self.deduct_points(equipment_id_1, 10)
            self.deduct_points(equipment_id_2, 10)
            self.udp_sender.send_message(f"{equipment_id_1}")
            self.udp_sender.send_message(f"{equipment_id_2}") #send back both equipment ids
        
        else:
            # Opposing teams - valid hit, attacker gets points
            self.award_points(equipment_id_1, 10)
            self.udp_sender.send_message(f"{equipment_id_2}") #send back victim equipment id
        
        
        
    def is_red_team(self, equipment_id: int) -> bool:
        """Red team = odd equipment IDs."""
        return equipment_id % 2 == 1
            

    def is_green_team(self, equipment_id: int) -> bool:
        """Green team = even equipment IDs."""
        return equipment_id % 2 == 0
    


    def main_loop(self, red_roster: list[int], green_roster: list[int]) -> None:
        # Main game logic loop to handle scoring and UDP communication
        print("Scoring main loop started. Listening for UDP events...")
        while True:
            message, addr = self.udp_receiver.listener()  # Unpack tuple properly
            if message:
                self.process_data(message, red_roster, green_roster)
    
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
        """Broadcast game start code 202."""
        self.udp_sender.send_message("202")
        print("Game started! Broadcast code 202")
        
    def end_game(self) -> None:
        """Broadcast game end code 221 three times."""
        for _ in range(3):
            self.udp_sender.send_message("221")
        print("Game ended! Broadcast code 221 (3x)")