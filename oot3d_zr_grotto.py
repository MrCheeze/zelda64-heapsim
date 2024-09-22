from sim import GameState, actors
import copy

def check(state_, actionList):

    if 1 not in state_.loadedRooms or state_.actorStates[actors.En_Butte]['numLoaded'] < 3:
        return False

    state = copy.deepcopy(state_)


    for node in list(state.heap()):
        if node.actorId == actors.En_Sw and not node.free:
            skulltula = node.addr
        #if node.actorId == actors.Obj_Mure and not node.free and node.actorParams & 0x1F == 4:
        #    state.allocMultipleActors(actors.En_Butte, node.childCount, tuple(node.rooms), 0x0000, (0,0,0), node.addr)

    token = state.allocActor(actors.En_Si).addr
    state.dealloc(skulltula)
    bomb = state.allocActor(actors.En_Bom).addr
    rang = state.allocActor(actors.En_Boom).addr
    chu = state.allocActor(actors.En_Bom_Chu).addr
    state.dealloc(rang)
    state.dealloc(token)
    state.dealloc(bomb)
    state.dealloc(chu)
    state.changeRoom(0)
    for node in state.heap():
        if node.actorId == actors.Door_Ana and not node.free:
            #print(hex(chu), hex(node.addr))
            if chu + 0x10 == node.addr:
                print(hex(chu), hex(node.addr), actionList)
                print(state)
                #return True

'''
for switchFlags in [[9],[9,8],[8,2],[2,10],[9,8,2,10],[]]:
    print(switchFlags)

    state = GameState('OoT3D', 'OoT3D-US', {'spawnFromGameOver':False,'beanPlanted':False,'lullaby':False,'clearedRooms':[],'collectibleFlags':[],'switchFlags':switchFlags,'bombchu':True,'bomb':True,'bottle':False,'sword':True,'hookshot':False,'boomerang':True,'slingshot':False})
    state.loadScene(sceneId=0x54, setupId=0, roomId=0)
    state.getAvailableActions(carryingActor=False, disableInteractionWith={actors.Obj_Mure2,actors.En_Wonder_Item,actors.En_Item00,actors.En_Kusa,actors.En_Ishi,actors.En_Okuta,actors.Obj_Bombiwa})

    ret = state.search(successFunction=check, actionLimit=5, carryingActor=False, disableInteractionWith={actors.Obj_Mure2,actors.En_Wonder_Item,actors.En_Item00,actors.En_Kusa,actors.En_Ishi,actors.En_Okuta,actors.Obj_Bombiwa}, num_worker_threads=1)

    print(ret)
'''

switchFlags = [8,2]
state = GameState('OoT3D', 'OoT3D-US', {'spawnFromGameOver':False,'beanPlanted':False,'lullaby':False,'clearedRooms':[],'collectibleFlags':[],'switchFlags':switchFlags,'bombchu':True,'bomb':True,'bottle':False,'sword':True,'hookshot':False,'boomerang':True,'slingshot':False})
state.loadScene(sceneId=0x54, setupId=0, roomId=0)
thunder = state.allocActor(actors.En_Bom_Chu).addr
state.changeRoom(1)
for node in list(state.heap()):
    if node.actorId == actors.Obj_Mure and not node.free:
        mure = node.addr
state.allocMultipleActors(actors.En_Butte, 3, (1,), 0, (0, 0, 0), mure)
state.dealloc(thunder)
print(state)
check(state, [])
#print(state.getAvailableActions(carryingActor=False))
#print(state)
