from collections import deque


class Rooms:
    def __init__(self, room_uuid):
        self.room = room_uuid
        self.players = deque([])
        self.turns = []
        self.first_player = None
        self.next_player = None
        self.president = None
        self.vice_president = None
        self.ah = None
        self.vice_ah = None
        self.number_of_card_dealed = None

    def add(self, player_id):
        self.players.append(player_id)
        print(self.players)

