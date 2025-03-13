from .room import Rooms


class RoomManager:
    def __init__(self):
        self.rooms = {}

    def join(self, player_id, room_id):
        if room_id not in self.rooms:
            self.rooms[room_id] = Rooms(room_id)
        if player_id not in self.rooms[room_id].players:
            self.rooms[room_id].add(player_id)

    def get_players(self, room_id):
        return self.rooms[room_id].players

    def next_player(self, room_id, times=1):
        return self.rooms[room_id].players.rotate(times)

    def get_turns(self, room_id):
        return self.rooms[room_id].turns

    def set_turns(self, room_id, card=None):
        if card is None:
            self.rooms[room_id].turns.clear()
        else:
            self.rooms[room_id].turns.append(card)

    def set_first_player(self, room_id, player):
        self.rooms[room_id].first_player = player

    def get_first_player(self, room_id):
        return self.rooms[room_id].first_player

    def set_number_of_card_dealed(self, room_id, number_of_card):
        self.rooms[room_id].number_of_card_dealed = number_of_card

    def get_number_of_card_dealed(self, room_id):
        return self.rooms[room_id].number_of_card_dealed

    def set_president(self, room_id, player):
        self.rooms[room_id].president = player

    def set_vice_president(self, room_id, player):
        self.rooms[room_id].vice_president = player

    def set_ah(self, room_id, player):
        self.rooms[room_id].ah = player

    def set_vice_ah(self, room_id, player):
        self.rooms[room_id].vice_ah = player
