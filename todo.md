## Attack Phrase:
- Goal: own as many continents as possible
- Goal 2: finish the enemy when opportunity arises

Core logic
1. Find continent with the least enemy troops that is not owned
    -> look into conquering that continent
    -> if not enough troops to conquer the continent with least enemy troops
        -> distrup others
        -> pass round and save more troops



Conquering Algorithm
- Basic version = current version
- Improved version
    1. shortest path to reach continent
    2. ????
        - strategy 1: attack territory with most troops = find shortest path to stringest enemy territory
        - strategy 2: conquer most territories, leave 1 behind
    3. Split troops strategically


Distrup algorithm
1. check if any opponent own the entire continent
2. dijkstra check if there is a reasonable path to that continent
3. attack to the territory specified by dijkstra
4. done

## handle_troops_after_attack
- Depends on the attach phrase
- Could store the action taken in the attack phrase in the global store
- 