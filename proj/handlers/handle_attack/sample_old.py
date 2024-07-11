from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_attack import QueryAttack
from risk_shared.records.moves.move_attack import MoveAttack
from risk_shared.records.moves.move_attack_pass import MoveAttackPass

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork

def handle_attack(game: Game, bot_state: BotState, query: QueryAttack, mapNetwork: MapNetwork) -> Union[MoveAttack, MoveAttackPass]:
    """After the troop phase of your turn, you may attack any number of times until you decide to
    stop attacking (by passing). After a successful attack, you may move troops into the conquered
    territory. If you eliminated a player you will get a move to redeem cards and then distribute troops."""

    player_list = list(range(5))
    other_players = list(set(player_list) - {game.state.me.player_id})

    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    my_territories_model = [game.state.territories[x] for x in my_territories]
    #get all the information into the map
    for i in my_territories:
        mapNetwork.set_node_owner(i,'me')
    for i in my_territories_model:
        mapNetwork.set_node_troops(i.territory_id, i.troops)

    for i in other_players:
        enemy_territories = game.state.get_territories_owned_by (i)
        enemy_territories_model = [game.state.territories[x] for x in enemy_territories]
        for j in enemy_territories:
            mapNetwork.set_node_owner(j, str(i))
        for j in enemy_territories_model:
            mapNetwork.set_node_troops(j.territory_id, j.troops)



    #attack weakest territory nearby -> continents
    def attack_weakest(territories: list[int]) -> Optional[MoveAttack]:
        # We will attack the weakest territory from the list.
        territories = sorted(territories, key=lambda x: game.state.territories[x].troops, reverse = True)
        for candidate_target in territories:
            #from weakest to strongest
            #get the nearby strongest border
            candidate_attackers = sorted(list(set(game.state.map.get_adjacent_to(candidate_target)) & set(my_territories)), key=lambda x: game.state.territories[x].troops, reverse=False)
            for candidate_attacker in candidate_attackers:
                #condition on attack
                if game.state.territories[candidate_attacker].troops >= 5 and game.state.territories[candidate_target].troops <= game.state.territories[candidate_attacker].troops//2:
                    #check if behind is a trap
                    attacker_surrounding = (set(game.state.map.get_adjacent_to(candidate_attacker))-set(my_territories))
                    target_surrounding = (set(game.state.map.get_adjacent_to(candidate_target))-set(my_territories))
                    surrounding_enemies = list(attacker_surrounding.union(target_surrounding))
                    surrounding_troops = []
                    for i in surrounding_enemies:
                        surrounding_troops.append(mapNetwork.get_node_troops(i))
                    #if safe, ATTACK
                    if max(surrounding_troops) < mapNetwork.get_node_troops(candidate_attacker):
                        return game.move_attack(query, candidate_attacker, candidate_target, min(3, game.state.territories[candidate_attacker].troops - 1))
                    

    '''game_phase'''
    game_state = len(game.state.recording) #game starts at 133
    avg = mapNetwork.get_average_troops() #average troops per players
    domination = len(mapNetwork.check_my_ownership()) + len(mapNetwork.check_ownership()) #how many continents are near conquered already

    all_my_continents = mapNetwork.calculate_continent_portion_owned(my_territories)
    
    bordering_territories = game.state.get_all_adjacent_territories(my_territories)

    weakest_continents = mapNetwork.calculate_enemy_troops_by_continent() #list of tuples [('NA',35troops/7territories)]

    strongest_list = mapNetwork.check_strongest() #[('0', forces 15)]

    continents_owner = mapNetwork.check_ownership() #get all continents and own by whom [(continent, owner)]
   
    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    total_troops_per_player = {}
    for player in game.state.players.values():
        total_troops_per_player[player.player_id] = sum([game.state.territories[x].troops for x in game.state.get_territories_owned_by(player.player_id)])

    most_powerful_player = max(total_troops_per_player.items(), key=lambda x: x[1])[0]

    if avg <=30 or game_state <500 or domination < 4:
        strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=True)
        #strengthen my continent
        #only the first 2 continents
        move = None
        for base, percent in all_my_continents[:2]:
            if 0.8<percent<1 and base in ['AS', 'EU'] or percent<1 and base in ['NA', 'AU', 'AF', 'SA']: #if continent is not fully owned
                for territory in strongest_territories:
                    adj = mapNetwork.get_neighbors(territory)
                    in_continent_enemy = list(set(adj)&set(mapNetwork.continents[base])-set(my_territories))
                    move = attack_weakest(in_continent_enemy)
                    if move!=None:
                        break
                    
        if move == None: #if top two continents secured
            if most_powerful_player == game.state.me.player_id: #attack weakest:
                strongest_list = sorted(strongest_list, key=lambda x: x[1], reverse=False)
            
            # attack the weakest/strongest player
            for strongest, power in strongest_list:
                if strongest != game.state.me.player_id and power != 0: #this is to check if weakest is not elimintated
                    man_nodes = mapNetwork.nodes_with_same_owner(str(strongest))
                    
                    #find the weakest continent of the dude
                    for group, force in weakest_continents:
                        for territory in strongest_territories:
                            adj = mapNetwork.get_neighbors(territory)
                            for i in adj:
                                if mapNetwork.G.nodes[i]['group'] == group:
                                    #adjacent territories that are both from the strongest players and not my territories
                                    move = attack_weakest(list(set(set(adj)&set(man_nodes) - set(my_territories))))
                                    if move!=None:
                                        break
        if move != None:
            return move

    else:
        strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=False)
        #strengthen my continent
        #only the first 3 continents
        move = None
        for base, percent in all_my_continents[:3]:
            if 0.8<percent<1 and base in ['AS', 'EU'] or percent<1 and base in ['NA', 'AU', 'AF', 'SA']: #if continent is not fully owned
                for territory in strongest_territories:
                    adj = mapNetwork.get_neighbors(territory)
                    in_continent_enemy = list(set(adj)&set(mapNetwork.continents[base])-set(my_territories))
                    move = attack_weakest(in_continent_enemy)
                    if move!=None:
                        break
                    
        if move == None: #if top two continents secured
            if most_powerful_player == game.state.me.player_id: #attack weakest:
                strongest_list = sorted(strongest_list, key=lambda x: x[1], reverse=False)
            
            # attack the weakest/strongest player
            for strongest, power in strongest_list:
                if strongest != game.state.me.player_id and power != 0: #this is to check if weakest is not elimintated
                    man_nodes = mapNetwork.nodes_with_same_owner(str(strongest))
                    
                    #find the weakest continent of the dude
                    for group, force in weakest_continents:
                        for territory in strongest_territories:
                            adj = mapNetwork.get_neighbors(territory)
                            for i in adj:
                                if mapNetwork.G.nodes[i]['group'] == group:
                                    #adjacent territories that are both from the strongest players and not my territories
                                    move = attack_weakest(list(set(set(adj)&set(man_nodes) - set(my_territories))))
                                    if move!=None:
                                        break
        if move != None:
            return move
    return game.move_attack_pass(query)