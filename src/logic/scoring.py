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
        redTeamScore = 0
        greenTeamScore = 0
        self.udp_sender = UDPSender()
        self.udp_receiver = UDPServer()

    def process_data(self, data: str, red_roster: list[str], green_roster: list[str]) -> None:
        #transform data into usable
        equipment_id_1, equipment_id_2 = map(int, data.split(":"))
        # equipment 1 tags equipment 2

        #base hit logig
        if equipment_id_2 == 43 : #green base hit
            if self.is_red_team(equipment_id_1): #filler
                self.award_base_points(equipment_id_1, "red") #filler they need 100 points
        elif equipment_id_2 == 53: #red base hit
            if self.is_green_team(equipment_id_1): #filler
                self.award_base_points(equipment_id_1, "green") #filler they need 100 points

        # individual tag logic
        elif equipment_id_1 in red_roster and equipment_id_2 in green_roster:
            self.award_points(equipment_id_1, 10) #red team player tagged green team player
            self.udp_sender.send_message(f"{equipment_id_2}") #send back equipment id of player who got tagged

        elif equipment_id_1 in green_roster and equipment_id_2 in red_roster:
            self.award_points(equipment_id_1, 10) #green team player tagged red team player
            self.udp_sender.send_message(f"{equipment_id_2}") #send back equipment id of player who got tagged
        
        elif equipment_id_1 in red_roster and equipment_id_2 in red_roster:
            self.deduct_points(equipment_id_1, 10) #red team player tagged red team player
            self.deduct_points(equipment_id_2, 10)
            self.udp_sender.send_message(f"{equipment_id_1}")
            self.udp_sender.send_message(f"{equipment_id_1}") #send back both equipment ids for same team tag
        
        elif equipment_id_1 in green_roster and equipment_id_2 in green_roster:
            self.deduct_points(equipment_id_1, 10) #green team player tagged green team player
            self.deduct_points(equipment_id_2, 10)
            self.udp_sender.send_message(f"{equipment_id_1}")
            self.udp_sender.send_message(f"{equipment_id_1}") #send back both equipment
        
        
        
    def is_red_team(self, equipment_id: int, red_roster) -> bool:
        for id in red_roster:
            if id == equipment_id:
                return True
            else:
                return False
            

    def is_green_team(self, equipment_id: int, green_roster) -> bool:
        for id in green_roster:
            if id == equipment_id:
                return True
        else:
            return False
    


    def main_loop(self, red_roster: list[str], green_roster: list[str]) -> None:
        # Main game logic loop to handle scoring and UDP communication
        while True:
            data = self.udp_receiver.listener()
            if data:
                self.process_data(data, red_roster, green_roster)  # Placeholder rosters



    

        





    


    