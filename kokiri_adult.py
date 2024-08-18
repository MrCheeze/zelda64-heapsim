from sim import GameState, actors
import copy

state = GameState('OoT', 'OoT-J-GC-MQDisc', {'bombchu':True, 'bomb':True, 'bottle':True, 'sword': False, 'hookshot': False, 'boomerang': False, 'clearedRooms':[], 'spawnFromGameOver':False, 'beanPlanted':False})
state.loadScene(sceneId=0x55, setupId=3, roomId=0)
state.actorStates[actors.En_Bom] = {'numLoaded': 0}
state.actorStates[actors.En_Bom_Chu] = {'numLoaded': 0}

#state.allocMultipleActors(actors.En_Ishi, 8, (0,), 0, (0, 0, 0), 0x801F5870)
#state.allocMultipleActors(actors.En_Kusa, 12, (0,), 0, (0, 0, 0), 0x801FB510)
#state.allocMultipleActors(actors.En_Item00, 7, (0,), 0, (0, 0, 0), 0x801EFEC0)

#print(sorted(state.getAvailableActions(carryingActor=False)))

state.allocMultipleActors(actors.En_Ishi, 8, (0,), 0, (0, 0, 0), 0x801F5870)

bombchu_addrs = set()

def check3(state, actionList):
    stateCopy = copy.deepcopy(state)
    for i in range(3):
        if (stateCopy.actorStates[actors.En_Bom_Chu]['numLoaded']+stateCopy.actorStates[actors.En_Bom]['numLoaded']) < 3:
            stateCopy.allocActor(actors.En_Bom_Chu)
    for node in stateCopy.heap():
        if node.nodeType == 'INSTANCE' and node.actorId == actors.En_Bom_Chu:
#        if node.nodeType == 'INSTANCE' and node.actorId in (actors.En_Bom_Chu, actors.En_Kusa, actors.En_Ishi, actors.En_Item00):
            a = node.addr + node.headerSize
            if a not in bombchu_addrs:
                bombchu_addrs.add(a)
                if 0x8020DF10 <= a <= 0x8020FF10:
                    print(hex(a)+"\n",end='')
            if a == 0x8020EF10:
                return True
    return False

print(state.search(check3, carryingActor=False, ignoreRooms={1,2}, actionLimit=5))

'''
import itertools

for actionList in itertools.permutations([('allocActor', 321, (0,)), ('allocActor', 33, (0,)), ('allocMultipleActors', 21, 7, (0,), 16384, (0, 0, 0), 2149514944), ('allocMultipleActors', 32, 3, (0,)), ('allocMultipleActors', 334, 8, (0,), 0, (0, 0, 0), 2149537904)]):
    stateCopy = copy.deepcopy(state)
    for action in actionList:
        func = getattr(stateCopy, action[0])
        func(*action[1:])

    print(check3(stateCopy, actionList), actionList)

'''
