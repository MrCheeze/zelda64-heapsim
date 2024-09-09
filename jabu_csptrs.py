from sim import GameState, actors
import copy


state = GameState('OoT', 'OoT-J-GC-MQDisc', {'spawnFromGameOver':True,'clearedRooms':[],'bombchu':False,'bomb':True,'bottle':False,'sword':False,'hookshot':False,'boomerang':True,'slingshot':False,'collectibleFlags':[],'switchFlags':[]})
state.loadScene(sceneId=0x55, setupId=0, roomId=0)

actorAddrs = {}

def check1(state, actionList):
    for node in state.heap():
        if not node.free and node.nodeType=='INSTANCE':
            if node.actorId in {actors.En_Bom, actors.En_Boom, actors.En_Arrow}:
                a = node.addr + state.headerSize
                if a not in actorAddrs or len(actionList) < len(actorAddrs[a]):
                    actorAddrs[a] = actionList

#state.search(check1, actionLimit=2, ignoreRooms={1,2}, disableInteractionWith={actors.En_Kusa, actors.En_Ishi},disableInteractionWithAddrs={0x801FA2D0,0x801FAF80,0x801FB150,0x801FB320})
state.search(check1, actionLimit=3, ignoreRooms={1,2}, disableInteractionWith={actors.En_Kusa, actors.En_Ishi},disableInteractionWithAddrs={})

for a in sorted(actorAddrs):
    print(hex(a), actorAddrs[a])


print('----------------------')


def getCutsceneAddr(state):
    if 2 in state.loadedRooms:
        return state.actorStates[actors.En_Ru1]['loadedOverlay']+state.headerSize+0x5C10
    return None


ss = []
def check2(state, actionList):
    if 1 not in state.loadedRooms:
        return False
    state2 = copy.deepcopy(state)
    state2.changeRoom(2)
    a = getCutsceneAddr(state2)
    assert a is not None
    if a in actorAddrs:
        ss.append(hex(a) + " "+ str(actionList))
    return False

state = GameState('OoT', 'OoT-J-GC-MQDisc', {'sword':False, 'bomb':True, 'bombchu':True, 'boomerang': False, 'bottle':False, 'clearedRooms':[], 'spawnFromGameOver':False, 'rutoFellInHole':False, 'hookshot':False, 'slingshot':False})
state.loadScene(sceneId=2, setupId=0, roomId=0)
state.search(check2,carryingActor=False,disableInteractionWith={actors.En_Holl}, actionLimit=5, ignoreRooms={3,4,5,14,0,2})

print('----------------------')

for s in sorted(ss):
    print(s)
